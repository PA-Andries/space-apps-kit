"""Vérifie les règles appliquées par les hooks git (src/space_apps_kit/regles.py). Propriétaire : rôle A."""

import pytest

from space_apps_kit.regles import (
    commande_interdite,
    erreurs_de_contenu,
    erreurs_de_couloir,
    est_un_agent,
    role_de_la_branche,
    role_du_fichier,
)


@pytest.mark.parametrize(
    ("chemin", "role"),
    [
        ("flame/recherche/moteur.py", "C"),
        ("pages/accueil.py", "F"),
        ("data/investigations.csv", "B"),
        ("tests/test_assistant.py", "E"),
        ("pages/donnees.py", "D"),
        ("pages/equipements.py", "E"),
        ("flame/commun/constantes.py", "A"),
        ("pyproject.toml", "A"),
    ],
)
def test_role_du_fichier(chemin, role):
    assert role_du_fichier(chemin) == role


def test_role_de_la_branche():
    assert role_de_la_branche("recherche/filtres") == "C"
    assert role_de_la_branche("ui/scene-flamme") == "F"
    assert role_de_la_branche("claude/tache-x") is None
    assert role_de_la_branche("main") is None


def test_dans_son_couloir():
    assert erreurs_de_couloir("recherche/filtres", "Ajoute les filtres", ["flame/recherche/moteur.py"]) == []


def test_hors_couloir_refuse():
    erreurs = erreurs_de_couloir("recherche/filtres", "Corrige la carte", ["flame/ui/composants.py"])
    assert "flame/ui/composants.py (rôle F)" in erreurs[0]


def test_fichier_partage_refuse_sans_role_a():
    assert erreurs_de_couloir("assistant/prompt", "Ajoute une lib", ["pyproject.toml"])


def test_accord_du_proprietaire():
    message = "Corrige la carte\n\nAccord: Hugo"
    assert erreurs_de_couloir("recherche/filtres", message, ["flame/ui/composants.py"]) == []


def test_branche_inconnue_demande_le_role():
    assert erreurs_de_couloir("claude/tache-x", "Un changement", ["flame/ui/scene.py"])
    assert erreurs_de_couloir("claude/tache-x", "Un changement\n\nRole: F", ["flame/ui/scene.py"]) == []
    assert erreurs_de_couloir("claude/tache-x", "Un changement\n\nRole: F", ["app.py"])


def test_role_a_touche_a_tout():
    assert erreurs_de_couloir("integration/hooks", "Regles", ["app.py", "flame/ui/scene.py"]) == []


def test_secrets_et_gros_fichiers():
    cle = "sk-ant-" + "a" * 30
    assert erreurs_de_contenu([".streamlit/secrets.toml"], "", {})
    assert erreurs_de_contenu([".env"], "", {})
    assert erreurs_de_contenu(["app.py"], f'CLE = "{cle}"', {})
    assert erreurs_de_contenu(["data/video.mp4"], "", {"data/video.mp4": 42.0})
    assert (
        erreurs_de_contenu([".env.example", ".streamlit/secrets.toml.example", "app.py"], "x = 1", {"app.py": 0.01})
        == []
    )


@pytest.mark.parametrize(
    "commande",
    ["git commit --no-verify -m x", "git push --no-verify", "git commit -nm x", "git config core.hooksPath /dev/null"],
)
def test_contournements_refuses(commande):
    assert commande_interdite(commande)


@pytest.mark.parametrize(
    "commande",
    ["git commit -m 'filtres'", "git commit --amend -m x", "git config core.hooksPath .githooks", "uv run verifier"],
)
def test_commandes_normales_permises(commande):
    assert commande_interdite(commande) is None


def test_commit_cosigne_par_une_ia(monkeypatch):
    for nom in ("CLAUDECODE", "AI_AGENT", "CODEX_SANDBOX", "CODEX_HOME", "CURSOR_AGENT", "GEMINI_CLI"):
        monkeypatch.delenv(nom, raising=False)
    assert est_un_agent("Filtres\n\nCo-authored-by: Claude <noreply@anthropic.com>")
    assert not est_un_agent("Filtres\n\nCo-authored-by: Hugo <hugo@example.org>")
