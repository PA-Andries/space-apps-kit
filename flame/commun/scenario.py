"""Le scénario de l'utilisateur : un habitat, un pilier, un profil.

Seul ce fichier lit et écrit ces trois clés dans `st.session_state`.
"""

import streamlit as st

SCENARIO_PAR_DEFAUT = {"habitat": "Base lunaire", "pilier": "Prévenir", "profil": "Étudiant"}


def get_scenario() -> dict[str, str]:
    """Le scénario courant, par exemple {"habitat": "Station", "pilier": ..., "profil": ...}."""
    return {cle: st.session_state.get(cle, defaut) for cle, defaut in SCENARIO_PAR_DEFAUT.items()}


def set_scenario(habitat: str, pilier: str, profil: str) -> None:
    """Enregistre le scénario pour toutes les pages."""
    st.session_state["habitat"] = habitat
    st.session_state["pilier"] = pilier
    st.session_state["profil"] = profil
