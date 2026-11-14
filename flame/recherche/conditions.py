"""Les tests qui tombent dans l'environnement de l'utilisateur (plages d'oxygène et de pression du scénario).

La règle de plage est `dans_la_plage` du rôle A, partagée avec le lot D (`flame.recherche` n'a pas le droit
d'importer `flame.comparateur`).
- Une plage est un couple (minimum, maximum) ; None = pas de borne.
- Si une plage d'oxygène est donnée, un test sans oxygène noté n'y est pas.
- Une plage de pression ne retire que les tests dont la pression est notée (beaucoup de tests de solides
  n'ont pas de pression dans les tables PSI).
"""

import pandas as pd

from flame.commun import HABITAT_PERSONNALISE, conditions_habitat, dans_la_plage
from flame.ui import label

PLAGE_VIDE = (None, None)


def _plage(scenario: dict | None, cle: str) -> tuple:
    """La plage `cle` du scénario ; si elle manque (ancien scénario), celle de l'habitat."""
    scenario = scenario or {}
    if cle in scenario and scenario[cle] is not None:
        minimum, maximum = scenario[cle]
        return (minimum, maximum)
    habitat = scenario.get("habitat")
    if habitat:
        return tuple(conditions_habitat(habitat).get(cle) or PLAGE_VIDE)
    return PLAGE_VIDE


def plages_du_scenario(scenario: dict | None) -> dict[str, tuple]:
    """Les plages d'oxygène (%) et de pression (kPa) de l'environnement choisi."""
    return {"oxygene_pct": _plage(scenario, "oxygene_pct"), "pression_kpa": _plage(scenario, "pression_kpa")}


def atmosphere_connue(scenario: dict | None) -> bool:
    """Vrai si l'environnement a au moins une borne d'oxygène ou de pression (faux pour Mars)."""
    return any(borne is not None for plage in plages_du_scenario(scenario).values() for borne in plage)


def tests_dans_les_plages(tests: pd.DataFrame, scenario: dict | None) -> pd.DataFrame:
    """Les tests dans les plages d'oxygène et de pression du scénario (tous si aucune plage n'est donnée).

    S'appuie sur `dans_la_plage` (rôle A), la règle partagée avec la page Compare.
    """
    plages = plages_du_scenario(scenario)
    garder = dans_la_plage(tests["oxygene_pct"], plages["oxygene_pct"])
    pression_notee = pd.to_numeric(tests["pression_kpa"], errors="coerce").notna()
    garder &= ~pression_notee | dans_la_plage(tests["pression_kpa"], plages["pression_kpa"])
    return tests[garder]


def decrire_plages(scenario: dict | None) -> str:
    """Les plages en mots, pour l'écran : « O2 ≥ 30 %, pressure ≤ 70.3 kPa »."""
    morceaux = []
    for cle, nom, unite in (("oxygene_pct", "O2", "%"), ("pression_kpa", "pressure", "kPa")):
        minimum, maximum = plages_du_scenario(scenario)[cle]
        if minimum is not None and maximum is not None:
            morceaux.append(f"{nom} {minimum:g} to {maximum:g} {unite}")
        elif minimum is not None:
            morceaux.append(f"{nom} ≥ {minimum:g} {unite}")
        elif maximum is not None:
            morceaux.append(f"{nom} ≤ {maximum:g} {unite}")
    return ", ".join(morceaux) or "no oxygen or pressure given"


def nom_de_l_environnement(scenario: dict | None) -> str:
    """Le nom affiché de l'habitat, ou « your custom environment »."""
    habitat = (scenario or {}).get("habitat")
    if not habitat or habitat == HABITAT_PERSONNALISE:
        return "your custom environment"
    return f"the {label(habitat)}"
