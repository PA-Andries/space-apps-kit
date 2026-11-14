"""Version de départ du moteur : compte les mots de la question présents dans le texte des fiches.

À faire par le rôle C : tenir compte du scénario pour classer les résultats
(score du brief : pilier 40, oxygène 25, combustible 20, données 15).
"""

import re

import pandas as pd

COLONNES_TEXTE = ["id", "nom", "pilier", "objectif", "type_combustible", "combustible", "materiel", "resume"]


def rechercher(question: str, fiches: pd.DataFrame, scenario: dict[str, str] | None = None) -> pd.DataFrame:
    """Les fiches qui correspondent à `question`, les plus pertinentes en premier.

    Ajoute une colonne `score`. Une question vide renvoie toutes les fiches.
    `scenario` (voir `get_scenario`) n'est pas encore utilisé.
    """
    texte = fiches[COLONNES_TEXTE].fillna("").astype(str).agg(" ".join, axis=1).str.lower()
    mots = question.lower().split()
    score = pd.Series(0, index=fiches.index)
    for mot in mots:
        score += texte.str.count(re.escape(mot))
    resultats = fiches.assign(score=score)
    if mots:
        resultats = resultats[resultats["score"] > 0]
    return resultats.sort_values("score", ascending=False, kind="stable").reset_index(drop=True)
