"""Home page "My scenario". Owner: role F (Interface and 3D).

The file name stays `accueil.py` because `app.py` (role A) points to it.
"""

import streamlit as st

from flame.commun import get_scenario
from flame.ui import EARTH, flame_scene, label, pillar_picker, place_conditions, place_picker

st.title("Flame in Freefall")
st.write("What NASA microgravity combustion experiments teach us about fire safety in space.")

st.subheader("1. Where are you going?")
body, place = place_picker()

pillar = None
if place:
    st.subheader("2. What do you need?")
    pillar = pillar_picker()

if place and pillar:
    st.subheader(f"{label(pillar)} fire · {label(place)}")
    conditions = place_conditions(place, body)
    left, right = st.columns([2, 1])
    with right:
        known = conditions["oxygen_pct"] is not None
        if known:
            st.metric("Typical atmosphere", f"{conditions['oxygen_pct']} % O₂ · {conditions['pressure_kpa']} kPa")
            st.caption("Source: challenge statement.")
        else:
            st.metric("Typical atmosphere", "Unknown")
            st.caption("Not given in the challenge statement, so the site shows no figure.")
        gravity = st.slider(
            "Gravity (0 = microgravity, 1 = Earth)", 0.0, 1.0, conditions["gravity"], key=f"accueil_gravity_{place}"
        )
        if place == EARTH:
            habitat = label(get_scenario()["habitat"])
            st.info(f"Earth is the reference. Search and Compare use your space habitat: {habitat}.")
        st.page_link("pages/recherche.py", label="Find the most useful experiments", icon=":material/search:")
    with left:
        # Unknown oxygen: the flame is drawn at Earth's 21 %, and the caption says so.
        flame_scene(gravity=gravity, oxygen=conditions["oxygen_pct"] if known else 21)
        caption = "Illustration: the flame's shape and colour are not computed."
        st.caption(caption if known else f"{caption} Oxygen unknown here: drawn at Earth's 21 %.")
