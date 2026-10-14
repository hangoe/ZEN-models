# Solver tests: why the full-flexibility models are slow

Started 2026-10-14. Plan: `~/.claude/plans/i-have-troubles-with-sorted-nest.md`.

## What we already know (from the existing Euler runs, 2022, 8 periods, interval 4, 10 ts, NF 2)

| run | constraints | variables | barrier it | solve time |
|---|---|---|---|---|
| no_flexibility | 8.0 M | 5.3 M | 183 | 1.5 h |
| no_flexibility_single_temp | 7.8 M | 5.2 M | 178 | 1.4 h |
| full_flexibility_single_temp | 27.5 M | 15.2 M | 384 | 17.5 h |

~12x slower = 3.4x bigger LP × 2x more iterations × costlier iterations.

- **Size**: 10 operational but **1969 storage-level steps per year**. ZEN-garden starts a new storage step
  whenever the hourly cluster sequence switches cluster (`zen_garden/input/time_series_aggregation.py`,
  `calculate_time_steps_storage_level`). 22 TES/DSM techs × 28 nodes × 8 years × 1969 ≈ 10 M extra
  storage-level variables. The TES/DSM chains are most of the model.
- **Iterations (hypothesis): degeneracy.** TES and DSM have power capex 0. TES variable opex is 1 Euro/GWh
  (≈ 0) and its efficiency is 1.0, so power capacity and flows are (nearly) free → many equally optimal
  solutions. TES costs are identical across the 4 sectors. DSM costs differ per sector.
- Symmetry in the MIP sense does not apply: barrier does not branch. Degeneracy mainly hurts the last
  barrier iterations (long tail; see `it_1e-4` vs `it` in `parse_logs.py`).

## New `parameters.csv` columns (handled in `run_model.py`, staged copy only)

| column | example | effect |
|---|---|---|
| `solver_options` | `BarOrder=1;BarHomogeneous=0` | merged into `solver.solver_options` |
| `cost_noise` | `1e-2` | TES/DSM capex/opex × (1 + eps·u), u ~ U(-1, 1), one draw per node (per-node CSVs) |
| `noise_seed` | `7` | RNG seed for `cost_noise` (default 0) |
| `flex_cost_fix` | `1` | TES/DSM power capex = 0.1 × energy capex. TES variable opex = 0.5 Euro/MWh. Numerical test, not final data |

## Round 1: 2 optimized years (2022, 2026), interval 4, 5 ts, NF 2

| task | dataset | change | question |
|---|---|---|---|
| 12 | no_flexibility | – | reference |
| 13 | full_flexibility | – | does the small model show the slowdown? |
| 16 | TES_only | – | TES or DSM? |
| 17 | DSM_only | – | TES or DSM? |
| 18 | full_flexibility | `BarOrder=1` | does nested dissection make iterations cheaper? (`factor_ops`, `s_per_it`) |
| 19 | full_flexibility | `BarHomogeneous=0` | is the homogeneous algorithm costing time? |
| 20 | full_flexibility | `flex_cost_fix=1` | does removing free variables cut the iterations? |

Datasets `zen_europe_ind_heat_v1_{TES,DSM}_only` were generated with ZEN-europe `d0dbd4d` (includes the TES
self-discharge fix). Apart from the removed techs, they differ from the committed full_flexibility only by float
noise (~1e-15).

### Commands (Euler)
```bash
cd ~/ZEN-models && git pull
sbatch --array=2 --time=72:00:00 submit_euler.sh            # the real full-flex run, longer walltime
sbatch --array=12,13,16-20 --time=04:00:00 submit_euler.sh  # round 1
# when finished:
python scripts/solver_tests/parse_logs.py zen_run_<JOBID>_*.out
sacct -j <JOBID> --format=JobID,State,Elapsed,MaxRSS
# also useful (the old big runs, if their .out files still exist):
python scripts/solver_tests/parse_logs.py zen_run_<OLDJOBID>_1.out zen_run_<OLDJOBID>_4.out
```

### How to read it
- **13 vs 12**: should show ≥ ~3x solve time and ≥ ~1.3x iterations. If not, 5 ts is too coarse → fallback:
  rows 14/15 at 10 ts.
- **16 vs 17**: whichever is closer to 13 is the family causing it.
- **18 vs 13**: lower `factor_ops`/`s_per_it` → ordering helps (try `BarOrder=-1` in round 2 too).
- **19 vs 13**: fewer iterations / less time → set `BarHomogeneous 0` (keep 1 only if infeasibility detection
  matters).
- **20 vs 13**: clearly fewer iterations (especially `it - it_1e-4`) → degeneracy confirmed → fix TES/DSM costs
  in ZEN-europe with sourced values. The objective changes here (different costs), so compare iterations/time,
  not the objective.
- Every other row should be OPTIMAL and match the objective of its baseline row to ~1e-6 relative.

## Round 2 (after round 1)
On the tier that reproduces the slowdown, change one factor at a time: `BarOrder=-1`, `NumericFocus=1`,
`BarConvTol=1e-6`, `Presolve=2;PreDual=1`, `ScaleFlag=-1`, then `cost_noise` 1e-4 / 1e-2 (low priority). Then run
the best combination on full_flex and no_flex. Then one mid-size check (2022-2030, 10 ts).

## Results

### Local smoke check (Mac, 2026-10-14): new columns work end to end
full_flexibility with `flex_cost_fix=1` + `cost_noise=1e-2` (seed 7) + `BarOrder=1;BarConvTol=1e-6`, 1 year, 3 ts,
Threads 4 → **Optimal 1.54973e6, 72 it, 838 s**. The solved model's parameters contain the per-node noisy values
(±1%) and the fixed power capex/opex. Side observations:
- Storage steps per year: **1095 at 3 ts** (1969 at 10 ts), with 3 operational steps.
- Factor Ops 1.8e11 (~11 s/it on the Mac), vs 3.9e9 for the no-flex smoke model (2 years, 3 ts) in
  zen-europe-bugfix. The TES/DSM part mainly makes each iteration far more expensive.

### Round 1 (Euler)
(fill in)
