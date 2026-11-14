"""Lecture des tableaux de données. Les pages ne lisent jamais un CSV directement.

Tant que `data/investigations.csv` n'existe pas, le site tourne sur les données
fictives de `data/exemples/` et l'affiche clairement.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

RACINE = Path(__file__).resolve().parents[2]
DOSSIER_DATA = RACINE / "data"
DOSSIER_EXEMPLES = DOSSIER_DATA / "exemples"


def donnees_exemple() -> bool:
    """Vrai tant que le site tourne sur les données fictives."""
    return not (DOSSIER_DATA / "investigations.csv").exists()


def _lire(nom_fichier: str) -> pd.DataFrame:
    dossier = DOSSIER_EXEMPLES if donnees_exemple() else DOSSIER_DATA
    return pd.read_csv(dossier / nom_fichier)


@st.cache_data
def charger_fiches() -> pd.DataFrame:
    """Les investigations validées (colonnes : COLONNES_FICHES)."""
    fiches = _lire("investigations.csv")
    return fiches[fiches["verifie_par"].notna()].reset_index(drop=True)


@st.cache_data
def charger_tests() -> pd.DataFrame:
    """Les tests de chaque investigation (colonnes : COLONNES_TESTS)."""
    return _lire("tests.csv")


@st.cache_data
def charger_publications() -> pd.DataFrame:
    """Les rapports NTRS (colonnes : COLONNES_PUBLICATIONS)."""
    return _lire("publications.csv")


# Tables complètes du jeu de données PSI, dans `data/psi/` (colonnes : `flame/pipeline/PSI_DATASET.md`).
TABLES_PSI = [
    "investigations",
    "tests",
    "measurements",
    "hardware_families",
    "relations",
    "habitats",
    "categories",
    "relevance",
    "raw_data_map",
    "publications",
    "documents",
    "resources",
]


@st.cache_data
def charger_table_psi(nom: str) -> pd.DataFrame:
    """Une table complète du jeu de données PSI (`nom` dans `TABLES_PSI`), vide tant qu'elle n'existe pas."""
    if nom not in TABLES_PSI:
        raise ValueError(f"Table PSI inconnue : {nom}. Tables possibles : {', '.join(TABLES_PSI)}")
    fichier = DOSSIER_DATA / "psi" / f"{nom}.csv"
    return pd.read_csv(fichier) if fichier.exists() else pd.DataFrame()
