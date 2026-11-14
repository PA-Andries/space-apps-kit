"""Tests du comparateur. Propriétaire : rôle D."""

from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from flame.commun import INCONNU, charger_fiches, charger_tests
from flame.comparateur import (
    ABSENT,
    CRITERES,
    VARIABLES,
    carte,
    comparables,
    comparer,
    cote_a_cote,
    explication_carte,
    instruments_communs,
    mesures,
    plages,
    points,
    portrait,
    resume,
    separer,
    variables_communes,
)

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
