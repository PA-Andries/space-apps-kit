"""Tests de l'assistant. Propriétaire : rôle E. Aucun test n'appelle le vrai Gemini."""

import requests

from flame.assistant import chatbot
from flame.commun import charger_fiches


class FausseReponse:
    """Imite la réponse HTTP de Gemini."""

    def __init__(self, code: int = 200, texte: str = "Réponse (EXEMPLE-A)."):
        self.status_code = code
        self.texte = texte

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)

    def json(self):
        return {"candidates": [{"content": {"parts": [{"text": self.texte}]}}]}


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
