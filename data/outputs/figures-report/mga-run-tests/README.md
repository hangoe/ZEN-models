# Near-optimal run tests: guide for the thesis appendix

These are the figures and tables behind the appendix section on what drives the
convergence and run time of the near-optimal runs. The text goes into the
`mt-report-hg` repo; the figures, numbers and scripts live here in `ZEN-models`.

## Words used in figures and text

| Term | Meaning |
|---|---|
| single model run | One cost-optimal ZEN-garden solve (no near-optimal exploration). Only in `single_model_runs_resources.csv`. |
| near-optimal run | One full near-optimal exploration: many LP solves in parallel batches until the convergence check passes. (In code and folder names this is "MGA"; don't use that word in the thesis figures.) |
| evaluation | One LP solve inside a near-optimal run (one direction). |
| batch round | One iteration: `batch size` evaluations solved in parallel. |
| axes | Dimensions of the near-optimal space, **including** net present cost (7 axes = 6 decision axes + cost). |
| tolerance (`tolerance_explore`) | Gap below which a direction counts as well explored. |
| convergence target | Required 95 % CI lower bound of the share of well-explored directions (0.95, for some calibration runs 0.90). |
| implied tolerance | Smallest tolerance that the directions sampled so far would already meet. Read off a single run, it shows what a looser tolerance would have cost. |
| cost slack (`epsilon`) | Allowed cost increase above the optimum (1 % = 0.01). |
| ts | Representative time steps per year (time series aggregation). |
| periods, e.g. `8a/4a` | 8 optimised years, 4 years apart. `7a/5a` = 7 years, 5 apart. |
| solve-round wall time | Sum of the parallel LP rounds only (from `diagnostics.csv`). It leaves out sampling and setup, so it is lower than the real job time. |
| elapsed job time | Real Euler wall-clock time from SLURM `sacct`. |
| ZEN-Europe | The input model. Old paths still say `Crystal_Ball`; always write ZEN-Europe. |

## Run IDs: where the table with names and numbers is

**`euler/mga_runs.csv`** is the master table. One row per near-optimal run, with:

- `run_id`, the name used in all figures:
  - **V1–V6**: calibration runs on the old v9 dataset (2020 start, 13 axes, tolerance 0.02)
  - **Z1–Z7**: calibration runs on the first ZEN-Europe dataset (2022 start)
  - **T1–T4**: thesis runs (task 54 / 56 / 57 / 67), the runs used in the main results
- `role` (calibration / thesis), `status` (completed / failed / running)
- `task_id`: the row number in `parameters_mga.csv` at the time. **Don't use it in the
  thesis**, because task IDs were reused for different runs.
- `job_id` (the completed Euler job) and `other_jobs` (failed or cancelled attempts)
- settings: `dataset`, `freeze_2022`, `ts_per_year`, `periods`, `axes_incl_cost`,
  `tolerance_explore`, `cost_slack`, `batch_size`, `ci_target`, `n_samples`,
  `normalisation`, `gurobi_threads`, `numeric_focus`, `seed`
- `folder`: the results folder under `data/outputs/euler_outputs_mga/`

**`data/outputs/figures-report/mga-run-tests/mga_run_tests_results.csv`** has the
results per `run_id`: iterations, evaluations, final CI lower bound, median
solve time per batch round, solve-round hours, elapsed hours, CPUs, requested
memory, peak memory (GiB), CPU efficiency, number of failed attempts. Take the
numbers in the text from here.

Other sources:

- `euler/slurm_usage/mga_sacct_2026-11-26.txt`: the raw SLURM accounting lines for these jobs.
- `euler/MGA_RUN_HISTORY.md`: why each run was made and what went wrong. Background only; it uses task IDs.
- The single model runs have no run ID. Their raw accounting is in
  `figures-report/mga-run-tests/slurm_usage_plain_solves/` (parameters.csv rows 10–13 at the time).

## Figures

Every figure exists twice, with the same layout: `figures-report/mga-run-tests/`
(serif font, for the thesis) and `figures-presi/mga-run-tests/` (Arial, for slides).
Width is the thesis text width (6.3 in). Panel headers are "(a) …"; there are no
titles, so captions go in the LaTeX.

| File | Shows |
|---|---|
| `fig4_convergence_by_effect.svg` | Convergence, one panel per effect: (a) tolerance Z6/Z7 + T2/T3, (b) dimensions Z7/Z2/Z1, (c) cost slack T3/T4, (d) batch size and seed V1/V2/V3, (e) time steps and periods V1/V4/V5/V6. Solid = 95 % CI lower bound of well-explored directions vs. number of evaluations (left axis); dashed = implied tolerance (right, log axis); grey dashed = convergence target; grey dotted = the run's tolerance. Panel (c) says "T4 not available yet" until task 67 is downloaded. V4/V5 logged no implied tolerance. |
| `fig7_effect_overview.svg` | The same effects as bars, one row each (log axes except memory and CPU): evaluations until stop, median solve time per batch round, elapsed job time, peak memory (GiB), CPU efficiency (%). Black outline = thesis run. Run time = evaluations × time per evaluation; this figure shows which of the two an effect changes. |

Tables in this folder (the numbers for the text):

| File | Content |
|---|---|
| `mga_run_tests_results.csv` | Results per `run_id` (see above). |
| `single_model_runs_resources.csv` | Euler time and memory of the single model runs (one cost-optimal solve each, old v9 dataset, 2020, 16 years 2 apart): 1/3/10/20 ts, the 1-ts run repeated with 16/6/3/2 CPUs. Columns: ts, job, CPUs, requested memory, elapsed minutes, peak memory, memory and CPU efficiency. Use it to compare a near-optimal run with a single solve of the same model. |

Colours: every run ID has its own colour, the same in both figures, and no two runs
share one. The lightness shows the group: **V** runs = full ETH colours, **Z** runs =
light ETH tints, **T** (thesis) runs = black and greys (darker = tighter setting, so
T3 is black). Defined in `RUN_COLOR`, `scripts/plots/mga_run_tests_registry.py`.
Suggested caption sentence: "Full colours: calibration runs on the v9 dataset;
light colours: calibration runs on ZEN-Europe v1; black/grey: thesis runs."

## Effects and which comparison is clean

| Effect | Comparison | Clean? |
|---|---|---|
| Tolerance | Z6/Z7, T2/T3 | yes, only the tolerance differs |
| Cost slack | T3/T4 | yes (the only clean pair; T4 pending) |
| Dimensions | Z7/Z2/Z1 | no: tolerance and cost slack also differ |
| Batch size | V1/V3 | yes (V3 also uses 2 instead of 10 Gurobi threads per worker) |
| Seed (noise) | V1/V2 | yes |
| Time steps | V1/V4/V5 | yes |
| Periods | V1/V6 | yes |
| Euler settings | fig7 (memory, CPU efficiency) + the results tables | descriptive |

V runs and Z/T runs use different datasets, axes and normalisation (share vs.
minmax), so compare absolute numbers only within one group.

## Regenerating

```bash
# from ZEN-models/, environment with zen_garden_plugins
PY=~/anaconda3/envs/zen-garden-plugins-env/bin/python
$PY scripts/import_slurm_usage.py euler/slurm_usage/<sacct file>  # after new runs: writes slurm_usage.json
$PY scripts/plot_mga_run_tests.py                                # fig4, fig7, both tables
FIGURE_MODE=presentation $PY scripts/plot_mga_run_tests.py       # presi versions
```

Effect groups and legend texts: `scripts/plots/mga_run_tests_registry.py` (`EFFECTS`).
A new run goes into `euler/mga_runs.csv` first. Earlier versions of these figures
(fig3a/b, fig4a–e, fig5 resource bars, fig6 polytope size) are in git history.
