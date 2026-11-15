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


def _table_nasa(*lignes: tuple[str, str, str]) -> pd.DataFrame:
    """Une table `investigations` de NASA minimale : (id, famille de matériel, type d'étude)."""
    return pd.DataFrame(lignes, columns=["investigation_id", "hardware_family", "project_type"])


def _liens(*lignes: tuple[str, str, str]) -> pd.DataFrame:
    """Une table `relations` minimale : (de, vers, relation)."""
    return pd.DataFrame(lignes, columns=["from_id", "to_id", "relation"])


VOL = "Microgravity Investigation"
SOL = "Ground Investigation"


def test_les_niveaux_et_leur_ordre():
    fiches = _fiches(
        ("DEPART", "solide", "x"),
        ("MEME-MATERIEL", "gaz", "x"),
        ("LIEE-PAR-NASA", "solide", "x"),
        ("RIEN-DE-COMMUN", "solide", "x"),
    )
    table = _table_nasa(
        ("DEPART", "MSG flow duct", VOL),
        ("MEME-MATERIEL", "MSG flow duct", VOL),
        ("LIEE-PAR-NASA", "Saffire (Cygnus)", VOL),
        ("RIEN-DE-COMMUN", "ACME gas burner", VOL),
    )
    liens = _liens(("LIEE-PAR-NASA", "DEPART", "related to"))
    resultat = comparables(fiches, _tests_vides(), "DEPART", table, liens)
    assert list(resultat["id"]) == ["MEME-MATERIEL", "LIEE-PAR-NASA", "RIEN-DE-COMMUN"]
    assert list(resultat["niveau"]) == [1, 2, 3]
    assert list(resultat["raison"]) == [
        "Same hardware (MSG flow duct)",
        "Listed as related in NASA's PSI",
        "No shared hardware and no link given by NASA",
    ]


def test_le_type_de_combustible_de_l_equipe_ne_compte_pas():
    # Même type de combustible, mais ni matériel commun ni lien de NASA : rien ne les rapproche.
    fiches = _fiches(("A", "solide", "x"), ("B", "solide", "y"), ("SANS-TYPE", None, "x"))
    table = _table_nasa(
        ("A", "MSG flow duct", VOL), ("B", "Saffire (Cygnus)", VOL), ("SANS-TYPE", "MSG flow duct", VOL)
    )
    resultat = comparables(fiches, _tests_vides(), "A", table, _liens()).set_index("id")
    assert resultat.loc["B", "niveau"] == 3
    assert resultat.loc["SANS-TYPE", "niveau"] == 1  # un type de combustible absent ne change rien non plus


def test_une_etude_au_sol_ne_se_compare_que_par_ses_liens():
    fiches = _fiches(
        ("VOL", "liquide", "x"), ("MODELE", "liquide (modèle)", "y"), ("AUTRE-MODELE", "gaz (modèle)", "y")
    )
    table = _table_nasa(
        ("VOL", "MDCA droplet", VOL), ("MODELE", "Ground study", SOL), ("AUTRE-MODELE", "Ground study", SOL)
    )
    liens = _liens(("MODELE", "VOL", "reuses data from"))
    resultat = comparables(fiches, _tests_vides(), "MODELE", table, liens).set_index("id")
    assert resultat.loc["VOL", "niveau"] == 2
    assert resultat.loc["VOL", "raison"] == "One reuses the other's data, according to NASA's PSI"
    assert resultat.loc["AUTRE-MODELE", "niveau"] == 3  # deux études au sol ne partagent pas un matériel


