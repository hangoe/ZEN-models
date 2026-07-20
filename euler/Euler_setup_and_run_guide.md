# Running your ZEN-models job on Euler — setup & execution plan

*For Hanne · MacBook · first time on Euler · VS Code Remote-SSH*

This is a plan, not an execution. Nothing here has been run for you — follow it step by step. Wherever a command matters, I explain **what it does and why**. Replace `hannegoericke` with your real ETH username if it differs.

---

## 0. Quick answers to your three questions

**Do you need XQuartz?**
No — not for this workflow. XQuartz is an X11 server, used only to forward *graphical* Linux windows (a plotting GUI, a CAD app, etc.) back to your Mac. You will connect over SSH, edit files in VS Code, and run batch jobs — none of that needs a GUI. The presentation itself lists X11 as *optional*. You can leave XQuartz installed (harmless) or ignore it. Only reinstall/care about it if you later want to open a graphical program running on Euler.

**Can you SSH into Euler from VS Code, like your Windows remote server?**
Yes. Euler is a normal Linux SSH host. You use the **Remote-SSH** extension in VS Code exactly as you did before: connect to the host, open a folder that lives on Euler, edit and run in the integrated terminal. One important caveat for HPC: the terminal you get is on a **login node**, which is shared and only for editing, compiling, submitting and monitoring jobs — **never for running the actual computation**. The computation goes to compute nodes via SLURM (`sbatch`). More on that below.

**Can Claude Code in VS Code help?**
Yes, and it's a good fit here. If you run Claude Code inside a VS Code window that is connected to Euler via Remote-SSH, it runs *on the Euler login node* and can: fix the job script, set up the Python environment, submit jobs, read the SLURM `.out`/`.err` logs, and debug errors with you. Two caveats: (1) it must only do light work on the login node (editing/submitting/monitoring — that's exactly what it'd do here, so fine); (2) it needs outbound internet to reach Anthropic's API. Euler login nodes normally have internet (you can `pip install` and `git clone` there), so it should work; if your group restricts outbound traffic it might not connect, in which case run Claude Code locally on your Mac and let it drive `ssh` commands. **Recommendation: switch to it** — it will save you the most time on the environment setup and on reading SLURM logs.

---

## Part A — One-time setup (do this once)

### A1. First login must happen in a plain Terminal, not VS Code

Because this is your **first** Euler login, the first connection triggers an interactive step (an email verification code + accepting the usage rules) that the VS Code Remote-SSH extension handles poorly. So do the very first login in macOS **Terminal**:

```bash
ssh hannegoericke@euler.ethz.ch
```

- Enter your **ETH password** when prompted.
- On first login, a **verification code is emailed** to `hannegoericke@ethz.ch`. Type it in.
- **Accept the cluster usage rules** when asked. Your account is then created automatically.
- If you are **off the ETH network** (home/café), first connect the **ETH VPN** (Cisco Secure Client → `sslvpn.ethz.ch`), otherwise `euler.ethz.ch` is unreachable. On the ETH campus network you don't need the VPN.

Once you see the `EULER CLUSTER` banner and a prompt like `[hannegoericke@eu-login-XX ~]$`, you're in. Type `exit` to leave.

### A2. Set up an SSH key (strongly recommended before using VS Code)

VS Code Remote-SSH opens **several** SSH connections at once and reconnects often. Typing your password every time is painful, so set up key-based login. On your Mac Terminal:

```bash
# 1. Generate a key pair (press Enter to accept the default path; set a passphrase if you like)
ssh-keygen -t ed25519 -C "hanne euler"

# 2. Copy your PUBLIC key to Euler (asks for your ETH password once)
ssh-copy-id hannegoericke@euler.ethz.ch
```

`ssh-keygen` creates two files: `~/.ssh/id_ed25519` (private — never share) and `~/.ssh/id_ed25519.pub` (public). `ssh-copy-id` appends the public one to `~/.ssh/authorized_keys` on Euler, so Euler recognizes your Mac. The exact ETH key procedure is documented here if anything differs: https://scicomp.ethz.ch/wiki/Accessing_the_clusters#SSH_keys

Test it: `ssh hannegoericke@euler.ethz.ch` should now log in **without** a password prompt.

### A3. Add a shortcut in your SSH config

Create/edit `~/.ssh/config` on your Mac and add:

```
Host euler
    HostName euler.ethz.ch
    User hannegoericke
    IdentityFile ~/.ssh/id_ed25519
```

Now `ssh euler` is enough, and VS Code will list **euler** as a ready target.

### A4. Connect VS Code to Euler

