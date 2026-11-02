# MGA run history

Notes moved verbatim (2026-10-30) out of the comments of `submit_euler_mga.sh`
and the docstring of `run_model.py`, so the scripts only describe what they do.
The task_ids refer to `parameters_mga.csv` at the time of writing.

## submit_euler_mga.sh: tasks and resource profiles

```text
submit_euler_mga.sh — run run_model.py against parameters_mga.csv as a
SLURM array sweep on Euler (the MGA counterpart of submit_euler.sh).

One array task = one row of parameters_mga.csv (selected by
SLURM_ARRAY_TASK_ID; the row's own task_id value, NOT its position in the
file). As of 2026-09-16, all 4 rows share the same MGA setup -- batch bbo,
"share" normalisation, batch_size=n_workers=4, tolerance_explore=0.02,
config_mga_axes_capex_cum.yaml (node_capex_cumulative axes), reference_year
2020 -- and only vary time series aggregation and the period schedule:
  task_id 0 = aggregated_time_steps_per_year=1, optimized_years=7,
              interval_between_years=5 (2020 -> 2050, 7 periods every 5y)
  task_id 1 = same 7a/5a period schedule as task_id 0, but
              aggregated_time_steps_per_year=3 (finer time series
              aggregation); config-identical to the former task_id 17
              (batch4, share, tol0.02, 3ts/year, 7a/5a), just renumbered
  task_id 2 = same 7a/5a period schedule as task_id 0/1, but
              aggregated_time_steps_per_year=10 (even finer aggregation);
              config-identical to the former task_id 18
  task_id 3 = aggregated_time_steps_per_year=3, optimized_years=4,
              interval_between_years=10 (2020 -> 2050, same end year as
              task_id 0-2, but only 4 periods spaced every 10y instead of
              7 periods every 5y)

parameters_mga.csv was trimmed down to just these 4 rows on 2026-09-16
(commit "adapt tasks to submit"); the former task_ids 7, 9-20 -- covering
minmax normalisation, batch6, capex_periods axes, tolerance_explore=0.01,
a 16a/2a interval variant and the capex_cum_tech axes -- were dropped. See
`git log -p -- parameters_mga.csv` for those removed rows if you need to
resurrect one; re-add it (and a matching #SBATCH profile below) rather
than reusing a task_id number that's been retired. weights, oracle mode,
"relative"/"units" normalisation and batch sampling (strategy_mode=
"sampling") aren't swept here either -- add a row for any of those too.

3 more rows added 2026-09-17, all config-identical to task_id 0
(1ts/7a/5a) except as noted -- fig3a/3b comparison runs, see
scripts/plot_mga_ts_resolution.py's TS_RUNS/TS_COLOR:
  task_id 4 = seed_rng=42 (task_id 0 itself has no seed_rng set --
              batch_oracle's BBO restarts/direction fallbacks then seed
              nondeterministically from OS entropy, see run_model.py's
              module docstring -- so this is a same-config, explicit-seed
              run to compare against task_id 0's unpinned draw, not a
              "different seed from task_id 0's seed" since task_id 0
              never had one). Same batch4/40cpu/4G profile as task_id 0.
  task_id 5 = batch_size=n_workers=16 (vs. 4), solver_threads=2 (vs. the
              config's default 10) -- needs its own #SBATCH profile, see
              below.
  task_id 6 = batch_size=n_workers=32, solver_threads=2 -- same reasoning
              as task_id 5, needs its own #SBATCH profile too.

task_id 7 added 2026-09-18 (commits "new run with 48 axes added for
testing" + "adapt solver threads") -- a different axes config from
task_id 0-6, not another share/capex_cum variant:
  task_id 7 = axes_config=config_mga_axes_total.yaml (48 axes: node_capex_
              cumulative and node_carbon_emissions_cumulative each give
              4 regions x 3 until_years, node_capacity_ratio gives 4
              regions x 3 years x 2 ratio_groups -- vs. task_id 0-6's
              12-axis config_mga_axes_capex_cum.yaml), normalisation=
              per_axes (not share/minmax), tolerance_explore=0.1 (vs.
              0.02), epsilon=0.07 (vs. the config's default 0.01),
              batch_size=n_workers=16, solver_threads=2 -- same batch/
              thread shape as task_id 5, so it needs task_id 5's #SBATCH
              profile below, not the 40cpu/4G standard. No prior
              completed run at any profile for this row, and 4x the axes
              of task_id 0-6 means more per_axes directions to explore
              per batch -- treat --time as unverified too, not just
              --mem-per-cpu/--cpus-per-task.

task_id 10-13 added 2026-10-28: a stepwise retry of task_id 7 after its
Euler failure, switched from per_axes to normalisation=minmax (per_axes
divided capex axes by 15e12 although costs are in model units, ~1e6x too
small; ratio axes reached ~150x their reference 1; emissions axes went
negative). Same 8a/4a/1ts model, tol 0.1, eps 0.07, solver_threads=2.
Each row is only worth submitting once the previous one finished cleanly:
  task_id 10 = emissions-only axes (config_mga_axes_emissions.yaml, 12 axes
              + cost), batch4, max_iterations=1: bound LPs + 1 batch.
  task_id 11 = all 48 axes (config_mga_axes_total.yaml), batch4,
              max_iterations=1.
  task_id 12 = all 48 axes, batch16 (task_id 7's shape), max_iterations=3.
  task_id 13 = the full run: task_id 7 with minmax.
Profiles sized from the v9 1ts runs' slurm_usage.json (batch4: MaxRSS
~29GB, 2.4-3.6h for a full converged run; batch16/solver_threads=2: ~87GB,
1.6h) plus headroom for the larger 8a/4a v1 dataset -- refine from
`sacct -j <jobid> --format=JobID,Elapsed,MaxRSS,State` of the previous row:
  sbatch --array=10 --time=08:00:00 --cpus-per-task=8 --mem-per-cpu=6G submit_euler_mga.sh
  sbatch --array=11 --time=1-00:00:00 --cpus-per-task=8 --mem-per-cpu=6G submit_euler_mga.sh
  sbatch --array=12 --time=1-00:00:00 --cpus-per-task=32 --mem-per-cpu=4G submit_euler_mga.sh
  sbatch --array=13 --time=4-00:00:00 --cpus-per-task=32 --mem-per-cpu=4G submit_euler_mga.sh

task_id 14-15 added 2026-10-28: task_id 12 showed the node_capacity_ratio
axes reach 14-2688x the baseline capacity (idle capacity bought with the
cost slack). These rows use config_mga_axes_total_output.yaml instead:
node_output_ratio axes (share of delivered flow_conversion_output, needs
the ZEN-garden-plugins node_output_ratio change), road = passenger cars
only, years 2030/2050 for all kinds -> 33 axes (66 bound LPs, ~30 min).
  task_id 14 = test, batch4, max_iterations=1.
  task_id 15 = the full run, batch16. task_id 12 peaked at ~109 GiB of
              128G, so 5G/cpu (160G):
  sbatch --array=14 --time=02:00:00 --cpus-per-task=8 --mem-per-cpu=6G submit_euler_mga.sh
  sbatch --array=15 --time=4-00:00:00 --cpus-per-task=32 --mem-per-cpu=5G submit_euler_mga.sh

task_id 16-17 added 2026-10-28, supersede 15: task_id 14 showed the
heating ratio axes reach 2.8-53x, because DAC consumes heat from the shared
heat carrier (its CO2 recycled via methanation/FT/methanol). The axes yaml
now covers industrial heat only (industry_heat_electrification), and the
rows use the *_export0 dataset copy (availability_export_yearly = 0 for the
heat_industry_* carriers and glass/paper/ceramic/food). Same 33 axes.
  task_id 16 = test, batch4, max_iterations=1.
  task_id 17 = the full run, batch16 (task_id 14 peaked at ~40 GiB on 8 cpus).
  sbatch --array=16 --time=02:00:00 --cpus-per-task=8 --mem-per-cpu=6G submit_euler_mga.sh
  sbatch --array=17 --time=4-00:00:00 --cpus-per-task=32 --mem-per-cpu=5G submit_euler_mga.sh

task_id 18-19 added 2026-10-29: task_id 17 (33 axes) did not converge
(CI lower bound 0.000 after 192 iterations). Same rows with two regions
(config_mga_axes_total_output_2reg.yaml: north = old north + BE, NL, DE,
PL, CZ; south = the rest) -> 17 axes. Targets unchanged.
  task_id 18 = test, batch4, max_iterations=1.
  task_id 19 = the full run, batch16.
  sbatch --array=18 --time=02:00:00 --cpus-per-task=8 --mem-per-cpu=6G submit_euler_mga.sh
  sbatch --array=19 --time=4-00:00:00 --cpus-per-task=32 --mem-per-cpu=5G submit_euler_mga.sh

Requires the MGA install step in setup_euler_env.sh to have been run once
(clones + installs ZEN-garden-plugins and near_optimal_tools/pyoNearOpt,
incl. the "bbo" extra needed by batch bbo mode).

Resource profile. task_id 0-4 use batch_size=n_workers=4, so cpus-per-task
is sized as 4 workers x 10 threads/worker = 40, since each worker's solver
requests Threads=10 -- the worker pool needs dedicated cores per worker
instead of dividing a flat core count. mem-per-cpu=4G (160G total): task_id
10/13 (the former share/tolerance_explore rows, same normalisation as
today's rows) were OOM-killed at 40 cpus x 1G on 2026-08-28 (jobs
12067246_10/_13), so don't drop below 4G/cpu. --time=14-00:00:00: the
former task_id 17 (config-identical to today's task_id 1) completed in 8d
at this cpu/mem profile (job 12374944 retry); 14d is the standard padding
used for every row since, so this is the #SBATCH default below -- no need
to pass --time/--cpus-per-task/--mem-per-cpu on the command line, just:
  sbatch --array=0-4 submit_euler_mga.sh    # task_id 0-4, batch4/share/tol002

task_id 5/6 use a bigger batch_size (16/32) than the config's default
Threads=10 was tuned for; rather than scale cpus-per-task to
batch_size x 10 (160/320 cores -- likely bigger than a single Euler node,
and the exact profile that thread-thrashed/OOM'd the retired batch8/batch16
rows once flat BLAS/numexpr thread pools oversubscribed it, see this
script's OPENBLAS_NUM_THREADS etc. exports below), each row's own
solver_threads column pins Gurobi's per-worker Threads down to 2, so
cpus-per-task only needs batch_size x 2 cores -- pass that as an explicit
CLI override (CLI flags win over the #SBATCH defaults above), since these
2 rows don't fit the 40cpu/4G standard profile:
  sbatch --array=5 --cpus-per-task=32 --mem-per-cpu=6G submit_euler_mga.sh   # task_id 5: batch16, 32cpu/192GB
  sbatch --array=6 --cpus-per-task=64 --mem-per-cpu=6G submit_euler_mga.sh   # task_id 6: batch32, 64cpu/384GB
None of task_id 5/6/7 has a prior completed run at this profile (unlike
the 14d/40cpu/4G standard, backed by job 12374944_17's own 8d completion)
-- watch their first attempts and adjust --time/--mem-per-cpu if they OOM
or run long.

task_id 7 shares task_id 5's batch16/solver_threads=2 shape, so the same
32cpu/192GB override applies -- but it's also the first run of the
per_axes/axes_total (48-axis) combination, so --time=14-00:00:00 (the
#SBATCH default) is an untested guess here, not a validated floor like it
is for task_id 0-4:
  sbatch --array=7 --cpus-per-task=32 --mem-per-cpu=6G submit_euler_mga.sh   # task_id 7: batch16/per_axes/axes_total, 32cpu/192GB, time unverified
```

