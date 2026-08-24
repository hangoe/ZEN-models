#!/bin/bash
###############################################################################
# submit_euler_mga.sh — run run_model.py against parameters_mga.csv as a
# SLURM array sweep on Euler (the MGA counterpart of submit_euler.sh).
#
# Only the minmax runs are swept right now, renumbered to a contiguous
# 0-4 range. One array task = one row of parameters_mga.csv (selected by
# SLURM_ARRAY_TASK_ID; the row's own task_id value, NOT its position in the
# file):
#   task_id 0  = sampling minmax  (LP-only, iterative; formerly called
#                                   "probabilistic"; each axis's own
#                                   near-optimal [min, max] is mapped onto
#                                   [0, 1])
#   task_id 1  = bbo minmax       (LP-only support-function pipeline like
#                                   sampling, but directions come from a
#                                   black-box optimiser; needs pyoNearOpt's
#                                   "bbo" extra, see setup_euler_env.sh)
#   task_id 2  = batch bbo minmax batch4   (batch mode, strategy_mode="bbo";
#                                            solves batch_size directions
#                                            concurrently per iteration via a
#                                            worker pool; batch_size=
#                                            n_workers=4)
#   task_id 3  = batch bbo minmax batch8   (same, batch_size=n_workers=8)
#   task_id 4  = batch bbo minmax batch16  (same, batch_size=n_workers=16)
#
# weights and the units-normalisation runs (former task_ids 0, 1, 3, 5, 6, 7
# in the old 0-10 numbering) are deliberately dropped from this sweep for
# now -- add rows back to parameters_mga.csv (and re-add their #SBATCH
# profile below) if you need them again. oracle mode and "relative"
# normalisation are also not swept (oracle: too slow to calibrate walltime
# for yet; relative: superseded by minmax for these runs) --
# config_mga_oracle.json and the "relative" normalisation still work if you
# add a row back manually. batch sampling (strategy_mode="sampling") is not
# swept either for now; use config_mga_batch_sampling.json the same way as
# config_mga_batch_bbo.json if you want it back.
#
# Requires the MGA install step in setup_euler_env.sh to have been run once
# (clones + installs ZEN-garden-plugins and near_optimal_tools/pyoNearOpt,
# incl. the "bbo" extra for task_ids 1-4).
#
# Resource profile per range. task_ids 0 and 1 (sampling/bbo, no worker
# pool) keep the original 4 cpus-per-task / 2G-per-cpu profile (8GB total).
# task_ids 2-4 (batch bbo) now size cpus-per-task as batch_size x 10, since
# each worker's solver requests Threads=10 (unchanged, see git history) --
# so the worker pool actually gets dedicated cores per worker instead of
# batch_size workers dividing a flat core count. mem-per-cpu is dropped to
# 1G for these (memory scales with cpus-per-task instead). --time is padded
# to 72h flat across all five task_ids for headroom. The #SBATCH block below
# is the batch16 profile (task_id 4), i.e. the safe default for a bare
# `sbatch submit_euler_mga.sh`; override per range on the command line (CLI
# flags win over #SBATCH) for the cheaper ranges instead of running
# everything at the batch16 profile:
#   sbatch --array=0,1                                                    \
#          --time=72:00:00 --cpus-per-task=4   --mem-per-cpu=2G  \
#          submit_euler_mga.sh                # sampling + bbo, minmax
#   sbatch --array=2                                                      \
#          --time=72:00:00 --cpus-per-task=40  --mem-per-cpu=1G  \
#          submit_euler_mga.sh                # batch bbo minmax, batch4
#   sbatch --array=3                                                      \
#          --time=72:00:00 --cpus-per-task=80  --mem-per-cpu=1G  \
#          submit_euler_mga.sh                # batch bbo minmax, batch8
#   sbatch --array=4                                                      \
#          submit_euler_mga.sh                # batch bbo minmax, batch16 (script default)
#   sbatch --array=0-4 submit_euler_mga.sh     # once you trust the walltime per range
###############################################################################

#SBATCH --job-name=zen_run_mga
#SBATCH --time=72:00:00              # TUNABLE: batch16 profile; override per range, see above
#SBATCH --ntasks=1                   # one process per array task -> keep at 1
#SBATCH --cpus-per-task=160          # TUNABLE: batch16 profile (16 workers x 10 threads); override per range, see above
#SBATCH --mem-per-cpu=1G              # TUNABLE: batch16 profile (~160GB total); override per range, see above
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

# task_ids 2-4 (batch bbo) fork/spawn batch_size worker PROCESSES, each with
# its own dedicated 10 cpus for Gurobi (solver_options["Threads"]=10 already
# accounts for those). Left unset, numpy/pandas/numexpr inside each worker
# separately try to size their own BLAS/numexpr thread pools off the
# allocation's full cpus-per-task (batch_size x 10) rather than the 10 cpus
# that worker actually owns -- batch_size of them doing that concurrently
# oversubscribes the node's process/thread budget. Seen on batch8/batch16
# (11281957_3/_4): repeated "OpenBLAS blas_thread_init: pthread_create
# failed ... Resource temporarily unavailable", then a worker died mid
# `import numpy` during pool (re)spawn, and the pool's `close()` ->
# `executor.shutdown(wait=True)` hung waiting on it -- both runs sat idle
# for ~3 days until SLURM killed them at --time, having made zero progress
# past the first outer iteration. batch4 (task_id 2, 4 workers) hit the same
# warning 3x but had enough headroom to survive and complete normally.
# Pinning these to 1 removes the oversubscription; Gurobi's own thread count
# is unaffected since it's set explicitly via solver_options, not these vars.
#
# Same issue hit polars (pulled in transitively via linopy, which builds the
# LP model in each worker) on a batch16 rerun: its Rust async executor sizes
# its own thread pool off the full cpus-per-task allocation the same way
# OpenBLAS did, so 16 workers doing that concurrently panicked with
# "async-executor-N ... WouldBlock: Resource temporarily unavailable", and
# once enough threads/processes had piled up, even Python's own
# multiprocessing fork() started failing the same way
# (BlockingIOError: [Errno 11] Resource temporarily unavailable). Pinned the
# same way as the BLAS libs above.
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
