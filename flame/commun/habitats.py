"""Les conditions de vie de chaque habitat, avec la source de chaque valeur.

Une plage s'écrit (minimum, maximum) ; `None` veut dire « pas de borne » ou « inconnu ».
On ne devine jamais : ce que l'énoncé du défi ne donne pas reste `None`, avec la source « inconnu ».
"""

import pandas as pd

from flame.commun.constantes import INCONNU

# Nom d'habitat à utiliser quand l'utilisateur saisit ses propres conditions.
HABITAT_PERSONNALISE = "Personnalisé"

# D'où vient une valeur : de l'énoncé du défi NASA, d'une hypothèse de l'équipe qui reste à sourcer, ou de nulle part.
SOURCE_ENONCE = "énoncé"
SOURCE_A_SOURCER = "à sourcer"
SOURCE_INCONNUE = INCONNU

# Vaisseau et station : 21 % d'oxygène et 101 kPa, avec la tolérance choisie par l'équipe. À sourcer.
_ORBITE = {
    "oxygene_pct": (19.0, 23.0),
    "pression_kpa": (90.0, 110.0),
    "gravite": 0.0,
    "sources": {"oxygene_pct": SOURCE_A_SOURCER, "pression_kpa": SOURCE_A_SOURCER, "gravite": SOURCE_A_SOURCER},
}
# Base lunaire et rover : l'énoncé dit 30 % d'oxygène ou plus, et 10,2 psi (70,3 kPa) ou moins. C'est une zone.
_LUNE = {
    "oxygene_pct": (30.0, None),
    "pression_kpa": (None, 70.3),
    "gravite": 0.165,
    "sources": {"oxygene_pct": SOURCE_ENONCE, "pression_kpa": SOURCE_ENONCE, "gravite": SOURCE_A_SOURCER},
}
# Base martienne : l'énoncé ne donne aucun chiffre d'atmosphère.
_MARS = {
    "oxygene_pct": (None, None),
    "pression_kpa": (None, None),
    "gravite": 0.38,
    "sources": {"oxygene_pct": SOURCE_INCONNUE, "pression_kpa": SOURCE_INCONNUE, "gravite": SOURCE_A_SOURCER},
}
_SANS_VALEUR = {
    "oxygene_pct": (None, None),
    "pression_kpa": (None, None),
    "gravite": None,
    "sources": {"oxygene_pct": SOURCE_INCONNUE, "pression_kpa": SOURCE_INCONNUE, "gravite": SOURCE_INCONNUE},
}
_CONDITIONS = {
    "Vaisseau": _ORBITE,
    "Station": _ORBITE,
    "Base lunaire": _LUNE,
    "Rover pressurisé": _LUNE,
    "Base martienne": _MARS,
    HABITAT_PERSONNALISE: _SANS_VALEUR,
}


def conditions_habitat(habitat: str) -> dict:
    """Les conditions de `habitat` : `oxygene_pct` et `pression_kpa` en plages, `gravite` en g, et `sources`.

    `sources` donne, pour chacune des trois clés, « énoncé », « à sourcer » ou « inconnu ».
    Un habitat qui n'est pas dans la liste (dont « Personnalisé ») n'a aucune valeur : tout est inconnu.
    """
    conditions = _CONDITIONS.get(habitat, _SANS_VALEUR)
    return {**conditions, "sources": dict(conditions["sources"])}


def dans_la_plage(valeurs: pd.Series, plage: tuple) -> pd.Series:
    """Vrai pour chaque valeur de `valeurs` qui tombe dans `plage`, bornes comprises.

    `plage` s'écrit (minimum, maximum), comme dans le scénario ; `None` veut dire « pas de borne ».
    Sans aucune borne, tout passe. Dès qu'il y a une borne, une valeur absente ne passe pas :
    on ne sait pas si elle respecte la plage, donc on ne la compte pas.
    """
    mini, maxi = plage
    if mini is None and maxi is None:
        return pd.Series(True, index=valeurs.index)
    nombres = pd.to_numeric(valeurs, errors="coerce")
    dedans = nombres.notna()
    if mini is not None:
        dedans &= nombres >= mini
    if maxi is not None:
        dedans &= nombres <= maxi
    return dedans
