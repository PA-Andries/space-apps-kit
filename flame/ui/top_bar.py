"""What shows at the top of every page: the site style, a short disclaimer, and the warnings.

There is no scenario bar any more (removed at role F's request): the home page sets the scenario,
by clicking a place and a pillar. This keeps the scenario in step with those choices.
"""

import streamlit as st

from flame.commun import PROFILS, donnees_exemple, get_scenario, set_scenario
from flame.ui.style import apply_style

# Profiles the site uses. "Étudiant" is removed at role F's request;
# it stays in the contract (PROFILS) until role A changes it.
PROFILES_OFFERED = [profile for profile in PROFILS if profile != "Étudiant"]


def show_top_bar() -> None:
    """Call once, in `app.py` (as `afficher_cadre`): style, disclaimer and scenario of every page."""
    scenario = get_scenario()
    # The home page buttons write into these keys: set them only once.
    st.session_state.setdefault("ui_habitat", scenario["habitat"])
    st.session_state.setdefault("ui_pillar", scenario["pilier"])
    if st.session_state.get("ui_profile") not in PROFILES_OFFERED:
        profile = scenario["profil"]
        st.session_state["ui_profile"] = profile if profile in PROFILES_OFFERED else PROFILES_OFFERED[0]
    apply_style()
    st.html('<p class="ff-disclaimer">A tool to help understand the research: not a safety certification.</p>')
    set_scenario(st.session_state["ui_habitat"], st.session_state["ui_pillar"], st.session_state["ui_profile"])
    if donnees_exemple():
        st.warning("Fictional sample data: the real NASA data is not loaded yet.")
