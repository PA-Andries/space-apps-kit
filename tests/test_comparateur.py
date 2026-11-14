"""Tests du comparateur. Propriétaire : rôle D."""

from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from flame.commun import INCONNU, charger_fiches, charger_tests
from flame.comparateur import (
    ABSENT,
    CRITERES,
    VARIABLES,
    capteurs,
    carte,
    ce_qui_varie,
    comparables,
    comparer,
    cote_a_cote,
    explication_carte,
    graphique_conditions,
    instruments_communs,
    mesures,
    plages,
    plages_du_scenario,
    points,
    portrait,
    resume,
    separer,
    tableau_des_tests,
    variables_communes,
)

# Importée sous un autre nom : pytest prendrait une fonction nommée `tests_...` pour un test.
from flame.comparateur import tests_correspondants as correspondants_du_scenario  # noqa: E402, I001

APP = str(Path(__file__).parents[1] / "app.py")


def _fiches(*lignes: tuple[str, str, str]) -> pd.DataFrame:
    """Des fiches minimales : (id, type de combustible, matériel)."""
    return pd.DataFrame(lignes, columns=["id", "type_combustible", "materiel"])


def _tests_vides() -> pd.DataFrame:
    return pd.DataFrame(columns=["investigation_id", *VARIABLES])


def test_les_trois_niveaux_et_leur_ordre():
    fiches = _fiches(
        ("DEPART", "solide", "MSG"),
        ("AUTRE-PHENOMENE", "fumée", "MSG"),
        ("AUTRE-ECHELLE", "solide", "Cygnus"),
        ("MEME-FAMILLE", "solide", "MSG"),
    )
    resultat = comparables(fiches, _tests_vides(), "DEPART")
    assert list(resultat["id"]) == ["MEME-FAMILLE", "AUTRE-ECHELLE", "AUTRE-PHENOMENE"]
    assert list(resultat["niveau"]) == [1, 2, 3]
    assert resultat["raison"].iloc[2] == "Same hardware, different fuel type"


def test_un_modele_garde_le_combustible_de_son_etude():
    fiches = _fiches(("VOL", "liquide", "MDCA"), ("MODELE", "liquide (modèle)", "Computer simulation"))
    assert comparables(fiches, _tests_vides(), "VOL")["niveau"].iloc[0] == 2


def test_un_combustible_inconnu_n_est_jamais_devine():
    fiches = _fiches(("VOL", "solide", "MSG"), ("SANS-TYPE", None, "MSG"))
    resultat = comparables(fiches, _tests_vides(), "VOL")
    assert resultat["niveau"].iloc[0] == 3
    assert resultat["raison"].iloc[0] == "Fuel type unknown"


def test_l_investigation_de_depart_n_est_pas_proposee():
    fiches = charger_fiches()
    resultat = comparables(fiches, charger_tests(), "EXEMPLE-A")
    assert "EXEMPLE-A" not in set(resultat["id"])
    assert len(resultat) == len(fiches) - 1


def test_variables_communes():
    tests = charger_tests()
    assert variables_communes(tests, ["EXEMPLE-A", "EXEMPLE-C"]) == VARIABLES
    assert variables_communes(tests, ["EXEMPLE-A", "EXEMPLE-B"]) == []  # EXEMPLE-B n'a aucun test


def test_une_colonne_par_investigation():
    tableau = comparer(charger_fiches(), ["EXEMPLE-A", "EXEMPLE-C"])
    assert list(tableau.columns) == ["EXEMPLE-A", "EXEMPLE-C"]
    assert list(tableau.index) == CRITERES


def test_plages_testees():
    tableau = plages(charger_tests(), ["EXEMPLE-A", "EXEMPLE-B"])
    assert tableau.loc["oxygene_pct", "EXEMPLE-A"] == "16 to 21"
    assert tableau.loc["pression_kpa", "EXEMPLE-A"] == "101"
    assert tableau.loc["oxygene_pct", "EXEMPLE-B"] == INCONNU


