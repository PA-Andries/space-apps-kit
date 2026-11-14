"""Traduit le jeu de données PSI vers les fichiers que le site lit : `data/investigations.csv` et `data/tests.csv`.

Copie aussi les tables complètes du jeu de données dans `data/psi/` (décrites dans `flame/pipeline/PSI_DATASET.md`).

À lancer après `psi_telecharger` : `uv run python -m flame.pipeline.psi_contrat`

Rien n'est inventé : une valeur absente de PSI reste vide. Choix de traduction, à connaître :
- `pression_kpa` et `oxygene_min` d'une fiche : la plus petite valeur testée. `debit_air` : le plus grand débit testé.
  Les plages complètes sont écrites dans `ce_qui_varie`.
- Dans `tests.csv`, oxygène et pression restent vides quand la ligne PSI donne une plage et non une valeur.
  `debit_air_cm_s` est le plus grand débit affiché pendant le test.
- `pilier` : le premier pilier attribué par l'équipe ; pour une étude fondamentale, la catégorie la mieux notée.
- `habitats` : les habitats dont le taux d'oxygène type (`ATMOSPHERES`) tombe dans la plage d'oxygène testée,
  à un point de pourcentage près. La pression n'entre pas dans ce choix.
- `verifie_par` reste vide : c'est une personne qui valide une fiche. Après sa relecture, elle relance le script
  avec `--verifie-par <prénom>`. Une validation déjà écrite dans `data/investigations.csv` est conservée.
"""

import argparse
import shutil
import sys
from pathlib import Path

import pandas as pd

from flame.commun.constantes import ATMOSPHERES, COLONNES_FICHES, COLONNES_PUBLICATIONS, COLONNES_TESTS

DOSSIER_DATA = Path(__file__).resolve().parents[2] / "data"
DOSSIER_PSI = DOSSIER_DATA / "raw" / "psi_dataset"
# Copie complète des tables PSI qui part sur git, pour les pages qui en ont besoin (liens, matériel, capteurs...).
DOSSIER_TABLES_PSI = DOSSIER_DATA / "psi"
TABLES_PSI = [
    "investigations",
    "tests",
    "measurements",
    "hardware_families",
    "relations",
    "habitats",
    "relevance",
    "raw_data_map",
    "publications",
    "documents",
    "resources",
]
KPA_PAR_ATM = 101.325
# Un essai à 21,5 % d'oxygène compte pour un habitat à 21 % : écart toléré, en points de pourcentage.
TOLERANCE_OXYGENE_PCT = 1.0
PILIER_FR = {"Prevention": "Prévenir", "Detection": "Détecter", "Suppression": "Éteindre"}
CATEGORIE_FR = {"prevent": "Prévenir", "detect": "Détecter", "react": "Éteindre"}
TYPES_COMBUSTIBLE = [
    ("smoke", "fumée"),
    ("dust", "poussière"),
    ("solid", "solide"),
    ("liquid", "liquide"),
    ("gas", "gaz"),
]


def _type_combustible(phase_psi: str) -> str:
    """`solide`, `liquide`, `gaz`, `fumée` ou `poussière`, avec `(modèle)` pour une simulation."""
    type_fr = next((fr for mot, fr in TYPES_COMBUSTIBLE if mot in phase_psi.lower()), "")
    return f"{type_fr} (modèle)" if "model" in phase_psi.lower() and type_fr else type_fr


def _pilier(fiche: pd.Series, pertinence: pd.DataFrame) -> str:
    premier = str(fiche["fire_safety_pillar"]).split(";")[0]
    if premier in PILIER_FR:
        return PILIER_FR[premier]
    # Depuis l'abandon des piliers (décision de PA, 14 novembre), `relevance` n'a plus de catégorie.
    if "category_weight" not in pertinence.columns:
        return ""
    notes = pertinence[pertinence["investigation_id"] == fiche["investigation_id"]]
    if notes.empty:
        return ""
    poids = notes.groupby("category_id")["category_weight"].mean()
    # À égalité, l'ordre de CATEGORIE_FR décide : prévenir, puis détecter, puis éteindre.
    return CATEGORIE_FR[max(CATEGORIE_FR, key=lambda categorie: poids.get(categorie, 0))]


def _plage(mini: float, maxi: float, facteur: float = 1.0) -> str:
    if pd.isna(mini) or mini == maxi:
        return ""
    return f"de {round(mini * facteur, 1):g} à {round(maxi * facteur, 1):g}"


def _ce_qui_varie(fiche: pd.Series) -> str:
    morceaux = []
    for nom, colonne, unite, facteur in [
        ("oxygène", "o2_pct", "%", 1.0),
        ("pression", "pressure_atm", "kPa", KPA_PAR_ATM),
        ("débit d'air", "flow_cm_s", "cm/s", 1.0),
    ]:
        plage = _plage(fiche[f"{colonne}_min"], fiche[f"{colonne}_max"], facteur)
        if plage:
            morceaux.append(f"{nom} {plage} {unite}")
    if fiche["n_distinct_fuels"] > 1:
        morceaux.append(f"combustible ({int(fiche['n_distinct_fuels'])} différents)")
    return " ; ".join(morceaux)


def _habitats(oxygene_min: float, oxygene_max: float) -> str:
    if pd.isna(oxygene_min):
        return ""
    proches = [
        nom
        for nom, (oxygene, _) in ATMOSPHERES.items()
        if oxygene is not None and oxygene_min - TOLERANCE_OXYGENE_PCT <= oxygene <= oxygene_max + TOLERANCE_OXYGENE_PCT
    ]
    return ";".join(proches)


def _arrondi(valeur: float, facteur: float = 1.0) -> float | None:
    return None if pd.isna(valeur) else round(valeur * facteur, 1)