## submit_euler_mga.sh: why the BLAS/numexpr/polars thread pools are pinned to 1

```text
Every current row runs batch bbo mode, which forks/spawns batch_size worker
PROCESSES, each with its own dedicated 10 cpus for Gurobi
(solver_options["Threads"]=10 already accounts for those). Left unset,
numpy/pandas/numexpr inside each worker separately try to size their own
BLAS/numexpr thread pools off the allocation's full cpus-per-task
(batch_size x 10) rather than the 10 cpus that worker actually owns --
batch_size of them doing that concurrently oversubscribes the node's
process/thread budget. Seen on old batch8/batch16 rows (job 11281957,
task_ids retired since): repeated "OpenBLAS blas_thread_init:
pthread_create failed ... Resource temporarily unavailable", then a worker
died mid `import numpy` during pool (re)spawn, and the pool's `close()` ->
`executor.shutdown(wait=True)` hung waiting on it -- both runs sat idle for
~3 days until SLURM killed them at --time, having made zero progress past
the first outer iteration. A batch4 row hit the same warning 3x but had
enough headroom to survive and complete normally -- which is the batch_size
all 4 current rows use. Pinning these to 1 removes the oversubscription;
Gurobi's own thread count is unaffected since it's set explicitly via
solver_options, not these vars.

Same issue hit polars (pulled in transitively via linopy, which builds the
LP model in each worker) on a batch16 rerun: its Rust async executor sizes
its own thread pool off the full cpus-per-task allocation the same way
OpenBLAS did, so 16 workers doing that concurrently panicked with
"async-executor-N ... WouldBlock: Resource temporarily unavailable", and
once enough threads/processes had piled up, even Python's own
multiprocessing fork() started failing the same way
(BlockingIOError: [Errno 11] Resource temporarily unavailable). Pinned the
same way as the BLAS libs above.
```

