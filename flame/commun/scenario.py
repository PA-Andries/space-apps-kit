"""Le scénario de l'utilisateur : son environnement, mémorisé pour toutes les pages.

Seul ce fichier lit et écrit le scénario dans `st.session_state`.
"""

import streamlit as st

from flame.commun.habitats import conditions_habitat

HABITAT_PAR_DEFAUT = "Base lunaire"
# Les clés qui dépendent de l'habitat : choisir un habitat les pré-remplit.
CLES_CONDITIONS = ("oxygene_pct", "pression_kpa", "gravite")
# Les clés qui s'écrivent en plage (minimum, maximum) ; None = pas de borne.
CLES_PLAGE = ("oxygene_pct", "pression_kpa", "debit_air_cm_s")
CLES_SCENARIO = (
    "habitat",
    "oxygene_pct",
    "pression_kpa",
    "gravite",
    "type_combustible",
    "debit_air_cm_s",
    "pilier",
    "profil",
)
# Les trois clés d'origine gardent leur nom dans la session ; les nouvelles sont préfixées pour ne pas
# entrer en collision avec la clé d'un widget.
_CLES_D_ORIGINE = ("habitat", "pilier", "profil")
_NON_DONNE = object()


def _cle_session(cle: str) -> str:
    return cle if cle in _CLES_D_ORIGINE else f"scenario_{cle}"


def _valeurs_par_defaut(habitat: str) -> dict:
    conditions = conditions_habitat(habitat)
    return {
        "habitat": habitat,
        "oxygene_pct": conditions["oxygene_pct"],
        "pression_kpa": conditions["pression_kpa"],
        "gravite": conditions["gravite"],
        "type_combustible": [],
        "debit_air_cm_s": (None, None),
        # Obsolète (décision du 14 nov. 17h00, les piliers sont abandonnés) : la clé reste tant que
        # les pages la lisent, puis elle sera retirée du contrat.
        "pilier": "Prévenir",
        "profil": "Étudiant",
    }


def _mise_en_forme(cle: str, valeur: object) -> object:
    """La valeur telle qu'on la range : une plage devient un couple, les combustibles une liste."""
    if cle in CLES_PLAGE:
        if valeur is None:
            return (None, None)
        if not isinstance(valeur, (tuple, list)) or len(valeur) != 2:
            raise ValueError(f"`{cle}` attend une plage (minimum, maximum), par exemple (30, None). Reçu : {valeur!r}")
        return (valeur[0], valeur[1])
    if cle == "type_combustible":
        return [] if valeur is None else list(valeur)
    return valeur


def get_scenario() -> dict:
    """Le scénario courant, avec ses 8 clés.

    - `habitat` : un nom de `HABITATS`, ou « Personnalisé » ;
    - `oxygene_pct`, `pression_kpa`, `debit_air_cm_s` : des plages (minimum, maximum), None = pas de borne ;
    - `gravite` : en g, None = inconnue ;
    - `type_combustible` : une liste parmi « solide », « liquide », « gaz » ; vide = tous ;
    - `pilier` (obsolète) et `profil`.

    Tant que l'utilisateur n'a rien saisi, l'oxygène, la pression et la gravité sont ceux de
    `conditions_habitat(habitat)`.
    """
    defauts = _valeurs_par_defaut(st.session_state.get("habitat", HABITAT_PAR_DEFAUT))
    scenario = {cle: st.session_state.get(_cle_session(cle), defauts[cle]) for cle in CLES_SCENARIO}
    scenario["type_combustible"] = list(scenario["type_combustible"])
    return scenario


def set_scenario(habitat=_NON_DONNE, pilier=_NON_DONNE, profil=_NON_DONNE, **cles) -> None:
    """Enregistre le scénario pour toutes les pages. Seules les clés données changent.

    `set_scenario(habitat, pilier, profil)` reste valable, et `set_scenario(oxygene_pct=(25, 35))` aussi.
    Quand l'habitat change, l'oxygène, la pression et la gravité qui ne sont pas donnés dans le même appel
    reprennent les valeurs de ce nouvel habitat : un scénario ne garde pas l'air de l'habitat précédent.
    """
    donnees = {"habitat": habitat, "pilier": pilier, "profil": profil, **cles}
    donnees = {cle: valeur for cle, valeur in donnees.items() if valeur is not _NON_DONNE}
    inconnues = sorted(set(donnees) - set(CLES_SCENARIO))
    if inconnues:
        raise TypeError(
            f"Clés de scénario inconnues : {', '.join(inconnues)}. Clés possibles : {', '.join(CLES_SCENARIO)}"
        )
    if "habitat" in donnees and donnees["habitat"] != st.session_state.get("habitat", HABITAT_PAR_DEFAUT):
        for cle in CLES_CONDITIONS:
            st.session_state.pop(_cle_session(cle), None)
    for cle, valeur in donnees.items():
        st.session_state[_cle_session(cle)] = _mise_en_forme(cle, valeur)
