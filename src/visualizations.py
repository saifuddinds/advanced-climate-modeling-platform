"""
visualizations.py
-----------------
All Matplotlib figures. Auto-adapts to any time range or grid size.
"""

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import logging

from src.config import (
    ZARR_STORE,
    GLOBAL_MEANS_CSV, CLIMATE_INDICES_CSV,
    ENSEMBLE_STATS_CSV, BIAS_CORRECTED_CSV, DOWNSCALED_CSV,
    FIG_GLOBAL_TEMP, FIG_GLOBAL_PRECIP,
    FIG_HEATWAVE, FIG_HEAVY_RAIN,
    FIG_TREND, FIG_ANOMALY,
    FIG_ENSEMBLE_MEAN, FIG_ENSEMBLE_SPREAD,
    FIG_BIAS_CORRECTED, FIG_DOWNSCALING,
    N_ENSEMBLE, ensure_dirs
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [visualizations] %(message)s")
log = logging.getLogger(__name__)

STYLE = {
    "figure.facecolor": "#0f1117",
    "axes.facecolor":   "#1a1d27",
    "axes.edgecolor":   "#3a3d4a",
    "axes.labelcolor":  "#c8ccd8",
    "xtick.color":      "#888",
    "ytick.color":      "#888",
    "text.color":       "#c8ccd8",
    "grid.color":       "#2a2d3a",
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
}


def _apply_style():
    plt.rcParams.update(STYLE)


def _save(fig, path, log_name=""):
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    log.info(f"  Saved: {path.name}")


def plot_global_temp():
    if not GLOBAL_MEANS_CSV.exists():
        log.warning("global_means.csv missing, skipping plot"); return
    df = pd.read_csv(GLOBAL_MEANS_CSV, parse_dates=["time"])
    _apply_style()
    fig, ax = plt.subplots(figsize=(10, 4), facecolor=STYLE["figure.facecolor"])
    ax.set_facecolor(STYLE["axes.facecolor"])
    ax.plot(df["time"], df["tas_global_K"], color="#4fc3f7", linewidth=1.5)
    ax.fill_between(df["time"], df["tas_global_K"].min(), df["tas_global_K"],
                    alpha=0.12, color="#4fc3f7")
    ax.set_title("Global Mean Near-Surface Air Temperature", fontsize=13, pad=10)
    ax.set_xlabel("Time"); ax.set_ylabel("Temperature (K)"); ax.grid(True)
    _save(fig, FIG_GLOBAL_TEMP)


def plot_global_precip():
    if not GLOBAL_MEANS_CSV.exists():
        log.warning("global_means.csv missing, skipping plot"); return
    df = pd.read_csv(GLOBAL_MEANS_CSV, parse_dates=["time"])
    _apply_style()
    fig, ax = plt.subplots(figsize=(10, 4), facecolor=STYLE["figure.facecolor"])
    ax.set_facecolor(STYLE["axes.facecolor"])
    ax.bar(df["time"], df["pr_global_mm"], color="#81c784", width=20, alpha=0.85)
    ax.set_title("Global Mean Precipitation", fontsize=13, pad=10)
    ax.set_xlabel("Time"); ax.set_ylabel("Precipitation (mm day-1)"); ax.grid(True, axis="y")
    _save(fig, FIG_GLOBAL_PRECIP)


def plot_heatwave():
    if not ZARR_STORE.exists():
        log.warning("Zarr store missing, skipping heatwave plot"); return
    ds   = xr.open_zarr(str(ZARR_STORE))
    tas95 = ds["tas"].quantile(0.95, dim="time").compute()
    hot   = (ds["tas"] > tas95).sum(dim="time").compute()
    _apply_style()
    fig, ax = plt.subplots(figsize=(11, 5), facecolor=STYLE["figure.facecolor"])
    ax.set_facecolor(STYLE["axes.facecolor"])
    im = ax.pcolormesh(ds["lon"].values, ds["lat"].values, hot.values,
                       cmap="YlOrRd", shading="auto")
    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Months > 95th pct", color="#c8ccd8")
    cbar.ax.yaxis.set_tick_params(color="#c8ccd8")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#c8ccd8")
    ax.set_title("Heatwave Months (tas > 95th percentile)", fontsize=13, pad=10)
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
    _save(fig, FIG_HEATWAVE)


def plot_heavy_rain():
    if not ZARR_STORE.exists():
        log.warning("Zarr store missing, skipping heavy rain plot"); return
    ds  = xr.open_zarr(str(ZARR_STORE))
    pr95 = ds["pr"].quantile(0.95, dim="time").compute()
    wet  = (ds["pr"] > pr95).sum(dim="time").compute()
    _apply_style()
    fig, ax = plt.subplots(figsize=(11, 5), facecolor=STYLE["figure.facecolor"])
    ax.set_facecolor(STYLE["axes.facecolor"])
    im = ax.pcolormesh(ds["lon"].values, ds["lat"].values, wet.values,
                       cmap="Blues", shading="auto")
    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Months > 95th pct", color="#c8ccd8")
    cbar.ax.yaxis.set_tick_params(color="#c8ccd8")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#c8ccd8")
    ax.set_title("Heavy Rainfall Months (pr > 95th percentile)", fontsize=13, pad=10)
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
    _save(fig, FIG_HEAVY_RAIN)


def plot_trend():
    if not ZARR_STORE.exists():
        log.warning("Zarr store missing, skipping trend plot"); return
    ds   = xr.open_zarr(str(ZARR_STORE))
    t    = np.arange(ds.dims["time"]).astype(float)
    t_da = xr.DataArray(t, dims=["time"], coords={"time": ds["time"]})
    t_c  = t_da - t_da.mean()
    trend    = ((ds["tas"] * t_c).mean("time") / (t_c ** 2).mean("time")).compute()
    trend_yr = trend * 12.0
    _apply_style()
    fig, ax = plt.subplots(figsize=(11, 5), facecolor=STYLE["figure.facecolor"])
    ax.set_facecolor(STYLE["axes.facecolor"])
    lim = float(abs(trend_yr).max().values)
    im  = ax.pcolormesh(ds["lon"].values, ds["lat"].values, trend_yr.values,
                        cmap="RdBu_r", vmin=-lim, vmax=lim, shading="auto")
    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("K year-1", color="#c8ccd8")
    cbar.ax.yaxis.set_tick_params(color="#c8ccd8")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#c8ccd8")
    ax.set_title("Linear Warming Trend (K year-1)", fontsize=13, pad=10)
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
    _save(fig, FIG_TREND)


def plot_anomaly():
    if not ZARR_STORE.exists():
        log.warning("Zarr store missing, skipping anomaly plot"); return
    ds   = xr.open_zarr(str(ZARR_STORE))
    times = pd.to_datetime(ds['time'].values)
    n     = len(times)
    base_end = str(times[int(n * 0.6) - 1])[:10]
    clim  = ds.sel(time=slice(None, base_end)).groupby("time.month").mean()
    anom  = (ds["tas"].groupby("time.month") - clim["tas"]).isel(time=0).compute()
    _apply_style()
    fig, ax = plt.subplots(figsize=(11, 5), facecolor=STYLE["figure.facecolor"])
    ax.set_facecolor(STYLE["axes.facecolor"])
    lim = float(abs(anom).max().values)
    im  = ax.pcolormesh(ds["lon"].values, ds["lat"].values, anom.values,
                        cmap="coolwarm", vmin=-lim, vmax=lim, shading="auto")
    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Anomaly (K)", color="#c8ccd8")
    cbar.ax.yaxis.set_tick_params(color="#c8ccd8")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#c8ccd8")
    ax.set_title(f"Temperature Anomaly - {str(ds['time'].values[0])[:7]}", fontsize=13, pad=10)
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
    _save(fig, FIG_ANOMALY)


def plot_ensemble_mean():
    if not ENSEMBLE_STATS_CSV.exists():
        log.warning("ensemble_stats.csv missing, skipping plot"); return
    df = pd.read_csv(ENSEMBLE_STATS_CSV, index_col="time", parse_dates=True)
    _apply_style()
    fig, ax = plt.subplots(figsize=(10, 4), facecolor=STYLE["figure.facecolor"])
    ax.set_facecolor(STYLE["axes.facecolor"])
    colors = cm.plasma(np.linspace(0.2, 0.9, N_ENSEMBLE))
    for i, c in enumerate(colors, start=1):
        col = f"member_{i}"
        if col in df.columns:
            ax.plot(df.index, df[col], color=c, alpha=0.5, linewidth=0.9, label=f"M{i}")
    if "ensemble_mean" in df.columns:
        ax.plot(df.index, df["ensemble_mean"], color="white", linewidth=2.0, label="Mean")
    ax.set_title("Ensemble Global Mean Temperature", fontsize=13, pad=10)
    ax.set_xlabel("Time"); ax.set_ylabel("Temperature (K)")
    ax.legend(fontsize=8, ncol=3, facecolor="#1a1d27", labelcolor="#c8ccd8")
    ax.grid(True)
    _save(fig, FIG_ENSEMBLE_MEAN)


def plot_ensemble_spread():
    if not ENSEMBLE_STATS_CSV.exists():
        log.warning("ensemble_stats.csv missing, skipping plot"); return
    df = pd.read_csv(ENSEMBLE_STATS_CSV, index_col="time", parse_dates=True)
    _apply_style()
    fig, ax = plt.subplots(figsize=(10, 4), facecolor=STYLE["figure.facecolor"])
    ax.set_facecolor(STYLE["axes.facecolor"])
    if "ensemble_mean" in df.columns and "ensemble_std" in df.columns:
        ax.fill_between(df.index,
                        df["ensemble_mean"] - df["ensemble_std"],
                        df["ensemble_mean"] + df["ensemble_std"],
                        alpha=0.3, color="#ce93d8", label="+-1 sigma")
        ax.plot(df.index, df["ensemble_mean"], color="#ce93d8", linewidth=2.0, label="Mean")
    ax.set_title("Ensemble Spread (Uncertainty)", fontsize=13, pad=10)
    ax.set_xlabel("Time"); ax.set_ylabel("Temperature (K)")
    ax.legend(fontsize=9, facecolor="#1a1d27", labelcolor="#c8ccd8")
    ax.grid(True)
    _save(fig, FIG_ENSEMBLE_SPREAD)


def plot_bias_correction():
    if not BIAS_CORRECTED_CSV.exists():
        log.warning("bias_corrected.csv missing, skipping plot"); return
    df = pd.read_csv(BIAS_CORRECTED_CSV, parse_dates=["time"])
    _apply_style()
    fig, ax = plt.subplots(figsize=(10, 4), facecolor=STYLE["figure.facecolor"])
    ax.set_facecolor(STYLE["axes.facecolor"])
    ax.plot(df["time"], df["raw_tas_K"],       color="#ef9a9a", linewidth=1.5, label="Raw Model")
    ax.plot(df["time"], df["bias_corrected_K"], color="#80cbc4", linewidth=1.5, label="Bias Corrected")
    ax.set_title("Bias Correction: Raw vs Corrected Temperature", fontsize=13, pad=10)
    ax.set_xlabel("Time"); ax.set_ylabel("Temperature (K)")
    ax.legend(fontsize=9, facecolor="#1a1d27", labelcolor="#c8ccd8")
    ax.grid(True)
    _save(fig, FIG_BIAS_CORRECTED)


def plot_downscaling():
    if not DOWNSCALED_CSV.exists():
        log.warning("downscaled_station.csv missing, skipping plot"); return
    df = pd.read_csv(DOWNSCALED_CSV, parse_dates=["time"])
    _apply_style()
    fig, ax = plt.subplots(figsize=(10, 4), facecolor=STYLE["figure.facecolor"])
    ax.set_facecolor(STYLE["axes.facecolor"])
    ax.plot(df["time"], df["observed_station_K"],   color="#a5d6a7", linewidth=1.5, label="Observed Station")
    ax.plot(df["time"], df["downscaled_station_K"], color="#ffcc80", linewidth=1.5,
            linestyle="--", label="Downscaled")
    ax.set_title("Statistical Downscaling: Station vs Downscaled", fontsize=13, pad=10)
    ax.set_xlabel("Time"); ax.set_ylabel("Temperature (K)")
    ax.legend(fontsize=9, facecolor="#1a1d27", labelcolor="#c8ccd8")
    ax.grid(True)
    _save(fig, FIG_DOWNSCALING)


def run():
    ensure_dirs()
    log.info("Generating all figures ...")
    plot_global_temp()
    plot_global_precip()
    plot_heatwave()
    plot_heavy_rain()
    plot_trend()
    plot_anomaly()
    plot_ensemble_mean()
    plot_ensemble_spread()
    plot_bias_correction()
    plot_downscaling()
    log.info("All figures saved.")


if __name__ == "__main__":
    run()
