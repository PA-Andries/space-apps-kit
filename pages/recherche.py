"""Page Investigations. Propriétaire : rôle C (Recherche). Les textes affichés sont en anglais.

Une seule vue depuis le 15 novembre (rôle F, accord de Martin) : la fiche d'une investigation. Les onglets
Classement et Ce qu'on ne sait pas sont retirés ; la page 1 montre déjà ce qu'on ne sait pas.
Le classement reste : il repose sur les preuves pour l'environnement choisi en page 1 et range la liste de
recherche, la plus pertinente en premier. Le score sert à trier mais n'est pas affiché.
Chaque fiche montre les rubriques du tableau blanc (comportement, dangers, prévention, trace des données,
comparer), tirées des fiches et des tests sans rien inventer.
"""

import pandas as pd
import streamlit as st

from flame.commun import charger_fiches, charger_tests, get_scenario
from flame.recherche import champs_inconnus, les_plus_pertinentes, tests_dans_les_plages
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
        morceaux.append(f"pressure from {pression:g} kPa (the lowest tested)")
    return ", ".join(morceaux) or "oxygen and pressure not recorded"


def _en_anglais(ce_qui_varie: object) -> str:
    """« oxygène de 12 à 34 % ; combustible (2 différents) » en anglais : la fiche est écrite en français."""
    texte = _texte(ce_qui_varie)
    for francais, anglais in (
        ("débit d'air", "air flow"),
        ("oxygène", "oxygen"),
        ("pression", "pressure"),
        ("combustible", "fuel"),
        ("différents", "different"),
        (" de ", " from "),
        (" à ", " to "),
    ):
        texte = texte.replace(francais, anglais)
    return texte


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
    st.markdown(
        f"**Conditions tested:** {_plage_testee(fiche)} · **What varies:** {_en_anglais(fiche.get('ce_qui_varie'))}"
    )

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
