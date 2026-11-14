"""Rôle F (Interface et 3D) : l'habillage du site et les composants réutilisables.

Les autres rôles peuvent utiliser tout ce qui est listé ici.
"""

from flame.ui.cadre import afficher_cadre
from flame.ui.composants import carte_fiche
from flame.ui.scene import scene_3d

__all__ = ["afficher_cadre", "carte_fiche", "scene_3d"]
