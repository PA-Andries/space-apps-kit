"""Rôle F (Interface et 3D) : l'habillage du site et les composants réutilisables.

Les autres rôles peuvent utiliser tout ce qui est listé ici.
"""

from flame.ui.cadre import afficher_cadre
from flame.ui.composants import carte_fiche, choix_lieu, choix_pilier
from flame.ui.libelles import libelle
from flame.ui.lieux import TERRE, conditions_lieu
from flame.ui.scene import scene_3d

__all__ = [
    "TERRE",
    "afficher_cadre",
    "carte_fiche",
    "choix_lieu",
    "choix_pilier",
    "conditions_lieu",
    "libelle",
    "scene_3d",
]
