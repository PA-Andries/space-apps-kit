"""Tests de l'interface. Propriétaire : rôle F."""

import json
import re
from pathlib import Path

from streamlit.testing.v1 import AppTest

from flame.ui.scene import DOSSIER_THREE, page_scene, reglages_scene

APP = str(Path(__file__).parents[1] / "app.py")


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


def test_libelle_traduit_les_valeurs_du_contrat():
    from flame.commun import HABITATS, PILIERS, PROFILS
    from flame.ui import libelle

    for valeur in [*HABITATS, *PILIERS, *PROFILS]:
        assert libelle(valeur) != valeur
    assert libelle("Prévenir;Éteindre") == "Prevent, Extinguish"
    assert libelle("valeur absente") == "valeur absente"


def test_chaque_lieu_a_ses_conditions():
    from flame.ui import TERRE, conditions_lieu
    from flame.ui.lieux import LIEUX

    for lieu in LIEUX:
        conditions = conditions_lieu(lieu)
        assert 0 <= conditions["gravite"] <= 1
    assert conditions_lieu(TERRE) == {"oxygene_pct": 21, "pression_kpa": 101, "gravite": 1.0, "source_enonce": True}


def _choisir_mars_puis_detecter():
    from flame.ui.lieux import choisir_lieu, choisir_pilier

    choisir_lieu("Base martienne")
    choisir_pilier("Détecter")


def _choisir_station_puis_terre():
    from flame.ui.lieux import choisir_lieu

    choisir_lieu("Station")
    choisir_lieu("Terre")


def test_un_habitat_choisi_devient_celui_du_scenario():
    site = AppTest.from_function(_choisir_mars_puis_detecter).run()
    assert site.session_state["ui_lieu"] == "Base martienne"
    assert site.session_state["ui_habitat"] == "Base martienne"
    assert site.session_state["ui_pilier"] == "Détecter"


def test_la_terre_ne_change_pas_l_habitat():
    site = AppTest.from_function(_choisir_station_puis_terre).run()
    assert site.session_state["ui_lieu"] == "Terre"
    assert site.session_state["ui_habitat"] == "Station"


def test_le_bouton_terre_affiche_la_reference():
    site = AppTest.from_file(APP, default_timeout=30).run()
    site.button(key="ui_lieu_Terre").click().run()
    assert not site.exception
    assert site.session_state["ui_lieu"] == "Terre"
    assert len(site.info) == 1
