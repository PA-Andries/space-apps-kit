"""Page Recherche. Propriétaire : rôle C (Recherche). Les textes affichés sont en anglais."""

import streamlit as st

from flame.commun import ATMOSPHERES, charger_fiches, charger_publications, charger_tests, get_scenario
from flame.recherche import les_plus_pertinentes
from flame.ui import carte_fiche

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

# Pas de barre de recherche : la page montre directement les fiches les plus utiles au scénario.
# Le score sert au tri et au seuil, mais il n'est pas affiché.
resultats = les_plus_pertinentes(fiches, scenario)

st.caption(f"{len(resultats)} most relevant investigation(s) out of {len(fiches)}")
if resultats.empty:
    st.info("No investigation is relevant enough for this scenario. Try another pillar or habitat in the sidebar.")

tests = charger_tests()
try:
    publications = charger_publications()
except FileNotFoundError:  # le tableau des rapports n'est pas encore livré
    publications = None

for _, fiche in resultats.iterrows():
    carte_fiche(fiche)
    st.page_link("pages/comparateur.py", label="Compare", query_params={"id": fiche["id"]})
    with st.expander(f"Details of {fiche['id']}"):
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
