"""Les blocs d'affichage partagés entre les pages."""

from collections.abc import Callable

import pandas as pd
import streamlit as st

from flame.commun import PILIERS
from flame.ui.libelles import libelle
from flame.ui.lieux import LIEUX, choisir_lieu, choisir_pilier, lieu_courant, pilier_courant
from flame.ui.scene import scene_lieux

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


def _rangee_boutons(valeurs: list[str], choisie: str | None, icones: dict, action: Callable, prefixe: str) -> None:
    """Une rangée de boutons ; celui de la valeur choisie est mis en avant."""
    for colonne, valeur in zip(st.columns(len(valeurs)), valeurs, strict=True):
        colonne.button(
            libelle(valeur),
            icon=icones.get(valeur),
            key=f"{prefixe}_{valeur}",
            type="primary" if valeur == choisie else "secondary",
            width="stretch",
            on_click=action,
            args=(valeur,),
        )


HAUTEUR_LIEUX = 190

# Les boutons des lieux sont posés par-dessus la scène 3D et rendus transparents :
# on clique « sur la planète », mais c'est le bouton Streamlit qui reçoit le clic.
STYLE_LIEUX = f"""<style>
.st-key-ui_lieux_boutons {{ margin-top: calc(-{HAUTEUR_LIEUX}px - 1rem); position: relative; z-index: 1; }}
.st-key-ui_lieux_boutons [data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap; }}
.st-key-ui_lieux_boutons [data-testid="stColumn"] {{ min-width: 0; }}
.st-key-ui_lieux_boutons button {{
  height: {HAUTEUR_LIEUX}px; align-items: flex-end; padding-bottom: 8px;
  background: transparent; border: 2px solid transparent; border-radius: 20px;
  transition: border-color 0.2s, background 0.2s, transform 0.2s;
}}
.st-key-ui_lieux_boutons button:hover {{
  background: rgba(249, 115, 22, 0.07); border-color: rgba(249, 115, 22, 0.45); transform: translateY(-2px);
}}
.st-key-ui_lieux_boutons [data-testid="stBaseButton-primary"] {{
  background: rgba(249, 115, 22, 0.1); border-color: #f97316; color: #fdba74;
}}
.st-key-ui_lieux_boutons button p {{
  font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
@media (max-width: 640px) {{
  .st-key-ui_lieux_boutons [data-testid="stHorizontalBlock"] {{ gap: 0.25rem; }}
  .st-key-ui_lieux_boutons button {{ padding: 0 2px 4px; }}
  .st-key-ui_lieux_boutons button p {{ font-size: 0.6rem; }}
}}
</style>"""


def choix_lieu() -> str | None:
    """Les lieux en 3D (Terre puis habitats), à choisir en cliquant dessus. Renvoie le lieu choisi, ou None."""
    lieu = lieu_courant()
    st.html(STYLE_LIEUX)
    scene_lieux(LIEUX, lieu, hauteur=HAUTEUR_LIEUX)
    with st.container(key="ui_lieux_boutons"):
        _rangee_boutons(LIEUX, lieu, {}, choisir_lieu, "ui_lieu")
    return lieu


def choix_pilier() -> str | None:
    """Les boutons des piliers : prévenir, détecter, éteindre. Renvoie le pilier choisi, ou None."""
    pilier = pilier_courant()
    _rangee_boutons(PILIERS, pilier, ICONES_PILIERS, choisir_pilier, "ui_pilier")
    return pilier
