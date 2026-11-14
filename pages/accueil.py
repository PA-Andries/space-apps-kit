"""Page d'accueil « My scenario ». Propriétaire : rôle F (Interface et 3D)."""

import streamlit as st

from flame.commun import get_scenario
from flame.ui import TERRE, choix_lieu, choix_pilier, conditions_lieu, libelle, scene_3d

st.title("Flame in Freefall")
st.write("What NASA microgravity combustion experiments teach us about fire safety in space.")

st.subheader("Where?")
lieu = choix_lieu()
st.subheader("What do you need?")
choix_pilier()

conditions = conditions_lieu(lieu)
gauche, droite = st.columns([2, 1])
with droite:
    st.metric("Typical atmosphere", f"{conditions['oxygene_pct']} % O₂ · {conditions['pression_kpa']} kPa")
    st.caption("Source: challenge statement." if conditions["source_enonce"] else "Team assumption, to be confirmed.")
    gravite = st.slider(
        "Gravity (0 = microgravity, 1 = Earth)", 0.0, 1.0, conditions["gravite"], key=f"accueil_gravite_{lieu}"
    )
    if lieu == TERRE:
        habitat = libelle(get_scenario()["habitat"])
        st.info(f"Earth is the reference. Search and Compare use your space habitat: {habitat}.")
with gauche:
    scene_3d(gravite=gravite, oxygene=conditions["oxygene_pct"])
    st.caption("Illustration: the flame's shape and colour are not computed.")
