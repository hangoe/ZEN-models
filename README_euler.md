# ZEN-garden sweep on Euler

These files lie into the `ZEN-models` repo.

| File | Role |
|---|---|
| `run_model.py` | Run, adapted so `my_dataset`, `my_comment` and all `system_overrides` come from **one row** of `parameters.csv` (chosen by `--task_id`). |
| `parameters.csv` | Sweep table — **one row per run**. Columns = `my_dataset`, `my_comment`, and one column per `system.json` override. |
| `submit_euler.sh` | The SLURM **array** job: one job per row of `parameters.csv`. |
| `setup_euler_env.sh` | One-time environment build (venv + `zen_garden`). Run once on a login node. |

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
        └── Crystal_Ball_HG_v5_2_no_flexibility/   <- input dataset (system.json etc.)
```

Both repos (`ZEN-models` and `ZEN-creator`) must be present in your Euler Home.

## How the sweep works

```
parameters.csv           submit_euler.sh                compute nodes
 task_id 0 ─┐         sbatch --array=0-2 ─┐        ┌─ run_model.py --task_id 0
 task_id 1 ─┤───────► (SLURM array)       ├───────►├─ run_model.py --task_id 1
 task_id 2 ─┘                             ┘        └─ run_model.py --task_id 2
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

Row 0 of the template reproduces the current settings
(`aggregated_time_steps_per_year=10`, `interval_between_years=5`, etc.); rows 1–2
are examples showing how to vary the sweep. **Edit `parameters.csv` to define the
real runs** — add/remove columns to match exactly the keys you want in
`system_overrides` (any column other than `my_dataset`/`my_comment` is applied as
an override).

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
sbatch --array=1-2   submit_euler.sh             # launch the rest (match task_ids)

# MONITOR / COLLECT
squeue                                            # PD = pending, R = running
scancel <jobID>                                   # cancel if needed
```


For the full Euler setup (SSH keys, VS Code Remote-SSH, VPN, storage, modules,
resource tuning), see `Euler_setup_and_run_guide.md`.
