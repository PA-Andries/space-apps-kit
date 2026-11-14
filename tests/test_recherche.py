"""Tests du moteur de recherche. Propriétaire : rôle C."""

from flame.commun import charger_fiches
from flame.recherche import rechercher


def test_question_vide_renvoie_tout():
    fiches = charger_fiches()
    assert len(rechercher("", fiches)) == len(fiches)


def test_un_mot_filtre_les_fiches():
    resultats = rechercher("tissu", charger_fiches())
    assert list(resultats["id"]) == ["EXEMPLE-A"]
