"""
ensemble.py
-----------
5-member ensemble with uncertainty stats.
Reads real grid dimensions from Zarr store — no hardcoded sizes.
"""

import numpy as np
import pandas as pd
import xarray as xr
import logging

from src.config import (
    ZARR_STORE, PROCESSED_DIR,
    ENSEMBLE_STATS_CSV, N_ENSEMBLE, ensure_dirs
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [ensemble] %(message)s")
log = logging.getLogger(__name__)


def run() -> dict:
    ensure_dirs()

    # Read actual dimensions from processed data
    log.info(f"Reading dimensions from {ZARR_STORE} ...")
    ds_ref = xr.open_zarr(str(ZARR_STORE))
    time   = pd.to_datetime(ds_ref["time"].values)
    lat    = ds_ref["lat"].values
    lon    = ds_ref["lon"].values
    n_t, n_y, n_x = len(time), len(lat), len(lon)
    data_mode = ds_ref.attrs.get('data_mode', 'UNKNOWN')
    log.info(f"  Grid: time={n_t}, lat={n_y}, lon={n_x}  mode={data_mode}")

    member_datasets = []

    for i in range(1, N_ENSEMBLE + 1):
        np.random.seed(i)
        t  = np.arange(n_t)[:, None, None]
        yy = lat[None, :, None]

        # Base signal from reference data + member-specific perturbation
        tas_ref = ds_ref["tas"].compute().values

        tas = (
            tas_ref
            + np.random.normal(0, 0.5 + i * 0.05, (n_t, n_y, n_x))
            + np.random.normal(0, 0.2)   # systematic offset
        ).astype("float32")

        ds_m = xr.Dataset(
            {"tas": (("time", "lat", "lon"), tas)},
            coords={"time": time, "lat": lat, "lon": lon},
        )
        ds_m["tas"].attrs = {
            "long_name": "Near-Surface Air Temperature",
            "standard_name": "air_temperature", "units": "K",
        }
        ds_m.attrs = {"ensemble_member": i, "data_mode": data_mode}

        out_path = PROCESSED_DIR / f"ensemble_member_{i}.nc"
        ds_m.to_netcdf(out_path)
        log.info(f"  Saved member {i} -> {out_path}")
        member_datasets.append(ds_m)

    # Ensemble statistics
    log.info("Computing ensemble statistics ...")
    ds_ens   = xr.concat(member_datasets, dim="member")
    ds_ens   = ds_ens.assign_coords(member=range(1, N_ENSEMBLE + 1))
    ens_mean = ds_ens["tas"].mean("member").compute()
    ens_std  = ds_ens["tas"].std("member").compute()

    weights = xr.DataArray(
        np.cos(np.deg2rad(lat)), dims=["lat"], coords={"lat": lat}
    )
    global_means = {}
    for i, ds_m in enumerate(member_datasets, start=1):
        gm = ds_m["tas"].weighted(weights).mean(("lat", "lon")).values
        global_means[f"member_{i}"] = gm

    df = pd.DataFrame(global_means, index=pd.to_datetime(time))
    df.index.name  = "time"
    df["ensemble_mean"] = df.mean(axis=1)
    df["ensemble_std"]  = df.iloc[:, :N_ENSEMBLE].std(axis=1)
    df.to_csv(ENSEMBLE_STATS_CSV)
    log.info(f"Ensemble stats saved -> {ENSEMBLE_STATS_CSV}")
    log.info(f"  Mean spread (sigma): {df['ensemble_std'].mean():.4f} K")

    return {"ens_mean": ens_mean, "ens_std": ens_std, "member_df": df}


if __name__ == "__main__":
    run()
