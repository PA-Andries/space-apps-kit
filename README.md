# Space Apps Kit

A prep and execution kit for the **NASA Space Apps Challenge 2026** (Paris local event, 14-15 Nov 2026), built as Claude Code skills plus templates and a submission checker.

It contains **no project code**: it's tooling to choose a challenge, understand the data, turn a brainstorm into a spec, write the pitch, and check the submission. Project code starts on Saturday 14 Nov at 09:00 in a separate repo.

## Workflow

| When | Step | Skill / file |
|---|---|---|
| Now | Fill in the team profile | `docs/team-profile.md` |
| 28 Oct (statements out) | Paste each challenge statement into `challenges/` | `challenges/_template.md` |
| 28 Oct → 1 Nov | Rank challenges against the team | `/challenge-scout` |
| 1 Nov → 13 Nov | Find, download and document the datasets | `/data-recon` |
| 1 Nov → 13 Nov | Brainstorm and freeze a one-page spec | `/brainstorm-spec` |
| 1 Nov → 15 Nov | Write the 30-second video script, storyboard and 7-slide fallback | `/pitch-builder` |
| Sunday 15 Nov | Check the project page, links and demo before submitting | `/submission-checker` + `scripts/check_submission.py` |

## Setup

```bash
git clone <this repo> && cd space-apps-kit
claude            # Claude Code picks up CLAUDE.md and .claude/skills automatically
```

Then type `/challenge-scout`, `/data-recon <challenge>`, etc.

Without Claude Code, every skill is a readable Markdown procedure in `.claude/skills/*/SKILL.md` you can follow by hand or paste into any AI assistant.

## Layout

```
CLAUDE.md                     event rules and judging context loaded in every session
.claude/skills/               the five skills
docs/rules.md                 rules summary (submission, data, AI use, branding)
docs/judging.md               criteria, awards, past winners
docs/team-profile.md          who we are, skills, availability (fill in)
docs/data-portals.md          where NASA and partner data lives
challenges/                   one file per challenge statement (fill in on 28 Oct)
templates/                    spec, data cheat sheet, pitch, slides, project page
scripts/check_submission.py   checks the project page draft, public links and demo limits
starter/                      generic environment (Python data stack), no project code
work/                         outputs written by the skills (shortlist, specs, scripts)
```

## Rules that matter most

- Teams of 1-6, all registered at the Paris local event.
- Official challenge only, NASA data required for global awards.
- Demo: video **≤ 30 s** or **≤ 7 slides**, English (or English subtitles), public links.
- AI tools allowed but must be declared; AI images/video watermarked; no NASA logos.
- Original content must be open source.

Details and sources in `docs/rules.md`. Re-check against the 2026 Project Submission Guide released on 13 Nov.

## License

MIT for this kit. Your hackathon project must use an OSI open-source license (see `docs/rules.md`).
