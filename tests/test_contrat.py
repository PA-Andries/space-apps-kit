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


def test_les_tables_psi_ont_des_colonnes():
    from flame.commun.donnees import TABLES_PSI

    for nom in TABLES_PSI:
        fichier = DOSSIER_DATA / "psi" / f"{nom}.csv"
        if fichier.exists():
            assert len(pd.read_csv(fichier).columns) > 1, nom


def test_une_table_psi_inconnue_est_refusee():
    from flame.commun import charger_table_psi

    with pytest.raises(ValueError):
        charger_table_psi("pas_une_table")


def test_atmospheres_et_gravites_couvrent_tous_les_habitats():
    from flame.commun import ATMOSPHERES, GRAVITES, HABITATS, INCONNU, NATURE_ATMOSPHERES

    assert set(ATMOSPHERES) == set(GRAVITES) == set(NATURE_ATMOSPHERES) == set(HABITATS)
    # L'énoncé ne donne aucun chiffre pour Mars : le contrat n'en invente pas.
    assert ATMOSPHERES["Base martienne"] == (None, None)
    assert NATURE_ATMOSPHERES["Base martienne"] == INCONNU


def test_le_scenario_reprend_l_environnement_de_l_habitat():
    from streamlit.testing.v1 import AppTest

    def page():
        import streamlit as st

        from flame.commun import get_scenario, set_scenario

        set_scenario("Base lunaire", "Prévenir", "Étudiant")
        st.session_state["lune"] = get_scenario()
        set_scenario("Base martienne", "Prévenir", "Étudiant", type_combustible="solide", oxygene_pct=25)
        st.session_state["mars"] = get_scenario()

    etat = AppTest.from_function(page).run().session_state
    assert etat["lune"]["oxygene_pct"] == 30
    assert etat["lune"]["pression_kpa"] == 70.3
    assert etat["lune"]["gravite"] == 0.17
    assert etat["lune"]["type_combustible"] is None
    assert etat["mars"]["oxygene_pct"] == 25
    assert etat["mars"]["pression_kpa"] is None
    assert etat["mars"]["type_combustible"] == "solide"
