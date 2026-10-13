# Space Apps Kit

The team's shared repo for the **NASA Space Apps Challenge 2026** (Paris local event, 14-15 Nov 2026): Claude Code skills, the rules that matter, and a submission checker, on a clean Python setup.

It contains **no project code**. The project itself is built from Saturday 14 Nov 09:00 (see `CLAUDE.md`).

## Setup

Needs [uv](https://docs.astral.sh/uv/getting-started/installation/) and, for the skills, [Claude Code](https://code.claude.com).

```bash
git clone https://github.com/PA-Andries/space-apps-kit && cd space-apps-kit
uv sync                 # one shared environment (.venv) from uv.lock: Python 3.12 + dev tools
uv sync --group data    # add the NASA data stack (earthaccess, xarray, geopandas...) when you need it
cp .env.example .env    # Earthdata and api.nasa.gov credentials, never committed
claude                  # picks up CLAUDE.md and .claude/skills automatically
```

## Workflow

| When | Step | Skill |
|---|---|---|
| Now | Fill in the team profile | `docs/team-profile.md` |
| 28 Oct (statements out) | One file per challenge in `challenges/` | `challenges/_template.md` |
| 28 Oct → 1 Nov | Rank challenges against the team | `/challenge-scout` |
| 1 Nov → 13 Nov | Find and document the datasets | `/data-recon` |
| 1 Nov → 13 Nov | Brainstorm and freeze a one-page spec | `/brainstorm-spec` |
| 1 Nov → 15 Nov | 30-second video script and 7-slide fallback | `/pitch-builder` |
| Sunday 15 Nov | Check page, links and demo before submitting | `/submission-checker` |

Each skill is a readable Markdown procedure in `.claude/skills/<name>/SKILL.md`, next to the templates it fills in, so teammates without Claude Code can follow it by hand.

## Layout

```
CLAUDE.md                   rules and context loaded in every Claude session
CONTRIBUTING.md             how we work: environment, checks, branches, PRs, commits
.claude/skills/             the five skills, each with its templates
.claude/settings.json       shared Claude Code permissions
docs/                       rules, judging criteria, team profile
challenges/                 one file per official challenge statement
work/                       outputs of the skills (shortlist, data notes, spec, pitch)
src/space_apps_kit/         shared Python tooling (check-submission)
tests/                      tests for that tooling
pyproject.toml, uv.lock     dependencies, pinned for everyone
.github/workflows/ci.yml    quality check on every PR: ruff lint, ruff format, pytest
```

## License

MIT. The hackathon project must also use an OSI open-source license (see `docs/rules.md`).
