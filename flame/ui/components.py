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
# One line under each pillar button, so users know what they pick (the three pillars of NASA fire safety).
PILLAR_HINTS = {
    "Prévenir": "Stop a fire from starting or spreading",
    "Détecter": "Notice a fire or smoke early",
    "Éteindre": "Put a fire out",
}

SCENE_HEIGHT = 420

# A zone is the clickable area around one 3D object: an ellipse centred on (cx, cy), in fractions of the
# frame's width and height, and w, h in fractions of the frame's HEIGHT (the scene sizes objects by the
# height, so zones stay around their objects whatever the screen width). The scene draws each object at its
# zone centre, and a transparent round button covers the zone: clicking the object clicks the button.
# `label`: where the name goes, "below" (default) or "right".
FIRST_VIEW_ZONES = [
    {"cx": 1 / 6, "cy": 0.48, "w": 0.75, "h": 0.5},
    {"cx": 1 / 2, "cy": 0.48, "w": 0.5, "h": 0.5},
    {"cx": 5 / 6, "cy": 0.48, "w": 0.5, "h": 0.5},
]
CENTRE = {"cx": 0.5, "cy": 0.55, "w": 0.7, "h": 0.7}  # the whole planet
LEFT = {"cx": 0.14, "cy": 0.55, "w": 0.55, "h": 0.5}  # on the orbit, left of the planet
RIGHT = {"cx": 0.86, "cy": 0.55, "w": 0.55, "h": 0.5}  # on the orbit, right of the planet
TOP = {"cx": 0.5, "cy": 0.15, "w": 0.36, "h": 0.2, "label": "right"}  # driving on the top edge

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

# Names glow instead of drawing a frame: white on hover, flame orange once chosen.
NAME_GLOW = "0 0 6px rgba(255, 255, 255, 0.9), 0 0 14px rgba(255, 255, 255, 0.6)"
CHOSEN_GLOW = "0 0 6px rgba(249, 115, 22, 0.95), 0 0 16px rgba(249, 115, 22, 0.7)"


def _picker_style(key: str, zones: list[dict]) -> str:
    """CSS that turns the buttons of container `key` into invisible round zones over the 3D frame."""
    box = f".st-key-{key}"
    rules = [
        f"{box} {{ margin-top: calc(-{SCENE_HEIGHT}px - 1rem); height: {SCENE_HEIGHT}px; position: relative; }}",
        f'{box} [data-testid="stHorizontalBlock"] {{ position: relative; height: {SCENE_HEIGHT}px; }}',
        f'{box} [data-testid="stColumn"] {{ position: absolute !important; min-width: 0; padding: 0; }}',
        f"""{box} button {{
  width: 100%; border-radius: 50%; border: none !important; background: transparent !important;
  box-shadow: none !important; position: relative; padding: 0;
}}""",
        f"""{box} button p {{
  position: absolute; left: 50%; top: calc(100% + 2px); transform: translateX(-50%); white-space: nowrap;
  font-weight: 700; color: rgba(230, 233, 242, 0.85); text-shadow: 0 1px 2px #000;
  transition: color 0.2s, text-shadow 0.2s;
}}""",
        f"{box} button:hover p, {box} button:focus-visible p {{ color: #fff; text-shadow: {NAME_GLOW}; }}",
        f'{box} [data-testid="stBaseButton-primary"] p {{ color: #fdba74; text-shadow: {CHOSEN_GLOW}; }}',
        f"@media (max-width: 640px) {{ {box} button p {{ font-size: 0.75rem; }} }}",
    ]
    for i, zone in enumerate(zones, start=1):
        width, height = zone["w"] * SCENE_HEIGHT, zone["h"] * SCENE_HEIGHT
        column = f'{box} [data-testid="stColumn"]:nth-child({i})'
        # `top` in pixels: Streamlit keeps the row's height at 0, so a percentage would give 0.
        top = zone["cy"] * SCENE_HEIGHT - height / 2
        rules.append(
            f"{column} {{ left: calc({zone['cx']:.2%} - {width / 2:.0f}px); top: {top:.0f}px;"
            f" width: {width:.0f}px !important; flex: none !important; }}"
        )
        rules.append(f"{column} button {{ height: {height:.0f}px; }}")
        if zone.get("label") == "right":
            rules.append(f"{column} button p {{ left: calc(100% - 1.5rem); top: 50%; transform: translateY(-50%); }}")
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
    hints: dict | None = None,
) -> None:
    """A row of buttons; the chosen value's button is highlighted. `hints`: a short line under each button."""
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
        if hints:
            column.caption(hints[value])


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
    st.html(BACK_STYLE)
    with st.container(key="ui_back_row"):
        st.button("All planets", icon=":material/chevron_left:", key="ui_back", on_click=go_back)
    places = PLACES_BY_BODY[body]
    place = current_place() if current_place() in places else None
    objects = [PLACE_VIEW[p][0] for p in places]
    zones = [PLACE_VIEW[p][1] for p in places]
    zoom_from = BODIES.index(body) if take_zoom() else -1
    _pick_in_3d(places, objects, zones, place, action=choose_place, prefix="ui_place", name=label, zoom_from=zoom_from)
    return body, place


