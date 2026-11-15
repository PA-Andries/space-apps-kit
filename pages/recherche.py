"""Page Investigations. Propriétaire : rôle C (Recherche). Les textes affichés sont en anglais.

Deux onglets depuis le 15 novembre.
« Investigation » (rôle F, accord de Martin) : la fiche d'une investigation, et le classement complet dans
une colonne à droite. Le classement repose sur les preuves pour l'environnement choisi en page 1 ; le score
sert à trier mais n'est pas affiché, seulement le rang.
La fiche est la même carte que sur la page 1 (demande de Hugo, 15 novembre) : ce que l'expérience a étudié,
pourquoi elle compte pour l'environnement, puis la description complète de NASA. Pour les huit investigations
que l'énoncé range sous prevention, detection ou suppression, la ligne « Statement » de la carte le dit.
« Tests + CSV » (demande d'Ethan) : le tableau des tests de l'environnement et son export, qui arrivent de
la page Data and export, retirée du menu.
"""

import streamlit as st

from flame.commun import HABITAT_PERSONNALISE, charger_fiches, charger_tests, get_scenario
from flame.comparateur import tableau_des_tests
from flame.recherche import descriptif, les_plus_pertinentes
from flame.ui import investigation_details, label

st.title("Investigations")

fiches = charger_fiches()
tests = charger_tests()
scenario = get_scenario()
habitat = scenario.get("habitat")
st.caption(
    f"Sorted for your environment, {label(habitat)}: the most relevant first (the tests nearest your oxygen and "
    "pressure, your fuels and your gravity). Pick one in the ranking. Change your environment on the first page."
)

# Le classement complet, dans une colonne à droite : un clic sur une investigation l'affiche à gauche.
# Le score n'est pas affiché, seulement le rang.
classement = les_plus_pertinentes(fiches, scenario)
if st.session_state.get("recherche_fiche") not in set(classement["id"]):
    st.session_state["recherche_fiche"] = classement["id"].iloc[0]  # la plus pertinente, au départ
choix = st.session_state["recherche_fiche"]


def _choisir(id_fiche: str) -> None:
    st.session_state["recherche_fiche"] = id_fiche


onglet_fiche, onglet_tests = st.tabs(["Investigation", "Tests + CSV"])

with onglet_fiche:
    colonne_fiche, colonne_classement = st.columns([3, 1.15], gap="large")
    with colonne_classement:
        st.html('<p class="ff-rank-title">Ranking</p>')
        with st.container(key="recherche_classement", height=720, border=False):
            for rang, (id_fiche, nom) in enumerate(zip(classement["id"], classement["nom"], strict=True), start=1):
                st.button(
                    f"{rang}. {nom}",
                    key=f"recherche_rang_{id_fiche}",
                    help=f"{nom} · {id_fiche}",  # le nom entier au survol : la liste le coupe après deux lignes
                    type="primary" if id_fiche == choix else "secondary",
                    width="stretch",
                    on_click=_choisir,
                    args=(id_fiche,),
                )

    with colonne_fiche:
        fiche = classement[classement["id"] == choix].iloc[0]
        rang = list(classement["id"]).index(choix) + 1
        # Le nom de l'environnement dans une phrase, comme sur la page 1 : « Why it matters for Moon base ».
        nom_habitat = label(habitat)
        environnement = (
            "your custom environment" if habitat == HABITAT_PERSONNALISE else nom_habitat[:1].upper() + nom_habitat[1:]
        )
        # La même carte que sur la page 1, avec les mêmes textes : rien n'est ajouté ni retiré ici.
        investigation_details(fiche, descriptif(fiche, scenario, tests), rang, environnement)


with onglet_tests:
    # Déménagé depuis la page Data and export : le tableau des tests de l'environnement et son export.
    tous = st.toggle("Show all NASA tests, not only those inside my environment", key="recherche_tests_tous")
    tableau = tableau_des_tests(tests, fiches, scenario, tous=tous)
    # Le tableau compte des lignes de test : seules les investigations qui en ont une y paraissent.
    st.caption(
        f"{len(tableau):,} test rows from {tableau['Investigation id'].nunique()} investigations "
        "that ran their own tests."
    )
    st.dataframe(tableau, hide_index=True, key="recherche_tests_tableau")
    st.download_button(
        "Download these tests (CSV)",
        tableau.to_csv(index=False).encode("utf-8"),
        file_name="flame_in_freefall_tests.csv",
        mime="text/csv",
        key="recherche_tests_csv",
    )
    st.caption("An empty cell means the value is not in NASA's tables. Source: NASA PSI, licence CC0-1.0.")