def test_ce_que_dit_l_enonce_passe_avant_la_famille_de_materiel():
    fiches = _fiches(("FUMEE", "fumée", "x"), ("POUSSIERE", "poussière", "y"))
    table = _table_nasa(("FUMEE", "SAME smoke hardware", VOL), ("POUSSIERE", "SAME smoke hardware", VOL))
    liens = _liens(("POUSSIERE", "FUMEE", "related to"), ("POUSSIERE", "FUMEE", "shared instrument"))
    resultat = comparables(fiches, _tests_vides(), "FUMEE", table, liens)
    assert list(resultat["niveau"]) == [2]
    assert resultat["raison"].iloc[0] == "Linked by the challenge statement: shared instrument"


def test_sans_les_tables_de_nasa_seul_le_materiel_des_fiches_sert():
    fiches = _fiches(("A", "solide", "MSG"), ("B", "fumée", "MSG"), ("C", "solide", "Cygnus"))
    resultat = comparables(fiches, _tests_vides(), "A", pd.DataFrame(), pd.DataFrame())
    assert list(resultat["niveau"]) == [1, 3]
    assert resultat["raison"].iloc[0] == "Same hardware (MSG)"


def test_la_page_ne_propose_que_les_niveaux_comparables():
    from flame.comparateur import EXPLICATIONS, NIVEAUX, NIVEAUX_PROPOSES

    assert NIVEAUX_PROPOSES == (1, 2)
    assert [NIVEAUX[niveau] for niveau in NIVEAUX_PROPOSES] == ["Directly comparable", "Comparable in principle"]
    assert all(EXPLICATIONS[niveau] for niveau in NIVEAUX_PROPOSES)
    assert not any("fuel" in EXPLICATIONS[niveau].lower() for niveau in NIVEAUX_PROPOSES)
    # Chaque phrase dit ce qui relie les deux investigations, puis ce qu'on peut comparer.
    assert EXPLICATIONS[1].startswith("Same hardware.") and "measurements" in EXPLICATIONS[1]
    assert EXPLICATIONS[2].startswith("Related, but different hardware.") and "not their numbers" in EXPLICATIONS[2]


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
    assert themes["How they relate"][0].startswith("Exemple C (fictif) : gouttes de carburant is not comparable to")
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
    assert "type_combustible" not in tableau.index  # le rangement de l'équipe n'est pas montré comme une donnée
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


def _correspond(trace) -> bool:
    """Les tests qui correspondent à l'environnement sont les seuls cerclés (la légende ne les nomme plus)."""
    contour = getattr(trace.marker, "line", None)
    return bool(contour is not None and contour.width)


def _tests_traces(figure) -> tuple[int, int]:
    """Le nombre de tests tracés qui correspondent à l'environnement, puis le nombre des autres."""
    points = [trace for trace in figure.data if trace.mode == "markers" and not trace.name.startswith("Spacesuit")]
    correspondent = sum(len(trace.x) for trace in points if _correspond(trace))
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
    assert {"ACME Flame Design", "ACME CFI-G"} <= set(_traces(figure))  # pas de « (matches) » en légende


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


def test_cocher_toutes_les_familles_garde_tous_les_tests():
    """Bug d'Ethan : « fumée » et « poussière » n'avaient pas de pastille, donc tout cocher écartait 119 tests.

    Un filtre qui offre toutes les familles présentes doit, quand elles sont toutes cochées, rendre
    exactement ce que rend « aucune cochée ». Sinon « tout sélectionner » couvre moins que ne rien choisir.
    """
    from flame.commun import INCONNU
    from flame.comparateur import famille_combustible

    fiches, tests = _vraies_donnees()
    ouvert = {
        "habitat": "Station",
        "oxygene_pct": (None, None),
        "pression_kpa": (None, None),
        "debit_air_cm_s": (None, None),
    }
    familles = sorted({famille_combustible(valeur) for valeur in fiches["type_combustible"]} - {INCONNU})
    assert {"solide", "liquide", "gaz", "fumée", "poussière"} <= set(familles)

    sans_filtre = correspondants_du_scenario(tests, fiches, {**ouvert, "type_combustible": []})
    tout_coche = correspondants_du_scenario(tests, fiches, {**ouvert, "type_combustible": familles})
    assert len(tout_coche) == len(sans_filtre) == len(tests)
    # 20 des 24 investigations ont des lignes de test ; les 4 autres sont des études de calcul.
    assert tout_coche["investigation_id"].nunique() == 20


