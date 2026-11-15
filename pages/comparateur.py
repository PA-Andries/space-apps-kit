"""Page Compare. Propriétaire : rôle D (Comparateur). Les textes affichés sont en anglais.

La page part d'une investigation et propose celles qui lui sont comparables, d'après NASA et l'énoncé du défi
seulement : même matériel (directement comparables), ou un lien donné par NASA (comparables en principe).
Le type de combustible rangé par l'équipe (solide, liquide, gaz) n'est ni utilisé ni affiché ici.
Elle montre ensuite la comparaison de haut en bas, du plus visuel au plus détaillé :
 1. le lien entre les deux, en une ligne ;
 2. le portrait de chacune, avec les textes de NASA (objectifs, approche, hypothèse) ;
 3. les chiffres côte à côte, puis les plages testées en barres (oxygène, pression, débit d'air) ;
 4. les fins de test en barres, quand NASA les note ;
 5. ce qui ressort, en phrases rangées par thème ;
 6. les tableaux complets, repliés dans des onglets.
Une autre page peut y envoyer l'utilisateur avec l'adresse `comparateur?id=<identifiant>`.
"""

from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

from flame.commun import charger_fiches, charger_table_psi, charger_tests, get_scenario
from flame.comparateur import (
    ABSENT,
    EXPLICATIONS,
    ISSUES,
    NIVEAUX,
    NIVEAUX_PROPOSES,
    barres_des_plages,
    carte,
    chiffres_cles,
    comparables,
    cote_a_cote,
    decrire_environnement,
    explication_carte,
    frequents,
    issues,
    ligne_psi,
    mesures,
    plages_du_scenario,
    portrait,
    resume,
    texte_de_plage,
)
from flame.recherche import descriptif

LIBELLES = {
    "same": "Same?",
    "oxygene_pct": "Oxygen (%)",
    "pression_kpa": "Pressure (kPa)",
    "debit_air_cm_s": "Air flow (cm/s)",
}
# Une couleur par investigation, lisibles sur le thème sombre : l'orange du site pour celle de départ.
COULEURS = ["#ff7a3d", "#6fb1ff"]
LETTRES = ["a", "b"]
# Les couleurs des fins de test, les mêmes que sur la page 1 (rôle F).
COULEURS_ISSUES = {
    "burned": "#ff7a3d",
    "went_out": "#8fa3d9",
    "no_ignition": "#c9ccd8",
    "unknown": "rgba(160, 175, 255, 0.18)",
}

