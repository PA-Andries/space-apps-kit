"""The site's single page: an interactive dashboard. Owner: role F (Interface and 3D).

The file name stays `accueil.py` because `app.py` (role A) points to it. The dashboard reuses the
exported functions of the other roles: `rechercher` (C, ranking), the comparator (D) and `repondre` (E).
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from flame.assistant import repondre
from flame.commun import PILIERS, charger_fiches, charger_tests, get_scenario
from flame.comparateur import carte, resume
from flame.recherche import detail_du_score, filtrer, rechercher, valeurs_possibles
from flame.ui import (
    EARTH,
    body_of,
    card_title,
    dashboard_header,
    footer,
    investigation_card,
    label,
    mascot,
    place_conditions,
    place_picker,
    stat_tiles,
)

AXIS_NAMES = {"oxygene_pct": "Oxygen (%)", "pression_kpa": "Pressure (kPa)", "debit_air_cm_s": "Air flow (cm/s)"}
COLOURS = ["#e0662a", "#2563eb", "#15803d"]  # one per compared investigation
MODELLING_TAG = "Objective 2 · Data for flammability modelling"
SCORE_TITLES = {"critere": "Criterion", "points": "Points", "maximum": "Out of", "explication": "Why"}

fiches = charger_fiches()
tests = charger_tests()
scenario = get_scenario()
habitat = scenario["habitat"]

dashboard_header(
    "Flame in Freefall",
    "Summarizing, ranking and interpreting NASA microgravity combustion experiments for fire safety "
    "in habitable crew environments.",
    [f"{len(fiches)} NASA investigations", f"{len(tests):,} test rows", "Source: NASA PSI"],
)

# --- Row 1: the habitable crew environment, and the parameters it sets ----------------------------------------
destination, conditions_column = st.columns([7, 5], gap="medium")

with destination, st.container(key="ui_card_destination", height="stretch"):
    card_title(
        "Habitable crew environment",
        "Spacecraft, space station, lunar base, Mars base or pressurized rover: tap a planet, then one of them.",
    )
    body, place = place_picker()

shown_place = place or habitat
shown_body = body or body_of(shown_place)
conditions = place_conditions(shown_place, shown_body)
known = conditions["oxygen_pct"] is not None
statement_oxygen = float(conditions["oxygen_pct"]) if known else None
statement_pressure = float(conditions["pressure_kpa"]) if known else None

with conditions_column, st.container(key="ui_card_conditions", height="stretch"):
    card_title(
        f"Environment parameters · {label(shown_place)}",
        "Set by the crew environment, and editable. They refine the investigations below.",
        tag="Objective 3 · Future fire-safety equipment",
    )
    st.segmented_control("Need", PILIERS, format_func=label, key="ui_pillar", label_visibility="collapsed")
    # One set of inputs per environment: choosing another environment fills them again with its own values.
    oxygen_column, pressure_column = st.columns(2)
    oxygen = oxygen_column.number_input(
        "Cabin oxygen (%)",
        min_value=0.0,
        max_value=100.0,
        value=statement_oxygen,
        step=1.0,
        format="%.1f",
        placeholder="not given",
        key=f"ui_oxygen_{shown_place}",
    )
    pressure = pressure_column.number_input(
        "Cabin pressure (kPa)",
        min_value=0.0,
        max_value=200.0,
        value=statement_pressure,
        step=1.0,
        format="%.1f",
        placeholder="not given",
        key=f"ui_pressure_{shown_place}",
    )
    st.caption(
        "Prefilled from the challenge statement."
        if known
        else "The challenge statement gives no cabin atmosphere here: type values to filter by them."
    )
    oxygen_margin, pressure_margin = st.columns(2)
    oxygen_tolerance = oxygen_margin.slider("Oxygen match (± points)", 1, 10, 5, key="ui_oxygen_tolerance")
    pressure_tolerance = pressure_margin.slider("Pressure match (± kPa)", 5, 50, 20, key="ui_pressure_tolerance")
    fuels = st.pills(
        "Fuel",
        valeurs_possibles(fiches, "type_combustible"),
        selection_mode="multi",
        format_func=label,
        key="ui_fuels",
    )
    only_near = st.toggle(
        "Only investigations with tests near these conditions",
        value=known,
        key=f"ui_only_near_{shown_place}",
        disabled=oxygen is None and pressure is None,
    )
    stat_tiles([(f"{conditions['gravity']:g} g", "Gravity here")], compact=True)
    if shown_place == EARTH:
        st.caption(f"Earth is the reference: the score uses your space habitat, {label(habitat)}.")


def tests_near(oxygen: float | None, pressure: float | None) -> pd.Series:
    """For each investigation, how many NASA test rows were run close to the given oxygen and pressure."""
    keep = pd.Series(True, index=tests.index)
    if oxygen is not None:
        keep &= (tests["oxygene_pct"] - oxygen).abs() <= oxygen_tolerance
    if pressure is not None:
        keep &= (tests["pression_kpa"] - pressure).abs() <= pressure_tolerance
    return tests[keep].groupby("investigation_id").size()


# --- Row 2: the experiments that matter most, and the assistant --------------------------------------------
ranking_column, assistant_column = st.columns([7, 5], gap="medium")

with ranking_column, st.container(key="ui_card_ranking", height="stretch"):
    card_title(
        "Most useful investigations for this environment",
        f"Ranked for {label(habitat)} · {label(scenario['pilier'])}. Select rows to compare them below.",
        tag="Objective 1 · Rank by crew environment",
    )
    question = st.text_input(
        "Search", placeholder="Search: fabric, extinction, smoke…", key="ui_search", label_visibility="collapsed"
    )
    has_conditions = oxygen is not None or pressure is not None
    near = tests_near(oxygen, pressure) if has_conditions else pd.Series(dtype=int)
    candidates = filtrer(fiches, types_combustible=fuels)
    if only_near and has_conditions:
        candidates = candidates[candidates["id"].isin(near.index)]
    ranked = rechercher(question, candidates, scenario)
    ranked = ranked.assign(near=ranked["id"].map(near).fillna(0).astype(int))
    filters = [label(shown_place), label(scenario["pilier"])]
    if oxygen is not None:
        filters.append(f"O₂ {oxygen:g} ± {oxygen_tolerance} %")
    if pressure is not None:
        filters.append(f"{pressure:g} ± {pressure_tolerance} kPa")
    if fuels:
        filters.append(", ".join(label(fuel) for fuel in fuels))
    st.caption(f"{len(ranked)} of {len(fiches)} investigations · " + " · ".join(filters))
    table = ranked.assign(pilier=ranked["pilier"].map(label), type_combustible=ranked["type_combustible"].map(label))[
        ["id", "nom", "pilier", "type_combustible", "near", "nb_tests", "score"]
    ]
    picked = st.dataframe(
        table,
        hide_index=True,
        height=min(470, 38 + 35 * max(len(table), 1)),
        on_select="rerun",
        selection_mode="multi-row",
        key="ui_ranking",
        column_config={
            "id": "PSI id",
            "nom": "Investigation",
            "pilier": "Pillar",
            "type_combustible": "Fuel",
            "near": st.column_config.NumberColumn(
                "Tests near", format="%d", help="NASA test rows run within the oxygen and pressure margins"
            ),
            "nb_tests": st.column_config.NumberColumn("Tests", format="%d"),
            "score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%d"),
        },
    )
    chosen_ids = list(table.iloc[picked.selection.rows]["id"])[:3]
    if ranked.empty:
        st.info("No investigation matches. Try another word.")


def oxygen_range_chart(fiches, ids: list[str], habitat_oxygen: float | None, habitat_name: str) -> None:
    """The oxygen range each investigation covered (from its NASA sheet), with the habitat's level."""
    rows = fiches.set_index("id").loc[ids].dropna(subset=["oxygene_min", "oxygene_max"])
    if rows.empty:
        st.info("No oxygen range is recorded for these investigations.")
        return
    figure = go.Figure(
        go.Bar(
            y=rows["nom"],
            x=rows["oxygene_max"] - rows["oxygene_min"],
            base=rows["oxygene_min"],
            orientation="h",
            marker_color=COLOURS[: len(rows)],
            hovertemplate="%{y}: %{base:g} to %{x:g} %<extra></extra>",
        )
    )
    if habitat_oxygen is not None:
        figure.add_vline(x=habitat_oxygen, line_dash="dash", annotation_text=f"{habitat_name} oxygen")
    figure.update_layout(
        height=60 + 70 * len(rows),
        margin={"l": 10, "r": 10, "t": 30, "b": 10},
        xaxis_title="Oxygen tested (%)",
        plot_bgcolor="#ffffff",
    )
    st.plotly_chart(figure, key="ui_oxygen_ranges")
    st.caption("Oxygen range of each investigation, from its NASA PSI sheet.")