1. Install **VS Code**, then the **"Remote - SSH"** extension (by Microsoft).
2. Press `Cmd+Shift+P` → **"Remote-SSH: Connect to Host…"** → pick **euler**.
3. A new VS Code window opens, connected to a login node.
4. **File → Open Folder →** `/cluster/home/hannegoericke/ZEN-models` (your repo).
5. Open the integrated terminal (`Ctrl+` `` ` ``) — this shell is on the Euler login node.

You now edit and submit from VS Code, and you can browse/download result files straight from the Explorer panel.

---

## Part B — Understand Euler before you run (the mental model)

**Nodes.** You always land on a **login node**. Real computation runs on **compute nodes**, which you reach *only* by submitting a job to the **batch system (SLURM)** with `sbatch`. Rule from the course: *don't run computations on login nodes* — they're for editing, compiling, quick tests, and file transfer.

**Storage** (this matters for your supervisor's instruction about scratch):

| Location | Path | Life span | Backup | Use it for |
|---|---|---|---|---|
| **Home** | `/cluster/home/hannegoericke` | Permanent | Yes | Code, scripts, configs. **50 GB / 500k files** limit. |
| **Global scratch** | `/cluster/scratch/hannegoericke` | **~2 weeks (auto-purged)** | No | Fast, large working space. **2.7 TB**. Job outputs. |

Check your quotas anytime with `lquota`.

Your supervisor's point — *"Sachen liegen auf Home → Ergebnisse auf scratch schreiben"* — maps cleanly onto this: **keep the code in Home, write results to scratch.** Scratch is big and fast, which is what you want for many output folders. Just remember scratch is **purged after ~2 weeks and never backed up**, so download anything you want to keep (from VS Code's Explorer, or `scp`) promptly.

**Modules.** Software isn't globally available; you activate it per session with `module load`. The layered order matters: first the stack, then the compiler, then things built on it:

```bash
module load stack/2024-06 gcc/12.2.0 python/3.12.8 gurobi/13.0.0
```

`module list` shows what's loaded; `module spider python` lists available versions.

---

## Part C — What your job does (your own files, not Jan's)

Jan's files were **reference only**. Your actual run uses your own set of four files
in `ZEN-models` — described in full in **`README_euler.md`**. In short:

1. **`run_model.py`** — your script, adapted so `my_dataset`, `my_comment`, and every
   `system_overrides` value come from **one row** of `parameters.csv` (selected by
   `--task_id`). Each task stages a private copy of the dataset, patches the copy's
   `system.json`, and writes results to scratch.

2. **`parameters.csv`** — your sweep table, one row per run (columns = `my_dataset`,
   `my_comment`, and one column per `system.json` override).

3. **`submit_euler.sh`** — the SLURM **array** job: `--array=0-4` launches one
   independent job per row, each passed its `SLURM_ARRAY_TASK_ID` as `--task_id`.
   That's the *"Array → verschiedene Jobs starten"* piece.

4. **`setup_euler_env.sh`** — one-time environment build.

**Results on scratch:** handled inside `run_model.py` — with `--run_on euler` it writes
to `$SCRATCH/zen_runs/...` automatically, so the code stays in Home and results go to
scratch, exactly as your supervisor asked. No config file to edit.

### C-note: two things to confirm before running

1. **Build the environment once, don't create a venv inside the job.** A fresh venv
   has no packages, and parallel array tasks would corrupt a shared `.venv`. Run
   `setup_euler_env.sh` once beforehand; the job only **activates** the venv. (Pick
   the correct `zen_garden` install line in that script — the one bit that depends on
   how your group ships the package.)

2. **Both repos must be in Home.** `run_model.py` reads datasets from
   `../ZEN-creator/outputs/<my_dataset>`, so `ZEN-creator` must sit next to
   `ZEN-models` in `/cluster/home/<user>/`.

---

## Part D — SLURM resources (your supervisor's first instruction)

*"SLURM Daten/Ressourcen: Zeit overestimaten; rausfinden wie viel CPU (16 CPU × 8 GB) → RAM per CPU."*

**How SLURM memory math works** (so the numbers are clear): you request memory **per CPU**, and total memory = `cpus-per-task × mem-per-cpu`.

- Jan's script: `--cpus-per-task=32 --mem-per-cpu=8G` → **32 cores, 256 GB** per array task, `--time=08:00:00`.
- Your supervisor's reference "16 CPU × 8 GB" → **16 cores, 128 GB**.

These disagree, and that's fine — the supervisor's point is: **you don't yet know the right size, so measure it.** The method:

1. **First run: overestimate deliberately.** Give it generous time and memory so it can't fail for those reasons. Run **one** task first (`sbatch --array=0 submit_euler.sh`) rather than all rows, so you spend little while calibrating.
2. **After it finishes, read the actual usage:**
   ```bash
   myjobs -j <jobID>              # shows requested vs. used: wall-clock, CPU utilization, resident memory
   sacct -j <jobID> --format=JobID,Elapsed,TotalCPU,MaxRSS,ReqMem,State
   ```
   `MaxRSS` = peak memory actually used; `Elapsed` = wall time used; CPU utilization tells you whether the cores were even helping.
3. **Right-size and launch the rest.** If, say, it peaked at ~90 GB and used ~3 h, set memory a bit above the peak (e.g. `--mem-per-cpu` so total ≈ 120–140 GB) and `--time` above the observed wall time (over-estimate — but not wildly, since huge requests queue longer). Then run the remaining rows: `sbatch --array=1-4 submit_euler.sh`.

Guidance from the course: over-estimating time is safer than under-estimating (a job that exceeds its `--time` is **killed**), but very large requests wait longer in the queue and waste the shared resource — so tighten toward the measured values on the real runs. Max runtime on Euler is 15 days.

**Which knob is which:**
- `--cpus-per-task` = cores for one task. Gurobi is multithreaded and will use them, so this is your CPU knob. (Because you run **one** process per array task, `--ntasks=1` is correct and `--cpus-per-task` is the right place to put the cores — not `--ntasks`.)
- `--mem-per-cpu` = RAM per core; total scales with cores.
- `--time` = walltime; job is killed if exceeded.
- `--array` = which `task_id`s to run, one job each.

---

## Part E — Step-by-step execution plan

Do these in order. Steps 1–4 are one-time; 5 onward is the run loop. Full detail is
in **`README_euler.md`**; this is the checklist.

**1. Get both repos onto Euler (Home).** In VS Code's Euler terminal:
```bash
cd /cluster/home/hannegoericke
git clone <ZEN-models repo URL>     # or confirm it's already here
git clone <ZEN-creator repo URL>    # datasets live here; must sit next to ZEN-models
```

**2. Add your four files to `ZEN-models`:** `run_model.py`, `parameters.csv`,
`submit_euler.sh`, `setup_euler_env.sh`. Submit jobs from this directory —
`run_model.py` reads `parameters.csv` from next to itself.

**3. Build the Python environment ONCE** (not inside the job):
```bash
cd /cluster/home/hannegoericke/ZEN-models
bash setup_euler_env.sh            # first pick the correct zen_garden install line in it
source .venv/bin/activate
python -c "from zen_garden import run, Results; print('imports OK')"
```

**4. Fill in `parameters.csv`** with your real runs (all 5 rows already match your
current TSA/time settings, one per model in `ZEN-creator/outputs`). Optional tiny
smoke test on the login node (keep settings small):
```bash
python run_model.py --task_id 0 --run_on local
```

**5. First calibration run — ONE task, overestimated resources:**
```bash
sbatch --array=0 submit_euler.sh
squeue                 # PD = pending, R = running
myjobs -j <jobID>      # detailed view
```
Check `zen_run_<jobID>_0.out` and `..._0.err` for progress/errors.

**6. Measure and right-size** (Part D): read `MaxRSS`, `Elapsed`, CPU utilization; edit
`--time`, `--cpus-per-task`, `--mem-per-cpu` in `submit_euler.sh`.

**7. Launch the remaining rows:**
```bash
sbatch --array=1-4 submit_euler.sh    # match the task_ids in your parameters.csv
```

**8. Monitor.** `squeue` for state, `myjobs -j <id>` for detail, `scancel <id>` to kill.
`--mail-type=END,FAIL` (already in the script) emails you when a task ends or fails.

**9. Get results back.** Results are under `$SCRATCH/zen_runs/outputs/<dataset>_<comment>`.
In VS Code, browse there and **download**, or:
```bash
# run this on your MAC, not on Euler:
scp -r euler:/cluster/scratch/hannegoericke/zen_runs/outputs/... ~/Downloads/
```
Do this promptly — **scratch is purged after ~2 weeks and not backed up.**

---

## Part F — Command cheat-sheet

```bash
# Access
ssh euler                      # login (after config in A3)
lquota                         # storage quotas (home + scratch)

# Modules
module load stack/2024-06 gcc/12.2.0 python/3.12.8 gurobi/13.0.0
module list                    # what's loaded
module spider python           # find versions

# Submit / monitor
sbatch --array=0 submit_euler.sh           # submit one task (calibrate)
sbatch --array=1-4 submit_euler.sh         # submit a range of rows
squeue                                     # my queued/running jobs (PD/R)
myjobs -j <jobID>                          # detailed job info + usage
sacct -j <jobID> --format=JobID,Elapsed,TotalCPU,MaxRSS,ReqMem,State
scancel <jobID>                            # cancel a job

# Files
scp -r euler:/cluster/scratch/hannegoericke/zen_runs/outputs/... ~/Downloads/   # download (run on Mac)
```

**Help:** wiki https://scicomp.ethz.ch · ticket https://smartdesk.ethz.ch · email cluster-support@id.ethz.ch. There's also a SLURM script generator: https://scicomp.ethz.ch/public/lsla/index2.html

---

## Open items to confirm (short list)

1. How the **`zen_garden` package** should be installed — an editable install of a
   ZEN-garden source repo, from `ZEN-models` itself, or from PyPI? (Pick the right
   OPTION in `setup_euler_env.sh`.)
2. **Gurobi license** on compute nodes, if `zen_garden` uses Gurobi (`echo $GRB_LICENSE_FILE`).
3. The exact **rows/columns** you want in `parameters.csv` (all 5 rows reproduce your current settings, one per model in `ZEN-creator/outputs`).
4. Final **resource sizing** (`--time`, `--cpus-per-task`, `--mem-per-cpu`) after the calibration run.
