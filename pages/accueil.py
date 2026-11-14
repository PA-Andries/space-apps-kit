"""Page d'accueil « My scenario ». Propriétaire : rôle F (Interface et 3D)."""

import streamlit as st

from flame.commun import get_scenario
from flame.ui import TERRE, choix_lieu, choix_pilier, conditions_lieu, libelle, scene_3d

st.title("Flame in Freefall")
st.write("What NASA microgravity combustion experiments teach us about fire safety in space.")

st.subheader("1. Where are you?")
lieu = choix_lieu()

pilier = None
if lieu:
    st.subheader("2. What do you need?")
    pilier = choix_pilier()

if lieu and pilier:
    st.subheader(f"3. {libelle(pilier)} fire · {libelle(lieu)}")
    conditions = conditions_lieu(lieu)
    gauche, droite = st.columns([2, 1])
    with droite:
        st.metric("Typical atmosphere", f"{conditions['oxygene_pct']} % O₂ · {conditions['pression_kpa']} kPa")
        source = "Source: challenge statement." if conditions["source_enonce"] else "Team assumption, to be confirmed."
        st.caption(source)
        gravite = st.slider(
            "Gravity (0 = microgravity, 1 = Earth)", 0.0, 1.0, conditions["gravite"], key=f"accueil_gravite_{lieu}"
        )
        if lieu == TERRE:
            habitat = libelle(get_scenario()["habitat"])
            st.info(f"Earth is the reference. Search and Compare use your space habitat: {habitat}.")
        st.page_link("pages/recherche.py", label="Find the most useful experiments", icon=":material/search:")
    with gauche:
        scene_3d(gravite=gravite, oxygene=conditions["oxygene_pct"])
        st.caption("Illustration: the flame's shape and colour are not computed.")
