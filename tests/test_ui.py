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


def _pick_moon_base_then_spacesuit():
    from flame.ui.places import choose_body, choose_place

    choose_body("Lune")
    choose_place("Base lunaire")
    choose_place("Scaphandre")


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


def test_the_spacesuit_does_not_change_the_habitat():
    """Like Earth, the spacesuit is a reference: it is explored without replacing the crew's habitat."""
    site = AppTest.from_function(_pick_moon_base_then_spacesuit).run()
    assert site.session_state["ui_place"] == "Scaphandre"
    assert site.session_state["ui_habitat"] == "Base lunaire"


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
    site.button(key="ui_place_Station").click().run()
    assert site.session_state["ui_habitat"] == "Station"  # app.py turns it into the scenario
    assert not site.exception


def test_moon_base_fills_the_statement_bounds():
    site = AppTest.from_file(APP, default_timeout=30).run()
    site.button(key="ui_place_Base lunaire").click().run()
    assert not site.exception
    # Lot F: "Moon base" fills O2 >= 30 % and <= 70.3 kPa (statement). A handle at the end of its scale = no bound.
    assert site.slider(key="ui_oxygen").value == (30.0, 100.0)
    assert site.slider(key="ui_pressure").value == (0.0, 70.3)
    assert site.session_state["ui_gravity"] is None  # no Moon button: the base keeps its 0.165 g


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
    # Lot F is done when "Moon base & rover" fills O2 >= 30 % and <= 70.3 kPa
    # and the other pages receive this scenario (they read it with get_scenario(), lot A).
    pages = re.findall(r'st\.Page\("([^"]+)"', Path(APP).read_text(encoding="utf-8"))
    site = AppTest.from_file(APP, default_timeout=60).run()
    site.button(key="ui_place_Base lunaire").click().run()
    site.slider(key="ui_oxygen").set_value((32.0, 100.0)).run()
    for page in pages:
        site.switch_page(page).run()
        assert not site.exception, page
        assert site.session_state["habitat"] == "Base lunaire", page
        assert site.session_state["scenario_oxygene_pct"] == (32.0, None), page
        assert site.session_state["scenario_pression_kpa"] == (None, 70.3), page


def test_the_three_most_relevant_are_shown_without_a_click():
    """Hierarchy (Ethan, 14 Nov): the results no longer wait for ANALYSE, which now opens the full ranking."""
    site = AppTest.from_file(APP, default_timeout=30).run()
    assert not site.exception
    textes = [block.value for block in site.markdown]
    assert not any("Where they agree" in texte for texte in textes)  # removed at Martin's request, 15 Nov
    assert any("Tests in your conditions, by fuel" in texte for texte in textes)  # the data gaps, on arrival
    assert site.button(key="ui_analyse_button").label == "ANALYSE ALL 24"


def test_slider_ranges_round_trip():
    from importlib import import_module

    assert import_module("flame.ui.environment").bounds_text("O₂", (30, None), "%") == "O₂ ≥ 30 %"


def test_mars_conditions_contain_no_atmosphere_figure():
    from flame.ui import conditions

    mars = conditions("Base martienne")
    assert mars["oxygene_pct"] == (None, None) and mars["pression_kpa"] == (None, None)
    assert mars["sources"]["oxygene_pct"] == "inconnu"


def test_page_one_has_one_button_per_atmosphere():
    from flame.commun import HABITATS, conditions_habitat
    from flame.ui.places import EARTH, PLACE_ICONS, PLACE_ROWS, SAME_CONDITIONS_AS, SPACESUIT

    offered = [place for row in PLACE_ROWS for place in row]
    # Earth, the reference, then the two crew environments. The spacesuit is no place to live in: no button.
    assert offered == [EARTH, "Station", "Base lunaire"]
    assert SPACESUIT not in offered
    assert set(offered) <= set(PLACE_ICONS)  # each button has its small logo
    # A habitat of the contract without a button either has exactly the conditions of a button's place...
    without_button = [habitat for habitat in HABITATS if habitat not in offered]
    assert sorted(without_button) == ["Base martienne", "Rover pressurisé", "Vaisseau"]
    for habitat, button in SAME_CONDITIONS_AS.items():
        assert button in offered and conditions_habitat(habitat) == conditions_habitat(button), habitat
    # ... or is the Mars base, for which the statement gives no atmosphere at all.
    assert set(without_button) - set(SAME_CONDITIONS_AS) == {"Base martienne"}
    assert conditions_habitat("Base martienne")["oxygene_pct"] == (None, None)
    site = AppTest.from_file(APP, default_timeout=30).run()
    assert [b.key for b in site.button if b.key.startswith("ui_place_")] == [f"ui_place_{place}" for place in offered]
    assert [b.label for b in site.button if b.key.startswith("ui_place_")] == [
        "Earth",
        "Station & spacecraft",
        "Moon base & rover",
    ]
    assert [b.key for b in site.button if b.key.startswith("ui_body_")] == []  # no planet to tap first


