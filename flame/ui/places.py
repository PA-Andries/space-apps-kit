"""Choosing the place on the home page, in two levels: first the celestial body, then the place.

Earth: the planet (reference), the station, the spacecraft. Moon: the base, the pressurized rover. Mars: the base.
Only what the team brief attributes to the challenge statement is used: the rover is listed with the lunar base.
Earth is not a habitat of the contract: choosing it does not change the habitat used by the other pages.
Place values are the contract values (French); `label()` shows them in English.
"""

import streamlit as st

from flame.commun import ATMOSPHERES

EARTH = "Terre"
# The spacesuit: 100 % oxygen at 4.3 psi in the statement. It is a reference, not a crew environment, and
# it is the lower bound that explains the lunar atmosphere (between the suit and Earth's air).
SPACESUIT = "Scaphandre"
# The two reference places: they are shown and can be explored, but they are not crew environments of the
# contract, so choosing one does not replace the habitat the other pages read.
REFERENCE_PLACES = (EARTH, SPACESUIT)
BODIES = ["Terre", "Lune", "Mars"]
PLACES_BY_BODY = {
    "Terre": [EARTH, "Station", "Vaisseau"],
    "Lune": ["Base lunaire", "Rover pressurisé", SPACESUIT],
    "Mars": ["Base martienne"],
}

# Page 1 offers one button per atmosphere, in one row, from the ground outwards: Earth (the reference),
# then the two crew environments. Places that share their conditions share a button (Hugo, Sun 15 Nov):
# the spacecraft has the station's conditions and the pressurized rover has the Moon base's
# (`conditions_habitat`, role A), so a second button changed nothing on the page.
# The spacesuit has no button any more (Hugo, Sun 15 Nov): it is not a place a crew lives in. It stays on
# the chart as a star. The Mars base has no button either: see `MARS_NOTE`.
PLACE_ROWS = [
    [EARTH, "Station", "Base lunaire"],
]
# A place without a button of its own, and the button that stands for it.
SAME_CONDITIONS_AS = {"Vaisseau": "Station", "Rover pressurisé": "Base lunaire"}
# Why Mars is not offered yet. Both facts are checked: the statement lists Martian bases among the crew
# environments but gives no oxygen or pressure for them, and it says PSI holds no partial-gravity data.
# "Future feature" is the team's intention, not a NASA announcement: the sentence does not promise data.
MARS_TITLE = "Mars base"
MARS_TAG = "Future feature"
MARS_NOTE = (
    "Not available yet. NASA's challenge statement gives no atmosphere for a Mars base, and no PSI "
    "experiment was run in Martian conditions or in partial gravity. This environment will be added "
    "once such data exists."
)
# The small logo of each button: a Material icon drawn by Streamlit (no NASA logo or insignia).
PLACE_ICONS = {
    "Station": ":material/satellite_alt:",
    "Vaisseau": ":material/rocket_launch:",
    "Base lunaire": ":material/nightlight:",
    "Rover pressurisé": ":material/airport_shuttle:",
    "Base martienne": ":material/landscape:",
    EARTH: ":material/public:",
    SPACESUIT: ":material/accessibility_new:",
}
# The text of each button; a place that is not listed here uses `label()`.
PLACE_NAMES = {
    "Station": "Station & spacecraft",
    "Base lunaire": "Moon base & rover",
    EARTH: "Earth",
    SPACESUIT: "Spacesuit (EVA)",  # no button any more; kept for the place's name elsewhere
}

# Atmospheres attributed to the challenge statement by BRIEF_EQUIPE_IA.md: Earth 21 % / 14.7 psi (about
# 101 kPa); "lunar base and pressurized rovers" 30 % / 10.2 psi (about 70 kPa, as in the contract ATMOSPHERES).
# For any other place the statement gives nothing: the site shows no figure rather than a guess.
STATEMENT_ATMOSPHERES = {
    EARTH: (21, 101),
    "Base lunaire": ATMOSPHERES["Base lunaire"],
    "Rover pressurisé": ATMOSPHERES["Rover pressurisé"],
    # The statement gives the suit exactly: 100 % oxygen at 4.3 psi, which is 29.6 kPa.
    SPACESUIT: (100, 29.6),
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
    """Remember the celestial body; the place has to be chosen again (the scene plays its zoom by itself)."""
    if body != st.session_state.get("ui_body"):
        st.session_state["ui_body"] = body
        st.session_state.pop("ui_place", None)


def go_back() -> None:
    """Back to the three celestial bodies."""
    for key in ["ui_body", "ui_place"]:
        st.session_state.pop(key, None)


def choose_place(place: str) -> None:
    """Remember the place; a habitat also becomes the scenario habitat (top bar).

    A click, even on the place already shown, gives the sliders of page 1 the place's own values again.
    """
    st.session_state["ui_place"] = place
    st.session_state.pop("ui_form_place", None)
    if place not in REFERENCE_PLACES:
        st.session_state["ui_habitat"] = place
