#!/bin/bash
###############################################################################
# ZEN-models SLURM array job for Euler  (corrected version of Jan's script)
#
# Key differences from the original:
#   * Does NOT create the venv inside the job (that produced an empty env and
#     4 array tasks corrupting the same .venv). It only ACTIVATES a venv you
#     built once beforehand with setup_euler_env.sh.
#   * Resource requests are marked as TUNABLES — do one calibration run first
#     (sbatch --array=12 ...), read usage with `myjobs`/`sacct`, then trim.
#   * Results go to scratch via run_settings.json (euler.root_path), not here.
#
# Submit from the repo dir that contains Run_array.xlsx and run_settings.json:
#   sbatch --array=12       submit_zen_garden.sh    # first: ONE task, calibrate
#   sbatch --array=13-15    submit_zen_garden.sh    # then the rest
###############################################################################

#SBATCH --job-name=zen_garden
#SBATCH --time=08:00:00              # TUNABLE: overestimate first, then trim (max 15 days)
#SBATCH --ntasks=1                   # one process per array task -> keep at 1
#SBATCH --cpus-per-task=16           # TUNABLE: cores for Gurobi. Jan used 32; supervisor ref = 16
#SBATCH --mem-per-cpu=8G             # TUNABLE: RAM per core. Total = cpus-per-task x this (16x8 = 128 GB)
#SBATCH --output=zen_garden_%A_%a.out  # %A = array job id, %a = task id
#SBATCH --error=zen_garden_%A_%a.err
#SBATCH --array=12-15                # which task_ids from Run_array.xlsx (overridable on cmd line)
#SBATCH --mail-type=END,FAIL         # email when a task ends or fails (uses your ETH address)

set -euo pipefail

# --- 1. Software modules (order matters: stack -> compiler -> python -> gurobi) ---
module purge
module load stack/2024-06
module load gcc/12.2.0
module load python/3.12.8
module load gurobi/13.0.0

# --- 2. Activate the pre-built environment (created ONCE by setup_euler_env.sh) ---
VENV="$HOME/ZEN-models/.venv"
if [[ ! -f "$VENV/bin/activate" ]]; then
    echo "ERROR: venv not found at $VENV — run 'bash setup_euler_env.sh' first." >&2
    exit 1
fi
source "$VENV/bin/activate"

# --- 3. Run the model for this array task's task_id -------------------------------
#   IMPORTANT: replace 'main_run_mean_variance_snapshot' below with the real module
#   name if your entry file is actually run_model.py -> then use 'run_model'.
echo "Starting task_id=${SLURM_ARRAY_TASK_ID} on $(hostname) at $(date)"

python -m main_run_mean_variance_snapshot \
    --task_id "${SLURM_ARRAY_TASK_ID}" \
    --nr_time_steps 720 \
    --run_on euler

echo "Finished task_id=${SLURM_ARRAY_TASK_ID} at $(date)"
