# Flame in Freefall: context for Claude

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

## How to work in this repo

The event has started and the app is built in this repo (see `DECISIONS.md`). The team are beginners working in French: explain simply, and write code comments, docstrings and identifiers in French (identifiers without accents).

- Read `CONTRIBUTING.md` before any edit: it assigns each folder to one role and sets the code rules. `BRIEF_EQUIPE_IA.md` holds the subject, data, pages and schedule.
- **Stay in the lane of the person you are helping.** Ask which role they have, then edit only that role's files. Shared files (`app.py`, `flame/commun/`, `pyproject.toml`, `uv.lock`, `.github/`) change only through role A.
- **Keep the contract stable**: column names in `flame/commun/constantes.py` and the functions exported by each folder's `__init__.py`. Propose changes instead of applying them.
- Logic goes in `flame/<dossier>/`, display in `pages/`. Pages read data only through `charger_fiches()`, `charger_tests()`, `charger_publications()` and the scenario through `get_scenario()`.
- **Never invent NASA data.** A missing value stays empty or `inconnu`. `data/exemples/` is fictional and labelled as such.
- Python: one environment managed by uv (`uv sync`, `uv run ...`); never `pip install`. Before proposing a commit, run `uv run verifier` (format, lint, tests: what CI runs).
- Never write keys or passwords in code: the LLM key is read from `st.secrets` (`.streamlit/secrets.toml.example`).
- Be explicit about what is verified (from a statement, dataset or source) and what is assumed.
- Prefer small, demo-able scope: one complete user flow on real NASA data beats many partial features.
- Coordinate with the other AI agents (Claude, Codex) in issue #2 "com inter agents": read it before any task, post a CLAIM before your first edit and a RELEASE when you stop.
- Prep-phase skills still live in `.claude/skills/` and write under `work/`; `/pitch-builder` and `/submission-checker` are the ones still needed.
