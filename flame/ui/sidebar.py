"""What shows on every page: the scenario in the sidebar, and the warnings."""

import streamlit as st

from flame.commun import HABITATS, PILIERS, PROFILS, donnees_exemple, get_scenario, set_scenario
from flame.ui.labels import label
from flame.ui.places import body_of

# Profiles offered in the sidebar. "Étudiant" is removed at role F's request;
# it stays in the contract (PROFILS) until role A changes it.
PROFILES_OFFERED = [profile for profile in PROFILS if profile != "Étudiant"]


def _follow_habitat() -> None:
    """A habitat chosen in the sidebar also becomes the place of the home page."""
    habitat = st.session_state["ui_habitat"]
    st.session_state["ui_body"] = body_of(habitat, st.session_state.get("ui_body"))
    st.session_state["ui_place"] = habitat


def show_sidebar() -> None:
    """Call once, in `app.py` (as `afficher_cadre`)."""
    scenario = get_scenario()
    # The home page buttons write into these keys: set them only once.
    st.session_state.setdefault("ui_habitat", scenario["habitat"])
    st.session_state.setdefault("ui_pillar", scenario["pilier"])
    if st.session_state.get("ui_profile") not in PROFILES_OFFERED:
        profile = scenario["profil"]
        st.session_state["ui_profile"] = profile if profile in PROFILES_OFFERED else PROFILES_OFFERED[0]
    with st.sidebar:
        st.subheader("My scenario")
        habitat = st.selectbox("Habitat", HABITATS, format_func=label, key="ui_habitat", on_change=_follow_habitat)
        pillar = st.selectbox("Need", PILIERS, format_func=label, key="ui_pillar")
        profile = st.selectbox("Profile", PROFILES_OFFERED, format_func=label, key="ui_profile")
        st.caption("A tool to help understand the research: this site is not a safety certification.")
    set_scenario(habitat, pillar, profile)
    if donnees_exemple():
        st.warning("Fictional sample data: the real NASA data is not loaded yet.")
