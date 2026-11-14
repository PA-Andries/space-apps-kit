"""Text blocks of the home page: the opening, section titles, key figures, footer (styles in style.py)."""

from html import escape

import streamlit as st


def hero(eyebrow: str, title: str, lead: str, accent: str = "", actions: list[tuple[str, str]] | None = None) -> None:
    """The big centred opening of a page.

    `accent`: words added after the title, painted in the flame gradient. `actions`: links
    [(text, "#anchor"), ...]; the first is a filled pill, the others are text links with a chevron.
    """
    painted = f' <span class="ff-gradient">{escape(accent)}</span>' if accent else ""
    links = []
    for i, (text, target) in enumerate(actions or []):
        kind = "ff-cta" if i == 0 else "ff-more"
        links.append(f'<a class="{kind}" href="{escape(target)}" target="_self">{escape(text)}</a>')
    buttons = f'<div class="ff-actions">{"".join(links)}</div>' if links else ""
    st.html(
        f'<div class="ff-hero"><p class="ff-eyebrow">{escape(eyebrow)}</p>'
        f'<h1>{escape(title)}{painted}</h1><p class="ff-lead">{escape(lead)}</p>{buttons}</div>'
    )


def section(title: str, subtitle: str = "", step: str = "", anchor: str = "") -> None:
    """A centred section title, with an optional small orange `step` above and a grey line below.

    `anchor`: an id, so that a link to "#anchor" scrolls here.
    """
    above = f'<p class="ff-step">{escape(step)}</p>' if step else ""
    below = f"<p>{escape(subtitle)}</p>" if subtitle else ""
    target = f' id="{escape(anchor)}"' if anchor else ""
    st.html(f'<div class="ff-section"{target}>{above}<h2>{escape(title)}</h2>{below}</div>')


def stat_tiles(tiles: list[tuple[str | None, str]], note: str = "") -> None:
    """A row of key figures: [(value, caption), ...]. A value of None shows "Not given", never a guess."""
    cells = []
    for value, caption in tiles:
        if value is None:
            figure = '<strong class="ff-unknown">Not given</strong>'
        else:
            figure = f"<strong>{escape(value)}</strong>"
        cells.append(f'<div class="ff-stat"><span>{escape(caption)}</span>{figure}</div>')
    st.html(f'<div class="ff-stats">{"".join(cells)}</div>')
    if note:
        st.html(f'<p class="ff-note">{escape(note)}</p>')


def footer(lines: list[str]) -> None:
    """Small grey lines at the bottom of a page, under a thin rule."""
    text = "".join(f"<p>{escape(line)}</p>" for line in lines)
    st.html(f'<footer class="ff-footer">{text}</footer>')
