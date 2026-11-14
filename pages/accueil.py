"""Page 1 « My environment ». Owner: role F (Interface and 3D); the conditions chart comes from role D.

Layout of sketch 1 of the team's whiteboard: the crew environment and its sliders (O₂, g, P, fuel), four
cards with the values and their sources, the O₂ × P chart of NASA's tests, an ANALYSE button, a chatbot icon.
The habitat fills the values; what the user changes is kept in the scenario (lot A) for every page.
The file name stays `accueil.py` because `app.py` (role A) points to it.
"""

import streamlit as st

import flame.comparateur as comparateur
import flame.recherche as recherche
from flame.commun import charger_fiches, charger_tests, get_scenario
from flame.ui import (
    EARTH,
    bounds_text,
    card_title,
    chatbot_button,
    conditions,
    dashboard_header,
    environment_values,
    footer,
    investigation_card,
    label,
    place_picker,
    save_environment,
    show_environment_in_sidebar,
    source_name,
    stat_tiles,
)

FUELS = ["solide", "liquide", "gaz"]  # the contract's fuel types; none chosen = all
# Slider scales. A handle left at the end of its scale means "no bound" on that side.
OXYGEN_SCALE = (0.0, 100.0)
PRESSURE_SCALE = (0.0, 350.0)  # NASA's tests go up to about 306 kPa
AIR_FLOW_SCALE = (0.0, 100.0)  # up to 85 cm/s in NASA's tests

fiches = charger_fiches()
tests = charger_tests()
habitat = st.session_state.get("ui_habitat", get_scenario()["habitat"])

dashboard_header(
    "My environment",
    "Describe your habitable crew environment: see which NASA microgravity combustion tests apply to it.",
    [f"{len(fiches)} NASA investigations", f"{len(tests):,} test rows", "Source: NASA PSI"],
)


def to_slider(bounds: tuple, scale: tuple) -> tuple:
    """A range (min, max) with None for "no bound", as the two handles of a slider."""
    low, high = bounds or (None, None)
    return (scale[0] if low is None else float(low), scale[1] if high is None else float(high))


def from_slider(handles: tuple, scale: tuple) -> tuple:
    """The two handles of a slider as a range: a handle at the end of the scale means "no bound"."""
    low, high = handles
    return (None if low <= scale[0] else low, None if high >= scale[1] else high)


# --- The crew environment, and its sliders -----------------------------------------------------------------
picker_column, sliders_column = st.columns([7, 5], gap="medium")

with picker_column, st.container(key="ui_card_destination", height="stretch"):
    card_title(
        "Habitable crew environment",
        "Spacecraft, space station, lunar base, Mars base or pressurized rover: tap a planet, then one of them.",
    )
    body, place = place_picker()

shown_place = place or habitat
sources = conditions(shown_place)["sources"]
values = environment_values(shown_place)

# The sliders start from the scenario: what the user typed stays, even after a visit to another page.
# They take the habitat's values again only when the habitat changes.
if st.session_state.get("ui_form_place") != shown_place or "ui_oxygen" not in st.session_state:
    st.session_state["ui_oxygen"] = to_slider(values["oxygene_pct"], OXYGEN_SCALE)
    st.session_state["ui_pressure"] = to_slider(values["pression_kpa"], PRESSURE_SCALE)
    st.session_state["ui_gravity"] = float(values["gravite"] or 0.0)
    st.session_state["ui_fuels"] = list(values["type_combustible"])
    st.session_state["ui_air_flow"] = to_slider(values["debit_air_cm_s"], AIR_FLOW_SCALE)
    st.session_state["ui_form_place"] = shown_place

with sliders_column, st.container(key="ui_card_conditions", height="stretch"):
    card_title(f"Parameters · {label(shown_place)}", "Filled in by the environment. Move a slider to change it.")
    oxygen = from_slider(st.slider("O₂ (%)", *OXYGEN_SCALE, step=0.5, key="ui_oxygen"), OXYGEN_SCALE)
    gravity = st.slider("g (gravity, in g)", 0.0, 1.0, step=0.005, format="%.3f", key="ui_gravity")
    pressure = from_slider(st.slider("P (kPa)", *PRESSURE_SCALE, step=0.1, key="ui_pressure"), PRESSURE_SCALE)
    fuels = st.pills("Fuel (none chosen = all)", FUELS, selection_mode="multi", format_func=label, key="ui_fuels")
    air_flow = from_slider(
        st.slider("Air flow (cm/s, optional)", *AIR_FLOW_SCALE, step=0.5, key="ui_air_flow"), AIR_FLOW_SCALE
    )
    st.caption("A handle left at the end of its scale means no bound on that side.")

