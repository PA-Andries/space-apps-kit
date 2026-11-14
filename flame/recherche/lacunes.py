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

    solides = tests[tests["type_de_base"] == "solide"]
    vrais = solides[~solides["investigation_id"].isin(EMULATEURS_DE_SOLIDE)]
    oxygene_vrais = pd.to_numeric(vrais["oxygene_pct"], errors="coerce")
    if oxygene_vrais.notna().any():
        phrase = (
            f"No real solid sample (fabric, plastic) was tested above {oxygene_vrais.max():g} % oxygen in PSI's tables."
        )
        emules = solides[solides["investigation_id"].isin(EMULATEURS_DE_SOLIDE)]
        oxygene_emules = pd.to_numeric(emules["oxygene_pct"], errors="coerce")
        if oxygene_emules.notna().any() and oxygene_emules.max() > oxygene_vrais.max():
            noms = ", ".join(sorted(EMULATEURS_DE_SOLIDE[i] for i in emules["investigation_id"].unique()))
            phrase += (
                f" Only {noms}, a gas burner that emulates a burning solid, goes up to {oxygene_emules.max():g} %."
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


def champs_inconnus(fiche: pd.Series) -> list[str]:
    """Les informations absentes d'une fiche, avec leur nom affiché (pour l'onglet de la fiche)."""
    return [nom for colonne, nom in CHAMPS_SUIVIS.items() if _est_vide(fiche.get(colonne))]
