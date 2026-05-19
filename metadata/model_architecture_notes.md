# Climate Model Architecture Notes

## Purpose
This document explains the model layer of the climate platform and shows how
CESM, MPAS, and NEMO fit into the overall architecture.

---

## 1. CESM — Community Earth System Model

**What it is:**
CESM is a fully-coupled global Earth system model developed by NCAR (National
Center for Atmospheric Research). It simulates atmosphere, ocean, land, sea ice,
land ice, and river components as a coupled system.

**Build requirements (from official docs):**
- Unix-like OS
- Python 3.8+
- Fortran/C compilers (gfortran, gcc)
- BLAS/LAPACK
- NetCDF4 + HDF5
- MPI (OpenMPI or MPICH)
- Batch scheduler (PBS/Slurm)

**In this project:**
CESM is included as a model-layer architecture reference. The platform's
data layer (NetCDF + HDF5), HPC layer (Slurm script), and Python stack
are all compatible with CESM's requirements.

**Official repository:** https://github.com/ESCOMP/CESM

---

## 2. MPAS — Model for Prediction Across Scales

**What it is:**
MPAS is an Earth-system modeling framework developed by NCAR and Los Alamos
National Laboratory. It uses unstructured Voronoi meshes to support
variable-resolution climate modeling across scales.

**Key features:**
- Atmosphere (MPAS-A), Ocean (MPAS-O), and Sea Ice components
- Unstructured mesh — allows local refinement without full-domain resolution increase
- Used in weather forecasting and climate research

**In this project:**
MPAS represents the multiscale modeling capability in the architecture.
The project's NetCDF/Zarr data layer is compatible with MPAS output formats.

**Official repository:** https://github.com/MPAS-Dev/MPAS-Model

---

## 3. NEMO — Nucleus for European Modelling of the Ocean

**What it is:**
NEMO is a state-of-the-art ocean modeling framework used by meteorological
services and research institutions across Europe (Met Office, ECMWF, Mercator Ocean).

**Key features:**
- Ocean dynamics, thermodynamics, sea-ice
- Passive tracer transport
- Biogeochemical cycles
- Used in Copernicus Marine Service products

**In this project:**
NEMO represents the ocean-model layer of the architecture.

**Official site:** https://www.nemo-ocean.eu

---

## 4. Architecture Alignment Table

| Platform Layer | Technology | Real Model Equivalent |
|---|---|---|
| Model execution | Python synthetic generation | CESM / MPAS / NEMO |
| HPC scheduling | Slurm job script | PBS / SLURM on Derecho/Atos |
| Data storage | NetCDF (CF-1.10) + Zarr | Standard climate output format |
| Analytics | Xarray + Dask | Pangeo-style post-processing |
| Visualization | Plotly + Streamlit | Jupyter + HoloViews |

---

## 5. Viva Statement

> "I designed the platform architecture to be compatible with real Earth system
> models such as CESM, MPAS, and NEMO. The data formats (CF-compliant NetCDF),
> HPC scheduling approach (Slurm), and analytics stack (Xarray + Dask) are all
> consistent with how these models are used in production research environments.
>
> In this prototype, the focus was on workflow, analytics, reproducibility,
> and data-serving layers, while heavy production model deployment was treated
> as the natural extension path."

---

## 6. Why These Are Not Fully Run in This Prototype

Full production runs of CESM, MPAS, or NEMO require:
- Dedicated HPC clusters (hundreds to thousands of CPU cores)
- Terabytes of storage
- Days to weeks of wall-clock time
- Licensed/configured model codes with scientific configuration

This project demonstrates the complete platform architecture and workflow
that surrounds these models — which is the layer where most climate science
work (post-processing, analysis, visualization) actually happens.
