"""La synthèse des investigations les plus pertinentes : là où elles s'accordent et là où il faut faire attention.

Pour la page 1 (rôle F). Les accords et les désaccords viennent des rapports NASA eux-mêmes : `constats_nasa.py`
range les constats tirés des rapports finaux (et des tables de tests PSI), chacun avec un thème, un effet, une
citation exacte et sa page. Deux investigations s'accordent quand elles ont le même thème et le même effet ;
elles se contredisent quand leurs effets sont déclarés contraires (`CONTRAIRES`). S'ajoutent les points
d'attention comptés sur les tests (atmosphère, émulateur, combustibles différents, peu de tests).
Les phrases s'affichent sur le site : elles sont en anglais.
"""

import pandas as pd

from flame.recherche.conditions import (
    atmosphere_connue,
    decrire_plages,
    nom_de_l_environnement,
    tests_dans_les_plages,
)
from flame.recherche.constats_nasa import CONSTATS
from flame.recherche.lacunes import EMULATEURS_DE_SOLIDE
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

# Ce que dit un effet, pour la phrase d'accord « X and Y both found that … ».
EFFETS = {
    "low_flow_quench": "flames go out when the air flow slows to a few cm/s",
    "faster_with_flow": "flames spread faster when the air flow is stronger",
    "more_o2_burns_more_easily": "more oxygen makes a fire start or keep burning more easily",
    "large_flames_die_radiating": "large flames in microgravity go out by losing heat through radiation",
    "cool_flames_exist": "cool flames, burning with almost no light, can follow or replace a visible flame",
    "1g_test_harsher": "NASA's 1-g screening test burned samples more than microgravity did",
    "1g_test_misses": "NASA's 1-g screening test can miss how a material behaves in microgravity",
    "toxic_co": "these fires produce a lot of carbon monoxide",
    "small_samples_only": "earlier experiments burned samples no larger than 10 cm",
    "smaller_with_more_o2": "flames are smaller in richer oxygen",
    "soot_at_ignition_only": "soot appears only at ignition",
    "field_moves_soot": "an electric field moves soot around the flame",
    "more_air_less_soot": "more air flow delays soot emission",
    "droplets_go_out": "fuel droplets often go out before burning completely",
}
# Les effets qui se contredisent sur un même thème.
CONTRAIRES = {"1g_test_harsher": "1g_test_misses", "1g_test_misses": "1g_test_harsher"}
# Le nom de chaque thème, pour dire sur quoi deux rapports ne sont pas d'accord.
THEMES = {"one_g_vs_microgravity": "NASA's 1-g screening test"}


def charger_constats() -> pd.DataFrame:
    """Les constats des rapports NASA : investigation, thème, effet, important, constat, citation, source, page."""
    return pd.DataFrame(CONSTATS)


def _source(constat: pd.Series) -> str:
    """« BASS-II Summary Report, p. 109 », ou le nom seul quand il n'y a pas de page."""
    return f"{constat['source']}, p. {constat['page']}" if constat["page"] else str(constat["source"])


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

    for _, fiche in choisies.iterrows():
        nb_tests = pd.to_numeric(fiche.get("nb_tests"), errors="coerce")
        if pd.notna(nb_tests) and nb_tests < PEU_DE_TESTS:
            phrases.append(f"{fiche['nom']} has only {nb_tests:g} test(s): thin evidence.")
    return phrases


def _accords_des_rapports(choisies: pd.DataFrame, constats: pd.DataFrame) -> list[str]:
    """Les accords : au moins deux des investigations ont le même thème et le même effet."""
    noms = dict(zip(choisies["id"], choisies["nom"], strict=True))
    siens = constats[constats["investigation_id"].isin(noms)]
    phrases = []
    for (_, effet), groupe in siens.groupby(["theme", "effet"], sort=False):
        groupe = groupe.drop_duplicates("investigation_id")
        if len(groupe) < 2:
            continue
        qui = [noms[i] for i in groupe["investigation_id"]]
        sujet = f"All {len(qui)}" if len(qui) == len(choisies) and len(qui) > 2 else f"{_liste(qui)} both"
        sources = "; ".join(_source(c) for _, c in groupe.iterrows())
        phrases.append(f"{sujet} found that {EFFETS.get(effet, effet)} ({sources}).")
    return phrases


