"""Le détail d'une comparaison : portrait de chaque investigation, tableau côte à côte, résumé par thèmes.

Tout vient des fiches et des tables de tests de NASA. Une information absente est dite
absente, jamais devinée. Les textes renvoyés pour l'affichage sont en anglais.
"""

import pandas as pd

from flame.commun import INCONNU
from flame.comparateur.comparaison import (
    MINIMUM_DE_POINTS,
    NIVEAUX,
    NOMS_VARIABLES,
    VARIABLES,
    carte,
    ecrire_plage,
    etendues,
    instruments_de,
    niveau_et_raison,
    variables_communes,
)

# Ce que représente une ligne des tables de tests de NASA, selon l'investigation.
SENS_D_UNE_LIGNE = {
    "test": "one row = one test",
    "sample": "one row = one sample",
    "test day": "one row = one day of tests",
    "session": "one row = one session",
    "planned condition set": "one row = one planned set of conditions, not a test that was run",
    "published data item": "one row = one published data item",
}
CONSEQUENCES = {
    1: "Their results can be read side by side.",
    2: "Comparing them shows whether a result holds in other hardware or at another scale.",
    3: "They answer different questions: compare what they study rather than their numbers.",
}
ABSENT = "not recorded"


def ligne_psi(table: pd.DataFrame, identifiant: str) -> pd.Series | None:
    """La ligne d'une investigation dans une table complète de PSI, ou None si la table ne l'a pas."""
    if table.empty or "investigation_id" not in table.columns:
        return None
    lignes = table[table["investigation_id"] == identifiant]
    return None if lignes.empty else lignes.iloc[0]


def frequents(tests: pd.DataFrame, identifiant: str, colonne: str, combien: int = 3) -> list[tuple[str, int]]:
    """Les valeurs les plus fréquentes d'une colonne des tests d'une investigation, avec leur nombre de lignes."""
    valeurs = tests[tests["investigation_id"] == identifiant][colonne].dropna()
    return [(str(valeur), int(nombre)) for valeur, nombre in valeurs.value_counts().head(combien).items()]


def nombre_de_valeurs(tests: pd.DataFrame, identifiant: str, colonne: str) -> int:
    """Le nombre de valeurs différentes d'une colonne des tests d'une investigation."""
    return int(tests[tests["investigation_id"] == identifiant][colonne].nunique())


def periode(psi: pd.Series | None) -> str:
    """Les années de début et de fin du projet sur PSI, par exemple « 2007 to 2016 »."""
    if psi is None:
        return ABSENT
    annees = [str(psi.get(colonne))[-4:] for colonne in ("start_date", "end_date")]
    annees = [annee for annee in annees if annee.isdigit()]
    return ecrire_plage(int(annees[0]), int(annees[-1])) if annees else ABSENT


def sens_des_lignes(psi: pd.Series | None) -> str:
    """Ce que représente une ligne de la table de tests de cette investigation, ou une chaîne vide."""
    if psi is None or pd.isna(psi.get("row_levels")):
        return ""
    return SENS_D_UNE_LIGNE.get(str(psi["row_levels"]), "")


def portrait(fiche: pd.Series, tests: pd.DataFrame, psi: pd.Series | None) -> dict[str, str]:
    """Ce qu'il faut savoir d'une investigation avant de la comparer : un libellé, une valeur."""
    identifiant = fiche["id"]
    lignes = int((tests["investigation_id"] == identifiant).sum())
    sens = sens_des_lignes(psi)
    combustibles = [nom for nom, _ in frequents(tests, identifiant, "combustible")]
    nombre = nombre_de_valeurs(tests, identifiant, "combustible")
    conditions = [
        f"{NOMS_VARIABLES[variable][0]} {ecrire_plage(*etendue)} {NOMS_VARIABLES[variable][1]}"
        for variable in VARIABLES
        for etendue in etendues(tests, [identifiant], variable).values()
    ]
    return {
        "Where": _texte(psi.get("flight_platform") if psi is not None else None),
        "Project dates": periode(psi),
        "Hardware": _texte(fiche["materiel"]),
        "Fuels tested": f"{nombre}: {', '.join(combustibles)}{' and others' if nombre > 3 else ''}"
        if nombre
        else ABSENT,
        "Conditions tested": "; ".join(conditions) or ABSENT,
        "Test rows": f"{lignes} ({sens})" if sens and lignes else str(lignes),
        "Papers listed by NASA": _texte(psi.get("n_publications") if psi is not None else None),
    }


def _texte(valeur: object) -> str:
    return ABSENT if pd.isna(valeur) or str(valeur) == INCONNU else str(valeur)


