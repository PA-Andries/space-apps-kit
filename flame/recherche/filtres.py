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
