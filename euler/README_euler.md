# ZEN-garden sweep on Euler

These files lie into the `ZEN-models` repo.

| File | Role |
|---|---|
| `run_model.py` | Run, adapted so `my_dataset`, `my_comment`, `config` and all `system_overrides` come from **one row** of a sweep CSV (chosen by `--task_id`; the CSV itself by `--params`, default `parameters.csv`). |
| `parameters.csv` | Normal (non-MGA) sweep table — **one row per run**. Columns = `my_dataset`, `my_comment`, and one column per `system.json` override. No `config` column, so every row runs `data/config.json`. |
| `submit_euler.sh` | The SLURM **array** job for the normal sweep: one job per row of `parameters.csv`. |
| `parameters_mga.csv` | MGA sweep table — same shape as `parameters.csv` plus a `config` column picking which `data/config_mga*.json` to run (weights / sampling / bbo / oracle, sampling and bbo each with a `relative`- and `units`-normalisation config). |
| `submit_euler_mga.sh` | The SLURM **array** job for the MGA sweep: one job per row of `parameters_mga.csv`. |
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
# checkout) before continuing.

# 2. Smoke-test the cheapest mode (weights) on a login node first:
source .venv/bin/activate
python run_model.py --task_id 0 --run_on local --params parameters_mga.csv

# 3. Calibrate on the cluster, one row at a time, before trusting the
#    48h walltime in submit_euler_mga.sh -- oracle can run much longer
#    than weights/sampling/bbo. sampling, bbo and oracle are run first
#    this round (weights stays task_id 0, run later if needed):
sbatch --array=1 submit_euler_mga.sh   # sampling, relative  (task_id 1)
myjobs -j <jobID>                      # check actual time/CPU/RAM used
sbatch --array=2 submit_euler_mga.sh   # sampling, units     (task_id 2)
sbatch --array=3 submit_euler_mga.sh   # bbo, relative       (task_id 3)
sbatch --array=4 submit_euler_mga.sh   # bbo, units          (task_id 4)
sbatch --array=5 submit_euler_mga.sh   # oracle              (task_id 5, can be slow)

# 4. Once you trust the resources, submit them together:
sbatch --array=1-5 submit_euler_mga.sh
```

Results land in the same place as the normal sweep:
```
$SCRATCH/zen_runs/outputs/Crystal_Ball_ind_heat_v8_0_no_flexibility_nodiffusion_2050_1a_5a_interval_5ts_MGA_<mode>/
```
Download before scratch is purged (~2 weeks) — see "Results go to scratch" above.

For the full Euler setup (SSH keys, VS Code Remote-SSH, VPN, storage, modules,
resource tuning), see `Euler_setup_and_run_guide.md`.
