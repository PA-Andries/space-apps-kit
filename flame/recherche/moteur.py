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
