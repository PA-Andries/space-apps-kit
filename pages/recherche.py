"""Page Recherche. Propriétaire : rôle C (Recherche)."""

import streamlit as st

from flame.commun import ATMOSPHERES, HABITATS, charger_fiches, charger_publications, charger_tests, get_scenario
from flame.recherche import detail_du_score, filtrer, rechercher, valeurs_possibles
from flame.ui import carte_fiche

st.title("Recherche")

fiches = charger_fiches()
scenario = get_scenario()
oxygene_pct, pression_kpa = ATMOSPHERES[scenario["habitat"]]
st.caption(
    f"Classement pour : {scenario['habitat']} ({oxygene_pct} % d'oxygène, {pression_kpa} kPa) · "
    f"pilier « {scenario['pilier']} ». Le scénario se change dans la barre latérale."
)

question = st.text_input("Que cherchez-vous ?", placeholder="tissu, extinction, fumée…", key="recherche_question")
with st.expander("Filtres"):
    piliers = st.multiselect("Pilier", valeurs_possibles(fiches, "pilier"), key="recherche_filtre_piliers")
    types_combustible = st.multiselect(
        "Type de combustible", valeurs_possibles(fiches, "type_combustible"), key="recherche_filtre_combustibles"
    )
    habitats = st.multiselect("Habitat concerné", HABITATS, key="recherche_filtre_habitats")

resultats = rechercher(question, filtrer(fiches, piliers, types_combustible, habitats), scenario)

st.caption(f"{len(resultats)} investigation(s) sur {len(fiches)}")
if resultats.empty:
    st.info("Aucune investigation ne correspond. Essayez un autre mot ou retirez un filtre.")

tests = charger_tests()
publications = charger_publications()
for _, fiche in resultats.iterrows():
    carte_fiche(fiche)
    st.progress(int(fiche["score"]) / 100, text=f"Score pour ce scénario : {int(fiche['score'])} / 100")
    with st.expander(f"Pourquoi ce score, et la fiche de {fiche['id']}"):
        st.dataframe(detail_du_score(fiche, scenario), hide_index=True, key=f"recherche_score_{fiche['id']}")
        st.markdown(f"**Objectif :** {fiche['objectif']}")
        st.markdown(f"**Combustible :** {fiche['combustible']} · **Ce qui varie :** {fiche['ce_qui_varie']}")
        st.markdown(f"**Mesures :** {fiche['capteurs']}")
        st.markdown("**Tests**")
        st.dataframe(
            tests[tests["investigation_id"] == fiche["id"]], hide_index=True, key=f"recherche_tests_{fiche['id']}"
        )
        st.markdown("**Rapports NTRS**")
        st.dataframe(
            publications[publications["investigation_id"] == fiche["id"]][["titre", "annee", "auteurs", "url"]],
            hide_index=True,
            key=f"recherche_publications_{fiche['id']}",
        )
