"""The user's environment (page 1): its conditions with their sources, read from and written to the scenario.

Lot A (PR #28) gives `conditions_habitat(habitat)` and an 8-key `get_scenario()` / `set_scenario(**keys)`.
Until it is on main, `conditions` uses a copy of its table and only habitat and profile reach the scenario.
"""

import contextlib

import flame.commun as commun
from flame.commun import get_scenario
from flame.ui.labels import label

EARTH = "Terre"
# The environment keys of the extended scenario (lot A), written by page 1.
ENVIRONMENT_KEYS = ("oxygene_pct", "pression_kpa", "gravite", "type_combustible", "debit_air_cm_s")

# Copy of the lot A table (`flame/commun/habitats.py` in PR #28), used until `conditions_habitat` is on main.
# Ranges are (min, max); None = no bound. Earth is the reference: 21 % and 14.7 psi from the statement.
FALLBACK_CONDITIONS = {
    "Vaisseau": ((19.0, 23.0), (90.0, 110.0), 0.0, "à sourcer", "à sourcer"),
    "Station": ((19.0, 23.0), (90.0, 110.0), 0.0, "à sourcer", "à sourcer"),
    "Base lunaire": ((30.0, None), (None, 70.3), 0.165, "énoncé", "à sourcer"),
    "Rover pressurisé": ((30.0, None), (None, 70.3), 0.165, "énoncé", "à sourcer"),
    "Base martienne": ((None, None), (None, None), 0.38, "inconnu", "à sourcer"),
    EARTH: ((19.0, 23.0), (90.0, 110.0), 1.0, "énoncé", "énoncé"),
}
SOURCE_NAMES = {"énoncé": "statement", "à sourcer": "to be sourced", "inconnu": "unknown"}


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


def environment_values(place: str) -> dict:
    """The environment of `place` as the scenario holds it: what the user typed, else the habitat's values."""
    scenario = get_scenario()
    if place != EARTH and scenario.get("habitat") == place and "oxygene_pct" in scenario:
        return {key: scenario[key] for key in ENVIRONMENT_KEYS}
    known = conditions(place)
    return {
        "oxygene_pct": known["oxygene_pct"],
        "pression_kpa": known["pression_kpa"],
        "gravite": known["gravite"],
        "type_combustible": [],
        "debit_air_cm_s": (None, None),
    }


def save_environment(**keys) -> None:
    """Write the environment of page 1 in the scenario, for every page (`set_scenario(**keys)`, lot A)."""
    # Before lot A is on main, set_scenario only takes habitat, pillar and profile: the top bar writes those.
    with contextlib.suppress(TypeError):
        commun.set_scenario(**keys)


def source_name(source: str) -> str:
    """A source in English: "énoncé" gives "statement"."""
    return SOURCE_NAMES.get(source, source)


def bounds_text(name: str, bounds: tuple | None, unit: str) -> str | None:
    """ "O₂ ≥ 30 %", "≤ 70.3 kPa", "19–23 %", or None when there is no bound."""
    low, high = bounds or (None, None)
    prefix = f"{name} " if name else ""
    if low is not None and high is not None:
        return f"{prefix}{low:g}–{high:g} {unit}"
    if low is not None:
        return f"{prefix}≥ {low:g} {unit}"
    if high is not None:
        return f"{prefix}≤ {high:g} {unit}"
    return None


def environment_summary(habitat: str) -> str:
    """One line for the sidebar: "Moon base · O₂ ≥ 30 % · ≤ 70.3 kPa · 0.165 g"."""
    values = environment_values(habitat)
    parts = [label(habitat)]
    parts.append(bounds_text("O₂", values["oxygene_pct"], "%") or "O₂ unknown")
    parts.append(bounds_text("", values["pression_kpa"], "kPa") or "pressure unknown")
    if values["gravite"] is not None:
        parts.append(f"{values['gravite']:g} g")
    if values["type_combustible"]:
        parts.append(label(";".join(values["type_combustible"])))
    return " · ".join(parts)
