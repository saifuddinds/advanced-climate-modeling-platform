"""
analytics.py
------------
Latitude-weighted global mean, climatology, anomalies.
Works with any grid size (synthetic or real ERA5).
"""

import numpy as np
import pandas as pd
import xarray as xr
import logging

from src.config import ZARR_STORE, GLOBAL_MEANS_CSV, ensure_dirs

logging.basicConfig(level=logging.INFO, format="%(asctime)s [analytics] %(message)s")
log = logging.getLogger(__name__)


def _baseline_slice(ds: xr.Dataset):
    """Auto-detect baseline period: first 60% of time range."""
    times = pd.to_datetime(ds['time'].values)
    n = len(times)
    cutoff = times[int(n * 0.6)]
    return slice(str(times[0])[:10], str(cutoff)[:10])


def run() -> dict:
    ensure_dirs()
    log.info(f"Loading Zarr store from {ZARR_STORE} ...")
    ds = xr.open_zarr(str(ZARR_STORE))

    log.info(f"  data_mode : {ds.attrs.get('data_mode', 'UNKNOWN')}")
    log.info(f"  variables : {list(ds.data_vars)}")
    log.info(f"  time      : {str(ds.time.values[0])[:10]} -> {str(ds.time.values[-1])[:10]}")

    weights = xr.DataArray(
        np.cos(np.deg2rad(ds["lat"])),
        dims=["lat"], coords={"lat": ds["lat"]}
    )

    log.info("Computing weighted global mean temperature ...")
    tas_global = ds["tas"].weighted(weights).mean(("lat", "lon")).compute()

    log.info("Computing weighted global mean precipitation ...")
    pr_global  = ds["pr"].weighted(weights).mean(("lat", "lon")).compute()

    # Auto baseline
    baseline_slice = _baseline_slice(ds)
    log.info(f"Baseline period: {baseline_slice}")

    baseline = ds.sel(time=baseline_slice)
    clim_tas = baseline["tas"].groupby("time.month").mean().compute()
    clim_pr  = baseline["pr"].groupby("time.month").mean().compute()

    log.info("Computing anomalies ...")
    tas_anom = (ds["tas"].groupby("time.month") - clim_tas).compute()
    pr_anom  = (ds["pr"].groupby("time.month")  - clim_pr).compute()

    # Annual summaries
    df = pd.DataFrame({
        "time":          pd.to_datetime(tas_global["time"].values),
        "tas_global_K":  tas_global.values,
        "pr_global_mm":  pr_global.values,
    })
    df.to_csv(GLOBAL_MEANS_CSV, index=False)
    log.info(f"Global means saved -> {GLOBAL_MEANS_CSV}")
    log.info(f"  Mean tas: {df['tas_global_K'].mean():.2f} K")
    log.info(f"  Mean pr : {df['pr_global_mm'].mean():.3f} mm/day")

    return {
        "tas_global":  tas_global,
        "pr_global":   pr_global,
        "clim_tas":    clim_tas,
        "clim_pr":     clim_pr,
        "tas_anom":    tas_anom,
        "pr_anom":     pr_anom,
    }


if __name__ == "__main__":
    run()
