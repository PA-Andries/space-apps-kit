"""Le contrat partagé par toutes les pages. Propriétaire : rôle A (Intégration).

Tout ce qui est importable depuis d'autres dossiers est listé ici.
Pour changer quoi que ce soit dans ce dossier, on passe par le rôle A.
"""

from flame.commun.constantes import (
    ATMOSPHERES,
    COLONNES_FICHES,
    COLONNES_PUBLICATIONS,
    COLONNES_TESTS,
    HABITATS,
    INCONNU,
    PILIERS,
    PROFILS,
    TYPES_COMBUSTIBLE,
)
from flame.commun.donnees import (
    TABLES_PSI,
    charger_fiches,
    charger_publications,
    charger_table_psi,
    charger_tests,
    donnees_exemple,
)
from flame.commun.habitats import HABITAT_PERSONNALISE, conditions_habitat, dans_la_plage
from flame.commun.scenario import get_scenario, set_scenario

__all__ = [
    "ATMOSPHERES",
    "COLONNES_FICHES",
    "COLONNES_PUBLICATIONS",
    "COLONNES_TESTS",
    "HABITATS",
    "HABITAT_PERSONNALISE",
    "INCONNU",
    "PILIERS",
    "PROFILS",
    "TABLES_PSI",
    "TYPES_COMBUSTIBLE",
    "charger_fiches",
    "charger_publications",
    "charger_table_psi",
    "charger_tests",
    "conditions_habitat",
    "dans_la_plage",
    "donnees_exemple",
    "get_scenario",
    "set_scenario",
]
