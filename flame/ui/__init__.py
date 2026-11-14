"""Role F (Interface and 3D): the look of the site and the reusable components.

Other roles may use everything listed here.
"""

from flame.ui.components import body_picker, investigation_card, pillar_picker, place_picker
from flame.ui.labels import label
from flame.ui.places import EARTH, place_conditions
from flame.ui.scene import flame_scene
from flame.ui.sidebar import show_sidebar

# French names from the team contract (BRIEF_EQUIPE_IA.md, section 5), still used by app.py
# and pages/recherche.py. Keep them until their owners switch to the English names.
afficher_cadre = show_sidebar
carte_fiche = investigation_card
scene_3d = flame_scene

__all__ = [
    "EARTH",
    "afficher_cadre",
    "body_picker",
    "carte_fiche",
    "flame_scene",
    "investigation_card",
    "label",
    "pillar_picker",
    "place_conditions",
    "place_picker",
    "scene_3d",
    "show_sidebar",
]
