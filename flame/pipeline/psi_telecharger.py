"""Télécharge les sources NASA PSI et fabrique le jeu de données de l'équipe, sur n'importe quelle machine.

Une seule commande, depuis la racine du dépôt :

    uv run python -m flame.pipeline.psi_telecharger

Ce que fait le script :
  1. Il demande au dépôt NASA PSI (https://psi.nasa.gov, API JSON ouverte, sans clé ni compte) la liste des
     investigations de combustion et la liste complète des fichiers de chacune.
  2. Il télécharge les tables d'expériences, les métadonnées, les Reports et les Science Documents dans
     data/raw/psi_mirror (environ 330 Mo). Les données brutes (14 To) ne sont jamais téléchargées : elles sont
     seulement listées dans all_files.csv, pour que le site puisse y renvoyer.
  3. Il lance psi_construire.py, qui écrit le jeu de données (CSV, dataset.json, SQLite) dans data/raw/psi_dataset.

data/raw/ est ignoré par git : seuls les scripts sont dans le dépôt. Relancer le script saute les fichiers déjà là.

Options : --mirror DOSSIER, --out DOSSIER, --tables-only (environ 5 Mo), --max-mb N (60 par défaut),
--no-build (télécharger seulement), --no-download (reconstruire seulement).

Le code vient du travail de préparation et garde ses noms en anglais. Détail des tables : PSI_DATASET.md.
Crédit des données : NASA Physical Sciences Informatics (PSI), licence CC0-1.0. Citer chaque investigation par son DOI.
"""

import argparse
import csv
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://psi.nasa.gov/geode-py/ws"
UA = {"User-Agent": "flame-in-freefall-dataset/1.0", "Accept": "application/json, text/plain, */*"}
NEVER = {"Raw Data", "Calibration"}
META = "Investigation Metadata Files"
ALWAYS = {"Experimental table", "Modeling table", META}
DOCS = {"Reports", "Science Documents", "Read Me"}
# spreadsheets and notes that psi_construire.py reads to fill in airflow, results and sensors
NEEDED = ("BASS test matrix.xlsx", "CFI_DataSummary_Spreadsheet_Jan2021.xlsx", "BASS-II data FAQ.docx")


def http(url, data=None, timeout=120, retries=4):
    body = json.dumps(data).encode() if data is not None else None
    headers = dict(UA)
    if body:
        headers["Content-Type"] = "application/json"
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=headers), timeout=timeout) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if isinstance(e, urllib.error.HTTPError) and e.code in (400, 403, 404):
                raise
            if attempt == retries - 1:
                raise
            time.sleep(2 * 2**attempt)


def list_combustion():
    url = BASE + "/repo/search?source=psi&type=investigation&sort=Public%20Release%20Date&order=desc&size=500"
    hits = json.loads(http(url))["hits"]["hits"]
    out = [h["_source"] for h in hits if "Combustion" in json.dumps(h["_source"].get("Research Area", ""))]
    return sorted(out, key=lambda s: int(s["Accession"].split("-")[1]))


def flatten(listing):
    flat = []

    def walk(node, category):
        for f in node.get("files") or []:
            if f.get("directory") is False:
                flat.append(
                    {
                        "key": f["key"],
                        "name": f["key"].rsplit("/", 1)[-1],
                        "bytes": int(f.get("bytes_size") or 0),
                        "version": f.get("version"),
                        "category": category,
                        "subcategory": f.get("subcategory") or "",
                        "restricted": bool(f.get("restricted") or f.get("restrictedAccess")),
                    }
                )
            else:
                walk(f, category or f.get("displayName", ""))

    for top in listing.get("files") or []:
        walk(top, top.get("displayName", ""))
    return flat


def download(acc, f, dest):
    if dest.exists() and dest.stat().st_size == f["bytes"]:
        return "already there"
    q = urllib.parse.urlencode({"file": f["name"], "version": f["version"], "redirect": "false"})
    signed = http(f"{BASE}/studies/{acc}/download?{q}").decode().strip().strip('"')
    if not signed.startswith(("http", "file:")):
        return f"failed: no download link ({signed[:80]})"
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    with (
        urllib.request.urlopen(
            urllib.request.Request(signed, headers={"User-Agent": UA["User-Agent"]}), timeout=300
        ) as r,
        open(tmp, "wb") as out,
    ):
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            out.write(chunk)
    tmp.replace(dest)
    return "downloaded"