def test_separer_range_chaque_ligne_une_seule_fois():
    tableau = pd.DataFrame(
        {"A": ["MSG", 12, None], "B": ["MSG", 8, None]}, index=["materiel", "nb_tests", "pression_kpa"]
    )
    communs, differences, inconnus = separer(tableau)
    assert list(communs.index) == ["materiel"]
    assert list(differences.index) == ["nb_tests"]
    assert list(inconnus.index) == ["pression_kpa"]


def test_points_sans_valeur_manquante():
    tests = pd.DataFrame(
        {
            "investigation_id": ["A", "A", "B"],
            "oxygene_pct": [21.0, None, 30.0],
            "pression_kpa": [101.0, 101.0, 70.0],
        }
    )
    assert len(points(tests, ["A", "B"], ["oxygene_pct", "pression_kpa"])) == 2


def test_instruments_communs():
    fiches = pd.DataFrame({"id": ["A", "B", "C"], "capteurs": ["Caméra ; Radiomètre", "Radiomètre ; Sonde", None]})
    assert instruments_communs(fiches, ["A", "B"]) == ["Radiomètre"]
    assert instruments_communs(fiches, ["A", "C"]) == []


def _phrases(themes: dict[str, list[str]]) -> str:
    return " ".join(phrase for phrases in themes.values() for phrase in phrases)


def test_resume_range_les_phrases_par_theme():
    themes = resume(charger_fiches(), charger_tests(), ["EXEMPLE-A", "EXEMPLE-C"], 30, "Moon base")
    assert list(themes) == [
        "How they relate",
        "For your habitat",
        "Test conditions",
        "Fuels and results",
        "Data and instruments",
    ]
    assert themes["How they relate"][0].startswith("Exemple C (fictif) : gouttes de carburant is complementary to")
    assert "has 1 test row(s) at or above the Moon base oxygen level (30 %), up to 40 %." in _phrases(themes)
    assert "stops at 21 % oxygen, below the Moon base oxygen level (30 %)." in _phrases(themes)
    assert "Oxygen ranges overlap at 16 to 21 % (test rows there:" in _phrases(themes)
    assert "Pressure ranges do not overlap" in _phrases(themes)


def test_resume_signale_ce_qui_manque_sans_l_inventer():
    phrases = _phrases(resume(charger_fiches(), charger_tests(), ["EXEMPLE-A", "EXEMPLE-B"], 30, "Moon base"))
    assert "Oxygen is only recorded for" in phrases
    assert "has no oxygen value in NASA's tables." in phrases
    assert "How each test ended is not recorded for Exemple B (fictif) : fumées de matériaux." in phrases
    assert "Rows in NASA's test tables:" in phrases


def test_resume_sans_atmosphere_connue_ne_parle_pas_de_l_habitat():
    themes = resume(charger_fiches(), charger_tests(), ["EXEMPLE-A", "EXEMPLE-C"])
    assert "For your habitat" not in themes


def test_resume_cite_les_liens_donnes_par_nasa():
    relations = pd.DataFrame(
        {
            "from_id": ["EXEMPLE-A", "EXEMPLE-C", "EXEMPLE-D"],
            "to_id": ["EXEMPLE-C", "EXEMPLE-A", "EXEMPLE-A"],
            "relation": ["related to", "related to", "reuses data from"],
        }
    )
    themes = resume(charger_fiches(), charger_tests(), ["EXEMPLE-A", "EXEMPLE-C"], relations=relations)
    liens = [phrase for phrase in themes["How they relate"] if "listed by NASA as related" in phrase]
    assert len(liens) == 1  # les deux sens ne font qu'une phrase, et EXEMPLE-D n'est pas comparée


def test_resume_previent_quand_les_lignes_ne_veulent_pas_dire_la_meme_chose():
    psi = pd.DataFrame({"investigation_id": ["EXEMPLE-A", "EXEMPLE-C"], "row_levels": ["test", "sample"]})
    phrases = _phrases(resume(charger_fiches(), charger_tests(), ["EXEMPLE-A", "EXEMPLE-C"], investigations_psi=psi))
    assert "so the counts are not comparable" in phrases


