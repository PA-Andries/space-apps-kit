"""Display blocks shared between pages."""

from collections.abc import Callable
from pathlib import Path

import pandas as pd
import streamlit as st

from flame.ui.labels import label
from flame.ui.places import (
    BODIES,
    EARTH,
    PLACE_ICONS,
    PLACE_NAMES,
    PLACE_ROWS,
    PLACES_BY_BODY,
    SPACESUIT,
    choose_body,
    choose_place,
    current_body,
    current_place,
    go_back,
)
from flame.ui.scene import places_scene

BODY_NAMES = {"Terre": "Earth & orbit", "Lune": "Moon", "Mars": "Mars"}
SCENE_HEIGHT = 440

# A zone is the clickable area around one 3D object: an ellipse centred on (cx, cy), in fractions of the
# frame's width and height, and w, h in fractions of the frame's HEIGHT (the scene sizes objects by the
# height, so zones stay around their objects whatever the screen width). The scene draws each object at its
# zone centre, and a transparent round button covers the zone: clicking the object clicks the button.
# `label`: where the name goes, "below" (default) or "right".
FIRST_VIEW_ZONES = [
    {"cx": 1 / 6, "cy": 0.48, "w": 0.62, "h": 0.5},
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
    # The spacesuit is worn on the Moon during an EVA: the lunar view, with no vehicle to point at.
    SPACESUIT: ("moon_whole", CENTRE),
}

