"""Rôle C (Recherche) : le moteur de recherche et le classement des investigations."""

from flame.recherche.filtres import filtrer, valeurs_possibles
from flame.recherche.moteur import SCORE_MIN, les_plus_pertinentes, rechercher
from flame.recherche.score import detail_du_score

__all__ = ["SCORE_MIN", "detail_du_score", "filtrer", "les_plus_pertinentes", "rechercher", "valeurs_possibles"]
