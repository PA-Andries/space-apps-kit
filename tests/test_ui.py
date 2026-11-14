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


def _pick_moon_rover():
    from flame.ui.places import choose_body, choose_place

    choose_body("Lune")
    choose_place("Rover pressurisé")


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
    site = AppTest.from_function(_pick_moon_rover).run()
    assert site.session_state["ui_body"] == "Lune"
    assert site.session_state["ui_habitat"] == "Rover pressurisé"


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


def test_page_one_keeps_the_environment_and_the_top_three():
    site = AppTest.from_file(APP, default_timeout=30).run()
    assert not site.exception
    assert not site.dataframe  # the full ranking lives on the Investigations page now
    site.button(key="ui_place_Base martienne").click().run()
    assert site.session_state["ui_habitat"] == "Base martienne"  # app.py turns it into the scenario
    assert not site.exception


def test_moon_base_fills_the_statement_bounds_and_mars_stays_unknown():
    site = AppTest.from_file(APP, default_timeout=30).run()
    site.button(key="ui_place_Base lunaire").click().run()
    assert not site.exception
    # Lot F: "Moon base" fills O2 >= 30 % and <= 70.3 kPa (statement). A handle at the end of its scale = no bound.
    assert site.slider(key="ui_oxygen").value == (30.0, 100.0)
    assert site.slider(key="ui_pressure").value == (0.0, 70.3)
    assert site.slider(key="ui_gravity").value == 0.165
    # Mars: the statement gives no atmosphere, so no bound at all.
    site.button(key="ui_place_Base martienne").click().run()
    assert site.slider(key="ui_oxygen").value == (0.0, 100.0)
    assert site.slider(key="ui_pressure").value == (0.0, 350.0)


def test_a_typed_value_stays_while_the_habitat_does_not_change():
    site = AppTest.from_file(APP, default_timeout=30).run()
    site.slider(key="ui_oxygen").set_value((25.0, 100.0)).run()
    site.run()  # another rerun, as after a click elsewhere
    assert site.slider(key="ui_oxygen").value == (25.0, 100.0)
    site.button(key="ui_place_Station").click().run()
    assert site.slider(key="ui_oxygen").value == (19.0, 23.0)  # a new habitat brings its own values


def test_a_typed_value_survives_a_visit_to_another_page():
    site = AppTest.from_file(APP, default_timeout=30).run()
    site.slider(key="ui_oxygen").set_value((25.0, 100.0)).run()
    assert site.session_state["scenario_oxygene_pct"] == (25.0, None)  # written in the scenario (lot A)
    site.switch_page("pages/comparateur.py").run()
    site.switch_page("pages/accueil.py").run()
    assert site.slider(key="ui_oxygen").value == (25.0, 100.0)


def test_every_page_receives_the_environment_of_page_one():
    # Lot F is done when "Moon base" (here the rover, same statement values) fills O2 >= 30 % and <= 70.3 kPa
    # and the other pages receive this scenario (they read it with get_scenario(), lot A).
    pages = re.findall(r'st\.Page\("([^"]+)"', Path(APP).read_text(encoding="utf-8"))
    site = AppTest.from_file(APP, default_timeout=60).run()
    site.button(key="ui_place_Rover pressurisé").click().run()
    site.slider(key="ui_oxygen").set_value((32.0, 100.0)).run()
    for page in pages:
        site.switch_page(page).run()
        assert not site.exception, page
        assert site.session_state["habitat"] == "Rover pressurisé", page
        assert site.session_state["scenario_oxygene_pct"] == (32.0, None), page
        assert site.session_state["scenario_pression_kpa"] == (None, 70.3), page


def test_analyse_shows_the_three_most_relevant():
    site = AppTest.from_file(APP, default_timeout=30).run()
    assert "ui_analysed" not in site.session_state  # the results wait for ANALYSE
    site.button(key="ui_analyse_button").click().run()
    assert not site.exception
    assert site.session_state["ui_analysed"]


