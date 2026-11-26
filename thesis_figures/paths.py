"""Repository paths used by the figure code (one place, no hard-coded paths elsewhere)."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = REPO_ROOT / "data"
DATASETS_DIR = DATA_DIR / "datasets"
SINGLE_RESULTS_DIR = DATA_DIR / "results" / "single"
MGA_RESULTS_DIR = DATA_DIR / "results" / "mga"
NATURAL_EARTH_DIR = DATA_DIR / "naturalearth"

# Euler resources of single cost-optimal solves (sacct), written by prep/import_slurm_usage.py
SINGLE_SOLVE_USAGE_DIR = DATA_DIR / "results" / "slurm_usage_single_solves"

FIGURES_DIR = REPO_ROOT / "figures"  # figures/report/, figures/presentation/
TABLES_DIR = FIGURES_DIR / "tables"

RUNS_DIR = REPO_ROOT / "runs"
MGA_RUNS_CSV = RUNS_DIR / "mga_runs.csv"
