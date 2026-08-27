# ZEN-garden sweep on Euler

These files lie into the `ZEN-models` repo.

| File | Role |
|---|---|
| `run_model.py` | Run, adapted so `my_dataset`, `my_comment`, `config` and all `system_overrides` come from **one row** of a sweep CSV (chosen by `--task_id`; the CSV itself by `--params`, default `parameters.csv`). For any MGA config except `weights`, also merges in the shared `data/config_mga_axes_capex.json` axes definition. Any `system_overrides` key a row's CSV doesn't set falls back to `DEFAULT_SYSTEM_OVERRIDES`. |
| `parameters.csv` | Normal (non-MGA) sweep table — **one row per run**. Columns = `my_dataset`, `my_comment`, and one column per `system.json` override. No `config` column, so every row runs `data/config.json`. |
| `submit_euler.sh` | The SLURM **array** job for the normal sweep: one job per row of `parameters.csv`. |
| `parameters_mga.csv` | MGA sweep table. `task_id` 7: historical CAPEX_PERIODS batch4 minmax run (left untouched, kept for reference — its axes file uses the old, now-superseded `node_capex_periods` schema). `task_id` 9-12: current cum_capex sweep — `config_mga_batch_bbo.json` with `axes_config=config_mga_axes_capex_cum.json` (`node_capex_cumulative`, `until_years=[2040, 2050]`), batch4/batch8 × minmax/share. Plain-CAPEX rows (former task_ids 0-6) and the CAPEX_PERIODS weights row (former task_id 8) were removed as no longer needed. Weights, oracle, batch-sampling and `relative`/`units` normalisation aren't swept right now (add a row back to use them). |
| `submit_euler_mga.sh` | The SLURM **array** job for the MGA sweep: one job per row of `parameters_mga.csv`. `#SBATCH` header carries the batch16 resource profile as a safe default; override `--time`/`--cpus-per-task`/`--mem-per-cpu` per `--array` range on the `sbatch` command line for the cheaper modes (see the script's header comment for the exact per-range values). |
| `data/config_mga_axes_capex.json` | Shared MGA axes for every mode except `weights`: 4 regions x 3 technology groups (power/hydrogen/carbon) of annualised node capex, 12 axes + cost. One file instead of duplicating the block in every `config_mga_*.json`. |
| `data/config_mga_axes_capacity.json` | The old technology-capacity axes (7 technologies + a CCS lump), kept for reference — not currently merged into any config. |
| `setup_euler_env.sh` | One-time environment build (venv + `zen_garden`, plus the MGA plugin + `pyoNearOpt` if you'll run MGA sweeps). Run once on a login node. |

## Directory layout it assumes (same as your original script)

```
/cluster/home/<user>/
├── ZEN-models/            
│   ├── run_model.py
│   ├── parameters.csv
│   ├── submit_euler.sh
│   ├── setup_euler_env.sh
│   └── data/
│       ├── config.json           
│       └── outputs/              <- local-run outputs (Euler outputs go to scratch)
└── ZEN-creator/
    └── outputs/
        └── Crystal_Ball_HG_v5_3_no_flexibility/   <- input dataset (system.json etc.)
```

Both repos (`ZEN-models` and `ZEN-creator`) must be present in your Euler Home.

## How the sweep works

```
parameters.csv           submit_euler.sh                compute nodes
 task_id 0 ─┐         sbatch --array=0-4 ─┐        ┌─ run_model.py --task_id 0
 task_id 1 ─┤                             ├───────►├─ run_model.py --task_id 1
 task_id 2 ─┤───────► (SLURM array)       ├        ├─ run_model.py --task_id 2
 task_id 3 ─┤                             ├        ├─ run_model.py --task_id 3
 task_id 4 ─┘                             ┘        └─ run_model.py --task_id 4
```

`SLURM_ARRAY_TASK_ID` → `--task_id` → the matching row of `parameters.csv`. Each
job reads its `my_dataset` + `system_overrides` from that row and runs only that
combination.

## What the adapted `run_model.py` does per task

1. Reads its row from `parameters.csv`.
2. **Copies the dataset** `ZEN-creator/outputs/<my_dataset>` to a private per-task
   folder on scratch (so parallel tasks never clash, and the original dataset is
   never modified — this replaces the in-place patch/restore in the version).
3. Applies the row's overrides to the **copy's** `system.json`.
4. Runs `zen_garden.run(config=data/config.json, dataset=<staged copy>, folder_output=<scratch>/outputs/<my_dataset>_<my_comment>)`.

All 5 rows share the same TSA/time settings (`aggregated_time_steps_per_year=10`,
`reference_year=2025`, `optimized_years=10`, `interval_between_years=5`); only
`my_dataset` varies, one row per model currently in `ZEN-creator/outputs`
(`Crystal_Ball_HG_v5_3`, and its `_no_flexibility`, `_DSM_only`, `_TES_only`,
`_single_temp` variants). **Edit `parameters.csv` to define the real runs** —
add/remove columns to match exactly the keys you want in `system_overrides`
(any column other than `my_dataset`/`my_comment` is applied as an override).

## Results go to scratch

With `--run_on euler`, both the staged dataset and the results land under
`$SCRATCH/zen_runs/...` (fast, large). ⚠️ Scratch is **purged after ~2 weeks and
never backed up** — download finished results promptly (VS Code Explorer, or
`scp -r euler:$SCRATCH/zen_runs/outputs/... ~/Downloads/`). For local test runs
(`--run_on local`) outputs stay in `data/outputs/` as before.

## Run order

```bash
# ONE-TIME
cd /cluster/home/<user>/ZEN-models
bash setup_euler_env.sh                          # build venv + install zen_garden
source .venv/bin/activate
python run_model.py --task_id 0 --run_on local   # quick smoke test (small settings!)

# CALIBRATE, then SWEEP
sbatch --array=0     submit_euler.sh             # one row first, to size resources
myjobs -j <jobID>                                # read actual CPU/RAM/time
# ...edit --time / --cpus-per-task / --mem-per-cpu in submit_euler.sh...
sbatch --array=0-5   submit_euler.sh             # launch the rest (match task_ids)

# MONITOR / COLLECT
squeue                                            # PD = pending, R = running
scancel <jobID>                                   # cancel if needed
```


## MGA sweep on Euler (next steps, one-time setup)

The normal sweep above doesn't need the MGA plugin. To also run the MGA
sweep (`parameters_mga.csv` / `submit_euler_mga.sh`), do this once:

```bash
# 1. Pull the new files onto Euler, then rebuild the env — setup_euler_env.sh
#    now also clones + installs the MGA plugin and pyoNearOpt as sibling
#    repos under $HOME (same pattern as $HOME/ZEN-garden):
cd /cluster/home/<user>/ZEN-models
git pull
bash setup_euler_env.sh
# Check the output ends with:
#   registered plugins: [..., 'mga', ...]
#   pyoNearOpt OK
# If 'mga' is missing, your Euler $HOME/ZEN-garden checkout isn't the
# entry-point-aware version -- update it (match your local $HOME/ZEN-garden
# checkout) before continuing. This also needs $HOME/ZEN-garden-plugins on
# branch feature/mga, pulled to its latest commit -- setup_euler_env.sh
# only clones it once and never re-pulls, so if you've updated the plugin
# since your last setup_euler_env.sh run, pull it by hand:
#   git -C $HOME/ZEN-garden-plugins pull

# 2. Smoke-test the cheapest mode (sampling minmax) on a login node first:
source .venv/bin/activate
python run_model.py --task_id 0 --run_on local --params parameters_mga.csv
```

`parameters_mga.csv` now holds:

| task_id | mode | normalisation | batch_size/n_workers | axes |
|---|---|---|---|---|
| 7 | batch bbo | minmax | 4 | capex_periods (historical, untouched) |
| 9 | batch bbo | minmax | 4 | capex_cum (until_years 2040/2050) |
| 10 | batch bbo | share | 4 | capex_cum (until_years 2040/2050) |
| 11 | batch bbo | minmax | 8 | capex_cum (until_years 2040/2050) |
| 12 | batch bbo | share | 8 | capex_cum (until_years 2040/2050) |

Task 7 is kept as-is from before the plugin's periods→cumulative rename;
don't resubmit it without first updating `config_mga_axes_capex_periods.json`
to the new `node_capex_cumulative` schema (the plugin no longer recognizes
`node_capex_periods`). Tasks 9-12 are the current cum_capex sweep, covering
both new normalisation modes (`minmax`, `share`) at batch4 and batch8.
Weights, oracle, batch-sampling and `relative`/`units` normalisation aren't
in this sweep either — `config_mga_weights.json`/`config_mga_oracle.json`/
`config_mga_batch_sampling.json` and those normalisation modes still work,
just add a row for them by hand if you need them (see
`submit_euler_mga.sh`'s header comment).

`submit_euler_mga.sh`'s `#SBATCH` header carries the batch8 (task_id 11/12)
resource profile as a safe default for a bare `sbatch submit_euler_mga.sh`.
Submit each range with its own tighter resource profile instead — task_ids
9/10 (batch4) at `cpus-per-task=40`; task_ids 11/12 (batch8) at
`cpus-per-task=80` (batch_size x 10 threads-per-worker, at 1G per cpu; see
the script's header comment for the full reasoning):

```bash
sbatch --array=9,10                                                 \
       --time=72:00:00 --cpus-per-task=40  --mem-per-cpu=1G  \
       submit_euler_mga.sh                # cum_capex batch4, minmax + share
sbatch --array=11,12                                                \
       submit_euler_mga.sh                # cum_capex batch8, minmax + share (script default)

myjobs -j <jobID>                          # check actual time/CPU/RAM used
                                            # against the profile once each
                                            # range's jobs finish, and adjust
                                            # if the padding was off

# Once you trust the resources, submit everything together:
sbatch --array=9-12 submit_euler_mga.sh
```

Results land tagged `_CAPEX_CUM_<mode>_batch<N>` to mark the new cumulative
capex axes:
```
$SCRATCH/zen_runs/outputs/Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion_2020_7a_5a_interval_3ts_MGA_CAPEX_CUM_batch_bbo_<mode>_batch<N>/
```
Download before scratch is purged (~2 weeks) — see "Results go to scratch" above.

For the full Euler setup (SSH keys, VS Code Remote-SSH, VPN, storage, modules,
resource tuning), see `Euler_setup_and_run_guide.md`.
