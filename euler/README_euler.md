# ZEN-garden sweep on Euler

These files lie into the `ZEN-models` repo.

| File | Role |
|---|---|
| `run_model.py` | Run, adapted so `my_dataset`, `my_comment`, `config` and all `system_overrides` come from **one row** of a sweep CSV (chosen by `--task_id`; the CSV itself by `--params`, default `parameters.csv`). For any MGA config except `weights`, also merges in the shared `data/config_mga_axes_capex.json` axes definition. Any `system_overrides` key a row's CSV doesn't set falls back to `DEFAULT_SYSTEM_OVERRIDES`. |
| `parameters.csv` | Normal (non-MGA) sweep table — **one row per run**. Columns = `my_dataset`, `my_comment`, and one column per `system.json` override. No `config` column, so every row runs `data/config.json`. |
| `submit_euler.sh` | The SLURM **array** job for the normal sweep: one job per row of `parameters.csv`. |
| `parameters_mga.csv` | MGA sweep table, `task_id` 0-10: `my_dataset`, `my_comment`, `config` (which `data/config_mga_*.json` to run), `normalisation`, `batch_size`/`n_workers`. Covers weights / sampling (units+minmax) / bbo (units+minmax) / batch bbo (units+minmax x batch4/8/16). Oracle, batch-sampling and `relative` normalisation aren't swept right now (add a row back to use them). The TSA/time-horizon `system_overrides` that used to be columns here (`conduct_time_series_aggregation` etc.) now come from `run_model.py`'s `DEFAULT_SYSTEM_OVERRIDES` instead. |
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

# 2. Smoke-test the cheapest mode (weights) on a login node first:
source .venv/bin/activate
python run_model.py --task_id 0 --run_on local --params parameters_mga.csv
```

`parameters_mga.csv` (`task_id` 0-10) is now:

| task_id | mode | normalisation | batch_size/n_workers |
|---|---|---|---|
| 0 | weights | — | — |
| 1 | sampling | units | — |
| 2 | sampling | minmax | — |
| 3 | bbo | units | — |
| 4 | bbo | minmax | — |
| 5 | batch bbo | units | 4 |
| 6 | batch bbo | units | 8 |
| 7 | batch bbo | units | 16 |
| 8 | batch bbo | minmax | 4 |
| 9 | batch bbo | minmax | 8 |
| 10 | batch bbo | minmax | 16 |

Oracle, batch-sampling and `relative` normalisation aren't in this sweep
right now — `config_mga_oracle.json`/`config_mga_batch_sampling.json` and
the `relative` normalisation still work, just add a row for them by hand if
you need them (see `submit_euler_mga.sh`'s header comment).

`submit_euler_mga.sh`'s `#SBATCH` header carries the batch16 resource
profile as a safe default for a bare `sbatch submit_euler_mga.sh`. Submit
each range with its own tighter resource profile instead (from `sacct`
history on the old axes, padded for the new bigger 12-axis capex problem —
see the script's header comment for the full reasoning and exact ranges):

```bash
sbatch --array=0                                                    \
       --time=1:00:00  --cpus-per-task=4  --mem-per-cpu=4G  \
       submit_euler_mga.sh                # weights
sbatch --array=1-4                                                  \
       --time=36:00:00 --cpus-per-task=12 --mem-per-cpu=2G  \
       submit_euler_mga.sh                # sampling + bbo, units + minmax
sbatch --array=5,8                                                  \
       --time=24:00:00 --cpus-per-task=16 --mem-per-cpu=4G  \
       submit_euler_mga.sh                # batch bbo, batch4
sbatch --array=6,9                                                  \
       --time=24:00:00 --cpus-per-task=16 --mem-per-cpu=6G  \
       submit_euler_mga.sh                # batch bbo, batch8
sbatch --array=7,10                                                 \
       submit_euler_mga.sh                # batch bbo, batch16 (script default)

myjobs -j <jobID>                          # check actual time/CPU/RAM used
                                            # against the profile once each
                                            # range's jobs finish, and adjust
                                            # if the padding was off

# Once you trust the resources, submit everything together:
sbatch --array=0-10 submit_euler_mga.sh
```

Results land in the same place as the normal sweep, now tagged `_CAPEX` to
mark the new region x tech-group capex axes:
```
$SCRATCH/zen_runs/outputs/Crystal_Ball_ind_heat_v8_0_no_flexibility_nodiffusion_2050_1a_5a_interval_5ts_MGA_CAPEX_<mode>/
```
Download before scratch is purged (~2 weeks) — see "Results go to scratch" above.

For the full Euler setup (SSH keys, VS Code Remote-SSH, VPN, storage, modules,
resource tuning), see `Euler_setup_and_run_guide.md`.
