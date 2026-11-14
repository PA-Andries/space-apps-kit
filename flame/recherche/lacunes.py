"""« Ce qu'on ne sait pas » : les trous des données NASA pour un environnement.

Tout est compté sur les vrais tests (`data/tests.csv`) et sur les atmosphères sourcées de
`data/psi/habitats.csv` (rôle B). Rien n'est deviné : une valeur absente est dite absente.
Les phrases s'affichent sur le site : elles sont en anglais.
"""

import pandas as pd

from flame.commun import charger_table_psi
from flame.recherche.texte import simplifier
from flame.ui import label

# La ligne de data/psi/habitats.csv qui décrit l'atmosphère de chaque habitat du contrat.
# Hypothèse (la même que relevance.csv) : un vaisseau a le même air que l'ISS.
HABITAT_ATMOSPHERE = {
    "Vaisseau": "iss",
    "Station": "iss",
    "Base lunaire": "moon_base",
    "Base martienne": "mars_base",
    "Rover pressurisé": "pressurized_rover",
}
# Comme relevance.csv : l'air de l'ISS (21 %) est compté de 19 à 23 % d'oxygène.
TOLERANCE_OXYGENE_PCT = 2
KPA_PAR_PSI = 6.894757
TYPES_COMBUSTIBLE = ["solide", "liquide", "gaz"]
# Classé « solide », mais sa fiche dit « Gas burner that emulates a burning material » : pas un vrai échantillon.
EMULATEURS_DE_SOLIDE = {"PSI-20": "ACME BRE"}
# Pour dire « des fiches sans oxygène » : les colonnes vérifiées et leur nom affiché.
CHAMPS_SUIVIS = {"oxygene_min": "oxygen range", "pression_kpa": "pressure", "nb_tests": "number of tests"}


def charger_atmospheres() -> pd.DataFrame:
    """La table `habitats` du rôle B (vide si elle n'existe pas, par exemple sur les données d'exemple)."""
    return charger_table_psi("habitats")


def _type_de_base(type_combustible: object) -> str:
    """« solide (modèle) » -> « solide » ; une valeur vide reste vide."""
    return simplifier(str(type_combustible).split("(")[0]) if pd.notna(type_combustible) else ""


def _est_vide(valeur: object) -> bool:
    return pd.isna(pd.to_numeric(valeur, errors="coerce"))


def tests_dans_l_environnement(tests: pd.DataFrame, atmosphere: pd.Series) -> pd.DataFrame:
    """Les tests faits dans l'oxygène et la pression d'une ligne de `habitats` (un test sans mesure n'y est pas)."""
    oxygene = pd.to_numeric(tests["oxygene_pct"], errors="coerce")
    pression = pd.to_numeric(tests["pression_kpa"], errors="coerce")
    oxygene_min, oxygene_max = atmosphere.get("o2_pct_min"), atmosphere.get("o2_pct_max")
    pression_max_psi = atmosphere.get("pressure_psi_max")
    if pd.notna(oxygene_max) and oxygene_max == oxygene_min:  # une valeur fixe, comme l'air de l'ISS
        garder = oxygene.between(oxygene_min - TOLERANCE_OXYGENE_PCT, oxygene_max + TOLERANCE_OXYGENE_PCT)
    else:  # une zone : « au moins 30 % » pour la Lune et le rover
        garder = oxygene >= oxygene_min
    if pd.notna(pression_max_psi) and oxygene_min != oxygene_max:
        garder &= pression <= pression_max_psi * KPA_PAR_PSI
    return tests[garder]


def ce_qu_on_ne_sait_pas(
    habitat: str,
    fiches: pd.DataFrame,
    tests: pd.DataFrame,
    atmospheres: pd.DataFrame | None = None,
) -> list[str]:
    """Les trous des données pour `habitat`, en phrases courtes : conditions jamais testées, gravité, champs vides."""
    if atmospheres is None:
        atmospheres = charger_atmospheres()
    constats: list[str] = []
    nom = label(habitat)
    types = fiches.set_index("id")["type_combustible"].map(_type_de_base)
    tests = tests.assign(type_de_base=tests["investigation_id"].map(types).fillna(""))

    lignes = (
        atmospheres[atmospheres["habitat_id"] == HABITAT_ATMOSPHERE.get(habitat)]
        if not atmospheres.empty
        else atmospheres
    )
    atmosphere = None if lignes.empty else lignes.iloc[0]
    if atmosphere is None:
        constats.append(f"The atmosphere of the {nom} is not available: no test can be matched to it.")
    elif pd.isna(atmosphere.get("o2_pct_min")):
        constats.append(
            f"The statement gives no oxygen or pressure for the {nom}: no NASA test can be placed in its conditions."
        )
    else:
        dedans = tests_dans_l_environnement(tests, atmosphere)
        for type_combustible in TYPES_COMBUSTIBLE:
            du_type = dedans[dedans["type_de_base"] == type_combustible]
            if du_type.empty:
                constats.append(f"No {label(type_combustible)}-fuel test was run in the atmosphere of the {nom}.")
            else:
                constats.append(
                    f"{len(du_type)} {label(type_combustible)}-fuel test(s), from "
                    f"{du_type['investigation_id'].nunique()} investigation(s), match the atmosphere of the {nom}."
                )

    solides = tests[tests["type_de_base"] == "solide"]
    vrais_solides = solides[~solides["investigation_id"].isin(EMULATEURS_DE_SOLIDE)]
    oxygene_vrais = pd.to_numeric(vrais_solides["oxygene_pct"], errors="coerce")
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

    gravite = None if atmosphere is None else pd.to_numeric(atmosphere.get("gravity_g"), errors="coerce")
    if gravite is not None and pd.notna(gravite) and 0 < gravite < 1:
        constats.append(
            f"No test at the partial gravity of the {nom}: PSI has microgravity and Earth-gravity data only. "
            "E-FIELD Flames mimics partial gravity with an electric field."
        )

    for colonne, nom_champ in CHAMPS_SUIVIS.items():
        vides = fiches[colonne].map(_est_vide).sum() if colonne in fiches.columns else 0
        if vides:
            constats.append(f"{vides} of {len(fiches)} investigations have no recorded {nom_champ}.")
    return constats


def champs_inconnus(fiche: pd.Series) -> list[str]:
    """Les informations absentes d'une fiche, avec leur nom affiché (pour l'onglet de la fiche)."""
    return [nom for colonne, nom in CHAMPS_SUIVIS.items() if _est_vide(fiche.get(colonne))]
