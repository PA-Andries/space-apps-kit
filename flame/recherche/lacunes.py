"""« Ce qu'on ne sait pas » : les trous des données NASA pour l'environnement de l'utilisateur.

Tout est compté sur les vrais tests (`data/tests.csv`) et sur les plages du scénario. Rien n'est deviné :
une valeur absente est dite absente. Les phrases s'affichent sur le site : elles sont en anglais.
"""

import pandas as pd

from flame.commun import TYPES_COMBUSTIBLE
from flame.recherche.conditions import (
    atmosphere_connue,
    decrire_plages,
    nom_de_l_environnement,
    plages_du_scenario,
    tests_dans_les_plages,
)
from flame.recherche.score import type_de_base
from flame.ui import label

# Classé « solide », mais sa fiche dit « Gas burner that emulates a burning material » : pas un vrai échantillon.
EMULATEURS_DE_SOLIDE = {"PSI-20": "ACME BRE"}
# Pour dire « des fiches sans oxygène » : les colonnes vérifiées et leur nom affiché.
CHAMPS_SUIVIS = {"oxygene_min": "oxygen range", "pression_kpa": "pressure", "nb_tests": "number of tests"}


def _est_vide(valeur: object) -> bool:
    return pd.isna(pd.to_numeric(valeur, errors="coerce"))


def frontiere_des_solides(fiches: pd.DataFrame, tests: pd.DataFrame) -> dict:
    """L'oxygène le plus haut auquel un vrai échantillon solide a été testé dans les tables de PSI.

    {"reel": %, "emule": % ou None, "emulateurs": "ACME BRE"} ; `reel` vaut None si aucun test solide
    n'a d'oxygène noté. Les émulateurs sont des brûleurs à gaz qui imitent un solide : ils montent plus
    haut, mais ce ne sont pas des échantillons.
    """
    types = fiches.set_index("id")["type_combustible"].map(type_de_base)
    solides = tests[tests["investigation_id"].map(types).fillna("") == "solide"]
    vrais = solides[~solides["investigation_id"].isin(EMULATEURS_DE_SOLIDE)]
    emules = solides[solides["investigation_id"].isin(EMULATEURS_DE_SOLIDE)]
    oxygene_vrais = pd.to_numeric(vrais["oxygene_pct"], errors="coerce")
    oxygene_emules = pd.to_numeric(emules["oxygene_pct"], errors="coerce")
    return {
        "reel": float(oxygene_vrais.max()) if oxygene_vrais.notna().any() else None,
        "emule": float(oxygene_emules.max()) if oxygene_emules.notna().any() else None,
        "emulateurs": ", ".join(sorted(EMULATEURS_DE_SOLIDE[i] for i in emules["investigation_id"].unique())),
    }


def ce_quon_ne_sait_pas(fiches: pd.DataFrame, tests: pd.DataFrame, scenario: dict | None) -> list[str]:
    """Les trous des données pour l'environnement de `scenario`, en phrases courtes appuyées sur les données."""
    scenario = scenario or {}
    constats: list[str] = []
    nom = nom_de_l_environnement(scenario)
    types = fiches.set_index("id")["type_combustible"].map(type_de_base)
    tests = tests.assign(type_de_base=tests["investigation_id"].map(types).fillna(""))

    if not atmosphere_connue(scenario):
        constats.append(
            f"The atmosphere of {nom} is unknown (no oxygen or pressure given): no test can be placed in it."
        )
    else:
        dedans = tests_dans_les_plages(tests, scenario)
        conditions = decrire_plages(scenario)
        for type_combustible in scenario.get("type_combustible") or TYPES_COMBUSTIBLE:
            du_type = dedans[dedans["type_de_base"] == type_combustible]
            nom_type = label(type_combustible)
            emules = du_type[du_type["investigation_id"].isin(EMULATEURS_DE_SOLIDE)]
            if not emules.empty and len(emules) == len(du_type):
                noms = ", ".join(sorted(EMULATEURS_DE_SOLIDE[i] for i in emules["investigation_id"].unique()))
                constats.append(
                    f"No real {nom_type} sample was tested at {conditions}: only {len(emules)} test(s) of {noms}, "
                    "a gas burner that emulates a burning solid."
                )
            elif du_type.empty:
                constats.append(f"No {nom_type}-fuel test was run at {conditions}.")
            else:
                constats.append(
                    f"{len(du_type)} {nom_type}-fuel test(s), from {du_type['investigation_id'].nunique()} "
                    f"investigation(s), were run at {conditions}."
                )

    frontiere = frontiere_des_solides(fiches, tests)
    if frontiere["reel"] is not None:
        phrase = (
            f"No real solid sample (fabric, plastic) was tested above {frontiere['reel']:g} % oxygen in PSI's tables."
        )
        if frontiere["emule"] is not None and frontiere["emule"] > frontiere["reel"]:
            phrase += (
                f" Only {frontiere['emulateurs']}, a gas burner that emulates a burning solid, "
                f"goes up to {frontiere['emule']:g} %."
            )
        constats.append(phrase)

    gravite = pd.to_numeric(scenario.get("gravite"), errors="coerce")
    if pd.isna(gravite):
        constats.append(f"The gravity of {nom} is unknown.")
    elif 0 < gravite < 1:
        constats.append(
            f"No test at the partial gravity of {nom} ({gravite:g} g): PSI has microgravity and Earth-gravity "
            "data only. E-FIELD Flames mimics partial gravity with an electric field."
        )

    for colonne, nom_champ in CHAMPS_SUIVIS.items():
        vides = int(fiches[colonne].map(_est_vide).sum()) if colonne in fiches.columns else 0
        if vides:
            constats.append(f"{vides} of {len(fiches)} investigations have no recorded {nom_champ}.")
    return constats


