"""La recherche utile aux équipements de demain (détecteurs, extincteurs) et ses retombées sur Terre.

Rien n'est rédigé ici : chaque texte vient d'une fiche ou d'une table PSI, avec sa source.
Le seul choix de l'équipe est le rattachement d'une investigation à un équipement (`EQUIPEMENTS`).
"""

import pandas as pd

# Quelle investigation éclaire quel équipement : un jugement de l'équipe, que la page annonce comme tel.
EQUIPEMENTS = {
    "detecteurs": ["PSI-102", "PSI-101", "PSI-47"],  # SAME, SAME-R, DAFT / DAFT-2
    "extincteurs": ["PSI-69", "PSI-68", "PSI-25"],  # FLEX, FLEX-2, BASS-II
}


def fiches_pour(equipement: str, fiches: pd.DataFrame) -> pd.DataFrame:
    """Les fiches rattachées à `equipement` ("detecteurs" ou "extincteurs"), dans l'ordre d'`EQUIPEMENTS`."""
    ids = EQUIPEMENTS[equipement]
    trouvees = fiches[fiches["id"].isin(ids)]
    ordre = trouvees["id"].map(ids.index)
    return trouvees.assign(_ordre=ordre).sort_values("_ordre").drop(columns="_ordre")


def instruments_de(investigation_id: str, mesures: pd.DataFrame) -> pd.DataFrame:
    """Les instruments d'une investigation et ce qu'ils mesurent, d'après la table PSI `measurements`."""
    colonnes = ["instrument", "measures", "unit", "source"]
    if mesures.empty or not set(colonnes) <= set(mesures.columns):
        return pd.DataFrame(columns=colonnes)
    return mesures.loc[mesures["investigation_id"] == investigation_id, colonnes].reset_index(drop=True)


def retombees_sur_terre(investigations_psi: pd.DataFrame) -> pd.DataFrame:
    """Le texte « impacts et bénéfices sur Terre » écrit par NASA pour chaque investigation, quand il existe.

    Colonnes : `id`, `nom`, `texte`, `source` (la page PSI de l'investigation).
    """
    colonnes = ["investigation_id", "acronym", "impacts_earth_benefits", "psi_url"]
    if investigations_psi.empty or not set(colonnes) <= set(investigations_psi.columns):
        return pd.DataFrame(columns=["id", "nom", "texte", "source"])
    table = investigations_psi[colonnes].dropna(subset=["impacts_earth_benefits"])
    table = table[table["impacts_earth_benefits"].astype(str).str.strip() != ""]
    return table.rename(
        columns={"investigation_id": "id", "acronym": "nom", "impacts_earth_benefits": "texte", "psi_url": "source"}
    ).reset_index(drop=True)


def liens_terre(ressources: pd.DataFrame) -> pd.DataFrame:
    """Les ressources officielles du défi classées « earth_benefit » : `title`, `url`, `note`."""
    colonnes = ["title", "url", "note"]
    if ressources.empty or not {"kind", *colonnes} <= set(ressources.columns):
        return pd.DataFrame(columns=colonnes)
    return ressources.loc[ressources["kind"] == "earth_benefit", colonnes].reset_index(drop=True)
