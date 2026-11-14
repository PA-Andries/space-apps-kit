"""Le score d'une investigation pour un scénario : sur 100, en quatre critères expliqués.

Les poids viennent de BRIEF_EQUIPE_IA.md (section 5). Les autres réglages de ce fichier
sont des hypothèses du rôle C, à ajuster avec le rôle A.
"""

import pandas as pd

from flame.commun import ATMOSPHERES
from flame.recherche.texte import simplifier

POINTS_PILIER = 40
POINTS_OXYGENE = 25
POINTS_COMBUSTIBLE = 20
POINTS_DONNEES = 15

# Hypothèse : au-delà de cet écart entre la plage testée et l'oxygène de l'habitat, le critère vaut 0.
ECART_OXYGENE_MAX_PCT = 10
# Le brief classe les combustibles : solides, puis liquides, puis gaz. Les valeurs sont une hypothèse.
POINTS_PAR_COMBUSTIBLE = {"solide": 20, "liquide": 12, "gaz": 6}
# Le nom anglais de chaque type, pour les explications affichées.
COMBUSTIBLE_EN_ANGLAIS = {"solide": "solid", "liquide": "liquid", "gaz": "gas"}
# Hypothèse : (nombre de tests à atteindre, points), du palier le plus haut au plus bas.
PALIERS_NB_TESTS = [(50, 15), (10, 10), (1, 5)]

COLONNES_SCORE = ["score_pilier", "score_oxygene", "score_combustible", "score_donnees"]
COLONNES_DETAIL = ["critere", "points", "maximum", "explication"]


def _nombre(valeur: object) -> float | None:
    """La valeur en nombre, ou None si elle est vide, « inconnu » ou illisible."""
    nombre = pd.to_numeric(valeur, errors="coerce")
    return None if pd.isna(nombre) else float(nombre)


def _points_pilier(fiche: pd.Series, scenario: dict[str, str] | None) -> tuple[int, str]:
    if not scenario or not scenario.get("pilier"):
        return 0, "No pillar chosen: criterion not counted."
    piliers = [pilier.strip() for pilier in str(fiche.get("pilier", "")).split(";") if pilier.strip()]
    if simplifier(scenario["pilier"]) in [simplifier(pilier) for pilier in piliers]:
        return POINTS_PILIER, f"The investigation addresses the chosen pillar ({scenario['pilier']})."
    connus = ", ".join(piliers) or "not recorded"
    return 0, f"Investigation pillar: {connus}; chosen pillar: {scenario['pilier']}."


def _points_oxygene(fiche: pd.Series, scenario: dict[str, str] | None) -> tuple[int, str]:
    habitat = (scenario or {}).get("habitat")
    if habitat not in ATMOSPHERES:
        return 0, "No habitat chosen: criterion not counted."
    oxygene_habitat_pct = ATMOSPHERES[habitat][0]
    if oxygene_habitat_pct is None:
        return 0, f"The oxygen level of {habitat} is unknown: criterion not counted."
    oxygene_min_pct, oxygene_max_pct = _nombre(fiche.get("oxygene_min")), _nombre(fiche.get("oxygene_max"))
    if oxygene_min_pct is None or oxygene_max_pct is None:
        return 0, "Tested oxygen range unknown."
    plage = f"{oxygene_min_pct:g} to {oxygene_max_pct:g} %"
    if oxygene_min_pct <= oxygene_habitat_pct <= oxygene_max_pct:
        return POINTS_OXYGENE, f"The tested range ({plage}) covers the {oxygene_habitat_pct} % oxygen of {habitat}."
    ecart_pct = min(abs(oxygene_habitat_pct - oxygene_min_pct), abs(oxygene_habitat_pct - oxygene_max_pct))
    points = round(POINTS_OXYGENE * max(0.0, 1 - ecart_pct / ECART_OXYGENE_MAX_PCT))
    return points, (
        f"The tested range ({plage}) is {ecart_pct:g} point(s) away from the {oxygene_habitat_pct} % oxygen "
        f"of {habitat}; the criterion drops to 0 from a gap of {ECART_OXYGENE_MAX_PCT} points."
    )


def _points_combustible(fiche: pd.Series) -> tuple[int, str]:
    # « solide (modèle) » désigne une étude au sol sur un solide : on compte son type de base.
    type_combustible = simplifier(str(fiche.get("type_combustible", "")).split("(")[0])
    if type_combustible in POINTS_PAR_COMBUSTIBLE:
        return POINTS_PAR_COMBUSTIBLE[type_combustible], (
            f"{COMBUSTIBLE_EN_ANGLAIS[type_combustible].capitalize()} fuel: a habitat holds mostly solids "
            "(fabrics, plastics), then liquids, then gases."
        )
    return 0, "No solid, liquid or gas fuel recorded."


def _points_donnees(fiche: pd.Series) -> tuple[int, str]:
    nb_tests = _nombre(fiche.get("nb_tests"))
    if nb_tests is None:
        return 0, "Number of tests unknown."
    for seuil, points in PALIERS_NB_TESTS:
        if nb_tests >= seuil:
            return points, f"{nb_tests:g} test(s) available (step: {seuil} or more)."
    return 0, "No test available."


def detail_du_score(fiche: pd.Series, scenario: dict[str, str] | None = None) -> pd.DataFrame:
    """Le score de `fiche` pour `scenario`, critère par critère : colonnes critere, points, maximum, explication.

    Les noms de critères et les explications s'affichent sur le site : ils sont en anglais.
    """
    lignes = [
        ("Pillar", *_points_pilier(fiche, scenario), POINTS_PILIER),
        ("Oxygen", *_points_oxygene(fiche, scenario), POINTS_OXYGENE),
        ("Fuel", *_points_combustible(fiche), POINTS_COMBUSTIBLE),
        ("Data", *_points_donnees(fiche), POINTS_DONNEES),
    ]
    detail = pd.DataFrame(lignes, columns=["critere", "points", "explication", "maximum"])
    return detail[COLONNES_DETAIL]


def ajouter_scores(fiches: pd.DataFrame, scenario: dict[str, str] | None = None) -> pd.DataFrame:
    """Les fiches avec les quatre colonnes de COLONNES_SCORE et leur somme dans `score` (de 0 à 100)."""
    points = [list(detail_du_score(fiche, scenario)["points"]) for _, fiche in fiches.iterrows()]
    scores = pd.DataFrame(points, columns=COLONNES_SCORE, index=fiches.index).astype(int)
    return fiches.assign(**{colonne: scores[colonne] for colonne in COLONNES_SCORE}, score=scores.sum(axis=1))