def cote_a_cote(
    fiches: pd.DataFrame, tests: pd.DataFrame, ids: list[str], investigations_psi: pd.DataFrame
) -> pd.DataFrame:
    """Le tableau complet : une ligne par critère, une colonne par investigation, et une colonne `same`.

    `same` vaut « same », « different » ou « not recorded » (aucune investigation n'a la valeur).
    """
    colonnes = {}
    for identifiant in ids:
        fiche = fiches[fiches["id"] == identifiant].iloc[0]
        fins = frequents(tests, identifiant, "resultat")
        colonnes[identifiant] = {
            "pilier": _texte(fiche["pilier"]),
            "type_combustible": _texte(fiche["type_combustible"]),
            **portrait(fiche, tests, ligne_psi(investigations_psi, identifiant)),
            "How tests ended": "; ".join(f"{valeur} ({nombre})" for valeur, nombre in fins) or ABSENT,
            "Measuring instruments": str(len(instruments_de(fiche["capteurs"]))) or ABSENT,
        }
    tableau = pd.DataFrame(colonnes)
    absent_partout = (tableau == ABSENT).all(axis=1)
    identique = tableau.nunique(axis=1) == 1
    verdicts = zip(absent_partout, identique, strict=True)
    tableau.insert(0, "same", [ABSENT if absent else "same" if pareil else "different" for absent, pareil in verdicts])
    return tableau.rename_axis("critère")


def mesures(fiches: pd.DataFrame, ids: list[str]) -> tuple[list[str], dict[str, list[str]]]:
    """Les instruments cités par toutes les investigations, puis ceux propres à chacune."""
    par_id = {
        identifiant: instruments_de(capteurs)
        for identifiant, capteurs in fiches.set_index("id").loc[ids, "capteurs"].items()
    }
    communs = set.intersection(*par_id.values())
    return sorted(communs), {identifiant: sorted(instruments - communs) for identifiant, instruments in par_id.items()}


def liens_nasa(relations: pd.DataFrame, ids: list[str], noms: dict[str, str]) -> list[str]:
    """Les liens que NASA indique entre ces investigations, en phrases."""
    if relations.empty:
        return []
    entre_elles = relations[relations["from_id"].isin(ids) & relations["to_id"].isin(ids)]
    paires = {(ligne["from_id"], ligne["to_id"], ligne["relation"]) for _, ligne in entre_elles.iterrows()}
    phrases = []
    for depart, arrivee, relation in sorted(paires):
        if relation == "related to" and (arrivee, depart, relation) in paires and depart > arrivee:
            continue  # « A related to B » et « B related to A » ne font qu'une phrase
        verbe = "reuses data from" if relation == "reuses data from" else "is listed by NASA as related to"
        phrases.append(f"{noms[depart]} {verbe} {noms[arrivee]}.")
    return phrases


def explication_carte(tests: pd.DataFrame, ids: list[str]) -> str:
    """Pourquoi le graphique est affiché, ou pourquoi il ne l'est pas."""
    communes = [NOMS_VARIABLES[variable][0] for variable in variables_communes(tests, ids)]
    if carte(tests, ids):
        return (
            f"Chart shown because NASA's tables give both {communes[0]} and {communes[1]} for every investigation here."
        )
    if not communes:
        return "No chart: NASA's tables give no test condition (oxygen, pressure, air flow) for all of them."
    if len(communes) == 1:
        return (
            f"No chart: {communes[0]} is the only test condition recorded for all of them. "
            "With a single condition, the ranges in the table already say everything a chart would."
        )
    return f"No chart: fewer than {MINIMUM_DE_POINTS} distinct test points have both {communes[0]} and {communes[1]}."