# Les expériences que l'énoncé annonce pour combler le trou de gravité partielle, et le substitut actuel.
A_VENIR_GRAVITE = "LUCI (Lunar-g Combustion Investigation) and FM2 (Flammability of Materials on the Moon)"
SUBSTITUT_GRAVITE = "ACME E-FIELD Flames mimics partial gravity with an electric field"

# Gravité d'un constat : 3 = la donnée manque là où l'utilisateur en a besoin, 1 = la donnée existe.
CRITIQUE, OK = 3, 1


def verdict(fiches: pd.DataFrame, tests: pd.DataFrame, scenario: dict | None) -> dict:
    """Le constat le plus grave pour cet environnement, prêt à devenir le titre de la page.

    {"niveau", "grave", "chiffre", "titre", "phrase", "source", "comblement"}. `chiffre` est la valeur à
    écrire en gros, `grave` dit s'il faut la peindre, et `comblement` dit ce qui remplira le trou, ou reste
    vide. Tout est compté sur les tables de PSI : aucun chiffre n'est estimé.
    """
    scenario = scenario or {}
    nom = nom_de_l_environnement(scenario)
    oxygene_mini = plages_du_scenario(scenario)["oxygene_pct"][0]
    gravite = pd.to_numeric(scenario.get("gravite"), errors="coerce")
    comblement = ""
    if pd.notna(gravite) and 0 < gravite < 1:
        comblement = (
            f"PSI holds no partial-gravity combustion data. {A_VENIR_GRAVITE} are expected to add it; "
            f"meanwhile {SUBSTITUT_GRAVITE}, and microgravity and Earth-gravity results bound what happens "
            f"at {gravite:g} g."
        )

    if not atmosphere_connue(scenario):
        return {
            "niveau": CRITIQUE,
            "grave": True,
            "chiffre": "—",
            "titre": f"No atmosphere is given for {nom}",
            "phrase": (
                f"The challenge statement names {nom} as a target habitat but gives no oxygen and no pressure. "
                "No NASA test can be placed in it, so this site shows none."
            ),
            "source": "NASA Space Apps challenge statement",
            "comblement": comblement,
        }

    # L'ordre compte : « aucun test du tout » passe avant « aucun solide assez haut », qui est plus précis
    # mais moins grave. Un scaphandre à 100 % d'oxygène n'a aucun test, pas seulement aucun solide.
    dedans = tests_dans_les_plages(tests, scenario)
    if dedans.empty:
        return {
            "niveau": CRITIQUE,
            "grave": True,
            "chiffre": "0",
            "titre": f"No NASA test matches the atmosphere of {nom}",
            "phrase": (
                f"No test of PSI's tables falls in {decrire_plages(scenario) or 'these conditions'}. "
                "Widen a slider to see the nearest tests."
            ),
            "source": "NASA PSI test tables",
            "comblement": comblement,
        }

    frontiere = frontiere_des_solides(fiches, tests)
    if frontiere["reel"] is not None and oxygene_mini is not None and frontiere["reel"] < oxygene_mini:
        emule = ""
        if frontiere["emule"] is not None and frontiere["emule"] > frontiere["reel"]:
            emule = (
                f" Only {frontiere['emulateurs']}, a gas burner that emulates a burning solid, "
                f"reaches {frontiere['emule']:g} %."
            )
        return {
            "niveau": CRITIQUE,
            "grave": True,
            "chiffre": f"{frontiere['reel']:g} %",
            "titre": "Solids have never been tested at your oxygen level",
            "phrase": (
                f"{frontiere['reel']:g} % is the highest oxygen at which a real solid sample (fabric, plastic) "
                f"was tested in PSI's tables. {nom[:1].upper()}{nom[1:]} starts at {oxygene_mini:g} %, so the "
                f"materials that line a habitat have no test at your conditions.{emule}"
            ),
            "source": "NASA PSI test tables",
            "comblement": comblement,
        }

    return {
        "niveau": OK,
        "grave": False,
        "chiffre": f"{len(dedans):,}",
        "titre": f"NASA tests match the atmosphere of {nom}",
        "phrase": (
            f"{len(dedans):,} test(s) of PSI's tables, from {dedans['investigation_id'].nunique()} "
            f"investigation(s), fall in {decrire_plages(scenario) or 'these conditions'}. They were run in "
            "orbit or on the ground at these conditions, not in the habitat itself."
        ),
        "source": "NASA PSI test tables",
        "comblement": comblement,
    }


def champs_inconnus(fiche: pd.Series) -> list[str]:
    """Les informations absentes d'une fiche, avec leur nom affiché (pour l'onglet de la fiche)."""
    return [nom for colonne, nom in CHAMPS_SUIVIS.items() if _est_vide(fiche.get(colonne))]
