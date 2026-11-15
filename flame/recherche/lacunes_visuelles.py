"""Les données des visuels de « What we don't know » : la grille de couverture, la règle de l'oxygène et les
mesures notées par NASA. Les mêmes comptes que `ce_quon_ne_sait_pas`, rendus sous forme de tableaux.

Rien n'est dessiné ici (voir `vue_lacunes`) et rien n'est deviné : une valeur absente reste None.
"""

import pandas as pd

from flame.commun import TYPES_COMBUSTIBLE
from flame.recherche.conditions import atmosphere_connue, decrire_plages, plages_du_scenario, tests_dans_les_plages
from flame.recherche.lacunes import EMULATEURS_DE_SOLIDE, frontiere_des_solides
from flame.recherche.score import type_de_base
from flame.ui import label

# Les mesures suivies pour « des fiches sans oxygène ni pression » : la colonne et son nom affiché.
MESURES_SUIVIES = {"oxygene_min": "Oxygen range", "pression_kpa": "Pressure"}


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


def regle_de_l_oxygene(fiches: pd.DataFrame, tests: pd.DataFrame, scenario: dict | None) -> dict:
    """La règle de l'oxygène : la plage testée de chaque combustible face à celle de l'environnement.

    {"environnement": (min, max) d'oxygène de l'environnement (None = pas de borne),
     "combustibles": [{"type", "nom", "plage": (min, max) ou None, "trou": (de, à) ou None, "ecart": % ou None}],
     "emule": l'oxygène le plus haut d'un émulateur de solide, ou None, "emulateurs": leurs noms}
    Les émulateurs de solide (des brûleurs à gaz) ne comptent pas dans la plage des solides.
    `trou` : l'oxygène jamais testé entre la plage du combustible et celle de l'environnement ; `ecart` sa largeur.
    """
    scenario = scenario or {}
    environnement = plages_du_scenario(scenario)["oxygene_pct"]
    env_min, env_max = environnement
    vrais = tests[~tests["investigation_id"].isin(EMULATEURS_DE_SOLIDE)]
    types = _types_des_tests(fiches, vrais)
    oxygene = pd.to_numeric(vrais["oxygene_pct"], errors="coerce")
    combustibles = []
    for type_combustible in _combustibles(scenario):
        valeurs = oxygene[types == type_combustible].dropna()
        plage = (float(valeurs.min()), float(valeurs.max())) if len(valeurs) else None
        trou = None
        if plage is not None and env_min is not None and env_min > plage[1]:
            trou = (plage[1], float(env_min))
        elif plage is not None and env_max is not None and env_max < plage[0]:
            trou = (float(env_max), plage[0])
        combustibles.append(
            {
                "type": type_combustible,
                "nom": label(type_combustible),
                "plage": plage,
                "trou": trou,
                "ecart": round(trou[1] - trou[0], 1) if trou else None,
            }
        )
    frontiere = frontiere_des_solides(fiches, tests)
    return {
        "environnement": environnement,
        "combustibles": combustibles,
        "emule": frontiere["emule"],
        "emulateurs": frontiere["emulateurs"],
    }


def mesures_notees(fiches: pd.DataFrame) -> dict[str, list[tuple[str, bool]]]:
    """Pour l'oxygène et la pression : chaque investigation (son nom) et si NASA a noté la mesure."""
    resultat = {}
    for colonne, nom in MESURES_SUIVIES.items():
        valeurs = pd.to_numeric(fiches[colonne], errors="coerce") if colonne in fiches.columns else None
        resultat[nom] = [
            (str(fiche["nom"]), valeurs is not None and pd.notna(valeurs.loc[index]))
            for index, fiche in fiches.iterrows()
        ]
    return resultat
