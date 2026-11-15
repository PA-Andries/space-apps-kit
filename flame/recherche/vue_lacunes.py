"""Le dessin de « What we don't know » : la grille de couverture et les règles de l'oxygène et de la pression.
Le même bloc sert à la page Investigations (rôle C) et à la page 1 (rôle F) : `afficher_ce_quon_ne_sait_pas`.

La page est sombre : des teintes claires sur des fonds translucides. Les textes affichés sont en anglais.
"""

from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from flame.recherche.lacunes_visuelles import couverture, regle_de_l_oxygene, regle_de_la_pression
from flame.ui import label

VERT = ("rgba(74, 222, 128, 0.14)", "#86efac")
ORANGE = ("rgba(251, 191, 36, 0.14)", "#fcd34d")
ROUGE = ("rgba(248, 113, 113, 0.16)", "#fca5a5")
GRIS = ("rgba(255, 255, 255, 0.06)", "#a3a9c4")
ACCENT = "#e8622a"


def _case(couleur: tuple[str, str], ligne1: str, ligne2: str = "") -> str:
    fond, texte = couleur
    dessous = f'<div style="font-size:0.75rem;opacity:0.85">{escape(ligne2)}</div>' if ligne2 else ""
    return (
        f'<div style="background:{fond};color:{texte};border-radius:12px;padding:0.6rem 0.4rem;'
        f'text-align:center;font-weight:600">{escape(ligne1)}{dessous}</div>'
    )


def _titre_de_ligne(titre: str, detail: str) -> str:
    return f'<div style="align-self:center">{escape(titre)}<br><small>{escape(detail)}</small></div>'


def _case_de_tests(tests: int | None, investigations: int | None, emule_seulement: bool = False) -> str:
    if tests is None:
        return _case(GRIS, "unknown")
    nombre = f"{tests} test" if tests == 1 else f"{tests} tests"
    if emule_seulement:
        return _case(ORANGE, nombre, "emulator only")
    if tests == 0:
        return _case(ROUGE, nombre, "never tested")
    return _case(VERT, nombre, f"{investigations} investigation" + ("" if investigations == 1 else "s"))


def grille_html(grille: dict) -> str:
    """La grille « combustible × atmosphère » : vert = testé, orange = émulateur seulement, rouge = jamais testé."""
    cases = grille["cases"]
    colonnes = f"minmax(9rem, 1.3fr) repeat({len(cases)}, minmax(0, 1fr))"
    morceaux = ["<div></div>"] + [
        f'<div style="text-align:center;color:{GRIS[1]};font-size:0.85rem">{escape(c["nom"].capitalize())}</div>'
        for c in cases
    ]
    morceaux.append(_titre_de_ligne("Your atmosphere", grille["atmosphere"] or "unknown"))
    morceaux += [_case_de_tests(c["tests"], c["investigations"], c["emule_seulement"]) for c in cases]

    legende = (
        f'<div style="font-size:0.75rem;color:{GRIS[1]};margin-top:0.5rem">'
        f'<span style="color:{VERT[1]}">■</span> tested · <span style="color:{ORANGE[1]}">■</span> only a gas '
        f'burner emulating a solid · <span style="color:{ROUGE[1]}">■</span> never tested</div>'
    )
    return (
        f'<div style="display:grid;grid-template-columns:{colonnes};gap:0.4rem;font-size:0.9rem">'
        f"{''.join(morceaux)}</div>{legende}"
    )


def _texte_de_plage(minimum: float | None, maximum: float | None, unite: str) -> str:
    if minimum is not None and maximum is not None:
        return f"{minimum:g} to {maximum:g} {unite}"
    return f"≥ {minimum:g} {unite}" if minimum is not None else f"≤ {maximum:g} {unite}"


def _texte_du_trou(debut: float | None, fin: float | None, unite: str) -> str:
    """« never tested above 22.2 % », « never tested below 43.2 kPa » ou « never tested: 22.2 to 23 % »."""
    if fin is None:
        return f"never tested above {debut:g} {unite}"
    if debut is None:
        return f"never tested below {fin:g} {unite}"
    return f"never tested: {debut:g} to {fin:g} {unite}"


