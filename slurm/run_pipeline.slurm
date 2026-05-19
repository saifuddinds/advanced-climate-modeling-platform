#!/bin/bash
#SBATCH --job-name=climate_platform
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=logs/slurm_%j.out
#SBATCH --error=logs/slurm_%j.err
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=saifuddinds01@gmail.com

# ─────────────────────────────────────────────────────────────────────────────
# Advanced Climate Modeling Platform — SLURM HPC Job Script
#
# Architecture evidence:
# This script demonstrates how this platform would be submitted on a real
# HPC cluster running Slurm (e.g., NCAR Derecho, ECMWF Atos, university clusters).
#
# Viva line:
# "I wrote a SLURM job script to demonstrate how the pipeline would be
# scheduled on a real HPC cluster — the same approach used with CESM, MPAS,
# and NEMO production runs."
# ─────────────────────────────────────────────────────────────────────────────

echo "================================================================"
echo "  Climate Platform HPC Job"
echo "  Job ID     : $SLURM_JOB_ID"
echo "  Node       : $SLURM_NODELIST"
echo "  CPUs       : $SLURM_CPUS_PER_TASK"
echo "  Start time : $(date)"
echo "================================================================"

# Load required modules (typical HPC module system)
# module load python/3.11
# module load netcdf/4.9.0
# module load hdf5/1.12.2
# module load openmpi/4.1.4

# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export DASK_SCHEDULER="synchronous"

# Move to project directory
cd $SLURM_SUBMIT_DIR

# Print environment info
echo "Python: $(which python)"
echo "Python version: $(python --version)"
echo ""

# Run the full pipeline
echo "Starting pipeline..."
python -m src.pipeline

EXIT_CODE=$?

echo ""
echo "================================================================"
echo "  Job completed with exit code: $EXIT_CODE"
echo "  End time: $(date)"
echo "================================================================"

exit $EXIT_CODE