# Names in small, quiet type: they brighten on hover and turn flame orange once chosen (no frame drawn).
NAME_GLOW = "0 0 10px rgba(255, 255, 255, 0.45)"
CHOSEN_GLOW = "0 0 12px rgba(240, 122, 58, 0.5)"


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
  font-weight: 500; font-size: 0.82rem; letter-spacing: 0.06em; text-transform: uppercase;
  color: rgba(226, 232, 245, 0.72); text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
  transition: color 0.2s, text-shadow 0.2s;
}}""",
        f"{box} button:hover p, {box} button:focus-visible p {{ color: #fff; text-shadow: {NAME_GLOW}; }}",
        f'{box} [data-testid="stBaseButton-primary"] p {{ color: #f59a66; text-shadow: {CHOSEN_GLOW}; }}',
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
            rules.append(f"{column} button p {{ left: calc(100% + 0.4rem); top: 50%; transform: translateY(-50%); }}")
    return "<style>\n" + "\n".join(rules) + "\n</style>"


def investigation_card(row: pd.Series) -> None:
    """Show an investigation as a short card: `investigation_card(fiches.iloc[0])`."""
    with st.container(border=True):
        st.markdown(f"**{row['id']}** · {row['nom']}")
        st.caption(f"{label(row['type_combustible'])} · {row['materiel']}")
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
    places_scene(objects, zones, f"ui_pick_{prefix}", zoom_from=options.get("zoom_from", -1), height=SCENE_HEIGHT)
    with st.container(key=f"ui_pick_{prefix}"):
        _button_row(values, chosen, options["action"], prefix, options["name"])


# Moon and Mars: one NASA image of the environment seen from the ground; tap what you want in it.
# A zone is (left, top, width, height) in fractions of the image (credits in images/README.md).
IMAGES_DIR = Path(__file__).parent / "images"
BODY_SCENES = {
    "Lune": (
        "moon_scene.jpg",
        1100 / 1084,  # width / height of the image
        "NASA illustration, Moon to Mars Transportation and Habitation (NASA logo removed from the rover)",
        {"Base lunaire": (0.0, 0.03, 0.78, 0.34), "Rover pressurisé": (0.24, 0.46, 0.72, 0.54)},
    ),
    "Mars": (
        "mars_base.jpg",
        1400 / 630,
        "NASA artist's concept, First Humans on Mars (PIA23302)",
        {"Base martienne": (0.37, 0.3, 0.6, 0.38)},
    ),
}
SCENE_MAX_HEIGHT = 520  # px: the image is never taller than this


def _image_style(key: str, aspect: float, zones: list[tuple[float, float, float, float]]) -> str:
    """CSS that lays transparent buttons over the zones of the image in container `key`."""
    box = f".st-key-{key}"
    rules = [
        f"{box} {{ position: relative; gap: 0; max-width: {SCENE_MAX_HEIGHT * aspect:.0f}px; margin: 0 auto; }}",
        f"{box} [data-testid='stImage'] img {{ border-radius: 18px; display: block; }}",
        f".st-key-{key}_spots {{ position: absolute !important; inset: 0; gap: 0; }}",
        f"""{box} button {{
  width: 100%; height: 100%; border: none !important; background: transparent !important; box-shadow: none !important;
  border-radius: 22px; padding: 0; position: relative;
}}""",
        f"""{box} button p {{
  position: absolute; left: 50%; bottom: 10px; transform: translateX(-50%); white-space: nowrap;
  font-weight: 600; font-size: 0.85rem; letter-spacing: 0.06em; text-transform: uppercase;
  color: rgba(255, 255, 255, 0.9); text-shadow: 0 1px 3px rgba(0, 0, 0, 0.85); transition: color 0.2s, text-shadow 0.2s;
  background: rgba(8, 11, 20, 0.45); padding: 0.2rem 0.6rem; border-radius: 980px;
}}""",
        f"{box} button:hover p, {box} button:focus-visible p {{ color: #fff; text-shadow: {NAME_GLOW}; }}",
        f'{box} [data-testid="stBaseButton-primary"] p {{ color: #f59a66; text-shadow: {CHOSEN_GLOW}; }}',
    ]
    for i, (left, top, width, height) in enumerate(zones):
        rules.append(
            f".st-key-{key}_spot{i} {{ position: absolute !important; left: {left:.1%}; top: {top:.1%};"
            f" width: {width:.1%}; height: {height:.1%}; }}"
        )
        rules.append(
            f".st-key-{key}_spot{i} .stButton, .st-key-{key}_spot{i} [data-testid='stElementContainer']"
            " { height: 100%; }"
        )
    return "<style>\n" + "\n".join(rules) + "\n</style>"


def _pick_on_image(body: str, chosen: str | None) -> None:
    """The NASA image of `body`, where each crew environment is a clickable zone."""
    file_name, aspect, credit, zones = BODY_SCENES[body]
    path = IMAGES_DIR / file_name
    key = f"ui_scene_{body}"
    st.html(_image_style(key, aspect, list(zones.values())))
    with st.container(key=key):
        st.image(str(path), width="stretch")
        with st.container(key=f"{key}_spots"):
            for i, place in enumerate(zones):
                with st.container(key=f"{key}_spot{i}"):
                    st.button(
                        label(place),
                        key=f"ui_place_{place}",
                        type="primary" if place == chosen else "secondary",
                        width="stretch",
                        on_click=choose_place,
                        args=(place,),
                    )
    st.caption(credit)


# The place buttons of page 1: large frosted-glass tiles, the logo in the flame colour; the chosen one is filled.
PLACE_BUTTONS_STYLE = """<style>
.st-key-ui_places { gap: 0.7rem; margin-top: 0.4rem; }
.st-key-ui_places button {
  min-height: 8rem; border-radius: 18px; padding: 0.6rem 1rem;
  background: rgba(255, 255, 255, 0.05); border: 1.5px solid rgba(160, 175, 255, 0.14);
}
.st-key-ui_places button p { font-weight: 600; font-size: 1rem; }
.st-key-ui_places button [data-testid="stIconMaterial"] { font-size: 1.6rem; color: #ff7a3d; margin-right: 0.2rem; }
.st-key-ui_places [data-testid="stBaseButton-primary"] [data-testid="stIconMaterial"] { color: #fff; }
.st-key-ui_places button:hover { border-color: #ff7a3d; background: rgba(255, 255, 255, 0.1); color: inherit; }
.st-key-ui_places [data-testid="stBaseButton-primary"] {
  background: #ff7a3d; border-color: transparent;
  box-shadow: 0 0 28px rgba(255, 122, 61, 0.35);
}
.st-key-ui_places [data-testid="stBaseButton-primary"]:hover { background: #ff8c55; color: #fff; }
.st-key-ui_places [data-testid="stBaseButton-primary"] p { color: #fff; }
</style>"""


def place_buttons(current: str, selected: bool = True) -> str:
    """One button per habitable crew environment, each with a small logo, and Earth as the reference.

    `current`: the place to show while the user has not clicked yet (the scenario's habitat).
    `selected`: False when the user's values left the place's range: no button is highlighted then.
    Returns the place to show; its button is highlighted.
    """
    chosen = current_place() or current
    st.html(PLACE_BUTTONS_STYLE)
    with st.container(key="ui_places"):
        for row in PLACE_ROWS:
            _button_row(row, chosen if selected else None, choose_place, "ui_place", place_name, PLACE_ICONS)
    return chosen


def place_name(place: str) -> str:
    """The text of a place's button: "Moon base", or "Earth (reference)"."""
    return PLACE_NAMES.get(place, label(place))


def place_picker() -> tuple[str | None, str | None]:
    """Earth, Moon and Mars in 3D; Earth zooms in on its orbit, the Moon and Mars show a NASA image to tap in.

    No longer on page 1, which uses `place_buttons()` (Hugo's request, with Mathéo's agreement); kept for reuse.
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
    if body in BODY_SCENES:
        _pick_on_image(body, place)
        return body, place
    objects = [PLACE_VIEW[p][0] for p in places]
    zones = [PLACE_VIEW[p][1] for p in places]
    zoom_from = BODIES.index(body)
    _pick_in_3d(places, objects, zones, place, action=choose_place, prefix="ui_place", name=label, zoom_from=zoom_from)
    return body, place


# "Back" as a plain flame-coloured text link with a chevron, not a framed button.
BACK_STYLE = """<style>
.st-key-ui_back_row button { border: none; background: transparent; padding: 0; min-height: 0; }
.st-key-ui_back_row button p, .st-key-ui_back_row button span { color: #ff7a3d; font-size: 1.05rem; }
.st-key-ui_back_row button:hover p { text-decoration: underline; }
.st-key-ui_back_row { margin-bottom: 0.4rem; }
</style>"""
