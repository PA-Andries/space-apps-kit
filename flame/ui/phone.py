"""The phone version of the site: everything that changes on a narrow screen, in one place.

During the demo the site is opened from a QR code, so on a phone. Two tools, and neither touches the
desktop version:
- `PHONE_STYLE`: style rules inside one `@media (max-width: 640px)` block. A wider window never reads them.
- `on_phone()`: True when the visitor's browser says it is a phone. It is used where a style rule cannot
  help: the chart of page 1 is drawn by Plotly, which sizes its legend in Python, not in CSS.

The rules carry `!important` because each card brings its own style later in the page: without it, the
card's desktop rule would win on a phone too.
"""

import plotly.graph_objects as go
import streamlit as st

PHONE_WIDTH = 640  # px: at this width and under, Streamlit stacks its columns
PHONE_WORDS = ("Mobi", "Android", "iPhone", "iPod")  # what a phone's browser writes in its User-Agent

PHONE_STYLE = f"""<style>
@media (max-width: {PHONE_WIDTH}px) {{
  /* Home's title on two lines instead of three. */
  .ff-header h1 {{ font-size: 2.1rem !important; line-height: 1.15 !important; }}

  /* Flamy's card is smaller and closer to the corner, so it covers less of the page... */
  .st-key-ui_flamy {{ width: 84px !important; right: 10px !important; bottom: 10px !important;
    border-radius: 20px !important; padding: 0.2rem 0 0.3rem !important; }}
  .st-key-ui_flamy [data-testid="stElementContainer"]:has(iframe) {{ height: 62px !important;
    max-height: 62px !important; flex: 0 0 62px !important; }}
  .st-key-ui_flamy iframe {{ height: 62px !important; }}
  .st-key-ui_flamy button {{ padding: 0 !important; }}
  .st-key-ui_flamy button p {{ font-size: 0.74rem !important; white-space: nowrap !important; }}
  .st-key-ui_flamy button [data-testid="stIconMaterial"] {{ display: none !important; }}
  /* ... and the page ends with an empty strip as tall as the card: its last lines can be scrolled clear of it. */
  [data-testid="stMainBlockContainer"] {{ padding-bottom: 8.5rem !important; }}

  /* Home's chart: Plotly's toolbar sat on top of the legend; a phone pinches to zoom instead. */
  .st-key-ui_conditions_chart .modebar-container {{ display: none !important; }}

  /* Investigations: the ranking comes first, in a short box that scrolls, instead of under the whole record. */
  [data-testid="stColumn"]:has(.st-key-recherche_classement) {{ order: -1 !important; position: static !important; }}
  .st-key-recherche_classement {{ height: 15rem !important; max-height: 15rem !important;
    padding-bottom: 0.4rem !important; }}
}}
</style>"""


def user_agent() -> str:
    """What the visitor's browser says it is, or "" when there is no browser behind the page (a test, a script)."""
    try:
        return st.context.headers.get("User-Agent") or ""
    except Exception:
        return ""


def on_phone() -> bool:
    """True when the visitor's browser says it is a phone; False on a computer, and when it says nothing."""
    agent = user_agent()
    return any(word in agent for word in PHONE_WORDS)


def chart_for_phone(figure: go.Figure) -> go.Figure:
    """On a phone, put the chart's legend under the plot; on a computer, return the chart as it is.

    On the right, the legend took more than half of a phone's width and squeezed the points into a strip.
    """
    if not on_phone():
        return figure
    figure.update_layout(
        legend={
            "orientation": "h",
            "x": 0,
            "xanchor": "left",
            "y": -0.22,
            "yanchor": "top",
            "font": {"size": 11},
            "title": {"text": ""},
        },
        margin={"l": 8, "r": 8, "t": 10},
        height=560,
    )
    return figure