@st.fragment
def assistant_panel() -> None:
    """The chat: only this card reruns when a question is sent."""
    mascot("Ask me which NASA experiments matter for your crew environment. I answer from the sheets only.")
    history = st.session_state.setdefault("ui_chat", [])
    with st.container(height=300, border=False):
        if not history:
            st.caption("Try: “Which experiments burned fabrics at high oxygen?”")
        for message in history:
            st.chat_message(message["role"]).write(message["content"])
    question = st.chat_input("Ask a question about the experiments", key="ui_chat_question")
    if question:
        with st.spinner("Looking through the investigations…"):
            answer = repondre(question, history, fiches)
        history.extend([{"role": "user", "content": question}, {"role": "assistant", "content": answer}])
        st.rerun(scope="fragment")


with assistant_column, st.container(key="ui_card_assistant", height="stretch"):
    card_title("Assistant", "AI answers built on the NASA investigation sheets, with their sources.", tag="AI")
    assistant_panel()

# --- Row 3: the selected investigations, side by side -------------------------------------------------------
with st.container(key="ui_card_compare"):
    names = dict(zip(fiches["id"], fiches["nom"], strict=True))
    if not chosen_ids:
        card_title(
            "Compare and extract test data",
            "Select one investigation in the table for its details, or two or three to compare.",
            tag=MODELLING_TAG,
        )
    elif len(chosen_ids) == 1:
        fiche = ranked[ranked["id"] == chosen_ids[0]].iloc[0]
        card_title(f"{fiche['id']} · {fiche['nom']}", "Why it ranks here, and what it studied.", tag=MODELLING_TAG)
        details, why = st.columns([1, 1], gap="medium")
        with details:
            investigation_card(fiche)
        with why:
            st.dataframe(
                detail_du_score(fiche, scenario), hide_index=True, column_config=SCORE_TITLES, key="ui_score_detail"
            )
    else:
        card_title(
            " vs ".join(names[i] for i in chosen_ids),
            "What stands out, and their NASA test conditions.",
            tag=MODELLING_TAG,
        )
        habitat_conditions = place_conditions(habitat, body_of(habitat))
        oxygen = habitat_conditions["oxygen_pct"]
        summary, chart = st.columns([2, 3], gap="medium")
        with summary:
            for sentence in resume(fiches, tests, chosen_ids, oxygen, label(habitat)):
                st.markdown(f"- {sentence}")
        with chart:
            to_plot = carte(tests, chosen_ids)
            if to_plot is None:
                oxygen_range_chart(fiches, chosen_ids, oxygen, label(habitat))
            else:
                (x_axis, y_axis), rows = to_plot
                rows = rows.assign(Investigation=rows["investigation_id"].map(names))
                figure = px.scatter(
                    rows,
                    x=x_axis,
                    y=y_axis,
                    color="Investigation",
                    color_discrete_sequence=COLOURS,
                    opacity=0.75,
                    labels=AXIS_NAMES,
                    hover_data=["test_id", "combustible"],
                )
                if oxygen is not None and x_axis == "oxygene_pct":
                    figure.add_vline(x=oxygen, line_dash="dash", annotation_text=f"{label(habitat)} oxygen")
                figure.update_layout(
                    height=340, margin={"l": 10, "r": 10, "t": 10, "b": 10}, legend={"orientation": "h", "y": -0.2}
                )
                st.plotly_chart(figure, key="ui_compare_chart")
                st.caption(f"Each point is one row of NASA's test tables ({len(rows)} rows).")

    export_ids = chosen_ids or list(ranked["id"])
    rows_to_export = tests[tests["investigation_id"].isin(export_ids)]
    st.download_button(
        f"Download the NASA test conditions ({len(rows_to_export):,} rows, CSV)",
        rows_to_export.to_csv(index=False).encode("utf-8"),
        file_name="flame_in_freefall_test_conditions.csv",
        mime="text/csv",
        icon=":material/download:",
        key="ui_export_tests",
        help="Fuel, oxygen, pressure, air flow and result of each NASA PSI test row: inputs for predictive "
        "flammability models. The selected investigations, or else all those listed in the table.",
    )

footer(
    [
        "Flame in Freefall is a student project for the NASA Space Apps Challenge 2026. It is not affiliated "
        "with or endorsed by NASA. Pillar and fuel type are the team's classification; scores are the team's "
        "judgement, not NASA data.",
        "Experiments: NASA Physical Sciences Informatics. Planet maps: NASA Scientific Visualization Studio (Blue "
        "Marble; LRO LROC colour map of the Moon) and NASA 3D Resources (Mars). Station, spacecraft and rover: "
        "simplified 3D shapes. Moon and Mars images: NASA (Ames artwork 1978; Lunar Electric Rover, 2008; "
        "PIA23302). The mascot is a drawing.",
    ]
)
