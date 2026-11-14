"""Version de départ du comparateur : un tableau, une colonne par investigation.

À faire par le rôle D : faire ressortir les différences, situer les conditions testées
par rapport à l'atmosphère de l'habitat (`ATMOSPHERES`), utiliser `charger_tests()`.
"""

import pandas as pd

CRITERES = [
    "nom",
    "pilier",
    "type_combustible",
    "combustible",
    "materiel",
    "oxygene_min",
    "oxygene_max",
    "pression_kpa",
    "debit_air",
    "nb_tests",
]


def comparer(fiches: pd.DataFrame, ids: list[str]) -> pd.DataFrame:
    """Un tableau avec une ligne par critère et une colonne par investigation de `ids`."""
    choisies = fiches.set_index("id").loc[ids, CRITERES]
    return choisies.T.rename_axis("critère")
