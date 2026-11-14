"""La synthèse des investigations les plus pertinentes : là où elles s'accordent et là où il faut faire attention.

Pour la page 1 « My environment » (rôle F) : quelques phrases courtes, comptées sur les fiches et les tests PSI.
Rien n'est deviné : si une donnée manque, la phrase le dit. Les phrases s'affichent sur le site : elles sont en anglais.
"""

import pandas as pd

from flame.recherche.conditions import (
    atmosphere_connue,
    decrire_plages,
    nom_de_l_environnement,
    tests_dans_les_plages,
)
from flame.recherche.lacunes import EMULATEURS_DE_SOLIDE, champs_inconnus
from flame.recherche.moteur import les_plus_pertinentes
from flame.recherche.score import type_de_base
from flame.ui import label

# Les matériaux qu'on sait reconnaître dans la colonne `combustible` (en minuscules) et leur nom affiché.
MATERIAUX = {
    "PMMA (acrylic)": ("pmma",),
    "SIBAL (cotton-fiberglass fabric)": ("sibal",),
    "Nomex": ("nomex",),
    "wax candles": ("wax", "candle"),
    "silicone": ("silicone",),
    "Ultem": ("ultem",),
    "ethylene gas": ("c2h4",),
    "methane gas": ("ch4",),
}
# En dessous de ce nombre de tests, on prévient que les données sont minces (hypothèse du rôle C).
PEU_DE_TESTS = 10


def _liste(noms: list[str]) -> str:
    """« A », « A and B », « A, B and C »."""
    return noms[0] if len(noms) == 1 else f"{', '.join(noms[:-1])} and {noms[-1]}"


def _materiaux(fiche: pd.Series) -> set[str]:
    texte = str(fiche.get("combustible") or "").lower()
    return {nom for nom, mots in MATERIAUX.items() if any(mot in texte for mot in mots)}


def _plage_oxygene(tests: pd.DataFrame) -> tuple[float, float] | None:
    oxygene = pd.to_numeric(tests["oxygene_pct"], errors="coerce").dropna()
    return None if oxygene.empty else (float(oxygene.min()), float(oxygene.max()))


def _accords(choisies: pd.DataFrame, tests: pd.DataFrame) -> list[str]:
    phrases: list[str] = []
    noms = dict(zip(choisies["id"], choisies["nom"], strict=True))

    types = choisies.set_index("id")["type_combustible"].map(type_de_base)
    for type_combustible, ids in types.groupby(types).groups.items():
        if type_combustible and len(ids) == len(choisies):
            phrases.append(f"All {len(choisies)} burn {label(type_combustible)} fuel.")
        elif type_combustible and len(ids) >= 2:
            phrases.append(f"{_liste([noms[i] for i in ids])} both burn {label(type_combustible)} fuel.")

    # Les matériaux brûlés par au moins deux d'entre elles, regroupés par groupe d'investigations.
    par_materiau: dict[str, list[str]] = {}
    for _, fiche in choisies.iterrows():
        for materiau in _materiaux(fiche):
            par_materiau.setdefault(materiau, []).append(fiche["nom"])
    par_groupe: dict[tuple[str, ...], list[str]] = {}
    for materiau, qui in sorted(par_materiau.items()):
        if len(qui) >= 2:
            par_groupe.setdefault(tuple(qui), []).append(materiau)
    for qui, materiaux in par_groupe.items():
        sujet = f"All {len(choisies)}" if len(qui) == len(choisies) else f"{_liste(list(qui))} both"
        phrases.append(f"{sujet} burned {_liste(materiaux)}: their results can be read side by side.")

    plages = {i: _plage_oxygene(tests[tests["investigation_id"] == i]) for i in choisies["id"]}
    connues = {i: plage for i, plage in plages.items() if plage is not None}
    if len(connues) >= 2:
        bas = max(plage[0] for plage in connues.values())
        haut = min(plage[1] for plage in connues.values())
        if len(connues) == len(choisies):
            sujet = f"All {len(choisies)}"
        else:
            sujet = f"{_liste([noms[i] for i in connues])} {'both' if len(connues) == 2 else 'all'}"
        if bas <= haut:
            commun = f"{bas:g} %" if bas == haut else f"{bas:g} to {haut:g} %"
            phrases.append(f"{sujet} ran tests at {commun} oxygen: a common ground to compare them.")
    return phrases