def fiches_du_contrat(psi: dict[str, pd.DataFrame], deja_verifiees: dict[str, str] | None = None) -> pd.DataFrame:
    """Les investigations PSI avec les colonnes de `COLONNES_FICHES`. `psi` : les tables du jeu de données PSI."""
    deja_verifiees = deja_verifiees or {}
    capteurs = psi["measurements"].groupby("investigation_id")["instrument"].agg(" ; ".join)
    rapports = (
        psi["documents"][psi["documents"]["category"] == "Reports"].groupby("investigation_id")["file_name"].first()
    )
    lignes = []
    for _, fiche in psi["investigations"].iterrows():
        identifiant = fiche["investigation_id"]
        lignes.append(
            {
                "id": identifiant,
                "psi": identifiant,
                "nom": fiche["acronym"] if pd.notna(fiche["acronym"]) else fiche["title"],
                "pilier": _pilier(fiche, psi["relevance"]),
                "priorite": fiche["team_priority"],
                "objectif": fiche["objectives"],
                "type_combustible": _type_combustible(str(fiche["fuel_phase"])),
                "combustible": fiche["fuels"],
                "materiel": fiche["facility"],
                "oxygene_min": fiche["o2_pct_min"],
                "oxygene_max": fiche["o2_pct_max"],
                "pression_kpa": _arrondi(fiche["pressure_atm_min"], KPA_PAR_ATM),
                "debit_air": fiche["flow_cm_s_max"],
                "ce_qui_varie": _ce_qui_varie(fiche),
                "capteurs": capteurs.get(identifiant, ""),
                "habitats": _habitats(fiche["o2_pct_min"], fiche["o2_pct_max"]),
                "nb_tests": fiche["n_table_rows"],
                "resume": fiche["one_liner"],
                "source_psi": fiche["psi_url"],
                "doi": fiche["doi"],
                "source_rapport": rapports.get(identifiant, ""),
                "verifie_par": deja_verifiees.get(identifiant),
            }
        )
    return pd.DataFrame(lignes, columns=COLONNES_FICHES)


def lignes_de_tests_du_contrat(tests_psi: pd.DataFrame) -> pd.DataFrame:
    """Les lignes de tests PSI avec les colonnes de `COLONNES_TESTS`."""
    une_valeur_o2 = tests_psi["o2_pct_min"] == tests_psi["o2_pct_max"]
    une_valeur_pression = tests_psi["pressure_atm_min"] == tests_psi["pressure_atm_max"]
    tests = pd.DataFrame(
        {
            "investigation_id": tests_psi["investigation_id"],
            "test_id": tests_psi["test_id"],
            "combustible": tests_psi["fuel"],
            "oxygene_pct": tests_psi["o2_pct_min"].where(une_valeur_o2),
            "pression_kpa": (tests_psi["pressure_atm_min"] * KPA_PAR_ATM).round(1).where(une_valeur_pression),
            "debit_air_cm_s": tests_psi["flow_cm_s_max"],
            "resultat": tests_psi["outcome"],
            "source": tests_psi["raw_data_url"],
        }
    )
    return tests[COLONNES_TESTS]


def main() -> None:
    parametres = argparse.ArgumentParser(description="Écrit data/investigations.csv et data/tests.csv.")
    parametres.add_argument("dossier_psi", nargs="?", type=Path, default=DOSSIER_PSI)
    parametres.add_argument(
        "--verifie-par",
        help="prénom de la personne qui a vérifié les fiches : il est écrit sur toutes les fiches non encore validées",
    )
    arguments = parametres.parse_args()
    dossier_psi = arguments.dossier_psi
    if not (dossier_psi / "investigations.csv").exists():
        sys.exit(f"Jeu de données PSI introuvable dans {dossier_psi} : lancer d'abord flame.pipeline.psi_telecharger")
    noms = ["investigations", "tests", "measurements", "documents", "relevance"]
    psi = {nom: pd.read_csv(dossier_psi / f"{nom}.csv") for nom in noms}
    fichier_fiches = DOSSIER_DATA / "investigations.csv"
    deja_verifiees = {}
    if fichier_fiches.exists():
        anciennes = pd.read_csv(fichier_fiches).dropna(subset=["verifie_par"])
        deja_verifiees = dict(zip(anciennes["id"], anciennes["verifie_par"], strict=True))
    fiches = fiches_du_contrat(psi, deja_verifiees)
    if arguments.verifie_par:
        fiches["verifie_par"] = fiches["verifie_par"].fillna(arguments.verifie_par)
    tests = lignes_de_tests_du_contrat(psi["tests"])
    fiches.to_csv(fichier_fiches, index=False)
    tests.to_csv(DOSSIER_DATA / "tests.csv", index=False)
    # Le site lit aussi data/publications.csv dès que les vraies fiches existent. Tant que le script NTRS ne l'a pas
    # écrit, on crée un fichier avec seulement les noms de colonnes, pour que la page Recherche ne plante pas.
    fichier_publications = DOSSIER_DATA / "publications.csv"
    if not fichier_publications.exists():
        pd.DataFrame(columns=COLONNES_PUBLICATIONS).to_csv(fichier_publications, index=False)
    DOSSIER_TABLES_PSI.mkdir(exist_ok=True)
    for nom in TABLES_PSI:
        shutil.copyfile(dossier_psi / f"{nom}.csv", DOSSIER_TABLES_PSI / f"{nom}.csv")
    validees = fiches["verifie_par"].notna().sum()
    sys.stdout.write(f"{len(fiches)} fiches ({validees} validées) et {len(tests)} tests écrits dans {DOSSIER_DATA}\n")


if __name__ == "__main__":
    main()