def _attention_des_rapports(choisies: pd.DataFrame, constats: pd.DataFrame) -> list[str]:
    """Les désaccords (effets contraires sur un même thème), puis les constats importants d'un seul rapport."""
    noms = dict(zip(choisies["id"], choisies["nom"], strict=True))
    siens = constats[constats["investigation_id"].isin(noms)]
    phrases = []
    deja_vus = set()
    for _, premier in siens.iterrows():
        contraire = CONTRAIRES.get(premier["effet"])
        opposes = siens[
            (siens["theme"] == premier["theme"])
            & (siens["effet"] == contraire)
            & (siens["investigation_id"] != premier["investigation_id"])
        ]
        for _, second in opposes.iterrows():
            paire = frozenset((premier.name, second.name))
            if paire in deja_vus:
                continue
            deja_vus.add(paire)
            sujet = THEMES.get(premier["theme"], premier["theme"].replace("_", " "))
            phrases.append(
                f"{noms[premier['investigation_id']]} and {noms[second['investigation_id']]} do not agree on "
                f"{sujet}. {noms[premier['investigation_id']]}: {premier['constat']} ({_source(premier)}) "
                f"{noms[second['investigation_id']]}: {second['constat']} ({_source(second)})"
            )
    # Un constat important qu'un seul des rapports affichés soutient (sauf s'il est déjà dans un désaccord).
    dans_un_desaccord = {index for paire in deja_vus for index in paire}
    partages = siens.groupby(["theme", "effet"])["investigation_id"].nunique()
    for index, constat in siens[siens["important"]].iterrows():
        if partages[(constat["theme"], constat["effet"])] == 1 and index not in dans_un_desaccord:
            phrases.append(
                f"Only {noms[constat['investigation_id']]} reports this: {constat['constat']} ({_source(constat)})"
            )
    return phrases


def citations_des_plus_pertinentes(fiches: pd.DataFrame, scenario: dict | None, nombre: int = 3) -> pd.DataFrame:
    """Les constats des rapports NASA des `nombre` investigations affichées, avec leur citation exacte."""
    choisies = les_plus_pertinentes(fiches, scenario).head(nombre)
    noms = dict(zip(choisies["id"], choisies["nom"], strict=True))
    constats = charger_constats()
    siens = constats[constats["investigation_id"].isin(noms)].copy()
    siens["investigation"] = siens["investigation_id"].map(noms)
    siens["reference"] = [_source(c) for _, c in siens.iterrows()]
    return siens[["investigation", "constat", "citation", "reference"]]


def synthese_des_plus_pertinentes(
    fiches: pd.DataFrame,
    tests: pd.DataFrame,
    scenario: dict | None,
    nombre: int = 3,
) -> dict[str, list[str]]:
    """Les `nombre` investigations les plus pertinentes pour `scenario`, comparées entre elles.

    Renvoie {"investigations": leurs noms, "accords": où elles s'accordent, "attention": où faire attention}.
    Les accords et les désaccords viennent des constats des rapports NASA (`constats_nasa.py`). Sans constat
    partagé, les accords retombent sur ce que les fiches ont en commun (combustible, matériaux, oxygène).
    """
    choisies = les_plus_pertinentes(fiches, scenario).head(nombre)
    if choisies.empty:
        return {"investigations": [], "accords": [], "attention": []}
    constats = charger_constats()
    accords = _accords_des_rapports(choisies, constats)
    if not accords:
        accords = ["Their NASA reports do not study the same effect, so no finding is shared. In common:"]
        accords += _accords(choisies, tests)
    return {
        "investigations": list(choisies["nom"]),
        "accords": accords,
        "attention": _attention_des_rapports(choisies, constats) + _attention(choisies, tests, scenario),
    }