STYLE = f"""<style>
.cmp-a, .stApp h3.cmp-a {{ color: {COULEURS[0]}; }} .cmp-b, .stApp h3.cmp-b {{ color: {COULEURS[1]}; }}
.cmp-levels {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.7rem; margin: 0.2rem 0 0.6rem; }}
.cmp-level {{ background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(160, 175, 255, 0.12);
  border-radius: 16px; padding: 0.7rem 0.9rem; }}
.cmp-level p {{ color: #a3abc9; font-size: 0.86rem; margin: 0.35rem 0 0; line-height: 1.4; }}
.cmp-badge {{ display: inline-block; border-radius: 980px; padding: 0.2rem 0.7rem; font-size: 0.78rem;
  font-weight: 700; letter-spacing: 0.02em; }}
.cmp-badge.l1 {{ background: {COULEURS[0]}; color: #fff; }}
.cmp-badge.l2 {{ background: rgba(255, 122, 61, 0.16); color: #ffb08a; border: 1px solid rgba(255, 122, 61, 0.5); }}
.cmp-band, .st-key-cmp_card_a, .st-key-cmp_card_b, .st-key-cmp_details, .cmp-panel {{
  background: rgba(26, 33, 80, 0.6); border: 1px solid rgba(160, 175, 255, 0.14) !important; border-radius: 24px;
  backdrop-filter: blur(16px) saturate(140%); -webkit-backdrop-filter: blur(16px) saturate(140%);
  box-shadow: 0 18px 50px -20px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}}
.cmp-band {{ padding: 1.1rem 1.3rem; margin: 0.4rem 0 0.2rem; }}
.cmp-band h2 {{ font-size: 1.7rem; font-weight: 800; letter-spacing: -0.03em; margin: 0.5rem 0 0.3rem; padding: 0; }}
.cmp-band h2 i {{ color: #a3abc9; font-style: normal; font-weight: 500; font-size: 1.1rem; margin: 0 0.4rem; }}
.cmp-band p {{ margin: 0.15rem 0 0; font-size: 0.95rem; line-height: 1.5; }}
.cmp-band p.cmp-quiet {{ color: #a3abc9; font-size: 0.86rem; }}
.st-key-cmp_card_a, .st-key-cmp_card_b, .st-key-cmp_details {{ padding: 1rem 1.1rem 1.1rem; }}
.st-key-cmp_card_a {{ border-top: 3px solid {COULEURS[0]} !important; }}
.st-key-cmp_card_b {{ border-top: 3px solid {COULEURS[1]} !important; }}
.cmp-card h3 {{ font-size: 1.2rem; font-weight: 700; letter-spacing: -0.02em; margin: 0; padding: 0; }}
.cmp-card h3 small {{ color: #a3abc9; font-size: 0.82rem; font-weight: 500; margin-left: 0.4rem; }}
.cmp-card .cmp-title {{ color: #a3abc9; font-size: 0.88rem; margin: 0.15rem 0 0.5rem; }}
.cmp-card .cmp-lead {{ font-weight: 700; font-size: 0.95rem; line-height: 1.45; margin: 0; }}
.cmp-label {{ display: block; color: #ff7a3d; font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; margin: 0.7rem 0 0.2rem; }}
.cmp-card .cmp-text {{ font-size: 0.9rem; line-height: 1.5; margin: 0; color: #dfe3f5; }}
.cmp-chips {{ display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.7rem; }}
.cmp-chip {{ background: rgba(255, 255, 255, 0.07); border: 1px solid rgba(160, 175, 255, 0.16);
  border-radius: 980px; padding: 0.25rem 0.7rem; font-size: 0.8rem; }}
.cmp-chip b {{ color: #a3abc9; font-weight: 500; margin-right: 0.3rem; }}
.cmp-panel {{ padding: 1.1rem 1.3rem 1.2rem; margin: 0.2rem 0; }}
.cmp-panel h3 {{ font-size: 1.15rem; font-weight: 700; letter-spacing: -0.02em; margin: 0; padding: 0; }}
.cmp-panel > p {{ color: #a3abc9; font-size: 0.88rem; margin: 0.15rem 0 0.7rem; }}
.cmp-figures {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 0.7rem; }}
.cmp-figure {{ background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(160, 175, 255, 0.10);
  border-radius: 18px; padding: 0.8rem 0.9rem; text-align: center; }}
.cmp-figure span {{ display: block; color: #a3abc9; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.3rem; }}
.cmp-figure div {{ display: flex; justify-content: center; align-items: baseline; gap: 1.1rem; }}
.cmp-figure b {{ font-size: 1.7rem; font-weight: 800; letter-spacing: -0.03em; }}
.cmp-figure b.cmp-small {{ font-size: 0.95rem; font-weight: 600; }}
.cmp-range {{ margin: 0.9rem 0 1.1rem; }}
.cmp-range-head {{ display: flex; justify-content: space-between; align-items: baseline; gap: 1rem; flex-wrap: wrap; }}
.cmp-range-head b {{ font-size: 0.98rem; }} .cmp-range-head b small {{ color: #a3abc9; font-weight: 500; }}
.cmp-range-head em {{ color: #a3abc9; font-style: normal; font-size: 0.85rem; }}
.cmp-track {{ position: relative; height: 34px; margin-top: 0.4rem; border-radius: 10px;
  background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(160, 175, 255, 0.10); overflow: hidden; }}
.cmp-zone {{ position: absolute; top: 0; bottom: 0; background: rgba(255, 255, 255, 0.10);
  border-left: 1px dashed rgba(255, 255, 255, 0.45); border-right: 1px dashed rgba(255, 255, 255, 0.45); }}
.cmp-bar {{ position: absolute; height: 11px; border-radius: 6px; min-width: 6px; }}
.cmp-bar.a {{ top: 5px; background: {COULEURS[0]}; }} .cmp-bar.b {{ top: 18px; background: {COULEURS[1]}; }}
.cmp-scale {{ display: flex; justify-content: space-between; color: #8790b3; font-size: 0.72rem; margin-top: 0.15rem; }}
.cmp-values {{ display: flex; gap: 1.4rem; flex-wrap: wrap; font-size: 0.85rem; margin-top: 0.15rem; }}
.cmp-key {{ display: flex; gap: 1.2rem; flex-wrap: wrap; color: #a3abc9; font-size: 0.82rem; margin-top: 0.2rem; }}
.cmp-key i {{ display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 0.35rem; }}
.cmp-outcome {{ margin: 0.7rem 0 0.9rem; }}
.cmp-outcome > b {{ font-size: 0.95rem; }} .cmp-outcome > small {{ color: #a3abc9; margin-left: 0.4rem; }}
.cmp-stack {{ display: flex; height: 16px; border-radius: 8px; overflow: hidden; margin-top: 0.35rem;
  background: rgba(160, 175, 255, 0.10); }}
.cmp-stack i {{ display: block; height: 100%; }}
.cmp-themes {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.7rem; }}
.cmp-theme {{ background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(160, 175, 255, 0.10);
  border-radius: 18px; padding: 0.8rem 1rem 0.9rem; }}
.cmp-theme h4 {{ color: #ff7a3d; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; margin: 0 0 0.4rem; padding: 0; }}
.cmp-theme ul {{ margin: 0; padding-left: 1.1rem; font-size: 0.9rem; line-height: 1.5; }}
.cmp-theme li {{ margin: 0.15rem 0; }}
@media (max-width: 760px) {{ .cmp-levels, .cmp-themes {{ grid-template-columns: 1fr; }} }}
</style>"""

