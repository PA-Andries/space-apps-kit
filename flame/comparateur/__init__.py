"""Rôle D (Comparateur) : part d'une investigation et dit avec lesquelles elle se compare, et sur quoi."""

from flame.comparateur.comparaison import (
    CRITERES,
    EXPLICATIONS,
    NIVEAUX,
    VARIABLES,
    carte,
    comparables,
    comparer,
    instruments_communs,
    plages,
    points,
    separer,
    variables_communes,
)
from flame.comparateur.details import (
    ABSENT,
    cote_a_cote,
    explication_carte,
    frequents,
    ligne_psi,
    mesures,
    portrait,
    resume,
)

__all__ = [
    "ABSENT",
    "CRITERES",
    "EXPLICATIONS",
    "NIVEAUX",
    "VARIABLES",
    "carte",
    "comparables",
    "comparer",
    "cote_a_cote",
    "explication_carte",
    "frequents",
    "instruments_communs",
    "ligne_psi",
    "mesures",
    "plages",
    "points",
    "portrait",
    "resume",
    "separer",
    "variables_communes",
]
