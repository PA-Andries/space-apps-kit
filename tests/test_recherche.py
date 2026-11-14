"""Tests du classement et de « ce qu'on ne sait pas ». Propriétaire : rôle C."""

import pandas as pd
import pytest

from flame.commun import INCONNU, charger_fiches, charger_tests
from flame.recherche import (
    ce_qu_on_ne_sait_pas,
    champs_inconnus,
    detail_du_score,
    filtrer,
    filtrer_par_pilier,
    les_plus_pertinentes,
    rechercher,
    valeurs_possibles,
)

LUNE = {"habitat": "Base lunaire", "pilier": "Prévenir", "profil": "Étudiant"}
STATION = {"habitat": "Station", "pilier": "Détecter", "profil": "Étudiant"}
MARS = {"habitat": "Base martienne", "pilier": "Prévenir", "profil": "Étudiant"}
SANS_O2 = "no rows at >=30% O2"
PROCHE = "1 rows at >=30% O2, none at reduced pressure"


def ligne(investigation_id, categorie, poids, atmosphere, gravite, why):
    return {
        "habitat_id": "moon_base",
        "investigation_id": investigation_id,
        "category_id": categorie,
        "category_weight": poids,
        "atmosphere_fit": atmosphere,
        "gravity_fit": gravite,
        "why": why,
    }


@pytest.fixture
def pertinence():
    """Une petite table `relevance` fictive, au format du rôle B, pour les fiches d'exemple."""
    return pd.DataFrame(
        [
            ligne("EXEMPLE-A", "prevent", 3, 0.0, 0.4, f"primary for 'prevent'; {SANS_O2}; microgravity only"),
            ligne("EXEMPLE-A", "react", 0, 0.0, 0.4, "not relevant to this category"),
            ligne("EXEMPLE-B", "detect", 2, 0.0, 0.4, "secondary for 'detect'; oxygen not recorded; microgravity only"),
            ligne(
                "EXEMPLE-C",
                "react",
                1,
                1.0,
                1.0,
                "indirect for 'react'; 1 rows at >=30% O2 and <=0.69 atm; mimics partial gravity",
            ),
            ligne("EXEMPLE-D", "prevent", 1, 0.7, 0.4, f"indirect for 'prevent'; {PROCHE}; microgravity only"),
            ligne("EXEMPLE-D", "react", 2, 0.7, 0.4, f"secondary for 'react'; {PROCHE}; microgravity only"),
        ]
    )


@pytest.fixture
def atmospheres():
    """Les lignes utiles de data/psi/habitats.csv (rôle B)."""
    colonnes = ["habitat_id", "o2_pct_min", "o2_pct_max", "pressure_psi_max", "gravity_g"]
    lignes = [
        ("iss", 21, 21, 14.7, 0.0),
        ("moon_base", 30, None, 10.2, 0.165),
        ("mars_base", None, None, None, 0.38),
    ]
    return pd.DataFrame(lignes, columns=colonnes)


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
    # Cas d'une page quand les filtres ne gardent aucune fiche.
    aucune_fiche = filtrer(charger_fiches(), piliers=["Pilier qui n'existe pas"])
    for question in ("", "flamme"):
        resultats = rechercher(question, aucune_fiche, LUNE)
        assert resultats.empty
        assert {"score", "mots_trouves"} <= set(resultats.columns)


# --- Le score sur les preuves (recadrage : le pilier n'en fait plus partie) ---


def test_detail_du_score_explique_les_quatre_criteres(pertinence):
    detail = detail_du_score(fiche("EXEMPLE-C"), LUNE, pertinence)
    assert list(detail.columns) == ["critere", "points", "maximum", "explication"]
    assert points(detail) == {"Atmosphere": 40, "Fuel": 15, "Gravity": 20, "Data": 10}
    assert list(detail["maximum"]) == [40, 25, 20, 15]
    assert detail["explication"].str.len().gt(0).all()
    # La raison vient de la colonne `why` du rôle B, sans toucher aux majuscules (« O2 »).
    assert "O2" in detail.iloc[0]["explication"]


def test_le_pilier_ne_change_pas_le_score(pertinence):
    a_prevenir = points(detail_du_score(fiche("EXEMPLE-D"), {**LUNE, "pilier": "Prévenir"}, pertinence))
    a_detecter = points(detail_du_score(fiche("EXEMPLE-D"), {**LUNE, "pilier": "Détecter"}, pertinence))
    assert a_prevenir == a_detecter


def test_atmosphere_et_gravite_suivent_relevance(pertinence):
    detail = points(detail_du_score(fiche("EXEMPLE-D"), LUNE, pertinence))
    assert detail["Atmosphere"] == 28  # 40 x 0,7
    assert detail["Gravity"] == 8  # 20 x 0,4


def test_mars_n_a_pas_d_atmosphere(pertinence):
    detail = detail_du_score(fiche("EXEMPLE-C"), MARS, pertinence)
    assert points(detail)["Atmosphere"] == 0
    assert "no atmosphere" in detail.iloc[0]["explication"]


