#!/bin/bash
###############################################################################
# submit_euler_mga.sh — run run_model.py against parameters_mga.csv as a
# SLURM array sweep on Euler (the MGA counterpart of submit_euler.sh).
#
# One array task = one row of parameters_mga.csv (selected by
# SLURM_ARRAY_TASK_ID; the row's own task_id value, NOT its position in the
# file). Current rows:
#   task_id 7  = batch bbo minmax batch4, capex_periods axes (historical --
#                left over from before the MGA plugin's periods->cumulative
#                axis rename; kept as-is, don't resubmit without first
#                updating config_mga_axes_capex_periods.json to the new
#                node_capex_cumulative schema)
#   task_id 9  = batch bbo minmax batch4, capex_cum axes (node_capex_cumulative,
#                until_years=[2040, 2050]; batch_size=n_workers=4)
#   task_id 10 = batch bbo share  batch4, capex_cum axes (same axes, "share"
#                normalisation instead of "minmax")
#   task_id 11 = batch bbo minmax batch6, capex_cum axes (batch_size=n_workers=6;
#                changed from batch8 on 2026-09-01 -- its earlier CONVERGED
#                result was under batch_size=8 and no longer matches this row)
#   task_id 12 = batch bbo share  batch6, capex_cum axes (was batch8)
#   task_id 13 = batch bbo share  batch4, capex_cum axes, tolerance_explore=0.01 (labeled _2030)
#   task_id 14 = batch bbo share  batch6, capex_cum axes, tolerance_explore=0.01 (labeled _2030; was batch8)
#   task_id 15 = batch bbo share  batch4, capex_cum axes, tolerance_explore=0.02
#                (FAILED on 2026-09-01, job 12374944_15: batch_ORACLE's
#                 add_cut() hit "Added cut but resulting outer approximation
#                 appears infeasible" -- a numerical issue in the exploration
#                 method itself, not a resource/config problem. Left as-is;
#                 see task_id 17 for the retry.)
#   task_id 16 = batch bbo share  batch6, capex_cum axes, tolerance_explore=0.02 (was batch8)
#   task_id 17 = retry of task_id 15 (batch bbo share batch4, capex_cum axes,
#                tolerance_explore=0.02) under a fresh task_id after the
#                2026-09-01 failure above
#   task_id 18 = copy of task_id 17 (batch bbo share batch4, capex_cum axes,
#                tolerance_explore=0.02) with aggregated_time_steps_per_year=10
#                instead of 3 (finer time series aggregation)
#   task_id 19 = copy of task_id 18 with interval_between_years=2 instead of 5
#                and optimized_years=16 instead of 7 (2020 + 15*2 = 2050, same
#                end year as task_id 17/18's 2020 + 6*5 = 2050, just evaluated
#                every 2 years instead of every 5)
#   task_id 20 = copy of task_id 17 (batch bbo share batch4, tolerance_explore=0.02,
#                7a/5a interval, 3ts/year) using the new node_capex_cumulative_tech
#                axes (config_mga_axes_capex_cum_tech.json: 4 regions x 3 tech
#                groups x until_years=[2030, 2040, 2050], i.e. capex_cum and capex
#                combined into one 3-way axis set) -- needs the not-yet-released
#                ZEN-garden-plugins MGA changes that add this axis kind. Untested;
#                run with --time=14-00:00:00 padded well above 17's 8d since the
#                combined axis set is much larger (4 nodes x 3 tech groups x 3
#                years = 36 capex axes vs. 17's 12).
#
# The old plain-CAPEX rows (former task_ids 0-6: sampling/bbo/batch_bbo
# minmax over the region x tech-group capex axes) and the CAPEX_PERIODS
# weights row (former task_id 8) were removed -- no longer needed. weights,
# oracle mode, "relative"/"units" normalisation and batch sampling
# (strategy_mode="sampling") aren't swept here either -- add a row to
# parameters_mga.csv (and a matching #SBATCH profile below) if you need any
# of them.
#
# Requires the MGA install step in setup_euler_env.sh to have been run once
# (clones + installs ZEN-garden-plugins and near_optimal_tools/pyoNearOpt,
# incl. the "bbo" extra needed by batch bbo mode).
#
# Resource profile per range. task_ids 9/10 (batch4) and 11/12 (batch6) size
# cpus-per-task as batch_size x 10, since each worker's solver requests
# Threads=10 -- so the worker pool actually gets dedicated cores per worker
# instead of batch_size workers dividing a flat core count. --time is padded
# to 72h flat for headroom. The #SBATCH block below is the batch6 profile
# (task_id 11/12), i.e. the safe default for a bare `sbatch
# submit_euler_mga.sh`; override per range on the command line (CLI flags
# win over #SBATCH) for the cheaper batch4 range instead of running
# everything at the batch6 profile:
#   sbatch --array=9,10,15,17                                             \
#          --time=8-00:00:00 --cpus-per-task=40  --mem-per-cpu=4G  \
#          submit_euler_mga.sh                # cum_capex batch4, minmax + share
#                                              # (--time bumped 6-06:00:00 -> 8-00:00:00
#                                              #  on 2026-09-01 for the task_id 17 retry;
#                                              #  normal.120h partition allows up to 15d)
#   sbatch --array=11,12,16                                               \
#          --time=6-06:00:00 --cpus-per-task=40  --mem-per-cpu=4G  \
#          submit_euler_mga.sh                # cum_capex batch6, minmax + share
#   sbatch --array=9-17 submit_euler_mga.sh    # once you trust the walltime per range
#   sbatch --array=18,19                                                  \
#          --time=14-00:00:00 --cpus-per-task=40  --mem-per-cpu=4G  \
#          submit_euler_mga.sh                # cum_capex batch4, share, 10ts/year
#                                              # (18: 7a/5a interval; 19: 16a/2a interval,
#                                              #  both untested -- 14d padded well above
#                                              #  17's 8d since 10ts/year and (for 19) more
#                                              #  periods both add per-solve cost; still
#                                              #  within normal.120h's 15d cap)
#   sbatch --array=20                                                     \
#          --time=14-00:00:00 --cpus-per-task=40  --mem-per-cpu=4G  \
#          submit_euler_mga.sh                # capex_cum_tech (3-way node x tech
#                                              # x until_year axes), batch4, share,
#                                              # tolerance_explore=0.02; untested,
#                                              # 14d padded for the much larger
#                                              # (36-axis) polytope vs. 17's 12
#
# cpus-per-task=40, mem-per-cpu=4G (160G total), time=6-06:00:00 for BOTH
# ranges -- this is the profile that actually completed task_id 9/10/11
# (job 11966251, 2026-08-27), not the #SBATCH defaults below (those were
# never exercised by a real run and are unverified; the 72h #SBATCH default
# in particular is short -- task_id 9 took 2d18h and task_id 11 took 4d
# under this profile). task_id 10/13 (share, tolerance_explore) were
# OOM-killed at 40 cpus x 1G (40G total) on 2026-08-28 (jobs
# 12067246_10/_13) -- 4G/cpu fixes that.
###############################################################################

#SBATCH --job-name=zen_run_mga
#SBATCH --time=72:00:00              # TUNABLE: batch6 profile; override per range, see above
#SBATCH --ntasks=1                   # one process per array task -> keep at 1
#SBATCH --cpus-per-task=60           # TUNABLE: batch6 profile (6 workers x 10 threads); override per range, see above
#SBATCH --mem-per-cpu=1G              # TUNABLE: batch6 profile (~60GB total); override per range, see above
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
