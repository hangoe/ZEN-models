# Running ZEN-models on Euler

Setup and run guide for the SLURM array sweeps in this repo (VS Code Remote-SSH,
MacBook). Replace `hannegoericke` with your ETH username if it differs.

---

## 1. One-time access setup

**First login in a plain Terminal (not VS Code).** The first connection asks for
an emailed verification code and acceptance of the usage rules, which VS Code
handles poorly:

```bash
ssh hannegoericke@euler.ethz.ch
```

Off the ETH network, connect the ETH VPN first (Cisco Secure Client →
`sslvpn.ethz.ch`).

**SSH key.** VS Code opens several connections and reconnects often, so use key login:

```bash
ssh-keygen -t ed25519 -C "hanne euler"
ssh-copy-id hannegoericke@euler.ethz.ch
```

Details: https://scicomp.ethz.ch/wiki/Accessing_the_clusters#SSH_keys

**SSH config** (`~/.ssh/config` on the Mac):

```
Host euler
    HostName euler.ethz.ch
    User hannegoericke
    IdentityFile ~/.ssh/id_ed25519
```

**VS Code.** Install the "Remote - SSH" extension → `Cmd+Shift+P` →
"Remote-SSH: Connect to Host…" → `euler` → open
`/cluster/home/hannegoericke/ZEN-models`. The integrated terminal runs on a login node.

XQuartz is not needed (it only matters for graphical Linux programs).

## 2. Euler basics

**Nodes.** You always land on a **login node**, which is for editing, submitting,
monitoring and quick tests only. Computation runs on **compute nodes** via `sbatch`.

**Storage.**

| Location | Path | Life span | Backup | Use it for |
|---|---|---|---|---|
| Home | `/cluster/home/hannegoericke` | permanent | yes | code, configs (50 GB / 500k files) |
| Scratch | `/cluster/scratch/hannegoericke` | **~2 weeks, auto-purged** | no | job outputs (2.7 TB) |

Code lives in Home, and results are written to scratch. Check quotas with `lquota`.

**Modules.**

```bash
module load stack/2024-06 gcc/12.2.0 python/3.12.8 gurobi/13.0.0
module list            # loaded modules
module spider python   # available versions
```

## 3. Files and directory layout

