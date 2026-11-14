"""`uv run verifier` : met le code en forme, puis lance les vérifications du CI."""

import subprocess
import sys

ETAPES = [
    ("Mise en forme", ["ruff", "format", "."]),
    ("Règles de code", ["ruff", "check", "--fix", "."]),
    ("Tests", ["pytest"]),
]


def main() -> int:
    echecs = []
    for nom, commande in ETAPES:
        print(f"\n== {nom} : {' '.join(commande)}", flush=True)
        if subprocess.run([sys.executable, "-m", *commande]).returncode != 0:
            echecs.append(nom)
    if echecs:
        print(f"\nÀ corriger avant d'envoyer : {', '.join(echecs)}.")
        return 1
    print("\nTout est bon : vous pouvez envoyer votre travail.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
