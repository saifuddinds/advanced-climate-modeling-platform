"""
provenance.py
-------------
Records full project provenance and runtime metadata.
Auto-detects data_mode (REAL or SYNTHETIC) from Zarr store.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import xarray as xr

from src.config import (
    PROJECT_ROOT, RAW_NC, PROCESSED_NC, ZARR_STORE,
    GLOBAL_MEANS_CSV, CLIMATE_INDICES_CSV,
    ENSEMBLE_STATS_CSV, BIAS_CORRECTED_CSV, DOWNSCALED_CSV,
    RUN_METADATA_JSON, PROVENANCE_MD, FAIR_NOTES_MD,
    METADATA_DIR, ensure_dirs
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [provenance] %(message)s")
log = logging.getLogger(__name__)


def _get_data_mode() -> str:
    try:
        ds = xr.open_zarr(str(ZARR_STORE))
        return ds.attrs.get('data_mode', 'UNKNOWN')
    except Exception:
        return 'UNKNOWN'


def run():
    ensure_dirs()
    data_mode = _get_data_mode()
    log.info(f"  data_mode detected: {data_mode}")

    metadata = {
        "project":       "Advanced Climate Modeling Platform Prototype",
        "author":        "Saif Ud Din Khan",
        "github":        "https://github.com/saifuddinds/The-Advanced-Climate-Modeling-Platform",
        "platform_style":"Pangeo-style analytics with HPC-oriented workflow",
        "run_timestamp": datetime.now().isoformat(),
        "data_mode":     data_mode,
        "model_architecture_alignment": [
            "CESM - Community Earth System Model",
            "MPAS - Model for Prediction Across Scales",
            "NEMO - Nucleus for European Modelling of the Ocean"
        ],
        "fair_alignment": {
            "Findable":      "Clear folder structure + run_metadata.json inventory",
            "Accessible":    "CSV/NetCDF/Zarr + Streamlit dashboard",
            "Interoperable": "CF-compliant NetCDF + Zarr + standard variable names",
            "Reusable":      "venv + requirements.txt + provenance tracking + Git"
        },
        "pipeline_steps": [
            {"step": 1, "name": "Data Generation",        "script": "src/generate_data.py",     "output": str(RAW_NC)},
            {"step": 2, "name": "Preprocessing",          "script": "src/preprocess.py",         "outputs": [str(PROCESSED_NC), str(ZARR_STORE)]},
            {"step": 3, "name": "Analytics",              "script": "src/analytics.py",          "output": str(GLOBAL_MEANS_CSV)},
            {"step": 4, "name": "Climate Indices",        "script": "src/climate_indices.py",    "output": str(CLIMATE_INDICES_CSV)},
            {"step": 5, "name": "Ensemble Uncertainty",   "script": "src/ensemble.py",           "output": str(ENSEMBLE_STATS_CSV)},
            {"step": 6, "name": "Bias Correction",        "script": "src/bias_correction.py",    "output": str(BIAS_CORRECTED_CSV)},
            {"step": 7, "name": "Statistical Downscaling","script": "src/downscaling.py",        "output": str(DOWNSCALED_CSV)},
            {"step": 8, "name": "Visualizations",         "script": "src/visualizations.py",     "output": "outputs/figures/*.png"},
            {"step": 9, "name": "Provenance",             "script": "src/provenance.py",         "output": str(RUN_METADATA_JSON)},
        ],
        "technology_stack": {
            "language":      "Python 3.11",
            "scientific":    ["NumPy", "Pandas", "SciPy", "Xarray", "Dask"],
            "storage":       ["NetCDF4", "h5netcdf", "Zarr"],
            "analytics":     ["scikit-learn", "statsmodels"],
            "visualization": ["Matplotlib", "Plotly", "Streamlit"]
        }
    }

    RUN_METADATA_JSON.write_text(json.dumps(metadata, indent=2))
    log.info(f"  Saved: {RUN_METADATA_JSON.name}")

    # Write fair_notes.md
    FAIR_NOTES_MD.write_text("""# FAIR Data Notes

FAIR = Findable, Accessible, Interoperable, Reusable

## Findable
Clear folder structure + meaningful file names + run_metadata.json inventory.

## Accessible
CSV/NetCDF/Zarr outputs + Streamlit dashboard (localhost:8501).

## Interoperable
CF-1.10 compliant NetCDF, Zarr chunked store, standard variable names
(air_temperature [K], precipitation_flux [mm day-1]).

## Reusable
venv, requirements.txt, documented scripts, provenance tracking, Git.
""")

    # Write provenance.md
    PROVENANCE_MD.write_text(f"""# Provenance Notes
Generated: {datetime.now().isoformat()}
Data mode: {data_mode}

## Pipeline Steps
1. src/generate_data.py   -> data/raw/synthetic_climate.nc
2. src/preprocess.py      -> data/processed/ + data/zarr/
3. src/analytics.py       -> outputs/reports/global_means.csv
4. src/climate_indices.py -> outputs/reports/climate_indices.csv
5. src/ensemble.py        -> data/processed/ensemble_member_*.nc
6. src/bias_correction.py -> outputs/reports/bias_corrected.csv
7. src/downscaling.py     -> outputs/reports/downscaled_station.csv
8. src/visualizations.py  -> outputs/figures/*.png
9. src/provenance.py      -> metadata/run_metadata.json

## Data Mode: {data_mode}
{'Real ERA5 data was used as input.' if data_mode == 'REAL' else 'Synthetic data was used (no ERA5 file found in data/raw/).'}
""")

    log.info("Provenance complete.")
    return metadata


if __name__ == "__main__":
    run()
