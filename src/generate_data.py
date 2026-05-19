"""
generate_data.py
----------------
SMART LOADER — 2 modes:

MODE 1 (REAL DATA):
  - ERA5 .nc file place karo: data/raw/era5_climate.nc
  - Auto-detect ho jayega
  - Variable rename + unit conversion automatic

MODE 2 (AUTO SYNTHETIC FALLBACK):
  - Agar koi .nc file nahi mili to realistic synthetic data generate hoga
  - Pipeline kabhi crash nahi karega
"""

import numpy as np
import pandas as pd
import xarray as xr
import logging
from pathlib import Path

from src.config import (
    RAW_DIR, RAW_NC,
    TIME_START, TIME_END,
    LAT_MIN, LAT_MAX, LAT_STEPS,
    LON_MIN, LON_MAX, LON_STEPS,
    RANDOM_SEED, ensure_dirs
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [generate_data] %(message)s")
log = logging.getLogger(__name__)

ERA5_VAR_MAP = {
    't2m': 'tas', 'temperature_2m': 'tas', '2m_temperature': 'tas', 'tas': 'tas',
    'tp': 'pr', 'total_precipitation': 'pr', 'precipitation': 'pr', 'pr': 'pr',
    'si10': 'sfcWind', 'wind_speed': 'sfcWind', '10m_wind_speed': 'sfcWind',
    'sfcWind': 'sfcWind', 'ws': 'sfcWind',
}

ERA5_COORD_MAP = {
    'latitude': 'lat',
    'longitude': 'lon',
}


def _find_nc_file():
    nc_files = list(RAW_DIR.glob("*.nc"))
    if nc_files:
        log.info(f"Real .nc file found: {nc_files[0]}")
        return nc_files[0]
    return None


def load_real_data(nc_path: Path) -> xr.Dataset:
    log.info(f"Loading real data from: {nc_path}")
    ds_raw = xr.open_dataset(nc_path, use_cftime=False)

    log.info(f"  Original variables : {list(ds_raw.data_vars)}")
    log.info(f"  Original coords    : {list(ds_raw.coords)}")
    log.info(f"  Dimensions         : {dict(ds_raw.dims)}")

    rename_vars = {}
    for orig_name in list(ds_raw.data_vars):
        mapped = ERA5_VAR_MAP.get(orig_name.lower(), ERA5_VAR_MAP.get(orig_name))
        if mapped and orig_name != mapped:
            rename_vars[orig_name] = mapped
    if rename_vars:
        log.info(f"  Renaming variables : {rename_vars}")
        ds_raw = ds_raw.rename(rename_vars)

    rename_coords = {}
    for orig_name in list(ds_raw.coords):
        mapped = ERA5_COORD_MAP.get(orig_name.lower())
        if mapped and orig_name != mapped:
            rename_coords[orig_name] = mapped
    if rename_coords:
        log.info(f"  Renaming coords    : {rename_coords}")
        ds_raw = ds_raw.rename(rename_coords)

    keep = [v for v in ['tas', 'pr', 'sfcWind'] if v in ds_raw]
    if not keep:
        raise ValueError(
            f"No recognizable climate variables found.\n"
            f"File variables: {list(ds_raw.data_vars)}\n"
            f"Expected one of: {list(ERA5_VAR_MAP.keys())}"
        )
    ds = ds_raw[keep]

    if 'tas' in ds:
        tas_min = float(ds['tas'].isel(time=0).min().values)
        if tas_min < 200:
            log.info("  Converting temperature: Celsius to Kelvin (+273.15)")
            ds['tas'] = ds['tas'] + 273.15

    if 'pr' in ds:
        pr_max = float(ds['pr'].isel(time=0).max().values)
        if pr_max < 1.0:
            log.info("  Converting precipitation: metres to mm/day (x1000)")
            ds['pr'] = ds['pr'] * 1000.0
        ds['pr'] = ds['pr'].clip(min=0)

    if 'lat' in ds.coords:
        if float(ds['lat'].values[0]) > float(ds['lat'].values[-1]):
            log.info("  Flipping latitude north-to-south -> south-to-north")
            ds = ds.isel(lat=slice(None, None, -1))

    if 'tas' in ds:
        ds['tas'].attrs = {
            'long_name': 'Near-Surface Air Temperature',
            'standard_name': 'air_temperature', 'units': 'K',
            'source': str(nc_path.name),
        }
    if 'pr' in ds:
        ds['pr'].attrs = {
            'long_name': 'Precipitation',
            'standard_name': 'precipitation_flux', 'units': 'mm day-1',
            'source': str(nc_path.name),
        }
    if 'sfcWind' in ds:
        ds['sfcWind'].attrs = {
            'long_name': 'Near-Surface Wind Speed',
            'standard_name': 'wind_speed', 'units': 'm s-1',
            'source': str(nc_path.name),
        }

    ds.attrs = {
        'title': f'Climate Platform Dataset - {nc_path.name}',
        'institution': 'Climate Platform Lab',
        'source': f'Real data - {nc_path.name}',
        'Conventions': 'CF-1.10',
        'author': 'Saif Ud Din Khan',
        'data_mode': 'REAL',
    }

    log.info(f"  Final variables : {list(ds.data_vars)}")
    log.info(f"  Final dims      : {dict(ds.dims)}")
    return ds


def generate_synthetic() -> xr.Dataset:
    log.info("No real data found -- generating realistic synthetic dataset ...")
    np.random.seed(RANDOM_SEED)

    time = pd.date_range(TIME_START, TIME_END, freq="MS")
    lat  = np.linspace(LAT_MIN, LAT_MAX, LAT_STEPS)
    lon  = np.linspace(LON_MIN, LON_MAX, LON_STEPS)

    n_t, n_y, n_x = len(time), len(lat), len(lon)
    t  = np.arange(n_t)[:, None, None]
    yy = lat[None, :, None]

    tas = (
        288.0
        + 12.0 * np.cos(np.deg2rad(yy))
        +  2.0 * np.sin(2 * np.pi * t / 12)
        +  0.02 * t
        + np.random.normal(0, 0.8, (n_t, n_y, n_x))
    ).astype("float32")

    pr = (
        3.0
        + 2.0 * np.maximum(0, np.cos(np.deg2rad(yy)))
        + 0.3 * np.sin(2 * np.pi * t / 12)
        + np.random.gamma(2.0, 0.3, (n_t, n_y, n_x))
    ).astype("float32")

    sfcwind = (
        5.0
        + 3.0 * np.abs(np.sin(np.deg2rad(yy) * 2))
        + np.random.normal(0, 0.5, (n_t, n_y, n_x))
    ).clip(0).astype("float32")

    ds = xr.Dataset(
        {
            'tas':     (('time', 'lat', 'lon'), tas),
            'pr':      (('time', 'lat', 'lon'), pr),
            'sfcWind': (('time', 'lat', 'lon'), sfcwind),
        },
        coords={'time': time, 'lat': lat, 'lon': lon},
    )

    ds['tas'].attrs     = {'long_name': 'Near-Surface Air Temperature',
                           'standard_name': 'air_temperature', 'units': 'K'}
    ds['pr'].attrs      = {'long_name': 'Precipitation',
                           'standard_name': 'precipitation_flux', 'units': 'mm day-1'}
    ds['sfcWind'].attrs = {'long_name': 'Near-Surface Wind Speed',
                           'standard_name': 'wind_speed', 'units': 'm s-1'}
    ds.attrs = {
        'title': 'Synthetic Climate Demo Dataset',
        'institution': 'Climate Platform Lab',
        'source': 'Synthetic - generate_data.py',
        'Conventions': 'CF-1.10',
        'author': 'Saif Ud Din Khan',
        'data_mode': 'SYNTHETIC',
    }

    log.info(f"  Synthetic dims: time={n_t}, lat={n_y}, lon={n_x}")
    return ds


def run() -> xr.Dataset:
    ensure_dirs()

    nc_file = _find_nc_file()

    if nc_file is not None:
        log.info("=" * 50)
        log.info("MODE: REAL DATA")
        log.info("=" * 50)
        try:
            ds = load_real_data(nc_file)
            ds.attrs['data_mode'] = 'REAL'
        except Exception as e:
            log.warning(f"Real data load failed: {e}")
            log.warning("Falling back to synthetic data ...")
            ds = generate_synthetic()
            ds.attrs['data_mode'] = 'SYNTHETIC_FALLBACK'
    else:
        log.info("=" * 50)
        log.info("MODE: SYNTHETIC (no .nc file in data/raw/)")
        log.info("=" * 50)
        log.info("To use real ERA5 data:")
        log.info("  1. python scripts/download_era5.py")
        log.info("  2. Place .nc file in: data/raw/")
        log.info("  3. Re-run: python -m src.pipeline")
        ds = generate_synthetic()

    if RAW_NC.exists():
        RAW_NC.unlink()
    ds.to_netcdf(RAW_NC)

    log.info(f"Dataset saved -> {RAW_NC}")
    log.info(f"  data_mode  : {ds.attrs.get('data_mode')}")
    log.info(f"  variables  : {list(ds.data_vars)}")
    log.info(f"  dimensions : {dict(ds.dims)}")

    return ds


if __name__ == "__main__":
    run()
