"""Les listes et les noms de colonnes sur lesquels tout le monde s'appuie.

`tests/test_contrat.py` vérifie que les fichiers CSV respectent ces colonnes.
"""

HABITATS = ["Vaisseau", "Station", "Base lunaire", "Base martienne", "Rover pressurisé"]
PILIERS = ["Prévenir", "Détecter", "Éteindre"]
PROFILS = ["Étudiant", "Chercheur", "Ingénieur"]

# Valeur à écrire quand une information manque. On ne devine jamais une donnée NASA.
INCONNU = "inconnu"

# Atmosphère type de chaque habitat : (oxygène en %, pression en kPa).
# Base lunaire et rover : chiffres de l'énoncé. Les autres sont des hypothèses à valider.
ATMOSPHERES = {
    "Vaisseau": (21, 101),
    "Station": (21, 101),
    "Base lunaire": (30, 70),
    "Base martienne": (30, 70),
    "Rover pressurisé": (30, 70),
}

# data/investigations.csv : une ligne par investigation PSI.
COLONNES_FICHES = [
    "id",
    "psi",
    "nom",
    "pilier",
    "priorite",
    "objectif",
    "type_combustible",
    "combustible",
    "materiel",
    "oxygene_min",
    "oxygene_max",
    "pression_kpa",
    "debit_air",
    "ce_qui_varie",
    "capteurs",
    "habitats",
    "nb_tests",
    "resume",
    "source_psi",
    "doi",
    "source_rapport",
    "verifie_par",
]

# data/tests.csv : une ligne par test d'une investigation.
COLONNES_TESTS = [
    "investigation_id",
    "test_id",
    "combustible",
    "oxygene_pct",
    "pression_kpa",
    "debit_air_cm_s",
    "resultat",
    "source",
]

# data/publications.csv : une ligne par rapport trouvé avec l'API NTRS.
COLONNES_PUBLICATIONS = [
    "ntrs_id",
    "titre",
    "annee",
    "auteurs",
    "resume",
    "url",
    "investigation_id",
]
