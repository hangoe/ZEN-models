#!/bin/bash
###############################################################################
# submit_euler_mga.sh — run run_model.py against parameters_mga.csv as a
# SLURM array sweep on Euler (the MGA counterpart of submit_euler.sh).
#
# One array task = one row of parameters_mga.csv (selected by SLURM_ARRAY_TASK_ID):
#   task_id 0  = weights          (cheapest, no pyoNearOpt/Gurobi-MILP)
#   task_id 1  = sampling units   (LP-only, iterative; formerly called
#                                   "probabilistic"; design axes kept in raw
#                                   physical units -- only sensible once the
#                                   selected axes share comparable units,
#                                   which the region x tech-group capex axes
#                                   now do: annualised CHF)
#   task_id 2  = sampling minmax  (same as task_id 1, but each axis's own
#                                   near-optimal [min, max] is mapped onto
#                                   [0, 1] instead of kept in raw units)
#   task_id 3  = bbo units        (LP-only support-function pipeline like
#                                   sampling, but directions come from a
#                                   black-box optimiser; needs pyoNearOpt's
#                                   "bbo" extra, see setup_euler_env.sh;
#                                   raw physical units)
#   task_id 4  = bbo minmax       (same as task_id 3, minmax normalisation)
#   task_id 5  = batch bbo units batch4    (batch mode, strategy_mode="bbo";
#                                            solves batch_size directions
#                                            concurrently per iteration via a
#                                            worker pool; batch_size=
#                                            n_workers=4; raw physical units)
#   task_id 6  = batch bbo units batch8    (same, batch_size=n_workers=8)
#   task_id 7  = batch bbo units batch16   (same, batch_size=n_workers=16)
#   task_id 8  = batch bbo minmax batch4   (same as task_id 5, minmax
#                                            normalisation)
#   task_id 9  = batch bbo minmax batch8   (same, batch_size=n_workers=8)
#   task_id 10 = batch bbo minmax batch16  (same, batch_size=n_workers=16)
#
# oracle mode and "relative" normalisation are deliberately not swept right
# now (oracle: too slow to calibrate walltime for yet; relative: superseded
# by units/minmax for these runs) -- config_mga_oracle.json and the
# "relative" normalisation still work if you add a row back manually. batch
# sampling (strategy_mode="sampling") is not swept either for now; use
# config_mga_batch_sampling.json the same way as config_mga_batch_bbo.json
# if you want it back.
#
# Requires the MGA install step in setup_euler_env.sh to have been run once
# (clones + installs ZEN-garden-plugins and near_optimal_tools/pyoNearOpt,
# incl. the "bbo" extra for task_ids 3-10).
#
# Resource profile per range, from sacct history on the old 8-axis capacity
# axes (weights ~5min/5.5GB; sampling+bbo 11-21h elapsed but only ~3-4/16
# cores average; batch4 7h47-9h50 elapsed, ~10.5/16 cores average, ~25.6-
# 27.5GB peak). Time is padded ~2.5x over the batch4 max for the new
# 12-axis region x tech-group capex axes, but held FLAT across batch4/8/16
# rather than scaled up with batch size: cpus-per-task stays 16 throughout
# (each worker's solver still requests Threads=10, unchanged, see git
# history), and max_iterations is fixed at 800 regardless of batch size, so
# more workers just divide the same 16 physical cores more ways -- it
# doesn't add compute, so there's no basis for batch8/16 taking dramatically
# longer than batch4 (batch8/16 are otherwise untested at those worker
# counts, hence still some padding on top of the batch4 number). Memory DOES
# scale with worker count (each worker holds its own model copy), so
# mem-per-cpu still climbs with batch size. The #SBATCH block below is the
# batch16 profile, i.e. the safe default for a bare `sbatch
# submit_euler_mga.sh`; override per range on the command line (CLI flags
# win over #SBATCH) for the cheaper ranges instead of running everything at
# the batch16 profile:
#   sbatch --array=0                                                      \
#          --time=1:00:00  --cpus-per-task=4  --mem-per-cpu=4G  \
#          submit_euler_mga.sh                # weights
#   sbatch --array=1-4                                                    \
#          --time=36:00:00 --cpus-per-task=12 --mem-per-cpu=2G  \
#          submit_euler_mga.sh                # sampling + bbo, units + minmax
#   sbatch --array=5,8                                                    \
#          --time=24:00:00 --cpus-per-task=16 --mem-per-cpu=4G  \
#          submit_euler_mga.sh                # batch bbo, batch4
#   sbatch --array=6,9                                                    \
#          --time=24:00:00 --cpus-per-task=16 --mem-per-cpu=6G  \
#          submit_euler_mga.sh                # batch bbo, batch8
#   sbatch --array=7,10                                                   \
#          submit_euler_mga.sh                # batch bbo, batch16 (script default)
#   sbatch --array=0-10 submit_euler_mga.sh    # once you trust the walltime per range
###############################################################################

#SBATCH --job-name=zen_run_mga
#SBATCH --time=24:00:00              # TUNABLE: batch16 profile; override per range, see above
#SBATCH --ntasks=1                   # one process per array task -> keep at 1
#SBATCH --cpus-per-task=16           # TUNABLE: batch16 profile; override per range, see above
#SBATCH --mem-per-cpu=7G              # TUNABLE: batch16 profile (~112GB total); override per range, see above
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