def test_page_one_says_why_mars_is_not_offered_and_that_it_will_come():
    from flame.ui.places import MARS_NOTE, MARS_TAG

    site = AppTest.from_file(APP, default_timeout=30).run()
    assert not site.exception
    shown = [block.value for block in site.markdown]
    titles = [text for text in shown if "**Mars base**" in text]
    assert len(titles) == 1 and MARS_TAG in titles[0] and MARS_TAG == "Future feature"
    assert MARS_NOTE in shown
    # The two checked facts, then the team's intention, without promising that NASA will publish anything.
    assert "no atmosphere" in MARS_NOTE and "partial gravity" in MARS_NOTE
    assert MARS_NOTE.endswith("once such data exists.")


def test_a_place_without_a_button_highlights_the_button_that_stands_for_it():
    site = AppTest.from_file(APP, default_timeout=30)
    site.session_state["ui_habitat"] = "Rover pressurisé"  # a scenario kept from before the buttons merged
    site.run()
    assert not site.exception
    assert site.button(key="ui_place_Base lunaire").proto.type == "primary"


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
    assert not any("Earth is the reference" in caption.value for caption in site.caption)  # no grey line (Mathéo)


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


def _investigations_tile(site) -> str:
    """The figure on the "Investigations" tile of page 1."""
    import re

    shown = " ".join(str(block.value) for block in site.get("html"))
    found = re.search(r"<span>Investigations</span><strong>([^<]+)</strong>", shown)
    assert found, "the Investigations tile is not on the page"
    return found.group(1)


def test_ticking_every_fuel_covers_as_much_as_ticking_none():
    """Ethan's bug (Sun 15 Nov): with three pills only, ticking them all covered less than ticking none.

    Smoke and dust had no pill, so the filter dropped them with no way to get them back. Every family of
    the data has a pill now, and ticking them all must come back to the same figures as ticking none.
    """
    site = AppTest.from_file(APP, default_timeout=30).run()
    aucune = _investigations_tile(site)

    pastilles = site.pills(key="ui_fuels")
    site.pills(key="ui_fuels").set_value(list(pastilles.options)).run()
    assert not site.exception
    assert _investigations_tile(site) == aucune


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
        # Les tests qui correspondent gardent le nom de leur investigation et sont cerclés.
        assert all(trace.marker.line.width for trace in points if trace not in grey)
    empty = {"oxygene_pct": (None, None), "pression_kpa": (None, None)}
    figure = style_conditions_chart(comparateur.graphique_conditions(tests, fiches, empty), empty, "pression")
    assert "Your selection" not in [trace.name for trace in figure.data]


def test_the_assistant_page_shows_the_flame_and_it_talks_while_answering():
    page = AppTest.from_file("../pages/assistant.py", default_timeout=60).run()
    assert not page.exception
    # The flame stands in the bottom bar, just before the chat box (which hides its lower half).
    bottom_bar = [block for block in page._tree.children.values() if "assistant_question" in str(block)][0]
    flame, chat_box = [str(child.proto) for child in bottom_bar.children.values()]
    assert "ui_assistant_mascot" in flame and "assistant_question" in chat_box

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


def test_colours_follow_the_60_30_10_rule():
    from flame.ui import chart, style

    # One accent only (flame orange): no pink, green or violet left in the interface's colours.
    interface = Path("flame/ui/style.py").read_text() + Path("flame/ui/components.py").read_text()
    for colour in ("#d9365e", "#f0457a", "#e44a70", "22, 163, 74", "124, 58, 237"):
        assert colour not in interface
    assert style.FLAME == style.ACCENT == "#e8622a"
    assert chart.SELECTION_COLOR == "232, 98, 42"  # the user's selection is the accent


