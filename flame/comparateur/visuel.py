"""Les chiffres derrière les dessins de la page Compare : barres des plages testées, fins de test, chiffres clés.

Ce fichier ne dessine rien : il prépare, pour deux investigations, ce que la page montre en barres.
Tout vient des tables de tests de NASA ; une valeur absente reste absente (`None`).
"""

import math

import pandas as pd

from flame.comparateur.comparaison import NOMS_VARIABLES, VARIABLES, ecrire_plage, etendues
from flame.comparateur.conditions import environnement_defini, plages_du_scenario, tests_correspondants
from flame.comparateur.details import ABSENT, ligne_psi, nombre_de_valeurs
from flame.ui import count_outcomes

# Les fins de test, dans l'ordre de lecture : clé de `count_outcomes` (rôle F), texte affiché.
ISSUES = {
    "burned": "A flame burned",
    "went_out": "The flame went out",
    "no_ignition": "No ignition",
    "unknown": "No result recorded",
}


def echelle(tests: pd.DataFrame, variable: str) -> tuple[float, float]:
    """L'échelle de la barre d'une condition : de 0 (ou moins) à la dizaine au-dessus du plus grand test.

    L'oxygène va toujours de 0 à 100 %. Un débit d'air négatif (flux inversé) étend l'échelle sous zéro.
    """
    if variable == "oxygene_pct":
        return (0.0, 100.0)
    valeurs = tests[variable].dropna()
    if valeurs.empty:
        return (0.0, 100.0)
    bas = min(0.0, math.floor(valeurs.min() / 10) * 10)
    return (float(bas), float(math.ceil(valeurs.max() / 10) * 10))


def barres_des_plages(tests: pd.DataFrame, ids: list[str], scenario: dict | None = None) -> list[dict]:
    """Pour chaque condition (oxygène, pression, débit d'air), de quoi dessiner une barre par investigation.

    Chaque élément : `variable`, `nom`, `unite`, `echelle` (min, max), `plages` {id: (min, max) ou None},
    `recouvrement` (bas, haut) quand toutes les plages se croisent, sinon None, et `environnement`
    (min, max) quand le scénario borne cette condition (une borne absente prend le bout de l'échelle).
    """
    environnement = plages_du_scenario(scenario) if scenario else {}
    barres = []
    for variable in VARIABLES:
        nom, unite = NOMS_VARIABLES[variable]
        connues = etendues(tests, ids, variable)
        mini, maxi = echelle(tests, variable)
        recouvrement = None
        if len(connues) == len(ids):
            bas = max(debut for debut, _ in connues.values())
            haut = min(fin for _, fin in connues.values())
            recouvrement = (bas, haut) if bas <= haut else None
        borne_basse, borne_haute = environnement.get(variable, (None, None))
        zone = None
        if borne_basse is not None or borne_haute is not None:
            zone = (
                mini if borne_basse is None else float(borne_basse),
                maxi if borne_haute is None else float(borne_haute),
            )
        barres.append(
            {
                "variable": variable,
                "nom": nom,
                "unite": unite,
                "echelle": (mini, maxi),
                "plages": {identifiant: connues.get(identifiant) for identifiant in ids},
                "recouvrement": recouvrement,
                "environnement": zone,
            }
        )
    return barres


def texte_de_plage(plage: tuple | None, unite: str) -> str:
    """« 13.6 to 22.2 % », ou « not recorded » quand NASA ne note pas cette condition."""
    return ABSENT if plage is None else f"{ecrire_plage(*plage)} {unite}"


def issues(tests: pd.DataFrame, ids: list[str]) -> dict[str, dict[str, int]]:
    """Pour chaque investigation, le nombre de ses lignes de tests par fin de test (clés de `ISSUES`).

    Le classement des libellés de NASA en quatre fins de test est la lecture de l'équipe (rôle F).
    """
    return {identifiant: count_outcomes(tests[tests["investigation_id"] == identifiant]) for identifiant in ids}


def chiffres_cles(
    fiches: pd.DataFrame,
    tests: pd.DataFrame,
    ids: list[str],
    scenario: dict | None = None,
    investigations_psi: pd.DataFrame | None = None,
) -> list[tuple[str, dict[str, str]]]:
    """Les chiffres à lire côte à côte : [(libellé, {id: valeur en texte}), ...]."""
    lignes = [
        ("Test rows", {i: f"{int((tests['investigation_id'] == i).sum()):,}" for i in ids}),
        ("Different fuels", {i: str(nombre_de_valeurs(tests, i, "combustible")) for i in ids}),
    ]
    if scenario is not None and environnement_defini(scenario):
        dedans = tests_correspondants(tests, fiches, scenario)
        lignes.append(
            ("Tests in your environment", {i: str(int((dedans["investigation_id"] == i).sum())) for i in ids})
        )
    if investigations_psi is not None and not investigations_psi.empty:
        articles = {}
        for identifiant in ids:
            psi = ligne_psi(investigations_psi, identifiant)
            nombre = None if psi is None else pd.to_numeric(psi.get("n_publications"), errors="coerce")
            articles[identifiant] = ABSENT if nombre is None or pd.isna(nombre) else f"{nombre:g}"
        lignes.append(("Papers listed by NASA", articles))
    return lignes
