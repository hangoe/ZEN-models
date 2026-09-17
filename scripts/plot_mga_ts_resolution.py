"""Compares MGA exploration convergence speed across ZEN-garden's temporal
resolution (representative timesteps/year) for the same run configuration
otherwise (CAPEX-CUM/share axes, batch_size=4, tolerance_explore=0.02, bbo --
see plot_mga_results.py's module docstring for what each of those means).
TS_RUNS below holds the interval_<N>ts run-folder suffixes; a mode whose
run_dir isn't downloaded yet is skipped with a printed reason, same
convention as plot_mga_results.main()'s own BATCH_MODES loop -- add "1ts"
there once its run finishes and syncs down, no other code change needed.

fig3a_convergence_vs_queries plots each run's own ci_lower (fraction_well_
explored's 95% CI lower bound, read straight off diagnostics.csv -- see
plot_mga_results.load_native_ci_history) against number of model queries.
This reproduces fig4_exploration_coverage_vs_queries.svg, an output left on
disk with no generating script still in the repo (git blame shows the .py
that made it was never committed) -- this script replaced it, first as
fig4a, then renamed to fig3a once this project retired
plot_mga_results.py's own max_separation/ci_lower fig3a/3b pair and reused
those figure numbers for these two figures instead.

fig3b_convergence_vs_time is the new companion this project actually wanted:
naively summing every iterate's own solving_time would overcount real
elapsed time by roughly batch_size, since batch4 solves 4 directions
concurrently (one worker pool, all 4 futures gathered together) and the
whole group only lands in the polytope once its slowest worker finishes --
see plot_mga_results._cum_seconds_wallclock's docstring for the full
reasoning (verified against Euler's own SLURM accounting). Rather than
reimplement that accounting, this script reuses load_native_ci_history's
"seconds" column directly, so fig3b gets the exact same batch-aware
(max-per-group, not sum) treatment as any other run plotted through that
function. Neither 3ts nor 10ts has a verified real-elapsed-time entry in
plot_mga_results.
REAL_ELAPSED_SECONDS yet, so fig3b's time axis is uncalibrated (a warning
prints for each run) and understates real wall-clock time by roughly the
same 2-3x every other uncalibrated mode in this project's figures does --
see _calibrate_cum_seconds's docstring for how to add a verified sacct total
once available. Until then, treat fig3b's absolute seconds as approximate;
the RELATIVE comparison between 3ts and 10ts should still be informative
since both runs share the same undercounting mechanism (same solver, same
batch_size, same machine).

Usage:
    python scripts/plot_mga_ts_resolution.py
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import matplotlib.pyplot as plt

from plots.figure_settings import SCENARIO_PALETTE, apply_font_mode

apply_font_mode()

import numpy as np

from plot_mga_results import (
    FIGURES_DIR,
    MGA_ROOT,
    MODEL,
    load_batch_points,
    load_native_ci_history,
    savefig,
    try_load_run_polytope,
)

# interval_<N>ts run-folder suffix, same CAPEX-CUM/share/batch4/tol002/bbo
# configuration otherwise (see module docstring).
TS_RUNS: dict[str, str] = {
    "1ts": "2020_7a_5a_interval_1ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002",
    "3ts": "2020_7a_5a_interval_3ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002",
    "10ts": "2020_7a_5a_interval_10ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002",
}
TS_COLOR: dict[str, str] = {
    "3ts": SCENARIO_PALETTE[2],
    "10ts": SCENARIO_PALETTE[0],
    "1ts": SCENARIO_PALETTE[3],
}


def load_ts_history(ts: str, suffix: str):
    """(history, label, convergence_threshold, has_solving_times) for one
    TS_RUNS entry, or None if its run_dir/polytope.npz isn't on disk yet.
    history is load_native_ci_history's own [n_queries, seconds, ci_lower,
    ci_upper] frame -- "seconds" already carries the batch-aware wall-clock
    accounting (see module docstring). has_solving_times is False when NONE
    of this run's per-point folders (and therefore their benchmarking.json)
    were synced down from Euler -- only its _batch_summary/ (polytope +
    diagnostics.csv) made it to disk, so every point's own solving_time is
    NaN and load_native_ci_history's "seconds" column is degenerate (stuck
    at 0.0 throughout, since _cum_seconds_wallclock's np.nan_to_num floors
    every NaN to 0) -- plotting that against ci_lower would draw a
    vertical line at x=0, not a real time axis, so main() excludes any such
    mode from fig3b (still included in fig3a, which only needs n_queries)."""
    run_dir = MGA_ROOT / f"{MODEL}_{suffix}"
    run_poly = try_load_run_polytope(run_dir, ts, folder_mode="batch")
    if run_poly is None:
        print(f"  {ts}: no usable polytope.npz under {run_dir.relative_to(REPO_ROOT)} (skipping)")
        return None
    batch_size = int(run_poly.run.get("batch_size", 4))
    points = load_batch_points(run_poly, run_dir, batch_size)
    has_solving_times = not all(np.isnan(t) for _, _, t in points)
    if not has_solving_times:
        print(f"  {ts}: no per-point benchmarking.json found under {run_dir.relative_to(REPO_ROOT)} "
              f"(only _batch_summary/ was synced down, not the {len(points)} individual solve folders) "
              f"-- excluding from fig3b, the time axis would be degenerate")
    history = load_native_ci_history(run_dir, ts, "batch", points, batch_size=batch_size)
    iterations_done = run_poly.run.get("iterations_done", "?")
    iterations_bold = f"$\\mathbf{{{iterations_done}}}$" if isinstance(iterations_done, int) else iterations_done
    label = (
        f"{run_poly.run.get('strategy_mode', '?')}, batch_size={batch_size}, "
        f"tol_explore={run_poly.run.get('tolerance_explore', float('nan')):g}, {ts}, "
        f"iter={batch_size}x{iterations_bold}="
        f"{batch_size * iterations_done if isinstance(iterations_done, int) else '?'}"
    )
    return history, label, float(run_poly.convergence_threshold), has_solving_times


def _figure(histories: dict, x_column: str, x_label: str, name: str, log_x: bool) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 5), constrained_layout=True)
    thresholds = set()
    for ts, (history, label, threshold, _) in histories.items():
        group = history[history[x_column] > 0] if log_x else history
        ax.plot(group[x_column], group["ci_lower"], marker="o", markersize=2,
                color=TS_COLOR[ts], label=label)
        thresholds.add(threshold)
    for threshold in thresholds:
        ax.axhline(threshold, color="grey", ls="--", lw=1)
    ax.set_title(f"directions with gap $\\leq$ 0.02, 95% CI lower bound", fontsize=11)
    ax.set_ylabel("fraction of well-explored directions")
    ax.set_xlabel(x_label)
    ax.set_ylim(-0.03, 1.03)
    if log_x:
        ax.set_xscale("log")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, frameon=False)
    savefig(fig, name)


def main() -> None:
    print("Loading ts-resolution runs...")
    histories = {}
    for ts, suffix in TS_RUNS.items():
        result = load_ts_history(ts, suffix)
        if result is not None:
            histories[ts] = result
            history, _, _, _ = result
            print(f"  {ts}: {len(history)} logged iterations")
    if not histories:
        print("  skipping fig3: no ts-resolution runs loaded")
        return

    _figure(histories, "n_queries", "number of model queries",
            "fig3a_convergence_vs_queries", log_x=False)

    time_histories = {ts: r for ts, r in histories.items() if r[3]}
    if len(time_histories) < len(histories):
        print(f"  fig3b: plotting {list(time_histories)} only (see per-run skip reasons above)")
    if time_histories:
        _figure(time_histories, "seconds", "cumulative ZEN-garden solving time [s]",
                "fig3b_convergence_vs_time", log_x=True)
    else:
        print("  skipping fig3b: no ts-resolution run has per-point solving times on disk")

    stale = FIGURES_DIR / "fig4_exploration_coverage_vs_queries.svg"
    if stale.exists():
        stale.unlink()
        print(f"  removed stale {stale.relative_to(REPO_ROOT)} (superseded by fig3a, see module docstring)")


if __name__ == "__main__":
    main()
