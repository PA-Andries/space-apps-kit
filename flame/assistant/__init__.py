"""Rôle E (Assistant) : le chatbot d'aide, qui répond à partir des fiches, et la page Equipment and Earth."""

from flame.assistant.chatbot import repondre, synthetiser
from flame.assistant.equipements import (
    EQUIPEMENTS,
    fiches_pour,
    instruments_de,
    liens_terre,
    retombees_sur_terre,
)

__all__ = [
    "EQUIPEMENTS",
    "fiches_pour",
    "instruments_de",
    "liens_terre",
    "repondre",
    "retombees_sur_terre",
    "synthetiser",
]
