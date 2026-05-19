#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# run_pipeline.sh
# Runs the full climate platform pipeline on a local machine
# ─────────────────────────────────────────────────────────────────────────────

set -e   # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=================================================="
echo " Advanced Climate Modeling Platform"
echo " Project root: $PROJECT_DIR"
echo " Start: $(date)"
echo "=================================================="

cd "$PROJECT_DIR"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "Virtual environment: .venv"
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment: venv"
else
    echo "WARNING: No virtual environment found. Using system Python."
fi

echo "Python: $(which python)"

# Run pipeline
python -m src.pipeline

EXIT_CODE=$?

echo ""
echo "=================================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo " Pipeline COMPLETED successfully"
    echo " Launch dashboard: streamlit run app.py"
else
    echo " Pipeline FAILED with exit code $EXIT_CODE"
    echo " Check logs/ directory for details"
fi
echo " End: $(date)"
echo "=================================================="

exit $EXIT_CODE
