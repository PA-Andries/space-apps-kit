# Where the data lives

Start from the datasets named in the challenge statement. These portals cover most of the rest.

## NASA Earth science

| Portal | What | Access |
|---|---|---|
| Earthdata Search (search.earthdata.nasa.gov) | Catalogue of all NASA Earth science data | Free Earthdata Login; Python: `earthaccess` |
| Worldview (worldview.earthdata.nasa.gov) | Browse satellite imagery by date, export | Web; tiles via GIBS |
| GIBS | Imagery tiles (WMTS) for maps | Direct in Leaflet/MapLibre/Cesium |
| ASF Data Search (search.asf.alaska.edu) | SAR data incl. NISAR, Sentinel-1 | Earthdata Login |
| Giovanni | Quick time series and maps of atmospheric/climate variables | Web |
| EONET (via api.nasa.gov) | Natural events (fires, storms, volcanoes) | JSON API |
| SMAP, MODIS, VIIRS, GPM, Landsat (via Earthdata/USGS) | Soil moisture, vegetation, fires, precipitation, land imagery | Earthdata/USGS |

## Planetary and space

| Portal | What | Access |
|---|---|---|
| NASA Trek (trek.nasa.gov: Moon, Mars) | Map layers, elevation, landing sites | Web + WMTS |
| PDS (pds.nasa.gov) | Planetary mission archives | Direct download |
| NASA Exoplanet Archive | Exoplanet catalogues, light curves | TAP/API |
| OSDR (osdr.nasa.gov) | Space biology and astronaut-related omics data | Web/API |
| NASA Image and Video Library (images.nasa.gov) | Media (check usage guidelines; no logos) | API |
| api.nasa.gov | APOD, EONET, Mars rover photos, etc. | Free API key |

## Partners and other open data

- ESA / Copernicus (Sentinel, Copernicus Data Space Ecosystem), CNES, JAXA, ISRO, CSA, UK Space Agency and the other Space Apps partner agencies.
- France: data.gouv.fr, Météo-France open data, IGN Géoplateforme, Paris open data (useful for a local angle).

## Python stack for sampling

`earthaccess`, `xarray`, `netCDF4`/`h5netcdf`, `rioxarray`/`rasterio`, `pystac-client`, `geopandas`, `pandas`, `matplotlib`. Installed with `uv sync --group data` (see `pyproject.toml`).
