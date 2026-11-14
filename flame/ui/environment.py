"""The user's environment (page 1): its conditions with their sources, and saving it in the scenario.

Lot A of the reframing gives `conditions_habitat(habitat)` and an extended `set_scenario(**keys)`.
Until it is merged, a copy of its table is used here, and only habitat, pillar and profile reach the
scenario; the other keys wait in `st.session_state["ui_environment"]`.
"""

import contextlib

import streamlit as st

import flame.commun as commun
from flame.commun import get_scenario
from flame.ui.labels import label

EARTH = "Terre"

# Copy of the lot A table (orchestration message of Sat 16:57), used until `conditions_habitat` is merged.
# Ranges are (min, max); None = no bound. Earth is the reference: 21 % and 14.7 psi from the statement.
FALLBACK_CONDITIONS = {
    "Vaisseau": ((19, 23), (90, 110), 0.0, "à sourcer", "microgravité"),
    "Station": ((19, 23), (90, 110), 0.0, "à sourcer", "microgravité"),
    "Base lunaire": ((30, None), (None, 70.3), 0.165, "énoncé", "à sourcer"),
    "Rover pressurisé": ((30, None), (None, 70.3), 0.165, "énoncé", "à sourcer"),
    "Base martienne": ((None, None), (None, None), 0.38, "inconnu", "à sourcer"),
    EARTH: ((19, 23), (90, 110), 1.0, "énoncé", "énoncé"),
}
SOURCE_NAMES = {"énoncé": "statement", "à sourcer": "to be sourced", "inconnu": "unknown", "microgravité": "orbit"}


def conditions(place: str) -> dict:
    """Oxygen and pressure ranges, gravity and the source of each, for a crew environment (or Earth).

    {"oxygene_pct": (min, max), "pression_kpa": (min, max), "gravite": g, "sources": {key: source}}
    """
    from_lot_a = getattr(commun, "conditions_habitat", None)
    if from_lot_a is not None and place != EARTH:
        return from_lot_a(place)
    oxygen, pressure, gravity, atmosphere_source, gravity_source = FALLBACK_CONDITIONS[place]
    return {
        "oxygene_pct": oxygen,
        "pression_kpa": pressure,
        "gravite": gravity,
        "sources": {"oxygene_pct": atmosphere_source, "pression_kpa": atmosphere_source, "gravite": gravity_source},
    }


def source_name(source: str) -> str:
    """A source in English: "énoncé" gives "statement"."""
    return SOURCE_NAMES.get(source, source)


def save_environment(**keys) -> None:
    """Write the environment of page 1 in the scenario, for every page.

    With lot A merged, `set_scenario(**keys)` takes them all; before, they wait in the session.
    """
    st.session_state["ui_environment"] = keys
    # Before lot A, set_scenario only takes habitat, pillar and profile: the top bar writes those.
    with contextlib.suppress(TypeError):
        commun.set_scenario(**keys)


def full_scenario() -> dict:
    """The scenario with the environment keys of page 1, even before lot A extends `get_scenario()`."""
    return {**get_scenario(), **st.session_state.get("ui_environment", {})}


def bounds_text(name: str, bounds: tuple | None, unit: str) -> str | None:
    """ "O₂ ≥ 30 %", "≤ 70.3 kPa", "19–23 %", or None when there is no bound."""
    low, high = bounds or (None, None)
    if low is not None and high is not None:
        return f"{name} {low:g}–{high:g} {unit}"
    if low is not None:
        return f"{name} ≥ {low:g} {unit}"
    if high is not None:
        return f"{name} ≤ {high:g} {unit}"
    return None


def environment_summary(scenario: dict) -> str:
    """One line for the sidebar: "Moon base · O₂ ≥ 30 % · ≤ 70.3 kPa · 0.165 g · Prevent"."""
    parts = [label(scenario.get("habitat", ""))]
    parts.append(bounds_text("O₂", scenario.get("oxygene_pct"), "%") or "O₂ unknown")
    parts.append(bounds_text("", scenario.get("pression_kpa"), "kPa") or "pressure unknown")
    if scenario.get("gravite") is not None:
        parts.append(f"{scenario['gravite']:g} g")
    if scenario.get("type_combustible"):
        parts.append(label(";".join(scenario["type_combustible"])))
    parts.append(label(scenario["pilier"]) if scenario.get("pilier") else "All pillars")
    return " · ".join(part.strip() for part in parts)
