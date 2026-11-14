"""Les listes et les noms de colonnes sur lesquels tout le monde s'appuie.

`tests/test_contrat.py` vérifie que les fichiers CSV respectent ces colonnes.
"""

HABITATS = ["Vaisseau", "Station", "Base lunaire", "Base martienne", "Rover pressurisé"]
PILIERS = ["Prévenir", "Détecter", "Éteindre"]
PROFILS = ["Étudiant", "Chercheur", "Ingénieur"]

# Valeur à écrire quand une information manque. On ne devine jamais une donnée NASA.
INCONNU = "inconnu"

# Atmosphère de chaque habitat : (oxygène en %, pression en kPa). `None` veut dire inconnu.
# - Base lunaire et rover : chiffres de l'énoncé, 30 % d'oxygène ou plus, 10,2 psi (70,3 kPa) ou moins.
#   Ce sont des bornes (oxygène minimum, pression maximum) : on les montre comme une zone, jamais comme un point.
# - Vaisseau et station : 21 %, environ 101 kPa. Hypothèse de l'équipe à sourcer, absente de l'énoncé.
# - Base martienne : l'énoncé ne donne aucun chiffre, donc aucun chiffre ici.
ATMOSPHERES = {
    "Vaisseau": (21, 101),
    "Station": (21, 101),
    "Base lunaire": (30, 70.3),
    "Base martienne": (None, None),
    "Rover pressurisé": (30, 70.3),
}

# Ce que valent les chiffres d'ATMOSPHERES : à afficher à côté d'eux.
# « borne » : oxygène minimum et pression maximum (énoncé). « hypothèse » : choix de l'équipe, à sourcer.
NATURE_ATMOSPHERES = {
    "Vaisseau": "hypothèse",
    "Station": "hypothèse",
    "Base lunaire": "borne",
    "Base martienne": INCONNU,
    "Rover pressurisé": "borne",
}

# Gravité de chaque habitat, en fraction de celle de la Terre (0 = microgravité).
# Valeurs physiques usuelles (Lune 0,17, Mars 0,38), pas des données de l'énoncé. Le rover est compté sur la Lune,
# comme sur la page d'accueil. PSI n'a aucun test en gravité lunaire ou martienne.
GRAVITES = {
    "Vaisseau": 0.0,
    "Station": 0.0,
    "Base lunaire": 0.17,
    "Base martienne": 0.38,
    "Rover pressurisé": 0.17,
}

# Les types de combustible que l'utilisateur peut choisir dans son environnement.
TYPES_COMBUSTIBLE = ["solide", "liquide", "gaz"]

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