def fetch(mirror, tables_only, max_mb):
    mirror.mkdir(parents=True, exist_ok=True)
    invs = list_combustion()
    print(f"{len(invs)} combustion investigations on PSI")
    rows, failed = [], []
    for s in invs:
        acc = s["Accession"]
        acr = "".join(c if c.isalnum() or c in "-." else "_" for c in (s.get("Acronym") or "")).strip("_")
        old = sorted(mirror.glob(acc + "_*")) + sorted(mirror.glob(acc))
        folder = old[0] if old else mirror / (acc + "_" + acr if acr else acc)
        folder.mkdir(exist_ok=True)
        meta = json.loads(http(f"{BASE}/repo/investigations/{acc}"))
        (folder / "investigation.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
        files = flatten(
            json.loads(
                http(
                    BASE + "/files/v2", {"folder": "", "fileType": "study", "studyId": acc, "version": meta["version"]}
                )
            )
        )
        n_ok = 0
        for f in files:
            cat = f["category"]
            want = cat in ALWAYS or (cat in DOCS and (not tables_only or f["name"] in NEEDED))
            status = ""
            if cat in NEVER:
                status = "not downloaded (raw data, listed only)"
            elif f["restricted"]:
                status = "restricted"
            elif want and cat in DOCS and f["bytes"] > max_mb * 1e6 and f["name"] not in NEEDED:
                status = "skipped (larger than --max-mb)"
            elif want:
                dest = folder / ("metadata" if cat == META else cat.replace("/", "-")) / f["name"]
                try:
                    status = download(acc, f, dest)
                except Exception as e:
                    status = f"failed: {e}"
                if status.startswith("failed"):
                    failed.append("{} {}: {}".format(acc, f["name"], status))
                else:
                    n_ok += 1
                    if cat == META and f["name"].lower().endswith(".zip"):
                        try:
                            with zipfile.ZipFile(dest) as z:
                                for m in z.namelist():
                                    if os.path.basename(m) == "i_Investigation.txt":
                                        (dest.parent / "i_Investigation.txt").write_bytes(z.read(m))
                        except zipfile.BadZipFile:
                            failed.append("{} {}: not a valid zip".format(acc, f["name"]))
                if status == "downloaded":
                    time.sleep(0.2)
            rows.append(
                {
                    "accession": acc,
                    "category": cat,
                    "subcategory": f["subcategory"],
                    "key": f["key"],
                    "name": f["name"],
                    "bytes": f["bytes"],
                    "version": f["version"],
                    "downloaded": status,
                }
            )
        raw = sum(f["bytes"] for f in files if f["category"] in NEVER)
        print(
            f"  {acc:<8} {s.get('Acronym') or '':<22} {len(files):5d} files listed, {n_ok:3d} local, "
            f"raw data left on PSI: {raw / 1e9:.1f} GB"
        )
    with open(mirror / "all_files.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    if failed:
        print(f"\n{len(failed)} file(s) could not be downloaded:")
        for x in failed:
            print("  ! " + x)
    return failed


def main():
    ap = argparse.ArgumentParser(
        description="Download the PSI combustion sources and build the Flame in Freefall dataset."
    )
    ap.add_argument("--mirror", default="data/raw/psi_mirror")
    ap.add_argument("--out", default="data/raw/psi_dataset")
    ap.add_argument("--tables-only", action="store_true")
    ap.add_argument("--max-mb", type=float, default=60)
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--no-download", action="store_true")
    a = ap.parse_args()
    mirror, out = Path(a.mirror), Path(a.out)
    if not a.no_download:
        try:
            fetch(mirror, a.tables_only, a.max_mb)
        except urllib.error.URLError as e:
            sys.exit(f"Could not reach psi.nasa.gov ({e}). Check the network, then run again.")
    if a.no_build:
        return
    build = Path(__file__).resolve().parent / "psi_construire.py"
    if not build.exists():
        sys.exit("psi_construire.py must sit next to psi_telecharger.py")
    out.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, str(build), str(mirror), str(out)])
    if r.returncode:
        sys.exit("psi_construire.py failed")
    print(f"\nDataset ready in {out.resolve()} (CSV files, dataset.json, flame_in_freefall.sqlite).")


if __name__ == "__main__":
    main()
