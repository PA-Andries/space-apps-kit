"""What shows at the top of every page: the scenario bar, and the warnings."""

import streamlit as st

from flame.commun import HABITATS, PILIERS, PROFILS, donnees_exemple, get_scenario, set_scenario
from flame.ui.labels import label
from flame.ui.places import body_of
from flame.ui.style import apply_style

# Profiles offered in the bar. "Étudiant" is removed at role F's request;
# it stays in the contract (PROFILS) until role A changes it.
PROFILES_OFFERED = [profile for profile in PROFILS if profile != "Étudiant"]

# A slim frosted bar that stays at the top while the page scrolls, like a product site's menu bar.
TOP_BAR_STYLE = """<style>
.st-key-ui_top_bar {
  position: sticky; top: 0.6rem; z-index: 999;
  background: rgba(255, 255, 255, 0.72); backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border: 1px solid rgba(0, 0, 0, 0.05); border-radius: 980px; padding: 0.35rem 0.6rem 0.35rem 1.4rem;
  box-shadow: 0 8px 30px rgba(29, 29, 31, 0.06);
}
.st-key-ui_top_bar [data-testid="stHorizontalBlock"] { align-items: center; gap: 0.6rem; }
.st-key-ui_top_bar [data-testid="stMarkdownContainer"] p { margin: 0; white-space: nowrap; }
.st-key-ui_top_bar .ff-brand { font-weight: 700; font-size: 1.05rem; letter-spacing: -0.02em; color: #1d1d1f; }
.st-key-ui_top_bar .ff-brand b { color: #e0662a; }
.st-key-ui_top_bar [data-baseweb="select"] > div {
  border-radius: 980px; background: rgba(0, 0, 0, 0.04); border-color: transparent; min-height: 2.2rem;
  font-size: 0.9rem; font-weight: 500;
}
.ff-disclaimer { text-align: center; color: #86868b; font-size: 0.78rem; margin: 0.2rem 0 0; }
@media (max-width: 640px) {
  .st-key-ui_top_bar { position: static; border-radius: 22px; padding: 0.6rem 0.9rem; }
}
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
        brand_column, habitat_column, pillar_column, profile_column = st.columns([1.3, 1, 1, 1])
        brand_column.html('<span class="ff-brand"><b>Flame</b> in Freefall</span>')
        # Labels stay for screen readers only: the menus themselves say what they hold.
        hidden = {"label_visibility": "collapsed"}
        habitat = habitat_column.selectbox(
            "Habitat", HABITATS, format_func=label, key="ui_habitat", on_change=_follow_habitat, **hidden
        )
        pillar = pillar_column.selectbox("Need", PILIERS, format_func=label, key="ui_pillar", **hidden)
        profile = profile_column.selectbox("Profile", PROFILES_OFFERED, format_func=label, key="ui_profile", **hidden)
    st.html('<p class="ff-disclaimer">A tool to help understand the research: not a safety certification.</p>')
    set_scenario(habitat, pillar, profile)
    if donnees_exemple():
        st.warning("Fictional sample data: the real NASA data is not loaded yet.")
