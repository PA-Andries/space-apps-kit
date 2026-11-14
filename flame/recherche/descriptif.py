"""Le descriptif d'une investigation : ce que l'expérience a étudié, et pourquoi elle compte pour l'environnement.

Tout vient des tables de NASA : le titre complet, la plateforme, les dates, les objectifs, l'approche et
l'hypothèse sont ceux de `data/psi/investigations.csv` (rôle B), recopiés tels quels. Les raisons sont celles
de `detail_du_score`. Rien n'est rédigé ni deviné ici : un texte absent reste absent.
Les textes renvoyés s'affichent sur le site : ils sont en anglais.
"""

import pandas as pd

from flame.commun import charger_table_psi
from flame.recherche.score import detail_du_score

# Les textes de NASA montrés en entier, dans cet ordre : colonne de la table PSI, titre affiché.
TEXTES_NASA = {
    "objectives": "Objectives",
    "approach": "Approach",
    "hypothesis": "Hypothesis",
    "impacts_earth_benefits": "Benefits on Earth",
}
LONGUEUR_COURTE = 380  # longueur maximale du début des objectifs montré sur la carte
CITEE = "Named in NASA's challenge statement as fire-safety work."


def _texte(valeur: object) -> str:
    """Le texte d'une case, ou "" quand elle est vide."""
    return "" if pd.isna(valeur) or not str(valeur).strip() else str(valeur).strip()


def debut(texte: str, maximum: int = LONGUEUR_COURTE) -> str:
    """Les premières phrases de `texte`, sans dépasser `maximum` caractères ; « … » quand le texte continue."""
    if len(texte) <= maximum:
        return texte
    coupe = texte[:maximum]
    fin_de_phrase = max(coupe.rfind(". "), coupe.rfind("? "), coupe.rfind("! "))
    if fin_de_phrase >= maximum // 3:
        return coupe[: fin_de_phrase + 1] + " …"
    return coupe.rsplit(" ", 1)[0] + " …"


def _annee(date: object) -> str:
    """« 01-14-1999 » donne « 1999 » ; une date absente donne ""."""
    texte = _texte(date)
    return texte[-4:] if len(texte) >= 4 and texte[-4:].isdigit() else ""


def _periode(ligne: pd.Series) -> str:
    debut_annee, fin_annee = _annee(ligne.get("start_date")), _annee(ligne.get("end_date"))
    if debut_annee and fin_annee:
        return debut_annee if debut_annee == fin_annee else f"{debut_annee}–{fin_annee}"
    return f"since {debut_annee}" if debut_annee else ""


def _cadre(ligne: pd.Series) -> str:
    """Où et quand : « Microgravity investigation · International Space Station (ISS) · 2010–2022 »."""
    plateforme = _texte(ligne.get("flight_platform"))
    morceaux = [
        _texte(ligne.get("project_type")).capitalize(),
        "" if plateforme == "Not Applicable" else plateforme,
        _periode(ligne),
    ]
    return " · ".join(morceau for morceau in morceaux if morceau)


def _chiffres(fiche: pd.Series, ligne: pd.Series) -> str:
    """« 129 tests in PSI's table · 17 publications », avec seulement ce qui est noté."""
    morceaux = []
    nb_tests = pd.to_numeric(fiche.get("nb_tests"), errors="coerce")
    if pd.notna(nb_tests):
        morceaux.append(f"{nb_tests:g} test rows in PSI")
    nb_publications = pd.to_numeric(ligne.get("n_publications"), errors="coerce")
    if pd.notna(nb_publications):
        morceaux.append(f"{nb_publications:g} publications listed by PSI")
    return " · ".join(morceaux)


def descriptif(
    fiche: pd.Series,
    scenario: dict | None = None,
    tests: pd.DataFrame | None = None,
    investigations_psi: pd.DataFrame | None = None,
    pertinence: pd.DataFrame | None = None,
) -> dict:
    """Ce que `fiche` a étudié et pourquoi elle compte pour `scenario`.

    - `titre` : le titre complet de NASA, ou "" ;
    - `cadre` : type d'étude, plateforme et années ; `chiffres` : nombre de tests et de publications ;
    - `en_bref` : la phrase de résumé de la fiche ; `objectif_court` : le début des objectifs de NASA ;
    - `textes` : {titre affiché: texte complet de NASA} pour les objectifs, l'approche, l'hypothèse et les
      retombées sur Terre (seulement ceux qui existent) ;
    - `raisons` : [(critère, explication), ...] de `detail_du_score`, sans les points ;
    - `citee` : la phrase « citée dans l'énoncé », ou "".

    `investigations_psi` (table `investigations` du rôle B) est lue sur le disque quand on ne la donne pas.
    """
    investigations_psi = charger_table_psi("investigations") if investigations_psi is None else investigations_psi
    lignes = (
        investigations_psi[investigations_psi["investigation_id"] == fiche.get("id")]
        if "investigation_id" in investigations_psi.columns
        else investigations_psi
    )
    ligne = lignes.iloc[0] if len(lignes) else pd.Series(dtype=object)
    objectifs = _texte(ligne.get("objectives")) or _texte(fiche.get("objectif"))
    textes = {titre: _texte(ligne.get(colonne)) for colonne, titre in TEXTES_NASA.items()}
    if not textes["Objectives"]:
        textes["Objectives"] = objectifs
    raisons = detail_du_score(fiche, scenario, pertinence, tests)
    citee = pd.to_numeric(ligne.get("cited_in_statement_as_fire_safety"), errors="coerce") == 1
    return {
        "titre": _texte(ligne.get("title")),
        "cadre": _cadre(ligne),
        "chiffres": _chiffres(fiche, ligne),
        "en_bref": _texte(fiche.get("resume")) or _texte(ligne.get("one_liner")),
        "objectif_court": debut(objectifs),
        "textes": {titre: texte for titre, texte in textes.items() if texte},
        "raisons": list(zip(raisons["critere"], raisons["explication"], strict=True)),
        "citee": CITEE if citee else "",
    }
