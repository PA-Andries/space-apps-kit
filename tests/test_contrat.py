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


@pytest.fixture
def scenario_vide():
    """Repart d'une session sans scénario, pour que les tests ne dépendent pas de leur ordre."""
    import streamlit as st

    from flame.commun.scenario import CLES_SCENARIO, _cle_session

    for cle in CLES_SCENARIO:
        st.session_state.pop(_cle_session(cle), None)


def test_le_scenario_a_ses_huit_cles_et_part_de_la_base_lunaire(scenario_vide):
    from flame.commun import get_scenario
    from flame.commun.scenario import CLES_SCENARIO

    scenario = get_scenario()
    assert tuple(scenario) == CLES_SCENARIO and len(scenario) == 8
    assert scenario["habitat"] == "Base lunaire"
    assert scenario["oxygene_pct"] == (30.0, None)
    assert scenario["pression_kpa"] == (None, 70.3)
    assert scenario["gravite"] == 0.165
    assert scenario["type_combustible"] == []
    assert scenario["debit_air_cm_s"] == (None, None)


def test_set_scenario_ne_change_que_les_cles_donnees(scenario_vide):
    from flame.commun import get_scenario, set_scenario

    set_scenario("Station", "Détecter", "Chercheur")  # l'appel d'origine, à trois valeurs
    scenario = get_scenario()
    assert (scenario["habitat"], scenario["pilier"], scenario["profil"]) == ("Station", "Détecter", "Chercheur")
    assert scenario["oxygene_pct"] == (19.0, 23.0)  # pré-rempli par l'habitat

    set_scenario(oxygene_pct=[25, 35], type_combustible=["solide"])
    scenario = get_scenario()
    assert scenario["oxygene_pct"] == (25, 35) and scenario["type_combustible"] == ["solide"]
    assert scenario["habitat"] == "Station" and scenario["pression_kpa"] == (90.0, 110.0)

    set_scenario("Station", "Détecter", "Chercheur")  # même habitat : la saisie de l'utilisateur reste
    assert get_scenario()["oxygene_pct"] == (25, 35)

    set_scenario(habitat="Base lunaire")  # nouvel habitat : son air remplace celui du précédent
    assert get_scenario()["oxygene_pct"] == (30.0, None)

    set_scenario(pilier=None)  # « tous les piliers »
    assert get_scenario()["pilier"] is None


def test_set_scenario_refuse_une_cle_inconnue_ou_une_plage_mal_ecrite(scenario_vide):
    from flame.commun import set_scenario

    with pytest.raises(TypeError):
        set_scenario(oxygene=30)
    with pytest.raises(ValueError):
        set_scenario(oxygene_pct=30)


def test_conditions_habitat_donne_chaque_valeur_avec_sa_source():
    from flame.commun import HABITAT_PERSONNALISE, HABITATS, conditions_habitat

    lune = conditions_habitat("Base lunaire")
    assert lune["oxygene_pct"] == (30.0, None) and lune["pression_kpa"] == (None, 70.3) and lune["gravite"] == 0.165
    assert lune["sources"] == {"oxygene_pct": "énoncé", "pression_kpa": "énoncé", "gravite": "à sourcer"}
    assert conditions_habitat("Rover pressurisé") == lune
    assert conditions_habitat("Station") == conditions_habitat("Vaisseau")
    assert conditions_habitat("Station")["sources"]["oxygene_pct"] == "à sourcer"
    for habitat in HABITATS:
        assert set(conditions_habitat(habitat)) == {"oxygene_pct", "pression_kpa", "gravite", "sources"}
    assert conditions_habitat(HABITAT_PERSONNALISE)["gravite"] is None


def test_mars_n_a_aucun_chiffre_d_atmosphere():
    from flame.commun import conditions_habitat

    mars = conditions_habitat("Base martienne")
    assert mars["oxygene_pct"] == (None, None) and mars["pression_kpa"] == (None, None)
    assert mars["sources"]["oxygene_pct"] == "inconnu" and mars["sources"]["pression_kpa"] == "inconnu"


def test_conditions_habitat_rend_une_copie():
    from flame.commun import conditions_habitat

    conditions_habitat("Station")["sources"]["oxygene_pct"] = "modifié"
    assert conditions_habitat("Station")["sources"]["oxygene_pct"] == "à sourcer"


def test_les_types_de_combustible_du_scenario():
    from flame.commun import TYPES_COMBUSTIBLE

    assert TYPES_COMBUSTIBLE == ["solide", "liquide", "gaz"]
