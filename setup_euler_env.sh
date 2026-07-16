#!/bin/bash
###############################################################################
# ONE-TIME environment setup for your ZEN-garden runs on Euler.
# Run ONCE on a login node (light: pip installs only). NOT inside a job.
#
#   cd /cluster/home/<user>/ZEN-models
#   bash setup_euler_env.sh
#
# Creates .venv in the repo with everything run_model.py needs, so the SLURM job
# (submit_euler.sh) only has to `source` it.
###############################################################################

set -euo pipefail

# --- Same modules the job uses (must match submit_euler.sh) ---
module purge
module load stack/2024-06
module load gcc/12.2.0
module load python/3.12.8
module load gurobi/13.0.0

# --- Create the venv in the repo (Home) ---
cd "$HOME/ZEN-models"
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# --- Install run_model.py's direct dependencies ---
python -m pip install pandas numpy

# --- Install zen_garden --  CHOOSE ONE OPTION and uncomment it ------------------
# Your script does `from zen_garden import run, Results`, so zen_garden must be
# importable. Pick the way your group ships it:
#
# OPTION A: ZEN-garden is a sibling source repo you install editable (most common):
python -m pip install -e "$HOME/ZEN-garden"
#
# OPTION B: it's installable from THIS repo:
# python -m pip install -e .
#
# OPTION C: there's a requirements.txt / environment file to follow:
# python -m pip install -r requirements.txt
#
# OPTION D: it's published on PyPI:
# python -m pip install zen-garden

# --- Sanity check ---------------------------------------------------------------
echo "Verifying imports..."
python -c "import pandas, numpy; print('base imports OK')"
python -c "from zen_garden import run, Results; print('zen_garden OK')" || \
    echo "zen_garden not importable yet — pick the correct OPTION above and re-run."

echo "Done. submit_euler.sh will 'source $HOME/ZEN-models/.venv/bin/activate'."
