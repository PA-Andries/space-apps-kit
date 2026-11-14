"""The three.js scenes, shown in a Streamlit page.

Python sends settings to the scene; the scene sends nothing back to Python.
"""

import base64
import json
from functools import cache
from pathlib import Path

import streamlit as st

THREE_DIR = Path(__file__).parent / "three"
ASSETS_DIR = THREE_DIR / "assets"  # NASA planet maps, credited in assets/README.md

# The NASA files each object needs. Small maps for the first view, sharp ones for the zoomed planet.
OBJECT_ASSETS = {
    "earth_system": {"earth": "earth_1k.jpg"},
    "moon": {"moon": "moon_1k.jpg"},
    "mars": {"mars": "mars_1k.jpg"},
    "earth_whole": {"earth": "earth.jpg"},
    "moon_whole": {"moon": "moon.jpg"},
    "mars_whole": {"mars": "mars.jpg"},
    "rover_moon": {},
    "spacecraft": {},
}
MEDIA_TYPES = {".jpg": "image/jpeg"}


@cache
def _data_url(file_name: str) -> str:
    """A file of `three/assets/` written inside the page, since the scene cannot read files of the site."""
    path = ASSETS_DIR / file_name
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{MEDIA_TYPES[path.suffix]};base64,{encoded}"


def scene_assets(objects: list[str]) -> dict[str, str]:
    """The NASA files the given objects need, as {name: data URL}: only those, to keep the page light."""
    needed = {}
    for name in objects:
        needed.update(OBJECT_ASSETS.get(name, {}))
    return {name: _data_url(file_name) for name, file_name in needed.items()}


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


def places_page(objects: list[str], zones: list[dict], pick_key: str, zoom_from: int = -1) -> str:
    """HTML of the places scene: each object drawn in its zone.

    A zone is {cx, cy, w, h} (see components.py). `pick_key` is the key of the container holding the
    buttons over the objects: the scene reads in the page which button is chosen, to highlight its object,
    so the HTML stays the same when the choice changes and the scene is not reloaded. `zoom_from` is the
    column (0, 1 or 2) the planet had among Earth, Moon and Mars: the scene plays the zoom from there, once.
    """
    settings = {
        "objects": objects,
        "zones": zones,
        "pickKey": pick_key,
        "zoomFrom": zoom_from,
        "assets": scene_assets(objects),
    }
    return _fill("places.html", settings)


def flame_scene(gravity: float, oxygen: float, height: int = 460) -> None:
    """Show the 3D flame. `gravity` goes from 0 (microgravity) to 1 (Earth), `oxygen` is in %."""
    st.iframe(flame_page(gravity, oxygen), height=height)


def places_scene(objects: list[str], zones: list[dict], pick_key: str, zoom_from: int = -1, height: int = 420) -> None:
    """Show 3D objects, each in its zone (see `places_page`)."""
    st.iframe(places_page(objects, zones, pick_key, zoom_from), height=height)


def mascot_scene(height: int = 260) -> None:
    """Show the cartoon flame mascot, on a transparent background."""
    st.iframe(_fill("mascot.html", {}), height=height)
