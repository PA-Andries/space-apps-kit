"""Page 1's look for role D's conditions chart: dotted reference zones, and the user's selection as a coloured box.

The chart itself comes from `flame.comparateur.graphique_conditions` (role D); only its look changes here.
"""

import plotly.graph_objects as go

SELECTION_COLOR = "255, 122, 61"  # the accent: the user's selection is what the page highlights
SELECTION_NAME = "Your selection"
OTHER_COLOR = "#7d86a8"  # the tests outside the environment, in the secondary family
# Reference zones in light secondary tones (60-30-10: the accent stays for the selection).
ZONE_COLORS = {"Earth": "143, 163, 217", "Moon": "220, 223, 235"}
OTHER_NAME = "Other tests"


def _edges(bounds: tuple | None, axis: tuple) -> tuple:
    """A range whose missing bounds are replaced by the edges of the axis."""
    low, high = bounds or (None, None)
    return (axis[0] if low is None else low, axis[1] if high is None else high)


def _extent(values: list) -> tuple:
    """The smallest and largest of `values`."""
    return (min(values), max(values))


def _matches_the_environment(trace: go.Scatter) -> bool:
    """True for the tests that match the environment: role D draws those, and only those, with an outline."""
    outline = getattr(trace.marker, "line", None)
    return bool(outline is not None and outline.width)


def style_conditions_chart(figure: go.Figure, scenario: dict, view: str) -> go.Figure:
    """Draw the Earth and Moon zones as dotted outlines, and the scenario's ranges as a filled coloured box.

    `view`: "pression" (oxygen × pressure) or "debit" (oxygen × air flow), as in `graphique_conditions`.
    Only the tests that match the environment stay in colour; the others turn grey.
    No box is drawn, and no test is greyed, when the scenario gives no bound at all.
    """
    # The reference zones are the only filled shapes of the chart (Earth and ISS, Moon base and rover).
    zones = [trace for trace in figure.data if trace.fill == "toself"]
    for trace in zones:
        # Light secondary outlines, readable on the dark page; the Earth zone a little bluer than the Moon's.
        rgb = next((value for key, value in ZONE_COLORS.items() if (trace.name or "").startswith(key)), "220, 223, 235")
        color = f"rgba({rgb}, 0.9)"
        trace.update(fill="none", line={"dash": "dot", "width": 2, "color": color})

    # A transparent chart, so that the glass card and the stars show through.
    figure.update_layout(paper_bgcolor="rgba(0, 0, 0, 0)", plot_bgcolor="rgba(0, 0, 0, 0)")

    key = "pression_kpa" if view == "pression" else "debit_air_cm_s"
    oxygen = scenario.get("oxygene_pct") or (None, None)
    other = scenario.get(key) or (None, None)
    if all(bound is None for bound in (*oxygen, *other)):
        return figure

    # Only the tests that match the environment keep their investigation's colour; the others turn grey,
    # grouped under one legend line.
    others = [
        trace
        for trace in figure.data
        if trace.mode == "markers" and trace.marker.symbol != "star" and not _matches_the_environment(trace)
    ]
    for rank, trace in enumerate(others):
        trace.update(
            marker={"color": OTHER_COLOR, "opacity": 0.45},
            name=OTHER_NAME,
            legendgroup="other",
            showlegend=rank == 0,
        )

    # The axis edges: set by the chart, else the extent of the zones (they reach the edges where unbounded).
    x_axis = tuple(figure.layout.xaxis.range or _extent([x for trace in zones for x in trace.x]))
    y_axis = tuple(figure.layout.yaxis.range or _extent([y for trace in zones for y in trace.y]))
    x0, x1 = _edges(oxygen, x_axis)
    y0, y1 = _edges(other, y_axis)
    box = go.Scatter(
        x=[x0, x1, x1, x0, x0],
        y=[y0, y0, y1, y1, y0],
        mode="lines",
        fill="toself",
        fillcolor=f"rgba({SELECTION_COLOR}, 0.18)",
        line={"color": f"rgba({SELECTION_COLOR}, 0.9)", "width": 2},
        name=SELECTION_NAME,
        hoverinfo="name",
    )
    # Drawn first, so that the test points stay on top of the box.
    figure.add_trace(box)
    figure.data = (figure.data[-1], *figure.data[:-1])
    return figure
