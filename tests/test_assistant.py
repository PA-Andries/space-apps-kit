"""Tests de l'assistant. Propriétaire : rôle E."""

from flame.assistant import chatbot
from flame.commun import charger_fiches


def test_sans_cle_l_assistant_le_dit(monkeypatch):
    monkeypatch.setattr(chatbot, "cle_api", lambda: None)
    reponse = chatbot.repondre("Qu'est-ce que BASS ?", [], charger_fiches())
    assert "LLM_API_KEY" in reponse


def test_la_consigne_existe():
    assert "je ne sais pas" in chatbot.lire_prompt("systeme")
