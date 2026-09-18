"""Benchmarks Euler resource usage (wall-clock time, peak memory) of the
plain (non-MGA) v9_0 no_flexibility_nodiffusion solve across temporal
resolution: 1/3/10/20 representative timesteps/year, 2020_16a_2a horizon
(parameters.csv task_ids 10-13, submit_euler.sh --array=10-13) -- single
deterministic solves under euler_outputs (RUN_ROOT below), one per row of
parameters.csv, no MGA plugin involved. Extended 2026-09-18 with 6 MGA batch
bbo runs from parameters_mga.csv (task_id 0-5, the exact same runs plot_mga_
ts_resolution.py's fig3a/3b/4/6 plot the exploration *convergence*/near-
optimal-space *size* of -- see that module's docstring, and its TS_RUNS/
TS_COLOR, for what each one varies) under euler_outputs_mga (MGA_ROOT below)
-- here it's their resource usage/wall-clock cost that's plotted, same
4-panel treatment as the plain-solve family, not their convergence. These are
a genuinely different kind of workload (a batch_size-worker pool jointly
exploring a near-optimal region over hundreds of LP solves, not one
deterministic solve), so their own #SBATCH footprints (160G/40cpu for
task_id 4's seed42 rerun and task_id 3's 4a/10a rerun, 192G/32cpu for
task_id 5's batch16 rerun -- see submit_euler_mga.sh) are much bigger than
the plain family's 16cpu/128G default and get their own hatch automatically
(see _resource_label/hatch_by_profile below, unchanged). Four of the six
(task_id 0's "1ts" baseline, task_id 4's seed42, task_id 5's batch16, and
task_id 3's 4a/10a) land on the "1" (aggregated_time_steps_per_year)
x-position, since all four ARE 1ts configs -- see RUNS' MGA_ROOT entries
below for what distinguishes each from the others and from the plain 1ts
family; task_id 1/2 (MGA "3ts"/"10ts") land on "3"/"10" instead, alongside
(but visually distinct in color from) the plain 3ts/10ts solves.

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
# Reused (not re-picked) so a run reads as the same color here as in
# fig3a/3b/4/6 -- see plot_mga_ts_resolution.py's TS_COLOR docstring for how
# each of these three hues was chosen.
from plot_mga_ts_resolution import TS_COLOR

RUN_ROOT = REPO_ROOT / "data" / "outputs" / "euler_outputs"
MGA_ROOT = REPO_ROOT / "data" / "outputs" / "euler_outputs_mga"
MODEL = "Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion"

# Ordered list of runs to plot: (aggregated_time_steps_per_year, run-folder
# suffix, slurm_usage sidecar filename, root, group, ts_color_key). The 1ts
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
# group (5th field): fig5_resource_usage_vs_resolution draws a vertical
# dashed divider wherever this changes between two consecutive LOADED
# entries -- not a per-entry divider_before flag (this project's first
# attempt at this split used one, keyed to a specific entry; it broke the
# moment that entry itself wasn't downloaded yet, silently dropping the
# divider instead of just moving to the next-loaded entry of the same
# group). Three groups, left to right: "plain_1ts" (the profile-
# recalibration bars), "plain_other_ts" (3ts/10ts/20ts), "mga" (every MGA
# run, all six task_id 0-5, regardless of their own ts value) -- so the
# divider before "plain_other_ts" survives even if e.g. the 2cpu/10G row
# above is still missing, and the one before "mga" survives even though, as
# of this writing, its own first three entries (task_id 0/1/2) haven't
# synced down yet either.
#
# ts_color_key (6th field): None for every plain-solve entry (RUN_ROOT) --
# these all get PLAIN_RUN_COLOR below, one shared color, since none of them
# is one of plot_mga_ts_resolution.py's TS_RUNS and so has no fig3/4/6 color
# of its own. Each MGA entry instead names its own TS_COLOR key, so it reuses
# the exact same hue fig3a/3b/4/6 already plot it in -- deliberately NOT
# "3ts"/"10ts" for the plain 3ts/10ts rows just above, even though those keys
# exist in TS_COLOR: that pair belongs to the MGA 3ts/10ts convergence runs
# (parameters_mga.csv task_id 1/2, under MGA_ROOT), a different run from
# these plain deterministic solves (under RUN_ROOT) that only coincidentally
# share a timestep count.
RUNS: list[tuple[int, str, str, Path, str, str | None]] = [
    (1, "2020_16a_2a_interval_1ts", "slurm_usage_16cpu_128g.json", RUN_ROOT, "plain_1ts", None),
    (1, "2020_16a_2a_interval_1ts", "slurm_usage_3cpu_12g.json", RUN_ROOT, "plain_1ts", None),
    (1, "2020_16a_2a_interval_1ts", "slurm_usage_6cpu_12g.json", RUN_ROOT, "plain_1ts", None),
    (1, "2020_16a_2a_interval_1ts", "slurm_usage_2cpu_12g.json", RUN_ROOT, "plain_1ts", None),
    (1, "2020_16a_2a_interval_1ts", "slurm_usage_2cpu_10g.json", RUN_ROOT, "plain_1ts", None),
    (3, "2020_16a_2a_interval_3ts", "slurm_usage.json", RUN_ROOT, "plain_other_ts", None),
    (10, "2020_16a_2a_interval_10ts", "slurm_usage.json", RUN_ROOT, "plain_other_ts", None),
    (20, "2020_16a_2a_interval_20ts", "slurm_usage.json", RUN_ROOT, "plain_other_ts", None),
    # The six MGA entries below are ordered to match plot_mga_ts_resolution.
    # py's own TS_RUNS/TS_COLOR insertion order (1ts, 1ts_seed42,
    # 1ts_batch16, 3ts, 10ts, 1ts_4a_10a), so this legend and fig3a/3b/4/6's
    # own legends list the same six runs in the same order. All six share
    # group="mga", so they land in one contiguous group regardless of which
    # of them are actually downloaded yet (see the group field's own note
    # above).
    #
    # task_id 0: MGA batch_bbo, CAPEX-CUM/share axes, batch_size=4,
    # tolerance_explore=0.02, 1ts/7a_5a -- this project's MGA baseline (see
    # [[project_mga_baseline_run]]); plot_mga_ts_resolution.py's TS_RUNS
    # "1ts" entry.
    (1, "2020_7a_5a_interval_1ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002",
     "slurm_usage.json", MGA_ROOT, "mga", "1ts"),
    # task_id 4: same config as task_id 0, but seed_rng=42 pinned -- see
    # plot_mga_ts_resolution.py's TS_RUNS "1ts_seed42" entry.
    (1, "2020_7a_5a_interval_1ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002_seed42",
     "slurm_usage.json", MGA_ROOT, "mga", "1ts_seed42"),
    # task_id 5: MGA batch_bbo, batch_size=n_workers=16 (vs. task_id 0's 4) --
    # see plot_mga_ts_resolution.py's TS_RUNS "1ts_batch16" entry.
    (1, "2020_7a_5a_interval_1ts_MGA_CAPEX_CUM_batch_bbo_share_batch16_tol002",
     "slurm_usage.json", MGA_ROOT, "mga", "1ts_batch16"),
    # task_id 1: same config as task_id 0, but 3 aggregated timesteps/year --
    # see plot_mga_ts_resolution.py's TS_RUNS "3ts" entry. Lands on the "3"
    # x-position alongside (but a different color from) the plain 3ts solve
    # above -- same coincidental-ts-value-collision note as RUNS' own
    # docstring above.
    (3, "2020_7a_5a_interval_3ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002",
     "slurm_usage.json", MGA_ROOT, "mga", "3ts"),
    # task_id 2: same config as task_id 0, but 10 aggregated timesteps/year --
    # see plot_mga_ts_resolution.py's TS_RUNS "10ts" entry.
    (10, "2020_7a_5a_interval_10ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002",
     "slurm_usage.json", MGA_ROOT, "mga", "10ts"),
    # task_id 3: same config as task_id 0, but a 4a/10a period schedule
    # instead of task_id 0's 7a/5a -- see plot_mga_ts_resolution.py's
    # TS_RUNS "1ts_4a_10a" entry.
    (1, "2020_4a_10a_interval_1ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002",
     "slurm_usage.json", MGA_ROOT, "mga", "1ts_4a_10a"),
]

# Shared color for every plain-solve (non-MGA) bar -- ETH grey, the same hue
# fig4_implied_threshold_for_tolerance reserves for its own non-run-specific
# reference lines (see plot_mga_ts_resolution.py's GREY constant), reused
# here for the same reason: it's neutral and outside TS_COLOR's per-run
# palette, so it can't be mistaken for one of the six MGA runs' own colors in
# the legend below.
PLAIN_RUN_COLOR = SCENARIO_PALETTE[6]


def _parse_mem_kb(mem_str: str) -> float:
    """Parses a SLURM ReqMem string (e.g. "128G") into KiB."""
    units = {"K": 1, "M": 1024, "G": 1024 ** 2, "T": 1024 ** 3}
    return float(mem_str[:-1]) * units[mem_str[-1].upper()]


def load_usage() -> list[tuple[int, dict, str, str | None]]:
    usage: list[tuple[int, dict, str, str | None]] = []
    for ts, suffix, usage_filename, root, group, ts_color_key in RUNS:
        run_dir = root / f"{MODEL}_{suffix}"
        usage_file = run_dir / usage_filename
        if not usage_file.exists():
            print(f"  {ts}ts ({usage_filename}): not downloaded yet at "
                  f"{run_dir.relative_to(REPO_ROOT)}, skipping")
            continue
        usage.append((ts, json.loads(usage_file.read_text()), group, ts_color_key))
    return usage


# Hatches applied to runs whose #SBATCH allocation differs from this run
# family's shared default (16 cpus/128G) -- e.g. a recalibration row
# submitted with a smaller --cpus-per-task/--mem-per-cpu -- so each
# non-default profile reads visibly differently at a glance, not just via
# its legend text. Cycled in order of first appearance if there's more than
# one non-default profile (e.g. two recalibration attempts at different
# footprints). Currently 5 distinct non-default profiles are in play (3/6/2
# CPU plain-solve recalibrations, plus the two MGA rerun footprints, 40
# CPU/160G and 32 CPU/192G) -- sized at 6 rather than exactly 5 so the still-
# undownloaded 2cpu/10G recalibration (see RUNS above) also gets its own
# pattern once it syncs down, instead of silently wrapping around and
# colliding with an earlier profile the way a bare 4-pattern cycle just did
# (32 CPU/192G was landing on the same "//" hatch as 3 CPU/12G).
_DIFF_HATCHES = ["//", "\\\\", "xx", "oo", "++", ".."]


def _resource_label(entry: dict) -> str:
    return f"{entry['alloc_cpus']} CPU, {entry['req_mem']}"


def fig5_resource_usage_vs_resolution(usage: list[tuple[int, dict, str, str | None]]) -> None:
    ts_values = [ts for ts, _, _, _ in usage]
    entries = [entry for _, entry, _, _ in usage]
    # A boundary sits wherever group changes between two consecutive LOADED
    # entries -- computed off `usage` (what's actually on disk), not off
    # RUNS' own ordering, so a still-undownloaded entry at a group's start
    # (e.g. task_id 0, "mga"'s first RUNS entry, as of this writing) can't
    # silently swallow that group's divider -- see the group field's own
    # docstring on RUNS above.
    groups = [group for _, _, group, _ in usage]
    boundary_indices = [i for i in range(1, len(groups)) if groups[i] != groups[i - 1]]
    positions = range(len(usage))
    # Per-bar run-identity color: PLAIN_RUN_COLOR for every plain-solve entry
    # (ts_color_key is None), TS_COLOR[key] for each of the six MGA runs --
    # so a run reads as the same color here as in fig3a/3b/4/6, and the
    # legend built below it (run_legend_handles) spells out what each color
    # means. Independent of hatch_by_profile's resource-profile coloring
    # below: color now encodes run identity, hatch still encodes #SBATCH
    # footprint, so the two dimensions stay separately readable.
    run_colors = [TS_COLOR[key] if key else PLAIN_RUN_COLOR for _, _, _, key in usage]
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

    # Vertical dividers at each boundary_indices position computed above --
    # see RUNS' own docstring on the group field for what the three groups
    # ("plain_1ts", "plain_other_ts", "mga") are.
    def _bar(ax, values):
        bars = ax.bar(positions, values, color=run_colors, edgecolor="black", linewidth=0.5)
        for bar, p in zip(bars, profiles):
            if hatch_by_profile[p]:
                bar.set_hatch(hatch_by_profile[p])
        for boundary_idx in boundary_indices:
            ax.axvline(boundary_idx - 0.5, color="black", linestyle="--", linewidth=1, alpha=0.6)
        return bars

    _bar(ax_time, minutes)
    ax_time.set_xlabel("Representative timesteps / year")
    ax_time.set_ylabel("Wall-clock time [min]")
    ax_time.set_title("Solve time")
    # Two stacked legends (leftmost panel only): the hatch-pattern one
    # (unchanged, resource-profile cpus/mem) and, below it, a new one for
    # what the bar COLOR now means -- since color has switched from one
    # fixed hue per panel to one hue per run (run_colors above), a reader
    # needs this to tell a "single model run" bar from one of the three
    # named MGA reruns at a glance, in every panel, not just this one.
    # Swatches are neutral light grey rather than ax_time's own blue for the
    # hatch legend, since the same profile/hatch applies across all four
    # panels' different run colors, not just this one.
    hatch_legend = ax_time.legend(
        handles=[
            Patch(facecolor="#d9d9d9", edgecolor="black", linewidth=0.5,
                  hatch=hatch_by_profile[p], label=p)
            for p in sorted(hatch_by_profile, key=lambda p: p != default_profile)
        ],
        fontsize=8,
        loc="upper left",
        title="#SBATCH resource profile",
        title_fontsize=8,
    )
    ax_time.add_artist(hatch_legend)  # kept on the axes once the 2nd .legend() call below replaces it as "the" legend

    # Run-identity legend, one swatch per color actually used above: PLAIN_
    # RUN_COLOR for "single model run" (only shown if at least one plain-
    # solve entry was loaded) and TS_COLOR[key] for each MGA rerun key
    # present (in RUNS order, so it lines up with fig3a/3b/4/6's own legend
    # order for the same three reruns).
    seen_keys = list(dict.fromkeys(key for _, _, _, key in usage if key))
    run_legend_entries = ([("single model run (plain solve)", PLAIN_RUN_COLOR)]
                           if any(key is None for _, _, _, key in usage) else [])
    run_legend_entries += [(key, TS_COLOR[key]) for key in seen_keys]
    # Positioned just below hatch_legend: drawn once so its actual rendered
    # height (font/title/entry count all affect this) is known, rather than
    # guessing a fixed offset that would need updating by hand every time
    # either legend's entry count changes -- same "measure, then place"
    # approach fig6_polytope_size_vs_resolution's axis-break marks use.
    fig.canvas.draw()
    hatch_bbox = hatch_legend.get_window_extent().transformed(ax_time.transAxes.inverted())
    ax_time.legend(
        handles=[Patch(facecolor=color, edgecolor="black", linewidth=0.5, label=label)
                 for label, color in run_legend_entries],
        fontsize=8,
        loc="upper left",
        bbox_to_anchor=(0.0, hatch_bbox.y0 - 0.03),
        bbox_transform=ax_time.transAxes,
        title="run",
        title_fontsize=8,
    )

    _bar(ax_mem, gb)
    ax_mem.set_xlabel("Representative timesteps / year")
    ax_mem.set_ylabel("Peak memory [GB]")
    ax_mem.set_title("Peak memory use (MaxRSS)")

    _bar(ax_memeff, mem_efficiency)
    ax_memeff.set_xlabel("Representative timesteps / year")
    ax_memeff.set_ylabel("Memory efficiency [%]")
    ax_memeff.set_title("Memory efficiency (MaxRSS / ReqMem)")
    ax_memeff.set_ylim(0, 100)

    _bar(ax_cpueff, cpu_efficiency)
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
                  "plain 2020_16a_2a solves vs. MGA batch_bbo runs")
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
