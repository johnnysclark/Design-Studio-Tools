from site_dossier.fetchers.climate import fetch_climate
from site_dossier.fetchers.demographics import fetch_demographics
from site_dossier.fetchers.sun import fetch_sun
from site_dossier.fetchers.wind import fetch_wind
from site_dossier.fetchers.zoning import fetch_zoning

__all__ = [
    "fetch_climate",
    "fetch_demographics",
    "fetch_sun",
    "fetch_wind",
    "fetch_zoning",
]
