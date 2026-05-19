"""
preprocess.py
-------------
Loads the raw NetCDF (real or synthetic), applies chunking,
saves processed NetCDF and Zarr store.

Handles variable grid size differences between ERA5 and synthetic data
automatically via config-free chunk sizing.
"""

import xarray as xr
import numpy as np
import logging

from src.config import RAW_NC, PROCESSED_NC, ZARR_STORE, ensure_dirs

logging.basicConfig(level=logging.INFO, format="%(asctime)s [preprocess] %(message)s")
log = logging.getLogger(__name__)


def _smart_chunks(ds: xr.Dataset) -> dict:
    """
    Auto-calculate safe chunk sizes based on actual dataset dimensions.
    Works for both small synthetic (61x144) and large ERA5 (721x1440) grids.
    """
    n_time = ds.dims.get('time', 60)
    n_lat  = ds.dims.get('lat', 61)
    n_lon  = ds.dims.get('lon', 144)

    # Chunk so each chunk is ~10-50 MB
    t_chunk   = min(12, n_time)
    lat_chunk = min(20, max(1, n_lat // 10))
    lon_chunk = min(40, max(1, n_lon // 20))

    return {"time": t_chunk, "lat": lat_chunk, "lon": lon_chunk}


def preprocess() -> xr.Dataset:
    ensure_dirs()
    log.info(f"Loading raw dataset from {RAW_NC} ...")

    if not RAW_NC.exists():
        raise FileNotFoundError(
            f"Raw file not found: {RAW_NC}\n"
            "Run: python -m src.generate_data  first"
        )

    ds = xr.open_dataset(RAW_NC)
    data_mode = ds.attrs.get('data_mode', 'UNKNOWN')
    log.info(f"  data_mode  : {data_mode}")
    log.info(f"  variables  : {list(ds.data_vars)}")
    log.info(f"  dimensions : {dict(ds.dims)}")

    # Sort time axis
    ds = ds.sortby("time")

    # Auto chunks
    chunks = _smart_chunks(ds)
    log.info(f"  chunks     : {chunks}")
    ds = ds.chunk(chunks)

    # Save processed NetCDF
    log.info(f"Saving processed NetCDF -> {PROCESSED_NC}")
    ds.load().to_netcdf(PROCESSED_NC)

    # Save Zarr store
    if ZARR_STORE.exists():
        import shutil
        shutil.rmtree(ZARR_STORE)
    log.info(f"Saving Zarr store -> {ZARR_STORE}")
    ds.to_zarr(str(ZARR_STORE), mode="w")

    log.info("Preprocessing complete.")
    return ds


if __name__ == "__main__":
    preprocess()
