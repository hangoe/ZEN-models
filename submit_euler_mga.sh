#!/bin/bash
###############################################################################
# submit_euler_mga.sh — run run_model.py against parameters_mga.csv as a
# SLURM array sweep on Euler (the MGA counterpart of submit_euler.sh).
#
# One array task = one row of parameters_mga.csv (selected by
# SLURM_ARRAY_TASK_ID; the row's own task_id value, NOT its position in the
# file). As of 2026-09-16, all 4 rows share the same MGA setup -- batch bbo,
# "share" normalisation, batch_size=n_workers=4, tolerance_explore=0.02,
# config_mga_axes_capex_cum.json (node_capex_cumulative axes), reference_year
# 2020 -- and only vary time series aggregation and the period schedule:
#   task_id 0 = aggregated_time_steps_per_year=1, optimized_years=7,
#               interval_between_years=5 (2020 -> 2050, 7 periods every 5y)
#   task_id 1 = same 7a/5a period schedule as task_id 0, but
#               aggregated_time_steps_per_year=3 (finer time series
#               aggregation); config-identical to the former task_id 17
#               (batch4, share, tol0.02, 3ts/year, 7a/5a), just renumbered
#   task_id 2 = same 7a/5a period schedule as task_id 0/1, but
#               aggregated_time_steps_per_year=10 (even finer aggregation);
#               config-identical to the former task_id 18
#   task_id 3 = aggregated_time_steps_per_year=3, optimized_years=4,
#               interval_between_years=10 (2020 -> 2050, same end year as
#               task_id 0-2, but only 4 periods spaced every 10y instead of
#               7 periods every 5y)
#
# parameters_mga.csv was trimmed down to just these 4 rows on 2026-09-16
# (commit "adapt tasks to submit"); the former task_ids 7, 9-20 -- covering
# minmax normalisation, batch6, capex_periods axes, tolerance_explore=0.01,
# a 16a/2a interval variant and the capex_cum_tech axes -- were dropped. See
# `git log -p -- parameters_mga.csv` for those removed rows if you need to
# resurrect one; re-add it (and a matching #SBATCH profile below) rather
# than reusing a task_id number that's been retired. weights, oracle mode,
# "relative"/"units" normalisation and batch sampling (strategy_mode=
# "sampling") aren't swept here either -- add a row for any of those too.
#
# 3 more rows added 2026-09-17, all config-identical to task_id 0
# (1ts/7a/5a) except as noted -- fig3a/3b comparison runs, see
# scripts/plot_mga_ts_resolution.py's TS_RUNS/TS_COLOR:
#   task_id 4 = seed_rng=42 (task_id 0 itself has no seed_rng set --
#               batch_oracle's BBO restarts/direction fallbacks then seed
#               nondeterministically from OS entropy, see run_model.py's
#               module docstring -- so this is a same-config, explicit-seed
#               run to compare against task_id 0's unpinned draw, not a
#               "different seed from task_id 0's seed" since task_id 0
#               never had one). Same batch4/40cpu/4G profile as task_id 0.
#   task_id 5 = batch_size=n_workers=16 (vs. 4), solver_threads=2 (vs. the
#               config's default 10) -- needs its own #SBATCH profile, see
#               below.
#   task_id 6 = batch_size=n_workers=32, solver_threads=2 -- same reasoning
#               as task_id 5, needs its own #SBATCH profile too.
#
# task_id 7 added 2026-09-18 (commits "new run with 48 axes added for
# testing" + "adapt solver threads") -- a different axes config from
# task_id 0-6, not another share/capex_cum variant:
#   task_id 7 = axes_config=config_mga_axes_total.json (48 axes: node_capex_
#               cumulative and node_carbon_emissions_cumulative each give
#               4 regions x 3 until_years, node_capacity_ratio gives 4
#               regions x 3 years x 2 ratio_groups -- vs. task_id 0-6's
#               12-axis config_mga_axes_capex_cum.json), normalisation=
#               per_axes (not share/minmax), tolerance_explore=0.1 (vs.
#               0.02), epsilon=0.07 (vs. the config's default 0.01),
#               batch_size=n_workers=16, solver_threads=2 -- same batch/
#               thread shape as task_id 5, so it needs task_id 5's #SBATCH
#               profile below, not the 40cpu/4G standard. No prior
#               completed run at any profile for this row, and 4x the axes
#               of task_id 0-6 means more per_axes directions to explore
#               per batch -- treat --time as unverified too, not just
#               --mem-per-cpu/--cpus-per-task.
#
# Requires the MGA install step in setup_euler_env.sh to have been run once
# (clones + installs ZEN-garden-plugins and near_optimal_tools/pyoNearOpt,
# incl. the "bbo" extra needed by batch bbo mode).
#
# Resource profile. task_id 0-4 use batch_size=n_workers=4, so cpus-per-task
# is sized as 4 workers x 10 threads/worker = 40, since each worker's solver
# requests Threads=10 -- the worker pool needs dedicated cores per worker
# instead of dividing a flat core count. mem-per-cpu=4G (160G total): task_id
# 10/13 (the former share/tolerance_explore rows, same normalisation as
# today's rows) were OOM-killed at 40 cpus x 1G on 2026-08-28 (jobs
# 12067246_10/_13), so don't drop below 4G/cpu. --time=14-00:00:00: the
# former task_id 17 (config-identical to today's task_id 1) completed in 8d
# at this cpu/mem profile (job 12374944 retry); 14d is the standard padding
# used for every row since, so this is the #SBATCH default below -- no need
# to pass --time/--cpus-per-task/--mem-per-cpu on the command line, just:
#   sbatch --array=0-4 submit_euler_mga.sh    # task_id 0-4, batch4/share/tol002
#
# task_id 5/6 use a bigger batch_size (16/32) than the config's default
# Threads=10 was tuned for; rather than scale cpus-per-task to
# batch_size x 10 (160/320 cores -- likely bigger than a single Euler node,
# and the exact profile that thread-thrashed/OOM'd the retired batch8/batch16
# rows once flat BLAS/numexpr thread pools oversubscribed it, see this
# script's OPENBLAS_NUM_THREADS etc. exports below), each row's own
# solver_threads column pins Gurobi's per-worker Threads down to 2, so
# cpus-per-task only needs batch_size x 2 cores -- pass that as an explicit
# CLI override (CLI flags win over the #SBATCH defaults above), since these
# 2 rows don't fit the 40cpu/4G standard profile:
#   sbatch --array=5 --cpus-per-task=32 --mem-per-cpu=6G submit_euler_mga.sh   # task_id 5: batch16, 32cpu/192GB
#   sbatch --array=6 --cpus-per-task=64 --mem-per-cpu=6G submit_euler_mga.sh   # task_id 6: batch32, 64cpu/384GB
# None of task_id 5/6/7 has a prior completed run at this profile (unlike
# the 14d/40cpu/4G standard, backed by job 12374944_17's own 8d completion)
# -- watch their first attempts and adjust --time/--mem-per-cpu if they OOM
# or run long.
#
# task_id 7 shares task_id 5's batch16/solver_threads=2 shape, so the same
# 32cpu/192GB override applies -- but it's also the first run of the
# per_axes/axes_total (48-axis) combination, so --time=14-00:00:00 (the
# #SBATCH default) is an untested guess here, not a validated floor like it
# is for task_id 0-4:
#   sbatch --array=7 --cpus-per-task=32 --mem-per-cpu=6G submit_euler_mga.sh   # task_id 7: batch16/per_axes/axes_total, 32cpu/192GB, time unverified
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

# Every current row runs batch bbo mode, which forks/spawns batch_size worker
# PROCESSES, each with its own dedicated 10 cpus for Gurobi
# (solver_options["Threads"]=10 already accounts for those). Left unset,
# numpy/pandas/numexpr inside each worker separately try to size their own
# BLAS/numexpr thread pools off the allocation's full cpus-per-task
# (batch_size x 10) rather than the 10 cpus that worker actually owns --
# batch_size of them doing that concurrently oversubscribes the node's
# process/thread budget. Seen on old batch8/batch16 rows (job 11281957,
# task_ids retired since): repeated "OpenBLAS blas_thread_init:
# pthread_create failed ... Resource temporarily unavailable", then a worker
# died mid `import numpy` during pool (re)spawn, and the pool's `close()` ->
# `executor.shutdown(wait=True)` hung waiting on it -- both runs sat idle for
# ~3 days until SLURM killed them at --time, having made zero progress past
# the first outer iteration. A batch4 row hit the same warning 3x but had
# enough headroom to survive and complete normally -- which is the batch_size
# all 4 current rows use. Pinning these to 1 removes the oversubscription;
# Gurobi's own thread count is unaffected since it's set explicitly via
# solver_options, not these vars.
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