fiches = charger_fiches()
tests = charger_tests()
investigations_psi = charger_table_psi("investigations")
relations = charger_table_psi("relations")
noms = dict(zip(fiches["id"], fiches["nom"], strict=True))


def nom_affiche(identifiant: str) -> str:
    return f"{identifiant} · {noms[identifiant]}"


def tableau_lisible(tableau: pd.DataFrame) -> pd.DataFrame:
    colonnes = {identifiant: nom_affiche(identifiant) for identifiant in noms}
    return tableau.rename(index=LIBELLES, columns={**colonnes, **LIBELLES}).rename_axis("Criterion")


def liste(lignes: list[str], sinon: str) -> None:
    st.markdown("\n".join(f"- {ligne}" for ligne in lignes) if lignes else sinon)


def en_pourcent(valeur: float, echelle: tuple[float, float]) -> float:
    """La place d'une valeur sur la barre, de 0 à 100 % de sa largeur."""
    mini, maxi = echelle
    return min(max((valeur - mini) / (maxi - mini) * 100, 0.0), 100.0) if maxi > mini else 0.0


def carte_portrait(identifiant: str, lettre: str, scenario: dict) -> None:
    """La carte d'une investigation : ce qu'elle a cherché, où, quand, avec quoi, et les textes de NASA."""
    fiche = fiches[fiches["id"] == identifiant].iloc[0]
    faits = portrait(fiche, tests, ligne_psi(investigations_psi, identifiant))
    nasa = descriptif(fiche, scenario, tests, investigations_psi)
    with st.container(key=f"cmp_card_{lettre}"):
        titre = f'<p class="cmp-title">{escape(nasa["titre"])}</p>' if nasa["titre"] else ""
        # Les combustibles sont ceux que NASA écrit dans ses tables de tests, pas une catégorie de l'équipe.
        etiquettes = [("Fuels in NASA's tables", faits["Fuels tested"])] if faits["Fuels tested"] != ABSENT else []
        etiquettes += [(nom, faits[nom]) for nom in ("Where", "Project dates", "Hardware") if faits[nom] != ABSENT]
        puces = "".join(
            f'<span class="cmp-chip"><b>{escape(nom)}</b>{escape(valeur)}</span>' for nom, valeur in etiquettes
        )
        objectif = (
            '<span class="cmp-label">What it set out to learn</span>'
            f'<p class="cmp-text">{escape(nasa["objectif_court"])}</p>'
            if nasa["objectif_court"]
            else ""
        )
        st.html(
            f'<div class="cmp-card"><h3 class="cmp-{lettre}">{escape(noms[identifiant])}'
            f"<small>{escape(identifiant)}</small>"
            f'</h3>{titre}<p class="cmp-lead">{escape(str(fiche["resume"]))}</p>{objectif}'
            f'<div class="cmp-chips">{puces}</div></div>'
        )
        if nasa["textes"]:
            with st.expander("NASA's full description"):
                st.html(
                    "".join(
                        f'<span class="cmp-label">{escape(rubrique)}</span>'
                        f'<p class="cmp-text" style="font-size:0.9rem;line-height:1.5;margin:0">{escape(texte)}</p>'
                        for rubrique, texte in nasa["textes"].items()
                    )
                )
                st.caption("Text from NASA's PSI record, unchanged.")
        st.link_button("View on PSI", fiche["source_psi"], key=f"comparateur_psi_{identifiant}")


