"""Display blocks shared between pages."""

from collections.abc import Callable

import pandas as pd
import streamlit as st

from flame.commun import PILIERS
from flame.ui.labels import label
from flame.ui.places import (
    BODIES,
    EARTH,
    PLACES_BY_BODY,
    choose_body,
    choose_pillar,
    choose_place,
    current_body,
    current_pillar,
    current_place,
    go_back,
    take_zoom,
)
from flame.ui.scene import places_scene

PILLAR_ICONS = {
    "Prévenir": ":material/shield:",
    "Détecter": ":material/sensors:",
    "Éteindre": ":material/fire_extinguisher:",
}
BODY_NAMES = {"Terre": "Earth & orbit", "Lune": "Moon", "Mars": "Mars"}

SCENE_HEIGHT = 300

# A zone is a rectangle of the 3D frame, in fractions of its width and height. The scene draws each
# object in its zone, and a transparent button covers the same zone: clicking the object clicks the button.
FIRST_VIEW_ZONES = [{"x": i / 3, "y": 0, "w": 1 / 3, "h": 1} for i in range(3)]
CENTRE = {"x": 0.3, "y": 0.3, "w": 0.4, "h": 0.58}  # the whole planet
LEFT = {"x": 0.02, "y": 0.27, "w": 0.24, "h": 0.64}  # on the orbit, left of the planet
RIGHT = {"x": 0.74, "y": 0.27, "w": 0.24, "h": 0.64}  # on the orbit, right of the planet
TOP = {"x": 0.38, "y": 0.0, "w": 0.24, "h": 0.3, "label": "top"}  # on the top edge; name above the object

# The three.js drawing of each choice (see `three/places.html`).
BODY_OBJECTS = {"Terre": "earth_system", "Lune": "moon", "Mars": "mars"}
# Zoomed view: tap the planet itself for Earth or a base; the station and spacecraft orbit it,
# the rover drives on the Moon's edge.
PLACE_VIEW = {
    EARTH: ("earth_whole", CENTRE),
    "Station": ("station", LEFT),
    "Vaisseau": ("spacecraft", RIGHT),
    "Base lunaire": ("moon_whole", CENTRE),
    "Rover pressurisé": ("rover_moon", TOP),
    "Base martienne": ("mars_whole", CENTRE),
}


def _picker_style(key: str, zones: list[dict]) -> str:
    """CSS that turns the buttons of container `key` into transparent zones over the 3D frame."""
    box = f".st-key-{key}"
    rules = [
        f"{box} {{ margin-top: calc(-{SCENE_HEIGHT}px - 1rem); height: {SCENE_HEIGHT}px; position: relative; }}",
        f'{box} [data-testid="stHorizontalBlock"] {{ position: relative; height: {SCENE_HEIGHT}px; }}',
        f'{box} [data-testid="stColumn"] {{ position: absolute !important; min-width: 0; padding: 0; }}',
        f"""{box} button {{
  width: 100%; align-items: flex-end; padding: 0 4px 8px; background: transparent;
  border: 2px solid transparent; border-radius: 20px; transition: border-color 0.2s, background 0.2s;
}}""",
        f"{box} button:hover {{ background: rgba(249, 115, 22, 0.07); border-color: rgba(249, 115, 22, 0.45); }}",
        f'{box} [data-testid="stBaseButton-primary"] {{ background: rgba(249,115,22,0.08); border-color: #f97316; }}',
        f"""{box} button p {{
  font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  text-shadow: 0 1px 2px #000, 0 0 8px #000, 0 0 14px #000;
}}""",
        f'{box} [data-testid="stBaseButton-primary"] p {{ color: #fdba74; }}',
        f"@media (max-width: 640px) {{ {box} button p {{ font-size: 0.7rem; }} }}",
    ]
    for i, zone in enumerate(zones, start=1):
        rules.append(
            # `top` in pixels: Streamlit keeps the row's height at 0, so a percentage would give 0.
            f'{box} [data-testid="stColumn"]:nth-child({i}) {{ left: {zone["x"]:.0%};'
            f" top: {zone['y'] * SCENE_HEIGHT:.0f}px;"
            f" width: {zone['w']:.0%} !important; flex: none !important; }}"
        )
        rules.append(
            f'{box} [data-testid="stColumn"]:nth-child({i}) button {{ height: {zone["h"] * SCENE_HEIGHT:.0f}px; }}'
        )
        if zone.get("label") == "top":
            rules.append(
                f'{box} [data-testid="stColumn"]:nth-child({i}) button {{ align-items: flex-start; padding-top: 2px; }}'
            )
    return "<style>\n" + "\n".join(rules) + "\n</style>"


def investigation_card(row: pd.Series) -> None:
    """Show an investigation as a short card: `investigation_card(fiches.iloc[0])`."""
    with st.container(border=True):
        st.markdown(f"**{row['id']}** · {row['nom']}")
        st.caption(f"{label(row['pilier'])} · {label(row['type_combustible'])} · {row['materiel']}")
        st.write(row["resume"])
        st.link_button("View on PSI", row["source_psi"])


def _button_row(
    values: list[str],
    chosen: str | None,
    action: Callable,
    prefix: str,
    name: Callable = label,
    icons: dict | None = None,
) -> None:
    """A row of buttons; the chosen value's button is highlighted."""
    for column, value in zip(st.columns(len(values)), values, strict=True):
        column.button(
            name(value),
            icon=(icons or {}).get(value),
            key=f"{prefix}_{value}",
            type="primary" if value == chosen else "secondary",
            width="stretch",
            on_click=action,
            args=(value,),
        )


def _pick_in_3d(values: list[str], objects: list[str], zones: list[dict], chosen: str | None, **options) -> None:
    """3D objects to choose by clicking on them. `options`: action, prefix, name, zoom_from."""
    prefix = options["prefix"]
    st.html(_picker_style(f"ui_pick_{prefix}", zones))
    chosen_object = objects[values.index(chosen)] if chosen in values else None
    places_scene(objects, zones, chosen_object, zoom_from=options.get("zoom_from", -1), height=SCENE_HEIGHT)
    with st.container(key=f"ui_pick_{prefix}"):
        _button_row(values, chosen, options["action"], prefix, options["name"])


def place_picker() -> tuple[str | None, str | None]:
    """Earth, Moon and Mars in 3D; clicking one zooms in on the whole planet and what belongs to it.

    Returns (body, place), each None until chosen.
    """
    body = current_body()
    if body is None:
        objects = [BODY_OBJECTS[b] for b in BODIES]
        _pick_in_3d(BODIES, objects, FIRST_VIEW_ZONES, None, action=choose_body, prefix="ui_body", name=BODY_NAMES.get)
        return None, None
    st.button("Back to Earth, Moon and Mars", icon=":material/arrow_back:", key="ui_back", on_click=go_back)
    places = PLACES_BY_BODY[body]
    place = current_place() if current_place() in places else None
    objects = [PLACE_VIEW[p][0] for p in places]
    zones = [PLACE_VIEW[p][1] for p in places]
    zoom_from = BODIES.index(body) if take_zoom() else -1
    _pick_in_3d(places, objects, zones, place, action=choose_place, prefix="ui_place", name=label, zoom_from=zoom_from)
    return body, place


def pillar_picker() -> str | None:
    """The pillar buttons: prevent, detect, extinguish. Returns the chosen pillar, or None."""
    pillar = current_pillar()
    _button_row(PILIERS, pillar, choose_pillar, "ui_pillar", icons=PILLAR_ICONS)
    return pillar