# The three pillars as large white tiles: an orange icon, the name, and its hint inside the tile.
# The chosen one gets a flame-orange ring and a faint warm tint.
PILLAR_STYLE = """<style>
.st-key-ui_pillars [data-testid="stColumn"] { position: relative; }
.st-key-ui_pillars button {
  height: 210px; border-radius: 28px; background: #fff; border: 2px solid transparent;
  flex-direction: column; justify-content: flex-start; gap: 0.7rem; padding: 1.8rem 1rem 0;
}
/* Icon above the name, not beside it. */
.st-key-ui_pillars button > div > span { display: flex; flex-direction: column; align-items: center; gap: 0.6rem; }
.st-key-ui_pillars button p { font-size: 1.6rem; font-weight: 700; letter-spacing: -0.03em; color: #1d1d1f; }
.st-key-ui_pillars button [data-testid="stIconMaterial"] { font-size: 2.6rem; color: #e0662a; }
.st-key-ui_pillars button:hover { transform: scale(1.02); box-shadow: 0 18px 40px -12px rgba(29, 29, 31, 0.2); }
.st-key-ui_pillars [data-testid="stBaseButton-primary"] { background: #fff8f3; border-color: #e0662a; }
.st-key-ui_pillars [data-testid="stBaseButton-primary"] p { color: #c9541c; }
/* The hint sits inside the tile, near its bottom edge; clicks go through it to the button. */
.st-key-ui_pillars [data-testid="stElementContainer"]:has([data-testid="stCaptionContainer"]) {
  position: absolute; left: 0; right: 0; top: 136px; padding: 0 1.4rem; pointer-events: none;
}
.st-key-ui_pillars [data-testid="stCaptionContainer"] p {
  text-align: center; font-size: 1rem; line-height: 1.35; color: #6e6e73; font-weight: 500;
}

</style>"""

# "Back" as a plain flame-coloured text link with a chevron, not a framed button.
BACK_STYLE = """<style>
.st-key-ui_back_row button { border: none; background: transparent; padding: 0; min-height: 0; }
.st-key-ui_back_row button p, .st-key-ui_back_row button span { color: #e0662a; font-size: 1.05rem; }
.st-key-ui_back_row button:hover p { text-decoration: underline; }
.st-key-ui_back_row { margin-bottom: 0.4rem; }
</style>"""


def pillar_picker() -> str | None:
    """The pillars as three large cards: prevent, detect, extinguish. Returns the chosen pillar, or None."""
    pillar = current_pillar()
    st.html(PILLAR_STYLE)
    with st.container(key="ui_pillars"):
        _button_row(PILIERS, pillar, choose_pillar, "ui_pillar", icons=PILLAR_ICONS, hints=PILLAR_HINTS)
    return pillar
