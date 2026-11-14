"""Recherche de rapports dans NTRS, le serveur de rapports techniques de NASA.

L'API est publique et sans clé : https://ntrs.nasa.gov/api/openapi/
Essai dans le terminal : `uv run python -m flame.pipeline.ntrs "BASS-II flame"`
"""

import sys

import pandas as pd
import requests

from flame.commun.constantes import COLONNES_PUBLICATIONS

URL_RECHERCHE = "https://ntrs.nasa.gov/api/citations/search"


def _vers_ligne(rapport: dict) -> dict:
    publications = rapport.get("publications") or [{}]
    auteurs = [a.get("meta", {}).get("author", {}).get("name", "") for a in rapport.get("authorAffiliations", [])]
    return {
        "ntrs_id": rapport["id"],
        "titre": rapport.get("title", ""),
        "annee": (publications[0].get("publicationDate") or "")[:4],
        "auteurs": "; ".join(nom for nom in auteurs if nom),
        "resume": rapport.get("abstract", ""),
        "url": f"https://ntrs.nasa.gov/citations/{rapport['id']}",
        "investigation_id": "",  # à relier à une fiche par le rôle B
    }


def chercher_publications(question: str, nombre: int = 25) -> pd.DataFrame:
    """Les `nombre` premiers rapports NTRS pour `question` (colonnes : COLONNES_PUBLICATIONS)."""
    reponse = requests.get(URL_RECHERCHE, params={"q": question, "page.size": nombre}, timeout=30)
    reponse.raise_for_status()
    lignes = [_vers_ligne(rapport) for rapport in reponse.json()["results"]]
    return pd.DataFrame(lignes, columns=COLONNES_PUBLICATIONS)


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "microgravity combustion"
    print(chercher_publications(question, nombre=5)[["ntrs_id", "annee", "titre"]].to_string(index=False))
