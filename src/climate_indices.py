"""
climate_indices.py
------------------
Climate extreme indices and trend analysis.
Auto-adapts to any time range (synthetic or real ERA5).
"""

import numpy as np
import pandas as pd
import xarray as xr
import logging

from src.config import ZARR_STORE, CLIMATE_INDICES_CSV, ensure_dirs

logging.basicConfig(level=logging.INFO, format="%(asctime)s [climate_indices] %(message)s")
log = logging.getLogger(__name__)


def run() -> dict:
    ensure_dirs()
    log.info(f"Loading Zarr store from {ZARR_STORE} ...")
    ds = xr.open_zarr(str(ZARR_STORE))

    # 95th percentile thresholds
    log.info("Computing 95th percentile thresholds ...")
    tas95 = ds["tas"].quantile(0.95, dim="time").compute()
    pr95  = ds["pr"].quantile(0.95,  dim="time").compute()

    # Extreme counts
    log.info("Counting extreme months ...")
    hot_extremes = (ds["tas"] > tas95).sum(dim="time").compute()
    wet_extremes = (ds["pr"]  > pr95).sum(dim="time").compute()

    # Annual heatwave fraction
    is_hot = (ds["tas"] > tas95)
    hot_fraction_monthly = is_hot.mean(("lat", "lon")).compute()
    hot_annual = (
        hot_fraction_monthly
        .assign_coords(year=hot_fraction_monthly["time"].dt.year)
        .groupby("year").sum()
    )

    # Linear trend
    log.info("Computing linear warming trend ...")
    t    = np.arange(ds.dims["time"]).astype(float)
    t_da = xr.DataArray(t, dims=["time"], coords={"time": ds["time"]})
    t_c  = t_da - t_da.mean()
    trend = ((ds["tas"] * t_c).mean("time") / (t_c ** 2).mean("time")).compute()
    trend_per_year = trend * 12.0

    log.info(f"  Global mean heatwave fraction : {float(hot_extremes.mean().values):.1f}")
    log.info(f"  Global mean trend (K/yr)      : {float(trend_per_year.mean().values):.4f}")

    df = pd.DataFrame({
        "year":              hot_annual["year"].values,
        "heatwave_fraction": hot_annual.values,
    })
    df.to_csv(CLIMATE_INDICES_CSV, index=False)
    log.info(f"Climate indices saved -> {CLIMATE_INDICES_CSV}")

    return {
        "hot_extremes":   hot_extremes,
        "wet_extremes":   wet_extremes,
        "trend_per_year": trend_per_year,
        "hot_annual":     hot_annual,
    }


if __name__ == "__main__":
    run()
