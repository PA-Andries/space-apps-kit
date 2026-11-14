"""Tests du classement et de « ce qu'on ne sait pas ». Propriétaire : rôle C.

Données d'exemple (data/exemples/tests.csv) :
- EXEMPLE-A (solide) : 16, 18 et 21 % d'O2, à 101 kPa ;
- EXEMPLE-C (liquide) : 10, 21 et 40 %, à 70 kPa ;
- EXEMPLE-D (gaz) : 21 et 40 %, à 101 kPa.
"""

import pandas as pd
import pytest

from flame.commun import INCONNU, charger_fiches, charger_tests
from flame.recherche import (
    ce_quon_ne_sait_pas,
    champs_inconnus,
    detail_du_score,
    filtrer,
    les_plus_pertinentes,
    rechercher,
    synthese_des_plus_pertinentes,
    valeurs_possibles,
)
from flame.recherche import (
    tests_dans_les_plages as dans_les_plages,
)

LUNE = {
    "habitat": "Base lunaire",
    "oxygene_pct": (30.0, None),
    "pression_kpa": (None, 70.3),
    "gravite": 0.165,
    "type_combustible": [],
    "debit_air_cm_s": (None, None),
}
STATION = {**LUNE, "habitat": "Station", "oxygene_pct": (19.0, 23.0), "pression_kpa": (90.0, 110.0), "gravite": 0.0}
MARS = {**LUNE, "habitat": "Base martienne", "oxygene_pct": (None, None), "pression_kpa": (None, None), "gravite": 0.38}
PERSONNALISE = {**MARS, "habitat": "Personnalisé", "gravite": None}


@pytest.fixture
def pertinence():
    """Une petite table `relevance` fictive, au format du rôle B (sans colonne de pilier)."""
    lignes = [
        ("moon_base", "EXEMPLE-A", 0.4, "no rows at >=30% O2; microgravity only: one bound for partial gravity"),
        ("moon_base", "EXEMPLE-C", 1.0, "1 rows at >=30% O2; mimics partial gravity with an electric field"),
        ("moon_base", "EXEMPLE-D", 0.4, "no rows at >=30% O2; microgravity only: one bound for partial gravity"),
    ]
    return pd.DataFrame(lignes, columns=["habitat_id", "investigation_id", "gravity_fit", "why"])


def fiche(id_fiche: str) -> pd.Series:
    fiches = charger_fiches()
    return fiches[fiches["id"] == id_fiche].iloc[0]


def points(detail: pd.DataFrame) -> dict[str, int]:
    return dict(zip(detail["critere"], detail["points"], strict=True))


# --- Recherche par mots (utilisée par l'assistant du rôle E) ---


def test_question_vide_renvoie_tout():
    fiches = charger_fiches()
    assert len(rechercher("", fiches)) == len(fiches)


def test_un_mot_filtre_les_fiches():
    assert list(rechercher("tissu", charger_fiches())["id"]) == ["EXEMPLE-A"]


def test_la_question_ignore_accents_majuscules_et_fin_de_mot():
    assert list(rechercher("FUMEE", charger_fiches())["id"]) == ["EXEMPLE-B"]
    assert list(rechercher("carbur", charger_fiches())["id"]) == ["EXEMPLE-C"]


def test_les_petits_mots_de_la_question_ne_comptent_pas():
    assert list(rechercher("quel tissu pour les", charger_fiches())["id"]) == ["EXEMPLE-A"]


def test_les_fiches_qui_ont_le_plus_de_mots_passent_devant():
    resultats = rechercher("gaz oxygène brûleur", charger_fiches(), LUNE)
    assert resultats.iloc[0]["id"] == "EXEMPLE-D"
    assert list(resultats["mots_trouves"]) == sorted(resultats["mots_trouves"], reverse=True)


def test_une_table_vide_ne_fait_pas_planter_la_recherche():
    aucune_fiche = filtrer(charger_fiches(), types_combustible=["plasma"])
    for question in ("", "flamme"):
        resultats = rechercher(question, aucune_fiche, LUNE)
        assert resultats.empty
        assert {"score", "mots_trouves"} <= set(resultats.columns)


# --- Les tests dans les plages du scénario ---


def test_tests_dans_les_plages_de_la_lune():
    # Seul C-03 (40 %, 70 kPa) a au moins 30 % d'O2 et au plus 70,3 kPa.
    assert list(dans_les_plages(charger_tests(), LUNE)["test_id"]) == ["C-03"]


