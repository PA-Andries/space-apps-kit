"""The look of the whole site, applied once per page by the top bar.

Inspired by clean product sites: lots of space, a light grey page with white cards, large tight headlines,
pill-shaped buttons, soft shadows. Colours come from `.streamlit/config.toml`; this adds what the theme
cannot set (font, spacing, shapes).
"""

import streamlit as st

INK = "#1d1d1f"  # main text
MUTED = "#6e6e73"  # secondary text
FLAME = "#e0662a"  # main colour (same as primaryColor in config.toml)

GLOBAL_STYLE = f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Font: Inter on text, never on the icon font. */
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp button, .stApp h1, .stApp h2, .stApp h3,
.stApp [data-testid="stMarkdownContainer"], .stApp [data-baseweb="select"] {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}
.stApp h1, .stApp h2, .stApp h3 {{ color: {INK}; letter-spacing: -0.025em; font-weight: 700; }}

/* A centred column with room to breathe. */
.stMainBlockContainer, .block-container {{ max-width: 1080px; padding-top: 2rem; padding-bottom: 6rem; }}

/* Pill-shaped buttons and links, with a soft lift on hover. */
.stButton button, .stLinkButton a, [data-testid="stPageLink"] a {{
  border-radius: 980px; font-weight: 500; transition: transform 0.15s, box-shadow 0.15s;
}}
[data-testid="stPageLink"] a {{ color: {FLAME}; }}
[data-testid="stPageLink"] a:hover {{ text-decoration: underline; }}

/* 3D scenes: large round-cornered windows on space, with a soft shadow. */
iframe {{ border-radius: 28px; box-shadow: 0 24px 60px rgba(29, 29, 31, 0.18); }}

/* Alerts and bordered containers as soft white cards. */
[data-testid="stAlert"] {{ border-radius: 18px; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 22px; }}

/* Home page text blocks (see flame/ui/home.py). */
.ff-hero {{ text-align: center; padding: 3.5rem 0 2.5rem; }}
.ff-eyebrow {{ color: {FLAME}; font-weight: 600; font-size: 1.05rem; margin: 0 0 0.6rem; letter-spacing: 0; }}
.ff-hero h1 {{ font-size: clamp(2.6rem, 6vw, 4.4rem); line-height: 1.04; margin: 0 auto; max-width: 14ch; padding: 0; }}
.ff-lead {{ color: {MUTED}; font-size: clamp(1.1rem, 2vw, 1.45rem); line-height: 1.4; max-width: 34ch;
  margin: 1.2rem auto 0; font-weight: 500; }}
.ff-section {{ text-align: center; margin: 4.5rem 0 1.6rem; }}
.ff-section h2 {{ font-size: clamp(1.9rem, 4vw, 2.8rem); margin: 0; padding: 0; }}
.ff-section p {{ color: {MUTED}; font-size: 1.15rem; margin: 0.5rem 0 0; }}
.ff-stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 0 0 1.5rem; }}
.ff-stat {{ background: #fff; border-radius: 24px; padding: 1.6rem 1rem; text-align: center;
  box-shadow: 0 2px 12px rgba(29, 29, 31, 0.06); }}
.ff-stat strong {{ display: block; font-size: clamp(1.8rem, 4vw, 2.8rem); font-weight: 700; color: {INK};
  letter-spacing: -0.03em; line-height: 1.1; }}
.ff-stat strong.ff-unknown {{ color: {MUTED}; font-size: clamp(1.3rem, 3vw, 1.8rem); }}
.ff-stat span {{ color: {MUTED}; font-size: 0.95rem; font-weight: 500; }}
.ff-note {{ color: {MUTED}; font-size: 0.9rem; text-align: center; margin: 0 0 1rem; }}
@media (max-width: 640px) {{ .ff-stats {{ grid-template-columns: 1fr; }} }}
</style>"""


def apply_style() -> None:
    """Add the site-wide style to the current page."""
    st.html(GLOBAL_STYLE)
