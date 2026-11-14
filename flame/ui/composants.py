"""Les blocs d'affichage partagés entre les pages."""

import pandas as pd
import streamlit as st


def carte_fiche(fiche: pd.Series) -> None:
    """Affiche une investigation en résumé : `carte_fiche(fiches.iloc[0])`."""
    with st.container(border=True):
        st.markdown(f"**{fiche['id']}** · {fiche['nom']}")
        st.caption(f"{fiche['pilier']} · {fiche['type_combustible']} · {fiche['materiel']}")
        st.write(fiche["resume"])
        st.link_button("Voir sur PSI", fiche["source_psi"])
