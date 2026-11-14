"""Version de départ de l'assistant : pas encore d'IA branchée.

À faire par le rôle E : envoyer `prompts/systeme.md`, les fiches et la question à l'API du LLM.
La clé se lit avec `cle_api()` et ne s'écrit jamais dans le code.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

DOSSIER_PROMPTS = Path(__file__).parent / "prompts"


def cle_api() -> str | None:
    """La clé du LLM rangée dans les Secrets de Streamlit, ou None si elle manque."""
    try:
        return st.secrets.get("LLM_API_KEY")
    except FileNotFoundError:  # aucun fichier .streamlit/secrets.toml sur cet ordinateur
        return None


def lire_prompt(nom: str) -> str:
    """Le texte d'une consigne, par exemple `lire_prompt("systeme")`."""
    return (DOSSIER_PROMPTS / f"{nom}.md").read_text(encoding="utf-8")


def repondre(question: str, historique: list[dict[str, str]], fiches: pd.DataFrame) -> str:
    """La réponse de l'assistant à `question`.

    `historique` est la liste des messages précédents : {"role": "user" ou "assistant", "content": texte}.
    """
    if cle_api() is None:
        return "L'assistant n'est pas encore branché : il manque `LLM_API_KEY` dans les Secrets."
    return f"(à faire) Réponse fondée sur {len(fiches)} fiches à la question : {question}"
