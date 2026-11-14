"""Page 1 « My environment ». Owner: role F (Interface and 3D); the conditions chart comes from role D.

The user describes their crew environment: the habitat fills oxygen, pressure and gravity, each with its
source, and every value stays editable. The page shows where NASA's tests sit against these conditions,
how many match, and the 3 most relevant investigations. The environment is saved for every page.
The file name stays `accueil.py` because `app.py` (role A) points to it.
"""

import streamlit as st

import flame.comparateur as comparateur
from flame.commun import PILIERS, charger_fiches, charger_tests
from flame.recherche import les_plus_pertinentes
from flame.ui import (
    EARTH,
    card_title,
    conditions,
    dashboard_header,
    footer,
    full_scenario,
    investigation_card,
    label,
    mascot,
    place_picker,
    save_environment,
    show_environment_in_sidebar,
    source_name,
)

FUELS = ["solide", "liquide", "gaz"]  # the contract's fuel types; none chosen = all

fiches = charger_fiches()
tests = charger_tests()
habitat = st.session_state.get("ui_habitat", full_scenario()["habitat"])

dashboard_header(
    "My environment",
    "Describe your habitable crew environment: see which NASA microgravity combustion tests apply to it.",
    [f"{len(fiches)} NASA investigations", f"{len(tests):,} test rows", "Source: NASA PSI"],
)

# --- The crew environment, then its parameters -------------------------------------------------------------
picker_column, form_column = st.columns([7, 5], gap="medium")

with picker_column, st.container(key="ui_card_destination", height="stretch"):
    card_title(
        "Habitable crew environment",
        "Spacecraft, space station, lunar base, Mars base or pressurized rover: tap a planet, then one of them.",
    )
    body, place = place_picker()

shown_place = place or habitat
known = conditions(shown_place)
sources = known["sources"]


def range_inputs(name: str, key: str, bounds: tuple, unit: str, maximum: float) -> tuple:
    """Two number inputs (min, max) for a range; an empty input means no bound."""
    low_default, high_default = (float(v) if v is not None else None for v in bounds)
    low, high = st.columns(2)
    return (
        low.number_input(
            f"{name} min ({unit})", 0.0, maximum, low_default, format="%.1f", placeholder="no bound", key=f"{key}_min"
        ),
        high.number_input(
            f"{name} max ({unit})", 0.0, maximum, high_default, format="%.1f", placeholder="no bound", key=f"{key}_max"
        ),
    )


with form_column, st.container(key="ui_card_conditions", height="stretch"):
    card_title(
        f"Parameters · {label(shown_place)}",
        "Filled in by the environment, with their source. Every value stays editable.",
    )
    # One set of inputs per environment: choosing another one fills them again with its own values.
    oxygen = range_inputs("Oxygen", f"ui_oxygen_{shown_place}", known["oxygene_pct"], "%", 100.0)
    st.caption(f"Oxygen source: {source_name(sources['oxygene_pct'])}")
    pressure = range_inputs("Pressure", f"ui_pressure_{shown_place}", known["pression_kpa"], "kPa", 500.0)
    st.caption(f"Pressure source: {source_name(sources['pression_kpa'])}")
    gravity_default = known["gravite"]
    gravity = st.number_input(
        "Gravity (g)",
        0.0,
        1.0,
        float(gravity_default) if gravity_default is not None else None,
        format="%.3f",
        placeholder="unknown",
        key=f"ui_gravity_{shown_place}",
    )
    st.caption(f"Gravity source: {source_name(sources['gravite'])}")
    fuels = st.pills("Fuel (none chosen = all)", FUELS, selection_mode="multi", format_func=label, key="ui_fuels")
    air_flow = range_inputs("Air flow", "ui_air_flow", (None, None), "cm/s", 500.0)
    st.segmented_control("Pillar", PILIERS, format_func=label, key="ui_pillar")
    if shown_place == EARTH:
        st.caption(f"Earth is the reference: the other pages keep your space habitat, {label(habitat)}.")
    else:
        save_environment(
            habitat=shown_place,
            oxygene_pct=oxygen,
            pression_kpa=pressure,
            gravite=gravity,
            type_combustible=list(fuels),
            debit_air_cm_s=air_flow,
            pilier=st.session_state.get("ui_pillar"),
            profil=full_scenario()["profil"],
        )
        show_environment_in_sidebar()

scenario = full_scenario()

# --- Where NASA's tests sit against these conditions (lot D) -----------------------------------------------
with st.container(key="ui_card_ranking"):
    card_title("NASA tests against your conditions", "Each point is one NASA PSI test; those that match are coloured.")
    matching = getattr(comparateur, "tests_correspondants", None)
    chart = getattr(comparateur, "graphique_conditions", None)
    if matching is None or chart is None:
        st.info("The conditions chart and the test counter arrive with role D's work (lot D).")
    else:
        found = matching(tests, fiches, scenario)
        st.markdown(
            f"**{len(found):,} tests · {found['investigation_id'].nunique()} investigations · 0 in partial gravity**"
        )
        view = st.segmented_control(
            "View",
            ["pression", "debit"],
            default="pression",
            format_func={"pression": "Oxygen × pressure", "debit": "Oxygen × air flow"}.get,
            key="ui_chart_view",
            label_visibility="collapsed",
        )
        st.plotly_chart(chart(tests, fiches, scenario, vue=view or "pression"), key="ui_conditions_chart")

# --- The 3 most relevant investigations (lot C), and the assistant --------------------------------------
top_column, assistant_column = st.columns([7, 5], gap="medium")

with top_column, st.container(key="ui_card_compare", height="stretch"):
    card_title("The 3 most relevant investigations", f"For {label(scenario['habitat'])}.")
    best = les_plus_pertinentes(fiches, scenario).head(3)
    if best.empty:
        st.info("No investigation scores for this environment yet.")
    for _, fiche in best.iterrows():
        investigation_card(fiche)
    st.page_link("pages/recherche.py", label="All investigations, ranked and explained  ›")

with assistant_column, st.container(key="ui_card_assistant", height="stretch"):
    card_title("Questions?", "The assistant answers from the NASA investigation sheets and your environment.")
    mascot(
        "Ask me which NASA experiments matter for your crew environment.",
        ("pages/assistant.py", "Ask the assistant  ›"),
    )

footer(
    [
        "Flame in Freefall is a student project for the NASA Space Apps Challenge 2026. It is not affiliated "
        "with or endorsed by NASA. Pillar and fuel type are the team's classification; scores are the team's "
        "judgement, not NASA data.",
        "Experiments: NASA Physical Sciences Informatics. Planet maps: NASA Scientific Visualization Studio (Blue "
        "Marble; LRO LROC colour map of the Moon) and NASA 3D Resources (Mars). Moon and Mars scenes: NASA "
        "illustrations (Moon to Mars Transportation and Habitation, NASA logo removed; PIA23302). Station and "
        "spacecraft: simplified 3D shapes. The mascot is a drawing.",
    ]
)
