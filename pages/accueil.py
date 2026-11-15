"""Page 1 « My environment ». Owner: role F (Interface and 3D); the conditions chart comes from role D.

The page reads from the choice to its consequences (Ethan's ask of Sun 15 Nov):
 1. the environment: one button per place, then the sliders that refine it;
 2. two figures, right underneath: the tests that match, and the investigations behind them;
 3. the chart of NASA's tests against those conditions;
 4. what we don't know, then the three most relevant investigations;
 5. folded away: the hardware and the shape of the samples.
Every page of the site is in the menu bar at the top.
The habitat fills the values; what the user changes is kept in the scenario (lot A) for every page.
The file name stays `accueil.py` because `app.py` (role A) points to it.
"""

import streamlit as st

import flame.comparateur as comparateur
import flame.recherche as recherche
from flame.commun import (
    HABITAT_PERSONNALISE,
    INCONNU,
    charger_fiches,
    charger_table_psi,
    charger_tests,
    get_scenario,
)
from flame.ui import (
    EARTH,
    REFERENCE_PLACES,
    SPACESUIT,
    card_title,
    conditions,
    dashboard_header,
    environment_values,
    footer,
    grey_tests_in_the_box,
    how_to_use,
    investigation_details,
    label,
    left_the_place,
    place_buttons,
    save_environment,
    show_environment_in_sidebar,
    single_value_style,
    source_name,
    stat_tiles,
    style_conditions_chart,
)

# The three states of matter, and nothing else: one pill each. The team's `type_combustible` also holds
# "fumée" and "poussière", but what burns in those investigations is a solid — PSI's own wording is
# "smoke aerosol (overheated solids)", and the dust experiment disperses solid particles. They are folded
# into "solid" instead of getting a pill: a fourth state of matter would be invented, and leaving them out
# made "tick everything" cover less than "tick nothing" (Ethan, Sun 15 Nov).
FUEL_GROUPS = {"solide": ("solide", "fumée", "poussière"), "liquide": ("liquide",), "gaz": ("gaz",)}
# Slider scales. A handle left at the end of its scale means "no bound" on that side, so each scale must
# reach past the most extreme test: otherwise a test exists that no selection can ever include.
OXYGEN_SCALE = (0.0, 100.0)  # NASA's tests run from 12 to 85 %
PRESSURE_SCALE = (0.0, 520.0)  # up to 506.6 kPa in NASA's tests
AIR_FLOW_SCALE = (-10.0, 100.0)  # from -5.92 (flow against the flame) to 85.28 cm/s
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


def fuel_pills(fiches) -> list[str]:
    """The pills to offer: a state of matter that the data holds, plus any family no group covers.

    Ticking them all must cover every investigation. A family that exists in the data but belongs to no
    pill would be dropped by the filter with no way to get it back, so it gets a pill of its own.
    """
    familles = {comparateur.famille_combustible(valeur) for valeur in fiches["type_combustible"]} - {INCONNU}
    groupees = {famille for groupe in FUEL_GROUPS.values() for famille in groupe}
    offertes = [etat for etat, groupe in FUEL_GROUPS.items() if familles & set(groupe)]
    return offertes + sorted(familles - groupees)


def fuel_filter(chosen: list[str]) -> list[str]:
    """The families behind the chosen pills: "solid" also stands for the smoke and dust investigations."""
    return sorted({famille for choix in chosen for famille in FUEL_GROUPS.get(choix, (choix,))})


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
        "One button per atmosphere: places that share their conditions share a button. "
        "Earth is the reference, not a habitat.",
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
    # Two buttons only, because PSI has no test in between. The spacesuit has no gravity of its own:
    # the statement gives none, and nothing is invented here.
    if values["gravite"] is None:
        own_gravity = f"{title_label(shown_place)}: not given by the statement."
    elif gravity_choice(values["gravite"]) is None:
        own_gravity = f"{title_label(shown_place)}: {float(values['gravite']):g} g, which no PSI test was run at."
    else:
        own_gravity = f"{title_label(shown_place)}: {float(values['gravite']):g} g."
    # PSI's test tables have no gravity column: the flights ran in microgravity, and only Saffire-II's rows
    # also record a 1-g burn length. Gravity therefore filters no test, and the page says so.
    st.caption(
        "NASA's PSI tests were run in microgravity (0 g), in orbit; only a few rows also record a result "
        f"at 1 g. Gravity does not filter the tests counted here. {own_gravity}"
    )
    pressure = from_slider(st.slider("P (kPa)", *PRESSURE_SCALE, step=0.1, key="ui_pressure"), PRESSURE_SCALE)
    fuels = st.pills(
        "Fuel (none chosen = all)", fuel_pills(fiches), selection_mode="multi", format_func=label, key="ui_fuels"
    )
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
    "type_combustible": fuel_filter(list(fuels)),
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

