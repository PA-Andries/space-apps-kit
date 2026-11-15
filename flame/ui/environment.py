"""The user's environment (page 1): its conditions with their sources, read from and written to the scenario.

The scenario and the habitats' conditions come from `flame.commun` (lot A): `get_scenario()`,
`set_scenario(**keys)` and `conditions_habitat(habitat)`. Only Earth, the reference, is described here.
"""

from flame.commun import conditions_habitat, get_scenario, set_scenario
from flame.ui.labels import label
from flame.ui.places import EARTH, REFERENCE_PLACES, SPACESUIT

# The environment keys of the extended scenario (lot A), written by page 1.
ENVIRONMENT_KEYS = ("oxygene_pct", "pression_kpa", "gravite", "type_combustible", "debit_air_cm_s")

# Earth is not a crew environment of the contract: it is the reference, 21 % and 14.7 psi from the statement,
# with the team's tolerance (as for the station in `conditions_habitat`).
EARTH_CONDITIONS = {
    "oxygene_pct": (19.0, 23.0),
    "pression_kpa": (90.0, 110.0),
    "gravite": 1.0,
    "sources": {"oxygene_pct": "énoncé", "pression_kpa": "énoncé", "gravite": "énoncé"},
}
# The spacesuit: the statement gives 100 % oxygen at 4.3 psi (29.6 kPa). It is the lower bound that explains
# the lunar atmosphere: between the suit and Earth's air, to shorten pre-breathing before an EVA.
# Its gravity is left unknown: a suit is worn in microgravity and on the Moon alike.
SPACESUIT_CONDITIONS = {
    "oxygene_pct": (100.0, 100.0),
    "pression_kpa": (29.6, 29.6),
    "gravite": None,
    "sources": {"oxygene_pct": "énoncé", "pression_kpa": "énoncé", "gravite": "inconnu"},
}
SOURCE_NAMES = {"énoncé": "statement", "à sourcer": "to be sourced", "inconnu": "unknown"}


def conditions(place: str) -> dict:
    """Oxygen and pressure ranges, gravity and the source of each, for a crew environment (or Earth).

    {"oxygene_pct": (min, max), "pression_kpa": (min, max), "gravite": g, "sources": {key: source}}
    """
    if place == EARTH:
        return EARTH_CONDITIONS
    if place == SPACESUIT:
        return SPACESUIT_CONDITIONS
    return conditions_habitat(place)


def environment_values(place: str) -> dict:
    """The environment of `place` as the scenario holds it: what the user typed, else the habitat's values."""
    scenario = get_scenario()
    if place not in REFERENCE_PLACES and scenario["habitat"] == place:
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
    """Write the environment of page 1 in the scenario, for every page."""
    set_scenario(**keys)


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
    """One line for the sidebar: "Moon base · O₂ ≥ 30 % · ≤ 70.3 kPa · 0.165 g (no NASA test at this gravity)"."""
    values = environment_values(habitat)
    parts = [label(habitat)]
    parts.append(bounds_text("O₂", values["oxygene_pct"], "%") or "O₂ unknown")
    parts.append(bounds_text("", values["pression_kpa"], "kPa") or "pressure unknown")
    if values["gravite"] is not None:
        # Partial gravity (Moon, Mars) is the place's own value, not a setting of the tool: NASA's PSI tests
        # exist at 0 g and 1 g only, and the line says so instead of showing a bare "0.165 g".
        partial = 0 < float(values["gravite"]) < 1
        parts.append(f"{values['gravite']:g} g" + (" (no NASA test at this gravity)" if partial else ""))
    if values["type_combustible"]:
        parts.append(label(";".join(values["type_combustible"])))
    return " · ".join(parts)
