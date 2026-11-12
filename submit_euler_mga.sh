#!/bin/bash
###############################################################################
# submit_euler_mga.sh -- run run_model.py against parameters_mga.csv as a
# SLURM array sweep on Euler (the MGA counterpart of submit_euler.sh).
#
# One array task = one row of parameters_mga.csv, selected by its task_id
# column (not its position). All rows run batch mode (bbo strategy) on the
# ZEN-europe dataset; see the CSV for each row's settings. The history of
# the rows and of these profiles is in euler/MGA_RUN_HISTORY.md.
#
# Requires the MGA install step of setup_euler_env.sh (ZEN-garden-plugins and
# pyoNearOpt with the "bbo" extra).
#
# cpus-per-task = batch_size x Gurobi threads per worker. The #SBATCH
# defaults below are the standard profile (batch4 x 10 threads, 160 GB;
# don't go below 4G/cpu). Rows with solver_threads=2 need batch_size x 2
# cores, passed on the command line (CLI flags win over #SBATCH):
#   sbatch --array=0-4 submit_euler_mga.sh                                      # capex_cum, share, batch4
#   sbatch --array=5 --cpus-per-task=32 --mem-per-cpu=6G submit_euler_mga.sh    # batch16
#   sbatch --array=6 --cpus-per-task=64 --mem-per-cpu=6G submit_euler_mga.sh    # batch32
#   sbatch --array=7 --cpus-per-task=32 --mem-per-cpu=6G submit_euler_mga.sh    # axes_total, per_axes, batch16
#   sbatch --array=10 --time=08:00:00 --cpus-per-task=8 --mem-per-cpu=6G submit_euler_mga.sh     # emissions, test
#   sbatch --array=11 --time=1-00:00:00 --cpus-per-task=8 --mem-per-cpu=6G submit_euler_mga.sh   # axes_total, test
#   sbatch --array=12 --time=1-00:00:00 --cpus-per-task=32 --mem-per-cpu=4G submit_euler_mga.sh  # axes_total, 3 iter
#   sbatch --array=13 --time=4-00:00:00 --cpus-per-task=32 --mem-per-cpu=4G submit_euler_mga.sh  # axes_total, full
#   sbatch --array=14,16,18 --time=02:00:00 --cpus-per-task=8 --mem-per-cpu=6G submit_euler_mga.sh    # output-ratio tests
#   sbatch --array=15,17,19 --time=4-00:00:00 --cpus-per-task=32 --mem-per-cpu=5G submit_euler_mga.sh # output-ratio full
#   sbatch --array=20 --time=02:00:00 --cpus-per-task=8 --mem-per-cpu=6G submit_euler_mga.sh          # CO2 fix, test
#   sbatch --array=21 --time=4-00:00:00 --cpus-per-task=32 --mem-per-cpu=6G submit_euler_mga.sh # CO2 fix, full (22/23: same flags)
#   sbatch --array=30 --time=02:00:00 --cpus-per-task=8 --mem-per-cpu=6G submit_euler_mga.sh          # 1 region + CO2 storage, test
#   sbatch --array=31 --time=4-00:00:00 --cpus-per-task=32 --mem-per-cpu=6G submit_euler_mga.sh # 1 region + CO2 storage, full (refine from task 30)
#   sbatch --array=32 --time=5-00:00:00 --cpus-per-task=32 --mem-per-cpu=6G submit_euler_mga.sh # as 31, tol 0.15, 700 iterations
#   sbatch --array=44 --cpus-per-task=128 --mem-per-cpu=5G submit_euler_mga.sh               # 5ts, batch16 x 8 threads, 640 GB -> bigmem/fat nodes only
#   sbatch --array=45 --time=5-00:00:00 --cpus-per-task=32 --mem-per-cpu=6G submit_euler_mga.sh # as 44 with 1ts, 2 threads (run 33's profile)
# Refine a profile from `sacct -j <jobid> --format=JobID,Elapsed,MaxRSS,State`
# of the previous run.
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
    --params parameters_mga.csv

echo "Finished MGA task_id=${SLURM_ARRAY_TASK_ID} at $(date)"
