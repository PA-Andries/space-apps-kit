"""Rôle C (Recherche) : le moteur de recherche et le classement des investigations."""

from flame.recherche.filtres import filtrer, valeurs_possibles
from flame.recherche.moteur import rechercher
from flame.recherche.score import detail_du_score

__all__ = ["detail_du_score", "filtrer", "rechercher", "valeurs_possibles"]
