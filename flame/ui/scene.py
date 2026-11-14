"""La scène three.js, affichée dans une page Streamlit.

Python envoie des réglages à la scène ; la scène ne renvoie rien à Python.
"""

import json
from pathlib import Path

import streamlit as st

DOSSIER_THREE = Path(__file__).parent / "three"


def scene_3d(gravite: float, oxygene: float, hauteur: int = 420) -> None:
    """Affiche la flamme en 3D. `gravite` va de 0 (microgravité) à 1 (Terre), `oxygene` est en %."""
    reglages = json.dumps({"gravite": gravite, "oxygene": oxygene})
    page = (DOSSIER_THREE / "flamme.html").read_text(encoding="utf-8")
    st.iframe(page.replace("__REGLAGES__", reglages), height=hauteur)
