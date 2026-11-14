"""Le score d'une investigation pour l'environnement de l'utilisateur : sur 100, en quatre critères expliqués.

Recadrage du 14 novembre et REPRISE de 18h38 (issue n°2) : les piliers sont abandonnés (ni score, ni filtre,
ni étiquette). Le score repose sur les preuves :
- atmosphère 40 : la part des tests de l'investigation dans les plages d'oxygène et de pression du scénario ;
- combustible 25 : solide, puis liquide, puis gaz, et 0 si ce n'est pas un des combustibles choisis ;
- gravité 20 : `gravity_fit` de `data/psi/relevance.csv` (rôle B) pour l'habitat ;
- données 15 : le nombre de tests.
Les poids sont un jugement d'équipe ; les barèmes du combustible et des données sont des hypothèses du rôle C.
"""

import pandas as pd

from flame.commun import charger_table_psi, charger_tests
from flame.recherche.conditions import (
    atmosphere_connue,
    decrire_plages,
    nom_de_l_environnement,
    tests_dans_les_plages,
)
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


def type_de_base(type_combustible: object) -> str:
    """« solide (modèle) » -> « solide » : une étude au sol sur un solide compte comme un solide."""
    return simplifier(str(type_combustible).split("(")[0]) if pd.notna(type_combustible) else ""


def _points_atmosphere(fiche: pd.Series, scenario: dict | None, tests: pd.DataFrame) -> tuple[int, str]:
    if not atmosphere_connue(scenario):
        return 0, f"The atmosphere of {nom_de_l_environnement(scenario)} is unknown: criterion not counted."
    siens = tests[tests["investigation_id"] == fiche.get("id")]
    if siens.empty:
        return 0, "No test of this investigation is in PSI's tables."
    dedans = len(tests_dans_les_plages(siens, scenario))
    part = dedans / len(siens)
    return round(POINTS_ATMOSPHERE * part), (
        f"{dedans} of its {len(siens)} tests ({part:.0%}) fall in your atmosphere ({decrire_plages(scenario)})."
    )


def _points_combustible(fiche: pd.Series, scenario: dict | None) -> tuple[int, str]:
    type_fiche = type_de_base(fiche.get("type_combustible"))
    choisis = [type_de_base(choix) for choix in (scenario or {}).get("type_combustible") or []]
    if type_fiche not in POINTS_PAR_COMBUSTIBLE:
        return 0, "No solid, liquid or gas fuel recorded."
    if choisis and type_fiche not in choisis:
        return 0, f"{_majuscule(label(type_fiche))} fuel: not one of the fuels you chose."
    return POINTS_PAR_COMBUSTIBLE[type_fiche], (
        f"{_majuscule(label(type_fiche))} fuel: a habitat holds mostly solids (fabrics, plastics), "
        "then liquids, then gases."
    )


def _points_gravite(fiche: pd.Series, scenario: dict | None, pertinence: pd.DataFrame) -> tuple[int, str]:
    habitat = (scenario or {}).get("habitat")
    if habitat not in HABITAT_PSI:
        return 0, "Gravity fit is only known for the listed habitats: criterion not counted."
    if pertinence.empty:
        return 0, "Gravity of the tests not recorded."
    lignes = pertinence[
        (pertinence["habitat_id"] == HABITAT_PSI[habitat]) & (pertinence["investigation_id"] == fiche.get("id"))
    ]
    ajustement = None if lignes.empty else _nombre(lignes.iloc[0].get("gravity_fit"))
    if ajustement is None:
        return 0, "Gravity of the tests not recorded."
    # Le morceau de la colonne `why` du rôle B qui parle de gravité, par exemple « microgravity flight data ».
    morceaux = str(lignes.iloc[0].get("why", "")).split(";")
    raison = next((m.strip() for m in morceaux if any(mot in m.lower() for mot in ("gravity", "ground", "1-g"))), "")
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
    fiche: pd.Series,
    scenario: dict | None = None,
    pertinence: pd.DataFrame | None = None,
    tests: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Le score de `fiche` pour `scenario`, critère par critère : colonnes critere, points, maximum, explication.

    `pertinence` (table `relevance` du rôle B) et `tests` sont lus sur le disque quand on ne les donne pas.
    Les noms de critères et les explications s'affichent sur le site : ils sont en anglais.
    """
    pertinence = charger_pertinence() if pertinence is None else pertinence
    tests = charger_tests() if tests is None else tests
    lignes = [
        ("Atmosphere", *_points_atmosphere(fiche, scenario, tests), POINTS_ATMOSPHERE),
        ("Fuel", *_points_combustible(fiche, scenario), POINTS_COMBUSTIBLE),
        ("Gravity", *_points_gravite(fiche, scenario, pertinence), POINTS_GRAVITE),
        ("Data", *_points_donnees(fiche), POINTS_DONNEES),
    ]
    detail = pd.DataFrame(lignes, columns=["critere", "points", "explication", "maximum"])
    return detail[COLONNES_DETAIL]


def ajouter_scores(
    fiches: pd.DataFrame,
    scenario: dict | None = None,
    pertinence: pd.DataFrame | None = None,
    tests: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Les fiches avec les quatre colonnes de COLONNES_SCORE et leur somme dans `score` (de 0 à 100)."""
    pertinence = charger_pertinence() if pertinence is None else pertinence
    tests = charger_tests() if tests is None else tests
    points = [list(detail_du_score(fiche, scenario, pertinence, tests)["points"]) for _, fiche in fiches.iterrows()]
    scores = pd.DataFrame(points, columns=COLONNES_SCORE, index=fiches.index).astype(int)
    return fiches.assign(**{colonne: scores[colonne] for colonne in COLONNES_SCORE}, score=scores.sum(axis=1))
