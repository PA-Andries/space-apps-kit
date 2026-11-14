# Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data

**Our chosen challenge** (decided 13 Nov 2026, see `DECISIONS.md`).

- Level: Intermediate / Advanced
- Subject: Space Exploration
- URL: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/
- Status: **summary only, from a secondary source.** The Space Apps site blocks automated readers, so the official text below has not been checked. A human must paste the full statement here before the spec is frozen.

## Summary

From an independent mirror (https://spacedata.swapniltamse.com/challenges/flame-in-freefall/), not the official wording: build a dashboard, powered by AI, that summarizes, ranks and explains decades of NASA microgravity combustion results to inform fire safety for Moon and Mars missions. Some teams quote the title as "AI-Powered" instead of "SI-Powered".

## Objectives

<paste the official objectives; check whether they favour literature summarization, quantitative flammability prediction, or both>

## Potential considerations

<paste>

## Listed resources and datasets

| Name | Provider | URL | Notes |
|---|---|---|---|
| NTRS (NASA Technical Reports Server) | NASA | https://ntrs.nasa.gov/api/openapi/ | Open JSON API, no key. About 1,077 records for "microgravity combustion". Full text available for most records. |
| PSI (Physical Sciences Informatics) | NASA | https://psi.nasa.gov/physci/repo/search?q=&data_source=psi&data_type=investigation | Raw ISS experiment data (FLEX, BASS-II, Saffire, ACME...). No public API, manual downloads. Registration: https://psiuserregistration.ndc.nasa.gov/ |

Not yet checked against the official list: any partner (ESA, CNES, JAXA) resources.

## Our notes

- First impression: a generic "AI dashboard over NTRS" is the obvious entry, and other local events have already shipped several. To stand out, pair one quantitative dataset (FLEX droplet tests or BASS-II burn/extinguish results) with cited NTRS evidence.
- Possible angle: show where tested conditions end and refuse to guess outside them, flagging the research gaps.
- Possible user: a habitat designer choosing a cabin oxygen level for an Artemis mission.
- Data prep notes: kept in the team's shared project files under `research/flame-in-freefall/`. Findings that code depends on go in `work/data/flame-in-freefall.md` with `/data-recon`.
