"""Page Recherche. Propriétaire : rôle C (Recherche)."""

import streamlit as st

from flame.commun import charger_fiches, get_scenario
from flame.recherche import rechercher
from flame.ui import carte_fiche

st.title("Recherche")

question = st.text_input("Que cherchez-vous ?", placeholder="tissu, extinction, fumée…", key="recherche_question")
resultats = rechercher(question, charger_fiches(), get_scenario())

st.caption(f"{len(resultats)} investigation(s)")
for _, fiche in resultats.iterrows():
    carte_fiche(fiche)