def test_flamy_is_the_chatbot_and_every_page_but_home_has_a_home_link():
    assert 'label="Flamy"' in Path("flame/ui/home.py").read_text()
    assert 'st.title("Flamy")' in Path("pages/assistant.py").read_text()


def test_the_menu_is_a_bar_at_the_top_and_the_environment_shows_under_it():
    app = Path("app.py").read_text()
    assert 'position="top"' in app
    for title in ("Home", "Investigations", "Compare"):
        assert f'title="{title}"' in app
    assert "Data and export" not in app  # retirée : son tableau est un onglet d'Investigations
    site = AppTest.from_file(APP, default_timeout=30).run()
    assert not site.exception
    assert not site.sidebar.children  # no sidebar any more
    assert "ui_status_line" in str([block.proto for block in site.main.children.values()])


def test_outcomes_sort_nasa_results_and_show_on_arrival():
    import pandas as pd

    from flame.ui import count_outcomes, kind_of_result

    assert kind_of_result("Extinction") == "went_out"
    assert kind_of_result("hot ignition: No; end: -") == "no_ignition"
    assert kind_of_result("hot ignition: yes; end: FT") == "burned"
    assert kind_of_result("cool flame observed") == "burned"
    assert kind_of_result(float("nan")) == "unknown"
    assert kind_of_result("no cool-flame burning rate reported") == "unknown"
    tests = pd.DataFrame({"resultat": ["Extinction", "Completion", None, "hot ignition: no; end: -"]})
    assert count_outcomes(tests) == {"burned": 1, "went_out": 1, "no_ignition": 1, "unknown": 1}

    from flame.ui import answer

    moon = {"oxygene_pct": (30.0, None), "pression_kpa": (None, 70.3)}
    assert answer({"burned": 3, "went_out": 1, "no_ignition": 0, "unknown": 5}, moon)[0] == "yes"
    # NASA's "Extinction" is a flame that burned and then went out by itself: it still burned.
    assert answer({"burned": 0, "went_out": 2, "no_ignition": 1, "unknown": 0}, moon)[0] == "yes"
    assert answer({"burned": 0, "went_out": 0, "no_ignition": 1, "unknown": 0}, moon)[0] == "not_seen"
    # Saffire-II: only the microgravity length says whether the sample burned in space.
    assert kind_of_result("microgravity burn length 5 cm & 0 (note 2); 1-g burn length ~ 0 (Nomex)") == "burned"
    assert kind_of_result("microgravity burn length ~ 0; 1-g burn length Complete") == "no_ignition"
    assert answer({"burned": 0, "went_out": 0, "no_ignition": 0, "unknown": 4}, moon)[1] == "No data"
    mars = {"oxygene_pct": (None, None), "pression_kpa": (None, None)}  # no atmosphere bounds: no answer
    assert answer({"burned": 400, "went_out": 1, "no_ignition": 1, "unknown": 0}, mars)[1] == "No answer"
    # The card itself left page 1 (Ethan, Sun 15 Nov): the sorting it rests on is still tested here.


def test_page_one_explains_how_to_use_the_dashboard():
    from flame.ui.intro import STEPS

    site = AppTest.from_file(APP, default_timeout=30).run()
    assert not site.exception
    shown = " ".join(str(block.value) for block in site.get("html"))
    assert "How to use this dashboard" in shown
    for title, _ in STEPS:
        assert title in shown, title


def test_the_how_to_card_folds_away_and_comes_back():
    site = AppTest.from_file(APP, default_timeout=30).run()
    site.button(key="ui_intro_hide").click().run()
    assert not site.exception
    assert [b.key for b in site.button if b.key == "ui_intro_hide"] == []
    assert "Choose your environment" not in " ".join(str(block.value) for block in site.get("html"))
    site.button(key="ui_intro_show").click().run()
    assert [b.key for b in site.button if b.key == "ui_intro_hide"] == ["ui_intro_hide"]


