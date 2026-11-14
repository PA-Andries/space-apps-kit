"""Page Comparateur. Propriétaire : rôle D (Comparateur). Les textes affichés sont en anglais.

La page part d'une investigation, propose celles qui lui sont comparables, puis résume
ce qui ressort de la comparaison. Une autre page peut y envoyer l'utilisateur avec
l'adresse `comparateur?id=<identifiant>`.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from flame.commun import INCONNU, charger_fiches, charger_tests, get_scenario
from flame.comparateur import (
    EXPLICATIONS,
    NIVEAUX,
    carte,
    comparables,
    comparer,
    instruments_communs,
    plages,
    resume,
    separer,
)
from flame.ui import label, place_conditions

LIBELLES = {
    "pilier": "Pillar",
    "type_combustible": "Fuel type",
    "materiel": "Hardware",
    "nb_tests": "Rows in NASA's test tables",
    "oxygene_pct": "Oxygen (%)",
    "pression_kpa": "Pressure (kPa)",
    "debit_air_cm_s": "Air flow (cm/s)",
}
# Les valeurs du contrat que `label()` ne traduit pas encore.
AUTRES_LIBELLES = {"fumée": "smoke", "poussière": "dust"}
COULEURS = ["#e0662a", "#2563eb", "#15803d"]  # une couleur par investigation, lisibles sur le thème clair

fiches = charger_fiches()
tests = charger_tests()
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
    for critere in ("pilier", "type_combustible"):
        if critere in lisible.index:
            lisible.loc[critere] = lisible.loc[critere].map(en_anglais)
    return lisible.rename(index=LIBELLES, columns=nom_affiche).rename_axis("Criterion")


st.title("Compare")
st.write("Start from one investigation and see how another relates to it: what they share and where they differ.")

# Une autre page peut choisir l'investigation de départ avec `?id=...` dans l'adresse.
demande = st.query_params.get("id")
if demande in noms and st.session_state.get("comparateur_id_adresse") != demande:
    st.session_state["comparateur_id_adresse"] = demande
    st.session_state["comparateur_depart"] = demande

colonne_depart, colonne_avec, colonne_troisieme = st.columns(3)
depart = colonne_depart.selectbox("Start from", list(noms), format_func=nom_affiche, key="comparateur_depart")
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

# L'atmosphère de l'habitat n'est utilisée que si l'énoncé la donne (le corps céleste ne sert qu'à la gravité).
habitat = get_scenario()["habitat"]
conditions = place_conditions(habitat, "Terre")
oxygene_habitat, pression_habitat = conditions["oxygen_pct"], conditions["pressure_kpa"]

with st.container(border=True):
    st.markdown("**What stands out**")
    for phrase in resume(fiches, tests, ids, oxygene_habitat, label(habitat)):
        st.markdown(f"- {phrase}")

# Le graphique n'apparaît que s'il apprend quelque chose : deux conditions chiffrées pour toutes, assez de points.
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
    if oxygene_habitat is not None:
        figure.add_vline(x=oxygene_habitat, line_dash="dash", annotation_text=f"{label(habitat)} oxygen")
        if axe_y == "pression_kpa":
            figure.add_hline(y=pression_habitat, line_dash="dash", annotation_text=f"{label(habitat)} pressure")
        legende += f" Dashed lines: the {label(habitat)} atmosphere given by the challenge statement."
    st.plotly_chart(figure, key="comparateur_carte")
    st.caption(legende)

communs, differences, _ = separer(pd.concat([comparer(fiches, ids), plages(tests, ids)]))
if not differences.empty:
    st.markdown("**Where they differ**")
    st.table(tableau_lisible(differences.replace(INCONNU, "not recorded")))
if not communs.empty:
    lisibles = tableau_lisible(communs)
    st.markdown(
        "**In common** · " + " · ".join(f"{critere}: {ligne.iloc[0]}" for critere, ligne in lisibles.iterrows())
    )

instruments = instruments_communs(fiches, ids)
if instruments:
    with st.expander(f"Measuring instruments they share ({len(instruments)})"):
        st.write(" · ".join(instruments))

st.caption("Pillar and fuel type are the team's classification, not NASA's. Test conditions come from NASA PSI.")