def test_portrait_d_une_investigation():
    fiche = charger_fiches().iloc[0]
    psi = pd.Series(
        {"flight_platform": "ISS", "start_date": "08-01-2007", "end_date": "07-31-2016", "row_levels": "test"}
    )
    infos = portrait(fiche, charger_tests(), psi)
    assert infos["Where"] == "ISS"
    assert infos["Project dates"] == "2007 to 2016"
    assert infos["Test rows"] == "3 (one row = one test)"
    assert infos["Conditions tested"].startswith("oxygen 16 to 21 %")


def test_portrait_sans_table_psi_ne_devine_rien():
    infos = portrait(charger_fiches().iloc[0], charger_tests(), None)
    assert infos["Where"] == ABSENT
    assert infos["Project dates"] == ABSENT


def test_cote_a_cote_dit_ce_qui_est_pareil():
    tableau = cote_a_cote(charger_fiches(), charger_tests(), ["EXEMPLE-A", "EXEMPLE-B"], pd.DataFrame())
    assert list(tableau.columns) == ["same", "EXEMPLE-A", "EXEMPLE-B"]
    assert tableau.loc["Hardware", "same"] == "same"
    assert tableau.loc["type_combustible", "same"] == "different"
    assert tableau.loc["Where", "same"] == ABSENT


def test_mesures_separe_le_commun_du_propre():
    fiches = pd.DataFrame({"id": ["A", "B"], "capteurs": ["Caméra ; Radiomètre", "Radiomètre ; Sonde"]})
    communs, propres = mesures(fiches, ["A", "B"])
    assert communs == ["Radiomètre"]
    assert propres == {"A": ["Caméra"], "B": ["Sonde"]}


def test_explication_carte_dit_toujours_pourquoi():
    tests = charger_tests()
    assert explication_carte(tests, ["EXEMPLE-A", "EXEMPLE-C"]).startswith("Chart shown because")
    assert "no test condition" in explication_carte(tests, ["EXEMPLE-A", "EXEMPLE-B"])
    assert "fewer than 5 distinct test points" in explication_carte(tests, ["EXEMPLE-A", "EXEMPLE-D"])


def test_carte_seulement_si_elle_apprend_quelque_chose():
    tests = charger_tests()
    axes, lignes = carte(tests, ["EXEMPLE-A", "EXEMPLE-C"])
    assert axes == ["oxygene_pct", "pression_kpa"]
    assert len(lignes) == 6
    assert carte(tests, ["EXEMPLE-A", "EXEMPLE-B"]) is None  # EXEMPLE-B n'a aucune condition chiffrée
    assert carte(tests, ["EXEMPLE-A", "EXEMPLE-D"]) is None  # trop peu de points distincts


def test_carte_refuse_une_seule_condition_commune():
    tests = pd.DataFrame(
        {
            "investigation_id": ["A"] * 6 + ["B"] * 6,
            "oxygene_pct": [None] * 12,
            "pression_kpa": [None] * 12,
            "debit_air_cm_s": list(range(12)),
        }
    )
    assert carte(tests, ["A", "B"]) is None


DONNEES_REELLES = Path(__file__).parents[1] / "data"
LUNE = {"habitat": "Base lunaire"}
MARS = {"habitat": "Base martienne"}


