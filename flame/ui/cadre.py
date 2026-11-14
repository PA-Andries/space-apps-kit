"""Ce qui s'affiche sur toutes les pages : le scénario dans la barre latérale et les avertissements."""

import streamlit as st

from flame.commun import HABITATS, PILIERS, PROFILS, donnees_exemple, get_scenario, set_scenario


def afficher_cadre() -> None:
    """À appeler une seule fois, dans `app.py`."""
    scenario = get_scenario()
    with st.sidebar:
        st.subheader("Mon scénario")
        habitat = st.selectbox("Habitat", HABITATS, index=HABITATS.index(scenario["habitat"]), key="ui_habitat")
        pilier = st.selectbox("Besoin", PILIERS, index=PILIERS.index(scenario["pilier"]), key="ui_pilier")
        profil = st.selectbox("Profil", PROFILS, index=PROFILS.index(scenario["profil"]), key="ui_profil")
        st.caption("Outil d'aide à la compréhension : ce site n'est pas une certification de sécurité.")
    set_scenario(habitat, pilier, profil)
    if donnees_exemple():
        st.warning("Données d'exemple fictives : les vraies données NASA ne sont pas encore chargées.")
