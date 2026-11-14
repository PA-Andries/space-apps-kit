"""Page Equipment and Earth. Propriétaire : rôle E (Assistant). Les textes affichés sont en anglais.

Trois onglets : la recherche utile aux détecteurs de demain, celle utile aux extincteurs,
et ce que ces recherches apportent sur Terre. Chaque texte vient d'une fiche ou d'une table PSI.
"""

import pandas as pd
import streamlit as st

from flame.assistant import fiches_pour, instruments_de, liens_terre, retombees_sur_terre
from flame.commun import charger_fiches, charger_table_psi

fiches = charger_fiches()
mesures = charger_table_psi("measurements")


def texte(valeur: object) -> str:
    """La valeur en texte, ou une chaîne vide quand la case est vide."""
    return "" if pd.isna(valeur) else str(valeur).strip()


def montrer_fiche(fiche: pd.Series) -> None:
    """Une investigation : ce qu'elle cherche, ce qu'elle mesure, et où lire la source."""
    with st.container(border=True):
        st.markdown(f"**{fiche['nom']}** · {fiche['id']}")
        if texte(fiche["resume"]):
            st.write(texte(fiche["resume"]))
        if texte(fiche["objectif"]):
            with st.expander("Objective, as written by NASA"):
                st.write(texte(fiche["objectif"]))
        instruments = instruments_de(fiche["id"], mesures)
        if not instruments.empty:
            with st.expander(f"What it measured ({len(instruments)} instruments)"):
                st.dataframe(
                    instruments.rename(
                        columns={"instrument": "Instrument", "measures": "Measures", "unit": "Unit", "source": "Source"}
                    ),
                    hide_index=True,
                )
        nb_tests = texte(fiche["nb_tests"])
        st.caption(f"Tests in NASA's PSI table: {nb_tests or 'not recorded'}")
        if texte(fiche["source_psi"]):
            st.link_button("Open on NASA PSI", texte(fiche["source_psi"]))


def montrer_equipement(equipement: str) -> None:
    trouvees = fiches_pour(equipement, fiches)
    if trouvees.empty:
        st.info("These investigations are not in the data loaded right now.")
    for _, fiche in trouvees.iterrows():
        montrer_fiche(fiche)


st.title("Equipment and Earth")
st.write(
    "Which NASA research helps design tomorrow's fire detectors and extinguishers, and what it brings back to Earth. "
    "The text about each investigation is quoted from NASA's PSI records; only the short introductions are ours."
)
st.caption(
    "Linking an investigation to a kind of equipment is our team's judgement, not a NASA classification. "
    "This site helps understand the research: it is not a safety certification."
)

onglet_detecteurs, onglet_extincteurs, onglet_terre = st.tabs(["Detectors", "Extinguishers", "On Earth"])

with onglet_detecteurs:
    st.subheader("Smoke and particles in microgravity")
    st.write(
        "Without buoyancy, smoke does not rise towards a detector: it follows the ventilation flow. "
        "These investigations measured the smoke itself."
    )
    montrer_equipement("detecteurs")

with onglet_extincteurs:
    st.subheader("What puts a flame out in microgravity")
    st.write("These investigations measured when a flame goes out: diluted atmospheres, air flow, oxygen limits.")
    montrer_equipement("extincteurs")

with onglet_terre:
    st.subheader("What this research brings back to Earth")
    retombees = retombees_sur_terre(charger_table_psi("investigations"))
    if retombees.empty:
        st.info("NASA's impact statements are not in the data loaded right now.")
    else:
        st.write("NASA's own impact statement for each investigation, quoted from its PSI record.")
        for ligne in retombees.itertuples():
            with st.expander(f"{ligne.nom} · {ligne.id}"):
                st.markdown(f"> {ligne.texte}")
                st.link_button("Source: NASA PSI", ligne.source, key=f"retombee_{ligne.id}")
    liens = liens_terre(charger_table_psi("resources"))
    if not liens.empty:
        st.subheader("NASA spinoffs listed in the challenge resources")
        for ligne in liens.itertuples():
            st.markdown(f"- [{ligne.title}]({ligne.url}) (our one-line description: {ligne.note})")