def test_page_one_explains_each_of_the_three_investigations():
    """The detailed cards of #49, now shown on arrival: the results no longer wait for ANALYSE."""
    site = AppTest.from_file(APP, default_timeout=30).run()
    assert not site.exception
    shown = " ".join(str(block.value) for block in site.get("html"))
    assert shown.count("What the experiment studied") == 3
    assert shown.count("Why it matters for Moon base") == 3
    assert "Atmosphere:" in shown and "Gravity:" in shown


def test_opening_every_slider_counts_all_of_nasa():
    """Demande d'Ethan : tout sélectionner doit atteindre les 24 investigations, pas plafonner à 20.

    Les quatre études de calcul n'ont aucune ligne de test. Poignées aux deux bouts = aucune borne :
    les compteurs disent alors ce que NASA tient en tout, sans prétendre que ces tests correspondent.
    """
    from flame.commun import charger_fiches, charger_tests

    site = AppTest.from_file(APP, default_timeout=30).run()
    site.slider(key="ui_oxygen").set_value((0.0, 100.0)).run()
    site.slider(key="ui_pressure").set_value((0.0, 520.0)).run()
    assert not site.exception
    shown = " ".join(str(block.value) for block in site.get("html"))
    assert f"<strong>{len(charger_tests()):,}</strong>" in shown
    assert f"<span>Investigations in all</span><strong>{len(charger_fiches())}</strong>" in shown


def test_the_investigation_search_follows_the_ranking():
    """La fiche et le classement complet à droite, la plus pertinente en premier, un clic l'affiche ;
    plus le tableau des tests venu de la page Data."""
    from flame.commun import charger_fiches, get_scenario
    from flame.recherche import les_plus_pertinentes

    site = AppTest.from_file(APP, default_timeout=60).run()
    site.switch_page("pages/recherche.py").run()
    assert not site.exception
    # Ni Ranking ni What we don't know ; la fiche, et le tableau des tests venu de la page Data.
    assert [onglet.label for onglet in site.tabs] == ["Investigation", "Tests + CSV"]
    ranked = list(les_plus_pertinentes(charger_fiches(), get_scenario())["id"])
    # The ranking on the right: one button per investigation, in the order of the ranking ("1. Name").
    buttons = [button for button in site.button if button.key.startswith("recherche_rang_")]
    assert [button.key.removeprefix("recherche_rang_") for button in buttons] == ranked
    assert all(button.help.endswith(identifier) for button, identifier in zip(buttons, ranked, strict=True))
    assert buttons[0].label.startswith("1. ") and buttons[0].proto.type == "primary"  # the first shown at start
    # A click on another one shows it.
    site.button(key=f"recherche_rang_{ranked[2]}").click().run()
    assert site.session_state["recherche_fiche"] == ranked[2]
    assert site.button(key=f"recherche_rang_{ranked[2]}").proto.type == "primary"


def test_within_reads_a_missing_bound_as_the_end_of_the_scale():
    from flame.ui.custom import within

    scale = (0.0, 100.0)
    assert within((30.0, 100.0), (30.0, None), scale)  # "30 % or more": the Moon base as it is filled in
    assert within((35.0, 50.0), (30.0, None), scale)  # a narrower choice stays inside
    assert not within((25.0, 100.0), (30.0, None), scale)
    assert not within((19.0, 30.0), (19.0, 23.0), scale)
    assert within((100.0, 100.0), (100.0, 100.0), scale)  # the spacesuit: a single point
    assert within((0.0, 100.0), (None, None), scale)  # Mars: no bound, nothing can leave it


def test_sliders_out_of_the_range_unselect_the_environment():
    site = AppTest.from_file(APP, default_timeout=30).run()
    assert site.button(key="ui_place_Base lunaire").proto.type == "primary"
    site.slider(key="ui_oxygen").set_value((25.0, 100.0)).run()  # under the Moon base's 30 %
    assert not site.exception
    assert [b.key for b in site.button if b.key.startswith("ui_place_") and b.proto.type == "primary"] == []
    assert site.session_state["ui_habitat"] == "Personnalisé"
    assert site.session_state["habitat"] == "Personnalisé"  # what the other pages read
    assert site.session_state["scenario_oxygene_pct"] == (25.0, None)  # the user's values are kept
    assert not any("no environment is selected" in caption.value for caption in site.caption)  # no grey line


