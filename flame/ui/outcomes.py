"""Can a flame burn in an environment? What NASA's tests that match it show, and nothing more.

Only the `resultat` column of NASA's tests is read. Sorting its wording into four kinds is the team's reading
of NASA's labels, and the card says so; a test with no recorded result stays "no result recorded".
"""

from html import escape

import pandas as pd
import streamlit as st

BURNED = "burned"
WENT_OUT = "went_out"
NO_IGNITION = "no_ignition"
UNKNOWN = "unknown"

# Order, wording and colour of each kind (60-30-10: the accent marks the flames that burned).
KINDS = {
    BURNED: ("A flame burned", "#e8622a"),
    # NASA's "Extinction" (FLEX droplets): the droplet was lit and burned, then the flame went out by itself.
    WENT_OUT: ("Burned, then went out by itself", "#8fa3d9"),
    NO_IGNITION: ("No ignition", "#c9ccd8"),
    UNKNOWN: ("No result recorded", "rgba(160, 175, 255, 0.18)"),
}


def kind_of_result(result: object) -> str:
    """One of the four kinds, from NASA's wording of a test result (the team's reading)."""
    if not isinstance(result, str) or not result.strip():
        return UNKNOWN
    text = result.lower()
    if "extinction" in text:
        return WENT_OUT
    # Saffire-II gives two lengths, "microgravity burn length ...; 1-g burn length ...": only the first one,
    # the microgravity one, says whether the sample burned in space.
    in_space = text.split(";")[0]
    if "hot ignition: no" in text or "burn length ~ 0" in in_space:
        return NO_IGNITION
    if (
        "hot ignition: yes" in text
        or "hot ignition: flash" in text
        or "cool flame observed" in text
        or "completion" in text
        or "disruption" in text
        or "burn length" in text
    ):
        return BURNED
    return UNKNOWN


def count_outcomes(tests: pd.DataFrame) -> dict[str, int]:
    """How many of `tests` fall in each kind, in the order of `KINDS`."""
    kinds = tests["resultat"].map(kind_of_result) if len(tests) else pd.Series(dtype=str)
    return {kind: int((kinds == kind).sum()) for kind in KINDS}


def _has_atmosphere_bounds(scenario: dict) -> bool:
    """True when the environment gives at least one oxygen or pressure bound (the Mars base gives none)."""
    bounds = [*(scenario.get("oxygene_pct") or (None, None)), *(scenario.get("pression_kpa") or (None, None))]
    return any(bound is not None for bound in bounds)


def answer(counts: dict[str, int], scenario: dict) -> tuple[str, str, str]:
    """The short answer to "can a flame burn here?": (level, headline, explanation).

    level: "yes", "not_seen" or "no_answer". Only what the matching tests show, never a safety judgement.
    """
    recorded = counts[BURNED] + counts[WENT_OUT] + counts[NO_IGNITION]
    if not _has_atmosphere_bounds(scenario):
        return (
            "no_answer",
            "No answer",
            "This environment gives no oxygen or pressure bounds, so every NASA test matches it and they say "
            "nothing about it.",
        )
    flames = counts[BURNED] + counts[WENT_OUT]
    if flames:
        went_out = (
            f" In {counts[WENT_OUT]:,} of them it went out by itself before the fuel was used up."
            if counts[WENT_OUT]
            else ""
        )
        return (
            "yes",
            "Yes",
            f"A flame burned in {flames:,} of the {recorded:,} NASA tests run in these conditions "
            f"that have a recorded result.{went_out}",
        )
    if recorded:
        return (
            "not_seen",
            "Not seen in NASA's tests",
            f"No flame burned in the {recorded:,} matching tests with a recorded result. "
            "That is what these tests show, not a proof that a fire cannot start.",
        )
    return "no_answer", "No data", "None of the NASA tests that match these conditions has a recorded result."


def outcomes_card(tests: pd.DataFrame, scenario: dict) -> None:
    """The answer, then a bar of the recorded outcomes of `tests` (the tests that match the environment).

    The tests with no recorded result are counted apart, outside the bar.
    """
    counts = count_outcomes(tests)
    level, headline, explanation = answer(counts, scenario)
    st.html(
        f'<div class="ff-answer ff-{level}"><strong>{escape(headline)}</strong><span>{escape(explanation)}</span></div>'
    )
    recorded = {kind: count for kind, count in counts.items() if kind != UNKNOWN}
    # The bar: only when the answer rests on tests with a recorded result.
    if level != "no_answer" and sum(recorded.values()):
        bar = "".join(
            f'<span style="flex: {count}; background: {KINDS[kind][1]};" '
            f'title="{escape(KINDS[kind][0])}: {count}"></span>'
            for kind, count in recorded.items()
            if count
        )
        legend = "".join(
            f'<li><i style="background: {KINDS[kind][1]};"></i>{escape(KINDS[kind][0])} <b>{count:,}</b></li>'
            for kind, count in recorded.items()
        )
        st.html(f'<div class="ff-outcomes"><div class="ff-bar">{bar}</div><ul>{legend}</ul></div>')
    st.caption(
        f"{sum(counts.values()):,} NASA PSI tests match your environment; {counts[UNKNOWN]:,} of them have no "
        "recorded result and are left out of the bar. These are controlled combustion experiments, not fires; "
        "sorting NASA's result wording into kinds is the team's reading. Not a safety certification."
    )
