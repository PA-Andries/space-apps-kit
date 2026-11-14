"""Le score d'une investigation pour un environnement : sur 100, en quatre critères expliqués.

Recadrage du 14 novembre (DECISIONS.md, 16:45, accord de PA) : le pilier ne compte plus dans le score,
c'est un filtre et une étiquette (voir filtres.py). Le score repose sur les preuves :
atmosphère 40, combustible 25, gravité 20, données 15.

L'atmosphère et la gravité viennent de `data/psi/relevance.csv` (rôle B), calculées sur les vrais tests,
sans son poids de pilier. Les poids sont un jugement d'équipe ; les barèmes du combustible et des données
sont des hypothèses du rôle C, à ajuster avec le rôle A.
"""

import pandas as pd

from flame.commun import charger_table_psi
from flame.recherche.texte import simplifier
from flame.ui import label

POINTS_ATMOSPHERE = 40
POINTS_COMBUSTIBLE = 25
POINTS_GRAVITE = 20
POINTS_DONNEES = 15

# Le brief classe les combustibles : solides, puis liquides, puis gaz. Les valeurs sont une hypothèse.
POINTS_PAR_COMBUSTIBLE = {"solide": 25, "liquide": 15, "gaz": 8}
# Hypothèse : (nombre de tests à atteindre, points), du palier le plus haut au plus bas.
PALIERS_NB_TESTS = [(50, 15), (10, 10), (1, 5)]

# Le nom de chaque habitat du contrat dans data/psi/relevance.csv.
HABITAT_PSI = {
    "Vaisseau": "spacecraft",
    "Station": "space_station",
    "Base lunaire": "moon_base",
    "Base martienne": "mars_base",
    "Rover pressurisé": "pressurized_rover",
}
# Décision du 14 novembre : l'énoncé ne donne aucune atmosphère pour Mars, elle reste inconnue.
HABITATS_SANS_ATMOSPHERE = {"Base martienne"}

COLONNES_SCORE = ["score_atmosphere", "score_combustible", "score_gravite", "score_donnees"]
COLONNES_DETAIL = ["critere", "points", "maximum", "explication"]


def charger_pertinence() -> pd.DataFrame:
    """La table `relevance` du rôle B (vide si elle n'existe pas, par exemple sur les données d'exemple)."""
    return charger_table_psi("relevance")


def _majuscule(texte: str) -> str:
    """La première lettre en majuscule, sans toucher au reste (« O2 » reste « O2 »)."""
    return texte[:1].upper() + texte[1:]


def _nombre(valeur: object) -> float | None:
    """La valeur en nombre, ou None si elle est vide, « inconnu » ou illisible."""
    nombre = pd.to_numeric(valeur, errors="coerce")
    return None if pd.isna(nombre) else float(nombre)


def _ligne_pertinence(fiche: pd.Series, habitat: str | None, pertinence: pd.DataFrame) -> pd.Series | None:
    """La ligne de `relevance` pour cette fiche et cet habitat, avec l'explication la plus complète."""
    if habitat not in HABITAT_PSI or pertinence.empty:
        return None
    lignes = pertinence[
        (pertinence["habitat_id"] == HABITAT_PSI[habitat]) & (pertinence["investigation_id"] == fiche.get("id"))
    ]
    if lignes.empty:
        return None
    # L'atmosphère et la gravité sont les mêmes pour tous les piliers ; seules certaines lignes ont le « why » complet.
    return lignes.loc[lignes["why"].fillna("").str.count(";").idxmax()]


def _morceau_du_pourquoi(ligne: pd.Series, mots: tuple[str, ...]) -> str | None:
    """Le morceau de la colonne `why` du rôle B qui parle d'un des `mots` (atmosphère ou gravité)."""
    for morceau in str(ligne.get("why", "")).split(";")[1:]:
        if any(mot in morceau.lower() for mot in mots):
            return morceau.strip()
    return None