def _attention(choisies: pd.DataFrame, tests: pd.DataFrame, scenario: dict | None) -> list[str]:
    phrases: list[str] = []
    noms = dict(zip(choisies["id"], choisies["nom"], strict=True))
    nom_env = nom_de_l_environnement(scenario)

    if not atmosphere_connue(scenario):
        phrases.append(f"The atmosphere of {nom_env} is unknown: none of their tests can be checked against it.")
    else:
        dehors = [
            noms[i]
            for i in choisies["id"]
            if tests_dans_les_plages(tests[tests["investigation_id"] == i], scenario).empty
        ]
        if dehors:
            verbe = "has" if len(dehors) == 1 else "have"
            phrases.append(f"{_liste(dehors)} {verbe} no test in your atmosphere ({decrire_plages(scenario)}).")

    types = {type_de_base(t) for t in choisies["type_combustible"]} - {""}
    if len(types) > 1:
        phrases.append(
            f"They burn different fuels ({_liste(sorted(label(t) for t in types))}): "
            "a flame on one does not tell how the other behaves."
        )

    for i in choisies["id"]:
        if i in EMULATEURS_DE_SOLIDE:
            phrases.append(
                f"{noms[i]} is a gas burner that emulates a burning solid: not a real fabric or plastic sample."
            )

    plages = {i: _plage_oxygene(tests[tests["investigation_id"] == i]) for i in choisies["id"]}
    connues = {i: plage for i, plage in plages.items() if plage is not None}
    if len(connues) >= 2 and max(p[0] for p in connues.values()) > min(p[1] for p in connues.values()):
        detail = "; ".join(f"{noms[i]} {p[0]:g} to {p[1]:g} %" for i, p in connues.items())
        phrases.append(f"Their oxygen ranges do not all overlap ({detail}): compare them with care.")

    gravite = pd.to_numeric((scenario or {}).get("gravite"), errors="coerce")
    if pd.notna(gravite) and 0 < gravite < 1:
        phrases.append(
            f"None of them was tested at the partial gravity of {nom_env} ({gravite:g} g): "
            "microgravity and Earth-gravity data only."
        )

    manquants: dict[str, list[str]] = {}
    for _, fiche in choisies.iterrows():
        nb_tests = pd.to_numeric(fiche.get("nb_tests"), errors="coerce")
        if pd.notna(nb_tests) and nb_tests < PEU_DE_TESTS:
            phrases.append(f"{fiche['nom']} has only {nb_tests:g} test(s): thin evidence.")
        for champ in champs_inconnus(fiche):
            manquants.setdefault(champ, []).append(fiche["nom"])
    for champ, qui in manquants.items():
        phrases.append(f"No recorded {champ} for {_liste(qui)}.")
    return phrases


def synthese_des_plus_pertinentes(
    fiches: pd.DataFrame,
    tests: pd.DataFrame,
    scenario: dict | None,
    nombre: int = 3,
) -> dict[str, list[str]]:
    """Les `nombre` investigations les plus pertinentes pour `scenario`, comparées entre elles.

    Renvoie {"investigations": leurs noms, "accords": où elles s'accordent, "attention": où faire attention}.
    """
    choisies = les_plus_pertinentes(fiches, scenario).head(nombre)
    if choisies.empty:
        return {"investigations": [], "accords": [], "attention": []}
    return {
        "investigations": list(choisies["nom"]),
        "accords": _accords(choisies, tests),
        "attention": _attention(choisies, tests, scenario),
    }
