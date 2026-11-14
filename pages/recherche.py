"""Page Investigations. Propriétaire : rôle C (Recherche). Les textes affichés sont en anglais.

Recadrage du 14 novembre (BRIEF_EQUIPE_IA.md, section 5) : trois onglets, Classement · Fiche · Ce qu'on ne sait pas.
Le classement repose sur les preuves pour l'environnement choisi ; le pilier est un filtre et une étiquette.
"""

import streamlit as st

from flame.commun import PILIERS, charger_fiches, charger_tests, get_scenario
from flame.recherche import ce_qu_on_ne_sait_pas, champs_inconnus, detail_du_score, les_plus_pertinentes
from flame.ui import carte_fiche, label

TOUS = "All"
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

st.title("Investigations")

fiches = charger_fiches()
tests = charger_tests()
scenario = get_scenario()
habitat = scenario["habitat"]
st.caption(f"Ranked for your environment: {label(habitat)}. Change it on the first page.")

choix_pilier = st.selectbox(
    "Fire-safety pillar",
    [TOUS, *PILIERS],
    format_func=lambda pilier: pilier if pilier == TOUS else label(pilier),
    key="recherche_pilier",
)
pilier = None if choix_pilier == TOUS else choix_pilier
classement = les_plus_pertinentes(fiches, scenario, pilier=pilier)

onglet_classement, onglet_fiche, onglet_inconnu = st.tabs(["Ranking", "Investigation", "What we don't know"])

with onglet_classement:
    st.caption(
        f"{len(classement)} investigation(s) out of {len(fiches)}. The score rests on the evidence for your "
        "environment: atmosphere 40, fuel 25, gravity 20, data 15. These weights are the team's judgement. "
        "The pillar filters the list; it is not part of the score."
    )
    if classement.empty:
        st.info("No investigation is useful to this pillar. Choose another pillar.")
    for _, fiche in classement.iterrows():
        carte_fiche(fiche)
        etiquette = f" · {fiche['etiquette']} for {label(pilier)}" if pilier and fiche["etiquette"] else ""
        st.markdown(f"**Score: {int(fiche['score'])} / 100**{etiquette}")
        with st.expander(f"Why {fiche['id']} is ranked here"):
            st.dataframe(
                detail_du_score(fiche, scenario),
                hide_index=True,
                column_config=TITRES_SCORE,
                key=f"recherche_score_{fiche['id']}",
            )
        st.page_link("pages/comparateur.py", label="Compare", query_params={"id": fiche["id"]})

with onglet_fiche:
    if classement.empty:
        st.info("No investigation to show.")
    else:
        noms = dict(zip(classement["id"], classement["nom"], strict=True))
        choix = st.selectbox(
            "Investigation",
            list(noms),
            format_func=lambda id_fiche: f"{id_fiche} · {noms[id_fiche]}",
            key="recherche_fiche",
        )
        fiche = classement[classement["id"] == choix].iloc[0]
        carte_fiche(fiche)
        st.markdown(f"**Goal:** {fiche['objectif']}")
        st.markdown(f"**Fuel:** {fiche['combustible']} · **What varies:** {fiche['ce_qui_varie']}")
        st.markdown(f"**Measurements:** {fiche['capteurs']}")
        inconnus = champs_inconnus(fiche)
        if inconnus:
            st.caption(f"Not recorded by NASA for this investigation: {', '.join(inconnus)}.")
        st.markdown("**Tests**")
        st.dataframe(
            tests[tests["investigation_id"] == fiche["id"]],
            hide_index=True,
            column_config=TITRES_TESTS,
            key="recherche_tests_fiche",
        )
        st.page_link("pages/comparateur.py", label="Compare", query_params={"id": fiche["id"]})

with onglet_inconnu:
    st.caption(
        f"Gaps in NASA's data for your environment ({label(habitat)}). "
        "Counted on PSI's test tables: nothing is guessed."
    )
    for constat in ce_qu_on_ne_sait_pas(habitat, fiches, tests):
        st.markdown(f"- {constat}")
