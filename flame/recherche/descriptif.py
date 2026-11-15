"""Le descriptif d'une investigation : ce que l'expérience a étudié, et pourquoi elle compte pour l'environnement.

Tout vient des tables de NASA : le titre complet, la plateforme, les dates, les objectifs, l'approche et
l'hypothèse sont ceux de `data/psi/investigations.csv` (rôle B), recopiés tels quels. Les raisons sont celles
de `detail_du_score`. Rien n'est rédigé ni deviné ici : un texte absent reste absent.
Les textes renvoyés s'affichent sur le site : ils sont en anglais.
"""

import pandas as pd

from flame.commun import charger_table_psi
from flame.recherche.score import EMULATEURS_DE_SOLIDE, detail_du_score

# Les textes de NASA montrés en entier, dans cet ordre : colonne de la table PSI, titre affiché.
TEXTES_NASA = {
    "objectives": "Objectives",
    "approach": "Approach",
    "hypothesis": "Hypothesis",
    "impacts_earth_benefits": "Benefits on Earth",
}
LONGUEUR_COURTE = 380  # longueur maximale du début des objectifs montré sur la carte
CITEE = "Named in NASA's challenge statement."

# Les trois axes du travail de NASA sur la sécurité incendie, d'après l'énoncé du défi (« NASA's spacecraft
# fire safety work is focused on prevention, detection, and suppression »), avec les seules investigations
# que l'énoncé range lui-même sous chaque axe, et sa phrase à leur sujet, reprise au plus près.
# Les autres investigations n'ont pas d'axe ici : la colonne `fire_safety_pillar` des tables est le classement
# de l'équipe, pas celui de NASA, et elle n'est pas utilisée.
AXES = {
    "Prevention": {
        "ids": ("PSI-25", "PSI-26", "PSI-98", "PSI-99", "PSI-100"),  # BASS-II, BASS, Saffire-I, -II, -III
        "texte": (
            "Prevention is achieved by controlling ignition sources and through material selection, which "
            "depends on understanding flammability limits. This investigation is one of the flammability "
            "studies of solid materials, such as fabrics and plastics, that the statement names."
        ),
    },
    "Detection": {
        "ids": ("PSI-101", "PSI-102"),  # SAME-R, SAME
        "texte": (
            "Fire detection was tested in microgravity through the Smoke and Aerosol Measurement Experiment "
            "studies, SAME and SAME-R: this investigation is one of them."
        ),
    },
    "Suppression": {
        "ids": ("PSI-69",),  # FLEX
        "texte": (
            "Suppression was studied in this experiment through dilution of the chamber atmosphere with "
            "carbon dioxide and helium, both of which suppress fire."
        ),
    },
}
SOURCE_DES_AXES = "Source: NASA's challenge statement, which names this investigation under this axis."


def axe_de_securite(identifiant: object) -> tuple[str, str] | None:
    """L'axe sous lequel l'énoncé range l'investigation, et sa phrase : ("Prevention", "..."), ou None.

    Seules les huit investigations que l'énoncé nomme sous un axe en ont un. Rien n'est déduit pour les autres.
    """
    for axe, contenu in AXES.items():
        if identifiant in contenu["ids"]:
            return axe, contenu["texte"]
    return None


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
    # Ce sont les dates du projet dans la fiche PSI, pas celles du vol (Saffire-I : 2001–2008, vol en 2016).
    if debut_annee and fin_annee:
        annees = debut_annee if debut_annee == fin_annee else f"{debut_annee}–{fin_annee}"
        return f"project dates in PSI: {annees}"
    return f"project start in PSI: {debut_annee}" if debut_annee else ""


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
    - `citee` : la phrase « citée dans l'énoncé », ou "" ; pour une investigation que l'énoncé range sous
      un axe (prevention, detection, suppression), elle nomme l'axe et reprend la phrase de l'énoncé ;
    - `axe` : le nom de cet axe, ou "".

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
    axe = axe_de_securite(fiche.get("id"))
    phrase_generale = CITEE if citee else ""
    phrase_citee = f"named under {axe[0].lower()}. {axe[1]}" if axe else phrase_generale
    return {
        "titre": _texte(ligne.get("title")),
        # Un brûleur à gaz qui imite un solide n'est pas affiché « Solid fuel ».
        "combustible_affiche": "Gas burner emulating a solid" if fiche.get("id") in EMULATEURS_DE_SOLIDE else "",
        "cadre": _cadre(ligne),
        "chiffres": _chiffres(fiche, ligne),
        "en_bref": _texte(fiche.get("resume")) or _texte(ligne.get("one_liner")),
        "objectif_court": debut(objectifs),
        "textes": {titre: texte for titre, texte in textes.items() if texte},
        "raisons": list(zip(raisons["critere"], raisons["explication"], strict=True)),
        "citee": phrase_citee,
        "axe": axe[0] if axe else "",
    }
