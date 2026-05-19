"""
bias_correction.py
------------------
Monthly delta bias correction.
Auto-splits time into historical (first 60%) and future (last 40%).
Works with real ERA5 or synthetic data.
"""

import numpy as np
import pandas as pd
import xarray as xr
import logging

from src.config import ZARR_STORE, BIAS_CORRECTED_CSV, ensure_dirs

logging.basicConfig(level=logging.INFO, format="%(asctime)s [bias_correction] %(message)s")
log = logging.getLogger(__name__)


def _split_time(ds: xr.Dataset):
    """Split time into historical (60%) and future (40%) periods."""
    times = pd.to_datetime(ds['time'].values)
    n     = len(times)
    split = int(n * 0.6)
    hist_end   = str(times[split - 1])[:10]
    future_start = str(times[split])[:10]
    return slice(None, hist_end), slice(future_start, None)


def run() -> dict:
    ensure_dirs()
    log.info(f"Loading Zarr store from {ZARR_STORE} ...")
    ds = xr.open_zarr(str(ZARR_STORE))

    data_mode = ds.attrs.get('data_mode', 'UNKNOWN')
    log.info(f"  data_mode : {data_mode}")

    hist_slice, future_slice = _split_time(ds)
    log.info(f"  Historical: {hist_slice}")
    log.info(f"  Future    : {future_slice}")

    if data_mode == 'REAL':
        # With real ERA5: create synthetic obs by adding controlled bias
        # In production: load actual CRU/station obs here instead
        log.info("  Real data mode: using synthetic observation offset for demo")
        obs = ds.copy(deep=True)
        obs["tas"] = ds["tas"] - 1.5 + 0.2
    else:
        obs = ds.copy(deep=True)
        obs["tas"] = ds["tas"] - 1.5 + 0.2

    model_hist   = ds.sel(time=hist_slice)
    obs_hist     = obs.sel(time=hist_slice)
    model_future = ds.sel(time=future_slice)

    log.info("Computing monthly climatologies ...")
    model_clim  = model_hist["tas"].groupby("time.month").mean().compute()
    obs_clim    = obs_hist["tas"].groupby("time.month").mean().compute()
    monthly_bias = (model_clim - obs_clim).compute()
    log.info(f"  Mean absolute bias: {float(abs(monthly_bias).mean().values):.3f} K")

    log.info("Applying bias correction ...")
    corrected = (model_future["tas"].groupby("time.month") - monthly_bias).compute()

    weights = xr.DataArray(
        np.cos(np.deg2rad(ds["lat"])), dims=["lat"],
        coords={"lat": ds["lat"]}
    )
    raw_global       = model_future["tas"].weighted(weights).mean(("lat", "lon")).compute()
    corrected_global = corrected.weighted(weights).mean(("lat", "lon")).compute()

    df = pd.DataFrame({
        "time":               pd.to_datetime(model_future["time"].values),
        "raw_tas_K":          raw_global.values,
        "bias_corrected_K":   corrected_global.values,
        "correction_applied": (corrected_global - raw_global).values,
    })
    df.to_csv(BIAS_CORRECTED_CSV, index=False)
    log.info(f"Bias-corrected data saved -> {BIAS_CORRECTED_CSV}")
    log.info(f"  Mean correction: {df['correction_applied'].mean():.3f} K")

    return {
        "raw_global":       raw_global,
        "corrected_global": corrected_global,
        "df":               df,
    }


if __name__ == "__main__":
    run()
