"""Tests du comparateur. Propriétaire : rôle D."""

from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from flame.commun import INCONNU, charger_fiches, charger_tests
from flame.comparateur import (
    CRITERES,
    VARIABLES,
    carte,
    comparables,
    comparer,
    instruments_communs,
    plages,
    points,
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


def test_resume_dit_ce_qui_ressort():
    phrases = resume(charger_fiches(), charger_tests(), ["EXEMPLE-A", "EXEMPLE-C"], 30, "Moon base")
    assert phrases[0].startswith("Exemple C (fictif) : gouttes de carburant is complementary to")
    assert "Tested at or above the Moon base oxygen level (30 %)" in phrases[1]
    assert "Oxygen ranges overlap at 16 to 21 %." in phrases
    assert "Pressure ranges do not overlap" in " ".join(phrases)


def test_resume_signale_ce_qui_manque_sans_l_inventer():
    phrases = " ".join(resume(charger_fiches(), charger_tests(), ["EXEMPLE-A", "EXEMPLE-B"], 30, "Moon base"))
    assert "Oxygen is only recorded for" in phrases
    assert "None was tested at the Moon base oxygen level (30 %): the highest is 21 %." in phrases


def test_resume_sans_atmosphere_connue_ne_parle_pas_de_l_habitat():
    phrases = " ".join(resume(charger_fiches(), charger_tests(), ["EXEMPLE-A", "EXEMPLE-C"]))
    assert "oxygen level" not in phrases


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