def resume(
    fiches: pd.DataFrame,
    tests: pd.DataFrame,
    ids: list[str],
    oxygene_habitat: float | None = None,
    habitat: str = "",
    relations: pd.DataFrame | None = None,
    investigations_psi: pd.DataFrame | None = None,
) -> dict[str, list[str]]:
    """Ce qui ressort de la comparaison, en phrases rangées par thème ; `ids[0]` est l'investigation de départ.

    `oxygene_habitat` est le taux d'oxygène de l'habitat quand l'énoncé le donne, sinon None.
    Un thème sans rien à dire n'apparaît pas.
    """
    noms = dict(zip(fiches["id"], fiches["nom"], strict=True))
    depart = fiches[fiches["id"] == ids[0]].iloc[0]
    themes: dict[str, list[str]] = {}

    relation = []
    for autre in ids[1:]:
        niveau, raison = niveau_et_raison(depart, fiches[fiches["id"] == autre].iloc[0])
        relation.append(
            f"{noms[autre]} is {NIVEAUX[niveau].lower()} to {noms[ids[0]]}: {raison.lower()}. {CONSEQUENCES[niveau]}"
        )
    if relations is not None:
        relation += liens_nasa(relations, ids, noms)
    themes["How they relate"] = relation

    oxygene = etendues(tests, ids, "oxygene_pct")
    if oxygene_habitat is not None:
        niveau_habitat = f"the {habitat} oxygen level ({oxygene_habitat:g} %)"
        pour_habitat = []
        for identifiant in ids:
            if identifiant not in oxygene:
                pour_habitat.append(f"{noms[identifiant]} has no oxygen value in NASA's tables.")
                continue
            plus_haut = oxygene[identifiant][1]
            valeurs = tests[tests["investigation_id"] == identifiant]["oxygene_pct"]
            au_dessus = int((valeurs >= oxygene_habitat).sum())
            if au_dessus:
                pour_habitat.append(
                    f"{noms[identifiant]} has {au_dessus} test row(s) at or above {niveau_habitat}, "
                    f"up to {plus_haut:g} %."
                )
            else:
                pour_habitat.append(f"{noms[identifiant]} stops at {plus_haut:g} % oxygen, below {niveau_habitat}.")
        themes["For your habitat"] = pour_habitat

    conditions, absentes = [], []
    for variable in VARIABLES:
        nom, unite = NOMS_VARIABLES[variable]
        connues = etendues(tests, ids, variable)
        if not connues:
            absentes.append(nom)
        elif len(connues) < len(ids):
            detail = ", ".join(f"{noms[i]} ({ecrire_plage(mini, maxi)} {unite})" for i, (mini, maxi) in connues.items())
            conditions.append(f"{nom.capitalize()} is only recorded for {detail}.")
        else:
            bas = max(mini for mini, _ in connues.values())
            haut = min(maxi for _, maxi in connues.values())
            if bas <= haut:
                dedans = ", ".join(f"{noms[i]} {_lignes_entre(tests, i, variable, bas, haut)}" for i in ids)
                conditions.append(
                    f"{nom.capitalize()} ranges overlap at {ecrire_plage(bas, haut)} {unite} "
                    f"(test rows there: {dedans})."
                )
            else:
                detail = ", ".join(f"{noms[i]} {ecrire_plage(mini, maxi)}" for i, (mini, maxi) in connues.items())
                conditions.append(f"{nom.capitalize()} ranges do not overlap ({unite}): {detail}.")
    if absentes:
        conditions.append(f"Not recorded in NASA's tables for any of them: {', '.join(absentes)}.")
    themes["Test conditions"] = conditions

    combustibles = []
    for identifiant in ids:
        nombre = nombre_de_valeurs(tests, identifiant, "combustible")
        if nombre:
            exemples = ", ".join(nom for nom, _ in frequents(tests, identifiant, "combustible"))
            combustibles.append(
                f"{noms[identifiant]} burned {nombre} fuel(s): {exemples}{' and others' if nombre > 3 else ''}."
            )
    fins = {identifiant: frequents(tests, identifiant, "resultat", 1) for identifiant in ids}
    for identifiant, plus_frequent in fins.items():
        if plus_frequent:
            valeur, nombre = plus_frequent[0]
            combustibles.append(
                f"{noms[identifiant]} records how each test ended, most often “{valeur}” ({nombre} rows)."
            )
    sans_fin = [noms[identifiant] for identifiant, plus_frequent in fins.items() if not plus_frequent]
    if sans_fin:
        combustibles.append(f"How each test ended is not recorded for {', '.join(sans_fin)}.")
    themes["Fuels and results"] = combustibles

    donnees = [
        "Rows in NASA's test tables: "
        + ", ".join(f"{noms[i]} {int((tests['investigation_id'] == i).sum())}" for i in ids)
        + "."
    ]
    if investigations_psi is not None:
        sens = {noms[i]: sens_des_lignes(ligne_psi(investigations_psi, i)) for i in ids}
        if len({valeur for valeur in sens.values() if valeur}) > 1:
            detail = "; ".join(f"{nom}: {valeur}" for nom, valeur in sens.items() if valeur)
            donnees.append(f"Their rows do not mean the same thing ({detail}), so the counts are not comparable.")
    communs, _ = mesures(fiches, ids)
    if communs:
        donnees.append(f"They share {len(communs)} measuring instrument(s), for example {', '.join(communs[:2])}.")
    else:
        donnees.append("No measuring instrument is listed for all of them.")
    themes["Data and instruments"] = donnees

    return {theme: phrases for theme, phrases in themes.items() if phrases}


def _lignes_entre(tests: pd.DataFrame, identifiant: str, variable: str, bas: float, haut: float) -> int:
    valeurs = tests[tests["investigation_id"] == identifiant][variable]
    return int(valeurs.between(bas, haut).sum())
