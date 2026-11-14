"""The three.js scenes, shown in a Streamlit page.

Python sends settings to the scene; the scene sends nothing back to Python.
"""

import json
from pathlib import Path

import streamlit as st

THREE_DIR = Path(__file__).parent / "three"


def _fill(file_name: str, settings: dict) -> str:
    """HTML of a scene from `three/`, with its settings written in place of `__SETTINGS__`."""
    page = (THREE_DIR / file_name).read_text(encoding="utf-8")
    return page.replace("__SETTINGS__", json.dumps(settings))


def flame_settings(gravity: float, oxygen: float) -> dict[str, float]:
    """Settings sent to the flame scene, clamped: gravity between 0 and 1, oxygen between 0 and 100 %."""
    return {"gravity": min(max(float(gravity), 0.0), 1.0), "oxygen": min(max(float(oxygen), 0.0), 100.0)}


def flame_page(gravity: float, oxygen: float) -> str:
    """HTML of the flame scene, with its settings already written in."""
    return _fill("flame.html", flame_settings(gravity, oxygen))


def places_page(objects: list[str], zones: list[dict], chosen: str | None, zoom_from: int = -1) -> str:
    """HTML of the places scene: each object drawn in its zone, the `chosen` one highlighted.

    A zone is {x, y, w, h} in fractions of the frame. `zoom_from` is the column (0, 1 or 2) the planet
    had among Earth, Moon and Mars: the scene then plays the zoom from there.
    """
    settings = {
        "objects": objects,
        "zones": zones,
        "chosen": objects.index(chosen) if chosen in objects else -1,
        "zoomFrom": zoom_from,
    }
    return _fill("places.html", settings)


def flame_scene(gravity: float, oxygen: float, height: int = 420) -> None:
    """Show the 3D flame. `gravity` goes from 0 (microgravity) to 1 (Earth), `oxygen` is in %."""
    st.iframe(flame_page(gravity, oxygen), height=height)


def places_scene(
    objects: list[str], zones: list[dict], chosen: str | None, zoom_from: int = -1, height: int = 300
) -> None:
    """Show 3D objects, each in its zone, the `chosen` one highlighted (see `places_page`)."""
    st.iframe(places_page(objects, zones, chosen, zoom_from), height=height)
