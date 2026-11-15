"""The look of the whole site, applied once per page by the top bar.

A space universe that stays easy to use: a deep night-blue page with soft nebula glows and a field of
stars, frosted-glass cards with light text, pill buttons, links in the flame colour, and a gentle rise of
each block as the page appears. Colours come from `.streamlit/config.toml`; this adds what the theme
cannot set (font, background, glass, shapes, motion). Text keeps a strong contrast on the dark glass.
"""

import base64
from pathlib import Path

import streamlit as st

# Colours follow the 60-30-10 rule:
# 60 % DOMINANT, the night-blue page and its background; 30 % SECONDARY, the slate-blue glass of cards,
# chips, sidebar and the secondary text; 10 % ACCENT, flame orange, kept for actions and highlights only
# (the chosen environment, ANALYSE, links, sliders, the user's selection on the chart).
DOMINANT = "#070a1c"
SECONDARY = "rgba(26, 33, 80, 0.6)"  # card glass, over the dominant page
SECONDARY_LINE = "rgba(160, 175, 255, 0.14)"  # thin rims of the glass
ACCENT = "#e8622a"
INK = "#eef1fb"  # main text, on the dark page
MUTED = "#d0d5ec"  # secondary text, still readable on the dark glass
FLAME = ACCENT  # same as primaryColor in config.toml
GRADIENT = "linear-gradient(90deg, #f5894f 0%, #e8622a 100%)"  # the accent, a little lighter on the left

# The background drawing: stars, small spiral galaxies and planets (an original SVG, drawn by
# flame/ui/images/make_space_background.py), embedded so that no file has to be served.
_BACKGROUND = Path(__file__).parent / "images" / "space_background.svg"
SPACE_BACKGROUND = "data:image/svg+xml;base64," + base64.b64encode(_BACKGROUND.read_bytes()).decode()

GLOBAL_STYLE = f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400..800&display=swap');