def _points_atmosphere(habitat: str | None, ligne: pd.Series | None) -> tuple[int, str]:
    if habitat not in HABITAT_PSI:
        return 0, "No habitat chosen: criterion not counted."
    if habitat in HABITATS_SANS_ATMOSPHERE:
        return 0, f"The statement gives no atmosphere for the {label(habitat)}: criterion unknown."
    ajustement = None if ligne is None else _nombre(ligne.get("atmosphere_fit"))
    if ajustement is None:
        return 0, "Test conditions not recorded for this habitat."
    raison = _morceau_du_pourquoi(ligne, ("o2", "oxygen", "pressure"))
    points = round(POINTS_ATMOSPHERE * ajustement)
    return points, f"{_majuscule(raison or 'test conditions')} (habitat: {label(habitat)})."


def _points_combustible(fiche: pd.Series) -> tuple[int, str]:
    # « solide (modèle) » désigne une étude au sol sur un solide : on compte son type de base.
    type_combustible = simplifier(str(fiche.get("type_combustible", "")).split("(")[0])
    if type_combustible in POINTS_PAR_COMBUSTIBLE:
        return POINTS_PAR_COMBUSTIBLE[type_combustible], (
            f"{_majuscule(label(type_combustible))} fuel: a habitat holds mostly solids "
            "(fabrics, plastics), then liquids, then gases."
        )
    return 0, "No solid, liquid or gas fuel recorded."


def _points_gravite(habitat: str | None, ligne: pd.Series | None) -> tuple[int, str]:
    if habitat not in HABITAT_PSI:
        return 0, "No habitat chosen: criterion not counted."
    ajustement = None if ligne is None else _nombre(ligne.get("gravity_fit"))
    if ajustement is None:
        return 0, "Gravity of the tests not recorded."
    raison = _morceau_du_pourquoi(ligne, ("gravity", "ground", "1-g"))
    return round(POINTS_GRAVITE * ajustement), f"{_majuscule(raison or 'gravity of the tests')}."


def _points_donnees(fiche: pd.Series) -> tuple[int, str]:
    nb_tests = _nombre(fiche.get("nb_tests"))
    if nb_tests is None:
        return 0, "Number of tests unknown."
    for seuil, points in PALIERS_NB_TESTS:
        if nb_tests >= seuil:
            return points, f"{nb_tests:g} test(s) available (step: {seuil} or more)."
    return 0, "No test available."


def detail_du_score(
    fiche: pd.Series, scenario: dict[str, str] | None = None, pertinence: pd.DataFrame | None = None
) -> pd.DataFrame:
    """Le score de `fiche` pour `scenario`, critère par critère : colonnes critere, points, maximum, explication.

    `pertinence` est la table `relevance` du rôle B ; elle est lue sur le disque quand on ne la donne pas.
    Les noms de critères et les explications s'affichent sur le site : ils sont en anglais.
    """
    if pertinence is None:
        pertinence = charger_pertinence()
    habitat = (scenario or {}).get("habitat")
    ligne = _ligne_pertinence(fiche, habitat, pertinence)
    lignes = [
        ("Atmosphere", *_points_atmosphere(habitat, ligne), POINTS_ATMOSPHERE),
        ("Fuel", *_points_combustible(fiche), POINTS_COMBUSTIBLE),
        ("Gravity", *_points_gravite(habitat, ligne), POINTS_GRAVITE),
        ("Data", *_points_donnees(fiche), POINTS_DONNEES),
    ]
    detail = pd.DataFrame(lignes, columns=["critere", "points", "explication", "maximum"])
    return detail[COLONNES_DETAIL]


def ajouter_scores(
    fiches: pd.DataFrame, scenario: dict[str, str] | None = None, pertinence: pd.DataFrame | None = None
) -> pd.DataFrame:
    """Les fiches avec les quatre colonnes de COLONNES_SCORE et leur somme dans `score` (de 0 à 100)."""
    if pertinence is None:
        pertinence = charger_pertinence()
    points = [list(detail_du_score(fiche, scenario, pertinence)["points"]) for _, fiche in fiches.iterrows()]
    scores = pd.DataFrame(points, columns=COLONNES_SCORE, index=fiches.index).astype(int)
    return fiches.assign(**{colonne: scores[colonne] for colonne in COLONNES_SCORE}, score=scores.sum(axis=1))
