#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# clean_and_run.sh
# Deletes ALL old cached data and reruns pipeline fresh
# Run this whenever you change TIME_START / TIME_END in config.py
# ─────────────────────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "=================================================="
echo " Cleaning old cached data ..."
echo "=================================================="

rm -f data/raw/*.nc
rm -f data/processed/*.nc
rm -rf data/zarr/*
rm -f outputs/reports/*.csv
rm -f outputs/figures/*.png

echo " Old data deleted."
echo ""
echo " Running fresh pipeline ..."
echo "=================================================="

# Activate venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

python -m src.pipeline

echo ""
echo "=================================================="
echo " Done! Launch dashboard:"
echo " streamlit run app.py"
echo "=================================================="
