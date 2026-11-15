"""Page 1 « My environment ». Owner: role F (Interface and 3D); the conditions chart comes from role D.

Sketch 1 of the team's whiteboard, built in five levels so that one thing is read first (hierarchy,
Ethan's ask of Sat 14 Nov):
 1. (the verdict banner is removed at Mathéo's request, Sun 15 Nov);
 2. three figures: tests, investigations, and how many are independent measurements;
 3. the environment (one button per place, then the sliders) and where NASA's tests sit on the oxygen axis;
 4. what NASA's tests show, what we don't know, then the three most relevant investigations;
 5. folded away: the detailed chart, the hardware and the shape of the samples.
Every page of the site is in the menu bar at the top.
The habitat fills the values; what the user changes is kept in the scenario (lot A) for every page.
The file name stays `accueil.py` because `app.py` (role A) points to it.
"""

import streamlit as st

import flame.comparateur as comparateur
import flame.recherche as recherche
from flame.commun import HABITAT_PERSONNALISE, charger_fiches, charger_table_psi, charger_tests, get_scenario
from flame.ui import (
    EARTH,
    REFERENCE_PLACES,
    SPACESUIT,
    card_title,
    chatbot_button,
    conditions,
    dashboard_header,
    environment_values,
    footer,
    how_to_use,
    investigation_details,
    label,
    left_the_place,
    outcomes_card,
    place_buttons,
    save_environment,
    show_environment_in_sidebar,
    single_value_style,
    source_name,
    stat_tiles,
    style_conditions_chart,
)

FUELS = ["solide", "liquide", "gaz"]  # the contract's fuel types; none chosen = all
# Slider scales. A handle left at the end of its scale means "no bound" on that side.
OXYGEN_SCALE = (0.0, 100.0)
PRESSURE_SCALE = (0.0, 350.0)  # NASA's tests go up to about 306 kPa
AIR_FLOW_SCALE = (0.0, 100.0)  # up to 85 cm/s in NASA's tests
# Gravity takes only a few values in the crew environments: one button each (lot A's habitats).
# Partial gravity (Moon 0.165 g, Mars 0.38 g) has no button: NASA's PSI tests have none. The Moon base,
# the rover and the Mars base keep their own gravity, with no button selected.
GRAVITY_CHOICES = {0.0: "0 g", 1.0: "1 g"}
# The three hardware families the challenge statement names, in the order it names them.
HARDWARE_ORDER = ["ACME gas burner", "MDCA droplet", "MSG flow duct"]


def gravity_choice(value: float | None) -> float | None:
    """The button of a gravity value, or None when it has no button (Moon or Mars)."""
    value = value or 0.0
    return next((choice for choice in GRAVITY_CHOICES if abs(choice - value) < 1e-9), None)


def title_label(place: str) -> str:
    """The English name of a place with a capital first letter, for a title ("spacesuit" gives "Spacesuit")."""
    name = label(place)
    return f"{name[:1].upper()}{name[1:]}"


fiches = charger_fiches()
tests = charger_tests()
habitat = st.session_state.get("ui_habitat", get_scenario()["habitat"])

dashboard_header(
    "Flame in Freefall · Fire-safety dashboard",
    "Describe your habitable crew environment: see where NASA's microgravity combustion data stops.",
    [f"{len(fiches)} NASA investigations", f"{len(tests):,} test rows", "Source: NASA PSI"],
    eyebrow="My environment",
)
how_to_use()  # a light cover: how the dashboard works, in four steps (can be folded away)
# Level 2 is printed at the top but needs the environment chosen below: it is filled in later.
figures_zone = st.container()


def to_slider(bounds: tuple, scale: tuple) -> tuple:
    """A range (min, max) with None for "no bound", as the two handles of a slider."""
    low, high = bounds or (None, None)
    return (scale[0] if low is None else float(low), scale[1] if high is None else float(high))


def from_slider(handles: tuple, scale: tuple) -> tuple:
    """The two handles of a slider as a range: a handle at the end of the scale means "no bound"."""
    low, high = handles
    return (None if low <= scale[0] else low, None if high >= scale[1] else high)


