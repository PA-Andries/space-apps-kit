"""Role F (Interface and 3D): the look of the site and the reusable components.

Other roles may use everything listed here.
"""

from flame.ui.components import investigation_card, pillar_picker, place_picker
from flame.ui.home import card_title, dashboard_header, footer, hero, mascot, section, stat_tiles
from flame.ui.labels import label
from flame.ui.places import EARTH, body_of, place_conditions
from flame.ui.scene import flame_scene
from flame.ui.top_bar import show_top_bar

# French names from the team contract (BRIEF_EQUIPE_IA.md, section 5), still used by app.py
# and pages/recherche.py. Keep them until their owners switch to the English names.
afficher_cadre = show_top_bar
carte_fiche = investigation_card
scene_3d = flame_scene

__all__ = [
    "EARTH",
    "afficher_cadre",
    "body_of",
    "card_title",
    "carte_fiche",
    "dashboard_header",
    "flame_scene",
    "footer",
    "hero",
    "investigation_card",
    "label",
    "mascot",
    "pillar_picker",
    "place_conditions",
    "place_picker",
    "scene_3d",
    "section",
    "show_top_bar",
    "stat_tiles",
]
