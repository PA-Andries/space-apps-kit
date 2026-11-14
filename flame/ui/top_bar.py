"""What shows on every page: the site style, a short disclaimer, the warnings, and the user's
environment recalled in the sidebar. The environment itself is set on page 1 (My environment).
"""

import streamlit as st

from flame.commun import PROFILS, donnees_exemple, get_scenario, set_scenario
from flame.ui.environment import environment_summary, full_scenario
from flame.ui.style import apply_style

# Profiles the site uses. "Étudiant" is removed at role F's request;
# it stays in the contract (PROFILS) until role A changes it.
PROFILES_OFFERED = [profile for profile in PROFILS if profile != "Étudiant"]


def show_top_bar() -> None:
    """Call once, in `app.py` (as `afficher_cadre`): style, disclaimer and scenario of every page."""
    scenario = get_scenario()
    # The home page buttons write into these keys: set them only once.
    st.session_state.setdefault("ui_habitat", scenario["habitat"])
    # The pillar switch of the dashboard can be emptied by a second click: keep the last pillar then.
    if st.session_state.get("ui_pillar") is None:
        st.session_state["ui_pillar"] = scenario["pilier"]
    if st.session_state.get("ui_profile") not in PROFILES_OFFERED:
        profile = scenario["profil"]
        st.session_state["ui_profile"] = profile if profile in PROFILES_OFFERED else PROFILES_OFFERED[0]
    apply_style()
    st.html('<p class="ff-disclaimer">A tool to help understand the research: not a safety certification.</p>')
    set_scenario(st.session_state["ui_habitat"], st.session_state["ui_pillar"], st.session_state["ui_profile"])
    if donnees_exemple():
        st.warning("Fictional sample data: the real NASA data is not loaded yet.")
    # The sidebar recalls the environment; page 1 writes in the same slot once its form is read.
    st.sidebar.caption("My environment")
    st.session_state["ui_sidebar_environment"] = st.sidebar.empty()
    show_environment_in_sidebar()


def show_environment_in_sidebar() -> None:
    """Write the current environment in the sidebar slot made by `show_top_bar`."""
    slot = st.session_state.get("ui_sidebar_environment")
    if slot is not None:
        slot.markdown(f"**{environment_summary(full_scenario())}**")