def test_les_etudes_de_calcul_comptent_par_les_donnees_qu_elles_reanalysent():
    """Bug d'Ethan : tout sélectionner affichait 20 investigations sur 24, et rien ne pouvait atteindre 24.

    Quatre investigations n'ont aucune ligne de test : ce sont des études de calcul qui reprennent les
    données d'autres vols. Elles comptent quand l'investigation qu'elles réanalysent compte, par le lien
    `reuses data from` de NASA. Tout sélectionner doit donc donner les 24.
    """
    from flame.comparateur import investigations_correspondantes

    fiches, tests = _vraies_donnees()
    relations = pd.read_csv(DONNEES_REELLES / "psi" / "relations.csv")
    ouvert = {
        "habitat": "Station",
        "oxygene_pct": (None, None),
        "pression_kpa": (None, None),
        "debit_air_cm_s": (None, None),
    }
    sans_relations = investigations_correspondantes(tests, fiches, ouvert)
    assert len(sans_relations) == 20  # les investigations qui ont fait leurs propres tests

    toutes = investigations_correspondantes(tests, fiches, ouvert, relations)
    assert len(toutes) == len(fiches) == 24
    # Les 4 gagnées sont exactement celles qui n'ont aucune ligne de test.
    sans_test = set(fiches["id"]) - set(tests["investigation_id"])
    assert set(toutes) - set(sans_relations) == sans_test

    # Une étude de calcul ne compte pas quand la source qu'elle réanalyse ne compte pas.
    lune = investigations_correspondantes(tests, fiches, LUNE, relations)
    assert set(lune) == set(correspondants_du_scenario(tests, fiches, LUNE)["investigation_id"])


def test_les_zones_disent_d_ou_viennent_leurs_chiffres():
    """La légende ne porte que le nom (demande d'Ethan) ; la provenance reste, au survol."""
    figure = graphique_conditions(charger_tests(), charger_fiches(), LUNE)
    traces = _traces(figure)
    reperes = ["Moon base and rover", "Earth and ISS", "Spacesuit"]
    assert set(reperes) <= set(traces)
    # Plus de « (statement) » ni de « (to be sourced) » : aucune de ces entrées n'ouvre de parenthèse.
    assert not any(nom.startswith(repere) and "(" in nom for nom in traces for repere in reperes)
    survols = " ".join(str(trace.hovertext or "") + str(trace.hovertemplate or "") for trace in figure.data)
    assert "Moon base and rover — statement" in survols
    assert "Earth and ISS — to be sourced" in survols
    assert "Spacesuit: 100 % oxygen, 29.6 kPa — statement" in survols


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


def _html(site) -> str:
    return " ".join(str(bloc.value) for bloc in site.get("html"))


def test_la_page_compare_deux_investigations_pas_trois():
    site = _page()
    assert not site.exception
    assert [menu.key for menu in site.selectbox] == ["comparateur_depart", "comparateur_avec_EXEMPLE-A"]


def test_la_page_ne_propose_que_des_investigations_comparables():
    site = _page()
    # EXEMPLE-B partage le matériel d'EXEMPLE-A ; EXEMPLE-C et EXEMPLE-D ne partagent rien avec elle.
    assert site.selectbox(key="comparateur_avec_EXEMPLE-A").options == [
        "EXEMPLE-B · Exemple B (fictif) : fumées de matériaux — directly comparable"
    ]
    assert "Directly comparable" in _html(site) and "Comparable in principle" in _html(site)
    assert "Complementary" not in _html(site)


