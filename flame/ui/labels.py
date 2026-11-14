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
    "Scaphandre": "spacesuit",
    # Pillars
    "Prévenir": "Prevent",
    "Détecter": "Detect",
    "Éteindre": "Extinguish",
    # Profiles
    "Chercheur": "Researcher",
    "Ingénieur": "Engineer",
    # Fuel types and other contract values
    "solide": "solid",
    "liquide": "liquid",
    "gaz": "gas",
    "aucun": "none",
    "fumée": "smoke",
    "poussière": "dust",
    INCONNU: "unknown",
}


def label(value: object) -> str:
    """English text for a value: `label("Prévenir")` gives "Prevent".

    Several values separated by ";" are translated one by one. A value missing from the
    dictionary is shown as it is.
    """
    parts = [part.strip() for part in str(value).split(";") if part.strip()]
    return ", ".join(_one(part) for part in parts)


def _one(part: str) -> str:
    """One value in English; "solide (modèle)" (a fuel modelled by a gas) gives "solid (model)"."""
    base, _, detail = part.partition(" (")
    if detail.startswith("modèle"):
        return f"{LABELS.get(base, base)} (model)"
    return LABELS.get(part, part)
