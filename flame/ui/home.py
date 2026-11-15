"""Text blocks of the dashboard: header, card titles, key figures, mascot, footer (styles in style.py)."""

from contextlib import contextmanager
from html import escape

import streamlit as st

from flame.ui.scene import mascot_scene


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


def dashboard_header(title: str, subtitle: str, chips: list[str], eyebrow: str = "") -> None:
    """The dashboard's top line: the name with a flame mark, a grey subtitle, and small figure chips on the right.

    `eyebrow`: a small orange line above the title, for example the name of the page.
    """
    badges = "".join(f'<span class="ff-chip">{escape(chip)}</span>' for chip in chips)
    above = f'<span class="ff-tag">{escape(eyebrow)}</span>' if eyebrow else ""
    st.html(
        f'<div class="ff-header"><div>{above}<h1><span class="ff-mark"></span>{escape(title)}</h1>'
        f'<p>{escape(subtitle)}</p></div><div class="ff-chips">{badges}</div></div>'
    )


def verdict_banner(figure: str, title: str, sentence: str, source: str, note: str = "", severe: bool = True) -> None:
    """The one thing the page says, at the top: a big figure, a title, a sentence and its source.

    `figure`: the number to read first ("22.2 %", "0", "—"). `note`: an extra line, for example what
    would fill the gap. `severe` paints the figure in the flame colour; otherwise it stays ink-coloured.
    The 60-30-10 rule of the site: this banner is the only place of the page where the figure is painted.
    """
    kind = "ff-verdict ff-severe" if severe else "ff-verdict"
    extra = f'<p class="ff-verdict-note">{escape(note)}</p>' if note else ""
    st.html(
        f'<section class="{kind}"><div class="ff-verdict-figure">{escape(figure)}</div>'
        f'<div class="ff-verdict-words"><h2>{escape(title)}</h2><p>{escape(sentence)}</p>'
        f'<p class="ff-verdict-source">Source: {escape(source)}</p>{extra}</div></section>'
    )


def card_title(title: str, subtitle: str = "", tag: str = "") -> None:
    """The title line of a dashboard card, with an optional grey hint.

    `tag`: a small orange line above the title, for example the challenge objective the card answers.
    """
    above = f'<span class="ff-tag">{escape(tag)}</span>' if tag else ""
    below = f"<p>{escape(subtitle)}</p>" if subtitle else ""
    st.html(f'<div class="ff-card-title">{above}<h3>{escape(title)}</h3>{below}</div>')


def stat_tiles(tiles: list[tuple], note: str = "", compact: bool = False, grid: bool = False) -> None:
    """A row of key figures: [(value, caption), ...] or [(value, caption, small line), ...].

    A value of None shows "Not given", never a guess. The small line goes under the value (a source).

    `compact`: smaller tiles, for a dashboard card. `grid`: two tiles per row (a 2 × 2 grid for four).
    """
    cells = []
    for value, caption, *small in tiles:
        below = f"<small>{escape(small[0])}</small>" if small else ""
        if value is None:
            figure = '<strong class="ff-unknown">Not given</strong>'
        else:
            figure = f"<strong>{escape(value)}</strong>"
        cells.append(f'<div class="ff-stat"><span>{escape(caption)}</span>{figure}{below}</div>')
    # La classe dit combien de tuiles : à deux ou à une, la rangée se centre au lieu de laisser
    # une colonne vide à droite (demande d'Ethan, dim. 15 nov.).
    size = (" ff-compact" if compact else "") + (" ff-grid2" if grid else "") + f" ff-cols{len(cells)}"
    st.html(f'<div class="ff-stats{size}">{"".join(cells)}</div>')
    if note:
        st.html(f'<p class="ff-note">{escape(note)}</p>')


def footer(lines: list[str]) -> None:
    """Small grey lines at the bottom of a page, under a thin rule."""
    text = "".join(f"<p>{escape(line)}</p>" for line in lines)
    st.html(f'<footer class="ff-footer">{text}</footer>')


def mascot(message: str, link: tuple[str, str] | None = None) -> None:
    """The cartoon flame mascot with a speech bubble: `mascot("Hi!", ("pages/assistant.py", "Ask me ›"))`.

    `link`: an optional (page, text) shown under the bubble. Any page may use it, the Assistant page first.
    """
    with st.container(key="ui_mascot"):
        figure, words = st.columns([1, 2.2], vertical_alignment="center")
        with figure:
            mascot_scene(height=170)
        with words:
            st.html(f'<div class="ff-bubble">{escape(message)}</div>')
            if link:
                st.page_link(link[0], label=link[1])


def chatbot_button(page: str) -> None:
    """The chatbot icon pinned to the bottom-right corner of the page: Flamy the mascot, and a link to `page`."""
    with st.container(key="ui_chatbot"):
        mascot_scene(height=96)
        st.page_link(page, label="Flamy", icon=":material/forum:")


def assistant_mascot() -> None:
    """Flamy, the flame mascot of the Assistant page, peeking out from behind the chat box on the left.

    As in a messaging app: only its head and shoulders show above the box; while `talking()` is open
    it rises a little and talks. It is placed in the bottom bar, just before the chat box.
    """
    # The bottom bar of the page (where the chat box lives); the main page if this Streamlit has none.
    bottom = getattr(st, "bottom", st)
    with bottom.container(key="ui_assistant_mascot"):
        mascot_scene(height=170, calm=True)  # almost still: Flamy just looks at the visitor


@contextmanager
def talking():
    """While this block runs, the mascot on the page talks.

    It shows a hidden marker that the mascot's scene looks for; the scene never reloads.

        with talking():
            answer = ...
    """
    marker = st.empty()
    marker.html('<span class="ff-talking" aria-hidden="true"></span>')
    try:
        yield
    finally:
        marker.empty()
