"""Le moteur de recherche : garde les fiches qui répondent à la question et les classe pour le scénario."""

import pandas as pd

from flame.recherche.score import ajouter_scores, charger_pertinence
from flame.recherche.texte import compter_mots_trouves, mots_de_la_question


def rechercher(
    question: str,
    fiches: pd.DataFrame,
    scenario: dict[str, str] | None = None,
    pertinence: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Les fiches qui correspondent à `question`, les plus pertinentes en premier.

    Une fiche est gardée si elle contient au moins un mot de la question ; une question vide garde tout.
    Colonnes ajoutées : `score` (de 0 à 100 pour l'habitat de `scenario`, voir `detail_du_score`), ses quatre
    parties (`score_atmosphere`, `score_combustible`, `score_gravite`, `score_donnees`) et `mots_trouves`.
    Tri : d'abord le nombre de mots trouvés, puis le score.
    """
    if pertinence is None:
        pertinence = charger_pertinence()
    mots = mots_de_la_question(question)
    resultats = ajouter_scores(fiches, scenario, pertinence).assign(mots_trouves=compter_mots_trouves(fiches, mots))
    if mots:
        resultats = resultats[resultats["mots_trouves"] > 0]
    return resultats.sort_values(["mots_trouves", "score"], ascending=False, kind="stable").reset_index(drop=True)


def les_plus_pertinentes(
    fiches: pd.DataFrame,
    scenario: dict | None = None,
    nombre: int | None = None,
    pertinence: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Le classement de la page Investigations : toutes les fiches, triées par score pour l'environnement
    de `scenario`. `nombre` garde les premières (la page 1 en affiche 4). Aucun filtre de pilier (REPRISE).
    """
    pertinence = charger_pertinence() if pertinence is None else pertinence
    classement = ajouter_scores(fiches, scenario, pertinence)
    classement = classement.sort_values("score", ascending=False, kind="stable").reset_index(drop=True)
    return classement if nombre is None else classement.head(nombre)