# --- Level 3: the crew environment, its sliders, and where NASA's tests sit --------------------------------
# The place whose button was clicked last (the scenario's habitat until the first click). It stays the
# place of the sliders even when the user's values leave its range and the environment becomes custom.
if habitat != HABITAT_PERSONNALISE:
    st.session_state.setdefault("ui_place", habitat)
shown_place = st.session_state.get("ui_place") or habitat
# Back from another page with a custom environment: the sliders take the user's values, not the place's.
was_custom = habitat == HABITAT_PERSONNALISE and shown_place not in REFERENCE_PLACES
values = environment_values(HABITAT_PERSONNALISE if was_custom else shown_place)
sources = conditions(shown_place)["sources"]

# The sliders start from the scenario: what the user typed stays, even after a visit to another page.
# They take the habitat's values again only when the habitat changes.
if st.session_state.get("ui_form_place") != shown_place or "ui_oxygen" not in st.session_state:
    st.session_state["ui_oxygen"] = to_slider(values["oxygene_pct"], OXYGEN_SCALE)
    st.session_state["ui_pressure"] = to_slider(values["pression_kpa"], PRESSURE_SCALE)
    st.session_state["ui_gravity"] = gravity_choice(values["gravite"])
    st.session_state["ui_fuels"] = list(values["type_combustible"])
    st.session_state["ui_air_flow"] = to_slider(values["debit_air_cm_s"], AIR_FLOW_SCALE)
    st.session_state["ui_form_place"] = shown_place

# Oxygen or pressure moved out of the place's range: the place is no longer selected, the environment is custom.
custom = left_the_place(
    shown_place, {"oxygene_pct": ("ui_oxygen", OXYGEN_SCALE), "pression_kpa": ("ui_pressure", PRESSURE_SCALE)}
)
shown_name = "Custom" if custom else title_label(shown_place)
environment_name = "your custom environment" if custom else title_label(shown_place)  # inside a sentence

picker_column, sliders_column = st.columns([7, 5], gap="medium")

with picker_column, st.container(key="ui_card_destination", height="stretch"):
    card_title(
        "Habitable crew environment",
        "Space station, spacecraft, lunar base, pressurized rover or Mars base. "
        "Earth and the spacesuit are references, not habitats.",
    )
    place_buttons(habitat, selected=not custom)
    if custom:
        st.caption(
            f"Your oxygen or pressure is outside the range of {title_label(shown_place)}: no environment is "
            "selected. Move the sliders back, or click a button, to return to one."
        )

with sliders_column, st.container(key="ui_card_conditions", height="stretch"):
    card_title(f"Parameters · {shown_name}", "Filled in by the environment. Move a slider to change it.")
    oxygen = from_slider(st.slider("O₂ (%)", *OXYGEN_SCALE, step=0.5, key="ui_oxygen"), OXYGEN_SCALE)
    gravity = st.segmented_control(
        "g (gravity)", list(GRAVITY_CHOICES), format_func=GRAVITY_CHOICES.get, key="ui_gravity"
    )
    if gravity is None:  # no button chosen (Moon, Mars): keep the environment's own gravity
        gravity = float(values["gravite"] or 0.0)
    # The spacesuit has no gravity of its own: the statement gives none, and nothing is invented here.
    own_gravity = "not given" if values["gravite"] is None else f"{float(values['gravite']):g} g"
    st.caption(f"0 g: spacecraft and station · 1 g: Earth. {title_label(shown_place)}: {own_gravity}.")
    # Gravity does not filter the tests: PSI's test tables have no gravity column, and the flight
    # investigations ran in microgravity. Saying so avoids reading 0 g tests as Moon, Mars or Earth tests.
    if gravity > 0:
        st.caption(
            f"NASA's PSI tables hold no test row at {gravity:g} g: the tests counted on this page were run in "
            "microgravity (0 g). Gravity changes the notes below, not the tests."
        )
    pressure = from_slider(st.slider("P (kPa)", *PRESSURE_SCALE, step=0.1, key="ui_pressure"), PRESSURE_SCALE)
    fuels = st.pills("Fuel (none chosen = all)", FUELS, selection_mode="multi", format_func=label, key="ui_fuels")
    air_flow = from_slider(
        st.slider("Air flow (cm/s, optional)", *AIR_FLOW_SCALE, step=0.5, key="ui_air_flow"), AIR_FLOW_SCALE
    )
    # Each value keeps its source visible: the statement gives some of them, the team assumes the others.
    # Once the environment is custom, oxygen and pressure are the user's own.
    oxygen_source = "your choice" if custom else source_name(sources["oxygene_pct"])
    pressure_source = "your choice" if custom else source_name(sources["pression_kpa"])
    st.caption(
        f"O₂ {oxygen_source} · pressure {pressure_source} · "
        f"gravity {source_name(sources['gravite'])} · fuel your choice. "
        "A handle left at the end of its scale means no bound on that side."
    )
    single_value_style(["ui_oxygen", "ui_pressure", "ui_air_flow"])  # one number when both handles meet

