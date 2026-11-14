"""Point d'entrée du site : `uv run streamlit run app.py`. Propriétaire : rôle A (Intégration).

Ce fichier ne contient que la liste des pages. Le contenu de chaque page est dans `pages/`.
Le site n'affiche qu'une page, le tableau de bord (accord de Clément, rôle A).
"""

import streamlit as st

from flame.ui import afficher_cadre

st.set_page_config(page_title="Flame in Freefall", page_icon=":material/local_fire_department:", layout="wide")

# Une seule page visible : le tableau de bord (accueil). Les autres pages restent dans la liste,
# sans menu, pour que leurs tests et leurs liens continuent de marcher.
page = st.navigation(
    [
        st.Page("pages/accueil.py", title="Dashboard", icon=":material/space_dashboard:", default=True),
        st.Page("pages/recherche.py", title="Search", icon=":material/search:"),
        st.Page("pages/comparateur.py", title="Compare", icon=":material/compare_arrows:"),
        st.Page("pages/assistant.py", title="Assistant", icon=":material/chat:"),
    ],
    position="hidden",
)
afficher_cadre()
page.run()
