"""La scène three.js, affichée dans une page Streamlit.

Python envoie des réglages à la scène ; la scène ne renvoie rien à Python.
"""

import json
from pathlib import Path

import streamlit as st

DOSSIER_THREE = Path(__file__).parent / "three"


def reglages_scene(gravite: float, oxygene: float) -> dict[str, float]:
    """Les réglages envoyés à la scène, bornés : gravité entre 0 et 1, oxygène entre 0 et 100 %."""
    return {"gravite": min(max(float(gravite), 0.0), 1.0), "oxygene": min(max(float(oxygene), 0.0), 100.0)}


def page_scene(gravite: float, oxygene: float) -> str:
    """Le code HTML de la scène, avec ses réglages déjà écrits dedans."""
    page = (DOSSIER_THREE / "flamme.html").read_text(encoding="utf-8")
    return page.replace("__REGLAGES__", json.dumps(reglages_scene(gravite, oxygene)))


def scene_3d(gravite: float, oxygene: float, hauteur: int = 420) -> None:
    """Affiche la flamme en 3D. `gravite` va de 0 (microgravité) à 1 (Terre), `oxygene` est en %."""
    st.iframe(page_scene(gravite, oxygene), height=hauteur)