def _vraies_donnees() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Les vraies fiches et les vrais tests de NASA (les autres tests tournent sur les données d'exemple)."""
    if not (DONNEES_REELLES / "tests.csv").exists():
        pytest.skip("pas encore de vraies données")
    return pd.read_csv(DONNEES_REELLES / "investigations.csv"), pd.read_csv(DONNEES_REELLES / "tests.csv")


def _traces(figure) -> dict[str, int]:
    return {trace.name: len(trace.x) for trace in figure.data}


def _tests_traces(figure) -> tuple[int, int]:
    """Le nombre de tests tracés qui correspondent à l'environnement, puis le nombre des autres."""
    points = [trace for trace in figure.data if trace.mode == "markers" and not trace.name.startswith("Spacesuit")]
    correspondent = sum(len(trace.x) for trace in points if trace.name.endswith("(matches)"))
    return correspondent, sum(len(trace.x) for trace in points) - correspondent


def test_les_plages_viennent_du_scenario_ou_de_son_habitat():
    assert plages_du_scenario(LUNE)["oxygene_pct"] == (30, None)
    assert plages_du_scenario(LUNE)["pression_kpa"] == (None, 70.3)
    assert plages_du_scenario(MARS)["oxygene_pct"] == (None, None)  # l'énoncé ne donne rien pour Mars
    etendu = {"habitat": "Base lunaire", "oxygene_pct": (25.0, 40.0), "type_combustible": ["solide"]}
    assert plages_du_scenario(etendu)["oxygene_pct"] == (25.0, 40.0)  # le scénario étendu passe avant le repli
    assert plages_du_scenario(etendu)["type_combustible"] == ["solide"]


def test_tests_correspondants_sur_les_exemples():
    fiches, tests = charger_fiches(), charger_tests()
    lune = correspondants_du_scenario(tests, fiches, LUNE)
    assert list(lune["test_id"]) == ["C-03"]  # 40 % d'oxygène à 70 kPa
    liquides = correspondants_du_scenario(tests, fiches, {"habitat": "Station", "type_combustible": ["liquide"]})
    assert liquides.empty  # le seul test d'exemple à 21 % et 101 kPa est un solide
    assert len(correspondants_du_scenario(tests, fiches, MARS)) == len(tests)  # sans plage, rien n'est écarté


def test_une_pression_absente_n_ecarte_pas_le_test_mais_se_voit():
    tests = pd.DataFrame(
        {
            "investigation_id": ["A", "A", "A"],
            "oxygene_pct": [35.0, 35.0, None],
            "pression_kpa": [60.0, None, 60.0],
            "debit_air_cm_s": [None, None, None],
        }
    )
    resultat = correspondants_du_scenario(tests, _fiches(("A", "gaz", "CIR")), LUNE)
    assert list(resultat["pression_notee"]) == [True, False]  # la ligne sans oxygène est écartée


def test_la_zone_lunaire_contient_66_tests_de_2_investigations():
    fiches, tests = _vraies_donnees()
    correspondants = correspondants_du_scenario(tests, fiches, LUNE)
    surs = correspondants[correspondants["pression_notee"]]
    assert len(surs) == 66
    assert set(surs["investigation_id"]) == {"PSI-10", "PSI-159"}  # ACME Flame Design et ACME CFI-G
    figure = graphique_conditions(tests, fiches, LUNE, vue="pression")
    assert _tests_traces(figure) == (66, 1022 - 66)
    assert {"ACME Flame Design (matches)", "ACME CFI-G (matches)"} <= set(_traces(figure))


def test_la_vue_du_debit_montre_les_131_tests_de_solides():
    fiches, tests = _vraies_donnees()
    figure = graphique_conditions(tests, fiches, LUNE, vue="debit")
    assert _tests_traces(figure) == (0, 131)  # aucun solide n'a été testé à 30 % d'oxygène ou plus


def test_chaque_investigation_a_sa_couleur_et_sa_ligne_de_legende():
    fiches, tests = _vraies_donnees()
    figure = graphique_conditions(tests, fiches, LUNE, vue="pression")
    points = [trace for trace in figure.data if trace.legendgroup]
    couleurs = {trace.legendgroup: trace.marker.color for trace in points}
    assert len(set(couleurs.values())) == len(couleurs)  # une couleur par investigation
    for groupe in couleurs:
        assert sum(trace.showlegend for trace in points if trace.legendgroup == groupe) == 1


def test_le_graphique_n_a_aucune_zone_pour_mars():
    fiches, tests = charger_fiches(), charger_tests()
    for vue in ("pression", "debit"):
        for scenario in (LUNE, MARS):
            assert not [nom for nom in _traces(graphique_conditions(tests, fiches, scenario, vue)) if "Mars" in nom]
    sans_plage = _traces(graphique_conditions(tests, fiches, MARS))
    assert not [nom for nom in sans_plage if nom.endswith("(matches)")]  # rien à surligner sans plage


def test_les_zones_disent_d_ou_viennent_leurs_chiffres():
    traces = _traces(graphique_conditions(charger_tests(), charger_fiches(), LUNE))
    assert "Moon base and rover (statement)" in traces
    assert "Earth and ISS (to be sourced)" in traces
    assert "Spacesuit (statement)" in traces


def test_resume_compte_les_tests_dans_l_environnement():
    themes = resume(charger_fiches(), charger_tests(), ["EXEMPLE-A", "EXEMPLE-C"], scenario=LUNE)
    phrases = themes["For your environment"]
    assert phrases[0] == "Your environment: oxygen at least 30 %, pressure at most 70.3 kPa."
    assert "has no test row inside it." in phrases[1]
    assert "has 1 test row(s) inside it." in phrases[2]
    mars = resume(charger_fiches(), charger_tests(), ["EXEMPLE-A", "EXEMPLE-C"], scenario=MARS)
    assert mars["For your environment"] == [
        "Your environment gives no oxygen, pressure or air flow range, so no test can be matched to it."
    ]


def _page(identifiant: str | None = None) -> AppTest:
    site = AppTest.from_file(APP, default_timeout=30)
    if identifiant:
        site.query_params["id"] = identifiant
    site.run()
    return site.switch_page("pages/comparateur.py").run()


def test_la_page_compare_sans_rien_choisir():
    site = _page()
    assert not site.exception
    assert site.selectbox(key="comparateur_depart").value == "EXEMPLE-A"
    assert site.selectbox(key="comparateur_avec_EXEMPLE-A").value is not None
    assert any("What stands out" in bloc.value for bloc in site.markdown)


def test_la_page_part_de_l_investigation_de_l_adresse():
    site = _page("EXEMPLE-C")
    assert not site.exception
    assert site.selectbox(key="comparateur_depart").value == "EXEMPLE-C"


def test_la_page_ignore_un_identifiant_inconnu():
    site = _page("PAS-UNE-ETUDE")
    assert not site.exception
    assert site.selectbox(key="comparateur_depart").value == "EXEMPLE-A"


def test_la_page_accepte_une_troisieme_investigation():
    site = _page()
    site.selectbox(key="comparateur_avec_EXEMPLE-A").set_value("EXEMPLE-C").run()
    site.selectbox(key="comparateur_troisieme_EXEMPLE-A_EXEMPLE-C").set_value("EXEMPLE-B").run()
    assert not site.exception
    assert any("vs" in titre.value and "Exemple B" in titre.value for titre in site.subheader)


def test_un_nouveau_lien_remplace_l_investigation_choisie_a_la_main():
    site = _page("EXEMPLE-C")
    site.selectbox(key="comparateur_depart").set_value("EXEMPLE-B").run()
    assert site.selectbox(key="comparateur_depart").value == "EXEMPLE-B"
    site.query_params["id"] = "EXEMPLE-C"  # l'utilisateur reclique sur « Compare » pour EXEMPLE-C
    site.run()
    assert not site.exception
    assert site.selectbox(key="comparateur_depart").value == "EXEMPLE-C"


def test_tableau_des_tests_de_l_environnement():
    fiches, tests = charger_fiches(), charger_tests()
    lune = tableau_des_tests(tests, fiches, LUNE)
    assert list(lune["Test"]) == ["C-03"]
    assert lune["Investigation"].iloc[0] == "Exemple C (fictif) : gouttes de carburant"
    assert "Oxygen (%)" in lune.columns and "Pressure (kPa)" in lune.columns
    assert len(tableau_des_tests(tests, fiches, LUNE, tous=True)) == len(tests)
    assert len(tableau_des_tests(tests, fiches, MARS)) == len(tests)  # sans plage, tout est montré


def test_le_csv_garde_les_cases_vides():
    tests = pd.DataFrame(
        {
            "investigation_id": ["A"],
            "test_id": ["1"],
            "combustible": ["PMMA"],
            "oxygene_pct": [35.0],
            "pression_kpa": [None],
            "debit_air_cm_s": [None],
            "resultat": [None],
            "source": ["https://psi.nasa.gov"],
        }
    )
    fiches = pd.DataFrame({"id": ["A"], "nom": ["Étude A"], "type_combustible": ["solide"]})
    csv = tableau_des_tests(tests, fiches, LUNE).to_csv(index=False)
    assert csv.splitlines()[1] == "A,Étude A,1,PMMA,35.0,,,,https://psi.nasa.gov"  # rien n'est inventé


def test_ce_qui_varie_par_investigation():
    tableau = ce_qui_varie(charger_tests(), charger_fiches()).set_index("Investigation")
    ligne = tableau.loc["Exemple A (fictif) : tissu dans une boîte à gants"]
    assert ligne["Test rows"] == 3
    assert ligne["Oxygen (%)"] == "16 to 21"
    assert ligne["Pressure (kPa)"] == "101"
    assert ligne["What varies"] == "oxygen, air flow"


def test_capteurs_filtre_par_investigation():
    mesures_psi = pd.DataFrame(
        {
            "investigation_id": ["EXEMPLE-A", "EXEMPLE-C"],
            "instrument": ["Caméra", "Radiomètre"],
            "measures": ["Images", "Rayonnement"],
            "unit": ["images", "W"],
            "basis": ["document", "document"],
            "source": ["rapport A", "rapport C"],
        }
    )
    fiches = charger_fiches()
    assert len(capteurs(mesures_psi, fiches)) == 2
    seul = capteurs(mesures_psi, fiches, ["EXEMPLE-C"])
    assert list(seul["Instrument"]) == ["Radiomètre"]
    assert capteurs(pd.DataFrame(), fiches).empty  # table PSI absente : un tableau vide, pas une erreur


def _page_donnees() -> AppTest:
    site = AppTest.from_file(APP, default_timeout=30).run()
    return site.switch_page("pages/donnees.py").run()


def test_la_page_data_compte_les_tests_de_l_environnement():
    site = _page_donnees()
    assert not site.exception
    assert [metrique.value for metrique in site.metric[:2]] == ["1", "1"]  # base lunaire : C-03, une investigation


def test_la_page_data_montre_tout_sur_demande():
    site = _page_donnees()
    site.toggle(key="comparateur_donnees_tous").set_value(True).run()
    assert not site.exception
    assert any("8 test rows" in legende.value for legende in site.caption)


def test_la_page_data_change_de_vue():
    site = _page_donnees()
    site.radio(key="comparateur_donnees_vue").set_value("Oxygen × air flow").run()
    assert not site.exception


def test_le_graphique_de_repartition_tient_en_trois_couleurs():
    """La vue d'ensemble : deux séries de barres, aucune légende, et la frontière des solides tracée."""
    from flame.comparateur import graphique_repartition
    from flame.comparateur.conditions import COULEUR_ACCENT, COULEUR_STRUCTURE

    fiches, tests = charger_fiches(), charger_tests()
    figure = graphique_repartition(tests, fiches, LUNE, frontiere=22.2)
    barres = [trace for trace in figure.data if trace.type == "bar"]
    assert len(barres) == 2
    assert [trace.marker.color for trace in barres] == [COULEUR_STRUCTURE, COULEUR_ACCENT]
    assert COULEUR_ACCENT == "#ff7a3d"  # l'accent du site (primaryColor), et lui seul
    assert all(trace.showlegend is False for trace in barres)
    assert figure.layout.barmode == "stack"
    formes = [forme for forme in figure.layout.shapes]
    assert any(forme.type == "line" for forme in formes)  # la frontière
    assert any("no solid tested above 22.2 %" in (note.text or "") for note in figure.layout.annotations)


def test_le_graphique_de_repartition_compte_tous_les_tests_notes():
    from flame.comparateur import graphique_repartition

    fiches, tests = charger_fiches(), charger_tests()
    figure = graphique_repartition(tests, fiches, LUNE)
    total = sum(int(valeur) for trace in figure.data for valeur in trace.y)
    assert total == int(tests["oxygene_pct"].notna().sum())
