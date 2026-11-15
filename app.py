"""Point d'entrée du site : `uv run streamlit run app.py`. Propriétaire : rôle A (Intégration).

Ce fichier ne contient que la liste des pages. Le contenu de chaque page est dans `pages/`.
"""

import streamlit as st

from flame.assistant import repondre
from flame.ui import afficher_cadre

st.set_page_config(page_title="Flame in Freefall", page_icon=":material/local_fire_department:", layout="wide")

page = st.navigation(
    [
        st.Page("pages/accueil.py", title="Home", icon=":material/home:", default=True),
        # L'ancienne page de données est retirée : son tableau et son export sont un onglet d'Investigations.
        st.Page("pages/recherche.py", title="Investigations", icon=":material/search:"),
        st.Page("pages/comparateur.py", title="Compare", icon=":material/compare_arrows:"),
    ],
    position="top",  # the menu is a bar at the top of the page, not a sidebar
)
afficher_cadre(repondre)  # Flamy, the assistant, sits in the bottom-right corner of every page
page.run()
