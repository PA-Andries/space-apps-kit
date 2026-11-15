"""L'environnement étudié par l'utilisateur (page 1), décrit en quelques lignes pour le LLM.

Le scénario vient de `get_scenario()` (rôle A). Une clé absente est omise et une plage sans borne
s'écrit « inconnu » : on ne devine jamais une valeur.
"""

from flame.commun import get_scenario


def scenario_courant() -> dict:
    """Le scénario choisi en page 1, ou un dictionnaire vide quand Streamlit ne tourne pas (scripts)."""
    try:
        return dict(get_scenario())
    except Exception:  # hors de Streamlit, la mémoire de session peut manquer
        return {}


def plage(valeurs: object, unite: str) -> str | None:
    """« au moins 30 % », « au plus 70.3 kPa », « de 19 à 23 % », ou None quand aucune borne n'est connue."""
    if isinstance(valeurs, int | float):
        return f"{valeurs:g} {unite}"
    if not isinstance(valeurs, list | tuple):
        return None
    mini, maxi = (list(valeurs) + [None, None])[:2]
    if mini is None and maxi is None:
        return None
    if mini is None:
        return f"au plus {maxi:g} {unite}"
    if maxi is None:
        return f"au moins {mini:g} {unite}"
    return f"de {mini:g} à {maxi:g} {unite}"


def gravite_en_texte(gravite: object) -> str:
    """« microgravité (0 g) », « 1 g », « 0.165 g (… aucun test NASA PSI à cette gravité …) » ou « inconnue »."""
    if not isinstance(gravite, int | float):
        return "inconnue"
    if gravite == 0:
        return "microgravité (0 g)"
    if 0 < gravite < 1:
        # La gravité partielle est celle du lieu (Lune, Mars), pas un réglage de l'outil : Flamy ne doit pas
        # la présenter comme une condition couverte par les données.
        return (
            f"{gravite:g} g (gravité propre du lieu ; aucun test NASA PSI à cette gravité : "
            "les tests existent en microgravité, 0 g, et quelques-uns à 1 g)"
        )
    return f"{gravite:g} g"


def decrire_environnement(scenario: dict) -> str:
    """L'environnement en une ligne par paramètre, ou une chaîne vide quand le scénario est vide."""
    lignes = []
    if scenario.get("habitat"):
        lignes.append(f"- Habitat : {scenario['habitat']}")
    for cle, nom, unite in [
        ("oxygene_pct", "Oxygène", "%"),
        ("pression_kpa", "Pression", "kPa"),
        ("debit_air_cm_s", "Débit d'air", "cm/s"),
    ]:
        if cle in scenario:
            lignes.append(f"- {nom} : {plage(scenario[cle], unite) or 'inconnu'}")
    if "gravite" in scenario:
        lignes.append(f"- Gravité : {gravite_en_texte(scenario['gravite'])}")
    if "type_combustible" in scenario:
        lignes.append(f"- Combustibles : {', '.join(scenario['type_combustible']) or 'tous'}")
    if scenario.get("profil"):
        lignes.append(f"- Profil du lecteur : {scenario['profil']}")
    return "\n".join(lignes)
