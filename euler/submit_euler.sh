#!/bin/bash
###############################################################################
# submit_euler.sh -- run rows of runs/parameters.csv as a SLURM array on Euler.
#
# One array task = one row (task_id = SLURM_ARRAY_TASK_ID). Submit from the
# repository root:
#   sbatch --array=0-2,5-7,15,16 euler/submit_euler.sh   # thesis scenarios, 10 time steps
#   sbatch --array=9,10 euler/submit_euler.sh             # 20 time steps (more time/memory)
###############################################################################

#SBATCH --job-name=zen_run
#SBATCH --time=08:00:00              # TUNABLE: max 15 days
#SBATCH --ntasks=1                   # one process per array task -> keep at 1
#SBATCH --cpus-per-task=16           # TUNABLE: cores 
#SBATCH --mem-per-cpu=12G            # TUNABLE: RAM per core. Total = cpus-per-task x this (16x12 = 192 GB)
#SBATCH --output=zen_run_%A_%a.out   # %A = array id, %a = task id
#SBATCH --error=zen_run_%A_%a.err
#SBATCH --mail-type=END,FAIL         # email when a task ends/fails (ETH address)

set -euo pipefail

# --- 1. Software modules (stack -> compiler -> python -> solver) ------------------
module purge
module load stack/2024-06
module load gcc/12.2.0
module load python/3.12.8
module load gurobi/13.0.0            

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
