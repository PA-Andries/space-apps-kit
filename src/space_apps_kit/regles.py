"""Les règles du dépôt, appliquées par les hooks git de `.githooks/` et par Claude Code.

Un hook bloque le commit ou l'envoi quand une règle de CONTRIBUTING.md n'est pas respectée,
et dit quoi faire. Les hooks s'activent avec `uv run verifier` (ou `uv run regles installer`).
"""

import json
import os
import re
import shlex
import subprocess
import sys
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path

DOSSIER_HOOKS = ".githooks"
TAILLE_MAX_MO = 5
ISSUE_AGENTS = "https://api.github.com/repos/PA-Andries/space-apps-kit/issues/2/comments"
# Nombre maximum de pages de 100 commentaires lues dans cette issue (2 000 commentaires).
PAGES_MAX_ISSUE = 20

# Qui possède quoi : le tableau de CONTRIBUTING.md. Le rôle A possède tout le reste.
COULOIRS = {
    "B": ("flame/pipeline/", "data/", "tests/test_pipeline.py"),
    "C": ("flame/recherche/", "pages/recherche.py", "tests/test_recherche.py"),
    "D": ("flame/comparateur/", "pages/comparateur.py", "pages/donnees.py", "tests/test_comparateur.py"),
    "E": ("flame/assistant/", "pages/assistant.py", "pages/equipements.py", "tests/test_assistant.py"),
    "F": ("flame/ui/", "pages/accueil.py", ".streamlit/config.toml", "tests/test_ui.py"),
}
# Le début du nom de branche (`dossier/sujet`) donne le rôle.
ROLE_PAR_PREFIXE = {
    "integration": "A",
    "commun": "A",
    "pitch": "A",
    "pipeline": "B",
    "donnees": "B",
    "data": "B",
    "recherche": "C",
    "comparateur": "D",
    "assistant": "E",
    "ui": "F",
    "interface": "F",
}
FICHIERS_SECRETS = re.compile(r"(^|/)(\.env(\..+)?|secrets\.toml)$")
FICHIERS_SECRETS_PERMIS = (".env.example",)
CLES = re.compile(
    r"sk-ant-[\w-]{20,}|sk-[A-Za-z0-9]{32,}|ghp_[A-Za-z0-9]{30,}|github_pat_\w{20,}|AKIA[0-9A-Z]{16}|AIza[\w-]{35}"
)
SIGNATURE_IA = re.compile(r"co-authored-by:.*(claude|codex|copilot|cursor|gemini|anthropic|openai)", re.I)
VARIABLES_AGENT = ("CLAUDECODE", "AI_AGENT", "CODEX_SANDBOX", "CODEX_HOME", "CURSOR_AGENT", "GEMINI_CLI")


