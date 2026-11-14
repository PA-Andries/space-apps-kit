"""Le texte anglais affiché à l'écran pour les valeurs du contrat.

Les valeurs du contrat (`flame/commun/constantes.py`) et des CSV restent en français :
on ne traduit que ce que l'utilisateur voit.
"""

from flame.commun import INCONNU

LIBELLES = {
    # Lieux et habitats
    "Terre": "Earth",
    "Vaisseau": "Spacecraft",
    "Station": "Space station",
    "Base lunaire": "Moon base",
    "Base martienne": "Mars base",
    "Rover pressurisé": "Pressurized rover",
    # Piliers
    "Prévenir": "Prevent",
    "Détecter": "Detect",
    "Éteindre": "Extinguish",
    # Profils
    "Étudiant": "Student",
    "Chercheur": "Researcher",
    "Ingénieur": "Engineer",
    # Types de combustible
    "solide": "solid",
    "liquide": "liquid",
    "gaz": "gas",
    "aucun": "none",
    INCONNU: "unknown",
}


def libelle(valeur: object) -> str:
    """Le texte anglais d'une valeur : `libelle("Prévenir")` donne « Prevent ».

    Plusieurs valeurs séparées par « ; » sont traduites une à une. Une valeur inconnue du
    dictionnaire est affichée telle quelle.
    """
    morceaux = [morceau.strip() for morceau in str(valeur).split(";") if morceau.strip()]
    return ", ".join(LIBELLES.get(morceau, morceau) for morceau in morceaux)
