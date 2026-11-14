"""Tests du pipeline de données. Propriétaire : rôle B. Aucun test n'appelle Internet."""

import pandas as pd

from flame.commun import COLONNES_FICHES, COLONNES_PUBLICATIONS, COLONNES_TESTS
from flame.pipeline.ntrs import _vers_ligne
from flame.pipeline.psi_contrat import fiches_du_contrat, lignes_de_tests_du_contrat


def test_un_rapport_ntrs_devient_une_ligne():
    rapport = {
        "id": 123,
        "title": "Titre",
        "abstract": "Résumé",
        "publications": [{"publicationDate": "2015-10-20T00:00:00"}],
        "authorAffiliations": [{"meta": {"author": {"name": "Nom, P."}}}],
    }
    ligne = _vers_ligne(rapport)
    assert list(ligne) == COLONNES_PUBLICATIONS
    assert ligne["annee"] == "2015"
    assert ligne["url"] == "https://ntrs.nasa.gov/citations/123"


def _jeu_psi():
    investigations = pd.DataFrame(
        [
            {
                "investigation_id": "PSI-1",
                "acronym": "ESSAI",
                "title": "Titre",
                "fire_safety_pillar": "Prevention;Suppression",
                "team_priority": 1,
                "objectives": "Objectif",
                "fuel_phase": "solid",
                "fuels": "PMMA",
                "facility": "MSG",
                "o2_pct_min": 13.6,
                "o2_pct_max": 22.2,
                "pressure_atm_min": 1.0,
                "pressure_atm_max": 1.0,
                "flow_cm_s_min": 0.0,
                "flow_cm_s_max": 53.0,
                "n_distinct_fuels": 2,
                "n_table_rows": 2,
                "one_liner": "Résumé",
                "psi_url": "https://psi.nasa.gov/physci/repo/data/investigations/PSI-1",
                "doi": "10.0/x",
            }
        ]
    )
    tests = pd.DataFrame(
        {
            "investigation_id": ["PSI-1", "PSI-1"],
            "test_id": ["a", "b"],
            "fuel": ["PMMA", "PMMA"],
            "o2_pct_min": [21.0, 17.0],
            "o2_pct_max": [21.0, 30.0],
            "pressure_atm_min": [1.0, None],
            "pressure_atm_max": [1.0, None],
            "flow_cm_s_max": [10.0, None],
            "outcome": ["Extinction", None],
            "raw_data_url": ["https://psi.nasa.gov", "https://psi.nasa.gov"],
        }
    )
    mesures = pd.DataFrame({"investigation_id": ["PSI-1", "PSI-1"], "instrument": ["Caméra", "Radiomètre"]})
    documents = pd.DataFrame({"investigation_id": ["PSI-1"], "category": ["Reports"], "file_name": ["rapport.pdf"]})
    pertinence = pd.DataFrame({"investigation_id": ["PSI-1"], "category_id": ["prevent"], "category_weight": [3]})
    return {
        "investigations": investigations,
        "tests": tests,
        "measurements": mesures,
        "documents": documents,
        "relevance": pertinence,
    }


def test_une_investigation_psi_devient_une_fiche():
    fiches = fiches_du_contrat(_jeu_psi(), {"PSI-1": "Prénom"})
    fiche = fiches.iloc[0]
    assert list(fiches.columns) == COLONNES_FICHES
    assert fiche["pilier"] == "Prévenir"
    assert fiche["pression_kpa"] == 101.3
    assert fiche["capteurs"] == "Caméra ; Radiomètre"
    assert fiche["habitats"] == "Vaisseau;Station"
    assert fiche["verifie_par"] == "Prénom"


def test_une_fiche_psi_n_est_pas_validee_toute_seule():
    assert fiches_du_contrat(_jeu_psi())["verifie_par"].isna().all()


def test_une_plage_d_oxygene_reste_vide_dans_les_tests():
    tests = lignes_de_tests_du_contrat(_jeu_psi()["tests"])
    assert list(tests.columns) == COLONNES_TESTS
    assert tests["oxygene_pct"].tolist()[0] == 21.0
    assert pd.isna(tests["oxygene_pct"].tolist()[1])
    assert tests["pression_kpa"].tolist()[0] == 101.3
