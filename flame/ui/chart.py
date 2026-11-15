"""Page 1's look for role D's conditions chart: dotted reference zones, and the user's selection as a coloured box.

The chart itself comes from `flame.comparateur.graphique_conditions` (role D); only its look changes here.
"""

import plotly.graph_objects as go

from flame.ui.phone import chart_for_phone

SELECTION_COLOR = "232, 98, 42"  # the accent: the user's selection is what the page highlights
SELECTION_NAME = "Your selection"
OTHER_COLOR = "#7d86a8"  # the tests outside the environment, in the secondary family
# Reference zones in light secondary tones (60-30-10: the accent stays for the selection).
ZONE_COLORS = {"Earth": "143, 163, 217", "Moon": "220, 223, 235"}
OTHER_NAME = "Other tests"


def _edges(bounds: tuple | None, axis: tuple) -> tuple:
    """A range whose missing bounds are replaced by the edges of the axis."""
    low, high = bounds or (None, None)
    return (axis[0] if low is None else low, axis[1] if high is None else high)


def _matches_the_environment(trace: go.Scatter) -> bool:
    """True for the tests that match the environment: role D draws those, and only those, with an outline."""
    outline = getattr(trace.marker, "line", None)
    return bool(outline is not None and outline.width)


def style_conditions_chart(figure: go.Figure, scenario: dict, view: str) -> go.Figure:
    """Draw the Earth and Moon zones as dotted outlines, and the scenario's ranges as a filled coloured box.

    `view`: "pression" (oxygen × pressure) or "debit" (oxygen × air flow), as in `graphique_conditions`.
    Only the tests that match the environment stay in colour; the others turn grey.
    No box is drawn, and no test is greyed, when the scenario gives no bound and no fuel at all.
    A range with no bound on one side reaches the edge of the axis.
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

    # The chart itself says which ranges chose its circled tests and where its axes end (`layout.meta`):
    # the box is drawn from those same values, so a circled test can never sit outside it.
    meta = figure.layout.meta or {}
    if not meta.get("defini"):
        return chart_for_phone(figure)

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

    x0, x1 = selection_box(meta)["x"]
    y0, y1 = selection_box(meta)["y"]
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
    return chart_for_phone(figure)  # the legend goes under the plot on a phone; unchanged on a computer


def selection_box(meta: dict) -> dict:
    """The box of the selection: {"x": (low, high), "y": (low, high)}, in the units of the axes.

    A missing bound reaches the edge of the axis, and a bound beyond the axis stops at its edge.
    """

    def side(bounds: list, axis: list) -> tuple:
        low, high = _edges(tuple(bounds), tuple(axis))
        return (min(max(low, axis[0]), axis[1]), min(max(high, axis[0]), axis[1]))

    return {"x": side(meta["plage_x"], meta["axe_x"]), "y": side(meta["plage_y"], meta["axe_y"])}


def grey_tests_in_the_box(figure: go.Figure) -> str:
    """One sentence on the grey tests that sit inside the box, or "" when there is none.

    A test inside the box stays grey only when a filter that is not on the axes excludes it: the chosen
    fuels, or the range of the other view. The sentence counts them and names that filter.
    """
    meta = figure.layout.meta or {}
    if not meta.get("defini"):
        return ""
    box = selection_box(meta)
    count = 0
    for trace in figure.data:
        if trace.mode != "markers" or trace.marker.symbol == "star" or _matches_the_environment(trace):
            continue
        count += sum(
            box["x"][0] <= x <= box["x"][1] and box["y"][0] <= y <= box["y"][1]
            for x, y in zip(trace.x, trace.y, strict=True)
        )
    if not count:
        return ""
    reasons = []
    if meta.get("combustibles"):
        reasons.append("their fuel is not one you chose")
    if any(bound is not None for bound in meta.get("autre_plage", [])):
        other = "air-flow" if figure.layout.yaxis.type == "log" else "pressure"
        reasons.append(f"they are outside your {other} range or do not record it")
    return f"{count:,} tests inside the box stay grey: {' or '.join(reasons)}."
