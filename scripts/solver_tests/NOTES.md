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

### Round 1 (Euler job 17074492, all OPTIMAL)

| task | test | it | it_1e-4 | solve s | s/it | rows | Factor NZ | Factor Ops |
|---|---|---|---|---|---|---|---|---|
| 12 | no-flex | 88 | 56 | 116 | 1.3 | 0.78 M | 2.6e7 | 8.0e9 |
| 13 | full-flex | 121 | 84 | 2047 | 16.9 | 4.22 M | 1.0e9 | 5.4e11 |
| 16 | TES only | 158 | 125 | 1847 | 11.7 | 2.76 M | 6.7e8 | 3.5e11 |
| 17 | DSM only | 88 | 56 | 731 | 8.3 | 2.24 M | 5.6e8 | 3.0e11 |
| 18 | BarOrder=1 | 121 | 84 | 2082 | 17.2 | same | same | same |
| 19 | BarHomogeneous=0 | 135 | 105 | 1913 | 14.2 | same | same | same |
| 20 | flex_cost_fix | 112 | 81 | 1950 | 17.4 | same | same | same |

- The small tier reproduces the slowdown (17.6x solve time). It is **cost per iteration** (Factor NZ 40x), not
  the iteration count (1.4x).
- None of the solver settings, nor the cost fix, help (±5%). BarOrder=1 gives an identical factor.
- **TES is the main driver**: most iterations (158) and ~90% of the full-flex solve time. DSM is cheaper.
- Objectives are equal to ~1e-6 (TES_only = no-flex exactly): flexibility is worth ~nothing in 2022/2026.

### TES use per temperature band (row 4, full 2022-2050 single_temp run)
| band | energy cap. 2050 | power cap. 2050 | discharge 2050 |
|---|---|---|---|
| water 100-150 | 204 GWh (63%) | 192 GW | 30.1 TWh (62%) |
| water 0-100 | 74 GWh (23%) | 69 GW | 10.1 TWh (21%) |
| steam 150-200 | 49 GWh (15%) | 180 GW | 8.6 TWh (18%) |
TES ≈ 0 before 2030. Storage sits at its minimum energy-to-power ratio (1 h water, 0.25 h steam). Power
capacity is free (0 capex) and floats under barrier without crossover, which is why there are values like
123 GW paper TES vs. a few GW of paper heat demand.

### Round 2 setup (2026-10-14)
TES `capacity_limit` added in ZEN-europe (uncommitted, `industry_heat_supply.get_capacity_limit_tes`,
`IndustryTES._set_capacity_limit`): heat demand of the band + all lower bands × `capacity_limit_margin`
(2.0), in MW, 0 at nodes without demand. **Caveat: every sector has heat demand in all 28 nodes, so no TES chain
is removed; expect little speed-up from the limit alone.** New ZEN-europe model
`zen_europe_ind_heat_v1_full_flexibility_TES_100_150` (8 TES techs removed).
In ZEN-models, only the TES folders of `zen_europe_ind_heat_v1_full_flexibility` were replaced (now with
`capacity_limit.csv`), so rows 2/13/18-20 use the limited TES from now on.

| task | dataset | question |
|---|---|---|
| 21 | full_flexibility (with TES limit) | does the limit alone help? compare to 13 |
| 22 | full_flexibility_TES_100_150 (with limit) | how much does dropping 8 of 12 TES techs give? |

```bash
sbatch --array=21,22 --time=04:00:00 submit_euler.sh
python3 scripts/solver_tests/parse_logs.py zen_run_<JOBID>_*.out
```

### Round 2 results (job 17080911; both on AMD EPYC nodes eu-a2p, ~1.5x slower per work unit than Round 1's eu-g9)
| task | test | it | solve s | work units | rows | Factor NZ |
|---|---|---|---|---|---|---|
| 13 (ref) | full-flex | 121 | 2047 | 7267 | 4.22 M | 1.0e9 |
| 21 | + TES limit | ~95-100 (not finished at last check, it 90 at 2185 s) | – | ~5500 (est.) | 4.22 M | 1.0e9 |
| 22 | TES 100-150 only + limit | 93 | 1547 | 3721 (−49%) | 2.90 M | 7.1e8 |
Work units of Round 1 rows: 16 = 6637, 17 = 2727, 18 = 7415, 19 = 6669, 20 = 6879.
- TES limit: same size, ~20% fewer iterations. Dropping 2 TES bands: −30% work per iteration.
- Use work units (not seconds) to compare runs on different node types.

### Decision for the production runs (2026-10-14)
Rows 2 and 4 edited in place: all 3 TES bands, TES capacity limit (ZEN-europe code), `BarHomogeneous=0`, no cost
changes, comment `2022_8a_4a_interval_10ts_tescaplimit_bh0`. The TES_100_150 model/dataset and row 22 were removed.
The full_flexibility_single_temp dataset was regenerated (only its TES folders replaced; they are identical to
full_flexibility's). Literature review on TES/DSM power capex and variable opex (not applied):
scratchpad `lit_review_tes_dsm_costs.md`. TES power capex 40k/50k/20k EUR/MW, TES opex 0.5 EUR/MWh, DSM power
capex 0 (production overcapacity already costed); DSM variable costs in the literature are much higher than current.
