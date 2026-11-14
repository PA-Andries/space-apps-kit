"""Rôle C (Recherche) : le classement des investigations pour un environnement, et ce qu'on ne sait pas."""

from flame.recherche.filtres import filtrer, filtrer_par_pilier, valeurs_possibles
from flame.recherche.lacunes import ce_qu_on_ne_sait_pas, champs_inconnus
from flame.recherche.moteur import les_plus_pertinentes, rechercher
from flame.recherche.score import detail_du_score

__all__ = [
    "ce_qu_on_ne_sait_pas",
    "champs_inconnus",
    "detail_du_score",
    "filtrer",
    "filtrer_par_pilier",
    "les_plus_pertinentes",
    "rechercher",
    "valeurs_possibles",
]
