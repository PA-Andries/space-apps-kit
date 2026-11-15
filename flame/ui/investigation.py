"""The detailed card of one investigation: what the experiment studied, and why it matters for the environment.

Used by page 1 (the 3 most relevant) and by the Investigations page (the ranking). The texts come from role C's
`descriptif()`: this file only lays them out, in the same frosted glass as the other cards.
"""

from html import escape

import pandas as pd
import streamlit as st

from flame.ui.style import FLAME, MUTED

DETAILS_STYLE = f"""<style>
.ff-inv-head {{ display: flex; align-items: baseline; gap: 0.6rem; flex-wrap: wrap; }}
.ff-inv-rank {{ display: inline-flex; align-items: center; justify-content: center; flex: none; width: 1.7rem;
  height: 1.7rem; border-radius: 50%; background: {FLAME}; color: #fff; font-size: 0.85rem; font-weight: 700; }}
.ff-inv-head h4 {{ font-size: 1.08rem; font-weight: 700; letter-spacing: -0.02em; margin: 0; padding: 0; }}
.ff-inv-head small {{ color: {MUTED}; font-size: 0.85rem; }}
.ff-inv-title {{ color: {MUTED}; font-size: 0.9rem; margin: 0.15rem 0 0; }}
.ff-inv-meta {{ color: {MUTED}; font-size: 0.8rem; margin: 0.25rem 0 0; }}
.ff-inv-label {{ display: block; color: {FLAME}; font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; margin: 0.7rem 0 0.15rem; }}
.ff-inv-text {{ font-size: 0.92rem; line-height: 1.5; margin: 0; }}
.ff-inv-text b {{ font-weight: 700; }}
.ff-inv-why {{ margin: 0; padding-left: 1.1rem; font-size: 0.9rem; line-height: 1.5; }}
.ff-inv-why li {{ margin: 0.1rem 0; }}
.ff-inv-why b {{ font-weight: 700; }}
</style>"""


def investigation_details(row: pd.Series, details: dict, rank: int | None = None, place: str = "") -> None:
    """Show an investigation with its summary and the reasons of its rank.

    `details`: the dict of `flame.recherche.descriptif(...)`. `rank`: its place in the ranking (1, 2, 3...).
    `place`: the environment's name, for the title of the reasons ("Why it matters for Moon base").
    """
    st.html(DETAILS_STYLE)
    with st.container(border=True):
        badge = f'<span class="ff-inv-rank">{rank}</span>' if rank else ""
        title = f'<p class="ff-inv-title">{escape(details["titre"])}</p>' if details.get("titre") else ""
        # No small grey line (PSI number, fuel and hardware): Mathéo wants none in the cards.
        blocks = [f'<div class="ff-inv-head">{badge}<h4>{escape(str(row["nom"]))}</h4></div>{title}']
        studied = "".join(
            f'<p class="ff-inv-text">{text}</p>'
            for text in (
                f"<b>{escape(details['en_bref'])}</b>" if details.get("en_bref") else "",
                escape(details.get("objectif_court", "")),
            )
            if text
        )
        if studied:
            blocks.append(f'<span class="ff-inv-label">What the experiment studied</span>{studied}')
        reasons = "".join(
            f"<li><b>{escape(criterion)}:</b> {escape(reason)}</li>" for criterion, reason in details.get("raisons", [])
        )
        if details.get("citee"):
            reasons += f"<li><b>Statement:</b> {escape(details['citee'])}</li>"
        if reasons:
            where = f" for {escape(place)}" if place else ""
            blocks.append(
                f'<span class="ff-inv-label">Why it matters{where}</span><ul class="ff-inv-why">{reasons}</ul>'
            )
        st.html("".join(blocks))
        if details.get("textes"):
            with st.expander("NASA's full description"):
                st.html(
                    "".join(
                        f'<span class="ff-inv-label">{escape(heading)}</span><p class="ff-inv-text">{escape(text)}</p>'
                        for heading, text in details["textes"].items()
                    )
                )
                st.caption("Text from NASA's Physical Sciences Informatics (PSI) record, unchanged.")
        compare, source = st.columns(2)
        with compare:
            st.page_link("pages/comparateur.py", label="Compare  ›", query_params={"id": row["id"]})
        with source:
            if pd.notna(row.get("source_psi")):
                st.link_button("View on PSI", row["source_psi"])
