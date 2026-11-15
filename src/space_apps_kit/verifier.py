"""`uv run verifier` : met le code en forme, puis lance les vérifications du dépôt.

Ce sont ces vérifications qui font foi : à lancer avant chaque envoi.
"""

import subprocess
import sys

ETAPES = [
    ("Mise en forme", ["ruff", "format", "."], ["ruff", "format", "--check", "."]),
    ("Règles de code", ["ruff", "check", "--fix", "."], ["ruff", "check", "."]),
    ("Tests", ["pytest"], ["pytest"]),
]


def verifier(corriger: bool = True) -> int:
    """Lance chaque étape. Avec `corriger`, ruff met en forme ; sinon rien n'est modifié."""
    echecs = []
    for nom, commande_qui_corrige, commande_qui_controle in ETAPES:
        commande = commande_qui_corrige if corriger else commande_qui_controle
        print(f"\n== {nom} : {' '.join(commande)}", flush=True)
        if subprocess.run([sys.executable, "-m", *commande]).returncode != 0:
            echecs.append(nom)
    if echecs:
        print(f"\nÀ corriger avant d'envoyer : {', '.join(echecs)}.")
        return 1
    print("\nTout est bon : vous pouvez envoyer votre travail.")
    return 0


def main() -> int:
    return verifier(corriger=True)


if __name__ == "__main__":
    sys.exit(main())