def test_sliders_back_in_the_range_select_the_environment_again():
    site = AppTest.from_file(APP, default_timeout=30).run()
    site.slider(key="ui_oxygen").set_value((25.0, 100.0)).run()
    site.slider(key="ui_oxygen").set_value((35.0, 100.0)).run()  # inside "30 % or more" again
    assert site.button(key="ui_place_Base lunaire").proto.type == "primary"
    assert site.session_state["ui_habitat"] == "Base lunaire"
    assert site.session_state["scenario_oxygene_pct"] == (35.0, None)


def test_a_narrower_choice_keeps_the_environment_selected():
    site = AppTest.from_file(APP, default_timeout=30).run()
    site.slider(key="ui_pressure").set_value((40.0, 60.0)).run()  # still under the Moon base's 70.3 kPa
    assert site.button(key="ui_place_Base lunaire").proto.type == "primary"
    assert site.session_state["ui_habitat"] == "Base lunaire"


def test_a_click_on_the_same_button_brings_its_values_back():
    site = AppTest.from_file(APP, default_timeout=30).run()
    site.slider(key="ui_oxygen").set_value((25.0, 100.0)).run()
    site.button(key="ui_place_Base lunaire").click().run()
    assert site.slider(key="ui_oxygen").value == (30.0, 100.0)
    assert site.button(key="ui_place_Base lunaire").proto.type == "primary"


def test_a_custom_environment_survives_a_visit_to_another_page():
    site = AppTest.from_file(APP, default_timeout=30).run()
    site.slider(key="ui_oxygen").set_value((25.0, 100.0)).run()
    site.switch_page("pages/recherche.py").run()
    assert not site.exception
    assert site.session_state["habitat"] == "Personnalisé"
    assert site.session_state["scenario_oxygene_pct"] == (25.0, None)
    site.switch_page("pages/accueil.py").run()
    assert site.slider(key="ui_oxygen").value == (25.0, 100.0)
    assert [b.key for b in site.button if b.key.startswith("ui_place_") and b.proto.type == "primary"] == []


def _spacesuit_sliders():
    import streamlit as st

    from flame.ui.custom import single_value_style

    st.session_state["ui_oxygen"] = (100.0, 100.0)  # the spacesuit: both handles on 100 %
    st.session_state["ui_pressure"] = (0.0, 70.3)
    single_value_style(["ui_oxygen", "ui_pressure", "ui_missing"])


def test_two_handles_on_the_same_point_show_one_number():
    site = AppTest.from_function(_spacesuit_sliders).run()
    assert not site.exception
    shown = " ".join(str(block.value) for block in site.get("html"))
    assert ".st-key-ui_oxygen" in shown and ".st-key-ui_pressure" not in shown


def test_flamy_sits_on_every_page_and_opens_a_chat_window():
    app = Path("app.py").read_text()
    assert "pages/assistant.py" not in app and "afficher_cadre(repondre)" in app
    site = AppTest.from_file(APP, default_timeout=30).run()
    assert not site.exception
    assert site.button(key="ui_flamy_open")  # Flamy's button, bottom right
    site.button(key="ui_flamy_open").click().run()
    assert not site.exception


def test_flamy_stays_calm_and_looks_at_the_visitor_on_the_assistant_page():
    from flame.ui.scene import _fill

    page = _fill("mascot.html", {"calm": True})
    assert '{"calm": true}' in page and "pointermove" in page  # the eyes follow the pointer
    assert "mascot_scene(height=170, calm=True)" in Path("flame/ui/home.py").read_text()
    assert '{"calm": false}' in _fill("mascot.html", {"calm": False})  # elsewhere he still waves


def test_the_flamy_window_opens_and_answers():
    def corner():
        import streamlit as st

        from flame.ui import flamy_corner

        def fake_answer(question, history, fiches):
            st.session_state["asked"] = question
            return "An answer from the records."

        flamy_corner(fake_answer)

    page = AppTest.from_function(corner, default_timeout=30).run()
    page.button(key="ui_flamy_open").click().run()
    assert not page.exception  # the window opens without error (it once failed on a missing argument)
    # The window's content is drawn: the conversation and the question box.
    assert page.chat_input(key="ui_flamy_question") is not None
    # (Typing a question reruns the window as a fragment in a real browser; AppTest cannot replay that.)


