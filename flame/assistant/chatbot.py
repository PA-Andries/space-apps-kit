"""L'assistant (RAG + outils) : retrouve les fiches utiles, puis les envoie à Gemini avec la question.

1. Recherche (`rag.py`) : les fiches dont le sens est le plus proche de la question.
2. Environnement (`environnement.py`) : l'habitat et les conditions choisis en page 1.
3. Génération : Gemini répond à partir des fiches, et peut appeler les outils de `outils.py`
   (investigations par habitat, comptage des tests dans des conditions données).

La clé se lit avec `cle_api()` et ne s'écrit jamais dans le code. Les messages affichés sont en anglais.
"""

from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from flame.assistant.environnement import decrire_environnement, scenario_courant
from flame.assistant.outils import DECLARATIONS, executer_outil
from flame.assistant.rag import NB_FICHES, fiches_proches
from flame.recherche import rechercher

DOSSIER_PROMPTS = Path(__file__).parent / "prompts"
MODELE = "gemini-3.5-flash"
URL_GEMINI = "https://generativelanguage.googleapis.com/v1beta/models/{modele}:generateContent"
DELAI_MAX_S = 60
NB_MAX_TOURS_OUTILS = 4  # au-delà, on arrête : Gemini tournerait en rond
# Colonnes des fiches qu'on n'envoie pas au LLM : les piliers sont abandonnés (décision de PA, 14 novembre).
COLONNES_IGNOREES = {"pilier"}
NB_MIN_SYNTHESE, NB_MAX_SYNTHESE = 2, 3
SYNTHESE_IMPOSSIBLE = "Pick two or three investigations to get a synthesis."
# Gemini appelle « model » ce que la page appelle « assistant ».
ROLES_GEMINI = {"user": "user", "assistant": "model"}
SANS_CLE = "The assistant is not connected yet: `LLM_API_KEY` is missing from the Secrets."
SANS_REPONSE = "I don't know: Gemini returned no answer."
MESSAGES_ERREUR = {
    429: "Gemini's free quota is used up for now. Please try again in a minute.",
    503: "Gemini is overloaded right now. Please try again in a few seconds.",
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
            f"{colonne}: {valeur}"
            for colonne, valeur in fiche.items()
            if colonne not in COLONNES_IGNOREES and pd.notna(valeur) and str(valeur).strip()
        ]
        blocs.append("\n".join(lignes))
    return "\n\n---\n\n".join(blocs) if blocs else "(aucune fiche)"


def catalogue(fiches: pd.DataFrame) -> str:
    """La liste courte de toutes les fiches : une ligne « - id : nom » par fiche."""
    return "\n".join(f"- {fiche['id']} : {fiche['nom']}" for fiche in fiches.to_dict("records"))


def texte_a_chercher(question: str, historique: list[dict[str, str]]) -> str:
    """La question, précédée de la question d'avant, pour comprendre une relance (« et celle sur les tissus ? »)."""
    precedentes = [message["content"] for message in historique if message["role"] == "user"]
    return f"{precedentes[-1]}\n{question}" if precedentes else question


def choisir_fiches(question: str, historique: list[dict[str, str]], fiches: pd.DataFrame, cle: str) -> pd.DataFrame:
    """Les fiches utiles à la question (étape « recherche » du RAG).

    Si Gemini ne peut pas calculer les embeddings, on se rabat sur la recherche par mots du rôle C,
    puis, si elle ne trouve rien, sur toutes les fiches.
    """
    texte = texte_a_chercher(question, historique)
    try:
        return fiches_proches(texte, fiches, cle)
    except requests.RequestException:
        trouvees = rechercher(texte, fiches)
        if trouvees.empty:
            return fiches
        return fiches[fiches["id"].isin(trouvees["id"].head(NB_FICHES))]


def consigne_systeme(fiches_utiles: pd.DataFrame, toutes_les_fiches: pd.DataFrame, environnement: str = "") -> str:
    """Les consignes, l'environnement de l'utilisateur, la liste de toutes les fiches, puis les fiches utiles."""
    bloc_environnement = environnement or "(non précisé : l'utilisateur n'a pas encore choisi d'environnement)"
    return (
        f"{lire_prompt('systeme')}\n\n"
        f"# L'environnement étudié par l'utilisateur\n\n{bloc_environnement}\n\n"
        f"# Toutes les investigations (id et nom seulement)\n\n{catalogue(toutes_les_fiches)}\n\n"
        f"# Les fiches détaillées utiles à cette question\n\n{fiches_en_texte(fiches_utiles)}"
    )


