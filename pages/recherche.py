"""Page Investigations. Propriétaire : rôle C (Recherche). Les textes affichés sont en anglais.

Recadrage du 14 novembre et REPRISE (issue n°2) : trois onglets, Classement · Fiche · Ce qu'on ne sait pas.
Le classement repose sur les preuves pour l'environnement choisi en page 1 ; il n'y a plus de pilier.
Le score sert à trier mais n'est pas affiché : la page dit seulement « les plus en lien avec votre environnement ».
Chaque fiche montre les rubriques du tableau blanc (comportement, dangers, prévention, trace des données,
comparer), tirées des fiches et des tests sans rien inventer.
"""

import pandas as pd
import streamlit as st

from flame.commun import charger_fiches, charger_tests, get_scenario
from flame.recherche import (
    ce_quon_ne_sait_pas,
    champs_inconnus,
    detail_du_score,
    les_plus_pertinentes,
    tests_dans_les_plages,
)
from flame.ui import carte_fiche, label

TITRES_TESTS = {
    "investigation_id": "Investigation",
    "test_id": "Test",
    "combustible": "Fuel",
    "oxygene_pct": "Oxygen (%)",
    "pression_kpa": "Pressure (kPa)",
    "debit_air_cm_s": "Air flow (cm/s)",
    "resultat": "Result",
    "source": "Source",
}
NON_NOTE = "Not recorded in the fiche."


def _texte(valeur: object) -> str:
    """Le texte d'une case de la fiche, ou « Not recorded » si elle est vide."""
    return NON_NOTE if pd.isna(valeur) or not str(valeur).strip() else str(valeur)


def _plage_testee(fiche: pd.Series) -> str:
    oxygene_min, oxygene_max, pression = (
        pd.to_numeric(fiche.get(colonne), errors="coerce") for colonne in ("oxygene_min", "oxygene_max", "pression_kpa")
    )
    morceaux = []
    if pd.notna(oxygene_min) and pd.notna(oxygene_max):
        morceaux.append(f"{oxygene_min:g} to {oxygene_max:g} % oxygen")
    if pd.notna(pression):
        morceaux.append(f"{pression:g} kPa")
    return ", ".join(morceaux) or "oxygen and pressure not recorded"


st.title("Investigations")

fiches = charger_fiches()
tests = charger_tests()
scenario = get_scenario()
habitat = scenario.get("habitat")
st.caption(f"Ranked for your environment: {label(habitat)}. Change it on the first page.")

classement = les_plus_pertinentes(fiches, scenario)

onglet_classement, onglet_fiche, onglet_inconnu = st.tabs(["Ranking", "Investigation", "What we don't know"])

with onglet_classement:
    # Le classement suit toujours le score sur les preuves, mais le score n'est pas affiché (demande du rôle C).
    st.caption(
        f"The {len(classement)} investigations most related to your environment, the closest first: "
        "the tests nearest your oxygen and pressure, your fuels and your gravity."
    )
    for _, fiche in classement.iterrows():
        carte_fiche(fiche)
        # Les raisons du classement, critère par critère, sans les points.
        with st.expander("Why this investigation is relevant"):
            for _, raison in detail_du_score(fiche, scenario, tests=tests).iterrows():
                st.markdown(f"- **{raison['critere']}:** {raison['explication']}")
        st.page_link("pages/comparateur.py", label="Compare", query_params={"id": fiche["id"]})

with onglet_fiche:
    noms = dict(zip(classement["id"], classement["nom"], strict=True))
    choix = st.selectbox(
        "Investigation",
        list(noms),
        format_func=lambda id_fiche: f"{id_fiche} · {noms[id_fiche]}",
        key="recherche_fiche",
    )
    fiche = classement[classement["id"] == choix].iloc[0]
    siens = tests[tests["investigation_id"] == fiche["id"]]
    resultats = siens["resultat"].dropna().value_counts()
    carte_fiche(fiche)

    st.subheader("Behaviour")
    st.markdown(_texte(fiche.get("resume")))
    if not resultats.empty:
        st.markdown(
            "Recorded test outcomes: " + ", ".join(f"{issue} ({nombre})" for issue, nombre in resultats.head(5).items())
        )

    st.subheader("Hazards")
    st.markdown(f"**Fuel:** {_texte(fiche.get('combustible'))} ({label(fiche.get('type_combustible', ''))})")
    st.markdown(f"**Conditions tested:** {_plage_testee(fiche)} · **What varies:** {_texte(fiche.get('ce_qui_varie'))}")

    st.subheader("Prevention")
    st.markdown(f"**What the investigation set out to learn:** {_texte(fiche.get('objectif'))}")

    st.subheader("Data trace")
    dedans = tests_dans_les_plages(siens, scenario)
    st.markdown(
        f"**Measurements:** {_texte(fiche.get('capteurs'))} · **Tests:** {len(siens)}, "
        f"of which {len(dedans)} in your environment."
    )
    inconnus = champs_inconnus(fiche)
    if inconnus:
        st.caption(f"Not recorded by NASA for this investigation: {', '.join(inconnus)}.")
    st.dataframe(siens, hide_index=True, column_config=TITRES_TESTS, key="recherche_tests_fiche")
    if pd.notna(fiche.get("source_psi")):
        st.markdown(f"Source: [PSI]({fiche['source_psi']})")

    st.subheader("Compare")
    st.page_link("pages/comparateur.py", label="Compare with similar investigations", query_params={"id": fiche["id"]})

with onglet_inconnu:
    st.caption("Gaps in NASA's data for your environment. Counted on PSI's test tables: nothing is guessed.")
    for constat in ce_quon_ne_sait_pas(fiches, tests, scenario):
        st.markdown(f"- {constat}")
