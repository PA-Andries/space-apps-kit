"""What shows on every page: the site style, a short disclaimer, the warnings, and the user's
environment recalled in the sidebar. The environment itself is set on page 1 (My environment).
"""

import streamlit as st

from flame.commun import PROFILS, donnees_exemple, get_scenario, set_scenario
from flame.ui.environment import environment_summary
from flame.ui.style import apply_style

# Profiles the site uses. "Étudiant" is removed at role F's request;
# it stays in the contract (PROFILS) until role A changes it.
PROFILES_OFFERED = [profile for profile in PROFILS if profile != "Étudiant"]


def show_top_bar() -> None:
    """Call once, in `app.py` (as `afficher_cadre`): style, disclaimer and scenario of every page."""
    scenario = get_scenario()
    # The home page buttons write into these keys: set them only once.
    st.session_state.setdefault("ui_habitat", scenario["habitat"])
    if st.session_state.get("ui_profile") not in PROFILES_OFFERED:
        profile = scenario["profil"]
        st.session_state["ui_profile"] = profile if profile in PROFILES_OFFERED else PROFILES_OFFERED[0]
    apply_style()
    # Back to the home page, on the far left of every page (page 1 hides it: it is the home page).
    # The home page then folds the sidebar away (see `fold_sidebar_after_home`).
    with st.container(key="ui_home_link"):
        if st.button("Home", icon=":material/arrow_back:", key="ui_home_button"):
            st.session_state["ui_home_clicked"] = st.session_state.get("ui_home_clicks", 0) + 1
            st.session_state["ui_home_clicks"] = st.session_state["ui_home_clicked"]
            st.switch_page("pages/accueil.py")
    st.html('<p class="ff-disclaimer">A tool to help understand the research: not a safety certification.</p>')
    # Pillars are dropped (PA, Sat 17:00): the obsolete `pilier` key is passed on as it is, never chosen here.
    set_scenario(st.session_state["ui_habitat"], scenario["pilier"], st.session_state["ui_profile"])
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
        slot.markdown(f"**{environment_summary(get_scenario()['habitat'])}**")


# A tiny invisible page that clicks the sidebar's own "collapse" button in the page around it.
_FOLD_SCRIPT = """<script>
// Click number __CLICK__ on Home (the number makes this page new each time, so that it runs again).
const fold = (tries) => {
  const page = window.parent.document;
  const sidebar = page.querySelector('[data-testid="stSidebar"]');
  const button = page.querySelector('[data-testid="stSidebarCollapseButton"] button')
    || page.querySelector('[data-testid="stSidebarHeader"] button');
  if (sidebar && sidebar.getAttribute("aria-expanded") === "false") return;
  if (button) { button.click(); return; }
  if (tries > 0) setTimeout(() => fold(tries - 1), 150);
};
fold(20);
</script>"""


def fold_sidebar_after_home() -> None:
    """On the home page: fold the sidebar away when the visitor has just pressed Home.

    The visitor can open it again with its usual arrow.
    """
    click = st.session_state.pop("ui_home_clicked", None)
    if click is None:
        return
    with st.container(key="ui_fold_sidebar"):
        st.iframe(_FOLD_SCRIPT.replace("__CLICK__", str(click)), height=1)