def test_sans_habitat_ni_relevance_atmosphere_et_gravite_valent_zero():
    detail = points(detail_du_score(fiche("EXEMPLE-A")))
    assert detail["Atmosphere"] == 0 and detail["Gravity"] == 0
    assert detail["Fuel"] == 25 and detail["Data"] == 10


def test_une_valeur_inconnue_ne_donne_aucun_point(pertinence):
    incomplete = fiche("EXEMPLE-A").copy()
    incomplete["nb_tests"] = None
    incomplete["type_combustible"] = INCONNU
    detail = points(detail_du_score(incomplete, STATION, pertinence))
    assert detail == {"Atmosphere": 0, "Fuel": 0, "Gravity": 0, "Data": 0}


def test_un_combustible_modele_compte_comme_son_type_de_base():
    modele = fiche("EXEMPLE-A").copy()
    modele["type_combustible"] = "solide (modèle)"
    assert points(detail_du_score(modele))["Fuel"] == 25
    modele["type_combustible"] = "fumée"
    assert points(detail_du_score(modele))["Fuel"] == 0


def test_le_score_est_la_somme_de_ses_quatre_parties(pertinence):
    resultats = rechercher("", charger_fiches(), LUNE, pertinence)
    parties = resultats[["score_atmosphere", "score_combustible", "score_gravite", "score_donnees"]].sum(axis=1)
    assert list(resultats["score"]) == list(parties)
    assert resultats["score"].between(0, 100).all()


# --- Le pilier : un filtre et une étiquette ---


def test_le_pilier_filtre_et_etiquette(pertinence):
    eteindre = filtrer_par_pilier(charger_fiches(), "Éteindre", pertinence)
    etiquettes = dict(zip(eteindre["id"], eteindre["etiquette"], strict=True))
    assert etiquettes == {"EXEMPLE-C": "indirect", "EXEMPLE-D": "secondary"}


def test_sans_pilier_rien_n_est_retire(pertinence):
    tous = filtrer_par_pilier(charger_fiches(), None, pertinence)
    assert len(tous) == len(charger_fiches())
    assert (tous["etiquette"] == "").all()


def test_sans_relevance_le_filtre_lit_la_colonne_pilier():
    prevenir = filtrer_par_pilier(charger_fiches(), "Prévenir", pd.DataFrame())
    assert list(prevenir["id"]) == ["EXEMPLE-A", "EXEMPLE-D"]


def test_le_classement_est_trie_par_score(pertinence):
    classement = les_plus_pertinentes(charger_fiches(), LUNE, pertinence=pertinence)
    assert list(classement["score"]) == sorted(classement["score"], reverse=True)
    assert classement.iloc[0]["id"] == "EXEMPLE-C"
    assert len(les_plus_pertinentes(charger_fiches(), LUNE, nombre=3, pertinence=pertinence)) == 3


# --- Ce qu'on ne sait pas ---


def test_les_conditions_jamais_testees_sont_dites(atmospheres):
    constats = ce_qu_on_ne_sait_pas("Base lunaire", charger_fiches(), charger_tests(), atmospheres)
    texte = "\n".join(constats)
    # Seul C-03 (liquide, 40 % et 70 kPa) est dans la zone lunaire : au moins 30 % et au plus 70,3 kPa.
    assert "No solid-fuel test was run in the atmosphere of the Moon base." in constats
    assert "1 liquid-fuel test(s), from 1 investigation(s), match the atmosphere of the Moon base." in constats
    assert "No gas-fuel test" in texte
    assert "partial gravity" in texte
    assert "above 21 % oxygen" in texte


def test_mars_dit_que_l_atmosphere_est_inconnue(atmospheres):
    constats = ce_qu_on_ne_sait_pas("Base martienne", charger_fiches(), charger_tests(), atmospheres)
    assert constats[0].startswith("The statement gives no oxygen or pressure for the Mars base")


def test_la_station_compte_l_air_de_19_a_23_pour_cent(atmospheres):
    constats = ce_qu_on_ne_sait_pas("Station", charger_fiches(), charger_tests(), atmospheres)
    assert "1 solid-fuel test(s), from 1 investigation(s), match the atmosphere of the Space station." in constats
    assert not any("partial gravity" in constat for constat in constats)


def test_champs_inconnus_d_une_fiche():
    incomplete = fiche("EXEMPLE-B").copy()
    incomplete["pression_kpa"] = None
    assert champs_inconnus(incomplete) == ["pressure"]


# --- Filtres et valeurs ---


def test_filtrer_garde_les_fiches_qui_ont_une_des_valeurs():
    fiches = charger_fiches()
    assert list(filtrer(fiches, piliers=["Éteindre"])["id"]) == ["EXEMPLE-C", "EXEMPLE-D"]
    assert list(filtrer(fiches, types_combustible=["solide", "gaz"])["id"]) == ["EXEMPLE-A", "EXEMPLE-D"]


def test_filtrer_sans_choix_ne_retire_rien():
    fiches = charger_fiches()
    assert len(filtrer(fiches)) == len(fiches)


def test_valeurs_possibles_separe_les_valeurs_multiples():
    assert valeurs_possibles(charger_fiches(), "pilier") == ["Détecter", "Prévenir", "Éteindre"]