| File | Role |
|---|---|
| `run_model.py` | Runs **one row** of a sweep CSV (`--task_id`; CSV chosen by `--params`, default `parameters.csv`). Stages a private copy of the dataset, applies the row's `system` overrides to the copy, and runs ZEN-garden. Any override a row doesn't set falls back to `DEFAULT_SYSTEM_OVERRIDES`. For MGA configs it merges in the axes file (`data/config_euler/config_mga_axes_capex.yaml`, or the row's `axes_config`). |
| `parameters.csv` | Normal sweep table, one row per run. Columns: `my_dataset`, `my_comment`, one column per `system` override, plus optional meta columns (e.g. `numeric_focus`). Runs `data/config.yaml`. |
| `submit_euler.sh` | SLURM array job for `parameters.csv`. |
| `parameters_mga.csv` | MGA sweep table. It adds the `config`, `normalisation`, `batch_size`, `n_workers`, `tolerance_explore` and `axes_config` columns. |
| `submit_euler_mga.sh` | SLURM array job for `parameters_mga.csv`. Its header comment lists the per-range resource profiles. |
| `setup_euler_env.sh` | One-time environment build (venv + `zen_garden`, plus the MGA plugin and `pyoNearOpt`). |

```
/cluster/home/<user>/
├── ZEN-models/
│   ├── run_model.py, parameters*.csv, submit_euler*.sh, setup_euler_env.sh
│   └── data/
│       ├── config*.yaml
│       └── outputs/              <- local-run outputs (Euler outputs go to scratch)
└── ZEN-creator/
    └── outputs/
        └── zen_europe_ind_heat_v1_no_flexibility/   <- input dataset
```

Both repos must be in Home, because `run_model.py` looks datasets up in
`../ZEN-creator/outputs/<my_dataset>` (falling back to `data/`).

## 4. How a sweep works

```
parameters.csv        submit_euler.sh                 compute nodes
 task_id 47 ─┐     sbatch --array=47-49 ─┐       ┌─ run_model.py --task_id 47
 task_id 48 ─┼──────► (SLURM array)      ├──────►├─ run_model.py --task_id 48
 task_id 49 ─┘                           ┘       └─ run_model.py --task_id 49
```

`SLURM_ARRAY_TASK_ID` → `--task_id` → the matching row. Per task, `run_model.py`:

1. reads its row,
2. copies the dataset to a private per-task folder on scratch (so parallel tasks never clash and the original is never modified),
3. applies the row's overrides to the copy's `system.json`/`system.yaml`,
4. runs ZEN-garden, writing to `$SCRATCH/zen_runs/outputs/<my_dataset>_<my_comment>`.

With `--run_on local`, outputs go to `data/outputs/zen-europe-outputs-new/` instead.

## 5. Run order

```bash
# ONE-TIME
cd /cluster/home/<user>/ZEN-models
bash setup_euler_env.sh           # build venv; never create a venv inside the job
source .venv/bin/activate
python -c "from zen_garden import run, Results; print('imports OK')"

# CALIBRATE, then SWEEP
sbatch --array=49 submit_euler.sh       # one small row first, generous resources
myjobs -j <jobID>                       # read actual CPU/RAM/time
# ...edit --time / --cpus-per-task / --mem-per-cpu in submit_euler.sh...
sbatch --array=47,48 submit_euler.sh    # the rest (must match task_ids in the CSV)

# MONITOR
squeue                                  # PD = pending, R = running
scancel <jobID>
```

`--mail-type=END,FAIL` in the script emails you when a task ends or fails.
Logs: `zen_run_<jobID>_<task>.out` / `.err`.

## 6. Sizing SLURM resources

Total memory = `cpus-per-task × mem-per-cpu`.

1. **Overestimate the first run** so it can't fail on time/memory, and run only one task.
2. **Read the actual usage:**
   ```bash
   myjobs -j <jobID>
   sacct -j <jobID> --format=JobID,Elapsed,TotalCPU,MaxRSS,ReqMem,State
   ```
   `MaxRSS` is peak memory and `Elapsed` is wall time. CPU utilization shows whether the extra cores helped.
3. **Right-size:** set memory a bit above the peak and `--time` above the observed wall time. A job that exceeds `--time` is killed, and very large requests queue longer. The maximum runtime is 15 days.

What each setting controls:
- `--cpus-per-task`: cores for the single process (Gurobi is multithreaded). Keep `--ntasks=1`.
- `--mem-per-cpu`: RAM per core.
- `--time`: walltime.
- `--array`: which `task_id`s to run.

## 7. MGA sweeps

The normal sweep doesn't need the MGA plugin. For `parameters_mga.csv` /
`submit_euler_mga.sh`, run this once:

```bash
cd /cluster/home/<user>/ZEN-models
git pull
bash setup_euler_env.sh
# Output should end with:
#   registered plugins: [..., 'mga', ...]
#   pyoNearOpt OK
# If 'mga' is missing, update $HOME/ZEN-garden to the entry-point-aware version.
# setup_euler_env.sh clones $HOME/ZEN-garden-plugins (branch feature/mga) once and
# never re-pulls, so pull plugin updates by hand:
#   git -C $HOME/ZEN-garden-plugins pull

source .venv/bin/activate
python run_model.py --task_id 0 --run_on local --params parameters_mga.csv   # smoke test
```

Batch mode forks `batch_size` Gurobi workers, so size `cpus-per-task` as
`batch_size × Threads-per-worker`. Submit each range with its own profile (see
the header comment of `submit_euler_mga.sh`), for example:

```bash
sbatch --array=0-2 --time=72:00:00 --cpus-per-task=40 --mem-per-cpu=1G submit_euler_mga.sh
```

Use `check_mga_convergence.sh` to follow a running MGA job.

## 8. Getting results back

Results are under `$SCRATCH/zen_runs/outputs/<dataset>_<comment>`. Download them
promptly, because scratch is purged after ~2 weeks:

```bash
# on the Mac
scp -r euler:/cluster/scratch/hannegoericke/zen_runs/outputs/<run> ~/Downloads/
```

Alternatively, download from the VS Code Explorer.

## 9. Cheat sheet

```bash
ssh euler                     # login
lquota                        # storage quotas
sbatch --array=49 submit_euler.sh
squeue
myjobs -j <jobID>
sacct -j <jobID> --format=JobID,Elapsed,TotalCPU,MaxRSS,ReqMem,State
scancel <jobID>
```

Help: https://scicomp.ethz.ch · ticket https://smartdesk.ethz.ch ·
cluster-support@id.ethz.ch · SLURM script generator https://scicomp.ethz.ch/public/lsla/index2.html