environment = {
    "oxygene_pct": oxygen,
    "pression_kpa": pressure,
    "gravite": gravity,
    "type_combustible": list(fuels),
    "debit_air_cm_s": air_flow,
}
# The habitat the other pages read: the place, or "Personnalisé" once the values left its range.
scenario_place = HABITAT_PERSONNALISE if custom else shown_place
if shown_place not in REFERENCE_PLACES:
    st.session_state["ui_habitat"] = scenario_place  # the top bar keeps it on the other pages
    save_environment(habitat=scenario_place, **environment)
    show_environment_in_sidebar()
# The scenario as the other pages read it. A reference place is explored here without replacing the habitat.
scenario = {**get_scenario(), "habitat": scenario_place, **environment}

if shown_place == EARTH:
    st.caption(f"Earth is the reference: the other pages keep your space habitat, {label(habitat)}.")
elif shown_place == SPACESUIT:
    st.caption(
        "The spacesuit is the reference at the other end: 100 % oxygen at 4.3 psi, the statement's lower "
        f"bound that explains the lunar atmosphere. The other pages keep your habitat, {label(habitat)}."
    )

frontiere = recherche.frontiere_des_solides(fiches, tests)
matching = comparateur.tests_correspondants(tests, fiches, scenario)

with st.container(key="ui_card_ranking"):
    card_title(
        "Where NASA's tests sit on the oxygen axis",
        "Grey: every test whose oxygen is recorded. Orange: the tests inside your environment.",
    )
    st.plotly_chart(
        comparateur.graphique_repartition(tests, fiches, scenario, frontiere=frontiere["reel"]),
        key="ui_distribution_chart",
    )
    with st.expander("Detailed view: oxygen × pressure, oxygen × air flow"):
        st.caption(
            "Each point is one NASA PSI test. Dotted: the Earth and Moon zones. Star: the spacesuit. "
            "No test records oxygen, pressure and air flow together, so the two views share the oxygen axis."
        )
        view = st.segmented_control(
            "View",
            ["pression", "debit"],
            default="pression",
            format_func={"pression": "O₂ × pressure", "debit": "O₂ × air flow"}.get,
            key="ui_chart_view",
        )
        view = view or "pression"
        st.plotly_chart(
            style_conditions_chart(comparateur.graphique_conditions(tests, fiches, scenario, vue=view), scenario, view),
            key="ui_conditions_chart",
        )

# --- Level 2: the three figures ---------------------------------------------------------------------------
independance = recherche.independance(matching["investigation_id"].unique())
with figures_zone:
    sure = matching[matching["pression_notee"]]
    if oxygen == (None, None) and pressure == (None, None):
        # No atmosphere given (Mars base): every test would "match", so no count is shown.
        stat_tiles(
            [
                ("—", "Tests in your environment", "no oxygen or pressure given"),
                ("—", "Investigations", "none can be placed"),
                ("—", "Independent measurements", "none can be placed"),
            ],
            note="Give an oxygen or a pressure range with the sliders to see the NASA tests that match it.",
            compact=True,
        )
    else:
        unsure = len(matching) - len(sure)
        stat_tiles(
            [
                (
                    f"{len(matching):,}",
                    "Test rows in your environment",
                    f"{unsure:,} of them with no recorded pressure" if unsure else "pressure recorded",
                ),
                (f"{matching['investigation_id'].nunique()}", "Investigations", "that ran them"),
                (f"{independance['independantes']}", "Independent measurements", "reanalyses folded in"),
            ],
            note=independance["phrase"],
            compact=True,
        )

