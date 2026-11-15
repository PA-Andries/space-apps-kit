"""Les calculs du comparateur : quelles investigations se comparent, et sur quoi.

La règle ne s'appuie que sur ce que NASA ou l'énoncé du défi donnent, jamais sur un classement de l'équipe :
- directement comparables : le même matériel. L'énoncé regroupe lui-même les expériences par matériel partagé
  (colonne `hardware_family` de `data/psi/investigations.csv`) ;
- comparables en principe : NASA les relie sans matériel commun (champ « Related Investigations » de PSI,
  réutilisation de données, ou instrument partagé cité par l'énoncé, dans `data/psi/relations.csv`) ;
- sinon, la page ne les propose pas.
Le type de combustible (solide, liquide, gaz) est un rangement de l'équipe : il n'entre pas dans la règle.
Les textes renvoyés pour l'affichage sont en anglais.
"""

import pandas as pd

from flame.commun import INCONNU, charger_table_psi

# Les critères lus dans la fiche de chaque investigation.
CRITERES = ["type_combustible", "materiel", "nb_tests"]

# Les conditions de test chiffrées, lues dans le tableau des tests.
VARIABLES = ["oxygene_pct", "pression_kpa", "debit_air_cm_s"]

NIVEAUX = {
    1: "Directly comparable",
    2: "Comparable in principle",
    3: "Not comparable",
}
# Les niveaux que la page propose : au niveau 3, rien n'est commun et la comparaison n'apprend rien.
NIVEAUX_PROPOSES = (1, 2)
# Nom et unité de chaque condition de test, pour les phrases du résumé.
NOMS_VARIABLES = {
    "oxygene_pct": ("oxygen", "%"),
    "pression_kpa": ("pressure", "kPa"),
    "debit_air_cm_s": ("air flow", "cm/s"),
}
# En dessous de ce nombre de points distincts, un graphique n'apprend rien de plus que le résumé.
MINIMUM_DE_POINTS = 5

# Chaque phrase dit d'abord ce qui relie les deux investigations, puis ce qu'on peut comparer : c'est toute la
# différence entre les deux niveaux (Hugo, dimanche 15 nov. : la première version ne la faisait pas comprendre).
EXPLICATIONS = {
    1: (
        "Same hardware. Both ran in the same NASA equipment, as the challenge statement or NASA's database "
        "groups them: their measurements can be read side by side."
    ),
    2: (
        "Related, but different hardware. NASA lists them as related, one reuses the other's data, or they "
        "share an instrument: compare their questions and findings, not their numbers one by one."
    ),
    3: "No shared hardware and no link given by NASA: not offered for comparison.",
}
# Une étude au sol (modèle, laboratoire) n'a pas de matériel de vol à partager : seuls ses liens comptent.
ETUDE_AU_SOL = "Ground Investigation"
LIENS_DE_PSI = {"related to", "reuses data from"}
LIEN_DE_L_ENONCE = "Linked by the challenge statement"


def famille_combustible(type_combustible: object) -> str:
    """Le type de combustible sans sa précision : « gaz (modèle) » devient « gaz ».

    Sert au filtre de combustible de l'environnement (page Data), pas à la règle de comparabilité.
    """
    if pd.isna(type_combustible):
        return INCONNU
    return str(type_combustible).split("(")[0].strip().lower() or INCONNU


def _ligne(table: pd.DataFrame, identifiant: object) -> pd.Series | None:
    """La ligne d'une investigation dans une table de PSI, ou None si la table ne l'a pas."""
    if table.empty or "investigation_id" not in table.columns:
        return None
    lignes = table[table["investigation_id"] == identifiant]
    return None if lignes.empty else lignes.iloc[0]


