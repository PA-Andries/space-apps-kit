"""Text blocks of the home page: the opening, section titles and key figures (styles in style.py)."""

from html import escape

import streamlit as st


def hero(eyebrow: str, title: str, lead: str) -> None:
    """The big centred opening of a page: small orange line, large headline, grey lead text."""
    st.html(
        f'<div class="ff-hero"><p class="ff-eyebrow">{escape(eyebrow)}</p>'
        f'<h1>{escape(title)}</h1><p class="ff-lead">{escape(lead)}</p></div>'
    )


def section(title: str, subtitle: str = "") -> None:
    """A centred section title, with an optional grey line below."""
    below = f"<p>{escape(subtitle)}</p>" if subtitle else ""
    st.html(f'<div class="ff-section"><h2>{escape(title)}</h2>{below}</div>')


def stat_tiles(tiles: list[tuple[str | None, str]], note: str = "") -> None:
    """A row of key figures: [(value, caption), ...]. A value of None shows "Unknown"."""
    cells = []
    for value, caption in tiles:
        figure = escape(value) if value is not None else "Unknown"
        style = "" if value is not None else ' class="ff-unknown"'
        cells.append(f'<div class="ff-stat"><strong{style}>{figure}</strong><span>{escape(caption)}</span></div>')
    st.html(f'<div class="ff-stats">{"".join(cells)}</div>')
    if note:
        st.html(f'<p class="ff-note">{escape(note)}</p>')
