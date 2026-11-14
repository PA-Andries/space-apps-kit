"""Vérifie les règles d'import de CONTRIBUTING.md (règles 4, 5 et 6). Propriétaire : rôle A."""

import ast
from pathlib import Path

import pytest

RACINE = Path(__file__).parent.parent
DOSSIERS = sorted(dossier.name for dossier in (RACINE / "flame").iterdir() if (dossier / "__init__.py").exists())
FICHIERS = sorted([RACINE / "app.py", *RACINE.glob("pages/*.py"), *RACINE.glob("flame/**/*.py")])
# Règle 5 : ce que chaque dossier a le droit d'importer en plus de lui-même.
PERMIS_POUR_TOUS = {"commun", "ui"}
PERMIS_EN_PLUS = {"assistant": {"recherche"}}
# Import profond toléré : `flame.commun` charge Streamlit, dont le pipeline n'a pas besoin.
EXCEPTIONS = {("pipeline", "flame.commun.constantes")}


def dossier_de(fichier: Path) -> str:
    """Le dossier de `flame/` auquel appartient un fichier ; `pages` ou `app` sinon."""
    parties = fichier.relative_to(RACINE).parts
    return parties[1] if parties[0] == "flame" and len(parties) > 2 else Path(parties[0]).stem


def imports_flame(fichier: Path) -> list[str]:
    """Les modules `flame...` importés par un fichier."""
    modules = []
    for noeud in ast.walk(ast.parse(fichier.read_text(encoding="utf-8"))):
        if isinstance(noeud, ast.ImportFrom) and noeud.module:
            modules.append(noeud.module)
        elif isinstance(noeud, ast.Import):
            modules.extend(alias.name for alias in noeud.names)
    return [module for module in modules if module == "flame" or module.startswith("flame.")]


def nom_court(fichier: Path) -> str:
    return str(fichier.relative_to(RACINE))


@pytest.mark.parametrize("fichier", FICHIERS, ids=nom_court)
def test_imports(fichier):
    ici = dossier_de(fichier)
    for module in imports_flame(fichier):
        cible, *sous_module = module.split(".")[1:] or [""]
        if cible == ici or (ici, module) in EXCEPTIONS:
            continue
        assert not sous_module, f"Règle 4 : importez `flame.{cible}`, pas `{module}` (on passe par la vitrine)."
        assert cible != "pipeline", "Règle 5 : personne n'importe `flame.pipeline`, le site ne lit que les CSV."
        if ici in DOSSIERS:
            permis = PERMIS_POUR_TOUS | PERMIS_EN_PLUS.get(ici, set())
            assert cible in permis, f"Règle 5 : `flame.{ici}` n'a pas le droit d'importer `flame.{cible}`."


@pytest.mark.parametrize("fichier", [f for f in FICHIERS if dossier_de(f) != "commun"], ids=nom_court)
def test_pas_de_lecture_directe_des_csv(fichier):
    if dossier_de(fichier) == "pipeline":
        pytest.skip("le pipeline écrit les CSV")
    assert "read_csv" not in fichier.read_text(encoding="utf-8"), (
        "Règle 6 : lisez les données avec charger_fiches(), charger_tests() ou charger_publications()."
    )