/* Font: Inter on text, never on the icon font. */
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp button, .stApp h1, .stApp h2, .stApp h3,
.stApp [data-testid="stMarkdownContainer"], .stApp [data-baseweb="select"] {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
}}
.stApp h1, .stApp h2, .stApp h3 {{ color: {INK}; letter-spacing: -0.03em; font-weight: 700; }}
.stApp header[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stMain"] {{ scroll-behavior: smooth; }}

/* A centred column with room to breathe. */
.stMainBlockContainer, .block-container {{ max-width: 1440px; padding: 4.6rem 2rem 2rem; }}  /* room for the menu bar */

/* Pill-shaped buttons, with a soft lift on hover. */
.stButton button, .stLinkButton a {{
  border-radius: 980px; font-weight: 500; transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
}}
[data-testid="stPageLink"] a {{ justify-content: center; }}
[data-testid="stPageLink"] a p {{ color: {FLAME}; font-size: 1.15rem; font-weight: 500; }}
[data-testid="stPageLink"] a:hover {{ background: transparent; }}
[data-testid="stPageLink"] a:hover p {{ text-decoration: none; opacity: 0.8; }}

/* 3D scenes: large round-cornered windows on space, with a soft, wide shadow. The dark background
   shows while a scene loads, instead of a white flash. */
iframe {{ border-radius: 30px; box-shadow: 0 30px 80px -20px rgba(29, 29, 31, 0.35); background: #080b14; }}

.ff-disclaimer {{ text-align: center; color: #86868b; font-size: 0.78rem; margin: 0.4rem 0 0; }}

/* No grey fade on the page while Streamlit updates it after a click. */
[data-stale="true"] {{ opacity: 1 !important; transition: none !important; }}

/* The mascot: no frame around it, and a speech bubble pointing at it. */
.st-key-ui_mascot {{ margin: 0; }}
.st-key-ui_mascot iframe {{ box-shadow: none; border-radius: 0; background: transparent; }}
.ff-bubble {{ position: relative; background: #f5f5f7; border-radius: 22px; padding: 1.1rem 1.3rem; color: {INK};
  font-size: 0.95rem; line-height: 1.45; font-weight: 500; }}
.ff-bubble::before {{ content: ""; position: absolute; left: -9px; top: 50%; width: 18px; height: 18px;
  background: #f5f5f7; transform: translateY(-50%) rotate(45deg); border-radius: 3px; }}

/* Alerts and bordered containers as soft white tiles. */
[data-testid="stAlert"] {{ border-radius: 18px; border: none; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 22px; }}

/* Each block rises gently into place. */
@keyframes ff-rise {{ from {{ opacity: 0; transform: translateY(18px); }} to {{ opacity: 1; transform: none; }} }}
.ff-hero, .ff-section, .ff-stats, .ff-footer {{
  animation: ff-rise 0.8s cubic-bezier(0.2, 0.7, 0.2, 1) both;
}}
@media (prefers-reduced-motion: reduce) {{ .ff-hero, .ff-section, .ff-stats, .ff-footer {{
  animation: none; }} }}

/* Home page text blocks (see flame/ui/home.py). */
.ff-hero .ff-gradient {{ display: block; }}
.ff-gradient {{ background: {GRADIENT}; -webkit-background-clip: text; background-clip: text; color: transparent;
  -webkit-text-fill-color: transparent; }}
.ff-hero {{ text-align: center; padding: 4.5rem 0 1rem; }}
.ff-eyebrow {{ color: {FLAME}; font-weight: 600; font-size: 1.1rem; margin: 0 0 0.8rem; letter-spacing: -0.01em; }}
.ff-hero h1 {{ font-size: clamp(2.8rem, 7.5vw, 5.6rem); line-height: 1.02; letter-spacing: -0.045em;
  font-weight: 800; margin: 0 auto; max-width: 13ch; padding: 0; }}
.ff-lead {{ color: {MUTED}; font-size: clamp(1.15rem, 2.2vw, 1.6rem); line-height: 1.35; max-width: 30ch;
  margin: 1.4rem auto 0; font-weight: 500; letter-spacing: -0.015em; }}
.ff-actions {{ display: flex; gap: 1.6rem; justify-content: center; align-items: center; flex-wrap: wrap;
  margin-top: 2.2rem; }}
.ff-cta {{ background: {FLAME}; color: #fff !important; text-decoration: none !important; font-weight: 500;
  font-size: 1.05rem; padding: 0.75rem 1.5rem; border-radius: 980px; transition: background 0.2s; }}
.ff-cta:hover {{ background: #c9541c; }}
.ff-more {{ color: {FLAME} !important; text-decoration: none !important; font-size: 1.1rem; font-weight: 500; }}
.ff-more::after {{ content: " \\203A"; }}
.ff-more:hover {{ text-decoration: none !important; opacity: 0.8; }}

.ff-section {{ text-align: center; margin: 6rem 0 2rem; scroll-margin-top: 6rem; }}
.ff-section .ff-step {{ color: {FLAME}; font-weight: 600; font-size: 1rem; margin: 0 0 0.5rem !important; }}
.ff-section h2 {{ font-size: clamp(2.1rem, 5vw, 3.5rem); line-height: 1.05; letter-spacing: -0.04em;
  font-weight: 800; margin: 0; padding: 0; }}
.ff-section p {{ color: {MUTED}; font-size: 1.25rem; margin: 0.8rem 0 0; font-weight: 500; letter-spacing: -0.01em; }}

.ff-stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2rem; margin: 0 0 1.2rem; }}
.ff-stat {{ background: #fff; border-radius: 28px; padding: 2rem 1.2rem 2.2rem; text-align: center; }}
.ff-stat span {{ display: block; color: {MUTED}; font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem; }}
.ff-stat strong {{ display: block; font-size: clamp(2.4rem, 5vw, 3.6rem); font-weight: 800; letter-spacing: -0.045em;
  line-height: 1; background: {GRADIENT}; -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent; color: transparent; padding-bottom: 0.08em; }}
.ff-stat strong.ff-unknown {{ background: none; -webkit-text-fill-color: #a1a1a6; color: #a1a1a6;
  font-size: clamp(1.5rem, 3vw, 2rem); letter-spacing: -0.03em; line-height: 1.6; }}
.ff-note {{ color: {MUTED}; font-size: 0.9rem; text-align: center; margin: 0 auto 2.5rem; max-width: 60ch; }}

/* What follows a 3D scene: a centred caption and link. */
.st-key-ui_after_scene [data-testid="stCaptionContainer"] {{ text-align: center; margin-top: 0.8rem; }}
.st-key-ui_after_scene [data-testid="stElementContainer"]:has([data-testid="stPageLink"]) {{ align-self: center; }}
/* Dashboard (see flame/ui/home.py): a header line, then white cards in a grid. */
.ff-header {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 1rem; flex-wrap: wrap;
  margin: 0.4rem 0 0.6rem; }}
.ff-header h1 {{ font-size: 1.9rem; font-weight: 800; letter-spacing: -0.035em; margin: 0; padding: 0;
  display: flex; align-items: center; gap: 0.6rem; }}
.ff-header p {{ color: {MUTED}; margin: 0.2rem 0 0; font-size: 0.98rem; font-weight: 500; }}
.ff-mark {{ width: 14px; height: 22px; border-radius: 50% 50% 50% 50% / 62% 62% 38% 38%; background: {GRADIENT};
  display: inline-block; }}
.ff-chips {{ display: flex; gap: 0.5rem; flex-wrap: wrap; }}
.ff-chip {{ background: #fff; border-radius: 980px; padding: 0.35rem 0.85rem; font-size: 0.85rem; font-weight: 600;
  color: {INK}; box-shadow: 0 1px 4px rgba(29, 29, 31, 0.06); }}
.st-key-ui_card_destination, .st-key-ui_card_conditions, .st-key-ui_card_ranking,
.st-key-ui_card_assistant, .st-key-ui_card_compare, .st-key-ui_card_gaps {{
  background: #fff; border: none !important; border-radius: 24px; padding: 1.1rem 1.2rem 1.2rem;
  box-shadow: 0 2px 14px rgba(29, 29, 31, 0.05);
}}
.ff-tag {{ display: block; color: {FLAME}; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; margin-bottom: 0.15rem; }}
.ff-card-title h3 {{ font-size: 1.15rem; font-weight: 700; letter-spacing: -0.02em; margin: 0; padding: 0; }}
.ff-card-title p {{ color: {MUTED}; font-size: 0.88rem; margin: 0.15rem 0 0.2rem; }}
.ff-compact.ff-stats {{ gap: 0.6rem; margin: 0.2rem 0 0.4rem; }}
.ff-compact .ff-stat {{ background: #f5f5f7; border-radius: 18px; padding: 0.8rem 0.5rem 0.9rem; }}
.ff-compact .ff-stat span {{ font-size: 0.8rem; margin-bottom: 0.2rem; }}
.ff-compact .ff-stat strong {{ font-size: 1.9rem; }}
.ff-compact .ff-stat strong.ff-unknown {{ font-size: 1.05rem; line-height: 1.9; }}
.ff-compact + .ff-note, .ff-note.ff-small {{ font-size: 0.78rem; margin: 0 0 0.4rem; }}
.st-key-ui_card_conditions iframe, .st-key-ui_card_destination iframe {{ box-shadow: none; border-radius: 18px; }}

.ff-grid2.ff-stats {{ grid-template-columns: repeat(2, 1fr); }}
/* Moins de trois tuiles : elles gardent leur taille et la rangée reste centrée. */
.ff-cols1.ff-stats, .ff-cols2.ff-stats {{ justify-content: center; }}
.ff-cols1.ff-stats {{ grid-template-columns: minmax(0, 22rem); }}
.ff-cols2.ff-stats {{ grid-template-columns: repeat(2, minmax(0, 22rem)); }}
.ff-stat small {{ display: block; color: #86868b; font-size: 0.72rem; margin-top: 0.25rem; }}

/* The chatbot icon, pinned to the bottom-right corner (sketch 1 of the whiteboard). */
.st-key-ui_chatbot, .st-key-ui_flamy {{ position: fixed; right: 22px; bottom: 18px; z-index: 1000; width: 112px; gap: 0;
  background: #fff; border-radius: 24px; padding: 0.3rem 0.4rem 0.4rem;
  box-shadow: 0 10px 30px rgba(29, 29, 31, 0.18); }}
.st-key-ui_chatbot iframe, .st-key-ui_flamy iframe, .st-key-ui_flamy_face iframe {{ box-shadow: none; border-radius: 0;
  background: transparent; }}
.st-key-ui_chatbot [data-testid="stPageLink"] a {{ justify-content: center; padding: 0; }}
.st-key-ui_chatbot [data-testid="stPageLink"] p {{ font-size: 0.85rem; font-weight: 600; }}
/* The whole button opens the chatbot, not only the word « Flamy »: the link gets an invisible layer over the
   whole card. The mascot's frame lets the clicks through (it does not react to the mouse), and the elements
   between the card and the link are not positioned, so that the layer covers the card. */
.st-key-ui_chatbot {{ cursor: pointer; }}
.st-key-ui_chatbot iframe, .st-key-ui_flamy iframe, .st-key-ui_flamy_face iframe {{ pointer-events: none; }}
.st-key-ui_chatbot [data-testid="stElementContainer"], .st-key-ui_chatbot [data-testid="stPageLink"],
.st-key-ui_chatbot [data-testid="stPageLink"] * {{ position: static; }}
.st-key-ui_chatbot [data-testid="stPageLink"] a::after {{ content: ""; position: absolute; inset: 0;
  border-radius: 24px; z-index: 1; }}
/* Same for Flamy's chat button (`ui_flamy`): the whole card opens the chat window, not only the word. */
.st-key-ui_flamy {{ cursor: pointer; }}
.st-key-ui_flamy [data-testid="stElementContainer"], .st-key-ui_flamy [data-testid="stButton"],
.st-key-ui_flamy [data-testid="stButton"] * {{ position: static; }}
.st-key-ui_flamy [data-testid="stButton"] button::after {{ content: ""; position: absolute; inset: 0;
  border-radius: 24px; z-index: 1; }}
/* Streamlit's captions, a little whiter so that they stand out on the dark glass. */
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{ color: {MUTED}; }}

/* The mascot of the Assistant page, as in a messaging app: on the left, its lower half hidden behind the
   chat box, so that it seems to stand behind it. The chat box is drawn on top of it. */
.st-key-ui_assistant_mascot {{ width: 150px; margin: 0 0 -74px 10px; position: relative; z-index: 0; gap: 0;
  align-self: flex-start;
  pointer-events: none; }}
.st-key-ui_assistant_mascot iframe {{ box-shadow: none; border-radius: 0; background: transparent; }}
[data-testid="stChatInput"] {{ position: relative; z-index: 1; }}
/* The bottom bar lets the space background show through. */
[data-testid="stBottom"], [data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] {{
  background: transparent; }}

/* The answer to "can a flame burn here?": a short headline, the accent only for "Yes". */
.ff-answer {{ display: flex; flex-direction: column; gap: 0.2rem; margin: 0.2rem 0 0.8rem; }}
.ff-answer strong {{ font-size: 1.6rem; font-weight: 800; letter-spacing: -0.03em; color: {INK}; }}
.ff-answer.ff-yes strong {{ color: {ACCENT}; }}
.ff-answer.ff-no_answer strong {{ color: {MUTED}; }}
.ff-answer span {{ color: {MUTED}; font-size: 0.95rem; }}

/* What NASA's tests show (after ANALYSE): one bar split by outcome, and its legend. */
.ff-outcomes .ff-bar {{ display: flex; height: 16px; border-radius: 980px; overflow: hidden; gap: 2px;
  margin: 0.3rem 0 0.7rem; }}
.ff-outcomes ul {{ display: flex; flex-wrap: wrap; gap: 0.4rem 1.2rem; list-style: none; padding: 0;
  margin: 0 0 0.6rem; }}
.ff-outcomes li {{ color: {MUTED}; font-size: 0.88rem; display: flex; align-items: center; gap: 0.4rem; margin: 0; }}
.ff-outcomes li b {{ color: {INK}; }}
.ff-outcomes i {{ width: 10px; height: 10px; border-radius: 3px; display: inline-block; }}
.st-key-ui_card_outcomes, .st-key-ui_card_coverage {{ background: {SECONDARY};
  border: 1px solid {SECONDARY_LINE} !important;
  border-radius: 24px; padding: 1.1rem 1.2rem 1.2rem; backdrop-filter: blur(16px) saturate(140%);
  -webkit-backdrop-filter: blur(16px) saturate(140%); }}

/* The menu: a frosted bar fixed at the top of the window, as on Apple's site. */
header[data-testid="stHeader"] {{ background: rgba(7, 10, 28, 0.72); backdrop-filter: blur(20px) saturate(160%);
  -webkit-backdrop-filter: blur(20px) saturate(160%); border-bottom: 1px solid {SECONDARY_LINE}; }}
[data-testid="stTopNav"] {{ justify-content: center; gap: 0.2rem; }}
[data-testid="stTopNav"] a {{ border-radius: 980px; padding: 0.3rem 0.85rem; }}
[data-testid="stTopNav"] a p, [data-testid="stTopNav"] a span {{ font-size: 0.9rem; font-weight: 500; color: {MUTED}; }}
[data-testid="stTopNav"] a:hover p, [data-testid="stTopNav"] a:hover span {{ color: {INK}; }}
[data-testid="stTopNav"] a[aria-current="page"] {{ background: rgba(255, 255, 255, 0.08); }}
[data-testid="stTopNav"] a[aria-current="page"] p, [data-testid="stTopNav"] a[aria-current="page"] span {{
  color: {INK}; font-weight: 600; }}

/* Under the menu: the user's environment on the left, the disclaimer on the right. */
.st-key-ui_status_line {{ justify-content: space-between; flex-wrap: wrap; gap: 0.4rem 1rem; margin: 0.2rem 0 0.4rem; }}
.st-key-ui_status_line .ff-disclaimer {{ margin: 0; }}
.ff-env-line {{ margin: 0; font-size: 0.88rem; color: {INK}; font-weight: 600; background: {SECONDARY};
  border: 1px solid {SECONDARY_LINE}; border-radius: 980px; padding: 0.3rem 0.9rem; }}
.ff-env-line span {{ color: {ACCENT}; font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; margin-right: 0.5rem; }}

/* Flamy's button under the mascot, and its chat window: a small panel in the bottom-right corner. */
.st-key-ui_flamy button {{ width: 100%; padding: 0.15rem 0.4rem; min-height: 0; border: none; background: transparent;
  color: {ACCENT}; }}
.st-key-ui_flamy button p {{ font-size: 0.82rem; font-weight: 700; }}
/* The whole card opens the chat window, Flamy included, not only the word « Flamy »: the button gets an
   invisible layer over the card (the mascot's frame lets clicks through, and nothing in between is positioned). */
.st-key-ui_flamy {{ cursor: pointer; }}
.st-key-ui_flamy [data-testid="stElementContainer"], .st-key-ui_flamy .stButton,
.st-key-ui_flamy .stButton > *, .st-key-ui_flamy button {{ position: static !important; }}
.st-key-ui_flamy button::after {{ content: ""; position: absolute; inset: 0; border-radius: 24px; z-index: 1; }}
.st-key-ui_flamy:hover {{ border-color: {ACCENT}; }}
section[role="dialog"]:has(.st-key-ui_flamy_conversation) {{ position: fixed; right: 24px; bottom: 24px; margin: 0;
  width: min(420px, calc(100vw - 32px)); background: rgba(14, 18, 44, 0.92); backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px); border: 1px solid {SECONDARY_LINE}; border-radius: 22px; }}
/* The chat window, laid out like a messaging app. */
section[role="dialog"]:has(.st-key-ui_flamy_conversation) > div:first-child {{ padding-bottom: 0; }}
.st-key-ui_flamy_header {{ flex-wrap: nowrap; margin-top: -2.6rem; padding-bottom: 0.6rem;
  border-bottom: 1px solid {SECONDARY_LINE}; }}
/* The header is pulled up beside the window's close cross: let clicks go through it, so the cross works. */
.st-key-ui_flamy_header {{ pointer-events: none; }}
.st-key-ui_flamy_face {{ flex: 0 0 64px; width: 64px; }}
.st-key-ui_flamy_header [data-testid="stElementContainer"]:has(.ff-chat-who) {{ flex: 1 1 auto;
  width: auto; }}
.st-key-ui_flamy_face iframe {{ width: 64px !important; }}
.ff-chat-who {{ display: flex; flex-direction: column; line-height: 1.25; }}
.ff-chat-who b {{ font-size: 1.05rem; color: {INK}; }}
.ff-chat-who span {{ font-size: 0.78rem; color: {MUTED}; }}
.st-key-ui_flamy_conversation {{ gap: 0.5rem; padding: 0.4rem 0.1rem; }}
/* Bubbles: no avatars; Flamy on the left in glass, the visitor on the right in the accent. */
.st-key-ui_flamy_conversation [data-testid^="stChatMessageAvatar"] {{ display: none; }}
.st-key-ui_flamy_conversation [data-testid="stChatMessage"] {{ width: fit-content; max-width: 85%; gap: 0;
  padding: 0.55rem 0.85rem; border-radius: 18px 18px 18px 6px; background: rgba(255, 255, 255, 0.07);
  border: 1px solid {SECONDARY_LINE}; }}
.st-key-ui_flamy_conversation [data-testid="stChatMessageContent"] {{ padding: 0; margin: 0; min-width: 0;
  height: auto !important; display: flow-root !important; }}
.st-key-ui_flamy_conversation [data-testid="stChatMessageContent"] div {{ margin: 0 !important; }}
/* Inside a bubble, plain blocks: Streamlit's flex boxes would keep the text at one line's height. */
.st-key-ui_flamy_conversation [data-testid="stChatMessageContent"] div {{ display: block !important;
  height: auto !important; }}
.st-key-ui_flamy_conversation [data-testid="stChatMessageContent"] p {{ font-size: 0.92rem; line-height: 1.45;
  margin: 0 0 0.3rem; }}
.st-key-ui_flamy_conversation [data-testid="stChatMessageContent"] p:last-child {{ margin-bottom: 0; }}
.st-key-ui_flamy_conversation [data-testid="stElementContainer"]:has([data-testid="stChatMessageAvatarUser"]) {{
  align-self: flex-end; display: flex; justify-content: flex-end; }}
.st-key-ui_flamy_conversation [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
  margin-left: auto; background: {ACCENT}; border-color: {ACCENT}; border-radius: 18px 18px 6px 18px; }}
.st-key-ui_flamy_conversation [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p {{
  color: #fff; }}

/* No underline on any link or button text, even on hover: the site should not look like a back office. */
.stApp a, .stApp a:hover, .stApp a:focus, .stApp a p, .stApp a:hover p, .stApp a span, .stApp a:hover span,
.stApp button p, .stApp button:hover p {{ text-decoration: none !important; }}

/* Under which conditions NASA ran its tests: a compact table with a status chip per condition. */
.ff-coverage {{ display: flex; flex-direction: column; }}
.ff-cov-row {{ display: grid; grid-template-columns: 1.3fr 1.4fr 1.3fr 0.9fr 2.6fr; gap: 0.8rem; align-items: center;
  padding: 0.55rem 0.2rem; border-bottom: 1px solid {SECONDARY_LINE}; font-size: 0.9rem; color: {INK}; }}
.ff-cov-row:last-child {{ border-bottom: none; }}
.ff-cov-head {{ color: {MUTED}; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.04em; }}
.ff-cov-name {{ font-weight: 700; }}
.ff-cov-nasa, .ff-cov-detail {{ color: {MUTED}; }}
.ff-cov-detail a, .ff-cov-verdict a {{ color: {ACCENT}; font-weight: 600; }}
/* The verdict for the whole combination, above the table. */
.ff-cov-verdict {{ display: flex; gap: 0.9rem; align-items: flex-start; padding: 0.9rem 1rem; margin-bottom: 0.6rem;
  border: 1px solid {SECONDARY_LINE}; border-radius: 14px; background: rgba(255, 255, 255, 0.04); color: {INK}; }}
.ff-cov-verdict .ff-cov-status {{ flex: 0 0 auto; margin-top: 0.15rem; }}
.ff-cov-verdict b {{ display: block; font-size: 1.05rem; margin-bottom: 0.2rem; }}
.ff-cov-verdict span:not(.ff-cov-status) {{ color: {MUTED}; font-size: 0.9rem; }}
.ff-cov-then {{ color: {MUTED}; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.04em; margin: 0.4rem 0 0; }}
.ff-cov-status {{ justify-self: start; border-radius: 980px; padding: 0.15rem 0.65rem; font-size: 0.78rem;
  font-weight: 700; border: 1px solid {SECONDARY_LINE}; background: rgba(255, 255, 255, 0.06); }}
.ff-cov-status.ff-tested {{ background: {ACCENT}; border-color: {ACCENT}; color: #fff; }}
.ff-cov-status.ff-partly {{ border-color: {ACCENT}; color: {ACCENT}; }}
@media (max-width: 760px) {{ .ff-cov-row {{ grid-template-columns: 1fr 1fr; }} .ff-cov-head {{ display: none; }} }}

/* Investigations: the ranking in a column on the right, one button per investigation, the chosen one in accent. */
.ff-rank-title {{ color: {MUTED}; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.04em; margin: 0 0 0.3rem; }}
.st-key-recherche_classement button {{ justify-content: flex-start; text-align: left; min-height: 0;
  padding: 0.45rem 0.8rem; border-radius: 12px; }}
/* A long name is cut after two lines, with « … »; the whole name shows on hover. */
.st-key-recherche_classement button p {{ font-size: 0.85rem; line-height: 1.3; white-space: normal;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
.st-key-recherche_classement button > div, .st-key-recherche_classement button [data-testid="stMarkdownContainer"] {{
  min-width: 0; overflow: hidden; }}
.st-key-recherche_classement button > div {{ justify-content: flex-start; width: 100%; }}
/* Room at the end of the list, so that Flamy's card in the corner never hides the last investigations. */
.st-key-recherche_classement {{ padding-bottom: 7rem; }}
/* The list stays within the window and follows the page as it scrolls, so it is always at hand. */
[data-testid="stColumn"]:has(.st-key-recherche_classement) {{ position: sticky; top: 4.6rem; align-self: flex-start; }}
.st-key-recherche_classement {{ height: calc(100vh - 7rem) !important; max-height: calc(100vh - 7rem); }}

/* The ANALYSE button under the chart. */
.st-key-ui_analyse button {{ background: {FLAME}; color: #fff; border: none; letter-spacing: 0.08em; font-weight: 700;
  padding: 0.6rem 2.2rem; }}
.st-key-ui_analyse button:hover {{ background: #c9541c; color: #fff; }}
.st-key-ui_analyse {{ align-items: center; }}
/* The verdict banner: the one thing the page says. The 60-30-10 rule of the site holds here — the
   night-blue page (60 %), one more pane of glass and light words (30 %), and the flame colour on the
   figure and the left edge alone (10 %). Nothing else on the page is painted, so the eye lands here. */
.ff-verdict {{ display: flex; align-items: center; gap: 1.6rem; background: {SECONDARY};
  border: 1px solid {SECONDARY_LINE}; border-left: 5px solid rgba(160, 175, 255, 0.28); border-radius: 26px;
  padding: 1.4rem 1.8rem; margin: 0 0 1.1rem;
  backdrop-filter: blur(16px) saturate(140%); -webkit-backdrop-filter: blur(16px) saturate(140%);
  box-shadow: 0 18px 50px -20px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.05); }}
.ff-verdict.ff-severe {{ border-left-color: {FLAME}; }}
.ff-verdict-figure {{ font-size: 3.4rem; font-weight: 800; letter-spacing: -0.04em; line-height: 1;
  color: {INK}; flex: 0 0 auto; min-width: 5.5rem; text-align: center; }}
.ff-verdict.ff-severe .ff-verdict-figure {{ color: {FLAME}; }}
.ff-verdict-words h2 {{ font-size: 1.45rem; font-weight: 700; letter-spacing: -0.03em; margin: 0 0 0.3rem;
  color: {INK}; }}
.ff-verdict-words p {{ color: {INK}; font-size: 0.97rem; line-height: 1.5; margin: 0; }}
.ff-verdict-source {{ color: {MUTED}; font-size: 0.78rem !important; margin-top: 0.4rem !important;
  text-transform: uppercase; letter-spacing: 0.04em; }}
.ff-verdict-note {{ color: {MUTED}; font-size: 0.85rem !important; margin-top: 0.5rem !important;
  padding-top: 0.5rem; border-top: 1px solid {SECONDARY_LINE}; }}
@media (max-width: 640px) {{
  .ff-verdict {{ flex-direction: column; align-items: flex-start; gap: 0.7rem; padding: 1.1rem 1.2rem; }}
  .ff-verdict-figure {{ font-size: 2.8rem; min-width: 0; text-align: left; }}
}}

.ff-footer {{ border-top: 1px solid #d2d2d7; margin-top: 2rem; padding-top: 1rem; }}
.ff-footer p {{ color: #86868b; font-size: 0.8rem; line-height: 1.5; margin: 0 0 0.5rem; }}


/* ---- The universe -------------------------------------------------------------------------------------
   A drawing of stars, small galaxies and planets fills the window and stays still while the page scrolls,
   over soft nebula glows. The planets and galaxies sit near the edges, so the cards never hide the text. */
.stApp {{
  background-color: {DOMINANT};
  background-image: url("{SPACE_BACKGROUND}"),
    radial-gradient(ellipse 60% 45% at 12% 8%, rgba(64, 76, 170, 0.20), transparent 70%),
    radial-gradient(ellipse 70% 50% at 70% 95%, rgba(37, 99, 235, 0.16), transparent 70%),
    linear-gradient(180deg, #050816 0%, #0a1030 55%, #060914 100%);
  background-size: cover, 100% 100%, 100% 100%, 100% 100%;
  background-position: center;
  background-attachment: fixed;
}}
[data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stBottomBlockContainer"] {{
  background: transparent;
}}

/* Sidebar: a darker pane of glass. */
[data-testid="stSidebar"] {{ background: rgba(6, 9, 26, 0.72); backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px); border-right: 1px solid rgba(160, 175, 255, 0.10); }}

/* Cards: frosted glass on the nebula, a thin light rim, and a soft glow under them. */
.st-key-ui_card_destination, .st-key-ui_card_conditions, .st-key-ui_card_ranking,
.st-key-ui_card_assistant, .st-key-ui_card_compare, .st-key-ui_card_gaps {{
  background: {SECONDARY}; border: 1px solid {SECONDARY_LINE} !important;
  backdrop-filter: blur(16px) saturate(140%); -webkit-backdrop-filter: blur(16px) saturate(140%);
  box-shadow: 0 18px 50px -20px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}}
.ff-stat, .ff-compact .ff-stat {{ background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(160, 175, 255, 0.10); }}
.ff-stat small {{ color: #8790b3; }}
.ff-stat strong.ff-unknown {{ -webkit-text-fill-color: #8790b3; color: #8790b3; }}
.ff-chip {{ background: rgba(255, 255, 255, 0.07); color: {INK}; border: 1px solid rgba(160, 175, 255, 0.16);
  box-shadow: none; backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); }}
.ff-header h1 {{ font-size: 2.9rem; }}
.ff-header .ff-mark {{ box-shadow: 0 0 18px rgba(232, 98, 42, 0.8); }}
.ff-bubble, .ff-bubble::before {{ background: rgba(255, 255, 255, 0.08); }}
.ff-disclaimer, .ff-footer p {{ color: #8790b3; }}
.ff-footer {{ border-top-color: rgba(160, 175, 255, 0.16); }}
[data-testid="stAlert"] {{ background: rgba(255, 255, 255, 0.06); }}
iframe {{ box-shadow: 0 30px 80px -20px rgba(0, 0, 0, 0.8); }}

/* The chatbot icon and the ANALYSE button glow a little, like the flame. */
.st-key-ui_chatbot, .st-key-ui_flamy {{ background: rgba(20, 26, 62, 0.82); border: 1px solid rgba(160, 175, 255, 0.18);
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  box-shadow: 0 10px 34px rgba(0, 0, 0, 0.55), 0 0 24px rgba(232, 98, 42, 0.18); }}
.st-key-ui_analyse button {{ background: {ACCENT};
  box-shadow: 0 0 28px rgba(232, 98, 42, 0.35); }}
.st-key-ui_analyse button:hover {{ background: #f2733a;
  box-shadow: 0 0 36px rgba(232, 98, 42, 0.5); }}

/* Keyboard focus stays clearly visible on the dark page. */
.stApp button:focus-visible, .stApp a:focus-visible {{ outline: 2px solid {FLAME}; outline-offset: 2px; }}

@media (max-width: 640px) {{
  .ff-stats {{ grid-template-columns: 1fr; }}
  .ff-section {{ margin-top: 4rem; }}
}}
</style>"""


def apply_style() -> None:
    """Add the site-wide style to the current page."""
    st.html(GLOBAL_STYLE)
