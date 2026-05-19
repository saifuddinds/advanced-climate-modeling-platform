# FAIR Data Notes

## Purpose
This file explains how the project aligns with FAIR-style data practices.

FAIR stands for:
- **F**indable
- **A**ccessible
- **I**nteroperable
- **R**eusable

---

## 1. Findable
The project uses a clear folder structure and meaningful file names.
Every output is registered in `metadata/run_metadata.json` which serves
as the project's data inventory.

- Consistent naming: `processed_climate.nc`, `ensemble_member_1.nc`, etc.
- Structured folder hierarchy: data/raw → data/processed → outputs/
- Git-tracked version history provides change lineage

## 2. Accessible
Datasets can be accessed through:
- Direct file access (CSV / NetCDF / Zarr)
- Streamlit interactive dashboard (localhost:8501)
- Standard open formats readable by any scientific tool

## 3. Interoperable
The project uses community-standard formats:
- **NetCDF** with CF-1.10 conventions (standard_name, units, cell_methods)
- **Zarr** — cloud/HPC-native chunked format compatible with Xarray + Dask
- **CSV** — universally readable report format
- **Standard variable names**: air_temperature [K], precipitation_flux [mm day-1]

This means any climate scientist with Python, NCO, CDO, or R can read the outputs.

## 4. Reusable
The project supports full reusability through:
- Python virtual environment (isolated, reproducible)
- `requirements.txt` — pinned package list
- Documented scripts (docstrings in every module)
- `src/config.py` — centralized path management
- `metadata/run_metadata.json` — full provenance record
- Git version control with `.gitignore`

---

## FAIR vs This Project

| FAIR Principle | Implementation |
|---|---|
| Findable | `metadata/run_metadata.json` + clear folder structure |
| Accessible | Streamlit dashboard + open file formats |
| Interoperable | CF-NetCDF + Zarr + standard variable names |
| Reusable | venv + requirements.txt + provenance + Git |

---

## Relationship to Pangeo
This project follows a **Pangeo-style** analytics approach:
- Open source tools only (Python, Xarray, Dask, Zarr)
- Reproducible environment (venv + requirements.txt)
- Scalable design (Zarr chunks + Dask workers)
- FAIR-aligned data practices

Pangeo officially promotes open, reproducible, scalable geoscience —
this project aligns with that mission.

---

## Final Statement
This prototype does not implement a full enterprise FAIR governance framework,
but it consistently applies FAIR-aligned practices in project organisation,
metadata, standard formats, and reproducibility.
