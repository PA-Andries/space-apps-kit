"""What shows on every page: the site style, the warnings, and the user's
environment recalled under the top menu. The environment itself is set on page 1 (Home).

The menu itself is a bar fixed at the top of the window (`st.navigation(position="top")` in `app.py`);
there is no sidebar.
"""

from collections.abc import Callable
from html import escape

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

from flame.commun import PROFILS, donnees_exemple, get_scenario, set_scenario
from flame.ui.chatbot import flamy_corner
from flame.ui.environment import environment_summary
from flame.ui.labels import label
from flame.ui.style import apply_style

# Profiles the site uses. "Étudiant" is removed at role F's request;
# it stays in the contract (PROFILS) until role A changes it.
PROFILES_OFFERED = [profile for profile in PROFILS if profile != "Étudiant"]


def show_top_bar(answer: Callable | None = None) -> None:
    """Call once, in `app.py` (as `afficher_cadre`): style and scenario of every page.

    `answer`: the assistant's `repondre`, handed in by `app.py`, for Flamy in the bottom-right corner.
    """
    scenario = get_scenario()
    # The home page buttons write into these keys: set them only once.
    st.session_state.setdefault("ui_habitat", scenario["habitat"])
    if st.session_state.get("ui_profile") not in PROFILES_OFFERED:
        profile = scenario["profil"]
        st.session_state["ui_profile"] = profile if profile in PROFILES_OFFERED else PROFILES_OFFERED[0]
    apply_style()
    # Under the menu: the user's environment.
    with st.container(key="ui_status_line", horizontal=True, vertical_alignment="center"):
        st.session_state["ui_sidebar_environment"] = (st.empty(), _this_run())
    # Pillars are dropped (PA, Sat 17:00): the obsolete `pilier` key is passed on as it is, never chosen here.
    set_scenario(st.session_state["ui_habitat"], scenario["pilier"], st.session_state["ui_profile"])
    if donnees_exemple():
        st.warning("Fictional sample data: the real NASA data is not loaded yet.")
    # Page 1 writes in the same slot again once its form is read.
    show_environment_in_sidebar()
    # Flamy in the bottom-right corner of every page; a click opens the chat window.
    flamy_corner(answer)


def show_environment_in_sidebar(reference: str | None = None, values: dict | None = None) -> None:
    """Write the current environment in the slot under the top menu, made by `show_top_bar`.

    `reference`: a reference place explored on page 1 (Earth, the spacesuit), with the `values` on screen.
    The line then shows that place, so that it agrees with the selected button and the sliders, and names
    the habitat the other pages keep. (The name stays from the time the environment was in the sidebar.)
    """
    slot, made_in = st.session_state.get("ui_sidebar_environment", (None, None))
    # Only a slot made in this very run: an older one points to a page that is no longer on screen.
    if slot is not None and made_in == _this_run():
        habitat = get_scenario()["habitat"]
        if reference is None:
            title, summary = "My environment", environment_summary(habitat)
        else:
            title = "Reference shown"
            summary = f"{environment_summary(reference, values)} · the other pages keep {label(habitat)}"
        with slot.container():
            st.html(f'<p class="ff-env-line"><span>{title}</span>{escape(summary)}</p>')


def _this_run() -> int | None:
    """A number that changes with every run of the page script (Streamlit renews its cursors each run)."""
    context = get_script_run_ctx()
    return id(context.cursors) if context is not None else None
