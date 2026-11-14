"""Tests du comparateur. Propriétaire : rôle D."""

from flame.commun import charger_fiches
from flame.comparateur import CRITERES, comparer


def test_une_colonne_par_investigation():
    tableau = comparer(charger_fiches(), ["EXEMPLE-A", "EXEMPLE-C"])
    assert list(tableau.columns) == ["EXEMPLE-A", "EXEMPLE-C"]
    assert list(tableau.index) == CRITERES