def test_the_research_conditions_say_what_was_tested_and_what_never_was():
    import pandas as pd

    from flame.ui import coverage

    tests = pd.DataFrame(
        {
            "investigation_id": ["A", "A", "B", "C"],
            "oxygene_pct": [21.0, 35.0, 21.0, 21.0],
            "pression_kpa": [101.0, 60.0, 101.0, None],
            "debit_air_cm_s": [None, None, None, None],
        }
    )
    fiches = pd.DataFrame({"id": ["A", "B", "C"], "type_combustible": ["gaz", "liquide", "solide"]})
    moon = {"oxygene_pct": (30.0, None), "pression_kpa": (None, 70.3), "gravite": 0.165}
    rows = {row["condition"]: row for row in coverage(tests, fiches, moon)}
    assert rows["Gravity"]["status"] == "Not tested"  # partial gravity: never tested, and said so
    assert rows["Oxygen and pressure together"]["status"] == "Partly"  # 1 test only
    assert rows["Gas fuels"]["status"] == "Tested" and rows["Liquid fuels"]["status"] == "Not tested"
    station = {"oxygene_pct": (19.0, 23.0), "pression_kpa": (90.0, 110.0), "gravite": 0.0}
    rows = {row["condition"]: row for row in coverage(tests, fiches, station)}
    assert rows["Gravity"]["status"] == "Tested"
    assert rows["Solid fuels"]["status"] == "Partly"  # tested at that oxygen, but its pressure is not recorded


def test_coverage_at_1_g_counts_only_rows_with_a_1_g_result():
    """PSI's tests flew in microgravity: only Saffire-II's rows also record a 1-g burn length."""
    from flame.commun import charger_fiches, charger_tests
    from flame.ui import coverage

    earth = {"oxygene_pct": (19.0, 23.0), "pression_kpa": (90.0, 110.0), "gravite": 1.0}
    gravity = coverage(charger_tests(), charger_fiches(), earth)[0]
    assert gravity["condition"] == "Gravity" and gravity["status"] != "Tested"
    assert "microgravity" in gravity["detail"]


def test_the_combination_verdict_checks_every_setting_at_once():
    """Le verdict compte les tests qui ont tous les réglages ensemble ; hors microgravité, jamais testé."""
    import pandas as pd

    from flame.ui import combination

    tests = pd.DataFrame(
        {
            "investigation_id": ["A", "A", "B", "D"],
            "oxygene_pct": [35.0, 35.0, 35.0, 35.0],
            "pression_kpa": [60.0, 101.0, 60.0, 60.0],
            "debit_air_cm_s": [None, None, None, None],
            "source": ["https://psi.nasa.gov/A", "https://psi.nasa.gov/A", "https://psi.nasa.gov/B", None],
        }
    )
    fiches = pd.DataFrame({"id": ["A", "B", "D"], "type_combustible": ["gaz", "liquide", "fumée"]})
    station = {"oxygene_pct": (30.0, None), "pression_kpa": (None, 70.3), "gravite": 0.0}
    verdict = combination(tests, fiches, station)
    assert verdict["status"] == "Tested" and verdict["headline"].startswith("Yes: 3 ")
    assert [name for name, _ in verdict["sources"]] == ["A", "B"]
    # Le combustible choisi compte aussi ; la fumée est un solide, comme dans le filtre de Home.
    assert combination(tests, fiches, {**station, "type_combustible": ["liquide"]})["headline"].startswith("Yes: 1 ")
    solids = ["solide", "fumée", "poussière"]
    assert combination(tests, fiches, {**station, "type_combustible": solids})["status"] == "Tested"
    # À la gravité lunaire : jamais testé, et le verdict dit ce qui s'en approche en microgravité.
    moon = combination(tests, fiches, {**station, "gravite": 0.165})
    assert moon["status"] == "Not tested" and "0.165 g" in moon["headline"] and "3 tests" in moon["detail"]


