"""Les lieux proposés sur l'accueil : la Terre comme référence, puis les habitats du contrat.

La Terre n'est pas un habitat du contrat : la choisir ne change pas l'habitat utilisé par
les autres pages, qui gardent le dernier habitat spatial choisi.
"""

import streamlit as st

from flame.commun import ATMOSPHERES, HABITATS, get_scenario

TERRE = "Terre"
LIEUX = [TERRE, *HABITATS]

# Terre : chiffres de l'énoncé (21 % d'oxygène, 14,7 psi soit environ 101 kPa).
ATMOSPHERE_TERRE = (21, 101)
# Atmosphères données par l'énoncé. Les autres sont des hypothèses de l'équipe (flame/commun/constantes.py).
LIEUX_ENONCE = {TERRE, "Base lunaire", "Rover pressurisé"}

# Gravité en fraction de la gravité terrestre, pour l'illustration 3D seulement.
# Lune 0,17 et Mars 0,38 : valeurs physiques usuelles. Le rover est supposé sur la Lune.
GRAVITES = {
    TERRE: 1.0,
    "Vaisseau": 0.0,
    "Station": 0.0,
    "Base lunaire": 0.17,
    "Base martienne": 0.38,
    "Rover pressurisé": 0.17,
}


def lieu_courant() -> str | None:
    """Le lieu choisi sur l'accueil, ou None tant que l'utilisateur n'en a pas choisi."""
    return st.session_state.get("ui_lieu")


def pilier_courant() -> str | None:
    """Le pilier choisi sur l'accueil, ou None tant que l'utilisateur n'a pas appuyé sur un bouton."""
    return get_scenario()["pilier"] if st.session_state.get("ui_pilier_choisi") else None


def conditions_lieu(lieu: str) -> dict:
    """Oxygène (%), pression (kPa), gravité (0 à 1) d'un lieu, et si l'atmosphère vient de l'énoncé."""
    oxygene_pct, pression_kpa = ATMOSPHERE_TERRE if lieu == TERRE else ATMOSPHERES[lieu]
    return {
        "oxygene_pct": oxygene_pct,
        "pression_kpa": pression_kpa,
        "gravite": GRAVITES[lieu],
        "source_enonce": lieu in LIEUX_ENONCE,
    }


def choisir_lieu(lieu: str) -> None:
    """Retient le lieu ; un habitat devient aussi l'habitat du scénario (barre latérale)."""
    st.session_state["ui_lieu"] = lieu
    if lieu != TERRE:
        st.session_state["ui_habitat"] = lieu


def choisir_pilier(pilier: str) -> None:
    """Retient le pilier du scénario (barre latérale)."""
    st.session_state["ui_pilier"] = pilier
    st.session_state["ui_pilier_choisi"] = True
