"""Page Data. Propriétaire : rôle D (Comparateur). Les textes affichés sont en anglais.

Trois onglets : le graphique des conditions testées, les tests de l'environnement à télécharger,
et ce que chaque investigation fait varier et mesure.
"""

import streamlit as st

from flame.commun import charger_fiches, charger_table_psi, charger_tests, get_scenario
from flame.comparateur import (
    capteurs,
    ce_qui_varie,
    decrire_environnement,
    environnement_defini,
    graphique_conditions,
    tableau_des_tests,
    tests_correspondants,
)
from flame.ui import label

VUES = {"Oxygen × pressure": "pression", "Oxygen × air flow": "debit"}

fiches = charger_fiches()
tests = charger_tests()
scenario = get_scenario()
habitat = label(scenario["habitat"])
noms = dict(zip(fiches["id"], fiches["nom"], strict=True))

st.title("Data")
st.write("Every point and every row below is a test from NASA's PSI tables. Nothing is estimated.")

# Le compteur : les tests dans l'environnement, en séparant ceux dont la pression n'est pas notée.
if environnement_defini(scenario):
    correspondants = tests_correspondants(tests, fiches, scenario)
    surs = correspondants[correspondants["pression_notee"]]
    st.caption(f"Your environment ({habitat}): {decrire_environnement(scenario) or 'fuel type only'}.")
    gauche, milieu, droite = st.columns(3)
    gauche.metric("Tests inside your environment", len(surs))
    milieu.metric("Investigations", surs["investigation_id"].nunique())
    droite.metric("More tests, pressure not recorded", len(correspondants) - len(surs))
else:
    st.info(
        f"Your environment ({habitat}) gives no oxygen, pressure or air flow range, so no test can be matched "
        "to it. All tests are shown and none is highlighted."
    )

onglet_graphique, onglet_tableau, onglet_variables = st.tabs(["Chart", "Table + CSV", "Variables and sensors"])

with onglet_graphique:
    vue = st.radio("View", list(VUES), horizontal=True, key="comparateur_donnees_vue")
    st.plotly_chart(graphique_conditions(tests, fiches, scenario, vue=VUES[vue]), key="comparateur_donnees_graphique")
    st.caption(
        "No test records oxygen, pressure and air flow together, so there are two views sharing the oxygen axis: "
        "pressure for gas flames and droplets, air flow for solids. One colour per investigation; tests inside "
        "your environment are solid and outlined. Zones say where their figures come from; Mars has none because "
        "the challenge statement gives no atmosphere for it. PSI has no test in lunar or Martian gravity."
    )

with onglet_tableau:
    tous = st.toggle("Show all NASA tests, not only those inside my environment", key="comparateur_donnees_tous")
    tableau = tableau_des_tests(tests, fiches, scenario, tous=tous)
    st.caption(f"{len(tableau)} test rows from {tableau['Investigation id'].nunique()} investigations.")
    st.dataframe(tableau, hide_index=True, key="comparateur_donnees_tableau")
    st.download_button(
        "Download these tests (CSV)",
        tableau.to_csv(index=False).encode("utf-8"),
        file_name="flame_in_freefall_tests.csv",
        mime="text/csv",
        key="comparateur_donnees_csv",
    )
    st.caption("An empty cell means the value is not in NASA's tables. Source: NASA PSI, licence CC0-1.0.")

with onglet_variables:
    st.markdown("**What each investigation varies**")
    st.dataframe(ce_qui_varie(tests, fiches), hide_index=True, key="comparateur_donnees_variables")
    st.markdown("**Sensors and measurements**")
    choisies = st.multiselect(
        "Investigations (leave empty for all)",
        list(noms),
        format_func=lambda identifiant: f"{identifiant} · {noms[identifiant]}",
        key="comparateur_donnees_capteurs",
    )
    instruments = capteurs(charger_table_psi("measurements"), fiches, choisies)
    if instruments.empty:
        st.info("No instrument is listed for this selection.")
    else:
        st.caption(f"{len(instruments)} instruments, read from NASA's reports and science documents.")
        st.dataframe(instruments, hide_index=True, key="comparateur_donnees_instruments")