def panneau_chiffres(ids: list[str], scenario: dict) -> str:
    """Les chiffres à lire côte à côte, une tuile par chiffre."""
    tuiles = []
    for libelle, valeurs in chiffres_cles(fiches, tests, ids, scenario, investigations_psi):
        nombres = "".join(
            f'<b class="cmp-{lettre}{" cmp-small" if valeurs[identifiant] == ABSENT else ""}">'
            f"{escape(valeurs[identifiant])}</b>"
            for identifiant, lettre in zip(ids, LETTRES, strict=True)
        )
        tuiles.append(f'<div class="cmp-figure"><span>{escape(libelle)}</span><div>{nombres}</div></div>')
    return f'<div class="cmp-figures">{"".join(tuiles)}</div>'


def panneau_plages(ids: list[str], scenario: dict) -> str:
    """Une barre par condition et par investigation : où NASA a testé, où les plages se croisent."""
    blocs = []
    for barre in barres_des_plages(tests, ids, scenario):
        echelle, unite = barre["echelle"], barre["unite"]
        connues = [plage for plage in barre["plages"].values() if plage is not None]
        if not connues:
            constat = "not recorded for either"
        elif len(connues) < len(ids):
            constat = "recorded for one only"
        elif barre["recouvrement"]:
            bas, haut = barre["recouvrement"]
            constat = f"both tested {texte_de_plage((bas, haut), unite)}"
        else:
            constat = "their ranges do not overlap"
        zone = ""
        if barre["environnement"]:
            debut, fin = (en_pourcent(borne, echelle) for borne in barre["environnement"])
            zone = f'<div class="cmp-zone" style="left:{debut:.2f}%;width:{max(fin - debut, 0.5):.2f}%"></div>'
        traits, valeurs = "", ""
        for identifiant, lettre in zip(ids, LETTRES, strict=True):
            plage = barre["plages"][identifiant]
            if plage is not None:
                debut, fin = (en_pourcent(borne, echelle) for borne in plage)
                traits += (
                    f'<div class="cmp-bar {lettre}" style="left:{debut:.2f}%;width:{max(fin - debut, 0.8):.2f}%"></div>'
                )
            valeurs += (
                f'<span class="cmp-{lettre}">{escape(noms[identifiant])}: {escape(texte_de_plage(plage, unite))}</span>'
            )
        blocs.append(
            f'<div class="cmp-range"><div class="cmp-range-head"><b>{escape(barre["nom"].capitalize())} '
            f"<small>({escape(unite)})</small></b><em>{escape(constat)}</em></div>"
            f'<div class="cmp-track">{zone}{traits}</div>'
            f'<div class="cmp-scale"><span>{echelle[0]:g}</span><span>{echelle[1]:g}</span></div>'
            f'<div class="cmp-values">{valeurs}</div></div>'
        )
    return "".join(blocs)


def panneau_issues(ids: list[str]) -> str:
    """Les fins de test de chaque investigation en une barre, ou une phrase quand NASA n'en note aucune."""
    comptes = issues(tests, ids)
    notees = {
        identifiant: sum(nombre for fin, nombre in fins.items() if fin != "unknown")
        for identifiant, fins in comptes.items()
    }
    if not any(notees.values()):
        return "<p>NASA's tables record how the tests ended for neither of them.</p>"
    blocs = []
    for identifiant, lettre in zip(ids, LETTRES, strict=True):
        fins, total = comptes[identifiant], sum(comptes[identifiant].values())
        if not notees[identifiant]:
            blocs.append(
                f'<div class="cmp-outcome"><b class="cmp-{lettre}">{escape(noms[identifiant])}</b>'
                f"<small>no test outcome recorded in NASA's tables ({total} rows)</small></div>"
            )
            continue
        segments = "".join(
            f'<i style="width:{nombre / total * 100:.2f}%;background:{COULEURS_ISSUES[fin]}"></i>'
            for fin, nombre in fins.items()
            if nombre
        )
        detail = " · ".join(f"{ISSUES[fin].lower()} {nombre}" for fin, nombre in fins.items() if nombre)
        blocs.append(
            f'<div class="cmp-outcome"><b class="cmp-{lettre}">{escape(noms[identifiant])}</b>'
            f'<small>{escape(detail)}</small><div class="cmp-stack">{segments}</div></div>'
        )
    legende = "".join(
        f'<span><i style="background:{COULEURS_ISSUES[fin]}"></i>{escape(texte)}</span>'
        for fin, texte in ISSUES.items()
    )
    return "".join(blocs) + f'<div class="cmp-key">{legende}</div>'


