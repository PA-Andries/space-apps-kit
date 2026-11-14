# Flame in Freefall

Our project for the **NASA Space Apps Challenge 2026** (Paris local event, 14-15 Nov 2026), challenge **[Flame in Freefall](challenges/flame-in-freefall.md)**: a Streamlit site that searches, compares and explains NASA microgravity combustion experiments, to inform fire safety in future space habitats.

The team works in French, so the working docs are in French. The submission (project page, video) is in English.

## Run it

Needs [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
git clone https://github.com/PA-Andries/space-apps-kit && cd space-apps-kit
uv sync                           # one shared environment (.venv) pinned by uv.lock
uv run streamlit run app.py       # the site, on http://localhost:8501
uv run verifier                   # format, lint and tests: run before every push; the first run turns the git hooks on
```

Until `data/investigations.csv` exists, the site runs on the fictional sample data in `data/exemples/` and says so on every page.

## Where to read what

| File | What it holds |
|---|---|
| `CONTRIBUTING.md` | Who owns which folder, how to send work (branch, PR, checks), code rules |
| `BRIEF_EQUIPE_IA.md` | The brief each teammate gives their AI assistant: subject, data, pages, roles, schedule |
| `GUIDE_SOURCES.md` | The NASA sources (PSI, NTRS) in detail |
| `DECISIONS.md` | What we decided and why, one line each |
| `AGENTS.md` | Rules every AI agent must follow, enforced by the git hooks in `.githooks/`; loaded by Codex and, through `CLAUDE.md`, by Claude Code |

## Layout

```
app.py                      entry point: the list of pages
pages/                      one short file per page (display only)
flame/commun/               shared contract: column names, data loading, scenario
flame/pipeline/             NTRS API client and data preparation (writes data/*.csv)
flame/recherche/            search engine and scenario score
flame/comparateur/          side-by-side comparison
flame/assistant/            help chatbot and its prompts
flame/ui/                   page frame, shared components, three.js scene
data/                       the three CSV files the site reads; data/exemples/ is fictional
tests/                      one test file per folder, plus page and data-contract checks
pitch/                      video script, subtitles, project page text
src/space_apps_kit/         team tooling: `verifier`, `regles` (the hooks' logic), `check-submission`
.claude/skills/             Claude Code skills from the prep phase, each with its templates
docs/                       event rules, judging criteria, team profile
.githooks/                  git hooks that enforce the repo rules on every commit and push (no CI on GitHub)
```

Each folder under `flame/` belongs to one role; the table is in `CONTRIBUTING.md`.

## License

MIT (see `LICENSE`). NASA data sources and AI use are credited on the project page.
