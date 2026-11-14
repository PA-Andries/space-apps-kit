"""Tests de l'interface. Propriétaire : rôle F."""

from flame.ui.scene import DOSSIER_THREE


def test_la_scene_attend_ses_reglages():
    assert "__REGLAGES__" in (DOSSIER_THREE / "flamme.html").read_text(encoding="utf-8")
