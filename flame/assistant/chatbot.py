"""L'assistant : envoie les consignes, les fiches, l'historique et la question à l'API Gemini.

La clé se lit avec `cle_api()` et ne s'écrit jamais dans le code.
"""

from pathlib import Path

import pandas as pd
import requests
import streamlit as st

DOSSIER_PROMPTS = Path(__file__).parent / "prompts"
MODELE = "gemini-3.5-flash"
URL_GEMINI = "https://generativelanguage.googleapis.com/v1beta/models/{modele}:generateContent"
DELAI_MAX_S = 60
# Gemini appelle « model » ce que la page appelle « assistant ».
ROLES_GEMINI = {"user": "user", "assistant": "model"}
MESSAGES_ERREUR = {
    429: "Le quota gratuit de Gemini est atteint pour le moment. Réessayez dans une minute.",
    503: "Gemini est surchargé en ce moment. Réessayez dans quelques secondes.",
}


def cle_api() -> str | None:
    """La clé du LLM rangée dans les Secrets de Streamlit, ou None si elle manque."""
    try:
        return st.secrets.get("LLM_API_KEY")
    except FileNotFoundError:  # aucun fichier .streamlit/secrets.toml sur cet ordinateur
        return None


def lire_prompt(nom: str) -> str:
    """Le texte d'une consigne, par exemple `lire_prompt("systeme")`."""
    return (DOSSIER_PROMPTS / f"{nom}.md").read_text(encoding="utf-8")


def fiches_en_texte(fiches: pd.DataFrame) -> str:
    """Les fiches en texte simple, une par bloc « colonne: valeur », sans les cases vides."""
    blocs = []
    for fiche in fiches.to_dict("records"):
        lignes = [
            f"{colonne}: {valeur}" for colonne, valeur in fiche.items() if pd.notna(valeur) and str(valeur).strip()
        ]
        blocs.append("\n".join(lignes))
    return "\n\n---\n\n".join(blocs) if blocs else "(aucune fiche)"


def consigne_systeme(fiches: pd.DataFrame) -> str:
    """Les consignes de `prompts/systeme.md`, suivies de toutes les fiches."""
    return f"{lire_prompt('systeme')}\n\n# Les fiches\n\n{fiches_en_texte(fiches)}"


def messages_gemini(question: str, historique: list[dict[str, str]]) -> list[dict]:
    """L'historique puis la question, au format attendu par Gemini."""
    messages = [
        {"role": ROLES_GEMINI.get(message["role"], "user"), "parts": [{"text": message["content"]}]}
        for message in historique
    ]
    messages.append({"role": "user", "parts": [{"text": question}]})
    return messages


def appeler_gemini(consigne: str, messages: list[dict], cle: str) -> str:
    """Le texte renvoyé par Gemini. Lève `requests.RequestException` si l'appel échoue."""
    reponse = requests.post(
        URL_GEMINI.format(modele=MODELE),
        headers={"x-goog-api-key": cle},  # la clé part dans un en-tête, jamais dans l'adresse
        json={"system_instruction": {"parts": [{"text": consigne}]}, "contents": messages},
        timeout=DELAI_MAX_S,
    )
    reponse.raise_for_status()
    candidats = reponse.json().get("candidates") or [{}]
    parties = candidats[0].get("content", {}).get("parts", [])
    return "".join(partie.get("text", "") for partie in parties).strip()


def message_erreur(erreur: requests.RequestException) -> str:
    """Une phrase simple pour l'utilisateur quand Gemini ne répond pas."""
    if isinstance(erreur, requests.Timeout):
        return "Gemini met trop de temps à répondre. Réessayez dans quelques secondes."
    code = getattr(erreur.response, "status_code", None)
    return MESSAGES_ERREUR.get(code, f"L'assistant n'a pas pu joindre Gemini (erreur {code or 'réseau'}).")


def repondre(question: str, historique: list[dict[str, str]], fiches: pd.DataFrame) -> str:
    """La réponse de l'assistant à `question`, fondée sur `fiches`.

    `historique` est la liste des messages précédents : {"role": "user" ou "assistant", "content": texte}.
    """
    cle = cle_api()
    if cle is None:
        return "L'assistant n'est pas encore branché : il manque `LLM_API_KEY` dans les Secrets."
    try:
        texte = appeler_gemini(consigne_systeme(fiches), messages_gemini(question, historique), cle)
    except requests.RequestException as erreur:
        return message_erreur(erreur)
    return texte or "Je ne sais pas : Gemini n'a renvoyé aucune réponse."