def regle_figure(regle: dict, habitat: str | None, nom: str = "oxygen", unite: str = "%") -> go.Figure:
    """Une règle (oxygène ou pression) : une ligne par combustible (la plage testée en vert), l'environnement en
    bas (orange), et en pointillé rouge ce que l'environnement demande et qu'aucun test n'a atteint : la zone
    part du bord de la plage testée et contient l'environnement quand il n'a jamais été testé."""
    env_min, env_max = regle["environnement"]
    lignes = regle["combustibles"]
    valeurs = [borne for ligne in lignes if ligne["plage"] for borne in ligne["plage"]]
    valeurs += [borne for borne in (env_min, env_max) if borne is not None]
    plafond = 100.0 if unite == "%" else float("inf")
    bord = min(plafond, max(valeurs + [10.0]) * 1.08)
    if unite == "%" and env_min is not None and env_max is None:
        bord = 100.0  # un oxygène sans borne haute va jusqu'à 100 % : l'axe aussi
    figure = go.Figure()
    noms = ["Your environment"]
    for rang, ligne in enumerate(reversed(lignes), start=1):
        noms.append(f"{ligne['nom'].capitalize()} fuel")
        if ligne["plage"] is None:
            figure.add_annotation(
                x=bord / 2, y=rang, text=f"no {nom} recorded", showarrow=False, font={"color": GRIS[1], "size": 12}
            )
            continue
        bas, haut = ligne["plage"]
        for debut, fin in ligne["trous"]:
            x0, x1 = (0 if debut is None else debut), (bord if fin is None else fin)
            figure.add_shape(
                type="rect",
                x0=x0,
                x1=x1,
                y0=rang - 0.3,
                y1=rang + 0.3,
                fillcolor=ROUGE[0],
                line={"color": ROUGE[1], "dash": "dot", "width": 1.5},
            )
            # Le texte sous la zone, collé au bord qui laisse de la place (sinon il sortirait du graphique).
            a_gauche = (x0 + x1) / 2 < bord / 2
            figure.add_annotation(
                x=x0 if a_gauche else x1,
                y=rang - 0.3,
                text=_texte_du_trou(debut, fin, unite),
                showarrow=False,
                xanchor="left" if a_gauche else "right",
                yanchor="top",
                font={"color": ROUGE[1], "size": 11},
            )
        # Une plage étroite (99.2 à 99.5 kPa sur un axe de 500) garde une largeur visible, centrée sur elle.
        marge = max(0.0, bord * 0.012 - (haut - bas)) / 2
        figure.add_shape(
            type="rect",
            x0=bas - marge,
            x1=haut + marge,
            y0=rang - 0.25,
            y1=rang + 0.25,
            fillcolor=VERT[1],
            opacity=0.85,
            line_width=0,
        )
        figure.add_annotation(
            x=bas,
            y=rang + 0.25,
            text=f"tested {bas:g} to {haut:g} {unite}" + (f" ({ligne['source']})" if ligne.get("source") else ""),
            showarrow=False,
            xanchor="left",
            yanchor="bottom",
            font={"color": VERT[1], "size": 11},
        )
    if env_min is None and env_max is None:
        figure.add_annotation(
            x=bord / 2, y=0, text=f"your {nom} is unknown", showarrow=False, font={"color": GRIS[1], "size": 12}
        )
    else:
        debut, fin = (env_min if env_min is not None else 0), (env_max if env_max is not None else bord)
        figure.add_shape(type="rect", x0=debut, x1=fin, y0=-0.25, y1=0.25, fillcolor=ACCENT, opacity=0.85, line_width=0)
        figure.add_annotation(
            x=debut,
            y=-0.25,
            text=f"your {label(habitat) or 'environment'}: {_texte_de_plage(env_min, env_max, unite)}",
            showarrow=False,
            xanchor="left",
            yanchor="top",
            font={"color": ACCENT, "size": 11},
        )
    figure.update_xaxes(range=[0, bord], ticksuffix=f" {unite}", showgrid=False, zeroline=False)
    figure.update_yaxes(
        range=[-0.8, len(lignes) + 0.7], tickvals=list(range(len(noms))), ticktext=noms, showgrid=False, zeroline=False
    )
    figure.update_layout(
        height=120 + 70 * len(lignes),
        margin={"t": 10, "b": 30, "l": 10, "r": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    return figure


def afficher_ce_quon_ne_sait_pas(fiches: pd.DataFrame, tests: pd.DataFrame, scenario: dict | None, cle: str) -> None:
    """Dessine les visuels de « What we don't know » : la grille, puis les règles de l'oxygène et de la pression,
    avec les phrases qui ne rentrent pas dans une case.

    `cle` : le début des clés Streamlit de la page qui l'affiche (« recherche », « ui »).
    """
    scenario = scenario or {}
    habitat = scenario.get("habitat")
    st.markdown("**Tests in your conditions, by fuel**")
    grille = couverture(fiches, tests, scenario)
    st.html(grille_html(grille))
    if grille["atmosphere"] is None:
        st.caption("Your environment gives no oxygen or pressure, so no test can be placed in it.")

    st.markdown("**Oxygen: where each fuel was tested**")
    oxygene = regle_de_l_oxygene(fiches, tests, scenario)
    st.plotly_chart(regle_figure(oxygene, habitat), config={"staticPlot": True}, key=f"{cle}_regle_oxygene")
    if oxygene["emule"] is not None:
        st.caption(
            f"Not counted in solids: {oxygene['emulateurs']}, a gas burner that emulates a burning solid, "
            f"goes up to {oxygene['emule']:g} % oxygen."
        )

    st.markdown("**Pressure: where each fuel was tested**")
    pression = regle_de_la_pression(fiches, tests, scenario)
    st.plotly_chart(
        regle_figure(pression, habitat, "pressure", "kPa"), config={"staticPlot": True}, key=f"{cle}_regle_pression"
    )
    if any(ligne["plage"] is None for ligne in pression["combustibles"]):
        st.caption("PSI's test tables give no pressure for some fuels.")
    for ligne in pression["combustibles"]:
        if ligne.get("source"):
            st.caption(
                f"{ligne['nom'].capitalize()}: PSI's test tables give no pressure, so the range comes from "
                f"NASA's {ligne['source']}."
            )
