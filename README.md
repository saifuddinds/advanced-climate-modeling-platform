# 🌍 Advanced Climate Modeling Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-red?style=for-the-badge&logo=streamlit)
![Xarray](https://img.shields.io/badge/Xarray-2023.6+-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Ubuntu%2022.04-orange?style=for-the-badge&logo=ubuntu)

**A prototype advanced climate science platform demonstrating the full workflow of a modern climate modeling and analytics system.**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Usage](#-usage) • [Real Data](#-using-real-era5-data) • [Dashboard](#-dashboard) • [Viva Guide](#-viva--exam-guide)

</div>

---

## 📌 Project Overview

This project is an educational single-node HPC-inspired climate science platform developed on Ubuntu 22.04. It demonstrates how a local environment can reproduce the core architecture of a modern climate modeling and analytics workflow used in research institutions and HPC environments.

**Two data modes supported:**
- **SYNTHETIC MODE** — Auto-generates realistic climate data. Works immediately, no downloads needed.
- **REAL DATA MODE** — Uses actual ERA5 reanalysis data from ECMWF Copernicus CDS.

> **Viva Statement:** *"This is a prototype advanced climate modeling platform that demonstrates the core layers of a modern climate-science workflow: model-layer alignment, HPC scheduling, scientific data storage, distributed analytics, uncertainty quantification, bias correction, statistical downscaling, visualization, and data publishing."*

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔄 Smart Data Loader | Auto-detects real ERA5 or generates synthetic data |
| 💾 Scientific Storage | CF-compliant NetCDF + Zarr chunked store |
| 📊 Climate Analytics | Latitude-weighted global mean, climatology, anomalies |
| 🌡️ Climate Indices | Heatwave days, heavy rainfall, linear warming trend |
| 🎲 Ensemble Analysis | 5-member ensemble with mean, std, signal-to-noise |
| 🔧 Bias Correction | Monthly delta bias correction |
| 📍 Downscaling | Statistical downscaling using LinearRegression |
| 🗺️ Spatial Maps | Interactive temperature, precipitation, wind maps |
| 📈 Dashboard | Streamlit + Plotly dark-theme interactive dashboard |
| 📋 FAIR Metadata | Provenance tracking, FAIR-aligned data practices |
| ⚙️ HPC Ready | Slurm job script for HPC cluster deployment |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  5-LAYER ARCHITECTURE                   │
├─────────────────────────────────────────────────────────┤
│  Layer 1 — MODEL LAYER                                  │
│  CESM · MPAS · NEMO  (architecture alignment)           │
├─────────────────────────────────────────────────────────┤
│  Layer 2 — HPC LAYER                                    │
│  Slurm job script · Dask distributed workers            │
├─────────────────────────────────────────────────────────┤
│  Layer 3 — DATA LAYER                                   │
│  NetCDF (CF-1.10) · Zarr chunked store                  │
├─────────────────────────────────────────────────────────┤
│  Layer 4 — ANALYTICS LAYER                              │
│  Xarray · Dask · scikit-learn · SciPy                   │
├─────────────────────────────────────────────────────────┤
│  Layer 5 — SHARING LAYER                                │
│  Streamlit · Plotly · FAIR metadata · Provenance        │
└─────────────────────────────────────────────────────────┘

Memory trick: Model → Schedule → Store → Analyze → Share
```

---

## 📁 Project Structure

```
climate_hpc_platform/
│
├── app.py                          # Streamlit + Plotly dashboard (9 pages)
├── README.md                       # This file
├── VIVA_GUIDE.md                   # 15 viva Q&A answers
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
│
├── src/                            # All Python modules
│   ├── __init__.py
│   ├── config.py                   # Central path + settings config
│   ├── generate_data.py            # Smart loader (real ERA5 or synthetic)
│   ├── preprocess.py               # Chunking + NetCDF + Zarr export
│   ├── analytics.py                # Global mean + climatology + anomalies
│   ├── climate_indices.py          # Extremes + linear trend
│   ├── ensemble.py                 # 5-member ensemble uncertainty
│   ├── bias_correction.py          # Monthly delta bias correction
│   ├── downscaling.py              # Statistical downscaling (sklearn)
│   ├── visualizations.py           # 10 Matplotlib dark-theme figures
│   ├── provenance.py               # FAIR metadata + provenance JSON
│   └── pipeline.py                 # Full automated orchestrator
│
├── data/
│   ├── raw/                        # Raw input (ERA5 .nc or synthetic)
│   ├── processed/                  # Processed NetCDF + ensemble members
│   └── zarr/                       # Zarr chunked store
│
├── outputs/
│   ├── figures/                    # 10 PNG plots
│   └── reports/                    # CSV analytics reports
│
├── metadata/
│   ├── fair_notes.md               # FAIR data alignment notes
│   ├── provenance.md               # Data lineage documentation
│   ├── model_architecture_notes.md # CESM/MPAS/NEMO notes
│   └── run_metadata.json           # Auto-generated run metadata
│
├── slurm/
│   └── run_pipeline.slurm          # HPC Slurm job script
│
├── scripts/
│   ├── download_era5.py            # ERA5 CDS download script
│   ├── clean_and_run.sh            # Delete cache + fresh pipeline
│   ├── run_pipeline.sh             # Bash pipeline runner
│   └── run_analysis.sh             # Analytics-only runner
│
└── notebooks/
    └── demo_analysis.ipynb         # Jupyter demo notebook
```

---

## 🚀 Quick Start

### Prerequisites

- Ubuntu 22.04 (or any Linux/macOS)
- Python 3.10 or 3.11
- Git
- 4 GB RAM minimum (8 GB recommended)
- 2 GB free disk space

### Step 1 — Clone the repository

```bash
git clone https://github.com/saifuddinds/The-Advanced-Climate-Modeling-Platform.git
cd The-Advanced-Climate-Modeling-Platform
```

### Step 2 — Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> **Windows users:** Use `python -m venv .venv` and `.venv\Scripts\activate`

### Step 3 — Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs all required packages: Xarray, Dask, NetCDF4, Zarr, Streamlit, Plotly, scikit-learn, and more. Takes 3–5 minutes on first install.

### Step 4 — Run the full pipeline

```bash
python -m src.pipeline
```

This runs all 9 steps automatically:

```
Step 1 — Generate / Load Data
Step 2 — Preprocess (Chunk + Zarr)
Step 3 — Analytics (Global Mean)
Step 4 — Climate Indices (Extremes)
Step 5 — Ensemble Uncertainty
Step 6 — Bias Correction
Step 7 — Statistical Downscaling
Step 8 — Visualizations (Figures)
Step 9 — Provenance and Metadata
```

Expected time: **2–5 minutes** on a standard laptop.

### Step 5 — Launch the dashboard

```bash
streamlit run app.py
```

Open your browser at: **http://localhost:8501**

---

## 🛠️ Usage

### Change the time range

Open `src/config.py` and edit:

```python
TIME_START = "2018-01-01"   # Your start year
TIME_END   = "2024-12-31"   # Your end year
```

Then run a clean pipeline (required to clear old cached data):

```bash
rm -f data/raw/*.nc data/processed/*.nc outputs/reports/*.csv
rm -rf data/zarr/*
python -m src.pipeline
```

Or use the helper script:

```bash
bash scripts/clean_and_run.sh
```

### Run only analytics (if data already generated)

```bash
bash scripts/run_analysis.sh
```

### Run individual modules

```bash
python -m src.generate_data      # Generate/load data only
python -m src.preprocess         # Preprocess only
python -m src.analytics          # Analytics only
python -m src.climate_indices    # Indices only
python -m src.ensemble           # Ensemble only
python -m src.bias_correction    # Bias correction only
python -m src.downscaling        # Downscaling only
python -m src.visualizations     # Figures only
python -m src.provenance         # Metadata only
```

---

## 🌐 Using Real ERA5 Data

By default the platform runs in **SYNTHETIC mode**. To use real ERA5 reanalysis data:

### Step 1 — Create a free CDS account

Go to: https://cds.climate.copernicus.eu and register.

### Step 2 — Get your API key

After login, go to: https://cds.climate.copernicus.eu/api-how-to

You will see your UID and API Key.

### Step 3 — Create the API config file

```bash
nano ~/.cdsapirc
```

Paste this (replace with your actual values):

```
url: https://cds.climate.copernicus.eu/api/v2
key: YOUR_UID:YOUR_API_KEY
```

Save: `Ctrl+X` → `Y` → `Enter`

### Step 4 — Install cdsapi

```bash
pip install cdsapi
```

### Step 5 — Download ERA5 data

```bash
python scripts/download_era5.py
```

This downloads monthly ERA5 data (temperature, precipitation, wind) into `data/raw/era5_climate.nc`. Download time: 10–30 minutes depending on internet speed.

### Step 6 — Run pipeline with real data

```bash
python -m src.pipeline
```

The platform **auto-detects** the ERA5 file and switches to REAL DATA mode automatically. No other changes needed.

---

## 📊 Dashboard

The Streamlit dashboard has **9 interactive pages**:

| Page | Content |
|---|---|
| 📊 Overview | Architecture cards + key metrics + temperature chart |
| 🌡️ Temperature Analytics | Monthly + annual mean with trend line |
| 🌧️ Precipitation | Monthly bar chart + distribution box plots |
| 📈 Climate Indices | Annual heatwave fraction chart |
| 🎲 Ensemble Analysis | 5-member spread + uncertainty band |
| 🔧 Bias Correction | Raw vs corrected temperature comparison |
| 📍 Downscaling | Station vs downscaled + scatter plot |
| 🗺️ Spatial Maps | Interactive heatmap (tas, pr, sfcWind) |
| 📋 Metadata & FAIR | Run metadata + FAIR alignment + provenance |
| 🔬 Pipeline Status | Output file status checker |

---

## 📦 Output Files

After running the pipeline, these files are generated:

```
data/raw/synthetic_climate.nc           Raw climate dataset
data/processed/processed_climate.nc    Preprocessed NetCDF
data/zarr/processed_climate.zarr/      Zarr chunked store
data/processed/ensemble_member_1.nc    Ensemble member 1
data/processed/ensemble_member_2.nc    Ensemble member 2
data/processed/ensemble_member_3.nc    Ensemble member 3
data/processed/ensemble_member_4.nc    Ensemble member 4
data/processed/ensemble_member_5.nc    Ensemble member 5
outputs/reports/global_means.csv       Global mean timeseries
outputs/reports/climate_indices.csv    Extreme indices
outputs/reports/ensemble_stats.csv     Ensemble statistics
outputs/reports/bias_corrected.csv     Bias correction results
outputs/reports/downscaled_station.csv Downscaling results
outputs/figures/*.png                  10 publication figures
metadata/run_metadata.json             Full provenance record
```

---

## 🧪 Technology Stack

| Category | Tools |
|---|---|
| Language | Python 3.11 |
| Scientific | NumPy, Pandas, SciPy |
| Climate | Xarray, Dask, cftime, cf_xarray |
| Storage | NetCDF4, h5netcdf, Zarr, numcodecs |
| ML | scikit-learn, statsmodels |
| Visualization | Matplotlib, Plotly |
| Dashboard | Streamlit |
| HPC Concepts | Slurm, Dask Distributed |
| Dev Tools | Git, GitHub, venv, Linux |

---

## 🔬 Scientific Methods

### Latitude-Weighted Global Mean
Grid cells near the equator are physically larger than those near poles. Cosine-of-latitude weighting corrects for this bias.

```python
weights = cos(deg2rad(lat))
global_mean = data.weighted(weights).mean(("lat", "lon"))
```

### Climate Extreme Indices
Based on ETCCDI-style indicators. Counts months where temperature or precipitation exceeds the 95th percentile of the full record.

### Ensemble Uncertainty
5 ensemble members generated with unique random seeds + perturbations. Ensemble standard deviation quantifies model uncertainty.

### Monthly Delta Bias Correction
Removes systematic model bias by subtracting the monthly mean difference between model and observations computed over a historical baseline period.

### Statistical Downscaling
LinearRegression maps coarse-resolution global mean to point station scale. Train on historical period, predict on future period.

---

## ⚙️ HPC Deployment

For real HPC cluster deployment, use the included Slurm job script:

```bash
sbatch slurm/run_pipeline.slurm
```

The script requests 8 CPUs, 32 GB RAM, and 4 hours wall time — suitable for moderate resolution climate data processing.

---

## 📋 FAIR Data Alignment

| Principle | Implementation |
|---|---|
| **F**indable | Clear folder structure + `metadata/run_metadata.json` |
| **A**ccessible | Streamlit dashboard + open CSV/NetCDF/Zarr formats |
| **I**nteroperable | CF-1.10 compliant NetCDF + standard variable names |
| **R**eusable | venv + requirements.txt + provenance + Git tracking |

---

## 🏛️ Model Architecture Alignment

This platform is architecturally aligned with real Earth system models:

| Model | Description | Role in this project |
|---|---|---|
| **CESM** | Community Earth System Model (NCAR) | Layer 1 architecture reference |
| **MPAS** | Model for Prediction Across Scales | Multiscale modeling concept |
| **NEMO** | Nucleus for European Modelling of the Ocean | Ocean layer reference |

Full production runs of these models require dedicated HPC clusters (hundreds of cores, terabytes of storage). This prototype demonstrates the surrounding workflow architecture.

---

## 🎓 Viva / Exam Guide

See [VIVA_GUIDE.md](VIVA_GUIDE.md) for complete answers to 15 common exam questions including:

- Why synthetic data?
- What is CESM/MPAS/NEMO?
- What is Zarr and why use it?
- What is chunking?
- What is ensemble analysis?
- What is bias correction?
- What is statistical downscaling?
- What is FAIR data?
- Why not run full CESM/MPAS/NEMO?

---

## 🐛 Troubleshooting

### Dashboard shows old years after config change

```bash
rm -f data/raw/*.nc data/processed/*.nc outputs/reports/*.csv
rm -rf data/zarr/*
python -m src.pipeline
```

### ModuleNotFoundError

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Pipeline runs but dashboard is blank

Make sure pipeline completed all 9 steps successfully, then:

```bash
streamlit run app.py
```

### ERA5 download fails

Check your `~/.cdsapirc` file has correct UID and API key with no extra spaces.

---

## 👤 Author

**Saif Ud Din Khan**
Diploma in Artificial Intelligence Operations — EduQual Level 6
📧 saifuddinds01@gmail.com
🔗 GitHub: [saifuddinds](https://github.com/saifuddinds)

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- [ECMWF](https://www.ecmwf.int) — ERA5 reanalysis dataset
- [Pangeo Community](https://pangeo.io) — Open, reproducible, scalable geoscience
- [NCAR](https://ncar.ucar.edu) — CESM and MPAS model frameworks
- [Xarray](https://xarray.dev) — N-dimensional labeled arrays
- [Dask](https://dask.org) — Parallel computing with task graphs
- [Streamlit](https://streamlit.io) — Interactive data applications

---

<div align="center">
<b>Model → Schedule → Store → Analyze → Share</b>
</div>
