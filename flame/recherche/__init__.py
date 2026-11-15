"""Rôle C (Recherche) : le classement des investigations pour un environnement, et ce qu'on ne sait pas."""

from flame.recherche.conditions import tests_dans_les_plages
from flame.recherche.descriptif import descriptif
from flame.recherche.filtres import filtrer, valeurs_possibles
from flame.recherche.independance import independance
from flame.recherche.lacunes import ce_quon_ne_sait_pas, champs_inconnus, frontiere_des_solides, verdict
from flame.recherche.lacunes_visuelles import couverture, mesures_notees, regle_de_l_oxygene
from flame.recherche.moteur import les_plus_pertinentes, rechercher
from flame.recherche.score import detail_du_score
from flame.recherche.synthese import synthese_des_plus_pertinentes
from flame.recherche.vue_lacunes import afficher_ce_quon_ne_sait_pas

__all__ = [
    "afficher_ce_quon_ne_sait_pas",
    "ce_quon_ne_sait_pas",
    "champs_inconnus",
    "couverture",
    "descriptif",
    "detail_du_score",
    "filtrer",
    "frontiere_des_solides",
    "independance",
    "les_plus_pertinentes",
    "mesures_notees",
    "rechercher",
    "regle_de_l_oxygene",
    "synthese_des_plus_pertinentes",
    "tests_dans_les_plages",
    "valeurs_possibles",
    "verdict",
]
