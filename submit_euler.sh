#!/bin/bash
###############################################################################
# submit_euler.sh — run YOUR run_model.py as a SLURM array sweep on Euler.
#
# One array task = one row of parameters.csv (selected by SLURM_ARRAY_TASK_ID).
# This is your own file — it does not depend on Jan's setup.
#
# Submit from the ZEN-models directory (where run_model.py + parameters.csv are):
#   sbatch --array=0        submit_euler.sh     # calibrate: run ONE row first
#   sbatch --array=1-4      submit_euler.sh     # then the rest
#   sbatch --array=0-4      submit_euler.sh     # or all rows at once
#
# The --array range must match the task_id values in parameters.csv.
#
# TODO: switch parameters.csv (and this array range -> 0-5) to the v6_0
# datasets in ZEN-creator/outputs once the v6_0 results are ready. v6_0 adds
# a 6th scenario, Crystal_Ball_HG_v6_0_DSM_pessimistic (optimistic/pessimistic
# DSM variants for fig2b). See scripts/figure_settings.py for the matching
# TODO on EULER_SCENARIO_ORDER/LABELS/PALETTE.
###############################################################################

#SBATCH --job-name=zen_run
#SBATCH --time=04:00:00              # TUNABLE: overestimate first, then trim (max 15 days)
#SBATCH --ntasks=1                   # one process per array task -> keep at 1
#SBATCH --cpus-per-task=16           # TUNABLE: cores (e.g. for Gurobi threads)
#SBATCH --mem-per-cpu=8G             # TUNABLE: RAM per core. Total = cpus-per-task x this (16x8 = 128 GB)
#SBATCH --output=zen_run_%A_%a.out   # %A = array id, %a = task id
#SBATCH --error=zen_run_%A_%a.err
#SBATCH --mail-type=END,FAIL         # email when a task ends/fails (your ETH address)

set -euo pipefail

# --- 1. Software modules (stack -> compiler -> python -> solver) ------------------
module purge
module load stack/2024-06
module load gcc/12.2.0
module load python/3.12.8
module load gurobi/13.0.0            # remove if your model doesn't use Gurobi

# --- 2. Activate the environment you built ONCE with setup_euler_env.sh -----------
VENV="$HOME/ZEN-models/.venv"
if [[ ! -f "$VENV/bin/activate" ]]; then
    echo "ERROR: venv not found at $VENV — run 'bash setup_euler_env.sh' first." >&2
    exit 1
fi
source "$VENV/bin/activate"

# --- 3. Run this array task's parameter row ---------------------------------------
echo "Starting task_id=${SLURM_ARRAY_TASK_ID} on $(hostname) at $(date)"

python run_model.py \
    --task_id "${SLURM_ARRAY_TASK_ID}" \
    --run_on euler

echo "Finished task_id=${SLURM_ARRAY_TASK_ID} at $(date)"
