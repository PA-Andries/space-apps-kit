"""What shows at the top of every page: the scenario bar, and the warnings."""

import streamlit as st

from flame.commun import HABITATS, PILIERS, PROFILS, donnees_exemple, get_scenario, set_scenario
from flame.ui.labels import label
from flame.ui.places import body_of
from flame.ui.style import apply_style

# Profiles offered in the bar. "Étudiant" is removed at role F's request;
# it stays in the contract (PROFILS) until role A changes it.
PROFILES_OFFERED = [profile for profile in PROFILS if profile != "Étudiant"]

TOP_BAR_STYLE = """<style>
.st-key-ui_top_bar {
  background: rgba(255, 255, 255, 0.8); backdrop-filter: saturate(180%) blur(20px);
  border: 1px solid rgba(0, 0, 0, 0.06); border-radius: 20px; padding: 0.8rem 1.2rem 0.5rem;
  box-shadow: 0 2px 12px rgba(29, 29, 31, 0.05);
}
.st-key-ui_top_bar label p { color: #6e6e73; font-size: 0.78rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.04em; }
.st-key-ui_top_bar [data-baseweb="select"] > div {
  border-radius: 12px; background: #f5f5f7; border-color: transparent;
}
.st-key-ui_top_bar [data-testid="stCaptionContainer"] { margin-top: -0.4rem; }
</style>"""


def _follow_habitat() -> None:
    """A habitat chosen in the bar also becomes the place of the home page."""
    habitat = st.session_state["ui_habitat"]
    st.session_state["ui_body"] = body_of(habitat)
    st.session_state["ui_place"] = habitat


def show_top_bar() -> None:
    """Call once, in `app.py` (as `afficher_cadre`): the scenario bar at the top of every page."""
    scenario = get_scenario()
    # The home page buttons write into these keys: set them only once.
    st.session_state.setdefault("ui_habitat", scenario["habitat"])
    st.session_state.setdefault("ui_pillar", scenario["pilier"])
    if st.session_state.get("ui_profile") not in PROFILES_OFFERED:
        profile = scenario["profil"]
        st.session_state["ui_profile"] = profile if profile in PROFILES_OFFERED else PROFILES_OFFERED[0]
    apply_style()
    st.html(TOP_BAR_STYLE)
    with st.container(key="ui_top_bar"):
        habitat_column, pillar_column, profile_column = st.columns(3)
        habitat = habitat_column.selectbox(
            "Habitat", HABITATS, format_func=label, key="ui_habitat", on_change=_follow_habitat
        )
        pillar = pillar_column.selectbox("Need", PILIERS, format_func=label, key="ui_pillar")
        profile = profile_column.selectbox("Profile", PROFILES_OFFERED, format_func=label, key="ui_profile")
        st.caption("A tool to help understand the research: this site is not a safety certification.")
    set_scenario(habitat, pillar, profile)
    if donnees_exemple():
        st.warning("Fictional sample data: the real NASA data is not loaded yet.")
