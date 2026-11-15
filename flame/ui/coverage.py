"""Under which conditions NASA's research was done, set against the user's environment.

One row per condition (gravity, oxygen, pressure, oxygen and pressure together, air flow, each fuel type):
what NASA's PSI tests cover, what the environment asks for, and whether any test was run there. When none
was, the row says so plainly. Everything is counted from NASA's test rows (`charger_tests`) and the team's
fuel type of each investigation (`charger_fiches`); nothing is estimated.
"""

from html import escape

import pandas as pd
import streamlit as st

TESTED, PARTLY, NOT_TESTED, NO_BOUNDS = "Tested", "Partly", "Not tested", "No bounds given"
FUEL_TYPES = {"solide": "Solid fuels", "liquide": "Liquid fuels", "gaz": "Gas fuels"}


def _inside(values: pd.Series, bounds: tuple | None) -> pd.Series:
    """Which values fall in a range (min, max); None means no bound on that side."""
    low, high = bounds or (None, None)
    keep = values.notna()
    if low is not None:
        keep &= values >= low
    if high is not None:
        keep &= values <= high
    return keep


def _range_text(bounds: tuple | None, unit: str) -> str:
    """ "≥ 30 %", "≤ 70.3 kPa", "19–23 %", or "any" when there is no bound."""
    low, high = bounds or (None, None)
    if low is not None and high is not None:
        return f"{low:g}–{high:g} {unit}"
    if low is not None:
        return f"≥ {low:g} {unit}"
    if high is not None:
        return f"≤ {high:g} {unit}"
    return "any"


def _span(values: pd.Series, unit: str) -> str:
    """The range NASA's tests cover, "12–85 %"."""
    values = values.dropna()
    return f"{values.min():g}–{values.max():g} {unit}" if len(values) else "not recorded"


def _no_bounds(bounds: tuple | None) -> bool:
    return all(bound is None for bound in (bounds or (None, None)))


def _sources(tests: pd.DataFrame, keep: pd.Series) -> list[tuple[str, str]]:
    """The NASA investigations behind some tests: (PSI id, its page on psi.nasa.gov), to check them by hand."""
    if "source" not in tests.columns:
        return []
    found = tests.loc[keep, ["investigation_id", "source"]].dropna().drop_duplicates("investigation_id")
    return sorted(zip(found["investigation_id"], found["source"], strict=False))


