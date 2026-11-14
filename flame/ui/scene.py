"""Les scènes three.js, affichées dans une page Streamlit.

Python envoie des réglages à la scène ; la scène ne renvoie rien à Python.
"""

import json
from pathlib import Path

import streamlit as st

DOSSIER_THREE = Path(__file__).parent / "three"


def _remplir(nom_fichier: str, reglages: dict) -> str:
    """Le code HTML d'une scène de `three/`, avec ses réglages écrits à la place de `__REGLAGES__`."""
    page = (DOSSIER_THREE / nom_fichier).read_text(encoding="utf-8")
    return page.replace("__REGLAGES__", json.dumps(reglages))


def reglages_scene(gravite: float, oxygene: float) -> dict[str, float]:
    """Les réglages envoyés à la scène, bornés : gravité entre 0 et 1, oxygène entre 0 et 100 %."""
    return {"gravite": min(max(float(gravite), 0.0), 1.0), "oxygene": min(max(float(oxygene), 0.0), 100.0)}


def page_scene(gravite: float, oxygene: float) -> str:
    """Le code HTML de la scène de la flamme, avec ses réglages déjà écrits dedans."""
    return _remplir("flamme.html", reglages_scene(gravite, oxygene))


def page_lieux(lieux: list[str], choisi: str) -> str:
    """Le code HTML de la scène des lieux, le lieu `choisi` mis en avant."""
    return _remplir("lieux.html", {"lieux": lieux, "choisi": lieux.index(choisi) if choisi in lieux else -1})


def scene_3d(gravite: float, oxygene: float, hauteur: int = 420) -> None:
    """Affiche la flamme en 3D. `gravite` va de 0 (microgravité) à 1 (Terre), `oxygene` est en %."""
    st.iframe(page_scene(gravite, oxygene), height=hauteur)


def scene_lieux(lieux: list[str], choisi: str, hauteur: int = 170) -> None:
    """Affiche les lieux en 3D côte à côte, une colonne chacun, le lieu `choisi` mis en avant."""
    st.iframe(page_lieux(lieux, choisi), height=hauteur)
