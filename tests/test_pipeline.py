"""Tests du pipeline de données. Propriétaire : rôle B. Aucun test n'appelle Internet."""

from flame.commun import COLONNES_PUBLICATIONS
from flame.pipeline.ntrs import _vers_ligne


def test_un_rapport_ntrs_devient_une_ligne():
    rapport = {
        "id": 123,
        "title": "Titre",
        "abstract": "Résumé",
        "publications": [{"publicationDate": "2015-10-20T00:00:00"}],
        "authorAffiliations": [{"meta": {"author": {"name": "Nom, P."}}}],
    }
    ligne = _vers_ligne(rapport)
    assert list(ligne) == COLONNES_PUBLICATIONS
    assert ligne["annee"] == "2015"
    assert ligne["url"] == "https://ntrs.nasa.gov/citations/123"