def test_la_page_dit_quand_rien_n_est_comparable():
    site = _page("EXEMPLE-C")  # le matériel d'EXEMPLE-C ne se retrouve nulle part ailleurs
    assert not site.exception
    assert any("nothing to compare it with" in bloc.value for bloc in site.info)
    assert not any("What stands out" in bloc.value for bloc in site.markdown)


def test_la_page_montre_les_barres_et_les_textes_sans_chiffres_ni_fins_de_test():
    site = _page()
    assert not site.exception
    html = _html(site)
    assert "Where NASA tested each one" in html
    # Retirés à la demande de Hugo (dimanche 15 nov.) : ils chargeaient la page sans aider à comparer.
    for titre in ("At a glance", "How the tests ended"):
        assert titre not in html, titre
    assert html.count('<div class="cmp-range-head">') == 3  # oxygène, pression, débit d'air
    assert not any("guessing" in bloc.value for bloc in site.caption)


def test_les_niveaux_sont_une_legende_dans_le_bandeau_pas_des_cartes_sous_le_choix():
    site = _page()
    assert not site.exception
    bandeau = next(str(bloc.value) for bloc in site.get("html") if '<div class="cmp-band">' in str(bloc.value))
    assert '<div class="cmp-legend"><b>Legend</b>' in bandeau
    assert "Directly comparable" in bandeau and "Comparable in principle" in bandeau
    assert '<div class="cmp-level">' not in _html(site)
    # Sans investigation comparable, il n'y a ni bandeau ni légende : la phrase d'information suffit.
    assert '<div class="cmp-legend">' not in _html(_page("EXEMPLE-C"))


def test_les_barres_des_plages_disent_ou_elles_se_croisent():
    from flame.comparateur import barres_des_plages

    scenario = {"habitat": "Base lunaire", "oxygene_pct": (30.0, None), "pression_kpa": (None, 70.3)}
    barres = {
        barre["variable"]: barre for barre in barres_des_plages(charger_tests(), ["EXEMPLE-A", "EXEMPLE-C"], scenario)
    }
    oxygene = barres["oxygene_pct"]
    assert oxygene["echelle"] == (0.0, 100.0)
    assert oxygene["plages"] == {"EXEMPLE-A": (16.0, 21.0), "EXEMPLE-C": (10.0, 40.0)}
    assert oxygene["recouvrement"] == (16.0, 21.0)
    assert oxygene["environnement"] == (30.0, 100.0)  # « 30 % ou plus » va jusqu'au bout de l'échelle
    assert barres["pression_kpa"]["recouvrement"] is None  # 101 kPa d'un côté, 70 kPa de l'autre
    assert barres["debit_air_cm_s"]["environnement"] is None  # le scénario ne borne pas le débit d'air


def test_une_condition_absente_reste_absente_dans_les_barres():
    from flame.comparateur import barres_des_plages, texte_de_plage

    tests = pd.DataFrame({"investigation_id": ["A", "B"], "oxygene_pct": [21.0, None]})
    tests = tests.assign(pression_kpa=None, debit_air_cm_s=None)
    oxygene = barres_des_plages(tests, ["A", "B"])[0]
    assert oxygene["plages"] == {"A": (21.0, 21.0), "B": None}
    assert oxygene["recouvrement"] is None and oxygene["environnement"] is None
    assert texte_de_plage(None, "%") == ABSENT and texte_de_plage((21.0, 21.0), "%") == "21 %"


def test_les_fins_de_test_sont_comptees_par_investigation():
    from flame.comparateur import ISSUES, issues

    tests = pd.DataFrame(
        {
            "investigation_id": ["A", "A", "A", "B"],
            "resultat": ["Hot ignition: yes", "extinction at 12 s", None, None],
        }
    )
    comptes = issues(tests, ["A", "B"])
    assert comptes["A"] == {"burned": 1, "went_out": 1, "no_ignition": 0, "unknown": 1}
    assert comptes["B"] == {"burned": 0, "went_out": 0, "no_ignition": 0, "unknown": 1}
    assert list(comptes["A"]) == list(ISSUES)


