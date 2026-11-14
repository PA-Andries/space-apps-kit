"""Page d'accueil « Mon scénario ». Propriétaire : rôle F (Interface et 3D)."""

import streamlit as st

from flame.commun import ATMOSPHERES, get_scenario
from flame.ui import scene_3d

scenario = get_scenario()
oxygene_habitat, pression_habitat = ATMOSPHERES[scenario["habitat"]]

st.title("Flame in Freefall")
st.write("Ce que les expériences NASA de combustion en microgravité nous apprennent pour la sécurité incendie.")

gauche, droite = st.columns([2, 1])
with droite:
    st.metric("Habitat", scenario["habitat"])
    st.metric("Atmosphère type", f"{oxygene_habitat} % O₂ · {pression_habitat} kPa")
    gravite = st.slider("Gravité (0 = microgravité, 1 = Terre)", 0.0, 1.0, 0.0, key="accueil_gravite")
with gauche:
    scene_3d(gravite=gravite, oxygene=oxygene_habitat)
    st.caption("Illustration : la forme et la couleur de la flamme ne sont pas calculées.")
