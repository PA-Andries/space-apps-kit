"""Les calculs du comparateur : quelles investigations se comparent, et sur quoi.

Deux investigations sont d'autant plus comparables qu'elles brûlent le même type de
combustible dans le même matériel. Les textes renvoyés pour l'affichage sont en anglais.
"""

import pandas as pd

from flame.commun import INCONNU

# Les critères lus dans la fiche de chaque investigation.
CRITERES = ["type_combustible", "materiel", "nb_tests"]

# Les conditions de test chiffrées, lues dans le tableau des tests.
VARIABLES = ["oxygene_pct", "pression_kpa", "debit_air_cm_s"]

NIVEAUX = {
    1: "Directly comparable",
    2: "Comparable in principle",
    3: "Complementary",
}
# Nom et unité de chaque condition de test, pour les phrases du résumé.
NOMS_VARIABLES = {
    "oxygene_pct": ("oxygen", "%"),
    "pression_kpa": ("pressure", "kPa"),
    "debit_air_cm_s": ("air flow", "cm/s"),
}
# En dessous de ce nombre de points distincts, un graphique n'apprend rien de plus que le résumé.
MINIMUM_DE_POINTS = 5

EXPLICATIONS = {
    1: "Same fuel type in the same hardware: results can be read side by side.",
    2: "Same fuel type in different hardware: useful to see whether a result holds at another scale.",
    3: "Different fuel types: they answer different questions and share few or no numbers.",
}


def famille_combustible(type_combustible: object) -> str:
    """Le type de combustible sans sa précision : « gaz (modèle) » devient « gaz »."""
    if pd.isna(type_combustible):
        return INCONNU
    return str(type_combustible).split("(")[0].strip().lower() or INCONNU


def niveau_et_raison(depart: pd.Series, autre: pd.Series) -> tuple[int, str]:
    """Le niveau de comparabilité (1 à 3) de deux fiches, et la phrase qui l'explique."""
    meme_materiel = pd.notna(depart["materiel"]) and depart["materiel"] == autre["materiel"]
    combustible_depart = famille_combustible(depart["type_combustible"])
    if INCONNU in (combustible_depart, famille_combustible(autre["type_combustible"])):
        return 3, "Fuel type unknown"
    if combustible_depart != famille_combustible(autre["type_combustible"]):
        return 3, "Same hardware, different fuel type" if meme_materiel else "Different fuel type and hardware"
    if meme_materiel:
        return 1, "Same fuel type and same hardware"
    return 2, "Same fuel type, different hardware"


def variables_communes(tests: pd.DataFrame, ids: list[str]) -> list[str]:
    """Les conditions de test chiffrées pour toutes les investigations de `ids`."""
    remplies = tests[tests["investigation_id"].isin(ids)].groupby("investigation_id")[VARIABLES].count()
    remplies = remplies.reindex(ids, fill_value=0)
    return [variable for variable in VARIABLES if (remplies[variable] > 0).all()]


def comparables(fiches: pd.DataFrame, tests: pd.DataFrame, id_depart: str) -> pd.DataFrame:
    """Les autres investigations, de la plus comparable à la moins comparable à `id_depart`.

    Ajoute les colonnes `niveau` (1 à 3), `raison` et `variables_communes` (liste de noms de colonnes).
    """
    depart = fiches[fiches["id"] == id_depart].iloc[0]
    autres = fiches[fiches["id"] != id_depart].copy()
    jugements = [niveau_et_raison(depart, autre) for _, autre in autres.iterrows()]
    autres["niveau"] = [niveau for niveau, _ in jugements]
    autres["raison"] = [raison for _, raison in jugements]
    autres["variables_communes"] = [variables_communes(tests, [id_depart, autre]) for autre in autres["id"]]
    autres["_nb_communes"] = autres["variables_communes"].str.len()
    autres = autres.sort_values(["niveau", "_nb_communes", "id"], ascending=[True, False, True], kind="stable")
    return autres.drop(columns="_nb_communes").reset_index(drop=True)


def comparer(fiches: pd.DataFrame, ids: list[str]) -> pd.DataFrame:
    """Un tableau avec une ligne par critère et une colonne par investigation de `ids`."""
    choisies = fiches.set_index("id").loc[ids, CRITERES]
    return choisies.T.rename_axis("critère")


def plages(tests: pd.DataFrame, ids: list[str]) -> pd.DataFrame:
    """La plage testée de chaque condition : une ligne par variable, une colonne par investigation."""
    colonnes = {}
    for investigation in ids:
        valeurs = tests[tests["investigation_id"] == investigation][VARIABLES]
        colonnes[investigation] = [_plage(valeurs[variable].dropna()) for variable in VARIABLES]
    return pd.DataFrame(colonnes, index=VARIABLES).rename_axis("critère")


def _plage(valeurs: pd.Series) -> str:
    return INCONNU if valeurs.empty else ecrire_plage(valeurs.min(), valeurs.max())


def separer(tableau: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Coupe un tableau de comparaison en trois : points communs, différences, lignes inconnues partout."""
    texte = tableau.astype("object").where(tableau.notna(), INCONNU).astype(str)
    inconnues = (texte == INCONNU).all(axis=1)
    identiques = (texte.nunique(axis=1) == 1) & ~inconnues
    return texte[identiques], texte[~identiques & ~inconnues], texte[inconnues]


def points(tests: pd.DataFrame, ids: list[str], variables: list[str]) -> pd.DataFrame:
    """Les lignes de tests de `ids` où toutes les `variables` sont chiffrées, prêtes à tracer."""
    choisis = tests[tests["investigation_id"].isin(ids)]
    return choisis.dropna(subset=variables).reset_index(drop=True)


def instruments_communs(fiches: pd.DataFrame, ids: list[str]) -> list[str]:
    """Les instruments de mesure cités dans la fiche de toutes les investigations de `ids`."""
    listes = [instruments_de(capteurs) for capteurs in fiches.set_index("id").loc[ids, "capteurs"]]
    return sorted(set.intersection(*listes))


def instruments_de(capteurs: object) -> set[str]:
    if pd.isna(capteurs):
        return set()
    return {instrument.strip() for instrument in str(capteurs).split(";") if instrument.strip()}


def carte(tests: pd.DataFrame, ids: list[str]) -> tuple[list[str], pd.DataFrame] | None:
    """Les deux axes et les points du graphique, ou None quand il n'apprendrait rien.

    Il faut deux conditions chiffrées pour toutes les investigations, et assez de points distincts.
    """
    communes = variables_communes(tests, ids)
    if len(communes) < 2:
        return None
    axes = communes[:2]
    a_tracer = points(tests, ids, axes)
    if a_tracer["investigation_id"].nunique() < len(ids) or len(a_tracer[axes].drop_duplicates()) < MINIMUM_DE_POINTS:
        return None
    return axes, a_tracer


def etendues(tests: pd.DataFrame, ids: list[str], variable: str) -> dict[str, tuple[float, float]]:
    """Le minimum et le maximum de `variable` pour chaque investigation qui a des valeurs."""
    etendues = {}
    for investigation in ids:
        valeurs = tests[tests["investigation_id"] == investigation][variable].dropna()
        if not valeurs.empty:
            etendues[investigation] = (valeurs.min(), valeurs.max())
    return etendues


def ecrire_plage(mini: float, maxi: float) -> str:
    return f"{mini:g}" if mini == maxi else f"{mini:g} to {maxi:g}"
