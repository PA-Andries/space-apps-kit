"""Les données des visuels de « What we don't know » : la grille de couverture et les règles de l'oxygène et
de la pression. Les mêmes comptes que `ce_quon_ne_sait_pas`, rendus sous forme de tableaux.

Rien n'est dessiné ici (voir `vue_lacunes`) et rien n'est deviné : une valeur absente reste None.
"""

import pandas as pd

from flame.commun import TYPES_COMBUSTIBLE
from flame.recherche.conditions import atmosphere_connue, decrire_plages, plages_du_scenario, tests_dans_les_plages
from flame.recherche.lacunes import EMULATEURS_DE_SOLIDE
from flame.recherche.score import type_de_base
from flame.ui import label

# Les plages qu'un rapport NASA écrit noir sur blanc quand les tableaux de tests de PSI n'en donnent aucune.
# Clé : (colonne, type de combustible). `citation` est recopiée telle quelle du rapport (vérifiée par un test).
PLAGES_DES_RAPPORTS = {
    ("pression_kpa", "solide"): {
        "plage": (99.2, 99.5),
        "investigation": "PSI-25",
        "fichier": "BASS-II_Summary_Report.pdf.txt",
        "page": 46,
        "source": "BASS-II report, p. 46",
        "citation": "varied from 99.2 to 99.5 kPa in the tests reported",
    },
}


def _types_des_tests(fiches: pd.DataFrame, tests: pd.DataFrame) -> pd.Series:
    types = fiches.set_index("id")["type_combustible"].map(type_de_base)
    return tests["investigation_id"].map(types).fillna("")


def _combustibles(scenario: dict) -> list:
    return list(scenario.get("type_combustible") or TYPES_COMBUSTIBLE)


def couverture(fiches: pd.DataFrame, tests: pd.DataFrame, scenario: dict | None) -> dict:
    """La grille « combustible × atmosphère » de l'environnement.

    {"atmosphere": les plages en mots, ou None si l'atmosphère est inconnue,
     "cases": une case par combustible choisi (tous si aucun) :
        {"type", "nom", "tests", "investigations", "emule_seulement"}}
    `emule_seulement` : les seuls tests dans l'atmosphère viennent d'un brûleur qui imite un solide.
    """
    scenario = scenario or {}
    connue = atmosphere_connue(scenario)
    dedans = tests_dans_les_plages(tests, scenario) if connue else tests.iloc[0:0]
    types = _types_des_tests(fiches, dedans)
    cases = []
    for type_combustible in _combustibles(scenario):
        du_type = dedans[types == type_combustible]
        emules = du_type["investigation_id"].isin(EMULATEURS_DE_SOLIDE)
        cases.append(
            {
                "type": type_combustible,
                "nom": label(type_combustible),
                "tests": len(du_type) if connue else None,
                "investigations": du_type["investigation_id"].nunique() if connue else None,
                "emule_seulement": bool(len(du_type)) and bool(emules.all()),
            }
        )
    return {"atmosphere": decrire_plages(scenario) if connue else None, "cases": cases}


def _trous(plage: tuple[float, float], environnement: tuple) -> list[tuple]:
    """Les morceaux de l'environnement jamais testés pour un combustible, depuis le bord de sa plage testée.

    Au-dessus : de la valeur testée la plus haute jusqu'au haut de l'environnement (None = sans borne) ;
    au-dessous : du bas de l'environnement (None = sans borne) jusqu'à la valeur testée la plus basse.
    Quand l'environnement est entièrement hors de la plage, le trou le contient donc tout entier.
    """
    bas, haut = plage
    env_min, env_max = environnement
    trous = []
    if env_max is None or env_max > haut:
        trous.append((haut, env_max))
    if env_min is None or env_min < bas:
        trous.append((env_min, bas))
    return trous


def regle(fiches: pd.DataFrame, tests: pd.DataFrame, scenario: dict | None, colonne: str) -> dict:
    """La règle d'une condition (`colonne` : "oxygene_pct" ou "pression_kpa") : la plage testée de chaque
    combustible face à celle de l'environnement.

    {"environnement": (min, max) de l'environnement (None = pas de borne), ou (None, None) s'il est inconnu,
     "combustibles": [{"type", "nom", "plage": (min, max) ou None, "source": None ou un rapport, "trous": [(de, à)]}],
     "emule": la valeur la plus haute d'un émulateur de solide, ou None, "emulateurs": leurs noms}
    Les émulateurs de solide (des brûleurs à gaz) ne comptent pas dans la plage des solides.
    Quand aucun test n'a de valeur mais qu'un rapport NASA en donne une (`PLAGES_DES_RAPPORTS`), la plage vient
    du rapport et `source` le nomme ; sinon `source` vaut None.
    `trous` : ce que l'environnement demande et qu'aucun test du combustible n'a atteint (voir `_trous`) ;
    vide si l'environnement est inconnu.
    """
    scenario = scenario or {}
    environnement = plages_du_scenario(scenario)[colonne]
    connu = any(borne is not None for borne in environnement)
    vrais = tests[~tests["investigation_id"].isin(EMULATEURS_DE_SOLIDE)]
    types = _types_des_tests(fiches, vrais)
    valeurs_tests = pd.to_numeric(vrais[colonne], errors="coerce")
    combustibles = []
    for type_combustible in _combustibles(scenario):
        valeurs = valeurs_tests[types == type_combustible].dropna()
        plage = (float(valeurs.min()), float(valeurs.max())) if len(valeurs) else None
        source = None
        rapport = PLAGES_DES_RAPPORTS.get((colonne, type_combustible))
        if plage is None and rapport is not None:
            plage, source = rapport["plage"], rapport["source"]
        combustibles.append(
            {
                "type": type_combustible,
                "nom": label(type_combustible),
                "plage": plage,
                "source": source,
                "trous": _trous(plage, environnement) if plage is not None and connu else [],
            }
        )
    emules = tests[tests["investigation_id"].isin(EMULATEURS_DE_SOLIDE)]
    valeurs_emules = pd.to_numeric(emules[colonne], errors="coerce").dropna()
    return {
        "environnement": environnement,
        "combustibles": combustibles,
        "emule": float(valeurs_emules.max()) if len(valeurs_emules) else None,
        "emulateurs": ", ".join(sorted(EMULATEURS_DE_SOLIDE[i] for i in emules["investigation_id"].unique())),
    }


def regle_de_l_oxygene(fiches: pd.DataFrame, tests: pd.DataFrame, scenario: dict | None) -> dict:
    """La règle de l'oxygène (%) : voir `regle`."""
    return regle(fiches, tests, scenario, "oxygene_pct")


def regle_de_la_pression(fiches: pd.DataFrame, tests: pd.DataFrame, scenario: dict | None) -> dict:
    """La règle de la pression (kPa) : voir `regle`. Aucun test de solide n'a de pression dans les tableaux de
    PSI : celle des solides vient du rapport de BASS-II (`PLAGES_DES_RAPPORTS`)."""
    return regle(fiches, tests, scenario, "pression_kpa")