def afficher_comparaison(ids: list[str], niveau: int) -> None:
    """Toute la comparaison de deux investigations, du lien entre elles aux tableaux complets."""
    scenario = get_scenario()
    themes = resume(fiches, tests, ids, relations=relations, investigations_psi=investigations_psi, scenario=scenario)

    # 1. Le lien entre les deux, en une ligne.
    liens = themes.pop("How they relate", [])
    phrases = "".join(
        f'<p class="{"cmp-quiet" if rang else ""}">{escape(phrase)}</p>' for rang, phrase in enumerate(liens)
    )
    st.html(
        f'<div class="cmp-band"><span class="cmp-badge l{niveau}">{escape(NIVEAUX[niveau])}</span>'
        f'<h2><span class="cmp-a">{escape(noms[ids[0]])}</span><i>vs</i>'
        f'<span class="cmp-b">{escape(noms[ids[1]])}</span></h2>{phrases}</div>'
    )

    # 2. Le portrait de chacune.
    for colonne, identifiant, lettre in zip(st.columns(2, gap="medium"), ids, LETTRES, strict=True):
        with colonne:
            carte_portrait(identifiant, lettre, scenario)

    # 3. Les chiffres côte à côte, puis les plages testées en barres.
    st.html(
        '<div class="cmp-panel"><h3>At a glance</h3>'
        f'<p><span class="cmp-a">{escape(noms[ids[0]])}</span> on the left, '
        f'<span class="cmp-b">{escape(noms[ids[1]])}</span> on the right.</p>{panneau_chiffres(ids, scenario)}</div>'
    )
    environnement = decrire_environnement(scenario)
    ombre = f" Shaded: your environment ({escape(environnement)})." if environnement else ""
    st.html(
        '<div class="cmp-panel"><h3>Where NASA tested each one</h3>'
        f"<p>One bar per investigation, from the lowest to the highest value in NASA's test tables.{ombre}</p>"
        f"{panneau_plages(ids, scenario)}</div>"
    )

    # 4. Les fins de test, quand NASA les note.
    st.html(
        '<div class="cmp-panel"><h3>How the tests ended</h3>'
        "<p>Share of each investigation's test rows. Sorting NASA's wording into these kinds is the team's reading.</p>"
        f"{panneau_issues(ids)}</div>"
    )

    # 5. Ce qui ressort, en phrases rangées par thème.
    st.markdown("#### What stands out")
    cartes = "".join(
        f'<div class="cmp-theme"><h4>{escape(theme)}</h4><ul>'
        + "".join(f"<li>{escape(phrase)}</li>" for phrase in phrases)
        + "</ul></div>"
        for theme, phrases in themes.items()
    )
    st.html(f'<div class="cmp-themes">{cartes}</div>')

    # 6. Les tableaux complets, dans une carte pour rester lisibles sur le fond étoilé.
    with st.container(key="cmp_details"):
        onglet_tableau, onglet_points, onglet_combustibles, onglet_mesures = st.tabs(
            ["Side by side", "Every test point", "Fuels and raw results", "Measurements"]
        )
        with onglet_tableau:
            st.table(tableau_lisible(cote_a_cote(fiches, tests, ids, investigations_psi)))
            st.caption(f"“{ABSENT}” means the value is not in NASA's tables.")
        with onglet_points:
            # Le graphique n'apparaît que s'il apprend quelque chose ; la phrase dit toujours pourquoi il est là ou non.
            st.info(explication_carte(tests, ids))
            a_tracer = carte(tests, ids)
            if a_tracer:
                (axe_x, axe_y), lignes = a_tracer
                lignes = lignes.assign(Investigation=lignes["investigation_id"].map(noms))
                figure = px.scatter(
                    lignes,
                    x=axe_x,
                    y=axe_y,
                    color="Investigation",
                    symbol="Investigation",
                    color_discrete_sequence=COULEURS,
                    category_orders={"Investigation": [noms[identifiant] for identifiant in ids]},
                    opacity=0.8,
                    labels=LIBELLES,
                    hover_data=["test_id", "combustible"],
                )
                figure.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.03)")
                legende = f"Each point is one row of NASA's test tables ({len(lignes)} rows)."
                # Les pointillés marquent les bornes de l'environnement, quand il en donne.
                bornes = plages_du_scenario(scenario)
                for borne in bornes["oxygene_pct"]:
                    if borne is not None:
                        figure.add_vline(x=borne, line_dash="dash", annotation_text=f"oxygen {borne:g} %")
                if axe_y == "pression_kpa":
                    for borne in bornes["pression_kpa"]:
                        if borne is not None:
                            figure.add_hline(y=borne, line_dash="dash", annotation_text=f"pressure {borne:g} kPa")
                if environnement:
                    legende += f" Dashed lines: the limits of your environment ({environnement})."
                st.plotly_chart(figure, key="comparateur_carte")
                st.caption(legende)
        with onglet_combustibles:
            for colonne, identifiant in zip(st.columns(2), ids, strict=True):
                with colonne:
                    st.markdown(f"**{noms[identifiant]}**")
                    st.caption("Most tested fuels")
                    combustibles = frequents(tests, identifiant, "combustible", 5)
                    liste([f"{nom} ({nombre} rows)" for nom, nombre in combustibles], f"Fuels: {ABSENT}.")
                    st.caption("How the tests ended, in NASA's words")
                    fins = frequents(tests, identifiant, "resultat", 5)
                    liste([f"{valeur} ({nombre} rows)" for valeur, nombre in fins], f"Outcomes: {ABSENT}.")
        with onglet_mesures:
            communs, propres = mesures(fiches, ids)
            st.markdown(f"**Instruments listed for both** ({len(communs)})")
            liste(communs, "None.")
            for colonne, identifiant in zip(st.columns(2), ids, strict=True):
                with colonne:
                    st.markdown(f"**Only listed for {noms[identifiant]}** ({len(propres[identifiant])})")
                    liste(propres[identifiant], "None.")


