"""Benchmarks Euler resource usage (wall-clock time, peak memory) of the
plain (non-MGA) v9_0 no_flexibility_nodiffusion solve across temporal
resolution: 1/3/10/20 representative timesteps/year, 2020_16a_2a horizon
(parameters.csv task_ids 10-13, submit_euler.sh --array=10-13). This is a
different run family from plot_mga_ts_resolution.py's fig3a/fig3b, which
benchmarks MGA *exploration convergence* across timestep resolution for a
CAPEX-CUM/share MGA sweep under euler_outputs_mga -- these are single
deterministic solves under euler_outputs (RUN_ROOT below), one per row of
parameters.csv, no MGA plugin involved.

benchmarking.json's own "solving_time" field undercounts real wall-clock
time (it only covers the solver call itself, not model construction/I/O) --
see plot_mga_results._cum_seconds_wallclock's docstring for the 2.3x-3.7x
gap this project already found for MGA runs. Rather than repeat that
calibration here, this script reads real wall-clock elapsed time and peak
memory (MaxRSS) straight from each run's slurm_usage.json sidecar file
(written from `sacct -j <jobid> --format=JobID,Elapsed,MaxRSS,...` at
download time -- see the mga_tests figure plan for the exact commands).

fig5_resource_usage_vs_resolution plots three panels as a function of
aggregated_time_steps_per_year: wall-clock minutes, peak memory (MaxRSS,
GB), and memory efficiency (MaxRSS / ReqMem, %) -- the last one showing how
badly over-requested the shared 128G/job SBATCH profile is at low
resolution (submit_euler.sh's --array=10-13 header comment) versus how
close to right-sized it gets by 20ts. A run whose folder or
slurm_usage.json isn't downloaded yet is skipped with a printed reason,
same convention as plot_mga_ts_resolution.py's TS_RUNS loop.

Usage:
    python scripts/plot_ts_resolution_benchmark.py
"""

import json

import matplotlib.pyplot as plt

from plots.figure_settings import SCENARIO_PALETTE, apply_font_mode

apply_font_mode()

from plot_mga_results import FIGURES_DIR, REPO_ROOT, savefig

RUN_ROOT = REPO_ROOT / "data" / "outputs" / "euler_outputs"
MODEL = "Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion"

# aggregated_time_steps_per_year -> run-folder suffix, parameters.csv
# task_ids 10-13 (2020_16a_2a_interval_<N>ts).
TS_RUNS: dict[int, str] = {
    1: "2020_16a_2a_interval_1ts",
    3: "2020_16a_2a_interval_3ts",
    10: "2020_16a_2a_interval_10ts",
    20: "2020_16a_2a_interval_20ts",
}


def _parse_mem_kb(mem_str: str) -> float:
    """Parses a SLURM ReqMem string (e.g. "128G") into KiB."""
    units = {"K": 1, "M": 1024, "G": 1024 ** 2, "T": 1024 ** 3}
    return float(mem_str[:-1]) * units[mem_str[-1].upper()]


def load_usage() -> dict[int, dict]:
    usage: dict[int, dict] = {}
    for ts, suffix in TS_RUNS.items():
        run_dir = RUN_ROOT / f"{MODEL}_{suffix}"
        usage_file = run_dir / "slurm_usage.json"
        if not usage_file.exists():
            print(f"  {ts}ts: no slurm_usage.json at {run_dir.relative_to(REPO_ROOT)}, skipping")
            continue
        usage[ts] = json.loads(usage_file.read_text())
    return usage


def fig5_resource_usage_vs_resolution(usage: dict[int, dict]) -> None:
    ts_values = sorted(usage)
    positions = range(len(ts_values))
    minutes = [usage[ts]["elapsed_seconds"] / 60 for ts in ts_values]
    # sacct's MaxRSS is in KiB; divide by 1024**2 for GiB, labelled "GB" below
    # per this project's convention of not distinguishing binary/decimal units
    # in figure labels.
    gb = [usage[ts]["max_rss_kb"] / (1024 ** 2) for ts in ts_values]
    mem_efficiency = [
        100 * usage[ts]["max_rss_kb"] / _parse_mem_kb(usage[ts]["req_mem"])
        for ts in ts_values
    ]

    fig, (ax_time, ax_mem, ax_eff) = plt.subplots(1, 3, figsize=(13.5, 4))

    ax_time.bar(positions, minutes, color=SCENARIO_PALETTE[0])
    ax_time.set_xlabel("Representative timesteps / year")
    ax_time.set_ylabel("Wall-clock time [min]")
    ax_time.set_title("Solve time")

    ax_mem.bar(positions, gb, color=SCENARIO_PALETTE[4])
    ax_mem.set_xlabel("Representative timesteps / year")
    ax_mem.set_ylabel("Peak memory [GB]")
    ax_mem.set_title("Peak memory use (MaxRSS)")

    ax_eff.bar(positions, mem_efficiency, color=SCENARIO_PALETTE[2])
    ax_eff.set_xlabel("Representative timesteps / year")
    ax_eff.set_ylabel("Memory efficiency [%]")
    ax_eff.set_title("Memory efficiency (MaxRSS / ReqMem)")
    ax_eff.set_ylim(0, 100)

    for ax, values, fmt in (
        (ax_time, minutes, "{:,.0f}"),
        (ax_mem, gb, "{:,.1f}"),
        (ax_eff, mem_efficiency, "{:,.1f}%"),
    ):
        ax.set_xticks(list(positions))
        ax.set_xticklabels([str(ts) for ts in ts_values])
        ax.grid(True, axis="y", alpha=0.3)
        for x, v in zip(positions, values):
            ax.text(x, v, fmt.format(v), ha="center", va="bottom", fontsize=8)

    fig.suptitle("Single model run for Crystal Ball ind heat, v9.0, no flexibility, no diffusion, 2020_16a_2a")
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
