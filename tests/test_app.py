"""Vérifie que chaque page du site s'ouvre sans erreur. Propriétaire : rôle A."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).parents[1] / "app.py")
PAGES = [
    "pages/accueil.py",
    "pages/recherche.py",
    "pages/donnees.py",
    "pages/comparateur.py",
    "pages/equipements.py",
    "pages/assistant.py",
]


def test_accueil_s_ouvre():
    site = AppTest.from_file(APP, default_timeout=30).run()
    assert not site.exception


@pytest.mark.parametrize("page", PAGES)
def test_page_s_ouvre(page):
    site = AppTest.from_file(APP, default_timeout=30).run()
    site.switch_page(page).run()
    assert not site.exception
