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


def places_page(objects: list[str], chosen: str | None, backdrop: str | None = None, zoom_from: int = -1) -> str:
    """HTML of the places scene, with the `chosen` object highlighted.

    `backdrop` draws a big planet behind the objects (the zoomed-in body). `zoom_from` is the column
    (0, 1 or 2) the body had among Earth, Moon and Mars: the scene then plays the zoom from there.
    """
    settings = {
        "objects": objects,
        "chosen": objects.index(chosen) if chosen in objects else -1,
        "backdrop": backdrop,
        "zoomFrom": zoom_from,
    }
    return _fill("places.html", settings)


def flame_scene(gravity: float, oxygen: float, height: int = 420) -> None:
    """Show the 3D flame. `gravity` goes from 0 (microgravity) to 1 (Earth), `oxygen` is in %."""
    st.iframe(flame_page(gravity, oxygen), height=height)


def places_scene(
    objects: list[str], chosen: str | None, backdrop: str | None = None, zoom_from: int = -1, height: int = 230
) -> None:
    """Show 3D objects side by side, one column each, the `chosen` one highlighted (see `places_page`)."""
    st.iframe(places_page(objects, chosen, backdrop, zoom_from), height=height)
