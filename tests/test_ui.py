"""Tests de l'interface. Propriétaire : rôle F."""

import json
import re

from flame.ui.scene import DOSSIER_THREE, page_scene, reglages_scene


def test_la_scene_attend_ses_reglages():
    assert "__REGLAGES__" in (DOSSIER_THREE / "flamme.html").read_text(encoding="utf-8")


def test_les_reglages_sont_bornes():
    assert reglages_scene(-1, 150) == {"gravite": 0.0, "oxygene": 100.0}
    assert reglages_scene(0.5, 30) == {"gravite": 0.5, "oxygene": 30.0}


def test_la_page_contient_les_reglages():
    page = page_scene(1, 21)
    assert "__REGLAGES__" not in page
    assert json.dumps({"gravite": 1.0, "oxygene": 21.0}) in page


def test_three_js_a_une_version_precise():
    page = (DOSSIER_THREE / "flamme.html").read_text(encoding="utf-8")
    assert re.search(r"three@\d+\.\d+\.\d+/", page)
