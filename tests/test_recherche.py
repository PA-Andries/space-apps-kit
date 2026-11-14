"""Tests du moteur de recherche. Propriétaire : rôle C."""

import pandas as pd

from flame.commun import INCONNU, charger_fiches
from flame.recherche import detail_du_score, filtrer, rechercher, valeurs_possibles

LUNE_PREVENIR = {"habitat": "Base lunaire", "pilier": "Prévenir", "profil": "Étudiant"}
STATION_DETECTER = {"habitat": "Station", "pilier": "Détecter", "profil": "Étudiant"}


def fiche(id_fiche: str) -> pd.Series:
    fiches = charger_fiches()
    return fiches[fiches["id"] == id_fiche].iloc[0]


def points(detail: pd.DataFrame) -> dict[str, int]:
    return dict(zip(detail["critere"], detail["points"], strict=True))


def test_question_vide_renvoie_tout():
    fiches = charger_fiches()
    assert len(rechercher("", fiches)) == len(fiches)


def test_un_mot_filtre_les_fiches():
    resultats = rechercher("tissu", charger_fiches())
    assert list(resultats["id"]) == ["EXEMPLE-A"]


def test_la_question_ignore_accents_majuscules_et_fin_de_mot():
    assert list(rechercher("FUMEE", charger_fiches())["id"]) == ["EXEMPLE-B"]
    assert list(rechercher("carbur", charger_fiches())["id"]) == ["EXEMPLE-C"]


def test_les_petits_mots_de_la_question_ne_comptent_pas():
    assert list(rechercher("quel tissu pour les", charger_fiches())["id"]) == ["EXEMPLE-A"]


def test_les_fiches_qui_ont_le_plus_de_mots_passent_devant():
    resultats = rechercher("gaz oxygène brûleur", charger_fiches(), LUNE_PREVENIR)
    assert resultats.iloc[0]["id"] == "EXEMPLE-D"
    assert list(resultats["mots_trouves"]) == sorted(resultats["mots_trouves"], reverse=True)


def test_le_score_classe_selon_le_scenario():
    assert rechercher("", charger_fiches(), LUNE_PREVENIR).iloc[0]["id"] == "EXEMPLE-D"
    assert rechercher("", charger_fiches(), STATION_DETECTER).iloc[0]["id"] == "EXEMPLE-B"


def test_le_score_est_la_somme_de_ses_quatre_parties():
    resultats = rechercher("", charger_fiches(), LUNE_PREVENIR)
    parties = resultats[["score_pilier", "score_oxygene", "score_combustible", "score_donnees"]].sum(axis=1)
    assert list(resultats["score"]) == list(parties)
    assert resultats["score"].between(0, 100).all()


def test_detail_du_score_explique_chaque_critere():
    detail = detail_du_score(fiche("EXEMPLE-D"), LUNE_PREVENIR)
    assert list(detail.columns) == ["critere", "points", "maximum", "explication"]
    assert points(detail) == {"Pillar": 40, "Oxygen": 25, "Fuel": 6, "Data": 10}
    assert list(detail["maximum"]) == [40, 25, 20, 15]
    assert detail["explication"].str.len().gt(0).all()


def test_l_oxygene_perd_des_points_avec_l_ecart():
    # EXEMPLE-A est testé de 16 à 21 % : à 9 points des 30 % de la base lunaire, couvert pour la station.
    assert points(detail_du_score(fiche("EXEMPLE-A"), LUNE_PREVENIR))["Oxygen"] == 2
    assert points(detail_du_score(fiche("EXEMPLE-A"), STATION_DETECTER))["Oxygen"] == 25


def test_sans_scenario_pilier_et_oxygene_valent_zero():
    detail = points(detail_du_score(fiche("EXEMPLE-A")))
    assert detail["Pillar"] == 0 and detail["Oxygen"] == 0
    assert detail["Fuel"] == 20 and detail["Data"] == 10


def test_une_valeur_inconnue_ne_donne_aucun_point():
    incomplete = fiche("EXEMPLE-C").copy()
    incomplete["oxygene_min"] = INCONNU
    incomplete["nb_tests"] = None
    incomplete["type_combustible"] = INCONNU
    detail = points(detail_du_score(incomplete, LUNE_PREVENIR))
    assert detail == {"Pillar": 0, "Oxygen": 0, "Fuel": 0, "Data": 0}


def test_filtrer_garde_les_fiches_qui_ont_une_des_valeurs():
    fiches = charger_fiches()
    assert list(filtrer(fiches, piliers=["Éteindre"])["id"]) == ["EXEMPLE-C", "EXEMPLE-D"]
    assert list(filtrer(fiches, types_combustible=["solide", "gaz"])["id"]) == ["EXEMPLE-A", "EXEMPLE-D"]
    assert list(filtrer(fiches, piliers=["Prévenir"], habitats=["Base martienne"])["id"]) == ["EXEMPLE-D"]


def test_filtrer_sans_choix_ne_retire_rien():
    fiches = charger_fiches()
    assert len(filtrer(fiches)) == len(fiches)
    assert len(filtrer(fiches, piliers=[], habitats=[])) == len(fiches)


def test_valeurs_possibles_separe_les_valeurs_multiples():
    assert valeurs_possibles(charger_fiches(), "pilier") == ["Détecter", "Prévenir", "Éteindre"]


def test_un_combustible_modele_compte_comme_son_type_de_base():
    modele = fiche("EXEMPLE-A").copy()
    modele["type_combustible"] = "solide (modèle)"
    assert points(detail_du_score(modele))["Fuel"] == 20
    modele["type_combustible"] = "fumée"
    assert points(detail_du_score(modele))["Fuel"] == 0


def test_une_table_vide_ne_fait_pas_planter_la_recherche():
    # Cas de la page Recherche quand les filtres ne gardent aucune fiche.
    aucune_fiche = filtrer(charger_fiches(), piliers=["Pilier qui n'existe pas"])
    for question in ("", "flamme"):
        resultats = rechercher(question, aucune_fiche, LUNE_PREVENIR)
        assert resultats.empty
        assert {"score", "mots_trouves"} <= set(resultats.columns)