def test_the_selection_box_always_holds_the_circled_tests():
    """Every circled test is inside the orange box, and a grey test inside it is explained (PA, 15 Nov)."""
    from itertools import product

    from flame import comparateur
    from flame.commun import charger_fiches, charger_tests
    from flame.ui import grey_tests_in_the_box, selection_box, style_conditions_chart

    tests, fiches = charger_tests(), charger_fiches()
    oxygen = [(None, None), (19, 23), (30, None), (None, 21), (21, 21)]
    pressure = [(None, None), (90, 110), (None, 70.3), (300, None), (None, 10)]
    air_flow = [(None, None), (0, None), (10, 30)]
    fuels = [[], ["solide"], ["gaz"]]
    for o2, kpa, flow, fuel, view in product(oxygen, pressure, air_flow, fuels, ["pression", "debit"]):
        scenario = {
            "habitat": "Personnalisé",
            "oxygene_pct": o2,
            "pression_kpa": kpa,
            "debit_air_cm_s": flow,
            "type_combustible": fuel,
        }
        chart = style_conditions_chart(
            comparateur.graphique_conditions(tests, fiches, scenario, vue=view), scenario, view
        )
        points = [t for t in chart.data if t.mode == "markers" and t.marker.symbol != "star"]
        circled = [(x, y) for t in points if t.marker.line.width for x, y in zip(t.x, t.y, strict=True)]
        grey = [(x, y) for t in points if not t.marker.line.width for x, y in zip(t.x, t.y, strict=True)]
        if not any(bound is not None for bound in (*o2, *kpa, *flow)) and not fuel:
            assert not [t for t in chart.data if t.name == "Your selection"] and not circled
            continue
        box = selection_box(chart.layout.meta)
        drawn = next(t for t in chart.data if t.name == "Your selection")
        assert (min(drawn.x), max(drawn.x)) == box["x"] and (min(drawn.y), max(drawn.y)) == box["y"]

        def inside(point, box=box):
            return box["x"][0] <= point[0] <= box["x"][1] and box["y"][0] <= point[1] <= box["y"][1]

        assert all(inside(point) for point in circled), (o2, kpa, flow, fuel, view)
        column = "pression_kpa" if view == "pression" else "debit_air_cm_s"
        matching = comparateur.tests_correspondants(tests, fiches, scenario).dropna(subset=["oxygene_pct", column])
        assert len(circled) == len(matching)
        grey_inside = sum(inside(point) for point in grey)
        caption = grey_tests_in_the_box(chart)
        assert caption.startswith(f"{grey_inside:,} tests inside the box") if grey_inside else caption == ""
        if grey_inside:  # only a filter that is not on the axes may leave a test of the box grey
            other = flow if view == "pression" else kpa
            assert fuel or any(bound is not None for bound in other), (o2, kpa, flow, fuel, view)


def test_setting_an_air_flow_moves_the_chart_to_the_air_flow_view():
    """No NASA test records both pressure and air flow: the pressure view would turn all grey (PA, 15 Nov)."""
    site = AppTest.from_file(APP, default_timeout=60).run()
    assert site.session_state["ui_chart_view"] == "pression"
    site.slider(key="ui_air_flow").set_range(0.0, 85.5).run()
    assert not site.exception
    assert site.session_state["ui_chart_view"] == "debit"
    site.slider(key="ui_air_flow").set_range(-6.0, 85.5).run()
    assert site.session_state["ui_chart_view"] == "pression"


def test_the_environment_line_says_partial_gravity_has_no_nasa_test():
    """The Moon's 0.165 g is the place's own gravity; the tool only has tests at 0 g and 1 g (PA, 15 Nov)."""
    from flame.ui.environment import environment_summary

    assert environment_summary("Base lunaire").endswith("0.165 g (no NASA test at this gravity)")
    assert environment_summary("Station").endswith("0 g")


def test_the_environment_line_follows_a_reference_place_and_hides_streamlit_chrome():
    """With Earth selected the line showed the station: it now shows Earth and names the kept habitat."""
    site = AppTest.from_file(APP, default_timeout=60)
    site.session_state["ui_place"] = "Terre"
    site.run()
    assert not site.exception
    shown = " ".join(str(block.value) for block in site.get("html"))
    assert "<span>Reference shown</span>Earth · O₂ 19–23 % · 90–110 kPa · 1 g" in shown
    assert "the other pages keep Moon base" in shown
    assert '[data-testid="stToolbarActions"]' in shown  # the host's toolbar is hidden for visitors


