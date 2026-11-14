"""Les tests tournent toujours sur les données fictives de `data/exemples/`, même quand les vraies données existent."""

import pytest
import streamlit as st

from flame.commun import donnees


@pytest.fixture(autouse=True)
def donnees_fictives(monkeypatch):
    monkeypatch.setattr(donnees, "DOSSIER_DATA", donnees.DOSSIER_EXEMPLES)
    st.cache_data.clear()
    yield
    st.cache_data.clear()
