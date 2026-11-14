"""Le moteur de recherche : garde les fiches qui répondent à la question et les classe pour le scénario."""

import pandas as pd

from flame.recherche.score import ajouter_scores
from flame.recherche.texte import compter_mots_trouves, mots_de_la_question


def rechercher(question: str, fiches: pd.DataFrame, scenario: dict[str, str] | None = None) -> pd.DataFrame:
    """Les fiches qui correspondent à `question`, les plus pertinentes en premier.

    Une fiche est gardée si elle contient au moins un mot de la question ; une question vide garde tout.
    Colonnes ajoutées : `score` (de 0 à 100 pour `scenario`, voir `detail_du_score`), ses quatre parties
    (`score_pilier`, `score_oxygene`, `score_combustible`, `score_donnees`) et `mots_trouves`.
    Tri : d'abord le nombre de mots trouvés, puis le score. Sans `scenario`, pilier et oxygène valent 0.
    """
    mots = mots_de_la_question(question)
    resultats = ajouter_scores(fiches, scenario).assign(mots_trouves=compter_mots_trouves(fiches, mots))
    if mots:
        resultats = resultats[resultats["mots_trouves"] > 0]
    return resultats.sort_values(["mots_trouves", "score"], ascending=False, kind="stable").reset_index(drop=True)


# Seuil de la page Recherche : seules les fiches au score strictement supérieur sont affichées.
SCORE_MIN = 80


def les_plus_pertinentes(
    fiches: pd.DataFrame, scenario: dict[str, str] | None = None, score_min: int = SCORE_MIN
) -> pd.DataFrame:
    """Les fiches dont le score pour `scenario` dépasse strictement `score_min`, la meilleure en premier.

    Pas de question : seul le score du scénario compte (voir `detail_du_score`).
    """
    resultats = rechercher("", fiches, scenario)
    resultats = resultats[resultats["score"] > score_min]
    return resultats.sort_values("score", ascending=False, kind="stable").reset_index(drop=True)