def git(*arguments: str) -> str:
    """La sortie d'une commande git, ou une chaîne vide si elle échoue."""
    resultat = subprocess.run(["git", *arguments], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return resultat.stdout.strip() if resultat.returncode == 0 else ""


def branche_courante() -> str:
    return git("rev-parse", "--abbrev-ref", "HEAD")


def fichiers_indexes() -> list[str]:
    return [ligne for ligne in git("diff", "--cached", "--name-only", "--diff-filter=ACMR").splitlines() if ligne]


def role_du_fichier(chemin: str) -> str:
    """Le rôle qui possède `chemin`, d'après COULOIRS."""
    for role, prefixes in COULOIRS.items():
        if any(chemin == prefixe or (prefixe.endswith("/") and chemin.startswith(prefixe)) for prefixe in prefixes):
            return role
    return "A"


def role_de_la_branche(branche: str) -> str | None:
    """Le rôle annoncé par le nom de branche `dossier/sujet`, ou None s'il est inconnu."""
    prefixe, separateur, _ = branche.partition("/")
    return ROLE_PAR_PREFIXE.get(prefixe.lower()) if separateur else None


def ligne_du_message(message: str, cle: str) -> str | None:
    """La valeur d'une ligne `Cle: valeur` du message de commit."""
    trouve = re.search(rf"^{cle}\s*:\s*(\S.*)$", message, re.I | re.M)
    return trouve.group(1).strip() if trouve else None


def erreurs_de_couloir(branche: str, message: str, fichiers: list[str]) -> list[str]:
    """Les fichiers du commit qui sortent du couloir du rôle (règle 1 de CONTRIBUTING.md)."""
    role = (ligne_du_message(message, "Role") or role_de_la_branche(branche) or "").upper()[:1]
    if role not in {"A", *COULOIRS}:
        return [
            f"La branche « {branche} » ne dit pas votre rôle. Nommez-la `dossier/sujet` (recherche/filtres...)"
            " ou ajoutez une ligne `Role: C` (A à F) au message de commit."
        ]
    if role == "A" or ligne_du_message(message, "Accord"):
        return []
    hors_couloir = [
        f"{chemin} (rôle {role_du_fichier(chemin)})" for chemin in fichiers if role_du_fichier(chemin) != role
    ]
    if not hors_couloir:
        return []
    return [
        f"Vous êtes le rôle {role} et ce commit touche les fichiers d'un autre rôle : {', '.join(hors_couloir)}."
        " Retirez-les du commit et demandez au propriétaire, ou, s'il est d'accord,"
        " ajoutez une ligne `Accord: <son prénom>` au message de commit."
    ]


def erreurs_de_contenu(fichiers: list[str], ajouts: str, tailles_mo: dict[str, float]) -> list[str]:
    """Clés, fichiers de secrets et gros fichiers dans le commit."""
    erreurs = []
    for chemin in fichiers:
        if FICHIERS_SECRETS.search(chemin) and not chemin.endswith(FICHIERS_SECRETS_PERMIS):
            erreurs.append(f"{chemin} contient des secrets et ne se commite jamais : `git restore --staged {chemin}`.")
        if tailles_mo.get(chemin, 0) > TAILLE_MAX_MO:
            erreurs.append(
                f"{chemin} pèse {tailles_mo[chemin]:.0f} Mo (limite {TAILLE_MAX_MO} Mo) : pas de gros fichier."
            )
    if CLES.search(ajouts):
        erreurs.append("Une clé d'API apparaît dans le code ajouté. Retirez-la : elle se lit dans `st.secrets`.")
    return erreurs


def operation_git_en_cours() -> bool:
    """Vrai pendant une fusion, un rebase ou un cherry-pick : le commit reprend le travail des autres."""
    dossier_git = Path(git("rev-parse", "--git-dir") or ".git")
    return any(
        (dossier_git / nom).exists() for nom in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "rebase-merge", "rebase-apply")
    )


def refuser(erreurs: list[str], etape: str) -> int:
    if not erreurs:
        return 0
    print(f"\n{etape} refusé par les règles du dépôt (AGENTS.md, CONTRIBUTING.md) :", file=sys.stderr)
    for erreur in erreurs:
        print(f"  - {erreur}", file=sys.stderr)
    print("Corrigez puis recommencez. Ne contournez pas avec --no-verify.\n", file=sys.stderr)
    return 1


def pre_commit() -> int:
    fichiers = fichiers_indexes()
    erreurs = []
    if branche_courante() == "main" and not operation_git_en_cours():
        erreurs.append("On ne commite pas sur `main` : créez une branche `dossier/sujet`, puis une pull request.")
    ajouts = "\n".join(
        ligne[1:]
        for ligne in git("diff", "--cached", "-U0").splitlines()
        if ligne.startswith("+") and ligne[:3] != "+++"
    )
    tailles = {chemin: Path(chemin).stat().st_size / 1e6 for chemin in fichiers if Path(chemin).is_file()}
    return refuser(erreurs + erreurs_de_contenu(fichiers, ajouts, tailles), "Commit")


def commit_msg(fichier_message: str) -> int:
    if operation_git_en_cours():
        return 0
    message = Path(fichier_message).read_text(encoding="utf-8", errors="replace")
    return refuser(erreurs_de_couloir(branche_courante(), message, fichiers_indexes()), "Commit")


def est_un_agent(messages_des_commits: str) -> bool:
    """Vrai si l'envoi vient d'un agent IA : variable d'environnement ou commit cosigné par une IA."""
    return any(os.environ.get(nom) for nom in VARIABLES_AGENT) or bool(SIGNATURE_IA.search(messages_des_commits))


