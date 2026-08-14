#!/bin/bash
###############################################################################
# submit_euler_mga.sh — run run_model.py against parameters_mga.csv as a
# SLURM array sweep on Euler (the MGA counterpart of submit_euler.sh).
#
# One array task = one row of parameters_mga.csv (selected by SLURM_ARRAY_TASK_ID):
#   task_id 0 = weights           (cheapest, no pyoNearOpt/Gurobi-MILP)
#   task_id 1 = sampling relative (LP-only, cheaper than oracle but iterative;
#                                   formerly called "probabilistic"; axes
#                                   normalised to their near-optimal max)
#   task_id 2 = sampling units    (same as task_id 1, but design axes kept in
#                                   raw physical units -- only sensible once
#                                   the selected axes share comparable units)
#   task_id 3 = bbo relative      (LP-only support-function pipeline like
#                                   sampling, but directions come from a
#                                   black-box optimiser; needs pyoNearOpt's
#                                   "bbo" extra, see setup_euler_env.sh)
#   task_id 4 = bbo units         (same as task_id 3, raw physical units)
#   task_id 5 = oracle            (can be slow: up to 700 refinement
#                                   iterations, each an LP + MILP --
#                                   calibrate before trusting the --time
#                                   below; normalisation is always
#                                   "relative" in oracle mode)
#   task_id 6 = batch bbo units         (batch mode, strategy_mode="bbo";
#                                         solves batch_size directions
#                                         concurrently per iteration via a
#                                         worker pool; batch_size=n_workers=4
#                                         for now, needs pyoNearOpt's "bbo"
#                                         extra like task_ids 3-4; design axes
#                                         kept in raw physical units)
#   task_id 7 = batch sampling units    (same, strategy_mode="sampling",
#                                         batch_size=n_workers=4 for now,
#                                         raw physical units)
#   task_id 8 = batch bbo relative      (same as task_id 6, but axes
#                                         normalised to their near-optimal
#                                         max instead of raw units)
#   task_id 9 = batch sampling relative (same as task_id 7, normalised)
#
# Requires the MGA install step in setup_euler_env.sh to have been run once
# (clones + installs ZEN-garden-plugins and near_optimal_tools/pyoNearOpt,
# incl. the "bbo" extra for task_ids 3-4, 6-9).
#
# Submit from the ZEN-models directory. sampling/bbo/oracle (1-5) are run
# first this round:
#   sbatch --array=1-5      submit_euler_mga.sh     # sampling, bbo, oracle
#   sbatch --array=1-2      submit_euler_mga.sh     # sampling, both modes
#   sbatch --array=3-4      submit_euler_mga.sh     # bbo, both modes
#   sbatch --array=5        submit_euler_mga.sh     # oracle, alone
#   sbatch --array=6-9      submit_euler_mga.sh     # batch, both strategies x both normalisations
#   sbatch --array=0        submit_euler_mga.sh     # weights, once needed
#   sbatch --array=0-9      submit_euler_mga.sh      # once you trust the walltime
###############################################################################

#SBATCH --job-name=zen_run_mga
#SBATCH --time=48:00:00              # TUNABLE: oracle mode may need much longer/shorter -- calibrate per row
#SBATCH --ntasks=1                   # one process per array task -> keep at 1
#SBATCH --cpus-per-task=16           # TUNABLE: cores
#SBATCH --mem-per-cpu=8G             # TUNABLE: RAM per core. Total = cpus-per-task x this (e.g. 16x8 = 128 GB)
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

# --- 3. Run this array task's parameter row ----------------------------------------
echo "Starting MGA task_id=${SLURM_ARRAY_TASK_ID} on $(hostname) at $(date)"

python run_model.py \
    --task_id "${SLURM_ARRAY_TASK_ID}" \
    --run_on euler \
    --params parameters_mga.csv

echo "Finished MGA task_id=${SLURM_ARRAY_TASK_ID} at $(date)"