# --- Level 4: what the tests show, what we don't know, then the 3 most relevant investigations ------------
with st.container(key="ui_card_outcomes"):
    card_title(
        "Can a flame burn in these conditions?",
        f"What the NASA tests that match {environment_name} show.",
        tag="What NASA's tests show",
    )
    outcomes_card(matching, scenario)

# What we don't know comes first, as a full-width banner; then the 3 most relevant investigations.
with st.container(key="ui_card_gaps"):
    card_title("What we don't know", "Where NASA's data stops, for this environment.")
    for sentence in recherche.ce_quon_ne_sait_pas(fiches, tests, scenario):
        st.markdown(f"- {sentence}")

best = recherche.les_plus_pertinentes(fiches, scenario).head(3)
with st.container(key="ui_card_compare"):
    card_title("The 3 most relevant investigations", f"For {environment_name}.")
    if best.empty:
        st.info("No investigation scores for this environment yet.")
    # Each one with what the experiment studied and why it matters here (role C's `descriptif`).
    for rank, (_, fiche) in enumerate(best.iterrows(), start=1):
        investigation_details(fiche, recherche.descriptif(fiche, scenario, tests), rank, environment_name)
    # The 3 compared with each other (role C): where they agree, where to be careful.
    compared = recherche.synthese_des_plus_pertinentes(fiches, tests, scenario)
    if compared and compared["investigations"]:
        agree_column, careful_column = st.columns(2, gap="medium")
        with agree_column:
            st.markdown("**Where they agree**")
            for sentence in compared["accords"] or ["No common fuel, material or oxygen level."]:
                st.markdown(f"- {sentence}")
        with careful_column:
            st.markdown("**Be careful**")
            for sentence in compared["attention"] or ["Nothing to flag."]:
                st.markdown(f"- {sentence}")
    with st.container(key="ui_analyse"):
        # The orange pill of sketch 1 of the whiteboard, kept as the page's main action.
        if st.button("ANALYSE ALL 24", key="ui_analyse_button"):
            st.switch_page("pages/recherche.py")

# --- Level 5: folded away — the hardware and the shape of the samples -------------------------------------
psi_investigations = charger_table_psi("investigations")
psi_tests = charger_table_psi("tests")
with st.expander("Hardware and samples: what these tests were run with"):
    if psi_investigations.empty:
        st.info("The PSI investigations table is not in `data/psi/` yet.")
    else:
        st.caption(
            "The statement groups the experiments by the hardware they share: results from the same "
            "hardware can be read side by side, results from different hardware compare questions, not numbers."
        )
        familles = psi_investigations.dropna(subset=["hardware_family"]).groupby("hardware_family")
        rang = {famille: index for index, famille in enumerate(HARDWARE_ORDER)}
        for famille, groupe in sorted(familles, key=lambda item: rang.get(item[0], len(HARDWARE_ORDER))):
            acronymes = ", ".join(sorted(str(nom) for nom in groupe["acronym"].dropna()))
            st.markdown(f"**{famille}** · {len(groupe)} investigation(s){f' — {acronymes}' if acronymes else ''}")
            installations = sorted({str(lieu) for lieu in groupe["facility"].dropna()})
            if installations:
                st.caption(" · ".join(installations))
        if not psi_tests.empty and not best.empty:
            st.markdown("**Shape and size of the samples, for the three investigations above**")
            for _, fiche in best.iterrows():
                formes = comparateur.frequents(psi_tests, fiche["id"], "fuel_form")
                detail = ", ".join(f"{forme} ({nombre} rows)" for forme, nombre in formes) or "not recorded"
                st.markdown(f"- **{fiche['nom']}** — {detail}")

chatbot_button("pages/assistant.py")

footer(
    [
        "Flame in Freefall is a student project for the NASA Space Apps Challenge 2026. It is not affiliated "
        "with or endorsed by NASA. Fuel types are the team's classification; scores are the team's judgement, "
        "not NASA data.",
        "Experiments: NASA Physical Sciences Informatics. Button icons: Google Material Symbols (Apache 2.0). "
        "The mascot and the space background are original drawings.",
    ]
)