environment = {
    "oxygene_pct": oxygen,
    "pression_kpa": pressure,
    "gravite": gravity,
    "type_combustible": list(fuels),
    "debit_air_cm_s": air_flow,
}
if shown_place != EARTH:
    save_environment(habitat=shown_place, **environment)
    show_environment_in_sidebar()
# The scenario as the other pages will read it (the same dict once lot A is on main).
scenario = {**get_scenario(), "habitat": shown_place, **environment}

# --- Four cards, and the chart of NASA's tests -------------------------------------------------------------
cards_column, chart_column = st.columns([4, 8], gap="medium")

with cards_column, st.container(key="ui_card_assistant", height="stretch"):
    card_title("Your environment", "Each value with its source.")
    stat_tiles(
        [
            (bounds_text("", oxygen, "%"), "Oxygen", source_name(sources["oxygene_pct"])),
            (bounds_text("", pressure, "kPa"), "Pressure", source_name(sources["pression_kpa"])),
            (f"{gravity:g} g", "Gravity", source_name(sources["gravite"])),
            (label(";".join(fuels)) if fuels else "All", "Fuel", "your choice"),
        ],
        compact=True,
        grid=True,
    )
    if shown_place == EARTH:
        st.caption(f"Earth is the reference: the other pages keep your space habitat, {label(habitat)}.")

with chart_column, st.container(key="ui_card_ranking", height="stretch"):
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
            format_func={"pression": "O₂ × pressure", "debit": "O₂ × air flow"}.get,
            key="ui_chart_view",
            label_visibility="collapsed",
        )
        st.plotly_chart(chart(tests, fiches, scenario, vue=view or "pression"), key="ui_conditions_chart")
    with st.container(key="ui_analyse"):
        if st.button("ANALYSE", key="ui_analyse_button"):
            st.session_state["ui_analysed"] = True

# --- After ANALYSE: the 3 most relevant investigations, and what we don't know -----------------------------
if st.session_state.get("ui_analysed"):
    best_column, gaps_column = st.columns([7, 5], gap="medium")
    with best_column, st.container(key="ui_card_compare", height="stretch"):
        card_title("The 3 most relevant investigations", f"For {label(shown_place)}.")
        best = recherche.les_plus_pertinentes(fiches, scenario).head(3)
        if best.empty:
            st.info("No investigation scores for this environment yet.")
        for _, fiche in best.iterrows():
            investigation_card(fiche)
        st.page_link("pages/recherche.py", label="All investigations, ranked and explained  ›")
    with gaps_column, st.container(key="ui_card_gaps", height="stretch"):
        card_title("What we don't know", "Where NASA's data stops, for this environment.")
        gaps = getattr(recherche, "ce_quon_ne_sait_pas", None)
        if gaps is None:
            st.info("The list of data gaps arrives with role C's work (lot C).")
        else:
            for sentence in gaps(fiches, tests, scenario):
                st.markdown(f"- {sentence}")

chatbot_button("pages/assistant.py")

footer(
    [
        "Flame in Freefall is a student project for the NASA Space Apps Challenge 2026. It is not affiliated "
        "with or endorsed by NASA. Fuel types are the team's classification; scores are the team's judgement, "
        "not NASA data.",
        "Experiments: NASA Physical Sciences Informatics. Planet maps: NASA Scientific Visualization Studio (Blue "
        "Marble; LRO LROC colour map of the Moon) and NASA 3D Resources (Mars). Moon and Mars scenes: NASA "
        "illustrations (Moon to Mars Transportation and Habitation, NASA logo removed; PIA23302). Station and "
        "spacecraft: simplified 3D shapes. The mascot is a drawing.",
    ]
)
