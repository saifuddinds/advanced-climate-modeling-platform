# Viva Preparation Guide
## Advanced Climate Modeling Platform

---

## Project Positioning Statement (Say this first)

> "This is a prototype advanced climate modeling platform that demonstrates the core layers of a modern climate-science workflow: model-layer alignment, HPC scheduling, scientific data storage, distributed analytics, uncertainty quantification, bias correction, statistical downscaling, visualization, and data publishing.
> 
> I implemented the full platform workflow. For heavy climate models like CESM, MPAS, and NEMO, I included architecture alignment and repository evidence — because these models require dedicated HPC clusters that weren't available locally."

---

## Q: Why did you use synthetic data?

> "Synthetic data is fully reproducible, lightweight, and runs on limited local hardware while preserving the exact structure of real CF-compliant climate model output. In a production environment, the same pipeline would ingest CESM or ERA5 data — the code structure doesn't change."

---

## Q: What is CESM / MPAS / NEMO?

> "CESM is a fully-coupled global Earth system model from NCAR — it simulates atmosphere, ocean, land, and sea ice together. MPAS uses unstructured Voronoi meshes for variable-resolution modeling. NEMO is the ocean modeling framework used by ECMWF and Copernicus Marine Service. These represent Layer 1 of my platform's 5-layer architecture."

---

## Q: What is Zarr and why use it instead of NetCDF?

> "NetCDF is the standard scientific format — it's CF-compliant and universally supported. Zarr adds chunked, cloud-native storage on top of that — it lets Dask process each chunk independently without loading the full dataset into memory. This is how large datasets are handled on HPC systems. I use both: NetCDF for compatibility, Zarr for analytics performance."

---

## Q: What is chunking?

> "Chunking divides the dataset into smaller pieces — for example {time:12, lat:20, lon:20}. Dask then processes each chunk as a separate task, potentially in parallel. This is how climate datasets with billions of grid points are analyzed on HPC systems — you never load the full dataset at once."

---

## Q: What is ensemble analysis?

> "Ensemble analysis runs multiple model simulations with slightly different initial conditions or parameters. The ensemble mean shows the robust climate signal while the standard deviation quantifies uncertainty. In operational climate modeling, 50–100 member ensembles are standard. My prototype uses 5 members to demonstrate the concept."

---

## Q: What is bias correction?

> "Climate models have systematic errors — they consistently run too warm or too cold relative to observations. Monthly delta bias correction computes the difference between model climatology and observed climatology for each month, then subtracts that from the model output. It preserves the seasonal cycle while removing the mean bias."

---

## Q: What is statistical downscaling?

> "Climate models output at 100km+ resolution, but impact studies need local-scale data. Statistical downscaling builds a regression relationship between large-scale model output and local station observations. I used scikit-learn LinearRegression — trained on 2000–2002, applied to 2003–2004. In production, more complex methods like BCSD or DELTA mapping are used."

---

## Q: What is FAIR data?

> "FAIR stands for Findable, Accessible, Interoperable, and Reusable. Findable means clear file names and structure. Accessible means the data can be reached — I have a Streamlit dashboard and standard open formats. Interoperable means CF-NetCDF with standard variable names that any tool can read. Reusable means requirements.txt, virtual environment, documented code, and provenance tracking."

---

## Q: What is provenance?

> "Provenance records the complete lineage of an output — which script created it, from which input, at what time, and what transformation was applied. My metadata/run_metadata.json records every step. This is required for reproducible science."

---

## Q: What is Dask?

> "Dask is a parallel computing library that integrates with Xarray. It processes data in chunks using a task graph — so you can analyze datasets larger than RAM. It can use multiple CPU cores locally, or distribute across a cluster. In my project I use Dask distributed with 4 workers for the analytics steps."

---

## Q: What is Slurm?

> "Slurm is the standard HPC batch scheduler used at NCAR Derecho, ECMWF Atos, and most university clusters. You submit a job script specifying resources — nodes, CPUs, memory, wall time — and Slurm queues and executes it. I included a Slurm job script in slurm/run_pipeline.slurm as architecture evidence."

---

## Q: Why didn't you run CESM/MPAS/NEMO?

> "Full production runs require dedicated HPC clusters with hundreds to thousands of cores, terabytes of storage, and weeks of wall-clock time. This project demonstrates the complete platform architecture and workflow that surrounds these models — post-processing, analysis, uncertainty quantification, visualization, and data serving — which is where most climate science work actually happens. The model layer is the extension path."

---

## Architecture in 10 seconds

```
Model (CESM/MPAS/NEMO)
    ↓ output files
HPC Layer (Slurm + MPI)
    ↓ scheduled runs
Data Layer (NetCDF + Zarr)
    ↓ chunked storage
Analytics (Xarray + Dask + sklearn)
    ↓ indices, ensemble, bias, downscaling
Sharing (Streamlit + FAIR metadata)
```

---

## Key numbers to remember

| Item | Value |
|---|---|
| Grid | 61 lat × 144 lon |
| Time | 60 months (2000–2004) |
| Variables | tas (K), pr (mm/day), sfcWind (m/s) |
| Chunks | time:12, lat:20, lon:20 |
| Ensemble members | 5 |
| Baseline period | 2000–2002 |
| Future period | 2003–2004 |
| Downscaling train | 36 months |
| Extreme threshold | 95th percentile |
| Figures generated | 10 |
