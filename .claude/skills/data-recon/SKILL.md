---
name: data-recon
description: Find, sample and document the NASA and partner datasets for one Space Apps challenge, producing a data cheat sheet the team can code against on the weekend. Use after a challenge is shortlisted.
---

# Data recon

Data wrangling is what sinks hackathon teams on Saturday afternoon. This skill removes that risk before the event.

## Input

A challenge name (argument). Read its file in `challenges/` and `docs/data-portals.md`.

## Procedure

1. **List candidate datasets**: every dataset named in the statement first, then relevant ones from `docs/data-portals.md`. For each: name, provider, URL, access method (direct download, API, Earthdata Login, STAC), format, spatial/temporal resolution and coverage, approximate size.
2. **Sample it** (allowed prep, not project code): in a scratch folder, download the smallest useful slice (one tile, one day, one region) and load it in Python. Typical loaders:
   - NetCDF/HDF5: `xarray.open_dataset`
   - GeoTIFF/COG: `rasterio` or `rioxarray`
   - Earthdata collections: `earthaccess.search_data` then `earthaccess.download`
   - CSV/JSON APIs: `pandas` / `requests`
   Record the exact code that worked and any errors.
3. **Document the gotchas**: units, fill values, scale factors, projection/CRS, time zone, gaps, rate limits, login requirements, licence and citation text.
4. **Pick the minimal set**: the 1-3 datasets the MVP really needs, and a pre-downloaded subset to bring on the weekend in case the venue Wi-Fi is bad.
5. **Validity hooks**: note how a judge could check the science (reference values, a known event to reproduce, a published paper).

## Output

Write `work/data/<challenge-slug>.md` using `templates/data-cheatsheet.md`. Don't commit large data files; store the download commands instead.

Finish by telling the user which datasets are confirmed loadable and which are risky.
