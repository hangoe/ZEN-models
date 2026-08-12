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

# --- MGA plugin support -- only needed if you'll run an MGA sweep --------------
# (submit_euler_mga.sh / parameters_mga.csv). Skip this block if you only use
# the normal (non-MGA) sweep. Neither package is on PyPI; both are pip-editable
# git repos, same pattern as the zen_garden install above.
if [[ ! -d "$HOME/ZEN-garden-plugins" ]]; then
    git clone https://github.com/hangoe/ZEN-garden-plugins.git "$HOME/ZEN-garden-plugins"
fi
python -m pip install -e "$HOME/ZEN-garden-plugins"

if [[ ! -d "$HOME/near_optimal_tools" ]]; then
    git clone https://github.com/evrenmturan/near_optimal_tools.git "$HOME/near_optimal_tools"
fi
# "[bbo]" pulls in pypop7, needed for MGA's bbo mode (black-box direction
# search); sampling/oracle/weights modes work without it too, so it's safe
# to always install.
python -m pip install -e "$HOME/near_optimal_tools[bbo]"

# --- Sanity check ---------------------------------------------------------------
echo "Verifying imports..."
python -c "import pandas, numpy; print('base imports OK')"
python -c "from zen_garden import run, Results; print('zen_garden OK')" || \
    echo "zen_garden not importable yet — pick the correct OPTION above and re-run."

echo "Verifying MGA plugin wiring..."
python -c "
from importlib.metadata import entry_points
names = [e.name for e in entry_points(group='zen_garden.plugins')]
print('registered plugins:', names)
assert 'mga' in names, 'mga entry point not registered - check the zen_garden version installed above'
" || echo "mga plugin not registered — your zen_garden may not be entry-point-aware, see euler/README_euler.md."
python -c "import pyoNearOpt; print('pyoNearOpt OK')" || \
    echo "pyoNearOpt not importable yet — check the near_optimal_tools install above."
python -c "import pypop7; print('pypop7 (bbo mode) OK')" || \
    echo "pypop7 not importable yet — bbo mode needs the '[bbo]' extra on the near_optimal_tools install above."

echo "Done. submit_euler.sh / submit_euler_mga.sh will 'source $HOME/ZEN-models/.venv/bin/activate'."
