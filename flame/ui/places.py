"""Choosing the place on the home page, in two levels: first the celestial body, then the place.

Earth: the planet (reference), the station, the spacecraft. Moon: the base, the pressurized rover. Mars: the base.
Only what the team brief attributes to the challenge statement is used: the rover is listed with the lunar base.
Earth is not a habitat of the contract: choosing it does not change the habitat used by the other pages.
Place values are the contract values (French); `label()` shows them in English.
"""

import streamlit as st

from flame.commun import ATMOSPHERES, get_scenario

EARTH = "Terre"
BODIES = ["Terre", "Lune", "Mars"]
PLACES_BY_BODY = {
    "Terre": [EARTH, "Station", "Vaisseau"],
    "Lune": ["Base lunaire", "Rover pressurisé"],
    "Mars": ["Base martienne"],
}

# Atmospheres attributed to the challenge statement by BRIEF_EQUIPE_IA.md: Earth 21 % / 14.7 psi (about
# 101 kPa); "lunar base and pressurized rovers" 30 % / 10.2 psi (about 70 kPa, as in the contract ATMOSPHERES).
# For any other place the statement gives nothing: the site shows no figure rather than a guess.
STATEMENT_ATMOSPHERES = {
    EARTH: (21, 101),
    "Base lunaire": ATMOSPHERES["Base lunaire"],
    "Rover pressurisé": ATMOSPHERES["Rover pressurisé"],
}

# Gravity as a fraction of Earth's, for the 3D illustration only.
# Moon 0.17 and Mars 0.38: usual physical values. In orbit (station, spacecraft): microgravity.
BODY_GRAVITY = {"Terre": 1.0, "Lune": 0.17, "Mars": 0.38}
ORBIT_PLACES = {"Station", "Vaisseau"}


def current_body() -> str | None:
    """The celestial body chosen on the home page, or None until the user picks one."""
    return st.session_state.get("ui_body")


def current_place() -> str | None:
    """The place chosen on the home page, or None until the user picks one."""
    return st.session_state.get("ui_place")


def current_pillar() -> str | None:
    """The pillar chosen on the home page, or None until the user presses one of its buttons."""
    return get_scenario()["pilier"] if st.session_state.get("ui_pillar_chosen") else None


def body_of(place: str) -> str | None:
    """The celestial body of a place, or None if the home page does not offer it (for example a rover on Mars)."""
    return next((body for body in BODIES if place in PLACES_BY_BODY[body]), None)


def place_conditions(place: str, body: str) -> dict:
    """Oxygen (%) and pressure (kPa) of a place, or None when the statement gives none; gravity from 0 to 1."""
    oxygen_pct, pressure_kpa = STATEMENT_ATMOSPHERES.get(place, (None, None))
    return {
        "oxygen_pct": oxygen_pct,
        "pressure_kpa": pressure_kpa,
        "gravity": 0.0 if place in ORBIT_PLACES else BODY_GRAVITY[body],
    }


def choose_body(body: str) -> None:
    """Remember the celestial body; the place has to be chosen again, and the scene zooms in once."""
    if body != st.session_state.get("ui_body"):
        st.session_state["ui_body"] = body
        st.session_state.pop("ui_place", None)
        st.session_state["ui_zoom_pending"] = True


def go_back() -> None:
    """Back to the three celestial bodies."""
    for key in ["ui_body", "ui_place", "ui_zoom_pending"]:
        st.session_state.pop(key, None)


def take_zoom() -> bool:
    """True only on the first display after a body was chosen, so the zoom plays once."""
    return st.session_state.pop("ui_zoom_pending", False)


def choose_place(place: str) -> None:
    """Remember the place; a habitat also becomes the scenario habitat (top bar)."""
    st.session_state["ui_place"] = place
    if place != EARTH:
        st.session_state["ui_habitat"] = place


def choose_pillar(pillar: str) -> None:
    """Remember the scenario pillar (top bar)."""
    st.session_state["ui_pillar"] = pillar
    st.session_state["ui_pillar_chosen"] = True
