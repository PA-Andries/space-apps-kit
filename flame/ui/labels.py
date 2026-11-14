"""English text shown on screen for the contract values.

Contract values (`flame/commun/constantes.py`) and the CSV files stay in French:
only what the user sees is translated.
"""

from flame.commun import INCONNU

LABELS = {
    # Celestial bodies, places and habitats
    "Terre": "Earth",
    "Lune": "Moon",
    "Mars": "Mars",
    "Vaisseau": "Spacecraft",
    "Station": "Space station",
    "Base lunaire": "Moon base",
    "Base martienne": "Mars base",
    "Rover pressurisé": "Pressurized rover",
    # Pillars
    "Prévenir": "Prevent",
    "Détecter": "Detect",
    "Éteindre": "Extinguish",
    # Profiles
    "Chercheur": "Researcher",
    "Ingénieur": "Engineer",
    # Fuel types
    "solide": "solid",
    "liquide": "liquid",
    "gaz": "gas",
    "aucun": "none",
    INCONNU: "unknown",
}


def label(value: object) -> str:
    """English text for a value: `label("Prévenir")` gives "Prevent".

    Several values separated by ";" are translated one by one. A value missing from the
    dictionary is shown as it is.
    """
    parts = [part.strip() for part in str(value).split(";") if part.strip()]
    return ", ".join(LABELS.get(part, part) for part in parts)
