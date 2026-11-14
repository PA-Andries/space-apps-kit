"""Tests de l'assistant. Propriétaire : rôle E. Aucun test n'appelle le vrai Gemini."""

import pandas as pd
import requests

from flame.assistant import chatbot, rag
from flame.commun import charger_fiches


class FausseReponse:
    """Imite une réponse HTTP de Gemini : `contenu` est le JSON renvoyé."""

    def __init__(self, contenu: dict | None = None, code: int = 200):
        self.status_code = code
        self.contenu = contenu or {"candidates": [{"content": {"parts": [{"text": "Réponse (EXEMPLE-A)."}]}}]}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)

    def json(self):
        return self.contenu


def faux_embeddings(appels: list[str]):
    """Un faux service d'embeddings : un texte qui parle de fumée vaut [1, 0], les autres [0, 1]."""

    def post(url, headers, json, timeout):
        appels.append(json["requests"][0]["taskType"])
        textes = [demande["content"]["parts"][0]["text"].lower() for demande in json["requests"]]
        vecteurs = [[1.0, 0.0] if "fum" in texte else [0.0, 1.0] for texte in textes]
        return FausseReponse({"embeddings": [{"values": vecteur} for vecteur in vecteurs]})

    return post


FICHES_TEST = pd.DataFrame(
    {
        "id": ["A", "B", "C"],
        "nom": ["Fumée des câbles", "Gouttes de carburant", "Tissu en feu"],
        "pilier": ["Détecter", "Éteindre", "Prévenir"],
        "resume": ["Mesure de la fumée.", "Extinction de gouttes.", "Propagation sur un tissu."],
    }
)


def test_sans_cle_l_assistant_le_dit(monkeypatch):
    monkeypatch.setattr(chatbot, "cle_api", lambda: None)
    reponse = chatbot.repondre("Qu'est-ce que BASS ?", [], charger_fiches())
    assert "LLM_API_KEY" in reponse


def test_la_consigne_existe():
    assert "je ne sais pas" in chatbot.lire_prompt("systeme")


def test_les_fiches_en_texte_gardent_les_id():
    fiches = charger_fiches()
    texte = chatbot.fiches_en_texte(fiches)
    assert all(f"id: {identifiant}" in texte for identifiant in fiches["id"])
    assert "nan" not in texte


def test_l_historique_est_traduit_pour_gemini():
    historique = [{"role": "user", "content": "Bonjour"}, {"role": "assistant", "content": "Salut"}]
    messages = chatbot.messages_gemini("Et BASS ?", historique)
    assert [message["role"] for message in messages] == ["user", "model", "user"]
    assert messages[-1]["parts"][0]["text"] == "Et BASS ?"


def test_la_similarite_cosinus():
    assert rag.similarite([1.0, 0.0], [2.0, 0.0]) == 1.0
    assert rag.similarite([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_la_recherche_garde_les_fiches_les_plus_proches(monkeypatch):
    monkeypatch.setattr(rag.requests, "post", faux_embeddings([]))
    proches = rag.fiches_proches("Qui a étudié la fumée ?", FICHES_TEST, "fausse-cle", nombre=1)
    assert list(proches["id"]) == ["A"]


def test_les_fiches_ne_sont_transformees_qu_une_fois(monkeypatch):
    appels = []
    monkeypatch.setattr(rag.requests, "post", faux_embeddings(appels))
    rag.fiches_proches("la fumée ?", FICHES_TEST, "fausse-cle", nombre=1)
    rag.fiches_proches("les gouttes ?", FICHES_TEST, "fausse-cle", nombre=1)
    assert appels.count("RETRIEVAL_DOCUMENT") == 1  # les fiches : une seule fois, puis le cache
    assert appels.count("RETRIEVAL_QUERY") == 2  # une question : un petit appel à chaque fois


def test_si_les_embeddings_echouent_on_cherche_par_mots(monkeypatch):
    def en_panne(*args, **kwargs):
        raise requests.ConnectionError

    monkeypatch.setattr(chatbot, "fiches_proches", en_panne)
    choisies = chatbot.choisir_fiches("tissu", [], FICHES_TEST, "fausse-cle")
    assert list(choisies["id"]) == ["C"]


def test_la_question_precedente_aide_la_recherche():
    historique = [{"role": "user", "content": "Parle-moi de la fumée"}, {"role": "assistant", "content": "…"}]
    assert chatbot.texte_a_chercher("et ensuite ?", historique) == "Parle-moi de la fumée\net ensuite ?"
    assert chatbot.texte_a_chercher("bonjour", []) == "bonjour"


def test_la_consigne_n_envoie_que_les_fiches_utiles():
    consigne = chatbot.consigne_systeme(FICHES_TEST.head(1), FICHES_TEST)
    assert all(f"- {identifiant} :" in consigne for identifiant in FICHES_TEST["id"])  # la liste courte
    assert "Mesure de la fumée." in consigne  # le détail de la fiche utile
    assert "Extinction de gouttes." not in consigne  # pas le détail des autres


def test_repondre_envoie_les_fiches_a_gemini(monkeypatch):
    envoye = {}

    def faux_post(url, headers, json, timeout):
        envoye.update(url=url, headers=headers, json=json)
        return FausseReponse()

    monkeypatch.setattr(chatbot, "cle_api", lambda: "fausse-cle")
    monkeypatch.setattr(chatbot.requests, "post", faux_post)
    reponse = chatbot.repondre("Qu'est-ce que BASS ?", [], charger_fiches())
    assert reponse == "Réponse (EXEMPLE-A)."
    assert envoye["headers"]["x-goog-api-key"] == "fausse-cle"
    assert "fausse-cle" not in envoye["url"]
    assert "EXEMPLE-A" in envoye["json"]["system_instruction"]["parts"][0]["text"]


def test_gemini_surcharge_donne_un_message_clair(monkeypatch):
    monkeypatch.setattr(chatbot, "cle_api", lambda: "fausse-cle")
    monkeypatch.setattr(chatbot.requests, "post", lambda *args, **kwargs: FausseReponse(code=503))
    reponse = chatbot.repondre("Qu'est-ce que BASS ?", [], charger_fiches())
    assert "surchargé" in reponse


def test_gemini_trop_lent_donne_un_message_clair(monkeypatch):
    def trop_lent(*args, **kwargs):
        raise requests.Timeout

    monkeypatch.setattr(chatbot, "cle_api", lambda: "fausse-cle")
    monkeypatch.setattr(chatbot.requests, "post", trop_lent)
    assert "trop de temps" in chatbot.repondre("Qu'est-ce que BASS ?", [], charger_fiches())