st.html(STYLE)
st.title("Compare")
st.write("Start from one investigation and see how a comparable one relates to it: what they share, where they differ.")

# Une autre page peut choisir l'investigation de départ avec `?id=...` dans l'adresse. `comparateur_id_adresse`
# retient la dernière valeur vue dans l'adresse : une valeur différente vient d'un lien, la même vient de cette page.
demande = st.query_params.get("id")
if demande in noms and st.session_state.get("comparateur_id_adresse") != demande:
    st.session_state["comparateur_depart"] = demande

colonne_depart, colonne_avec = st.columns(2, gap="medium")
depart = colonne_depart.selectbox("Start from", list(noms), format_func=nom_affiche, key="comparateur_depart")
st.query_params["id"] = depart
st.session_state["comparateur_id_adresse"] = depart
# Seules les investigations comparables sont proposées : même matériel, ou un lien donné par NASA.
candidats = comparables(fiches, tests, depart, investigations_psi, relations)
candidats = candidats[candidats["niveau"].isin(NIVEAUX_PROPOSES)].reset_index(drop=True)
niveaux = dict(zip(candidats["id"], candidats["niveau"], strict=True))

if candidats.empty:
    colonne_avec.selectbox(
        "Compare with", ["No comparable investigation"], disabled=True, key=f"comparateur_aucune_{depart}"
    )
else:
    avec = colonne_avec.selectbox(
        "Compare with",
        list(candidats["id"]),
        format_func=lambda identifiant: f"{nom_affiche(identifiant)} — {NIVEAUX[niveaux[identifiant]].lower()}",
        key=f"comparateur_avec_{depart}",
        help="The most comparable investigations come first.",
    )

# Ce que veulent dire les deux niveaux, toujours visible.
st.html(
    '<div class="cmp-levels">'
    + "".join(
        f'<div class="cmp-level"><span class="cmp-badge l{niveau}">{escape(NIVEAUX[niveau])}</span>'
        f"<p>{escape(EXPLICATIONS[niveau])}</p></div>"
        for niveau in NIVEAUX_PROPOSES
    )
    + "</div>"
)

if candidats.empty:
    st.info(
        f"No other investigation shares the hardware of {noms[depart]} or is linked to it by NASA, "
        "so there is nothing to compare it with. Here is what it studied."
    )
    carte_portrait(depart, "a", get_scenario())
else:
    afficher_comparaison([depart, avec], int(niveaux[avec]))

st.caption(
    "Every value on this page comes from NASA's PSI database; the hardware groups and some links between "
    "investigations come from the challenge statement. The one-line summary in bold on each card is written "
    "by the team from NASA's record."
)
