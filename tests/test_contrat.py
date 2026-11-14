"""Vérifie que les fichiers de données respectent le contrat. Propriétaire : rôle A."""

import pandas as pd
import pytest

from flame.commun import COLONNES_FICHES, COLONNES_PUBLICATIONS, COLONNES_TESTS
from flame.commun.donnees import DOSSIER_DATA, DOSSIER_EXEMPLES

CONTRAT = {
    "investigations.csv": COLONNES_FICHES,
    "tests.csv": COLONNES_TESTS,
    "publications.csv": COLONNES_PUBLICATIONS,
}
FICHIERS = [dossier / nom for dossier in (DOSSIER_EXEMPLES, DOSSIER_DATA) for nom in CONTRAT]
PRESENTS = [fichier for fichier in FICHIERS if fichier.exists()]


def nom_court(fichier):
    return f"{fichier.parent.name}/{fichier.name}"


@pytest.mark.parametrize("fichier", PRESENTS, ids=nom_court)
def test_colonnes(fichier):
    assert list(pd.read_csv(fichier).columns) == CONTRAT[fichier.name]


@pytest.mark.parametrize("dossier", [DOSSIER_EXEMPLES, DOSSIER_DATA], ids=lambda dossier: dossier.name)
def test_identifiants(dossier):
    if not (dossier / "investigations.csv").exists():
        pytest.skip("pas encore de vraies données")
    fiches = pd.read_csv(dossier / "investigations.csv")
    assert fiches["id"].is_unique
    if (dossier / "tests.csv").exists():
        tests = pd.read_csv(dossier / "tests.csv")
        inconnus = set(tests["investigation_id"]) - set(fiches["id"])
        assert not inconnus, f"tests.csv cite des investigations absentes : {inconnus}"


def test_pas_d_exemple_dans_les_vraies_donnees():
    vraies = DOSSIER_DATA / "investigations.csv"
    if not vraies.exists():
        pytest.skip("pas encore de vraies données")
    assert not pd.read_csv(vraies)["id"].str.startswith("EXEMPLE").any()