def messages_gemini(question: str, historique: list[dict[str, str]]) -> list[dict]:
    """L'historique puis la question, au format attendu par Gemini."""
    messages = [
        {"role": ROLES_GEMINI.get(message["role"], "user"), "parts": [{"text": message["content"]}]}
        for message in historique
    ]
    messages.append({"role": "user", "parts": [{"text": question}]})
    return messages


def envoyer(consigne: str, contenus: list[dict], cle: str, avec_outils: bool = True) -> dict:
    """Un aller-retour avec Gemini : le contenu de sa réponse (du texte, ou des demandes d'outils)."""
    corps = {"system_instruction": {"parts": [{"text": consigne}]}, "contents": contenus}
    if avec_outils:
        corps["tools"] = [{"functionDeclarations": DECLARATIONS}]
    reponse = requests.post(
        URL_GEMINI.format(modele=MODELE),
        headers={"x-goog-api-key": cle},  # la clé part dans un en-tête, jamais dans l'adresse
        json=corps,
        timeout=DELAI_MAX_S,
    )
    reponse.raise_for_status()
    candidats = reponse.json().get("candidates") or [{}]
    return candidats[0].get("content") or {}


def appeler_gemini(consigne: str, messages: list[dict], cle: str) -> str:
    """Le texte final de Gemini, après avoir exécuté les outils qu'il demande. Lève `requests.RequestException`."""
    contenus = list(messages)
    for _ in range(NB_MAX_TOURS_OUTILS + 1):
        parties = envoyer(consigne, contenus, cle).get("parts", [])
        appels = [partie["functionCall"] for partie in parties if "functionCall" in partie]
        if not appels:
            return "".join(partie.get("text", "") for partie in parties).strip()
        # On renvoie à Gemini sa propre demande telle quelle, puis le résultat de chaque outil.
        contenus.append({"role": "model", "parts": parties})
        resultats = [
            {"functionResponse": {"name": appel["name"], "response": executer_outil(appel["name"], appel.get("args"))}}
            for appel in appels
        ]
        contenus.append({"role": "user", "parts": resultats})
    return ""


def message_erreur(erreur: requests.RequestException) -> str:
    """Une phrase simple pour l'utilisateur quand Gemini ne répond pas."""
    if isinstance(erreur, requests.Timeout):
        return "Gemini is taking too long to answer. Please try again in a few seconds."
    code = getattr(erreur.response, "status_code", None)
    return MESSAGES_ERREUR.get(code, f"The assistant could not reach Gemini (error {code or 'network'}).")


def repondre(question: str, historique: list[dict[str, str]], fiches: pd.DataFrame) -> str:
    """La réponse de l'assistant à `question`, fondée sur `fiches` et sur l'environnement choisi en page 1.

    `historique` est la liste des messages précédents : {"role": "user" ou "assistant", "content": texte}.
    """
    cle = cle_api()
    if cle is None:
        return SANS_CLE
    try:
        fiches_utiles = choisir_fiches(question, historique, fiches, cle)
        consigne = consigne_systeme(fiches_utiles, fiches, decrire_environnement(scenario_courant()))
        texte = appeler_gemini(consigne, messages_gemini(question, historique), cle)
    except requests.RequestException as erreur:
        return message_erreur(erreur)
    return texte or SANS_REPONSE


def synthetiser(fiches: pd.DataFrame, ids: list[str]) -> str:
    """Une synthèse en anglais de deux ou trois investigations, écrite par Gemini à partir de leurs seules fiches.

    Cinq rubriques : comportement du feu, inflammabilité, dangers, prévention, détection.
    `ids` sont les `id` des fiches à comparer ; `fiches` vient de `charger_fiches()`.
    """
    choisies = fiches[fiches["id"].isin(ids)]
    if not NB_MIN_SYNTHESE <= len(choisies) <= NB_MAX_SYNTHESE:
        return SYNTHESE_IMPOSSIBLE
    cle = cle_api()
    if cle is None:
        return SANS_CLE
    consigne = f"{lire_prompt('synthese')}\n\n# Les fiches à comparer\n\n{fiches_en_texte(choisies)}"
    demande = [{"role": "user", "parts": [{"text": "Write the synthesis."}]}]
    try:
        parties = envoyer(consigne, demande, cle, avec_outils=False).get("parts", [])
    except requests.RequestException as erreur:
        return message_erreur(erreur)
    return "".join(partie.get("text", "") for partie in parties).strip() or SANS_REPONSE
