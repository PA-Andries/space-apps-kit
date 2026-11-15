"""Le dessin de « What we don't know » : la grille de couverture, la règle de l'oxygène et les carrés des mesures
notées. Le même bloc sert à la page Investigations (rôle C) et à la page 1 (rôle F) : `afficher_ce_quon_ne_sait_pas`.

La page est sombre : des teintes claires sur des fonds translucides. Les textes affichés sont en anglais.
"""

from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from flame.recherche.lacunes_visuelles import couverture, mesures_notees, regle_de_l_oxygene
from flame.ui import label

VERT = ("rgba(74, 222, 128, 0.14)", "#86efac")
ORANGE = ("rgba(251, 191, 36, 0.14)", "#fcd34d")
ROUGE = ("rgba(248, 113, 113, 0.16)", "#fca5a5")
GRIS = ("rgba(255, 255, 255, 0.06)", "#a3a9c4")
ACCENT = "#ff7a3d"
BLEU_NOTE = "#8fa3d9"


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


def _texte_de_plage(minimum: float | None, maximum: float | None) -> str:
    if minimum is not None and maximum is not None:
        return f"{minimum:g} to {maximum:g} %"
    return f"≥ {minimum:g} %" if minimum is not None else f"≤ {maximum:g} %"


def regle_figure(regle: dict, habitat: str | None) -> go.Figure:
    """La règle de l'oxygène : une ligne par combustible (la plage testée), l'environnement en bas,
    et pour chaque combustible le trou jamais testé jusqu'à l'environnement, en pointillé rouge."""
    env_min, env_max = regle["environnement"]
    lignes = regle["combustibles"]
    hauts = [ligne["plage"][1] for ligne in lignes if ligne["plage"]]
    bord = min(100.0, max([45.0, (env_max or 0) + 5, (env_min or 0) + 10] + [haut + 5 for haut in hauts]))
    figure = go.Figure()
    noms = ["Your environment"]
    for rang, ligne in enumerate(reversed(lignes), start=1):
        noms.append(f"{ligne['nom'].capitalize()} fuel")
        if ligne["plage"] is None:
            figure.add_annotation(
                x=bord / 2, y=rang, text="no oxygen recorded", showarrow=False, font={"color": GRIS[1], "size": 12}
            )
            continue
        bas, haut = ligne["plage"]
        figure.add_shape(
            type="rect", x0=bas, x1=haut, y0=rang - 0.25, y1=rang + 0.25, fillcolor=VERT[1], opacity=0.85, line_width=0
        )
        figure.add_annotation(
            x=bas,
            y=rang + 0.25,
            text=f"tested {bas:g} to {haut:g} %",
            showarrow=False,
            xanchor="left",
            yanchor="bottom",
            font={"color": VERT[1], "size": 11},
        )
        if ligne["trou"] is not None:
            debut, fin = ligne["trou"]
            figure.add_shape(
                type="rect",
                x0=debut,
                x1=fin,
                y0=rang - 0.3,
                y1=rang + 0.3,
                fillcolor=ROUGE[0],
                line={"color": ROUGE[1], "dash": "dot", "width": 1.5},
            )
            # Le texte à droite du trou (un trou étroit ne le contiendrait pas).
            figure.add_annotation(
                x=fin,
                y=rang,
                text=f"  never tested · {ligne['ecart']:g} %",
                showarrow=False,
                xanchor="left",
                font={"color": ROUGE[1], "size": 12},
            )
    if env_min is None and env_max is None:
        figure.add_annotation(
            x=bord / 2, y=0, text="your oxygen is unknown", showarrow=False, font={"color": GRIS[1], "size": 12}
        )
    else:
        debut, fin = (env_min if env_min is not None else 0), (env_max if env_max is not None else bord)
        figure.add_shape(type="rect", x0=debut, x1=fin, y0=-0.25, y1=0.25, fillcolor=ACCENT, opacity=0.85, line_width=0)
        figure.add_annotation(
            x=debut,
            y=-0.25,
            text=f"your {label(habitat) or 'environment'}: {_texte_de_plage(env_min, env_max)}",
            showarrow=False,
            xanchor="left",
            yanchor="top",
            font={"color": ACCENT, "size": 11},
        )
    figure.update_xaxes(range=[0, bord], ticksuffix=" %", showgrid=False, zeroline=False)
    figure.update_yaxes(
        range=[-0.8, len(lignes) + 0.7], tickvals=list(range(len(noms))), ticktext=noms, showgrid=False, zeroline=False
    )
    figure.update_layout(
        height=110 + 62 * len(lignes),
        margin={"t": 10, "b": 30, "l": 10, "r": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    return figure


def mesures_html(mesures: dict[str, list[tuple[str, bool]]]) -> str:
    """Un carré par investigation : plein si NASA a noté la mesure, vide et cerclé de rouge sinon."""
    lignes = []
    for nom, fiches_notees in mesures.items():
        notees = sum(notee for _, notee in fiches_notees)
        # Les mesures notées d'abord : la ligne se lit comme une jauge.
        ordre = sorted(fiches_notees, key=lambda paire: not paire[1])
        carres = "".join(
            f'<span title="{escape(investigation)}" style="display:inline-block;width:18px;height:18px;'
            "border-radius:4px;margin:0 4px 4px 0;box-sizing:border-box;"
            + (f"background:{BLEU_NOTE}" if notee else f"border:1.5px solid {ROUGE[1]}")
            + '"></span>'
            for investigation, notee in ordre
        )
        lignes.append(
            f'<div style="margin-bottom:0.6rem"><div style="font-size:0.9rem">{escape(nom)} · '
            f'<span style="color:{GRIS[1]}">recorded for {notees} of {len(fiches_notees)} investigations</span>'
            f"</div><div>{carres}</div></div>"
        )
    legende = (
        f'<div style="font-size:0.75rem;color:{GRIS[1]}">One square per investigation (hover for its name): '
        f'<span style="color:{BLEU_NOTE}">■</span> recorded · <span style="color:{ROUGE[1]}">□</span> not recorded'
        "</div>"
    )
    return "".join(lignes) + legende


def afficher_ce_quon_ne_sait_pas(fiches: pd.DataFrame, tests: pd.DataFrame, scenario: dict | None, cle: str) -> None:
    """Dessine les trois visuels de « What we don't know », avec les phrases qui ne rentrent pas dans une case.

    `cle` : le début des clés Streamlit de la page qui l'affiche (« recherche », « ui »).
    """
    scenario = scenario or {}
    st.markdown("**Tests in your conditions, by fuel**")
    grille = couverture(fiches, tests, scenario)
    st.html(grille_html(grille))
    if grille["atmosphere"] is None:
        st.caption("Your environment gives no oxygen or pressure, so no test can be placed in it.")

    st.markdown("**Oxygen: where each fuel was tested**")
    regle = regle_de_l_oxygene(fiches, tests, scenario)
    st.plotly_chart(
        regle_figure(regle, scenario.get("habitat")), config={"staticPlot": True}, key=f"{cle}_regle_oxygene"
    )
    if regle["emule"] is not None:
        st.caption(
            f"Not counted in solids: {regle['emulateurs']}, a gas burner that emulates a burning solid, "
            f"goes up to {regle['emule']:g} % oxygen."
        )

    st.markdown("**What NASA did not record**")
    st.html(mesures_html(mesures_notees(fiches)))
