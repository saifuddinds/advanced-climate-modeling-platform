# Provenance Notes

## Purpose
This file records the complete data lineage of the project — which script
created each output, from which input, and why.

---

## Step 1: Synthetic Data Generation
- **Script**  : `src/generate_data.py`
- **Output**  : `data/raw/synthetic_climate.nc`
- **Method**  : NumPy random generation with physical structure
- **Variables**: tas (K), pr (mm day-1), sfcWind (m s-1)
- **Period**  : 2000-01 to 2004-12 (monthly, 60 time steps)
- **Grid**    : 61 × 144 (lat × lon)

## Step 2: Preprocessing
- **Script**  : `src/preprocess.py`
- **Input**   : `data/raw/synthetic_climate.nc`
- **Outputs** :
  - `data/processed/processed_climate.nc`
  - `data/zarr/processed_climate.zarr`
- **Method**  : Sort by time, apply Dask chunks {time:12, lat:20, lon:20}

## Step 3: Analytics
- **Script**  : `src/analytics.py`
- **Input**   : `data/zarr/processed_climate.zarr`
- **Output**  : `outputs/reports/global_means.csv`
- **Method**  : Cosine-latitude weighted global mean, monthly climatology, anomalies

## Step 4: Climate Indices
- **Script**  : `src/climate_indices.py`
- **Input**   : `data/zarr/processed_climate.zarr`
- **Output**  : `outputs/reports/climate_indices.csv`
- **Method**  : 95th percentile extremes, linear trend (polyfit)

## Step 5: Ensemble
- **Script**  : `src/ensemble.py`
- **Inputs**  : Config parameters (seed-based generation)
- **Outputs** :
  - `data/processed/ensemble_member_1..5.nc`
  - `outputs/reports/ensemble_stats.csv`
- **Method**  : 5 members, unique seeds, ensemble mean/std/SNR

## Step 6: Bias Correction
- **Script**  : `src/bias_correction.py`
- **Input**   : `data/zarr/processed_climate.zarr`
- **Output**  : `outputs/reports/bias_corrected.csv`
- **Method**  : Monthly delta bias correction, baseline 2000-2002

## Step 7: Statistical Downscaling
- **Script**  : `src/downscaling.py`
- **Input**   : `data/zarr/processed_climate.zarr`
- **Output**  : `outputs/reports/downscaled_station.csv`
- **Method**  : scikit-learn LinearRegression, train 2000-2002, predict 2003-2004

## Step 8: Visualizations
- **Script**  : `src/visualizations.py`
- **Inputs**  : CSV reports + Zarr store
- **Output**  : `outputs/figures/*.png` (10 figures)

## Step 9: Provenance
- **Script**  : `src/provenance.py`
- **Output**  : `metadata/run_metadata.json`
- **Notes**   : Full pipeline metadata, FAIR alignment record

---

## Final Provenance Statement
Each major output is fully traceable to:
- a source script
- an input dataset
- a documented transformation
- a timestamp

This satisfies the **Reusable** principle of FAIR data management and
supports full scientific reproducibility.
