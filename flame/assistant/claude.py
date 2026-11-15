"""Flamy avec Claude : les appels à l'API d'Anthropic, avec la bibliothèque officielle `anthropic`.

Claude reçoit la même consigne, les mêmes fiches et les mêmes outils que Gemini (`outils.py`).
La clé se lit dans les Secrets sous le nom `ANTHROPIC_API_KEY` ; elle ne s'écrit jamais dans le code.
Le modèle peut se changer sans toucher au code, avec la ligne `CLAUDE_MODEL` des Secrets.
"""

import json
import os

import anthropic
import streamlit as st

from flame.assistant.outils import DECLARATIONS, executer_outil

MODELE = "claude-opus-5-5"
NB_MAX_TOKENS = 16000  # plafond de la réponse (réflexion comprise), pas une longueur visée
DELAI_MAX_S = 90
NB_MAX_TOURS_OUTILS = 4  # au-delà, on arrête : le modèle tournerait en rond
# Si le modèle refuse une question, l'API la confie d'elle-même à un autre modèle (option en bêta).
BETA_REPLI = "server-side-fallback-2026-07-01"
MODELES_AVEC_REPLI = {"claude-opus-5-5", "claude-sonnet-5-5"}
SECRET_A_REMPLIR = "à-remplacer"  # la valeur du modèle `.streamlit/secrets.toml.example`
REFUS = "I can't answer this question. Try asking it another way."
# Les mêmes outils que pour Gemini, au format attendu par Claude.
OUTILS_CLAUDE = [
    {"name": outil["name"], "description": outil["description"], "input_schema": outil["parameters"]}
    for outil in DECLARATIONS
]


def lire_secret(nom: str) -> str | None:
    """La valeur `nom` des Secrets de Streamlit, sinon de l'environnement ; None si elle est vide ou absente."""
    try:
        valeur = st.secrets.get(nom)
    except FileNotFoundError:  # aucun fichier .streamlit/secrets.toml sur cet ordinateur
        valeur = None
    valeur = str(valeur or os.environ.get(nom) or "").strip()
    return None if valeur in ("", SECRET_A_REMPLIR) else valeur


def cle_claude() -> str | None:
    """La clé de l'API d'Anthropic (`ANTHROPIC_API_KEY`), ou None si elle manque."""
    return lire_secret("ANTHROPIC_API_KEY")


def modele_claude() -> str:
    """Le modèle utilisé : `CLAUDE_MODEL` des Secrets s'il est donné, sinon `MODELE`."""
    return lire_secret("CLAUDE_MODEL") or MODELE


def messages_claude(question: str, historique: list[dict[str, str]]) -> list[dict]:
    """L'historique puis la question, au format attendu par Claude (les messages vides sont retirés)."""
    messages = [
        {"role": "assistant" if message["role"] == "assistant" else "user", "content": message["content"]}
        for message in historique
        if str(message.get("content", "")).strip()
    ]
    messages.append({"role": "user", "content": question})
    return messages


def envoyer(client: anthropic.Anthropic, consigne: str, messages: list[dict], avec_outils: bool = True):
    """Un aller-retour avec Claude : sa réponse (du texte, ou des demandes d'outils)."""
    modele = modele_claude()
    options = {
        "model": modele,
        "max_tokens": NB_MAX_TOKENS,
        "system": consigne,
        "messages": messages,
        # La consigne et les fiches sont gardées en cache : les allers-retours suivants coûtent moins cher.
        "cache_control": {"type": "ephemeral"},
    }
    if avec_outils:
        options["tools"] = OUTILS_CLAUDE
    if modele not in MODELES_AVEC_REPLI:
        return client.messages.create(**options)
    try:
        return client.beta.messages.create(**options, betas=[BETA_REPLI], fallbacks="default")
    except anthropic.BadRequestError:
        # L'option de repli est en bêta : si l'API la refuse, on pose la même question sans elle.
        return client.messages.create(**options)


def appeler_claude(consigne: str, messages: list[dict], cle: str, avec_outils: bool = True) -> str:
    """Le texte final de Claude, après avoir exécuté les outils qu'il demande. Lève `anthropic.APIError`."""
    client = anthropic.Anthropic(api_key=cle, timeout=DELAI_MAX_S, max_retries=1)
    echanges = list(messages)
    for _ in range(NB_MAX_TOURS_OUTILS + 1):
        reponse = envoyer(client, consigne, echanges, avec_outils)
        if reponse.stop_reason == "refusal":
            return REFUS
        appels = [bloc for bloc in reponse.content if bloc.type == "tool_use"]
        if not appels:
            return "".join(bloc.text for bloc in reponse.content if bloc.type == "text").strip()
        # On renvoie à Claude sa propre demande telle quelle, puis le résultat de chaque outil.
        echanges.append({"role": "assistant", "content": reponse.content})
        resultats = [
            {
                "type": "tool_result",
                "tool_use_id": appel.id,
                "content": json.dumps(executer_outil(appel.name, appel.input), ensure_ascii=False),
            }
            for appel in appels
        ]
        echanges.append({"role": "user", "content": resultats})
    return ""


def message_erreur_claude(erreur: anthropic.APIError) -> str:
    """Une phrase simple pour l'utilisateur quand Claude ne répond pas."""
    if isinstance(erreur, anthropic.APITimeoutError):
        return "Claude is taking too long to answer. Please try again in a few seconds."
    if isinstance(erreur, anthropic.APIConnectionError):
        return "The assistant could not reach Claude (network error). Please try again."
    if isinstance(erreur, anthropic.AuthenticationError):
        return "Claude refused the API key: check `ANTHROPIC_API_KEY` in the Secrets."
    if isinstance(erreur, anthropic.PermissionDeniedError):
        return "This Anthropic API key is not allowed to use this model: check the key and `CLAUDE_MODEL`."
    if isinstance(erreur, anthropic.NotFoundError):
        return f"Claude does not know the model `{modele_claude()}`: check `CLAUDE_MODEL` in the Secrets."
    if isinstance(erreur, anthropic.RateLimitError):
        return "Claude's rate limit is reached for now. Please try again in a minute."
    if "credit balance" in str(erreur).lower():
        return "The Anthropic account has no API credit left: add credit on console.anthropic.com."
    code = getattr(erreur, "status_code", None)
    if code is not None and code >= 500:
        return "Claude is overloaded right now. Please try again in a few seconds."
    return f"The assistant could not get an answer from Claude (error {code or 'unknown'})."