def test_une_pression_non_notee_ne_retire_pas_le_test():
    tests = pd.DataFrame({"investigation_id": ["X"], "test_id": ["X-1"], "oxygene_pct": [35], "pression_kpa": [None]})
    assert len(dans_les_plages(tests, LUNE)) == 1


def test_sans_plage_tous_les_tests_sont_gardes():
    assert len(dans_les_plages(charger_tests(), MARS)) == len(charger_tests())


# --- Le score sur les preuves ---


def test_detail_du_score_explique_les_quatre_criteres(pertinence):
    detail = detail_du_score(fiche("EXEMPLE-C"), LUNE, pertinence)
    assert list(detail.columns) == ["critere", "points", "maximum", "explication"]
    assert points(detail) == {"Atmosphere": 13, "Fuel": 15, "Gravity": 20, "Data": 10}  # 40 x 1/3 = 13
    assert list(detail["maximum"]) == [40, 25, 20, 15]
    assert detail.iloc[0]["explication"].startswith("1 of its 3 tests (33%) fall in your atmosphere (O2 ≥ 30 %")
    assert detail["explication"].str.len().gt(0).all()


def test_le_classement_change_avec_l_oxygene_et_la_pression():
    lune = les_plus_pertinentes(charger_fiches(), LUNE)
    station = les_plus_pertinentes(charger_fiches(), STATION)
    assert lune.iloc[0]["id"] != station.iloc[0]["id"]
    assert points(detail_du_score(fiche("EXEMPLE-D"), STATION))["Atmosphere"] == 20  # D-01 : 1 test sur 2


def test_un_habitat_personnalise_avec_une_plage_compte_l_atmosphere():
    personnalise = {**PERSONNALISE, "oxygene_pct": (30, None)}
    detail = points(detail_du_score(fiche("EXEMPLE-D"), personnalise))
    assert detail["Atmosphere"] == 20  # D-02 à 40 % : 1 test sur 2


def test_sans_atmosphere_le_critere_ne_compte_pas():
    detail = detail_du_score(fiche("EXEMPLE-C"), MARS)
    assert points(detail)["Atmosphere"] == 0
    assert "unknown" in detail.iloc[0]["explication"]


def test_les_combustibles_choisis_comptent():
    seulement_gaz = {**LUNE, "type_combustible": ["gaz"]}
    assert points(detail_du_score(fiche("EXEMPLE-A"), seulement_gaz))["Fuel"] == 0
    assert points(detail_du_score(fiche("EXEMPLE-D"), seulement_gaz))["Fuel"] == 8
    assert points(detail_du_score(fiche("EXEMPLE-A"), LUNE))["Fuel"] == 25


def test_un_combustible_modele_compte_comme_son_type_de_base():
    modele = fiche("EXEMPLE-A").copy()
    modele["type_combustible"] = "solide (modèle)"
    assert points(detail_du_score(modele))["Fuel"] == 25
    modele["type_combustible"] = "fumée"
    assert points(detail_du_score(modele))["Fuel"] == 0


def test_une_valeur_inconnue_ne_donne_aucun_point(pertinence):
    incomplete = fiche("EXEMPLE-A").copy()
    incomplete["nb_tests"] = None
    incomplete["type_combustible"] = INCONNU
    detail = points(detail_du_score(incomplete, LUNE, pertinence))
    assert detail["Fuel"] == 0 and detail["Data"] == 0


def test_la_gravite_vient_de_relevance(pertinence):
    assert points(detail_du_score(fiche("EXEMPLE-D"), LUNE, pertinence))["Gravity"] == 8  # 20 x 0,4
    assert points(detail_du_score(fiche("EXEMPLE-D"), PERSONNALISE, pertinence))["Gravity"] == 0


def test_le_score_est_la_somme_de_ses_quatre_parties(pertinence):
    resultats = rechercher("", charger_fiches(), LUNE, pertinence)
    parties = resultats[["score_atmosphere", "score_combustible", "score_gravite", "score_donnees"]].sum(axis=1)
    assert list(resultats["score"]) == list(parties)
    assert resultats["score"].between(0, 100).all()


def test_le_classement_garde_toutes_les_fiches_trie_par_score(pertinence):
    classement = les_plus_pertinentes(charger_fiches(), LUNE, pertinence=pertinence)
    assert len(classement) == len(charger_fiches())
    assert list(classement["score"]) == sorted(classement["score"], reverse=True)
    assert len(les_plus_pertinentes(charger_fiches(), LUNE, nombre=3, pertinence=pertinence)) == 3


# --- Ce qu'on ne sait pas ---


