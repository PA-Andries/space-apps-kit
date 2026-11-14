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
