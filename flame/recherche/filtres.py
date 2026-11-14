"""Les filtres de la page Recherche : ne garder que certaines fiches."""

import pandas as pd

from flame.recherche.texte import simplifier


def _valeurs(cellule: object) -> set[str]:
    """Les valeurs simplifiées d'une cellule qui en contient plusieurs séparées par « ; »."""
    if pd.isna(cellule):
        return set()
    return {simplifier(valeur) for valeur in str(cellule).split(";") if valeur.strip()}


def _contient_une_valeur(colonne: pd.Series, choix: list[str]) -> pd.Series:
    cherchees = {simplifier(valeur) for valeur in choix}
    return colonne.map(lambda cellule: bool(_valeurs(cellule) & cherchees))


def filtrer(
    fiches: pd.DataFrame,
    piliers: list[str] | None = None,
    types_combustible: list[str] | None = None,
    habitats: list[str] | None = None,
) -> pd.DataFrame:
    """Les fiches qui ont au moins un des `piliers`, un des `types_combustible` et un des `habitats`.

    Un filtre vide ou absent ne retire rien.
    """
    garder = pd.Series(True, index=fiches.index)
    for colonne, choix in (("pilier", piliers), ("type_combustible", types_combustible), ("habitats", habitats)):
        if choix:
            garder &= _contient_une_valeur(fiches[colonne], choix)
    return fiches[garder].reset_index(drop=True)


def valeurs_possibles(fiches: pd.DataFrame, colonne: str) -> list[str]:
    """Les valeurs distinctes de `colonne` (cellules à plusieurs valeurs séparées par « ; »), triées."""
    valeurs = {valeur.strip() for cellule in fiches[colonne].dropna() for valeur in str(cellule).split(";")}
    return sorted(valeur for valeur in valeurs if valeur)


# Les piliers du contrat et leurs noms dans data/psi/relevance.csv (« react » est l'ancien nom d'« Éteindre »).
PILIER_PSI = {"Prévenir": {"prevent"}, "Détecter": {"detect"}, "Éteindre": {"react", "extinguish"}}
# Le poids de pilier du rôle B (jugement d'équipe) devient une étiquette, il ne compte plus dans le score.
ETIQUETTES = {3: "primary", 2: "secondary", 1: "indirect"}


def filtrer_par_pilier(fiches: pd.DataFrame, pilier: str | None, pertinence: pd.DataFrame) -> pd.DataFrame:
    """Les fiches utiles au `pilier`, avec une colonne `etiquette` (primary, secondary ou indirect).

    Sans pilier, rien n'est retiré et l'étiquette reste vide. Sans la table `relevance` (données d'exemple),
    on se rabat sur la colonne `pilier` des fiches, sans étiquette.
    """
    if not pilier:
        return fiches.assign(etiquette="").reset_index(drop=True)
    if pertinence.empty or pilier not in PILIER_PSI:
        return filtrer(fiches, piliers=[pilier]).assign(etiquette="")
    lignes = pertinence[pertinence["category_id"].isin(PILIER_PSI[pilier])]
    poids = pd.to_numeric(lignes["category_weight"], errors="coerce").groupby(lignes["investigation_id"]).max()
    etiquettes = fiches["id"].map(poids).fillna(0).astype(int).map(ETIQUETTES)
    gardees = fiches.assign(etiquette=etiquettes)[etiquettes.notna()]
    return gardees.reset_index(drop=True)