def test_les_conditions_jamais_testees_sont_dites():
    constats = ce_quon_ne_sait_pas(charger_fiches(), charger_tests(), LUNE)
    conditions = "O2 ≥ 30 %, pressure ≤ 70.3 kPa"
    assert f"No solid-fuel test was run at {conditions}." in constats
    assert f"1 liquid-fuel test(s), from 1 investigation(s), were run at {conditions}." in constats
    assert f"No gas-fuel test was run at {conditions}." in constats
    assert any("partial gravity of the Moon base (0.165 g)" in constat for constat in constats)
    assert any("above 21 % oxygen" in constat for constat in constats)


def test_seuls_les_combustibles_choisis_sont_comptes():
    constats = ce_quon_ne_sait_pas(charger_fiches(), charger_tests(), {**LUNE, "type_combustible": ["solide"]})
    assert not any("liquid-fuel" in constat or "gas-fuel" in constat for constat in constats)


def test_mars_dit_que_l_atmosphere_est_inconnue():
    constats = ce_quon_ne_sait_pas(charger_fiches(), charger_tests(), MARS)
    assert constats[0].startswith("The atmosphere of the Mars base is unknown")


def test_la_station_n_a_pas_de_gravite_partielle():
    constats = ce_quon_ne_sait_pas(charger_fiches(), charger_tests(), STATION)
    assert (
        "1 solid-fuel test(s), from 1 investigation(s), were run at O2 19 to 23 %, pressure 90 to 110 kPa." in constats
    )
    assert not any("partial gravity" in constat for constat in constats)


def test_une_gravite_inconnue_est_dite():
    constats = ce_quon_ne_sait_pas(charger_fiches(), charger_tests(), PERSONNALISE)
    assert "The gravity of your custom environment is unknown." in constats


def test_champs_inconnus_d_une_fiche():
    incomplete = fiche("EXEMPLE-B").copy()
    incomplete["pression_kpa"] = None
    assert champs_inconnus(incomplete) == ["pressure"]


# --- La synthèse des 3 plus pertinentes (pour la page 1) ---


def test_la_synthese_compare_les_trois_plus_pertinentes():
    synthese = synthese_des_plus_pertinentes(charger_fiches(), charger_tests(), LUNE)
    assert len(synthese["investigations"]) == 3
    assert "All 3 ran tests at 21 % oxygen: a common ground to compare them." in synthese["accords"]
    assert any(phrase.startswith("They burn different fuels") for phrase in synthese["attention"])
    assert any("partial gravity of the Moon base (0.165 g)" in phrase for phrase in synthese["attention"])


def test_la_synthese_trouve_le_combustible_et_le_materiau_communs():
    fiches = charger_fiches()
    fiches.loc[fiches["id"] != "EXEMPLE-B", ["type_combustible", "combustible"]] = ["solide", "PMMA slab"]
    accords = synthese_des_plus_pertinentes(fiches, charger_tests(), LUNE)["accords"]
    assert "All 3 burn solid fuel." in accords
    assert "All 3 burned PMMA (acrylic): their results can be read side by side." in accords


def test_la_synthese_previent_quand_les_donnees_sont_minces():
    fiches = charger_fiches()
    fiches.loc[fiches["id"] == "EXEMPLE-A", "nb_tests"] = 2
    attention = synthese_des_plus_pertinentes(fiches, charger_tests(), STATION)["attention"]
    assert any(phrase.endswith("has only 2 test(s): thin evidence.") for phrase in attention)


def test_la_synthese_dit_que_l_atmosphere_de_mars_est_inconnue():
    attention = synthese_des_plus_pertinentes(charger_fiches(), charger_tests(), MARS)["attention"]
    assert attention[0].startswith("The atmosphere of the Mars base is unknown")


def test_la_synthese_sans_fiche_est_vide():
    aucune_fiche = filtrer(charger_fiches(), types_combustible=["plasma"])
    assert synthese_des_plus_pertinentes(aucune_fiche, charger_tests(), LUNE) == {
        "investigations": [],
        "accords": [],
        "attention": [],
    }


# --- Filtres et valeurs (utilisés par la page 1) ---


def test_filtrer_garde_les_fiches_qui_ont_une_des_valeurs():
    fiches = charger_fiches()
    assert list(filtrer(fiches, types_combustible=["solide", "gaz"])["id"]) == ["EXEMPLE-A", "EXEMPLE-D"]


def test_filtrer_sans_choix_ne_retire_rien():
    fiches = charger_fiches()
    assert len(filtrer(fiches)) == len(fiches)


def test_valeurs_possibles_separe_les_valeurs_multiples():
    assert valeurs_possibles(charger_fiches(), "pilier") == ["Détecter", "Prévenir", "Éteindre"]
