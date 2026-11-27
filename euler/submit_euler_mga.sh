#!/bin/bash
###############################################################################
# submit_euler_mga.sh -- run rows of runs/parameters_mga.csv as a SLURM array on
# Euler (the MGA counterpart of submit_euler.sh).
#
# One array task = one row, selected by its task_id column. Requires the MGA
# install step of setup_euler_env.sh (ZEN-garden-plugins and pyoNearOpt with
# the "bbo" extra). History of the runs: euler/MGA_RUN_HISTORY.md.
#
# cpus-per-task = batch_size x Gurobi threads per worker (solver_threads).
# Profiles of the thesis runs (CLI flags win over the #SBATCH defaults below);
# submit from the repository root:
#   sbatch --array=54 --cpus-per-task=128 --mem-per-cpu=5600M euler/submit_euler_mga.sh    # T1: 5 ts, 16 x 8 threads, ~700 GB
#   sbatch --array=65 --cpus-per-task=128 --mem-per-cpu=5600M euler/submit_euler_mga.sh    # T5 (T6 = 64 same profile)
#   sbatch --array=56,57,67 --time=5-00:00:00 --cpus-per-task=32 --mem-per-cpu=6G euler/submit_euler_mga.sh  # T2-T4: 1 ts, 16 x 2 threads
#   sbatch --array=21,32,33,45-47 --time=5-00:00:00 --cpus-per-task=32 --mem-per-cpu=6G euler/submit_euler_mga.sh  # Z runs (dataset not included)
# Refine a profile from `sacct -j <jobid> --format=JobID,Elapsed,MaxRSS,State`.
###############################################################################

#SBATCH --job-name=zen_run_mga
#SBATCH --time=14-00:00:00           # TUNABLE: standard profile (see above); this is the default now, no need to override
#SBATCH --ntasks=1                   # one process per array task -> keep at 1
#SBATCH --cpus-per-task=40           # TUNABLE: standard profile (4 workers x 10 threads)
#SBATCH --mem-per-cpu=4G             # TUNABLE: standard profile (160GB total); don't drop below 4G/cpu, see above
#SBATCH --output=zen_run_mga_%A_%a.out   # %A = array id, %a = task id
#SBATCH --error=zen_run_mga_%A_%a.err
#SBATCH --mail-type=END,FAIL         # email when a task ends/fails (ETH address)

set -euo pipefail

# --- 1. Software modules (stack -> compiler -> python -> solver) ------------------
module purge
module load stack/2024-06
module load gcc/12.2.0
module load python/3.12.8
module load gurobi/13.0.0            # oracle mode's baseline + max-min solves need Gurobi

# --- 2. Activate the environment you built ONCE with setup_euler_env.sh -----------
VENV="$HOME/ZEN-models/.venv"
if [[ ! -f "$VENV/bin/activate" ]]; then
    echo "ERROR: venv not found at $VENV — run 'bash setup_euler_env.sh' first." >&2
    exit 1
fi
source "$VENV/bin/activate"

# Each batch worker owns only its own Gurobi threads; left unset, the
# BLAS/numexpr/polars thread pools of every worker size themselves off the
# whole allocation and oversubscribe the node (pthread_create / fork failures,
# hung pools). Pinned to 1; Gurobi's threads are set via solver_options.
# Details: euler/MGA_RUN_HISTORY.md.
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export MKL_NUM_THREADS=1
export POLARS_MAX_THREADS=1

# --- 3. Run this array task's parameter row ----------------------------------------
echo "Starting MGA task_id=${SLURM_ARRAY_TASK_ID} on $(hostname) at $(date)"

python run_model.py \
    --task_id "${SLURM_ARRAY_TASK_ID}" \
    --run_on euler \
    --params runs/parameters_mga.csv

echo "Finished MGA task_id=${SLURM_ARRAY_TASK_ID} at $(date)"
