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
)
from flame.ui.scene import places_scene

PILLAR_ICONS = {
    "Prévenir": ":material/shield:",
    "Détecter": ":material/sensors:",
    "Éteindre": ":material/fire_extinguisher:",
}
BODY_NAMES = {"Terre": "Earth & orbit", "Lune": "Moon", "Mars": "Mars"}

# The three.js drawing of each choice (see `three/places.html`).
BODY_OBJECTS = {"Terre": "earth_system", "Lune": "moon", "Mars": "mars"}
PLACE_OBJECTS = {
    EARTH: "earth",
    "Station": "station",
    "Vaisseau": "spacecraft",
    "Base lunaire": "moon_base",
    "Base martienne": "mars_base",
}

SCENE_HEIGHT = 190

# The buttons sit on top of the 3D scene and are transparent:
# you click "on the planet", but the Streamlit button receives the click.
PICKER_STYLE = f"""<style>
[class*="st-key-ui_pick_"] {{ margin-top: calc(-{SCENE_HEIGHT}px - 1rem); position: relative; z-index: 1; }}
[class*="st-key-ui_pick_"] [data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap; }}
[class*="st-key-ui_pick_"] [data-testid="stColumn"] {{ min-width: 0; }}
[class*="st-key-ui_pick_"] button {{
  height: {SCENE_HEIGHT}px; align-items: flex-end; padding-bottom: 8px;
  background: transparent; border: 2px solid transparent; border-radius: 20px;
  transition: border-color 0.2s, background 0.2s, transform 0.2s;
}}
[class*="st-key-ui_pick_"] button:hover {{
  background: rgba(249, 115, 22, 0.07); border-color: rgba(249, 115, 22, 0.45); transform: translateY(-2px);
}}
[class*="st-key-ui_pick_"] [data-testid="stBaseButton-primary"] {{
  background: rgba(249, 115, 22, 0.1); border-color: #f97316; color: #fdba74;
}}
[class*="st-key-ui_pick_"] button p {{
  font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
@media (max-width: 640px) {{
  [class*="st-key-ui_pick_"] [data-testid="stHorizontalBlock"] {{ gap: 0.25rem; }}
  [class*="st-key-ui_pick_"] button {{ padding: 0 2px 4px; }}
  [class*="st-key-ui_pick_"] button p {{ font-size: 0.7rem; }}
}}
</style>"""


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


def _pick_in_3d(values: list[str], objects: list[str], chosen: str | None, action: Callable, prefix: str, name) -> None:
    """A row of 3D objects to choose by clicking on them."""
    st.html(PICKER_STYLE)
    chosen_object = objects[values.index(chosen)] if chosen in values else None
    places_scene(objects, chosen_object, height=SCENE_HEIGHT)
    with st.container(key=f"ui_pick_{prefix}"):
        _button_row(values, chosen, action, prefix, name)


def body_picker() -> str | None:
    """Earth, Moon or Mars in 3D, chosen by clicking on them. Returns the chosen body, or None."""
    body = current_body()
    _pick_in_3d(BODIES, [BODY_OBJECTS[b] for b in BODIES], body, choose_body, "ui_body", BODY_NAMES.get)
    return body


def place_picker(body: str) -> str | None:
    """The places of the chosen body in 3D (for example base or rover). Returns the chosen place, or None."""
    places = PLACES_BY_BODY[body]
    place = current_place() if current_place() in places else None
    objects = [PLACE_OBJECTS.get(p, f"rover_{BODY_OBJECTS[body]}") for p in places]
    _pick_in_3d(places, objects, place, choose_place, "ui_place", label)
    return place


def pillar_picker() -> str | None:
    """The pillar buttons: prevent, detect, extinguish. Returns the chosen pillar, or None."""
    pillar = current_pillar()
    _button_row(PILIERS, pillar, choose_pillar, "ui_pillar", icons=PILLAR_ICONS)
    return pillar
