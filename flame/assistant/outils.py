"""Les outils que Gemini peut appeler (function calling) pour répondre sur un habitat ou sur des conditions.

Gemini choisit l'outil et ses arguments ; le code l'exécute ici et lui renvoie le résultat.
Les résultats ne contiennent que des types JSON simples (str, int, float, None, listes, dictionnaires).
"""

import pandas as pd

from flame.commun import HABITATS, charger_fiches, charger_table_psi, charger_tests

# Les habitats du contrat, tels que les nomme `data/psi/relevance.csv`.
IDS_HABITATS = {
    "Vaisseau": "spacecraft",
    "Station": "space_station",
    "Base lunaire": "moon_base",
    "Base martienne": "mars_base",
    "Rover pressurisé": "pressurized_rover",
}
TYPES_COMBUSTIBLE = ["solide", "liquide", "gaz"]
NB_MAX_INVESTIGATIONS = 10


def _nombre(valeur: object) -> float | None:
    return None if pd.isna(valeur) else float(valeur)


def filtrer_par_habitat(habitat: str) -> dict:
    """Les investigations les plus pertinentes pour `habitat`, d'après `data/psi/relevance.csv`."""
    if habitat not in IDS_HABITATS:
        return {"erreur": f"Habitat inconnu : {habitat}. Habitats possibles : {', '.join(HABITATS)}."}
    table = charger_table_psi("relevance")
    if table.empty:
        return {"habitat": habitat, "investigations": [], "note": "La table de pertinence n'est pas disponible."}
    lignes = table[table["habitat_id"] == IDS_HABITATS[habitat]]
    # L'ancienne table avait une ligne par pilier : on garde la meilleure ligne de chaque investigation.
    meilleures = lignes.sort_values("score", ascending=False).drop_duplicates("investigation_id")
    return {
        "habitat": habitat,
        "investigations": [
            {
                "id": str(ligne.investigation_id),
                "nom": str(ligne.acronym),
                "score_sur_100": _nombre(ligne.score),
                "pourquoi": "" if pd.isna(ligne.why) else str(ligne.why),
            }
            for ligne in meilleures.head(NB_MAX_INVESTIGATIONS).itertuples()
        ],
        "note": "Score calculé par l'équipe (atmosphère testée, gravité, citation dans l'énoncé) : "
        "ce n'est pas une donnée NASA.",
    }


def compter_tests(
    oxygene_min_pct: float | None = None,
    oxygene_max_pct: float | None = None,
    pression_min_kpa: float | None = None,
    pression_max_kpa: float | None = None,
    types_combustible: list[str] | None = None,
) -> dict:
    """Combien de tests NASA ont été faits dans ces conditions, et par quelles investigations."""
    tests = charger_tests()
    types = charger_fiches().set_index("id")["type_combustible"]
    type_du_test = tests["investigation_id"].map(types).fillna("").astype(str)
    garde = pd.Series(True, index=tests.index)
    # Une comparaison avec une case vide donne False : un test sans valeur notée n'est pas compté.
    for colonne, borne, plus_grand in [
        ("oxygene_pct", oxygene_min_pct, True),
        ("oxygene_pct", oxygene_max_pct, False),
        ("pression_kpa", pression_min_kpa, True),
        ("pression_kpa", pression_max_kpa, False),
    ]:
        if borne is not None:
            garde &= tests[colonne] >= borne if plus_grand else tests[colonne] <= borne
    if types_combustible:
        garde &= type_du_test.apply(lambda valeur: any(valeur.startswith(t) for t in types_combustible))
    par_investigation = tests[garde].groupby("investigation_id").size().sort_values(ascending=False)
    return {
        "nb_tests": int(garde.sum()),
        "nb_tests_au_total": int(len(tests)),
        "investigations": [{"id": str(i), "nb_tests": int(n)} for i, n in par_investigation.items()],
        "note": "Un test sans valeur notée pour une condition demandée n'est pas compté. "
        "Aucun test n'a été fait en gravité partielle (Lune, Mars).",
    }


OUTILS = {"filtrer_par_habitat": filtrer_par_habitat, "compter_tests": compter_tests}

# La description des outils, au format attendu par Gemini.
DECLARATIONS = [
    {
        "name": "filtrer_par_habitat",
        "description": "Les investigations NASA les plus pertinentes pour un habitat, avec leur score sur 100 "
        "(un jugement de l'équipe) et la raison.",
        "parameters": {
            "type": "object",
            "properties": {"habitat": {"type": "string", "enum": HABITATS}},
            "required": ["habitat"],
        },
    },
    {
        "name": "compter_tests",
        "description": "Le nombre de tests NASA faits dans des conditions données (plages d'oxygène en %, de "
        "pression en kPa, types de combustible), et les investigations qui les ont faits.",
        "parameters": {
            "type": "object",
            "properties": {
                "oxygene_min_pct": {"type": "number"},
                "oxygene_max_pct": {"type": "number"},
                "pression_min_kpa": {"type": "number"},
                "pression_max_kpa": {"type": "number"},
                "types_combustible": {"type": "array", "items": {"type": "string", "enum": TYPES_COMBUSTIBLE}},
            },
        },
    },
]


def executer_outil(nom: str, arguments: dict | None) -> dict:
    """Le résultat de l'outil `nom`, ou une erreur que Gemini peut lire (jamais d'exception)."""
    if nom not in OUTILS:
        return {"erreur": f"Outil inconnu : {nom}."}
    try:
        return OUTILS[nom](**(arguments or {}))
    except (TypeError, ValueError, KeyError) as erreur:
        return {"erreur": f"L'outil {nom} n'a pas pu répondre : {erreur}."}
