"""Extrait le texte des rapports et documents NASA téléchargés depuis PSI, pour l'assistant.

À lancer après `psi_telecharger` : `uv run python -m flame.pipeline.psi_textes`

Lit les dossiers « Reports » et « Science Documents » de `data/raw/psi_mirror/` et écrit un fichier texte par
document dans `data/psi/textes/<PSI-n>/`, plus un index `data/psi/textes.csv` (une ligne par document : investigation,
catégorie, fichier source, fichier texte, nombre de pages et de caractères). Les PDF et les .docx sont lus en entier.
Les vieux .doc Word sont lus au mieux : le texte peut contenir quelques caractères parasites. Les tableurs (.xlsx)
et les archives (.zip) ne sont pas des textes : ils restent listés dans `data/psi/documents.csv`.

Un PDF scanné (une image sans texte) donne un fichier presque vide : la colonne `caracteres` le montre.
Données : NASA Physical Sciences Informatics (PSI), licence CC0-1.0.
"""

import argparse
import html
import logging
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

RACINE = Path(__file__).resolve().parents[2]
DOSSIER_MIROIR = RACINE / "data" / "raw" / "psi_mirror"
DOSSIER_TEXTES = RACINE / "data" / "psi" / "textes"
INDEX_TEXTES = RACINE / "data" / "psi" / "textes.csv"
CATEGORIES = ("Reports", "Science Documents")
COLONNES_INDEX = ["investigation_id", "categorie", "fichier_source", "fichier_texte", "pages", "caracteres"]

# pypdf signale beaucoup de petits défauts de PDF sans gravité : on ne garde que les erreurs.
logging.getLogger("pypdf").setLevel(logging.ERROR)


def texte_pdf(chemin: Path) -> tuple[str, int]:
    """Le texte d'un PDF, page par page, et son nombre de pages."""
    lecteur = PdfReader(chemin)
    pages = []
    for numero, page in enumerate(lecteur.pages, start=1):
        try:
            contenu = page.extract_text() or ""
        except Exception as erreur:  # une page abîmée ne doit pas arrêter tout le document
            contenu = f"[page illisible : {erreur}]"
        pages.append(f"--- page {numero} ---\n{contenu.strip()}")
    return "\n\n".join(pages), len(lecteur.pages)


def texte_docx(chemin: Path) -> str:
    """Le texte d'un document Word récent (.docx), paragraphe par paragraphe."""
    xml = zipfile.ZipFile(chemin).read("word/document.xml").decode("utf-8", "ignore")
    xml = xml.replace("</w:p>", "\n").replace("<w:tab/>", "\t")
    return html.unescape(re.sub(r"<[^>]+>", "", xml))


def texte_doc(chemin: Path) -> str:
    """Le texte d'un vieux document Word (.doc), au mieux : les passages du fichier qui ressemblent à des phrases."""
    passages = re.findall(rb"[\x07\x09\x0a\x0d\x20-\x7e\x91-\x97\xa0-\xff]{8,}", chemin.read_bytes())
    phrases = []
    for passage in passages:
        texte = passage.decode("cp1252", errors="replace").replace("\x07", "\t").replace("\r", "\n").strip()
        mots = texte.split()
        lettres = sum(c.isalpha() or c == " " for c in texte) / max(len(texte), 1)
        # Un passage de texte : surtout des lettres et des espaces, des mots de longueur normale.
        if len(mots) > 1 and lettres > 0.8 and sum(map(len, mots)) / len(mots) < 12:
            phrases.append(texte)
    return "\n".join(phrases)


def extraire(chemin: Path) -> tuple[str, int | None] | None:
    """Le texte du document et son nombre de pages (inconnu hors PDF), ou None si ce n'est pas un texte."""
    extension = chemin.suffix.lower()
    if extension == ".pdf":
        return texte_pdf(chemin)
    if extension == ".docx":
        return texte_docx(chemin), None
    if extension == ".doc":
        return texte_doc(chemin), None
    return None


def nom_texte(nom_fichier: str) -> str:
    """Un nom de fichier texte sans espaces ni caractères spéciaux."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", nom_fichier).strip("_") + ".txt"


def main() -> None:
    parametres = argparse.ArgumentParser(description="Extrait le texte des documents PSI dans data/psi/textes/.")
    parametres.add_argument("miroir", nargs="?", type=Path, default=DOSSIER_MIROIR)
    miroir = parametres.parse_args().miroir
    dossiers = sorted(miroir.glob("PSI-*"), key=lambda d: int(d.name.split("_")[0].split("-")[1]))
    if not dossiers:
        sys.exit(f"Aucun dossier PSI-* dans {miroir} : lancer d'abord flame.pipeline.psi_telecharger")
    lignes = []
    for dossier in dossiers:
        investigation = dossier.name.split("_")[0]
        for categorie in CATEGORIES:
            for source in sorted((dossier / categorie).glob("*")):
                resultat = extraire(source)
                if resultat is None:
                    continue
                texte, pages = resultat
                cible = DOSSIER_TEXTES / investigation / nom_texte(source.name)
                cible.parent.mkdir(parents=True, exist_ok=True)
                entete = f"Source : NASA PSI, {investigation}, {categorie}, {source.name}\n\n"
                cible.write_text(entete + texte, encoding="utf-8", errors="replace")
                lignes.append(
                    {
                        "investigation_id": investigation,
                        "categorie": categorie,
                        "fichier_source": source.name,
                        "fichier_texte": cible.relative_to(RACINE).as_posix(),
                        "pages": pages,
                        "caracteres": len(texte),
                    }
                )
    index = pd.DataFrame(lignes, columns=COLONNES_INDEX)
    index.to_csv(INDEX_TEXTES, index=False)
    sys.stdout.write(f"{len(index)} documents extraits dans {DOSSIER_TEXTES}\n")


if __name__ == "__main__":
    main()
