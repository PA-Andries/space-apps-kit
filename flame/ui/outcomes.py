"""What NASA's tests show for an environment: how the flames behaved in the tests that match it.

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
    BURNED: ("A flame burned", "#ff7a3d"),
    WENT_OUT: ("The flame went out", "#8fa3d9"),
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
    if "hot ignition: no" in text or "burn length ~ 0" in text:
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


def outcomes_card(tests: pd.DataFrame) -> None:
    """A bar of the four kinds for `tests` (the tests that match the environment), with the counts."""
    counts = count_outcomes(tests)
    total = sum(counts.values())
    if total == 0:
        st.info("No NASA test matches this environment, so there is nothing to show yet.")
        return
    recorded = total - counts[UNKNOWN]
    bar = "".join(
        f'<span style="flex: {count}; background: {KINDS[kind][1]};" title="{escape(KINDS[kind][0])}: {count}"></span>'
        for kind, count in counts.items()
        if count
    )
    legend = "".join(
        f'<li><i style="background: {KINDS[kind][1]};"></i>{escape(KINDS[kind][0])} <b>{count:,}</b></li>'
        for kind, count in counts.items()
    )
    st.html(f'<div class="ff-outcomes"><div class="ff-bar">{bar}</div><ul>{legend}</ul></div>')
    if recorded:
        share = round(100 * counts[BURNED] / recorded)
        st.markdown(
            f"**A flame burned in {counts[BURNED]:,} of the {recorded:,} matching tests with a recorded result "
            f"({share} %).** Under these conditions, NASA's tests show that a fire can start and keep burning."
            if counts[BURNED]
            else f"**No flame burned in the {recorded:,} matching tests with a recorded result.** "
            "That is what these tests show, not a proof that a fire cannot start."
        )
    st.caption(
        f"{total:,} NASA PSI tests match your environment; {counts[UNKNOWN]:,} have no recorded result. "
        "Sorting NASA's result wording into these four kinds is the team's reading. Not a safety certification."
    )
