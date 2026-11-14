"""Le scénario de l'utilisateur : son environnement (habitat, oxygène, pression, gravité, combustible, débit d'air),
un pilier et un profil.

Seul ce fichier lit et écrit ces clés dans `st.session_state`.
"""

import streamlit as st

from flame.commun.constantes import ATMOSPHERES, GRAVITES

SCENARIO_PAR_DEFAUT = {"habitat": "Base lunaire", "pilier": "Prévenir", "profil": "Étudiant"}
# Les clés de l'environnement. Sans valeur choisie, l'oxygène, la pression et la gravité viennent de l'habitat.
CLES_ENVIRONNEMENT = ("oxygene_pct", "pression_kpa", "gravite", "type_combustible", "debit_air_cm_s")


def environnement_de(habitat: str) -> dict[str, float | None]:
    """L'oxygène (%), la pression (kPa) et la gravité (fraction de celle de la Terre) connus pour un habitat.

    Une valeur vaut `None` quand elle est inconnue (par exemple l'atmosphère d'une base martienne).
    Pour la base lunaire et le rover, l'oxygène est un minimum et la pression un maximum (`NATURE_ATMOSPHERES`).
    """
    oxygene_pct, pression_kpa = ATMOSPHERES.get(habitat, (None, None))
    return {"oxygene_pct": oxygene_pct, "pression_kpa": pression_kpa, "gravite": GRAVITES.get(habitat)}


def get_scenario() -> dict:
    """Le scénario courant.

    Les clés `habitat`, `pilier` et `profil` sont toujours remplies. Les clés `oxygene_pct`, `pression_kpa`,
    `gravite`, `type_combustible` et `debit_air_cm_s` valent ce que l'utilisateur a choisi ; sinon l'oxygène,
    la pression et la gravité de l'habitat ; sinon `None` (inconnu ou pas choisi).
    """
    scenario = {cle: st.session_state.get(cle, defaut) for cle, defaut in SCENARIO_PAR_DEFAUT.items()}
    valeurs_habitat = environnement_de(scenario["habitat"])
    for cle in CLES_ENVIRONNEMENT:
        choisie = st.session_state.get(cle)
        scenario[cle] = choisie if choisie is not None else valeurs_habitat.get(cle)
    return scenario


def set_scenario(
    habitat: str,
    pilier: str,
    profil: str,
    *,
    oxygene_pct: float | None = None,
    pression_kpa: float | None = None,
    gravite: float | None = None,
    type_combustible: str | None = None,
    debit_air_cm_s: float | None = None,
) -> None:
    """Enregistre le scénario pour toutes les pages.

    Les valeurs d'environnement sont facultatives : avec `None`, `get_scenario()` rend celles de l'habitat.
    """
    st.session_state["habitat"] = habitat
    st.session_state["pilier"] = pilier
    st.session_state["profil"] = profil
    st.session_state["oxygene_pct"] = oxygene_pct
    st.session_state["pression_kpa"] = pression_kpa
    st.session_state["gravite"] = gravite
    st.session_state["type_combustible"] = type_combustible
    st.session_state["debit_air_cm_s"] = debit_air_cm_s