matching = comparateur.tests_correspondants(tests, fiches, scenario)

# --- Level 2: the figures, right under the choice that produces them ---------------------------------------
# Each tile says what it counts: the first figure was the tests whose pressure is recorded, which read as
# a missing third of the data (Ethan, Sun 15 Nov). The whole count comes first, the sure ones underneath.
sure = matching[matching["pression_notee"]]
ran_tests = tests["investigation_id"].nunique()
without_tests = len(fiches) - ran_tests
if oxygen == (None, None) and pressure == (None, None):
    # No atmosphere given (Mars base): every test would "match", so no count is shown.
    stat_tiles(
        [
            ("—", "Tests in your environment", "no oxygen or pressure given"),
            ("—", "Investigations", "none can be placed"),
        ],
        note="Give an oxygen or a pressure range with the sliders to see the NASA tests that match it.",
        compact=True,
    )
else:
    stat_tiles(
        [
            (f"{len(matching):,}", "Tests in your environment", f"{len(sure):,} with pressure recorded"),
            (f"{matching['investigation_id'].nunique()}", "Investigations", f"of the {ran_tests} that ran tests"),
        ],
        note=(
            f"{without_tests} of the {len(fiches)} investigations ran no test of their own: they reanalyse "
            "data from other flights, so no test row can be counted for them."
        ),
        compact=True,
    )

# --- Level 3: NASA's tests against those conditions --------------------------------------------------------
with st.container(key="ui_card_ranking"):
    card_title(
        "NASA tests against your conditions",
        "Each point is one NASA PSI test; the ones inside your environment are circled. Dotted: the Earth "
        "and Moon zones. Star: the spacesuit. Hover a shape to see where its figures come from.",
    )
    view = st.segmented_control(
        "View",
        ["pression", "debit"],
        default="pression",
        format_func={"pression": "O₂ × pressure", "debit": "O₂ × air flow"}.get,
        key="ui_chart_view",
    )
    view = view or "pression"
    chart = style_conditions_chart(comparateur.graphique_conditions(tests, fiches, scenario, vue=view), scenario, view)
    st.plotly_chart(chart, key="ui_conditions_chart")
    # The orange box is your oxygen range and the range of this view's other axis. A circled test is always
    # inside it; a test inside it stays grey only when a filter that is not on the axes excludes it.
    if grey_tests_in_the_box(chart):
        st.caption(grey_tests_in_the_box(chart))
    st.caption("No test records oxygen, pressure and air flow together, so the two views share the oxygen axis.")

# --- Level 4: what we don't know, then the 3 most relevant investigations ---------------------------------
with st.container(key="ui_card_gaps"):
    card_title("What we don't know", "Where NASA's data stops, for this environment.")
    # Role C's visuals: tests by fuel in your conditions, then the oxygen and pressure rulers.
    recherche.afficher_ce_quon_ne_sait_pas(fiches, tests, scenario, cle="ui")

best = recherche.les_plus_pertinentes(fiches, scenario).head(3)
with st.container(key="ui_card_compare"):
    card_title("The 3 most relevant investigations", f"For {environment_name}.")
    if best.empty:
        st.info("No investigation scores for this environment yet.")
    # Each one with what the experiment studied and why it matters here (role C's `descriptif`).
    for rank, (_, fiche) in enumerate(best.iterrows(), start=1):
        investigation_details(fiche, recherche.descriptif(fiche, scenario, tests), rank, environment_name)
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


footer(
    [
        "Flame in Freefall is a student project for the NASA Space Apps Challenge 2026. It is not affiliated "
        "with or endorsed by NASA. Fuel types are the team's classification; scores are the team's judgement, "
        "not NASA data.",
        "Experiments: NASA Physical Sciences Informatics. Button icons: Google Material Symbols (Apache 2.0). "
        "The mascot and the space background are original drawings.",
    ]
)