def materiel_commun(depart: pd.Series, autre: pd.Series, investigations_psi: pd.DataFrame) -> str:
    """Le nom du matériel que deux investigations partagent, ou une chaîne vide.

    Avec la table de NASA : la même famille de matériel (`hardware_family`), pour deux expériences en vol.
    Sans elle (données d'exemple) : le même `materiel` dans les deux fiches.
    """
    lignes = [_ligne(investigations_psi, fiche.get("id")) for fiche in (depart, autre)]
    if all(ligne is not None and "hardware_family" in ligne.index for ligne in lignes):
        if any(str(ligne.get("project_type")) == ETUDE_AU_SOL for ligne in lignes):
            return ""
        famille = lignes[0]["hardware_family"]
        return str(famille) if pd.notna(famille) and famille == lignes[1]["hardware_family"] else ""
    materiel = depart.get("materiel")
    return str(materiel) if pd.notna(materiel) and materiel == autre.get("materiel") else ""


def lien_donne_par_nasa(id_depart: object, id_autre: object, relations: pd.DataFrame) -> str:
    """Le lien que NASA ou l'énoncé donne entre deux investigations, en une phrase, ou une chaîne vide."""
    if relations.empty or not {"from_id", "to_id", "relation"} <= set(relations.columns):
        return ""
    aller = (relations["from_id"] == id_depart) & (relations["to_id"] == id_autre)
    retour = (relations["from_id"] == id_autre) & (relations["to_id"] == id_depart)
    liens = set(relations[aller | retour]["relation"])
    if not liens:
        return ""
    # Ce que l'énoncé dit de précis passe d'abord, puis les deux liens du champ « Related Investigations » de PSI.
    de_l_enonce = sorted(liens - LIENS_DE_PSI)
    if de_l_enonce:
        return f"{LIEN_DE_L_ENONCE}: {de_l_enonce[0]}"
    if "reuses data from" in liens:
        return "One reuses the other's data, according to NASA's PSI"
    return "Listed as related in NASA's PSI"


def niveau_et_raison(
    depart: pd.Series,
    autre: pd.Series,
    investigations_psi: pd.DataFrame | None = None,
    relations: pd.DataFrame | None = None,
) -> tuple[int, str]:
    """Le niveau de comparabilité (1 à 3) de deux fiches, et la phrase qui l'explique.

    Sans les tables de NASA, seul le `materiel` des fiches sert, et aucun lien n'est connu.
    """
    investigations_psi = pd.DataFrame() if investigations_psi is None else investigations_psi
    relations = pd.DataFrame() if relations is None else relations
    lien = lien_donne_par_nasa(depart.get("id"), autre.get("id"), relations)
    # Quand l'énoncé dit précisément ce qui est partagé (un seul instrument, par exemple), on le répète tel quel
    # plutôt que d'annoncer « le même matériel ».
    if lien.startswith(LIEN_DE_L_ENONCE):
        return 2, lien
    materiel = materiel_commun(depart, autre, investigations_psi)
    if materiel:
        return 1, f"Same hardware ({materiel})"
    if lien:
        return 2, lien
    return 3, "No shared hardware and no link given by NASA"


def variables_communes(tests: pd.DataFrame, ids: list[str]) -> list[str]:
    """Les conditions de test chiffrées pour toutes les investigations de `ids`."""
    remplies = tests[tests["investigation_id"].isin(ids)].groupby("investigation_id")[VARIABLES].count()
    remplies = remplies.reindex(ids, fill_value=0)
    return [variable for variable in VARIABLES if (remplies[variable] > 0).all()]


def comparables(
    fiches: pd.DataFrame,
    tests: pd.DataFrame,
    id_depart: str,
    investigations_psi: pd.DataFrame | None = None,
    relations: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Les autres investigations, de la plus comparable à la moins comparable à `id_depart`.

    Ajoute les colonnes `niveau` (1 à 3), `raison` et `variables_communes` (liste de noms de colonnes).
    La page ne propose que les niveaux de `NIVEAUX_PROPOSES`. Les tables `investigations` et `relations`
    de NASA sont lues sur le disque quand on ne les donne pas.
    """
    investigations_psi = charger_table_psi("investigations") if investigations_psi is None else investigations_psi
    relations = charger_table_psi("relations") if relations is None else relations
    depart = fiches[fiches["id"] == id_depart].iloc[0]
    autres = fiches[fiches["id"] != id_depart].copy()
    jugements = [niveau_et_raison(depart, autre, investigations_psi, relations) for _, autre in autres.iterrows()]
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
