"""The look of the whole site, applied once per page by the top bar.

Inspired by Apple's product pages: a frosted bar, very large tight headlines, a light grey page with
white tiles, pill buttons, blue-free "Learn more ›" links in the flame colour, soft shadows and a gentle
rise of each block as the page appears. Colours come from `.streamlit/config.toml`; this adds what the
theme cannot set (font, spacing, shapes, motion).
"""

import streamlit as st

INK = "#1d1d1f"  # main text
MUTED = "#6e6e73"  # secondary text
FLAME = "#e0662a"  # main colour (same as primaryColor in config.toml)
GRADIENT = "linear-gradient(90deg, #f59e0b 0%, #e0662a 45%, #d9365e 100%)"  # sunrise, for big words

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
.stMainBlockContainer, .block-container {{ max-width: 1040px; padding-top: 1rem; padding-bottom: 3rem; }}

/* Pill-shaped buttons, with a soft lift on hover. */
.stButton button, .stLinkButton a {{
  border-radius: 980px; font-weight: 500; transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
}}
[data-testid="stPageLink"] a {{ justify-content: center; }}
[data-testid="stPageLink"] a p {{ color: {FLAME}; font-size: 1.15rem; font-weight: 500; }}
[data-testid="stPageLink"] a:hover {{ background: transparent; }}
[data-testid="stPageLink"] a:hover p {{ text-decoration: underline; }}

/* 3D scenes: large round-cornered windows on space, with a soft, wide shadow. */
iframe {{ border-radius: 30px; box-shadow: 0 30px 80px -20px rgba(29, 29, 31, 0.35); }}

/* Alerts and bordered containers as soft white tiles. */
[data-testid="stAlert"] {{ border-radius: 18px; border: none; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 22px; }}

/* Each block rises gently into place. */
@keyframes ff-rise {{ from {{ opacity: 0; transform: translateY(18px); }} to {{ opacity: 1; transform: none; }} }}
.ff-hero, .ff-section, .ff-stats, .st-key-ui_pillars, .ff-footer {{
  animation: ff-rise 0.8s cubic-bezier(0.2, 0.7, 0.2, 1) both;
}}
@media (prefers-reduced-motion: reduce) {{ .ff-hero, .ff-section, .ff-stats, .st-key-ui_pillars, .ff-footer {{
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
.ff-footer {{ border-top: 1px solid #d2d2d7; margin-top: 6rem; padding-top: 1.2rem; }}
.ff-footer p {{ color: #86868b; font-size: 0.8rem; line-height: 1.5; margin: 0 0 0.5rem; }}

@media (max-width: 640px) {{
  .ff-stats {{ grid-template-columns: 1fr; }}
  .ff-section {{ margin-top: 4rem; }}
}}
</style>"""


def apply_style() -> None:
    """Add the site-wide style to the current page."""
    st.html(GLOBAL_STYLE)
