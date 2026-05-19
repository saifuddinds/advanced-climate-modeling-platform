"""
downscaling.py
--------------
Statistical downscaling using LinearRegression.
Auto train/test split: first 60% train, last 40% test.
Works with real or synthetic data.
"""

import numpy as np
import pandas as pd
import xarray as xr
import logging

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

from src.config import ZARR_STORE, DOWNSCALED_CSV, ensure_dirs

logging.basicConfig(level=logging.INFO, format="%(asctime)s [downscaling] %(message)s")
log = logging.getLogger(__name__)


def run() -> dict:
    ensure_dirs()
    log.info(f"Loading Zarr store from {ZARR_STORE} ...")
    ds = xr.open_zarr(str(ZARR_STORE))

    data_mode = ds.attrs.get('data_mode', 'UNKNOWN')
    log.info(f"  data_mode : {data_mode}")

    weights = xr.DataArray(
        np.cos(np.deg2rad(ds["lat"])), dims=["lat"],
        coords={"lat": ds["lat"]}
    )
    global_mean = ds["tas"].weighted(weights).mean(("lat", "lon")).compute().values
    time = pd.to_datetime(ds["time"].values)

    # Synthetic station: linear relationship + noise
    np.random.seed(7)
    station_temp = 0.8 * global_mean + 40.0 + np.random.normal(0, 0.5, len(global_mean))

    # Auto train/test split (60/40)
    n_train = int(len(time) * 0.6)
    log.info(f"  Train: {n_train} months  |  Test: {len(time)-n_train} months")

    X = global_mean.reshape(-1, 1)
    y = station_temp

    X_train, X_test = X[:n_train],   X[n_train:]
    y_train, y_test = y[:n_train],   y[n_train:]

    log.info("Fitting LinearRegression ...")
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    r2   = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    log.info(f"  Coefficient : {model.coef_[0]:.4f}")
    log.info(f"  Intercept   : {model.intercept_:.4f}")
    log.info(f"  R2          : {r2:.4f}")
    log.info(f"  RMSE        : {rmse:.4f} K")

    df = pd.DataFrame({
        "time":                   time[n_train:],
        "coarse_global_mean_K":   X_test[:, 0],
        "observed_station_K":     y_test,
        "downscaled_station_K":   y_pred,
        "residual_K":             y_test - y_pred,
    })
    df.to_csv(DOWNSCALED_CSV, index=False)
    log.info(f"Downscaled data saved -> {DOWNSCALED_CSV}")

    return {"model": model, "df": df, "r2": r2, "rmse": rmse}


if __name__ == "__main__":
    run()
