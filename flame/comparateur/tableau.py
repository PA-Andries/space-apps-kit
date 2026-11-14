"""Les tableaux de la page Data : les tests de l'environnement, ce que chaque investigation fait varier, ses capteurs.

Chaque ligne vient des tables de NASA. Une valeur absente reste absente. Les titres de colonnes sont en anglais.
"""

import pandas as pd

from flame.comparateur.comparaison import NOMS_VARIABLES, VARIABLES, ecrire_plage
from flame.comparateur.conditions import environnement_defini, tests_correspondants
from flame.comparateur.details import ABSENT

# Colonnes du tableau des tests : nom dans les données, titre affiché et écrit dans le CSV.
COLONNES_TESTS = {
    "investigation_id": "Investigation id",
    "investigation": "Investigation",
    "test_id": "Test",
    "combustible": "Fuel",
    "oxygene_pct": "Oxygen (%)",
    "pression_kpa": "Pressure (kPa)",
    "debit_air_cm_s": "Air flow (cm/s)",
    "resultat": "Result",
    "source": "Source",
}
COLONNES_CAPTEURS = {
    "investigation": "Investigation",
    "instrument": "Instrument",
    "measures": "What it measures",
    "unit": "Unit",
    "basis": "Described in",
    "source": "Source document",
}


def tableau_des_tests(tests: pd.DataFrame, fiches: pd.DataFrame, scenario: dict, tous: bool = False) -> pd.DataFrame:
    """Les tests de l'environnement, prêts à afficher et à télécharger.

    Avec `tous`, ou quand l'environnement ne donne aucune condition, tous les tests sont renvoyés.
    """
    lignes = tests if tous or not environnement_defini(scenario) else tests_correspondants(tests, fiches, scenario)
    noms = dict(zip(fiches["id"], fiches["nom"], strict=True))
    lignes = lignes.assign(
        investigation=lignes["investigation_id"].map(lambda identifiant: noms.get(identifiant, identifiant))
    )
    return lignes[list(COLONNES_TESTS)].rename(columns=COLONNES_TESTS).reset_index(drop=True)


def ce_qui_varie(tests: pd.DataFrame, fiches: pd.DataFrame) -> pd.DataFrame:
    """Pour chaque investigation qui a des tests : la plage de chaque condition et ce qui change d'un test à l'autre."""
    noms = dict(zip(fiches["id"], fiches["nom"], strict=True))
    lignes = []
    for identifiant, groupe in tests.groupby("investigation_id", sort=False):
        ligne = {"Investigation": noms.get(identifiant, identifiant), "Test rows": len(groupe)}
        change = []
        for variable in VARIABLES:
            nom, unite = NOMS_VARIABLES[variable]
            valeurs = groupe[variable].dropna()
            ligne[f"{nom.capitalize()} ({unite})"] = (
                ABSENT if valeurs.empty else ecrire_plage(valeurs.min(), valeurs.max())
            )
            if valeurs.nunique() > 1:
                change.append(nom)
        combustibles = groupe["combustible"].nunique()
        ligne["Fuels"] = combustibles
        if combustibles > 1:
            change.append("fuel")
        ligne["What varies"] = ", ".join(change) or "nothing recorded"
        lignes.append(ligne)
    return pd.DataFrame(lignes).sort_values("Test rows", ascending=False, kind="stable").reset_index(drop=True)


def capteurs(mesures_psi: pd.DataFrame, fiches: pd.DataFrame, ids: list[str] | None = None) -> pd.DataFrame:
    """Les instruments de mesure de `measurements.csv`, pour toutes les investigations ou seulement pour `ids`.

    Renvoie un tableau vide quand la table de PSI n'est pas disponible.
    """
    if mesures_psi.empty:
        return pd.DataFrame(columns=list(COLONNES_CAPTEURS.values()))
    noms = dict(zip(fiches["id"], fiches["nom"], strict=True))
    lignes = mesures_psi if not ids else mesures_psi[mesures_psi["investigation_id"].isin(ids)]
    lignes = lignes.assign(
        investigation=lignes["investigation_id"].map(lambda identifiant: noms.get(identifiant, identifiant))
    )
    return lignes[list(COLONNES_CAPTEURS)].rename(columns=COLONNES_CAPTEURS).reset_index(drop=True)
