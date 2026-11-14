"""Interface tests. Owner: role F."""

import json
import re
from pathlib import Path

from streamlit.testing.v1 import AppTest

from flame.ui.scene import THREE_DIR, flame_page, flame_settings, places_page

APP = str(Path(__file__).parents[1] / "app.py")


def test_scenes_wait_for_their_settings():
    for scene in THREE_DIR.glob("*.html"):
        assert "__SETTINGS__" in scene.read_text(encoding="utf-8"), scene.name


def test_settings_are_clamped():
    assert flame_settings(-1, 150) == {"gravity": 0.0, "oxygen": 100.0}
    assert flame_settings(0.5, 30) == {"gravity": 0.5, "oxygen": 30.0}


def test_flame_page_contains_its_settings():
    page = flame_page(1, 21)
    assert "__SETTINGS__" not in page
    assert json.dumps({"gravity": 1.0, "oxygen": 21.0}) in page


def test_three_js_has_an_exact_version():
    for scene in THREE_DIR.glob("*.html"):
        assert re.search(r"three@\d+\.\d+\.\d+/", scene.read_text(encoding="utf-8")), scene.name


ZONE = {"cx": 0.5, "cy": 0.5, "w": 0.5, "h": 0.5}


def test_places_scene_highlights_the_chosen_object():
    assert '"chosen": 1' in places_page(["moon_whole", "rover_moon"], [ZONE, ZONE], "rover_moon")
    assert '"chosen": -1' in places_page(["moon_whole", "rover_moon"], [ZONE, ZONE], None)


def test_places_scene_gets_its_zones_and_zoom():
    page = places_page(["mars_whole"], [ZONE], None, zoom_from=2)
    assert '"zones": [{"cx": 0.5, "cy": 0.5, "w": 0.5, "h": 0.5}]' in page
    assert '"zoomFrom": 2' in page


def test_every_object_has_a_drawing():
    from flame.ui.components import BODY_OBJECTS, PLACE_VIEW

    scene = (THREE_DIR / "places.html").read_text(encoding="utf-8")
    for name in [*BODY_OBJECTS.values(), *(view[0] for view in PLACE_VIEW.values())]:
        assert re.search(rf"\b{name}: \[", scene), name


def test_every_offered_place_has_a_view():
    from flame.ui.components import PLACE_VIEW
    from flame.ui.places import PLACES_BY_BODY

    for places in PLACES_BY_BODY.values():
        for place in places:
            zone = PLACE_VIEW[place][1]
            assert 0 <= zone["cx"] <= 1
            assert zone["cy"] - zone["h"] / 2 >= 0 and zone["cy"] + zone["h"] / 2 <= 1


def test_label_translates_contract_values():
    from flame.commun import HABITATS, PILIERS
    from flame.ui import label
    from flame.ui.top_bar import PROFILES_OFFERED

    for value in [*HABITATS, *PILIERS, *PROFILES_OFFERED]:
        assert label(value) != value
    assert label("Prévenir;Éteindre") == "Prevent, Extinguish"
    assert label("missing value") == "missing value"


def test_every_place_has_its_conditions():
    from flame.ui import EARTH, place_conditions
    from flame.ui.places import PLACES_BY_BODY

    for body, places in PLACES_BY_BODY.items():
        for place in places:
            assert 0 <= place_conditions(place, body)["gravity"] <= 1
    assert place_conditions(EARTH, "Terre") == {"oxygen_pct": 21, "pressure_kpa": 101, "gravity": 1.0}
    assert place_conditions("Station", "Terre")["gravity"] == 0.0
    assert place_conditions("Rover pressurisé", "Lune")["gravity"] == 0.17
    assert place_conditions("Base martienne", "Mars")["gravity"] == 0.38


def test_only_figures_from_the_statement_are_shown():
    from flame.ui import place_conditions

    assert place_conditions("Base lunaire", "Lune")["oxygen_pct"] == 30
    assert place_conditions("Rover pressurisé", "Lune")["pressure_kpa"] == 70
    for place, body in [("Base martienne", "Mars"), ("Station", "Terre"), ("Vaisseau", "Terre")]:
        assert place_conditions(place, body)["oxygen_pct"] is None
        assert place_conditions(place, body)["pressure_kpa"] is None


