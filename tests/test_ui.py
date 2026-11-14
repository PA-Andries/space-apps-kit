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


def test_places_scene_does_not_change_with_the_choice():
    # The scene reads the chosen button in the page: its HTML must not depend on the choice (no reload).
    page = places_page(["moon_whole", "rover_moon"], [ZONE, ZONE], "ui_pick_ui_place")
    assert '"pickKey": "ui_pick_ui_place"' in page
    assert '"chosen"' not in page


def test_places_scene_gets_its_zones_and_zoom():
    page = places_page(["mars_whole"], [ZONE], "ui_pick_ui_place", zoom_from=2)
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
    assert label("solide (modèle)") == "solid (model)"


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


def test_planet_maps_are_sent_only_when_needed():
    from flame.ui.scene import scene_assets

    assert set(scene_assets(["moon", "mars"])) == {"moon", "mars"}
    assert scene_assets(["spacecraft"]) == {}
    assert scene_assets(["earth_whole"])["earth"].startswith("data:image/jpeg;base64,")


def test_dashboard_shows_everything_at_once():
    site = AppTest.from_file(APP, default_timeout=30).run()
    assert not site.exception
    assert len(site.dataframe) >= 1  # the ranking is there from the start
    site.button(key="ui_body_Mars").click().run()
    assert [b.key for b in site.button if b.key.startswith("ui_body_")] == []
    assert [b.key for b in site.button if b.key.startswith("ui_place_")] == ["ui_place_Base martienne"]
    site.button(key="ui_place_Base martienne").click().run()
    assert site.session_state["ui_habitat"] == "Base martienne"  # app.py turns it into the scenario
    assert not site.exception


def test_crew_environment_sets_parameters_that_refine_the_list():
    site = AppTest.from_file(APP, default_timeout=30).run()
    site.button(key="ui_body_Lune").click().run()
    site.button(key="ui_place_Rover pressurisé").click().run()
    assert not site.exception
    # The statement gives the rover 30 % oxygen and 70 kPa: the inputs are filled and the list narrows.
    assert site.number_input(key="ui_oxygen_Rover pressurisé").value == 30
    assert site.number_input(key="ui_pressure_Rover pressurisé").value == 70
    narrowed = len(site.dataframe[0].value)
    # The statement gives no atmosphere for the station: no figure, so nothing is filtered out.
    site.button(key="ui_back").click().run()
    site.button(key="ui_body_Terre").click().run()
    site.button(key="ui_place_Station").click().run()
    assert site.number_input(key="ui_oxygen_Station").value is None
    assert narrowed < len(site.dataframe[0].value)  # sample data in tests: the rover list may be empty


def _pillar_switch_emptied():
    import streamlit as st

    from flame.ui.top_bar import show_top_bar

    st.session_state["ui_pillar"] = "Éteindre"
    show_top_bar()
    st.session_state["first"] = st.session_state["pilier"]
    st.session_state["ui_pillar"] = None  # a second click on the switch empties it
    show_top_bar()


def test_pillar_switch_sets_the_scenario_and_never_empties_it():
    site = AppTest.from_function(_pillar_switch_emptied).run()
    assert site.session_state["first"] == "Éteindre"
    assert site.session_state["pilier"] == "Éteindre"


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
    assert not site.exception
    assert site.session_state["ui_place"] == "Terre"
    assert any("Earth is the reference" in caption.value for caption in site.caption)


def test_no_scenario_bar_and_student_is_not_offered():
    from flame.ui.top_bar import PROFILES_OFFERED

    site = AppTest.from_file(APP, default_timeout=30).run()
    assert len(site.selectbox) == 0  # the scenario is set by the home page clicks only
    assert "Étudiant" not in PROFILES_OFFERED
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
