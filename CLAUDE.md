# Space Apps Kit: context for Claude

This repo prepares a team for the **NASA Space Apps Challenge 2026**, Paris local event, 14-15 Nov 2026 (theme "The Next Frontier"). Submission closes Sunday 15 Nov 23:59 Paris time.

## Hard constraints (never violate)

- **No project code before Sat 14 Nov 09:00.** This repo holds tooling, research, specs and pitch drafts only. Generic boilerplate is fine; the actual app is built during the event in a separate repo.
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

- Read `docs/team-profile.md` before recommending anything: advice must fit the team's skills and time.
- Challenge statements live in `challenges/`. If a statement is missing, ask for it rather than inventing details.
- Write outputs under `work/` (create it if needed): `work/shortlist.md`, `work/data/<challenge>.md`, `work/spec.md`, `work/pitch.md`.
- Be explicit about what is verified (from a statement, dataset or source) and what is assumed.
- Prefer small, demo-able scope: one complete user flow on real NASA data beats many partial features.
- Python: one environment managed by uv (`uv sync`, `uv run ...`); add dependencies with `uv add`, never `pip install`. Before proposing a commit, run `uv run ruff check .`, `uv run ruff format --check .` and `uv run pytest` (what CI runs).
- Never write keys or passwords in code; they go in `.env` (see `.env.example`). Team workflow (branches, PRs, commits): `CONTRIBUTING.md`.