def test_the_rover_is_only_on_the_moon():
    from flame.ui.places import PLACES_BY_BODY, body_of

    assert PLACES_BY_BODY["Mars"] == ["Base martienne"]
    assert body_of("Rover pressurisé") == "Lune"
    assert body_of("Station") == "Terre"


def _pick_moon_rover_then_detect():
    from flame.ui.places import choose_body, choose_pillar, choose_place

    choose_body("Lune")
    choose_place("Rover pressurisé")
    choose_pillar("Détecter")


def _pick_station_then_earth():
    from flame.ui.places import choose_body, choose_place

    choose_body("Terre")
    choose_place("Station")
    choose_place("Terre")


def _pick_moon_then_mars():
    from flame.ui.places import choose_body, choose_place

    choose_body("Lune")
    choose_place("Base lunaire")
    choose_body("Mars")


# After a click, AppTest reruns only the page, not `app.py`: these tests check the keys
# the buttons write, which the top bar reads on the next run.
def test_a_chosen_habitat_becomes_the_scenario_habitat():
    site = AppTest.from_function(_pick_moon_rover_then_detect).run()
    assert site.session_state["ui_body"] == "Lune"
    assert site.session_state["ui_habitat"] == "Rover pressurisé"
    assert site.session_state["ui_pillar"] == "Détecter"


def test_earth_does_not_change_the_habitat():
    site = AppTest.from_function(_pick_station_then_earth).run()
    assert site.session_state["ui_place"] == "Terre"
    assert site.session_state["ui_habitat"] == "Station"


def test_a_new_body_resets_the_place():
    site = AppTest.from_function(_pick_moon_then_mars).run()
    assert site.session_state["ui_body"] == "Mars"
    assert "ui_place" not in site.session_state
    assert site.session_state["ui_zoom_pending"] is True


def _zoom_plays_once():
    import streamlit as st

    from flame.ui.places import choose_body, take_zoom

    choose_body("Lune")
    st.session_state["first"] = take_zoom()
    st.session_state["second"] = take_zoom()


def test_the_zoom_plays_only_once():
    site = AppTest.from_function(_zoom_plays_once).run()
    assert site.session_state["first"] is True
    assert site.session_state["second"] is False


def test_home_page_goes_step_by_step():
    site = AppTest.from_file(APP, default_timeout=30).run()
    assert [b.key for b in site.button if not b.key.startswith("ui_body_")] == []
    site.button(key="ui_body_Mars").click().run()
    assert [b.key for b in site.button if b.key.startswith("ui_body_")] == []
    assert [b.key for b in site.button if b.key.startswith("ui_place_")] == ["ui_place_Base martienne"]
    site.button(key="ui_place_Base martienne").click().run()
    assert len([b for b in site.button if b.key.startswith("ui_pillar_")]) == 3
    assert len(site.caption) == 3  # one hint per pillar, no result yet
    site.button(key="ui_pillar_Éteindre").click().run()
    assert not site.exception
    assert len(site.caption) == 4  # the flame caption of the result


def test_back_button_returns_to_the_bodies():
    site = AppTest.from_file(APP, default_timeout=30).run()
    site.button(key="ui_body_Lune").click().run()
    site.button(key="ui_back").click().run()
    assert not site.exception
    assert len([b for b in site.button if b.key.startswith("ui_body_")]) == 3


def test_earth_button_shows_the_reference():
    site = AppTest.from_file(APP, default_timeout=30).run()
    site.button(key="ui_body_Terre").click().run()
    site.button(key="ui_place_Terre").click().run()
    site.button(key="ui_pillar_Prévenir").click().run()
    assert not site.exception
    assert site.session_state["ui_place"] == "Terre"
    assert len(site.info) == 1


def test_student_is_not_offered():
    site = AppTest.from_file(APP, default_timeout=30).run()
    assert "Étudiant" not in site.selectbox(key="ui_profile").options
    assert site.session_state["profil"] == "Chercheur"


def test_french_contract_names_still_work():
    from flame.ui import afficher_cadre, carte_fiche, flame_scene, investigation_card, scene_3d, show_top_bar

    assert afficher_cadre is show_top_bar
    assert carte_fiche is investigation_card
    assert scene_3d is flame_scene


def _two_tiles():
    from flame.ui.home import stat_tiles

    stat_tiles([(None, "Oxygen"), ("0.38 g", "Gravity")], "note")


def test_stat_tiles_show_unknown_instead_of_a_guess():
    site = AppTest.from_function(_two_tiles).run()
    assert not site.exception
