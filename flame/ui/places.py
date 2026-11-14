"""Choosing the place on the home page, in two levels: first the celestial body, then the place.

Earth: the planet (reference), the station, the spacecraft. Moon: the base, the rover. Mars: the base, the rover.
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
    "Mars": ["Base martienne", "Rover pressurisé"],
}

# Earth: figures from the challenge statement (21 % oxygen, 14.7 psi, about 101 kPa).
EARTH_ATMOSPHERE = (21, 101)
# Atmospheres given by the statement. The others are team assumptions (flame/commun/constantes.py).
STATEMENT_PLACES = {EARTH, "Base lunaire", "Rover pressurisé"}

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


def body_of(place: str, current: str | None = None) -> str:
    """The celestial body of a place. The rover exists on the Moon and on Mars: keep `current` if it fits."""
    candidates = [body for body in BODIES if place in PLACES_BY_BODY[body]]
    return current if current in candidates else candidates[0]


def place_conditions(place: str, body: str) -> dict:
    """Oxygen (%), pressure (kPa), gravity (0 to 1) of a place, and whether the atmosphere comes from the statement."""
    oxygen_pct, pressure_kpa = EARTH_ATMOSPHERE if place == EARTH else ATMOSPHERES[place]
    return {
        "oxygen_pct": oxygen_pct,
        "pressure_kpa": pressure_kpa,
        "gravity": 0.0 if place in ORBIT_PLACES else BODY_GRAVITY[body],
        "from_statement": place in STATEMENT_PLACES,
    }


def choose_body(body: str) -> None:
    """Remember the celestial body; the place has to be chosen again."""
    if body != st.session_state.get("ui_body"):
        st.session_state["ui_body"] = body
        st.session_state.pop("ui_place", None)


def choose_place(place: str) -> None:
    """Remember the place; a habitat also becomes the scenario habitat (sidebar)."""
    st.session_state["ui_place"] = place
    if place != EARTH:
        st.session_state["ui_habitat"] = place


def choose_pillar(pillar: str) -> None:
    """Remember the scenario pillar (sidebar)."""
    st.session_state["ui_pillar"] = pillar
    st.session_state["ui_pillar_chosen"] = True
