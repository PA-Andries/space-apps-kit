"""Ce qui s'affiche sur toutes les pages : le scénario dans la barre latérale et les avertissements."""

import streamlit as st

from flame.commun import HABITATS, PILIERS, PROFILS, donnees_exemple, get_scenario, set_scenario
from flame.ui.libelles import libelle

# Profils proposés dans la barre latérale. « Étudiant » est retiré à la demande du rôle F ;
# il reste dans le contrat (PROFILS) tant que le rôle A ne l'a pas changé.
PROFILS_PROPOSES = [profil for profil in PROFILS if profil != "Étudiant"]


def _suivre_habitat() -> None:
    """Un habitat choisi dans la barre latérale devient aussi le lieu de l'accueil."""
    st.session_state["ui_lieu"] = st.session_state["ui_habitat"]


def afficher_cadre() -> None:
    """À appeler une seule fois, dans `app.py`."""
    scenario = get_scenario()
    # Les boutons de l'accueil écrivent dans ces clés : on ne les initialise qu'une fois.
    for cle in ["habitat", "pilier"]:
        st.session_state.setdefault(f"ui_{cle}", scenario[cle])
    if st.session_state.get("ui_profil") not in PROFILS_PROPOSES:
        profil = scenario["profil"]
        st.session_state["ui_profil"] = profil if profil in PROFILS_PROPOSES else PROFILS_PROPOSES[0]
    with st.sidebar:
        st.subheader("My scenario")
        habitat = st.selectbox("Habitat", HABITATS, format_func=libelle, key="ui_habitat", on_change=_suivre_habitat)
        pilier = st.selectbox("Need", PILIERS, format_func=libelle, key="ui_pilier")
        profil = st.selectbox("Profile", PROFILS_PROPOSES, format_func=libelle, key="ui_profil")
        st.caption("A tool to help understand the research: this site is not a safety certification.")
    set_scenario(habitat, pilier, profil)
    if donnees_exemple():
        st.warning("Fictional sample data: the real NASA data is not loaded yet.")
