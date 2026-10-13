# How we work

## Environment

One environment for everyone, defined by `pyproject.toml` and pinned in `uv.lock`.

- `uv sync` installs it into `.venv`. Run tools with `uv run <cmd>`; no manual activation or `pip install`.
- Add a dependency with `uv add <pkg>` (runtime), `uv add --group dev <pkg>` (tooling) or `uv add --group data <pkg>` (NASA data stack). Commit `pyproject.toml` and `uv.lock` together.
- Secrets go in `.env` (copied from `.env.example`), never in code or commits.

## Checks

The same three commands run in CI on every pull request. Run them before you push:

```bash
uv run ruff check .          # lint (add --fix to auto-fix)
uv run ruff format .         # format
uv run pytest                # tests
```

## Branches and pull requests

- `main` always works. Nobody pushes to it directly.
- Short branches named after your lane: `data/firms-ingest`, `app/search-screen`, `story/script-v2`.
- One feature per PR, ideally under ~300 lines. CI must be green; the integrator merges.
- Write only in your own lane's folder. Changes to someone else's files go through them.

## Commits

- Commit from your own GitHub account, with the email linked to it, so your work counts on your profile.
- When Claude wrote part of the change, add it as co-author, not author:
  `Co-authored-by: Claude <noreply@anthropic.com>`

## Event weekend (from Sat 14 Nov 09:00)

The integrator adds three shared files: `CONTRACTS.md` (data and screen interfaces, frozen Saturday morning), `DECISIONS.md` (one line per change, with time and who) and `AI_LOG.md` (one line per significant AI use, needed for the AI declaration). Every Claude session starts by reading them.
