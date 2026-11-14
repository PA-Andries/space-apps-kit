"""Mesures indépendantes : plusieurs résultats peuvent venir des mêmes données de vol.

`data/psi/relations.csv` note, depuis le champ « Related Investigations » de PSI, quelles investigations
réutilisent les données d'une autre. Une étude au sol qui réanalyse un vol n'est pas une preuve de plus :
la replier évite de compter deux fois la même mesure. Les phrases affichées sont en anglais.
"""

import pandas as pd

from flame.commun import charger_table_psi

# La relation de PSI qui dit « cette investigation réutilise les données d'une autre ».
REUTILISATION = "reuses data from"
# Au-delà, un nom d'investigation est coupé : les études au sol ont des titres d'article entiers.
LONGUEUR_MAX_NOM = 46


def acronymes() -> dict[str, str]:
    """L'acronyme PSI de chaque investigation, ou son identifiant quand PSI n'en donne pas.

    Les études au sol qui réanalysent un vol n'ont pas d'acronyme : « PSI-117 » vaut mieux que leur
    titre d'article complet.
    """
    table = charger_table_psi("investigations")
    if table.empty or "investigation_id" not in table.columns:
        return {}
    courts = {}
    for _, ligne in table.iterrows():
        identifiant = str(ligne["investigation_id"])
        acronyme = ligne.get("acronym")
        # Une case vide de pandas vaut NaN, qui est « vrai » : il faut la tester avec `pd.notna`.
        acronyme = str(acronyme).strip() if pd.notna(acronyme) else ""
        courts[identifiant] = acronyme or identifiant
    return courts


def _court(nom: str) -> str:
    """Un nom d'investigation raccourci pour tenir dans une phrase."""
    return nom if len(nom) <= LONGUEUR_MAX_NOM else f"{nom[: LONGUEUR_MAX_NOM - 1].rstrip()}…"


def chaines_de_reutilisation() -> dict[str, str]:
    """Pour chaque investigation qui réutilise des données, celle d'où elles viennent au bout de la chaîne.

    Une chaîne A → B → C donne {A: C, B: C} : on remonte jusqu'à la mesure d'origine. Sans la table
    `relations` (fichier absent), le dictionnaire est vide et personne n'est replié.
    """
    relations = charger_table_psi("relations")
    if relations.empty or not {"from_id", "to_id", "relation"} <= set(relations.columns):
        return {}
    reutilisations = relations[relations["relation"] == REUTILISATION]
    directes = {str(ligne["from_id"]): str(ligne["to_id"]) for _, ligne in reutilisations.iterrows()}
    racines: dict[str, str] = {}
    for depart in directes:
        vus = {depart}
        courant = depart
        # On suit la chaîne jusqu'à la source, en s'arrêtant si elle boucle sur elle-même.
        while courant in directes and directes[courant] not in vus:
            courant = directes[courant]
            vus.add(courant)
        racines[depart] = courant
    return racines


def independance(identifiants: object, noms: dict | None = None) -> dict:
    """Combien de mesures indépendantes dans une liste d'investigations, et lesquelles sont des réanalyses.

    {"total": n, "independantes": m, "reanalyses": {id: id d'origine}, "phrase": "..."}.
    `noms` sert à écrire les noms dans la phrase ; sans lui, les acronymes de PSI sont utilisés.
    """
    identifiants = [str(i) for i in dict.fromkeys(identifiants or []) if pd.notna(i)]
    racines = chaines_de_reutilisation()
    reanalyses = {identifiant: racines[identifiant] for identifiant in identifiants if identifiant in racines}
    origines = {racines.get(identifiant, identifiant) for identifiant in identifiants}
    resultat = {
        "total": len(identifiants),
        "independantes": len(origines),
        "reanalyses": reanalyses,
        "phrase": "",
    }
    if not identifiants:
        resultat["phrase"] = "No investigation to count."
        return resultat
    courts = acronymes()
    if not reanalyses:
        resultat["phrase"] = f"{len(identifiants)} investigation(s), all independent measurements."
        return resultat

    def nommer(identifiant: str) -> str:
        # L'acronyme de PSI d'abord : c'est le nom court. `noms` ne sert que pour un identifiant absent.
        return _court(str(courts.get(identifiant) or (noms or {}).get(identifiant) or identifiant))

    paires = ", ".join(
        f"{nommer(identifiant)} reuses the data of {nommer(origine)}"
        for identifiant, origine in sorted(reanalyses.items())
    )
    resultat["phrase"] = (
        f"{len(identifiants)} investigation(s), but only {len(origines)} independent measurement(s): {paires}."
    )
    return resultat