def coverage(tests: pd.DataFrame, fiches: pd.DataFrame, scenario: dict) -> list[dict]:
    """One row per condition: {condition, nasa, yours, status, detail}. status is Tested, Partly, Not tested
    or No bounds given; detail says how many tests, or what is missing."""
    rows = []
    gravity = scenario.get("gravite")
    if gravity is None:
        rows.append(
            dict(
                condition="Gravity",
                nasa="Microgravity (ISS, Cygnus) and Earth's 1 g",
                yours="unknown",
                status=NO_BOUNDS,
                detail="Your environment gives no gravity.",
            )
        )
    elif gravity == 0 or gravity == 1:
        where = "in microgravity on the ISS and the Cygnus spacecraft" if gravity == 0 else "at Earth's 1 g"
        rows.append(
            dict(
                condition="Gravity",
                nasa="Microgravity (ISS, Cygnus) and Earth's 1 g",
                yours=f"{gravity:g} g",
                status=TESTED,
                detail=f"NASA's PSI tests were run {where}.",
            )
        )
    else:
        rows.append(
            dict(
                condition="Gravity",
                nasa="Microgravity (ISS, Cygnus) and Earth's 1 g",
                yours=f"{gravity:g} g",
                status=NOT_TESTED,
                detail=f"No PSI test was run at {gravity:g} g: partial gravity has never been tested.",
            )
        )

    oxygen, pressure = scenario.get("oxygene_pct"), scenario.get("pression_kpa")
    in_oxygen = _inside(tests["oxygene_pct"], oxygen)
    in_pressure = _inside(tests["pression_kpa"], pressure)
    for name, column, bounds, unit, inside in (
        ("Oxygen", "oxygene_pct", oxygen, "%", in_oxygen),
        ("Pressure", "pression_kpa", pressure, "kPa", in_pressure),
    ):
        count = int(inside.sum())
        found = _sources(tests, inside) if count else []
        if _no_bounds(bounds):
            status, detail = NO_BOUNDS, f"Your environment gives no {name.lower()} bound."
        elif count:
            status, detail = TESTED, f"{count:,} tests ran at {_range_text(bounds, unit)}."
        else:
            status, detail = NOT_TESTED, f"No test was run at {_range_text(bounds, unit)}."
        rows.append(
            dict(
                condition=name,
                nasa=_span(tests[column], unit),
                yours=_range_text(bounds, unit),
                status=status,
                detail=detail,
                sources=found if status == TESTED and len(found) <= 6 else [],  # a long list of links says nothing
            )
        )

    both = in_oxygen & in_pressure
    if _no_bounds(oxygen) and _no_bounds(pressure):
        status, detail = NO_BOUNDS, "Without oxygen or pressure bounds, every test matches and says nothing specific."
    elif int(both.sum()):
        status = TESTED if int(both.sum()) >= 10 else PARTLY
        detail = (
            f"{int(both.sum()):,} tests ran with both the oxygen and the pressure of your environment, "
            f"in {tests.loc[both, 'investigation_id'].nunique()} investigation(s)."
        )
    else:
        status, detail = NOT_TESTED, "No test was run with both your oxygen and your pressure at once."
    rows.append(
        dict(
            condition="Oxygen and pressure together",
            nasa="see the chart",
            yours=(f"{_range_text(oxygen, '%')}, {_range_text(pressure, 'kPa')}"),
            status=status,
            detail=detail,
            sources=_sources(tests, both) if not _no_bounds(oxygen) or not _no_bounds(pressure) else [],
        )
    )

    flow = scenario.get("debit_air_cm_s")
    if not _no_bounds(flow):
        count = int((both & _inside(tests["debit_air_cm_s"], flow)).sum())
        rows.append(
            dict(
                condition="Air flow",
                nasa=_span(tests["debit_air_cm_s"], "cm/s"),
                yours=_range_text(flow, "cm/s"),
                status=TESTED if count else NOT_TESTED,
                detail=f"{count:,} of those tests also had your air flow."
                if count
                else "None of those tests had your air flow.",
                sources=_sources(tests, both & _inside(tests["debit_air_cm_s"], flow)),
            )
        )

    fuel_of = dict(zip(fiches["id"], fiches["type_combustible"].fillna(""), strict=False))
    types = tests["investigation_id"].map(lambda identifier: str(fuel_of.get(identifier, "")))
    # Tests at the right oxygen whose pressure was not recorded: they may or may not fit, so they are told apart.
    pressure_unknown = in_oxygen & tests["pression_kpa"].isna() & (not _no_bounds(pressure))
    for key, name in FUEL_TYPES.items():
        of_type = types.str.contains(key)
        count = int((both & of_type).sum())
        unknown = int((pressure_unknown & of_type).sum())
        sources = _sources(tests, (both | pressure_unknown) & of_type)
        if count:
            status, detail = TESTED, f"{count:,} tests."
        elif unknown:
            status = PARTLY
            plural = "s" if unknown > 1 else ""
            detail = f"No test with both; {unknown:,} test{plural} ran at your oxygen with no recorded pressure."
        else:
            status, detail = NOT_TESTED, "Not tested in your conditions."
        rows.append(
            dict(
                condition=name,
                nasa=f"{int(of_type.sum()):,} tests in all",
                yours="in your oxygen and pressure",
                status=status,
                detail=detail,
                sources=sources,
            )
        )
    return rows


def coverage_card(rows: list[dict]) -> None:
    """The rows as a compact table: condition, what NASA covers, your environment, and a status chip.
    Each row links the NASA investigations its tests come from, so the numbers can be checked on psi.nasa.gov."""

    def links(row: dict) -> str:
        found = row.get("sources") or []
        if not found:
            return ""
        return (
            " From "
            + ", ".join(f'<a href="{escape(url)}" target="_blank">{escape(name)}</a>' for name, url in found)
            + "."
        )

    lines = "".join(
        f'<div class="ff-cov-row"><span class="ff-cov-name">{escape(row["condition"])}</span>'
        f'<span class="ff-cov-nasa">{escape(row["nasa"])}</span>'
        f'<span class="ff-cov-yours">{escape(row["yours"])}</span>'
        f'<span class="ff-cov-status ff-{row["status"].lower().replace(" ", "-")}">{escape(row["status"])}</span>'
        f'<span class="ff-cov-detail">{escape(row["detail"])}{links(row)}</span></div>'
        for row in rows
    )
    head = (
        '<div class="ff-cov-row ff-cov-head"><span>Condition</span><span>Tested by NASA</span>'
        "<span>Your environment</span><span>Status</span><span></span></div>"
    )
    st.html(f'<div class="ff-coverage">{head}{lines}</div>')
    st.caption(
        "Counted from the test rows of NASA's Physical Sciences Informatics (psi.nasa.gov); a test counts when its "
        "recorded value falls in your range. Each link opens the investigation, with its test list and data files. "
        "Fuel types are the team's classification of each investigation."
    )
