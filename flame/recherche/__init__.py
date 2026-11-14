"""Rôle C (Recherche) : le classement des investigations pour un environnement, et ce qu'on ne sait pas."""

from flame.recherche.conditions import tests_dans_les_plages
from flame.recherche.filtres import filtrer, valeurs_possibles
from flame.recherche.lacunes import ce_quon_ne_sait_pas, champs_inconnus
from flame.recherche.moteur import les_plus_pertinentes, rechercher
from flame.recherche.score import detail_du_score

__all__ = [
    "ce_quon_ne_sait_pas",
    "champs_inconnus",
    "detail_du_score",
    "filtrer",
    "les_plus_pertinentes",
    "rechercher",
    "tests_dans_les_plages",
    "valeurs_possibles",
]
