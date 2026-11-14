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
        return 0, "Pas de pilier choisi : critère non compté."
    piliers = [pilier.strip() for pilier in str(fiche.get("pilier", "")).split(";") if pilier.strip()]
    if simplifier(scenario["pilier"]) in [simplifier(pilier) for pilier in piliers]:
        return POINTS_PILIER, f"L'investigation traite le pilier « {scenario['pilier']} »."
    connus = ", ".join(piliers) or "non renseignés"
    return 0, f"Piliers de l'investigation : {connus} ; pilier choisi : {scenario['pilier']}."


def _points_oxygene(fiche: pd.Series, scenario: dict[str, str] | None) -> tuple[int, str]:
    habitat = (scenario or {}).get("habitat")
    if habitat not in ATMOSPHERES:
        return 0, "Pas d'habitat choisi : critère non compté."
    oxygene_habitat_pct = ATMOSPHERES[habitat][0]
    oxygene_min_pct, oxygene_max_pct = _nombre(fiche.get("oxygene_min")), _nombre(fiche.get("oxygene_max"))
    if oxygene_min_pct is None or oxygene_max_pct is None:
        return 0, "Plage d'oxygène testée inconnue."
    plage = f"{oxygene_min_pct:g} à {oxygene_max_pct:g} %"
    if oxygene_min_pct <= oxygene_habitat_pct <= oxygene_max_pct:
        return (
            POINTS_OXYGENE,
            f"La plage testée ({plage}) couvre les {oxygene_habitat_pct} % d'oxygène de « {habitat} ».",
        )
    ecart_pct = min(abs(oxygene_habitat_pct - oxygene_min_pct), abs(oxygene_habitat_pct - oxygene_max_pct))
    points = round(POINTS_OXYGENE * max(0.0, 1 - ecart_pct / ECART_OXYGENE_MAX_PCT))
    return points, (
        f"La plage testée ({plage}) est à {ecart_pct:g} point(s) des {oxygene_habitat_pct} % d'oxygène "
        f"de « {habitat} » ; "
        f"le critère tombe à 0 à partir de {ECART_OXYGENE_MAX_PCT} points d'écart."
    )


def _points_combustible(fiche: pd.Series) -> tuple[int, str]:
    type_combustible = simplifier(fiche.get("type_combustible", ""))
    if type_combustible in POINTS_PAR_COMBUSTIBLE:
        return POINTS_PAR_COMBUSTIBLE[type_combustible], (
            f"Combustible {type_combustible} : un habitat contient surtout des solides (tissus, plastiques), "
            "puis des liquides, puis des gaz."
        )
    return 0, "Pas de combustible solide, liquide ou gazeux renseigné."


def _points_donnees(fiche: pd.Series) -> tuple[int, str]:
    nb_tests = _nombre(fiche.get("nb_tests"))
    if nb_tests is None:
        return 0, "Nombre de tests inconnu."
    for seuil, points in PALIERS_NB_TESTS:
        if nb_tests >= seuil:
            return points, f"{nb_tests:g} test(s) disponibles (palier : {seuil} ou plus)."
    return 0, "Aucun test disponible."


def detail_du_score(fiche: pd.Series, scenario: dict[str, str] | None = None) -> pd.DataFrame:
    """Le score de `fiche` pour `scenario`, critère par critère : colonnes critere, points, maximum, explication."""
    lignes = [
        ("Pilier", *_points_pilier(fiche, scenario), POINTS_PILIER),
        ("Oxygène", *_points_oxygene(fiche, scenario), POINTS_OXYGENE),
        ("Combustible", *_points_combustible(fiche), POINTS_COMBUSTIBLE),
        ("Données", *_points_donnees(fiche), POINTS_DONNEES),
    ]
    detail = pd.DataFrame(lignes, columns=["critere", "points", "explication", "maximum"])
    return detail[COLONNES_DETAIL]


def ajouter_scores(fiches: pd.DataFrame, scenario: dict[str, str] | None = None) -> pd.DataFrame:
    """Les fiches avec les quatre colonnes de COLONNES_SCORE et leur somme dans `score` (de 0 à 100)."""
    points = [list(detail_du_score(fiche, scenario)["points"]) for _, fiche in fiches.iterrows()]
    scores = pd.DataFrame(points, columns=COLONNES_SCORE, index=fiches.index).astype(int)
    return fiches.assign(**{colonne: scores[colonne] for colonne in COLONNES_SCORE}, score=scores.sum(axis=1))
