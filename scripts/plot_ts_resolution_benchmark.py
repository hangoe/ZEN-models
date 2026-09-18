"""Benchmarks Euler resource usage (wall-clock time, peak memory) of the
plain (non-MGA) v9_0 no_flexibility_nodiffusion solve across temporal
resolution: 1/3/10/20 representative timesteps/year, 2020_16a_2a horizon
(parameters.csv task_ids 10-13, submit_euler.sh --array=10-13) -- single
deterministic solves under euler_outputs (RUN_ROOT below), one per row of
parameters.csv, no MGA plugin involved. Extended 2026-09-18 with 3 MGA batch
bbo runs from parameters_mga.csv (task_id 3-5, same runs plot_mga_ts_
resolution.py's fig3a/3b/4 plot the exploration *convergence* of -- see that
module's docstring for what each one varies) under euler_outputs_mga
(MGA_ROOT below) -- here it's their resource usage/wall-clock cost that's
plotted, same 4-panel treatment as the plain-solve family, not their
convergence. These are a genuinely different kind of workload (a batch_size-
worker pool jointly exploring a near-optimal region over hundreds of LP
solves, not one deterministic solve), so their own #SBATCH footprints (160G/
40cpu for task_id 4's seed42 rerun and task_id 3's 4a/10a rerun, 192G/32cpu
for task_id 5's batch16 rerun -- see submit_euler_mga.sh) are much bigger
than the plain family's 16cpu/128G default and get their own hatch
automatically (see _resource_label/hatch_by_profile below, unchanged). All
three still land on the "1" (aggregated_time_steps_per_year) x-position,
since all three ARE 1ts configs -- see RUNS' MGA_ROOT entries below for what
distinguishes each from the others and from the plain 1ts family.

benchmarking.json's own "solving_time" field undercounts real wall-clock
time (it only covers the solver call itself, not model construction/I/O) --
see plot_mga_results._cum_seconds_wallclock's docstring for the 2.3x-3.7x
gap this project already found for MGA runs. Rather than repeat that
calibration here, this script reads real wall-clock elapsed time and peak
memory (MaxRSS) straight from each run's slurm_usage.json sidecar file
(written from `sacct -j <jobid> --format=JobID,Elapsed,MaxRSS,...` at
download time -- see the mga_tests figure plan for the exact commands).

fig5_resource_usage_vs_resolution plots four panels as a function of
aggregated_time_steps_per_year: wall-clock minutes, peak memory (MaxRSS,
GB), memory efficiency (MaxRSS / ReqMem, %), and CPU efficiency (TotalCPU /
(Elapsed x AllocCPUs), %, the same figure `seff <jobid>` reports). Both
efficiency panels show how badly over-provisioned the shared
16-cpu/128G-per-job SBATCH profile (submit_euler.sh's --array=10-13 header
comment) is at low resolution -- the 1ts run uses only ~7% of its 16
allocated cores (the LP is too small for Gurobi's barrier method to keep
them busy) and ~7% of its requested memory, while 10ts/20ts sit much closer
to fully using both. A run whose folder or slurm_usage sidecar isn't
downloaded yet is skipped with a printed reason, same convention as
plot_mga_ts_resolution.py's TS_RUNS loop. The 1ts row has been resubmitted
at shrinking #SBATCH footprints (see RUNS below) to quantify that
over-provisioning; each resubmission adds its own bar rather than replacing
the original one, so the comparison stays visible.

Usage:
    python scripts/plot_ts_resolution_benchmark.py
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from plots.figure_settings import SCENARIO_PALETTE, apply_font_mode

apply_font_mode()

from plot_mga_results import FIGURES_DIR, REPO_ROOT, savefig

RUN_ROOT = REPO_ROOT / "data" / "outputs" / "euler_outputs"
MGA_ROOT = REPO_ROOT / "data" / "outputs" / "euler_outputs_mga"
MODEL = "Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion"

# Ordered list of runs to plot: (aggregated_time_steps_per_year, run-folder
# suffix, slurm_usage sidecar filename, root, divider_before). The 1ts
# entries (task_id 10) are resubmissions at shrinking #SBATCH footprints to
# see how far the shared 16-cpu/128G default (used for 3/10/20ts too) is
# over-provisioned at low resolution -- since parameters.csv only has one row
# per ts value, each resubmission reused the same output folder and would
# otherwise have clobbered the previous run's slurm_usage.json, so those are
# kept as separate sidecar files in that folder (slurm_usage.json itself is
# retired in favour of explicit per-profile names). Note the 2cpu/10G row:
# the first 2cpu/10G attempt (job 14433884) OOM-killed during model
# construction (before the solver even started -- peak logged at ~4.1GB
# right before the kill), so 2cpu/12G (job 14434074) was submitted instead to
# get a clean CPU-only comparison; this row is a second 2cpu/10G attempt (job
# 14434647) to see whether the OOM reproduces at that exact footprint.
#
# divider_before=True draws a vertical dashed divider immediately before that
# entry (fig5_resource_usage_vs_resolution) -- used to mark a group boundary,
# not every ts change: the first True below separates the plain-solve
# family's grouped 1ts profile-recalibration bars (leftmost) from its
# 3/10/20ts bars; the second separates the plain-solve family (all of it)
# plus the two MGA "same-config-as-1ts" comparison runs (seed42) from the two
# MGA runs whose CONFIG actually differs (task_id 3's 4a/10a period schedule,
# task_id 5's batch16) -- see the module docstring for what those 3 MGA
# entries (added 2026-09-18) are.
RUNS: list[tuple[int, str, str, Path, bool]] = [
    (1, "2020_16a_2a_interval_1ts", "slurm_usage_16cpu_128g.json", RUN_ROOT, False),
    (1, "2020_16a_2a_interval_1ts", "slurm_usage_3cpu_12g.json", RUN_ROOT, False),
    (1, "2020_16a_2a_interval_1ts", "slurm_usage_6cpu_12g.json", RUN_ROOT, False),
    (1, "2020_16a_2a_interval_1ts", "slurm_usage_2cpu_12g.json", RUN_ROOT, False),
    (1, "2020_16a_2a_interval_1ts", "slurm_usage_2cpu_10g.json", RUN_ROOT, False),
    (3, "2020_16a_2a_interval_3ts", "slurm_usage.json", RUN_ROOT, True),
    (10, "2020_16a_2a_interval_10ts", "slurm_usage.json", RUN_ROOT, False),
    (20, "2020_16a_2a_interval_20ts", "slurm_usage.json", RUN_ROOT, False),
    # task_id 4: MGA batch_bbo, same 1ts/7a_5a/batch4/share/tol002 config as
    # parameters_mga.csv's task_id 0, but seed_rng=42 pinned -- see
    # plot_mga_ts_resolution.py's TS_RUNS "1ts_seed42" entry.
    (1, "2020_7a_5a_interval_1ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002_seed42",
     "slurm_usage.json", MGA_ROOT, False),
    # task_id 3: MGA batch_bbo, same 1ts/batch4/share/tol002 config, but a
    # 4a/10a period schedule instead of task_id 0's 7a/5a -- see
    # plot_mga_ts_resolution.py's TS_RUNS "1ts_4a_10a" entry. divider_before
    # marks this as where the "different config, not just a rerun" MGA runs
    # start (see docstring above).
    (1, "2020_4a_10a_interval_1ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002",
     "slurm_usage.json", MGA_ROOT, True),
    # task_id 5: MGA batch_bbo, batch_size=n_workers=16 (vs. task_id 0's 4) --
    # see plot_mga_ts_resolution.py's TS_RUNS "1ts_batch16" entry.
    (1, "2020_7a_5a_interval_1ts_MGA_CAPEX_CUM_batch_bbo_share_batch16_tol002",
     "slurm_usage.json", MGA_ROOT, False),
]


def _parse_mem_kb(mem_str: str) -> float:
    """Parses a SLURM ReqMem string (e.g. "128G") into KiB."""
    units = {"K": 1, "M": 1024, "G": 1024 ** 2, "T": 1024 ** 3}
    return float(mem_str[:-1]) * units[mem_str[-1].upper()]


def load_usage() -> list[tuple[int, dict, bool]]:
    usage: list[tuple[int, dict, bool]] = []
    for ts, suffix, usage_filename, root, divider_before in RUNS:
        run_dir = root / f"{MODEL}_{suffix}"
        usage_file = run_dir / usage_filename
        if not usage_file.exists():
            print(f"  {ts}ts ({usage_filename}): not downloaded yet at "
                  f"{run_dir.relative_to(REPO_ROOT)}, skipping")
            continue
        usage.append((ts, json.loads(usage_file.read_text()), divider_before))
    return usage


# Hatches applied to runs whose #SBATCH allocation differs from this run
# family's shared default (16 cpus/128G) -- e.g. a recalibration row
# submitted with a smaller --cpus-per-task/--mem-per-cpu -- so each
# non-default profile reads visibly differently at a glance, not just via
# its legend text. Cycled in order of first appearance if there's more than
# one non-default profile (e.g. two recalibration attempts at different
# footprints).
_DIFF_HATCHES = ["//", "\\\\", "xx", "oo"]


def _resource_label(entry: dict) -> str:
    return f"{entry['alloc_cpus']} CPU, {entry['req_mem']}"


def fig5_resource_usage_vs_resolution(usage: list[tuple[int, dict, bool]]) -> None:
    ts_values = [ts for ts, _, _ in usage]
    entries = [entry for _, entry, _ in usage]
    boundary_indices = [i for i, (_, _, divider_before) in enumerate(usage) if divider_before and i > 0]
    positions = range(len(usage))
    minutes = [e["elapsed_seconds"] / 60 for e in entries]
    # sacct's MaxRSS is in KiB; divide by 1024**2 for GiB, labelled "GB" below
    # per this project's convention of not distinguishing binary/decimal units
    # in figure labels.
    gb = [e["max_rss_kb"] / (1024 ** 2) for e in entries]
    mem_efficiency = [
        100 * e["max_rss_kb"] / _parse_mem_kb(e["req_mem"]) for e in entries
    ]
    cpu_efficiency = [
        100 * e["total_cpu_seconds"] / (e["elapsed_seconds"] * e["alloc_cpus"])
        for e in entries
    ]

    # Resource profile per run -- the most common (alloc_cpus, req_mem) pair
    # across the runs actually loaded is the "default" #SBATCH profile and is
    # drawn as a plain bar; every other profile (e.g. a recalibration run at
    # a smaller footprint) gets its own hatch instead, so it's visually
    # distinguishable in every panel, not just ax_time.
    profiles = [_resource_label(e) for e in entries]
    default_profile = max(set(profiles), key=profiles.count)
    hatch_by_profile = {default_profile: None}
    for p in profiles:
        if p not in hatch_by_profile:
            hatch_by_profile[p] = _DIFF_HATCHES[(len(hatch_by_profile) - 1) % len(_DIFF_HATCHES)]

    fig, ((ax_time, ax_mem), (ax_memeff, ax_cpueff)) = plt.subplots(2, 2, figsize=(10.5, 8.5))

    # Vertical dividers at each RUNS entry marked divider_before=True (see
    # RUNS' own docstring for what each boundary in the current ordering
    # separates -- the plain-solve family's grouped 1ts profile-
    # recalibration bars vs. its 3/10/20ts bars, and the "same-config-as-1ts"
    # MGA reruns vs. the "different-config" MGA reruns).
    def _bar(ax, values, color):
        bars = ax.bar(positions, values, color=color, edgecolor="black", linewidth=0.5)
        for bar, p in zip(bars, profiles):
            if hatch_by_profile[p]:
                bar.set_hatch(hatch_by_profile[p])
        for boundary_idx in boundary_indices:
            ax.axvline(boundary_idx - 0.5, color="black", linestyle="--", linewidth=1, alpha=0.6)
        return bars

    _bar(ax_time, minutes, SCENARIO_PALETTE[0])
    ax_time.set_xlabel("Representative timesteps / year")
    ax_time.set_ylabel("Wall-clock time [min]")
    ax_time.set_title("Solve time")
    # Legend (leftmost panel only) spelling out cpus/mem per resource
    # profile, so the hatch pattern's meaning is readable without cross-
    # referencing the other panels. Swatches are neutral light grey rather
    # than ax_time's own blue, since the same profile/hatch applies across
    # all four panels' different bar colors, not just this one.
    ax_time.legend(
        handles=[
            Patch(facecolor="#d9d9d9", edgecolor="black", linewidth=0.5,
                  hatch=hatch_by_profile[p], label=p)
            for p in sorted(hatch_by_profile, key=lambda p: p != default_profile)
        ],
        fontsize=8,
        loc="upper left",
    )

    _bar(ax_mem, gb, SCENARIO_PALETTE[4])
    ax_mem.set_xlabel("Representative timesteps / year")
    ax_mem.set_ylabel("Peak memory [GB]")
    ax_mem.set_title("Peak memory use (MaxRSS)")

    _bar(ax_memeff, mem_efficiency, SCENARIO_PALETTE[2])
    ax_memeff.set_xlabel("Representative timesteps / year")
    ax_memeff.set_ylabel("Memory efficiency [%]")
    ax_memeff.set_title("Memory efficiency (MaxRSS / ReqMem)")
    ax_memeff.set_ylim(0, 100)

    _bar(ax_cpueff, cpu_efficiency, SCENARIO_PALETTE[3])
    ax_cpueff.set_xlabel("Representative timesteps / year")
    ax_cpueff.set_ylabel("CPU efficiency [%]")
    ax_cpueff.set_title("CPU efficiency (TotalCPU / (Elapsed × AllocCPUs))")
    ax_cpueff.set_ylim(0, 100)

    for ax, values, fmt in (
        (ax_time, minutes, "{:,.0f}"),
        (ax_mem, gb, "{:,.1f}"),
        (ax_memeff, mem_efficiency, "{:,.1f}%"),
        (ax_cpueff, cpu_efficiency, "{:,.1f}%"),
    ):
        ax.set_xticks(list(positions))
        ax.set_xticklabels([str(ts) for ts in ts_values])
        ax.grid(True, axis="y", alpha=0.3)
        for x, v in zip(positions, values):
            ax.text(x, v, fmt.format(v), ha="center", va="bottom", fontsize=8)

    fig.suptitle("Crystal Ball ind heat, v9.0, no flexibility, no diffusion -- "
                  "plain 2020_16a_2a solves vs. MGA batch_bbo 1ts reruns")
    fig.tight_layout()
    savefig(fig, "fig5_resource_usage_vs_resolution")


def main() -> None:
    usage = load_usage()
    if len(usage) < 2:
        print("  fewer than 2 runs downloaded, skipping fig5_resource_usage_vs_resolution")
        return
    fig5_resource_usage_vs_resolution(usage)


if __name__ == "__main__":
    main()