## run_model.py: change log of the sweep driver

```text
ZEN-models run, adapted to run as a SLURM array sweep.

CHANGES:
  * `my_dataset`, `my_comment` and every `system_overrides` value now come from
    ONE ROW of `parameters.csv`, selected by --task_id. So each row is a complete
    run configuration and a SLURM array can run them all in parallel.
  * Instead of patching the dataset's shared system.json in place (which races
    when several array tasks run at once, and can leave the file corrupted if a
    job is killed), each task STAGES A PRIVATE COPY of the dataset, patches that
    copy, and runs on it. Your pristine dataset (in ZEN-creator/outputs or
    data/) is never modified.
  * On Euler, the staged dataset and the results go to $SCRATCH.
  * `--params` selects which CSV to sweep over (default parameters.csv). Each
    row may also set a `config` column (e.g. config_mga_weights.yaml) to pick
    which data/*.yaml config to run with; rows without it use config.yaml, so
    the original parameters.csv/submit_euler.sh path is unaffected.
  * Rows may also set a `normalisation` column (e.g. "relative", "units" or
    "minmax") that overwrites plugins.mga.normalisation in a private staged
    copy of the chosen config -- the shared data/*.yaml config is never
    touched, so one config_mga_bbo.yaml / config_mga_sampling.yaml covers
    all normalisation modes instead of needing a config file per mode.
  * Rows may also set `batch_size` / `n_workers` / `tolerance_explore` /
    `seed_rng` columns that overwrite the matching keys under
    plugins.mga.batch (batch mode only) in the same private staged copy, the
    same way `normalisation` does -- e.g. a row using normalisation="share"
    can set its own tolerance_explore without changing the shared config
    file's value for the other (minmax) rows that also point at it.
    `seed_rng` pins pyoNearOpt's batch_oracle RNG (BBO restarts + direction
    fallbacks); left unset, batch_oracle seeds nondeterministically from OS
    entropy (see shared_direction_oracle._get_rng), so two rows with
    otherwise-identical config still explore different directions and are
    NOT reproducible against each other unless both set seed_rng explicitly.
    `max_iterations` caps plugins.mga.batch.max_iterations the same way --
    e.g. for short Euler test rows that only need the bound LPs plus a
    batch iteration or two before committing to a full run.
  * Rows may also set a `solver_threads` column that overwrites
    solver.solver_options.Threads in the same private staged copy. Batch
    mode forks batch_size worker processes that each run their own Gurobi
    solve concurrently, so cpus-per-task (see submit_euler_mga.sh) needs to
    be sized as batch_size x Threads-per-worker -- a row using a larger
    batch_size than the shared config's default Threads was tuned for
    should set solver_threads to whatever per-worker core count its own
    #SBATCH profile actually allocates, or Gurobi will oversubscribe the
    node (see submit_euler_mga.sh's batch8/batch16 postmortem).
  * The `axes` block for every MGA mode except `weights` is no longer
    duplicated per config file -- it's merged in from data/config_euler/config_mga_axes_capex.yaml
    (the default) into the private staged copy, so all five
    config_mga_{bbo,sampling,oracle,batch_bbo,batch_sampling}.yaml files
    share one axes definition. A row may set an `axes_config` column (e.g.
    config_mga_axes_capex_cum.yaml) to merge in a different axes file
    instead, without touching the shared default.
  * Any system_overrides key a row's CSV doesn't set falls back to
    DEFAULT_SYSTEM_OVERRIDES, so a sweep whose rows all share the same
    dataset-processing setup (e.g. parameters_mga.csv) doesn't need to repeat
    those columns in every row -- a row can still override any of them by
    adding that column, the way parameters.csv already does explicitly.
    A BLANK cell in an existing system column means "keep the dataset's own
    system.yaml value" (no override, no default) -- e.g. rows 50/51 run the
    zen-europe datasets exactly as generated.
  * Solver/degeneracy tests for the TES/DSM (full flexibility) models, all
    applied to the private staged copies only:
    `solver_options` ("BarOrder=1;BarHomogeneous=0") merges any Gurobi
    parameters into solver.solver_options; `cost_noise` (+ `noise_seed`)
    multiplies TES/DSM cost parameters by (1 + eps*u), u ~ U(-1, 1), per node;
    `flex_cost_fix` = 1 gives TES/DSM a power capex (0.1 x energy capex) and
    TES a 0.5 Euro/MWh variable opex (numerical test, not final data).
    See scripts/solver_tests/NOTES.md.
  * Datasets are looked up first in data/outputs/zen-europe-new (current
    ZEN-europe output, models.yaml names), then data/outputs/zen-europe-old (older
    ZEN-europe output), then ZEN-creator/outputs, then data/ (see
    DATASET_SEARCH_DIRS).

Run one row by hand (local test):   python run_model.py --task_id 0 --run_on local
On Euler it is launched by submit_euler.sh (or submit_euler_mga.sh) via the
SLURM array.
KNOWN ISSUE (ZEN-garden, not patched here): for interval_between_years (dy) > 1,
`constraint_technology_diffusion_limit` in zen_garden/model/technology/technology.py
scales the growth term correctly ((1+max_diffusion_rate)**dy - 1) but NOT the
"unbounded" terms -- `market_share_unbounded * capacity_previous` and
`capacity_addition_unbounded` are per-year amounts, while capacity additions are
per investment period. The docstring states dy*(xi*sum(S) + zeta), but the code
omits the factor dy, so at dy=2 the unbounded diffusion allowance is effectively
halved (no effect at dy=1). Results at dy > 1 (e.g. v9 and the 2a v10 runs) are
therefore slightly more diffusion-constrained than intended. Left unfixed on purpose.
```