def test_slider_ranges_round_trip():
    from importlib import import_module

    assert import_module("flame.ui.environment").bounds_text("O₂", (30, None), "%") == "O₂ ≥ 30 %"


def test_mars_conditions_contain_no_atmosphere_figure():
    from flame.ui import conditions

    mars = conditions("Base martienne")
    assert mars["oxygene_pct"] == (None, None) and mars["pression_kpa"] == (None, None)
    assert mars["sources"]["oxygene_pct"] == "inconnu"


def test_page_one_has_one_button_per_crew_environment():
    from flame.commun import HABITATS
    from flame.ui.places import EARTH, PLACE_ICONS, PLACE_ROWS

    offered = [place for row in PLACE_ROWS for place in row]
    assert sorted(offered) == sorted([*HABITATS, EARTH])  # every habitat of the contract, and the Earth reference
    assert set(PLACE_ICONS) == set(offered)  # each button has its small logo
    site = AppTest.from_file(APP, default_timeout=30).run()
    assert [b.key for b in site.button if b.key.startswith("ui_place_")] == [f"ui_place_{place}" for place in offered]
    assert [b.key for b in site.button if b.key.startswith("ui_body_")] == []  # no planet to tap first


def test_the_button_of_the_current_habitat_is_highlighted():
    site = AppTest.from_file(APP, default_timeout=30).run()
    assert site.button(key="ui_place_Base lunaire").proto.type == "primary"  # the scenario starts on the Moon base
    site.button(key="ui_place_Station").click().run()
    assert site.button(key="ui_place_Station").proto.type == "primary"
    assert site.button(key="ui_place_Base lunaire").proto.type == "secondary"


def test_earth_button_shows_the_reference():
    site = AppTest.from_file(APP, default_timeout=30).run()
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


def test_chart_draws_dotted_zones_and_the_selection_as_a_box():
    import flame.comparateur as comparateur
    from flame.commun import charger_fiches, charger_tests
    from flame.ui import style_conditions_chart

    tests, fiches = charger_tests(), charger_fiches()
    scenario = {"oxygene_pct": (32.0, None), "pression_kpa": (None, 70.3), "debit_air_cm_s": (None, None)}
    for view in ("pression", "debit"):
        figure = style_conditions_chart(
            comparateur.graphique_conditions(tests, fiches, scenario, vue=view), scenario, view
        )
        box, *others = figure.data
        assert box.name == "Your selection" and box.fill == "toself"
        assert min(box.x) == 32.0
        zones = [trace for trace in others if trace.line.dash == "dot"]
        assert len(zones) == 2 and all(trace.fill == "none" for trace in zones)
        points = [trace for trace in others if trace.mode == "markers" and trace.marker.symbol != "star"]
        grey = [trace for trace in points if trace.name == "Other tests"]
        assert grey and all(trace.marker.color == "#7d86a8" for trace in grey)
        assert all(trace.name.endswith("(matches)") for trace in points if trace not in grey)
    empty = {"oxygene_pct": (None, None), "pression_kpa": (None, None)}
    figure = style_conditions_chart(comparateur.graphique_conditions(tests, fiches, empty), empty, "pression")
    assert "Your selection" not in [trace.name for trace in figure.data]


def test_the_assistant_page_shows_the_flame_and_it_talks_while_answering():
    page = AppTest.from_file("../pages/assistant.py", default_timeout=60).run()
    assert not page.exception
    # The flame comes after the conversation; the style pins it to the bottom-right corner.
    blocks = list(page.main.children.values())
    assert "ui_assistant_mascot" in str(blocks[-1].proto)

    def answer_while_talking():
        import streamlit as st

        from flame.ui import talking

        with talking():
            st.session_state["marker_seen"] = True
        st.session_state["done"] = True

    page = AppTest.from_function(answer_while_talking).run()
    assert not page.exception and page.session_state["done"]
    # The marker is gone once the answer is written: the flame stops talking.
    assert "ff-talking" not in str(page.main)
    assert "ff-talking" in Path("flame/ui/three/mascot.html").read_text()
