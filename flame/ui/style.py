"""The look of the whole site, applied once per page by the top bar.

A space universe that stays easy to use: a deep night-blue page with soft nebula glows and a field of
stars, frosted-glass cards with light text, pill buttons, links in the flame colour, and a gentle rise of
each block as the page appears. Colours come from `.streamlit/config.toml`; this adds what the theme
cannot set (font, background, glass, shapes, motion). Text keeps a strong contrast on the dark glass.
"""

import base64
from pathlib import Path

import streamlit as st

INK = "#eef1fb"  # main text, on the dark page
MUTED = "#a3abc9"  # secondary text, still readable on the dark glass
FLAME = "#ff7a3d"  # main colour (same as primaryColor in config.toml)
GRADIENT = "linear-gradient(90deg, #fbbf24 0%, #ff7a3d 45%, #f0457a 100%)"  # sunrise, for big words

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
.stMainBlockContainer, .block-container {{ max-width: 1440px; padding: 1.2rem 2rem 2rem; }}

/* Pill-shaped buttons, with a soft lift on hover. */
.stButton button, .stLinkButton a {{
  border-radius: 980px; font-weight: 500; transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
}}
[data-testid="stPageLink"] a {{ justify-content: center; }}
[data-testid="stPageLink"] a p {{ color: {FLAME}; font-size: 1.15rem; font-weight: 500; }}
[data-testid="stPageLink"] a:hover {{ background: transparent; }}
[data-testid="stPageLink"] a:hover p {{ text-decoration: underline; }}

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
.ff-more:hover {{ text-decoration: underline !important; }}

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
.ff-stat small {{ display: block; color: #86868b; font-size: 0.72rem; margin-top: 0.25rem; }}

/* The chatbot icon, pinned to the bottom-right corner (sketch 1 of the whiteboard). */
.st-key-ui_chatbot {{ position: fixed; right: 22px; bottom: 18px; z-index: 1000; width: 112px; gap: 0;
  background: #fff; border-radius: 24px; padding: 0.3rem 0.4rem 0.4rem;
  box-shadow: 0 10px 30px rgba(29, 29, 31, 0.18); }}
.st-key-ui_chatbot iframe {{ box-shadow: none; border-radius: 0; background: transparent; }}
.st-key-ui_chatbot [data-testid="stPageLink"] a {{ justify-content: center; padding: 0; }}
.st-key-ui_chatbot [data-testid="stPageLink"] p {{ font-size: 0.85rem; font-weight: 600; }}

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

/* The ANALYSE button under the chart. */
.st-key-ui_analyse button {{ background: {FLAME}; color: #fff; border: none; letter-spacing: 0.08em; font-weight: 700;
  padding: 0.6rem 2.2rem; }}
.st-key-ui_analyse button:hover {{ background: #c9541c; color: #fff; }}
.st-key-ui_analyse {{ align-items: center; }}
.ff-footer {{ border-top: 1px solid #d2d2d7; margin-top: 2rem; padding-top: 1rem; }}
.ff-footer p {{ color: #86868b; font-size: 0.8rem; line-height: 1.5; margin: 0 0 0.5rem; }}


/* ---- The universe -------------------------------------------------------------------------------------
   A drawing of stars, small galaxies and planets fills the window and stays still while the page scrolls,
   over soft nebula glows. The planets and galaxies sit near the edges, so the cards never hide the text. */
.stApp {{
  background-color: #070a1c;
  background-image: url("{SPACE_BACKGROUND}"),
    radial-gradient(ellipse 60% 45% at 12% 8%, rgba(124, 58, 237, 0.18), transparent 70%),
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
  background: rgba(20, 26, 62, 0.58); border: 1px solid rgba(160, 175, 255, 0.14) !important;
  backdrop-filter: blur(16px) saturate(140%); -webkit-backdrop-filter: blur(16px) saturate(140%);
  box-shadow: 0 18px 50px -20px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}}
.ff-stat, .ff-compact .ff-stat {{ background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(160, 175, 255, 0.10); }}
.ff-stat small {{ color: #8790b3; }}
.ff-stat strong.ff-unknown {{ -webkit-text-fill-color: #8790b3; color: #8790b3; }}
.ff-chip {{ background: rgba(255, 255, 255, 0.07); color: {INK}; border: 1px solid rgba(160, 175, 255, 0.16);
  box-shadow: none; backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); }}
.ff-header h1 {{ font-size: 2.2rem; }}
.ff-header .ff-mark {{ box-shadow: 0 0 18px rgba(255, 122, 61, 0.8); }}
.ff-bubble, .ff-bubble::before {{ background: rgba(255, 255, 255, 0.08); }}
.ff-disclaimer, .ff-footer p {{ color: #8790b3; }}
.ff-footer {{ border-top-color: rgba(160, 175, 255, 0.16); }}
[data-testid="stAlert"] {{ background: rgba(255, 255, 255, 0.06); }}
iframe {{ box-shadow: 0 30px 80px -20px rgba(0, 0, 0, 0.8); }}

/* The chatbot icon and the ANALYSE button glow a little, like the flame. */
.st-key-ui_chatbot {{ background: rgba(20, 26, 62, 0.82); border: 1px solid rgba(160, 175, 255, 0.18);
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  box-shadow: 0 10px 34px rgba(0, 0, 0, 0.55), 0 0 24px rgba(255, 122, 61, 0.18); }}
.st-key-ui_analyse button {{ background: linear-gradient(135deg, #ff9a3d, #e0662a 55%, #d9365e);
  box-shadow: 0 0 28px rgba(255, 122, 61, 0.35); }}
.st-key-ui_analyse button:hover {{ background: linear-gradient(135deg, #ffab5c, #f0763a 55%, #e44a70);
  box-shadow: 0 0 36px rgba(255, 122, 61, 0.5); }}

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
