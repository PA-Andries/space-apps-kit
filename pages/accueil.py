"""Home page "My scenario". Owner: role F (Interface and 3D).

The file name stays `accueil.py` because `app.py` (role A) points to it.
"""

import streamlit as st

from flame.commun import get_scenario
from flame.ui import (
    EARTH,
    flame_scene,
    hero,
    label,
    pillar_picker,
    place_conditions,
    place_picker,
    section,
    stat_tiles,
)

hero(
    "NASA Space Apps Challenge 2026",
    "Fire behaves differently in space.",
    "See what NASA microgravity combustion experiments teach us about keeping crews safe in orbit, "
    "on the Moon and on Mars.",
)

section("Where are you going?", "Tap a planet, then the place you will live in.")
body, place = place_picker()

pillar = None
if place:
    section("What do you need?", "The three pillars of NASA fire safety.")
    pillar = pillar_picker()

if place and pillar:
    conditions = place_conditions(place, body)
    known = conditions["oxygen_pct"] is not None
    section(f"{label(pillar)} fire · {label(place)}", "The conditions your crew would live in.")
    stat_tiles(
        [
            (f"{conditions['oxygen_pct']} %" if known else None, "Oxygen"),
            (f"{conditions['pressure_kpa']} kPa" if known else None, "Pressure"),
            (f"{conditions['gravity']:g} g", "Gravity"),
        ],
        "Oxygen and pressure: challenge statement."
        if known
        else "Oxygen and pressure are not given in the challenge statement, so the site shows no figure.",
    )
    if place == EARTH:
        habitat = label(get_scenario()["habitat"])
        st.info(f"Earth is the reference. Search and Compare use your space habitat: {habitat}.")
    # Unknown oxygen: the flame is drawn at Earth's 21 %, and the caption says so.
    flame_scene(gravity=conditions["gravity"], oxygen=conditions["oxygen_pct"] if known else 21)
    caption = "Illustration of a flame at this gravity: its shape and colour are not computed."
    st.caption(caption if known else f"{caption} Oxygen unknown here: drawn at Earth's 21 %.")
    st.page_link("pages/recherche.py", label="Find the most useful experiments  ›")