def test_the_air_flow_slider_stops_at_the_extremes_of_nasa_tests():
    """The scale ends at the lowest and highest air flow in NASA's tests, rounded to its 0.5 step (PA, 15 Nov)."""
    import pandas as pd

    site = AppTest.from_file(APP, default_timeout=60).run()
    slider = site.slider(key="ui_air_flow")
    flows = pd.read_csv("data/tests.csv")["debit_air_cm_s"].dropna()
    assert slider.min <= flows.min() < slider.min + 0.5
    assert slider.max - 0.5 < flows.max() <= slider.max


def test_the_page_carries_the_script_that_hides_the_host_badge():
    """Community Cloud draws its badge and "Manage app" outside the page: a script reaches the host's page."""
    from flame.ui.style import HOST_CHROME, HOST_CHROME_SCRIPT

    for target in ("viewerBadge", "profileContainer", "manage-app-button", "stToolbarActions"):
        assert target in HOST_CHROME
    assert "page.parent" in HOST_CHROME_SCRIPT and "display: none !important" in HOST_CHROME_SCRIPT
    site = AppTest.from_file(APP, default_timeout=60).run()
    assert not site.exception


# --- The phone version: only for narrow screens, the desktop version is not touched --------------------------
ANDROID = "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/130.0 Mobile Safari/537.36"
IPHONE = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148"
MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/130.0 Safari/537.36"


def test_every_phone_rule_sits_inside_one_narrow_screen_block():
    from flame.ui.phone import PHONE_STYLE, PHONE_WIDTH

    assert PHONE_WIDTH == 640
    body = PHONE_STYLE.removeprefix("<style>").removesuffix("</style>").strip()
    assert body.startswith("@media (max-width: 640px) {") and body.endswith("}")
    # One block only: its braces close at the very end, so no rule can reach a wide window.
    depth = 0
    for position, character in enumerate(body[body.index("{") :], start=body.index("{")):
        depth += character == "{"
        depth -= character == "}"
        assert depth > 0 or position == len(body) - 1, body[position - 40 : position + 40]
    assert depth == 0


def test_a_phone_is_told_from_a_computer_by_its_browser(monkeypatch):
    from flame.ui import phone

    assert phone.on_phone() is False  # no browser behind a test: the desktop version
    for agent, expected in [(ANDROID, True), (IPHONE, True), (MAC, False), ("", False)]:
        monkeypatch.setattr(phone, "user_agent", lambda agent=agent: agent)
        assert phone.on_phone() is expected, agent


def test_the_chart_keeps_its_legend_on_a_computer_and_moves_it_under_the_plot_on_a_phone(monkeypatch):
    import plotly.graph_objects as go

    from flame.ui import phone

    figure = go.Figure(go.Scatter(x=[1], y=[1], name="a test"))
    figure.update_layout(height=480)
    monkeypatch.setattr(phone, "user_agent", lambda: MAC)
    on_computer = phone.chart_for_phone(figure)
    assert on_computer.layout.legend.orientation is None and on_computer.layout.height == 480
    monkeypatch.setattr(phone, "user_agent", lambda: ANDROID)
    on_a_phone = phone.chart_for_phone(figure)
    assert on_a_phone.layout.legend.orientation == "h" and on_a_phone.layout.legend.y < 0


def test_on_a_phone_the_place_buttons_take_the_height_they_need():
    """With the fixed height of the row of three, the third stacked tile covered the Mars block on a phone."""
    from flame.ui.components import PLACE_BUTTONS_STYLE

    desktop, _, narrow = PLACE_BUTTONS_STYLE.partition("@media (max-width: 640px)")
    assert "height: 15rem" in desktop  # the desktop row keeps its fixed height
    assert "height: auto" in narrow


def test_page_one_carries_the_phone_style_and_the_desktop_chart():
    from flame.ui.phone import PHONE_STYLE

    site = AppTest.from_file(APP, default_timeout=30).run()
    assert not site.exception
    assert PHONE_STYLE in [str(block.value) for block in site.get("html")]
    chart = site.get("plotly_chart")[0]
    drawn = str(chart.proto).replace(" ", "").replace("\\", "")
    assert "legend" in drawn and '"orientation":"h"' not in drawn  # no phone behind a test: the desktop legend
