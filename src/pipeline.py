"""
pipeline.py
-----------
Full automated pipeline. Run with: python -m src.pipeline

Works in 2 modes:
  - SYNTHETIC: no .nc file in data/raw/ -> auto-generates synthetic data
  - REAL:      ERA5 .nc file in data/raw/ -> loads and processes real data
"""

import time
import logging
import traceback
from datetime import datetime

from src.config import ensure_dirs, LOGS_DIR

ensure_dirs()
log_file = LOGS_DIR / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger(__name__)


def _run_step(name: str, func):
    log.info("=" * 60)
    log.info(f"STEP: {name}")
    log.info("=" * 60)
    t0 = time.time()
    try:
        result  = func()
        elapsed = time.time() - t0
        log.info(f"OK  {name} completed in {elapsed:.1f}s")
        return result
    except Exception as e:
        log.error(f"FAIL  {name}: {e}")
        log.error(traceback.format_exc())
        raise


def run():
    log.info("=" * 60)
    log.info("  Advanced Climate Modeling Platform -- Pipeline")
    log.info("  Author: Saif Ud Din Khan")
    log.info("=" * 60)
    pipeline_start = time.time()

    from src import generate_data, preprocess, analytics
    from src import climate_indices, ensemble, bias_correction
    from src import downscaling, visualizations, provenance

    steps = [
        ("1. Generate / Load Data",        generate_data.run),
        ("2. Preprocess (Chunk + Zarr)",   preprocess.preprocess),
        ("3. Analytics (Global Mean)",     analytics.run),
        ("4. Climate Indices (Extremes)",  climate_indices.run),
        ("5. Ensemble Uncertainty",        ensemble.run),
        ("6. Bias Correction",             bias_correction.run),
        ("7. Statistical Downscaling",     downscaling.run),
        ("8. Visualizations (Figures)",    visualizations.run),
        ("9. Provenance and Metadata",     provenance.run),
    ]

    for name, func in steps:
        _run_step(name, func)

    total = time.time() - pipeline_start
    log.info("=" * 60)
    log.info(f"PIPELINE COMPLETE in {total:.1f}s")
    log.info(f"Log: {log_file}")
    log.info("Launch dashboard: streamlit run app.py")
    log.info("=" * 60)


if __name__ == "__main__":
    run()
