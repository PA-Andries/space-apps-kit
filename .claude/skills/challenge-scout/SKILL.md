---
name: challenge-scout
description: Rank the NASA Space Apps 2026 challenges against our team profile and produce a shortlist with data links and a target award. Use after the challenge statements are in challenges/.
---

# Challenge scout

Goal: pick **one challenge and one backup** the team can win with, not the coolest one.

## Inputs

- `docs/team-profile.md` (skills, availability, interests). If it's empty, ask the user to fill it first, or ask the 5 questions in it.
- Every file in `challenges/` except `_template.md`. If a challenge has only a summary (no full statement), say so in the output.
- `docs/judging.md` for the criteria and the 10 global awards.

## Procedure

1. For each challenge, extract: objectives, expected outputs, named datasets, difficulty level, and any "considerations" the statement lists.
2. Score it 1-5 on each axis, with one sentence of justification per score:
   - **Demo in 48h**: can the team show one complete flow on real data by Sunday afternoon?
   - **Real user**: is there a nameable user we could interview before the event?
   - **Data access**: are the datasets documented, small enough, loadable in under an hour? (Check the links; note format and size if visible.)
   - **Team fit**: does it use the team's strongest skills from the profile?
   - **Differentiation**: is there an angle most teams won't take? Propose it.
   - **Award fit**: which global award (from `docs/judging.md`) it naturally targets.
   - **Wow on screen**: will a 30-second video look good (map, 3D, sound, game, before/after)?
   - **Local angle**: is there a Paris/France use case (floods, urban heat, agriculture, subsidence...) that makes the local jury care?
3. Compute a total (equal weights unless the user says otherwise) and sort.
4. For the top 3, write: a one-line pitch, the differentiating angle, the target award, the first datasets to test, the main risk, and who on the team would own what.
5. Recommend one challenge and one backup and say why in three sentences.

## Output

Write `work/shortlist.md`:

```markdown
# Challenge shortlist (date)

## Recommendation
Main: <challenge> because ... Backup: <challenge> because ...

## Scores
| Challenge | Demo | User | Data | Fit | Diff | Award | Wow | Local | Total |
|---|---|---|---|---|---|---|---|---|---|

## Top 3 detail
### <challenge>
- Pitch:
- Angle:
- Target award:
- Datasets to test first:
- Main risk:
- Owners:
```

Then tell the user the recommendation and the next step (`/data-recon <challenge>`).
