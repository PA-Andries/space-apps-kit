"""Role F (Interface and 3D): the look of the site and the reusable components.

Other roles may use everything listed here.
"""

from flame.ui.chart import style_conditions_chart
from flame.ui.chatbot import flamy_corner
from flame.ui.components import investigation_card, place_buttons, place_picker
from flame.ui.coverage import coverage, coverage_card
from flame.ui.custom import left_the_place, single_value_style
from flame.ui.environment import (
    REFERENCE_PLACES,
    bounds_text,
    conditions,
    environment_values,
    save_environment,
    source_name,
)
from flame.ui.home import (
    assistant_mascot,
    card_title,
    chatbot_button,
    dashboard_header,
    footer,
    hero,
    mascot,
    section,
    stat_tiles,
    talking,
    verdict_banner,
)
from flame.ui.intro import how_to_use
from flame.ui.investigation import investigation_details
from flame.ui.labels import label
from flame.ui.outcomes import answer, count_outcomes, kind_of_result, outcomes_card
from flame.ui.places import EARTH, SPACESUIT, body_of, place_conditions
from flame.ui.scene import flame_scene
from flame.ui.top_bar import show_environment_in_sidebar, show_top_bar

# French names from the team contract (BRIEF_EQUIPE_IA.md, section 5), still used by app.py
# and pages/recherche.py. Keep them until their owners switch to the English names.
afficher_cadre = show_top_bar
carte_fiche = investigation_card
scene_3d = flame_scene

__all__ = [
    "coverage",
    "coverage_card",
    "flamy_corner",
    "answer",
    "count_outcomes",
    "kind_of_result",
    "outcomes_card",
    "assistant_mascot",
    "talking",
    "style_conditions_chart",
    "show_environment_in_sidebar",
    "source_name",
    "save_environment",
    "environment_values",
    "bounds_text",
    "conditions",
    "EARTH",
    "REFERENCE_PLACES",
    "SPACESUIT",
    "verdict_banner",
    "afficher_cadre",
    "body_of",
    "card_title",
    "chatbot_button",
    "carte_fiche",
    "dashboard_header",
    "flame_scene",
    "footer",
    "hero",
    "investigation_card",
    "investigation_details",
    "how_to_use",
    "label",
    "left_the_place",
    "mascot",
    "place_buttons",
    "place_conditions",
    "place_picker",
    "scene_3d",
    "section",
    "show_top_bar",
    "single_value_style",
    "stat_tiles",
]