def claim_trouve(branche: str) -> bool | None:
    """Vrai si l'issue « com inter agents » porte un CLAIM récent citant `branche`. None sans réseau.

    GitHub rend les commentaires par pages de 100, du plus ancien au plus récent : on lit toutes les pages,
    sinon un CLAIM posté après le centième commentaire reste invisible.
    """
    depuis = (datetime.now(UTC) - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    for page in range(1, PAGES_MAX_ISSUE + 1):
        try:
            adresse = f"{ISSUE_AGENTS}?since={depuis}&per_page=100&page={page}"
            with urllib.request.urlopen(adresse, timeout=8) as reponse:
                commentaires = json.load(reponse)
        except Exception:
            return None
        if any("CLAIM" in c.get("body", "") and branche in c.get("body", "") for c in commentaires):
            return True
        if len(commentaires) < 100:
            break
    return False


def pre_push(lignes: list[str]) -> int:
    erreurs = []
    messages = ""
    for ligne in lignes:
        ref_locale, sha_local, ref_distante, sha_distant = ligne.split()
        if set(sha_local) == {"0"}:
            continue
        if ref_distante == "refs/heads/main":
            erreurs.append("On n'envoie pas directement sur `main` : poussez votre branche et ouvrez une pull request.")
        base = "origin/main" if set(sha_distant) == {"0"} else sha_distant
        messages += git("log", "--format=%B", f"{base}..{sha_local}")
    branche = branche_courante()
    if not erreurs and est_un_agent(messages):
        trouve = claim_trouve(branche)
        if trouve is False:
            erreurs.append(
                f"Agent IA : aucun CLAIM pour la branche « {branche} » dans l'issue n°2 « com inter agents »."
                " Postez-le (tâche, branche, fichiers) avant d'envoyer."
            )
        elif trouve is None:
            print("regles : issue n°2 injoignable, CLAIM non vérifié.", file=sys.stderr)
    if erreurs:
        return refuser(erreurs, "Envoi")
    from space_apps_kit.verifier import verifier

    if verifier(corriger=False) != 0:
        return refuser(["Les vérifications échouent. Lancez `uv run verifier`, corrigez, commitez."], "Envoi")
    return 0


def commande_interdite(commande: str) -> str | None:
    """La raison de refuser une commande shell d'un agent, ou None si elle est permise."""
    if "--no-verify" in commande:
        return "`--no-verify` contourne les règles du dépôt."
    if "core.hooksPath" in commande and DOSSIER_HOOKS not in commande:
        return "Les hooks du dépôt restent actifs : `core.hooksPath` ne change pas."
    try:
        mots = shlex.split(commande)
    except ValueError:
        mots = commande.split()
    if "git" in mots and "commit" in mots and any(re.fullmatch(r"-[a-zA-Z]*n[a-zA-Z]*", mot) for mot in mots):
        return "`git commit -n` contourne les règles du dépôt."
    return None


def garde_claude() -> int:
    """Hook PreToolUse de Claude Code : le code 2 bloque la commande et renvoie la raison à l'agent."""
    try:
        commande = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except (json.JSONDecodeError, AttributeError):
        return 0
    raison = commande_interdite(commande)
    if raison:
        print(f"Commande refusée : {raison} Corrigez ce que le hook signale (AGENTS.md).", file=sys.stderr)
        return 2
    return 0


def installer() -> bool:
    """Active les hooks du dépôt dans ce clone. Renvoie vrai s'ils viennent d'être activés."""
    if not Path(DOSSIER_HOOKS).is_dir() or git("config", "core.hooksPath") == DOSSIER_HOOKS:
        return False
    subprocess.run(["git", "config", "core.hooksPath", DOSSIER_HOOKS], check=False)
    return git("config", "core.hooksPath") == DOSSIER_HOOKS


def main() -> int:
    etape, *reste = sys.argv[1:] or ["installer"]
    if etape == "pre-commit":
        return pre_commit()
    if etape == "commit-msg":
        return commit_msg(reste[0])
    if etape == "pre-push":
        return pre_push([ligne for ligne in sys.stdin.read().splitlines() if ligne.strip()])
    if etape == "claude-bash":
        return garde_claude()
    if etape == "installer":
        installer()
        print(f"Hooks du dépôt actifs ({DOSSIER_HOOKS}/).")
        return 0
    print(f"Étape inconnue : {etape}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
