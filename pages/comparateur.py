"""Page Comparateur. Propriétaire : rôle D (Comparateur). Les textes affichés sont en anglais.

La page part d'une investigation, propose celles qui lui sont comparables, puis détaille
la comparaison : portrait de chaque expérience, résumé par thèmes, tableau côte à côte.
Une autre page peut y envoyer l'utilisateur avec l'adresse `comparateur?id=<identifiant>`.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from flame.commun import charger_fiches, charger_table_psi, charger_tests, get_scenario
from flame.comparateur import (
    ABSENT,
    EXPLICATIONS,
    NIVEAUX,
    carte,
    comparables,
    cote_a_cote,
    decrire_environnement,
    explication_carte,
    frequents,
    ligne_psi,
    mesures,
    plages,
    plages_du_scenario,
    portrait,
    resume,
)
from flame.ui import label

LIBELLES = {
    "same": "Same?",
    "type_combustible": "Fuel type",
    "oxygene_pct": "Oxygen (%)",
    "pression_kpa": "Pressure (kPa)",
    "debit_air_cm_s": "Air flow (cm/s)",
}
# Les valeurs du contrat que `label()` ne traduit pas encore.
AUTRES_LIBELLES = {"fumée": "smoke", "poussière": "dust"}
COULEURS = ["#e0662a", "#2563eb", "#15803d"]  # une couleur par investigation, lisibles sur le thème clair

fiches = charger_fiches()
tests = charger_tests()
investigations_psi = charger_table_psi("investigations")
relations = charger_table_psi("relations")
noms = dict(zip(fiches["id"], fiches["nom"], strict=True))


def nom_affiche(identifiant: str) -> str:
    return f"{identifiant} · {noms[identifiant]}"


def en_anglais(valeur: object) -> str:
    """Une valeur du contrat en anglais : « gaz (modèle) » devient « gas (model) »."""
    base, _, precision = str(valeur).partition(" (")
    texte = AUTRES_LIBELLES.get(base, label(base))
    return f"{texte} (model)" if precision.startswith("modèle") else texte


def tableau_lisible(tableau: pd.DataFrame) -> pd.DataFrame:
    lisible = tableau.copy()
    if "type_combustible" in lisible.index:
        valeurs = lisible.columns != "same"
        lisible.loc["type_combustible", valeurs] = lisible.loc["type_combustible", valeurs].map(en_anglais)
    colonnes = {identifiant: nom_affiche(identifiant) for identifiant in noms}
    return lisible.rename(index=LIBELLES, columns={**colonnes, **LIBELLES}).rename_axis("Criterion")


def liste(lignes: list[str], sinon: str) -> None:
    st.markdown("\n".join(f"- {ligne}" for ligne in lignes) if lignes else sinon)


st.title("Compare")
st.write("Start from one investigation and see how another relates to it: what they share and where they differ.")

# Une autre page peut choisir l'investigation de départ avec `?id=...` dans l'adresse. `comparateur_id_adresse`
# retient la dernière valeur vue dans l'adresse : une valeur différente vient d'un lien, la même vient de cette page.
demande = st.query_params.get("id")
if demande in noms and st.session_state.get("comparateur_id_adresse") != demande:
    st.session_state["comparateur_depart"] = demande

colonne_depart, colonne_avec, colonne_troisieme = st.columns(3)
depart = colonne_depart.selectbox("Start from", list(noms), format_func=nom_affiche, key="comparateur_depart")
st.query_params["id"] = depart
st.session_state["comparateur_id_adresse"] = depart
candidats = comparables(fiches, tests, depart)
niveaux = dict(zip(candidats["id"], candidats["niveau"], strict=True))


def candidat_affiche(identifiant: str | None) -> str:
    if identifiant is None:
        return "No third investigation"
    return f"{nom_affiche(identifiant)} — {NIVEAUX[niveaux[identifiant]].lower()}"


avec = colonne_avec.selectbox(
    "Compare with",
    list(candidats["id"]),
    format_func=candidat_affiche,
    key=f"comparateur_avec_{depart}",
    help="The most comparable investigations come first.",
)
troisieme = colonne_troisieme.selectbox(
    "Add a third (optional)",
    [None, *(identifiant for identifiant in candidats["id"] if identifiant != avec)],
    format_func=candidat_affiche,
    key=f"comparateur_troisieme_{depart}_{avec}",
)
ids = [depart, avec] + ([troisieme] if troisieme else [])

with st.expander(f"Why these suggestions: all {len(candidats)} investigations, from most to least comparable"):
    for niveau, titre in NIVEAUX.items():
        st.markdown(f"**{titre}** ({(candidats['niveau'] == niveau).sum()}) · {EXPLICATIONS[niveau]}")
    apercu = pd.DataFrame(
        {
            "Investigation": candidats["id"].map(nom_affiche),
            "Level": candidats["niveau"].map(NIVEAUX),
            "Why": candidats["raison"],
            "Shared test conditions": candidats["variables_communes"].map(
                lambda variables: ", ".join(LIBELLES[variable] for variable in variables) or "none"
            ),
        }
    )
    st.dataframe(apercu, hide_index=True, key="comparateur_candidats")

st.subheader(" vs ".join(noms[identifiant] for identifiant in ids))

# Le portrait de chaque expérience, côte à côte.
for colonne, identifiant in zip(st.columns(len(ids)), ids, strict=True):
    fiche = fiches[fiches["id"] == identifiant].iloc[0]
    psi = ligne_psi(investigations_psi, identifiant)
    with colonne.container(border=True):
        st.markdown(f"**{noms[identifiant]}** · {identifiant}")
        if psi is not None and pd.notna(psi.get("title")):
            st.caption(str(psi["title"]))
        st.write(fiche["resume"])
        st.caption(f"Fuel type: {en_anglais(fiche['type_combustible'])}")
        for libelle, valeur in portrait(fiche, tests, psi).items():
            st.markdown(f"**{libelle}:** {valeur}")
        if pd.notna(fiche["objectif"]):
            with st.expander("Goal of the experiment"):
                st.write(fiche["objectif"])
        st.link_button("View on PSI", fiche["source_psi"], key=f"comparateur_psi_{identifiant}")

# Les conditions sont situées par rapport aux plages de l'environnement choisi (le scénario), et plus par
# rapport à une atmosphère unique par habitat. Un environnement sans plage connue (Mars) ne donne aucun chiffre.
scenario = get_scenario()
environnement = plages_du_scenario(scenario)

with st.container(border=True):
    st.markdown("#### What stands out")
    themes = resume(fiches, tests, ids, relations=relations, investigations_psi=investigations_psi, scenario=scenario)
    for theme, phrases in themes.items():
        st.markdown(f"**{theme}**")
        liste(phrases, "")

onglet_tableau, onglet_conditions, onglet_combustibles, onglet_mesures = st.tabs(
    ["Side by side", "Test conditions", "Fuels and results", "Measurements"]
)

with onglet_tableau:
    st.table(tableau_lisible(cote_a_cote(fiches, tests, ids, investigations_psi)))
    st.caption(f"“{ABSENT}” means the value is not in NASA's tables. Nothing is filled in by guessing.")

with onglet_conditions:
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
            opacity=0.7,
            labels=LIBELLES,
            hover_data=["test_id", "combustible"],
        )
        legende = f"Each point is one row of NASA's test tables ({len(lignes)} rows)."
        # Les pointillés marquent les bornes de l'environnement, quand il en donne.
        for borne in environnement["oxygene_pct"]:
            if borne is not None:
                figure.add_vline(x=borne, line_dash="dash", annotation_text=f"oxygen {borne:g} %")
        if axe_y == "pression_kpa":
            for borne in environnement["pression_kpa"]:
                if borne is not None:
                    figure.add_hline(y=borne, line_dash="dash", annotation_text=f"pressure {borne:g} kPa")
        if decrire_environnement(scenario):
            legende += f" Dashed lines: the limits of your environment ({decrire_environnement(scenario)})."
        st.plotly_chart(figure, key="comparateur_carte")
        st.caption(legende)
    st.markdown("**Range tested for each condition**")
    st.table(tableau_lisible(plages(tests, ids).replace("inconnu", ABSENT)))

with onglet_combustibles:
    for colonne, identifiant in zip(st.columns(len(ids)), ids, strict=True):
        with colonne:
            st.markdown(f"**{noms[identifiant]}**")
            st.caption("Most tested fuels")
            combustibles = frequents(tests, identifiant, "combustible", 5)
            liste([f"{nom} ({nombre} rows)" for nom, nombre in combustibles], f"Fuels: {ABSENT}.")
            st.caption("How the tests ended")
            fins = frequents(tests, identifiant, "resultat", 5)
            liste([f"{valeur} ({nombre} rows)" for valeur, nombre in fins], f"Outcomes: {ABSENT}.")

with onglet_mesures:
    communs, propres = mesures(fiches, ids)
    st.markdown(f"**Instruments listed for all of them** ({len(communs)})")
    liste(communs, "None.")
    for colonne, identifiant in zip(st.columns(len(ids)), ids, strict=True):
        with colonne:
            st.markdown(f"**Only listed for {noms[identifiant]}** ({len(propres[identifiant])})")
            liste(propres[identifiant], "None.")

st.caption("Fuel type is the team's classification, not NASA's. Everything else comes from NASA PSI.")
