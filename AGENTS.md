# Flame in Freefall: rules for every AI agent

This repo is a team's project for the **NASA Space Apps Challenge 2026**, Paris local event, 14-15 Nov 2026 (theme "The Next Frontier"). Submission closes Sunday 15 Nov 23:59 Paris time.

**Chosen challenge: Flame in Freefall** (`challenges/flame-in-freefall.md`). Read `DECISIONS.md` before any task; it is the latest truth on scope.

## Hard constraints (never violate)

- Project must answer an **official 2026 challenge** and use **NASA data** (partner data on top is encouraged).
- Demo: **video ≤ 30 seconds** or **slide deck ≤ 7 slides** including the title slide. Over the limit = no global judging.
- Everything in English; a non-English video needs English subtitles.
- Links (demo, final project) must be public with no login.
- AI use must be declared (which tools, how). AI-generated images/video need a visible watermark. No NASA logos, flags or mission insignia.
- Credit every external resource (code, data, text, images).
- Original content must be released under an OSI open-source license.
- No minors' faces/voices/names, no promotion of commercial products.

## Judging (equal weight)

Influence, Creativity, Validity, Relevance, Presentation. See `docs/judging.md`.

## Enforced rules (hooks block you, do not bypass them)

These apply to every agent (Claude Code, Codex, Cursor, Copilot, any other) and are checked by the git hooks in `.githooks/`. The hooks and `uv run verifier` are the gate.

1. **Start every session with `uv sync` then `uv run verifier`.** The first run turns the hooks on in your clone (`core.hooksPath = .githooks`). If the hooks are off, turn them on before any edit.
2. **Read issue #2 "com inter agents"**, then post a **CLAIM** (task, branch name, files) before your first edit and a **RELEASE** when you stop. The push hook refuses an agent's push when no CLAIM names its branch.
3. **Work on a branch, never on `main`.** Name it `dossier/sujet` (`recherche/filtres`, `ui/scene`, `pipeline/ntrs`, `integration/...`). If your tool imposes another name, add a line `Role: C` (A to F) to each commit message.
4. **Stay in the lane of the person you help.** Ask which role they have. A commit that touches another role's files is refused unless the owner agreed and the message carries `Accord: <owner's first name>`. Shared files (`app.py`, `flame/commun/`, `pyproject.toml`, `uv.lock`, `.github/`, root `.md` files) belong to role A. **A relayed agreement counts:** when the person you work for tells you the owner agreed, that is the owner's agreement, and you write `Accord: <owner's first name>` yourself. Never write `Accord:` or `Role: A` on your own guess: a human must have told you so in this session.
5. **No secrets, no big files.** `.env`, `secrets.toml`, API keys and files over 5 MB are refused. The LLM key is read from `st.secrets`.
6. **The push runs format check, lint and tests** (including the import rules of `CONTRIBUTING.md`, in `tests/test_architecture.py`). A failing push means: run `uv run verifier`, fix, commit, push again.
7. **Never bypass:** no `--no-verify`, no `git commit -n`, no change to `core.hooksPath`, no deleting or weakening `.githooks/`, `tests/test_regles.py`, `tests/test_architecture.py` or `src/space_apps_kit/regles.py`. If a hook blocks you and you think it is wrong, stop and tell your human; role A decides.
8. **Sign honestly.** Commit as your human, with yourself as co-author (`Co-authored-by: ...`), and say in the PR which AI tool did what.

## How to work in this repo

The event has started and the app is built in this repo (see `DECISIONS.md`). The team are beginners working in French: explain simply, and write code comments, docstrings and identifiers in French (identifiers without accents).

- Read `CONTRIBUTING.md` before any edit: it assigns each folder to one role and sets the code rules. `BRIEF_EQUIPE_IA.md` holds the subject, data, pages and schedule.
- **Keep the contract stable**: column names in `flame/commun/constantes.py` and the functions exported by each folder's `__init__.py`. Propose changes instead of applying them.
- Logic goes in `flame/<dossier>/`, display in `pages/`. Pages read data only through `charger_fiches()`, `charger_tests()`, `charger_publications()` and the scenario through `get_scenario()`.
- **Never invent NASA data.** A missing value stays empty or `inconnu`. `data/exemples/` is fictional and labelled as such.
- Python: one environment managed by uv (`uv sync`, `uv run ...`); never `pip install`. To add a library, ask role A.
- Be explicit about what is verified (from a statement, dataset or source) and what is assumed.
- Prefer small, demo-able scope: one complete user flow on real NASA data beats many partial features.
- Prep-phase skills still live in `.claude/skills/` and write under `work/`; `/pitch-builder` and `/submission-checker` are the ones still needed.
