"""Point d'entrée du site : `uv run streamlit run app.py`. Propriétaire : rôle A (Intégration).

Ce fichier ne contient que la liste des pages. Le contenu de chaque page est dans `pages/`.
"""

import streamlit as st

from flame.ui import afficher_cadre

st.set_page_config(page_title="Flame in Freefall", page_icon=":material/local_fire_department:", layout="wide")

page = st.navigation(
    [
        st.Page("pages/accueil.py", title="Mon scénario", icon=":material/home:", default=True),
        st.Page("pages/recherche.py", title="Recherche", icon=":material/search:"),
        st.Page("pages/comparateur.py", title="Comparateur", icon=":material/compare_arrows:"),
        st.Page("pages/assistant.py", title="Assistant", icon=":material/chat:"),
    ]
)
afficher_cadre()
page.run()
