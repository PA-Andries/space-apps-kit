# Flame in Freefall: shared dashboard dataset (v0.2, 14 Nov 2026)

One small dataset (about 6 MB) that every team member can copy and that the dashboard reads. Built only from NASA PSI
(the challenge's required source) plus facts stated on the official challenge page. No raw data inside: raw data is
**mapped** so the dashboard can send a user to it.

Use whichever format suits you: the CSV files, `dataset.json` (all tables in one file), or `flame_in_freefall.sqlite`.
## Get it on any machine

From the root of the repo:

```bash
uv run python -m flame.pipeline.psi_telecharger   # about 330 MB from PSI into data/raw/psi_mirror, dataset into data/raw/psi_dataset
```

The script asks PSI's open API (no key, no login) for the 24 combustion investigations, downloads their experiment
tables, metadata, Reports and Science Documents, lists the raw data without downloading it, and builds every table
below. Adding `--tables-only` downloads about 5 MB instead (the `documents` table is then nearly empty).
Re-running skips files already present. `data/raw/` is ignored by git: only the scripts are in the repo.
Status: the download logic was tested against a local replay of the PSI API, and the same API calls were used by hand
on 14 Nov 2026. It has not yet been run end to end against psi.nasa.gov, which the build machine's network blocks.

Then, from the repo with uv:

```bash
uv run python -m flame.pipeline.psi_contrat --verifie-par <prénom>   # data/investigations.csv, data/tests.csv, data/psi/*.csv
uv run python -m flame.pipeline.psi_textes                          # full text of every report: data/psi/textes/
```

`psi_textes` writes one text file per report and NASA document (PDF, Word) under `data/psi/textes/<PSI-n>/` and
an index `data/psi/textes.csv` (investigation, category, source file, text file, pages, characters). About 7 MB of
text for 98 documents. A scanned PDF gives an almost empty text, which shows in `caracteres`. Old `.doc` files are
read on a best-effort basis.

To rebuild from an existing mirror: `uv run python flame/pipeline/psi_construire.py <psi_mirror_folder> <output_folder>`.

## Tables

| Table | Rows | One row is | Main use in the dashboard |
|---|---|---|---|
| `investigations` | 24 | a PSI combustion investigation (19 flight, 5 ground) | Catalogue, ranking, comparison |
| `tests` | 1,989 | a row of a PSI "Experimental Table", harmonised | Filter by fuel, oxygen, pressure, airflow; export for modelling |
| `hardware_families` | 6 | a hardware group | "Same hardware" grouping |
| `relations` | 32 | a link between investigations or to a theme | Graph: related work, reused data, shared instruments |
| `habitats` | 6 | a crew environment (ISS, suit, Moon Base, rover, Mars) | "Relevant to my habitat" view, coverage gaps |
| `publications` | 352 | a paper listed by PSI for an investigation | Evidence, citations |
| `documents` | 192 | a report or document in the local mirror | Sources for AI summaries; link to open the PDF |
| `raw_data_map` | 24 | where the raw data of an investigation lives | Redirect users to raw data, with size and API recipe |
| `resources` | 10 | an official challenge resource | Home page, Earth benefits page |
| `measurements` | 163 | an instrument or measurement type of one investigation, with its source document | "What was measured and how" panel, comparison of sensors |
| `raw_files` | about 79,000 | one raw or calibration file on PSI (only present after `psi_telecharger.py`) | Per-file redirect to raw data |
| `relevance` | 120 | an investigation scored for one habitat | **The ranking shown after the user picks a habitat** |

### `investigations` columns
- Identity: `investigation_id` (PSI-25), `acronym`, `title`, `one_liner`, `project_type`, `flight_platform`, `start_date`, `end_date`, `doi`, `license`, `psi_url`.
- Classification: `hardware_family`, `facility`, `hardware_psi`, `fuel_phase` (solid, liquid droplet, gas, smoke aerosol), `fire_safety_pillar` (Prevention, Detection, Suppression, Fundamental), `cited_in_statement_as_fire_safety` (1/0), `team_priority` (1 to 3), `related_investigations`.
- Computed from `tests`: `n_table_rows`, `row_levels`, `fuels`, `n_distinct_fuels`, `o2_pct_min/max`, `pressure_atm_min/max`, `flow_cm_s_min/max`, `recorded_variables` (all column names of its experiment tables).
- PSI text: `objectives`, `approach`, `hypothesis`, `impacts_earth_benefits`, `n_publications`.
- Raw data: `psi_total_files`, `raw_data_files`, `raw_data_gb`.

### `tests` columns
`investigation_id`, `acronym`, `source_table`, `row_level`, `test_id`, `date`, `fuel`, `fuel_form`, `o2_pct_min`, `o2_pct_max`,
`pressure_atm_min`, `pressure_atm_max`, `flow_cm_s_min`, `flow_cm_s_max`, `flow_direction`, `diluent`, `outcome`, `burn_time_s`,
`n_flames`, `notes`, `raw_data_url`, `original_row_json`.

- **`row_level` matters.** PSI tables are not all at the same grain: `test` (one burn), `sample`, `test day` (several flames
  ignited that day, see `n_flames`), `session`, `planned condition set` (FLEX-2: ranges from the test matrix, not runs),
  `published data item` (PSI-142). Do not count rows across levels as "number of tests" without saying so.
- min = max when the source gives a single value. Blank = not in PSI's table (not zero).
- `original_row_json` keeps every original column and value untouched, so nothing is lost by the harmonisation.

## How the ranking works (`relevance`)

The user picks a habitat (space station, spacecraft, Moon Base, pressurized rover, Mars base). Filter `relevance`
on it and sort by `rank`. There is one row per habitat and investigation (120 rows). Each row carries its `score`
(0 to 100), the parts of the score, and a plain-English `why`.

`score = 60 x atmosphere_fit + 20 x gravity_fit + 20 x cited_in_statement`

PA's decision of 14 Nov 2026: **the fire-safety pillars (prevent, detect, react) are dropped.** The table has no
category any more and `categories.csv` is gone. The three parts of the score keep the proportions they had before
(30, 10, 10), brought back to 100. Many investigations tie, and ties are broken by `investigation_id`: the site's own
ranking (role C) is the one shown to the user.

- `atmosphere_fit`: **computed from `tests`**. Station and spacecraft: rows at 19-23% O2. Moon Base and rover: rows at
  30% O2 or more and at 0.694 atm (10.2 psi) or less score 1; high oxygen only 0.7; reduced pressure only 0.3.
  Mars base: empty for every investigation, because the statement gives no atmosphere for Mars; the score then
  counts gravity and the citation only.
- `gravity_fit`: microgravity flight data fits a station fully. For the Moon and Mars, PSI has no partial-gravity data:
  E-FIELD Flames scores 1 (the statement says it mimics partial gravity), Saffire-II 0.6 (has 1-g and microgravity
  results), other flight data 0.4.
- `cited_in_statement`: 1 if the statement names it as fire-safety work.

To show in the UI: spacecraft and station cabin air is an assumption, and the Mars base atmosphere is unknown; the
statement gives neither (`atmosphere_source` says so). The weights 60/20/20 are a starting point, easy to change in
the script.

## Where each value comes from (verified vs chosen by us)

| Kind | Columns | Source |
|---|---|---|
| NASA data, untouched | `original_row_json`, `objectives`, `approach`, `hypothesis`, `impacts_earth_benefits`, `publications.*`, `doi`, dates | PSI experiment tables and PSI metadata files |
| NASA data, converted | `o2_pct_*` (mole fraction x 100), `pressure_atm_*` (mmHg / 760, bar / 1.01325), `flow_cm_s_*`, `fuel`, `diluent`, `outcome`, `burn_time_s` | Computed by `psi_construire.py` from the same tables |
| Official statement | `hardware_families`, `habitats` atmosphere values, statement-sourced `relations`, `cited_in_statement_as_fire_safety`, `resources` | Challenge page, Details and Resources tabs |
| Team judgement, to validate | `fire_safety_pillar`, `team_priority`, `one_liner`, `fuel_phase` | Proposed by the team (Hugo's guide) and Claude. Not NASA's classification |
| Read on PSI on 14 Nov 2026 | `raw_data_gb`, `raw_data_files`, `psi_total_files` | PSI file listings |

Known quirks handled: FLEX column headers lost their subscripts in PSI's CSV (O = O2, N = N2, CO = CO2). FLEX test 114
has pressure 0 in the source (treated as missing). ACME BRE has two oxygen values stored as "3400%" and "2100%" (read as
34 and 21). Saffire "pre-test flow visualisation" rows are dropped. SPICE has a few negative air rates, kept as recorded.
`habitats.gravity_g` and the ISS row are general knowledge, not from the statement: cite a source before showing them.

## Coverage of the challenge's "potential considerations"

| Consideration | Covered by | Status |
|---|---|---|
| Experimental objectives | `investigations.objectives`, `approach`, `hypothesis`, `one_liner` | Yes, all 24 |
| Fuels, shape and size of samples or burners | `tests.fuel`, `tests.fuel_form`, `investigations.fuels`, `fuel_phase` | Yes where PSI's table gives it. Sample size is free text in `fuel` / `fuel_form` (e.g. "100 micron PMMA film 2 cm wide") |
| Test conditions: oxygen, airflow | `tests.o2_pct_*`, `flow_cm_s_*`, `pressure_atm_*`, `diluent`, `flow_direction` | Mostly. Oxygen for 1192 rows, pressure 1046, airflow 807. BASS-II airflow comes from its "Air display" column (cm/s per NASA's data FAQ); BASS airflow from NASA's as-run test matrix spreadsheet. Still missing: oxygen for BASS (not logged; its requirements document restricts tests to cabin air at 21% O2 or above) and for SAME |
| Variables: how tests of one investigation differ | `tests` grouped by investigation; `investigations.recorded_variables` and min/max ranges | Yes. The dashboard can compute "what varies" as the columns with more than one value |
| Sensors or types of measurements | `measurements` (instrument, what it measures, unit, source document, basis) | Yes, all 24. Read from NASA's Reports and Science Documents. `basis` says whether the instrument is described in a document of that investigation (`document`), for a sister investigation on the same hardware (`shared hardware`), or only in PSI's Approach text (`PSI metadata`). It lists instrument types, not time series: sensor readings themselves are raw data |
| Similarities and differences between investigations | `investigations` (same columns for all), `hardware_families`, `relations` | Yes |
| DAFT reused a SAME instrument | `relations` | Yes |
| ACME BRE is a materials flammability study | `relations`, `one_liner`, `cited_in_statement_as_fire_safety` | Yes |
| Other, less directly relevant investigations | `team_priority` 2 and 3, `fire_safety_pillar` = Fundamental | Yes |
| Hardware families (ACME / MDCA / MSG duct) | `hardware_families`, `investigations.hardware_family` | Yes |
| Spacesuits and oxygen; Moon Base at 30% O2 or more | `habitats`, with test counts at or above each habitat's oxygen level | Yes. Finding: 509 table rows at 30% O2 or more, all gas or droplet flames. **No solid-material test at 30% O2 in PSI's tables** |
| CFI-G has the highest-oxygen tests (85%) | `tests` for PSI-159 (max 85%), `relations` | Yes, confirmed in the data. ACME Flame Design (PSI-10) also reaches 85% |
| No partial-gravity data; E-FIELD Flames mimics it | `relations`, `habitats.note` | Yes (as a stated gap) |
| Microgravity vs normal gravity bounds | Saffire-II rows keep 1-g and microgravity burn lengths in `outcome` / `original_row_json` | Partial. Only Saffire-II has both in its table |

Objectives of the statement: (1) relevant investigations per habitat = `investigations` + `habitats`; (2) data for
predictive modelling = `tests` + `raw_data_map`; (3) research for next-generation equipment = `fire_safety_pillar`,
`impacts_earth_benefits`, `publications`. Optional Earth benefits = `resources` (kind `earth_benefit`).

## Raw data mapping

`raw_data_map` gives, per investigation: size and file count of the raw data, the PSI page where it sits, and the two
open API calls to list and download files. The map is per investigation (and every `tests` row carries
`raw_data_url`). `psi_telecharger.py` also saves PSI's complete file listing, so a dataset built with it has a `raw_files`
table: one row per raw or calibration file with its folder path (`key`), size and PSI page.

## What changed in v0.2

- New `measurements` table (sensors and measurement types for all 24 investigations, each with its source document).
- Airflow added for BASS and BASS-II; burn time, burning rates, extinction diameter and PI comments added for CFI from NASA's data summary spreadsheet (see `notes` and `original_row_json`).
- New `psi_telecharger.py`: one command to download the sources and build the dataset on any machine.

## Credits

NASA Physical Sciences Informatics (PSI), CC0-1.0. Cite each investigation by its DOI (`investigations.doi`).
Dataset assembled with AI assistance (Claude); declare it in the submission.
