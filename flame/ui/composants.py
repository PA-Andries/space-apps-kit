"""Les blocs d'affichage partagés entre les pages."""

from collections.abc import Callable

import pandas as pd
import streamlit as st

from flame.commun import PILIERS, get_scenario
from flame.ui.libelles import libelle
from flame.ui.lieux import LIEUX, choisir_lieu, choisir_pilier, lieu_courant

ICONES_LIEUX = {
    "Terre": "🌍",
    "Vaisseau": "🚀",
    "Station": "🛰️",
    "Base lunaire": "🌕",
    "Base martienne": "🔴",
    "Rover pressurisé": "🚙",
}
ICONES_PILIERS = {
    "Prévenir": ":material/shield:",
    "Détecter": ":material/sensors:",
    "Éteindre": ":material/fire_extinguisher:",
}


def carte_fiche(fiche: pd.Series) -> None:
    """Affiche une investigation en résumé : `carte_fiche(fiches.iloc[0])`."""
    with st.container(border=True):
        st.markdown(f"**{fiche['id']}** · {fiche['nom']}")
        st.caption(f"{libelle(fiche['pilier'])} · {libelle(fiche['type_combustible'])} · {fiche['materiel']}")
        st.write(fiche["resume"])
        st.link_button("View on PSI", fiche["source_psi"])


def _rangee_boutons(valeurs: list[str], choisie: str, icones: dict, action: Callable, prefixe: str) -> None:
    """Une rangée de boutons ; celui de la valeur choisie est mis en avant."""
    for colonne, valeur in zip(st.columns(len(valeurs)), valeurs, strict=True):
        colonne.button(
            libelle(valeur),
            icon=icones[valeur],
            key=f"{prefixe}_{valeur}",
            type="primary" if valeur == choisie else "secondary",
            width="stretch",
            on_click=action,
            args=(valeur,),
        )


def choix_lieu() -> str:
    """Les boutons des lieux (Terre puis habitats). Renvoie le lieu choisi."""
    lieu = lieu_courant()
    _rangee_boutons(LIEUX, lieu, ICONES_LIEUX, choisir_lieu, "ui_lieu")
    return lieu


def choix_pilier() -> str:
    """Les boutons des piliers : prévenir, détecter, éteindre. Renvoie le pilier choisi."""
    pilier = get_scenario()["pilier"]
    _rangee_boutons(PILIERS, pilier, ICONES_PILIERS, choisir_pilier, "ui_pilier")
    return pilier