def test_les_chiffres_cles_ne_comptent_que_ce_qui_existe():
    from flame.comparateur import chiffres_cles

    fiches, tests = charger_fiches(), charger_tests()
    lignes = dict(chiffres_cles(fiches, tests, ["EXEMPLE-A", "EXEMPLE-C"]))
    assert set(lignes) == {"Test rows", "Fuel or sample descriptions"}  # sans scénario ni table PSI, rien de plus
    assert lignes["Test rows"]["EXEMPLE-A"] == str(int((tests["investigation_id"] == "EXEMPLE-A").sum()))


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


def _onglet_des_tests() -> AppTest:
    """L'onglet « Tests + CSV », qui a quitté la page Data pour la page Investigations (Ethan, 15 nov.)."""
    site = AppTest.from_file(APP, default_timeout=30).run()
    return site.switch_page("pages/recherche.py").run()


def test_le_tableau_ne_montre_que_les_tests_de_l_environnement():
    site = _onglet_des_tests()
    assert not site.exception
    assert any("test rows from 1 investigations that ran their own tests" in legende.value for legende in site.caption)


def test_le_tableau_montre_tout_sur_demande():
    site = _onglet_des_tests()
    site.toggle(key="recherche_tests_tous").set_value(True).run()
    assert not site.exception
    assert any("8 test rows" in legende.value for legende in site.caption)


def test_le_tableau_s_exporte_en_csv():
    site = _onglet_des_tests()
    assert not site.exception
    assert any(bouton.label == "Download these tests (CSV)" for bouton in site.get("download_button"))


def test_le_graphique_de_repartition_tient_en_trois_couleurs():
    """La vue d'ensemble : deux séries de barres, aucune légende, et la frontière des solides tracée."""
    from flame.comparateur import graphique_repartition
    from flame.comparateur.conditions import COULEUR_ACCENT, COULEUR_STRUCTURE

    fiches, tests = charger_fiches(), charger_tests()
    figure = graphique_repartition(tests, fiches, LUNE, frontiere=22.2)
    barres = [trace for trace in figure.data if trace.type == "bar"]
    assert len(barres) == 2
    assert [trace.marker.color for trace in barres] == [COULEUR_STRUCTURE, COULEUR_ACCENT]
    assert COULEUR_ACCENT == "#e8622a"  # l'accent du site (primaryColor), et lui seul
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


def test_un_lien_de_l_enonce_ne_double_pas_la_phrase_du_lien_de_psi():
    """SAME et DAFT : PSI les dit « related », l'énoncé leur donne un instrument commun. Une seule phrase de lien."""
    from flame.comparateur.details import liens_nasa

    noms = {"A": "Alpha", "B": "Beta", "C": "Gamma"}
    relations = pd.DataFrame(
        [
            {"from_id": "A", "to_id": "B", "relation": "related to"},
            {"from_id": "A", "to_id": "B", "relation": "shared instrument (smoke detector used for dust)"},
            {"from_id": "C", "to_id": "B", "relation": "reuses data from"},
            {"from_id": "B", "to_id": "C", "relation": "related to"},
            {"from_id": "C", "to_id": "B", "relation": "related to"},
        ]
    )
    assert liens_nasa(relations, ["A", "B"], noms) == ["Alpha is listed by NASA as related to Beta."]
    # Le lien de l'énoncé seul ne donne aucune phrase ici : c'est la phrase du niveau qui le dit.
    assert liens_nasa(relations.iloc[[1]], ["A", "B"], noms) == []
    # « reuses data from » garde sa phrase, et deux « related to » croisés n'en font qu'une.
    assert liens_nasa(relations, ["B", "C"], noms) == [
        "Beta is listed by NASA as related to Gamma.",
        "Gamma reuses data from Beta.",
    ]
