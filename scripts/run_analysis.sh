#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# run_analysis.sh
# Runs only the analytics steps (assumes data already generated)
# ─────────────────────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

if [ -d ".venv" ]; then source .venv/bin/activate
elif [ -d "venv" ]; then source venv/bin/activate; fi

echo "Running analytics steps only..."

python -c "from src import analytics; analytics.run()"
python -c "from src import climate_indices; climate_indices.run()"
python -c "from src import ensemble; ensemble.run()"
python -c "from src import bias_correction; bias_correction.run()"
python -c "from src import downscaling; downscaling.run()"
python -c "from src import visualizations; visualizations.run()"
python -c "from src import provenance; provenance.run()"

echo "Analysis steps complete."
echo "Launch dashboard: streamlit run app.py"
