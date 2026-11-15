"""The short "How to use this dashboard" card at the top of page 1: a light cover, not a page of its own.

Four numbered steps, in the same frosted glass as the other cards. The visitor can fold it away; a small
link brings it back. Its style lives here, next to the block it dresses.
"""

from html import escape

import streamlit as st

from flame.ui.home import card_title
from flame.ui.style import FLAME, MUTED, SECONDARY, SECONDARY_LINE

# The steps, in the order of the page: (short title, one sentence).
STEPS = [
    ("Choose your environment", "Station and spacecraft, or Moon base and rover: one button per atmosphere."),
    ("Refine the conditions", "Oxygen, pressure, fuel and air flow. Your values follow you on every page."),
    ("Read the chart", "Each point is one NASA test. The circled ones are inside your environment."),
    ("Read the results", "What NASA's data lacks for you, then the 3 most relevant investigations."),
]
NEXT = "Then go further with the menu at the top: Investigations, Compare, or ask Flamy in the bottom-right corner."
HIDDEN_KEY = "ui_intro_hidden"

INTRO_STYLE = f"""<style>
.st-key-ui_card_intro {{
  background: {SECONDARY}; border: 1px solid {SECONDARY_LINE} !important; border-radius: 24px;
  padding: 1.1rem 1.2rem 1rem; margin-bottom: 0.4rem;
  backdrop-filter: blur(16px) saturate(140%); -webkit-backdrop-filter: blur(16px) saturate(140%);
  box-shadow: 0 18px 50px -20px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}}
.ff-steps {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.7rem; margin: 0.5rem 0 0.2rem; }}
.ff-step-tile {{ background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(160, 175, 255, 0.10);
  border-radius: 18px; padding: 0.7rem 0.9rem 0.8rem; }}
.ff-step-head {{ display: flex; align-items: center; gap: 0.55rem; margin-bottom: 0.35rem; }}
.ff-step-head b {{ display: inline-flex; align-items: center; justify-content: center; flex: none;
  width: 1.6rem; height: 1.6rem; border-radius: 50%; background: {FLAME}; color: #fff; font-size: 0.85rem;
  font-weight: 700; }}
.ff-step-head strong {{ font-size: 0.98rem; font-weight: 700; line-height: 1.25; }}
.ff-step-tile span {{ display: block; color: {MUTED}; font-size: 0.85rem; line-height: 1.4; }}
.ff-steps-next {{ color: {MUTED}; font-size: 0.85rem; margin: 0.5rem 0 0; }}
.st-key-ui_intro_show button {{ border: none; background: transparent; padding: 0; min-height: 0; }}
.st-key-ui_intro_show button p,
.st-key-ui_intro_show button [data-testid="stIconMaterial"] {{ color: {FLAME}; font-size: 0.9rem; }}
.st-key-ui_intro_show button:hover p {{ text-decoration: underline; }}
/* "Got it, hide this" is the action of the card: an orange pill, filled when the pointer is on it. */
.st-key-ui_intro_hide button {{
  border: 1.5px solid {FLAME}; background: rgba(232, 98, 42, 0.14); border-radius: 980px;
  padding: 0.4rem 1.15rem; min-height: 0; margin-top: 0.3rem; }}
.st-key-ui_intro_hide button p, .st-key-ui_intro_hide button [data-testid="stIconMaterial"] {{
  color: {FLAME}; font-size: 0.95rem; font-weight: 700; }}
.st-key-ui_intro_hide button:hover {{ background: {FLAME}; border-color: {FLAME}; }}
.st-key-ui_intro_hide button:hover p,
.st-key-ui_intro_hide button:hover [data-testid="stIconMaterial"] {{ color: #fff; }}
@media (max-width: 900px) {{ .ff-steps {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
@media (max-width: 520px) {{ .ff-steps {{ grid-template-columns: 1fr; }} }}
</style>"""


def _hide() -> None:
    st.session_state[HIDDEN_KEY] = True


def _show() -> None:
    st.session_state[HIDDEN_KEY] = False


def how_to_use() -> None:
    """The "How to use this dashboard" card of page 1, or a small link to bring it back once folded away."""
    st.html(INTRO_STYLE)
    if st.session_state.get(HIDDEN_KEY):
        st.button("How to use this dashboard", icon=":material/help:", key="ui_intro_show", on_click=_show)
        return
    with st.container(key="ui_card_intro"):
        card_title("How to use this dashboard", "Four steps, from your environment to NASA's evidence.")
        tiles = "".join(
            f'<div class="ff-step-tile"><div class="ff-step-head"><b>{number}</b><strong>{escape(title)}</strong></div>'
            f"<span>{escape(sentence)}</span></div>"
            for number, (title, sentence) in enumerate(STEPS, start=1)
        )
        st.html(f'<div class="ff-steps">{tiles}</div><p class="ff-steps-next">{escape(NEXT)}</p>')
        st.button("Got it, hide this", icon=":material/check:", key="ui_intro_hide", on_click=_hide)
