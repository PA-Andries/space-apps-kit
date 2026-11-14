"""Page Comparateur. Propriétaire : rôle D (Comparateur)."""

import streamlit as st

from flame.commun import charger_fiches
from flame.comparateur import comparer

st.title("Comparateur")

fiches = charger_fiches()
ids = st.multiselect("Investigations à comparer", list(fiches["id"]), max_selections=3, key="comparateur_ids")

if len(ids) < 2:
    st.info("Choisissez deux ou trois investigations.")
else:
    st.dataframe(comparer(fiches, ids).astype(str), width="stretch")
