"""Page Recherche. Propriétaire : rôle C (Recherche). Les textes affichés sont en anglais."""

import streamlit as st

from flame.commun import ATMOSPHERES, HABITATS, charger_fiches, charger_publications, charger_tests, get_scenario
from flame.recherche import detail_du_score, filtrer, rechercher, valeurs_possibles
from flame.ui import carte_fiche

TITRES_SCORE = {"critere": "Criterion", "points": "Points", "maximum": "Out of", "explication": "Why"}
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
TITRES_PUBLICATIONS = {"titre": "Title", "annee": "Year", "auteurs": "Authors", "url": "Link"}

st.title("Search")

fiches = charger_fiches()
scenario = get_scenario()
oxygene_pct, pression_kpa = ATMOSPHERES[scenario["habitat"]]
st.caption(
    f"Ranked for: {scenario['habitat']} ({oxygene_pct} % oxygen, {pression_kpa} kPa) · "
    f"pillar: {scenario['pilier']}. Change the scenario in the sidebar."
)

question = st.text_input(
    "What are you looking for?", placeholder="fabric, extinction, smoke…", key="recherche_question"
)
with st.expander("Filters"):
    piliers = st.multiselect("Pillar", valeurs_possibles(fiches, "pilier"), key="recherche_filtre_piliers")
    types_combustible = st.multiselect(
        "Fuel type", valeurs_possibles(fiches, "type_combustible"), key="recherche_filtre_combustibles"
    )
    habitats = st.multiselect("Relevant habitat", HABITATS, key="recherche_filtre_habitats")

resultats = rechercher(question, filtrer(fiches, piliers, types_combustible, habitats), scenario)

st.caption(f"{len(resultats)} investigation(s) out of {len(fiches)}")
if resultats.empty:
    st.info("No investigation matches. Try another word or remove a filter.")

tests = charger_tests()
try:
    publications = charger_publications()
except FileNotFoundError:  # le tableau des rapports n'est pas encore livré
    publications = None

for _, fiche in resultats.iterrows():
    carte_fiche(fiche)
    st.progress(int(fiche["score"]) / 100, text=f"Score for this scenario: {int(fiche['score'])} / 100")
    st.page_link("pages/comparateur.py", label="Compare", query_params={"id": fiche["id"]})
    with st.expander(f"Why this score, and the details of {fiche['id']}"):
        st.dataframe(
            detail_du_score(fiche, scenario),
            hide_index=True,
            column_config=TITRES_SCORE,
            key=f"recherche_score_{fiche['id']}",
        )
        st.markdown(f"**Goal:** {fiche['objectif']}")
        st.markdown(f"**Fuel:** {fiche['combustible']} · **What varies:** {fiche['ce_qui_varie']}")
        st.markdown(f"**Measurements:** {fiche['capteurs']}")
        st.markdown("**Tests**")
        st.dataframe(
            tests[tests["investigation_id"] == fiche["id"]],
            hide_index=True,
            column_config=TITRES_TESTS,
            key=f"recherche_tests_{fiche['id']}",
        )
        if publications is not None:
            st.markdown("**NTRS reports**")
            st.dataframe(
                publications[publications["investigation_id"] == fiche["id"]][list(TITRES_PUBLICATIONS)],
                hide_index=True,
                column_config=TITRES_PUBLICATIONS,
                key=f"recherche_publications_{fiche['id']}",
            )
