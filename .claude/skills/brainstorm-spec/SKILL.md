---
name: brainstorm-spec
description: Run a guided brainstorm for the chosen Space Apps challenge and freeze a one-page spec built around the five judging criteria, a target award and a 48-hour MVP. Use once a challenge is chosen.
---

# Brainstorm to spec

Produce a spec a team of 4-6 can build in 48 hours and that scores on all five criteria.

## Inputs

`docs/team-profile.md`, the challenge file in `challenges/`, `work/shortlist.md` and `work/data/*.md` if they exist, `docs/judging.md`.

## Procedure

Ask the questions **one at a time**, wait for the answer, and push back when an answer is vague. Offer 2-3 concrete options with each question so the user can just pick.

1. **User**: who exactly uses this? (A named persona: "a cereal farmer in Beauce", "a 12-year-old in a school club".) Have we spoken to one?
2. **Problem**: what do they struggle with today, in one sentence, and how do they cope now?
3. **Insight**: what does NASA data reveal that they can't see today?
4. **Core flow**: what is the one thing they do in our product, from opening it to getting value? Describe it in 3-5 steps.
5. **Wow moment**: what will look impressive in the first 10 seconds of the video?
6. **Data**: which datasets power the core flow (from data-recon)? What's pre-processed vs live?
7. **Validity**: how do we show the science is sound (method, assumptions, limits, sanity check)?
8. **Creativity**: what exists already, and what's our angle that doesn't?
9. **Influence**: who benefits beyond the first user, and at what scale? Any local Paris/France case?
10. **Target award**: which global award, and what does that change in the design?

Then generate 3 alternative concepts that answer the same user/problem differently, compare them quickly against the criteria, and let the user choose or merge.

## Spec rules

- MVP = the core flow working end to end on real NASA data, deployed at a public URL.
- Everything else is a stretch goal, ordered by value to the video.
- Each team member gets an owner role.
- Add a timeline for the weekend with a feature freeze on Sunday midday.

## Output

Write `work/spec.md` from `templates/spec.md`. End by listing the open questions and the 3 riskiest assumptions to test before the event.

Reminder: the spec, mockups and research are allowed prep. The product code is written from Saturday 09:00.
