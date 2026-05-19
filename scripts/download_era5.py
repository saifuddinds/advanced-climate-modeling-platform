"""
download_era5.py
----------------
Downloads ERA5 monthly reanalysis data from Copernicus CDS.

SETUP (one time only):
  1. Register free account: https://cds.climate.copernicus.eu
  2. Get your API key from: https://cds.climate.copernicus.eu/api-how-to
  3. Create file ~/.cdsapirc with:
        url: https://cds.climate.copernicus.eu/api/v2
        key: YOUR-UID:YOUR-API-KEY

USAGE:
  pip install cdsapi
  python scripts/download_era5.py

OUTPUT:
  data/raw/era5_climate.nc
  (pipeline auto-detects it next time you run python -m src.pipeline)
"""

from pathlib import Path

# ── USER SETTINGS — change these ─────────────────────────────────────────────
YEAR_START = 2000
YEAR_END   = 2023
# Area bounding box [North, West, South, East]
# Global: [90, -180, -90, 180]
# Pakistan + South Asia: [40, 55, 20, 80]
AREA = [60, -180, -60, 180]
OUTPUT_FILE = "data/raw/era5_climate.nc"
# ─────────────────────────────────────────────────────────────────────────────


def download():
    try:
        import cdsapi
    except ImportError:
        print("ERROR: cdsapi not installed.")
        print("Run: pip install cdsapi")
        return

    Path("data/raw").mkdir(parents=True, exist_ok=True)

    c = cdsapi.Client()

    print(f"Downloading ERA5 monthly data: {YEAR_START}-{YEAR_END}")
    print(f"Area: {AREA}")
    print(f"Output: {OUTPUT_FILE}")
    print("This may take a few minutes ...")

    c.retrieve(
        'reanalysis-era5-single-levels-monthly-means',
        {
            'product_type': 'monthly_averaged_reanalysis',
            'variable': [
                '2m_temperature',       # -> tas
                'total_precipitation',  # -> pr
                '10m_wind_speed',       # -> sfcWind
            ],
            'year':  [str(y) for y in range(YEAR_START, YEAR_END + 1)],
            'month': [f'{m:02d}' for m in range(1, 13)],
            'time':  '00:00',
            'area':  AREA,
            'format': 'netcdf',
        },
        OUTPUT_FILE
    )

    print(f"\nDownload complete: {OUTPUT_FILE}")
    print("Now run the pipeline:")
    print("  python -m src.pipeline")


if __name__ == "__main__":
    download()
