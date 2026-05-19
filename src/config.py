"""
config.py
---------
Central path and settings configuration.
Change TIME_START/TIME_END here when using real ERA5 data.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR      = PROJECT_ROOT / "data"
RAW_DIR       = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
ZARR_DIR      = DATA_DIR / "zarr"

OUTPUTS_DIR   = PROJECT_ROOT / "outputs"
FIGURES_DIR   = OUTPUTS_DIR / "figures"
REPORTS_DIR   = OUTPUTS_DIR / "reports"

METADATA_DIR  = PROJECT_ROOT / "metadata"
LOGS_DIR      = PROJECT_ROOT / "logs"

RAW_NC        = RAW_DIR       / "synthetic_climate.nc"
PROCESSED_NC  = PROCESSED_DIR / "processed_climate.nc"
ZARR_STORE    = ZARR_DIR      / "processed_climate.zarr"

GLOBAL_MEANS_CSV    = REPORTS_DIR / "global_means.csv"
CLIMATE_INDICES_CSV = REPORTS_DIR / "climate_indices.csv"
ENSEMBLE_STATS_CSV  = REPORTS_DIR / "ensemble_stats.csv"
BIAS_CORRECTED_CSV  = REPORTS_DIR / "bias_corrected.csv"
DOWNSCALED_CSV      = REPORTS_DIR / "downscaled_station.csv"

FIG_GLOBAL_TEMP     = FIGURES_DIR / "annual_mean_temperature.png"
FIG_GLOBAL_PRECIP   = FIGURES_DIR / "annual_total_precipitation.png"
FIG_HEATWAVE        = FIGURES_DIR / "heatwave_days.png"
FIG_HEAVY_RAIN      = FIGURES_DIR / "heavy_rain_days.png"
FIG_TREND           = FIGURES_DIR / "tas_trend_map.png"
FIG_ANOMALY         = FIGURES_DIR / "tas_anomaly_snapshot.png"
FIG_ENSEMBLE_MEAN   = FIGURES_DIR / "ensemble_mean_temperature.png"
FIG_ENSEMBLE_SPREAD = FIGURES_DIR / "ensemble_temperature_spread.png"
FIG_BIAS_CORRECTED  = FIGURES_DIR / "bias_correction_comparison.png"
FIG_DOWNSCALING     = FIGURES_DIR / "downscaling_comparison.png"

FAIR_NOTES_MD    = METADATA_DIR / "fair_notes.md"
PROVENANCE_MD    = METADATA_DIR / "provenance.md"
RUN_METADATA_JSON = METADATA_DIR / "run_metadata.json"

# ── Dataset parameters ───────────────────────────────────────────────────────
# REAL DATA: Change TIME_START and TIME_END to match your ERA5 download range
# Example: TIME_START        = "2018-01-01"
RANDOM_SEED       = 42
TIME_START        = "2018-01-01"
TIME_END          = "2024-12-31"
LAT_MIN, LAT_MAX  = -60, 60
LAT_STEPS         = 61
LON_MIN, LON_MAX  = 0, 357.5
LON_STEPS         = 144
N_ENSEMBLE        = 5

CHUNKS = {"time": 12, "lat": 20, "lon": 20}


def ensure_dirs():
    for d in [RAW_DIR, PROCESSED_DIR, ZARR_DIR,
              FIGURES_DIR, REPORTS_DIR, METADATA_DIR, LOGS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    ensure_dirs()
    print(f"Project root: {PROJECT_ROOT}")
