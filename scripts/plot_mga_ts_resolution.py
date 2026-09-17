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

fig4_implied_threshold_for_tolerance answers the question this project
actually wants an answer to: would tightening/relaxing tolerance_explore
(currently 0.02 for every TS_RUNS entry) meaningfully change how long a run
takes? implied_threshold_for_tolerance (see pyoNearOpt.metrics /
mga.rst's track_implied_threshold) is, at each iteration, the *smallest*
tolerance_explore that would already satisfy tolerance_prob given the
directions sampled so far for that iteration's convergence check -- so
plotting it against number of evaluations/wall_time_seconds alongside ci_lower directly
shows how far the run's own convergence check is from the configured
tolerance_explore at every point, without re-running anything. Only logged
when a run's config had track_implied_threshold: true; as of this project's
current TS_RUNS downloads, only 1ts has it (3ts/10ts predate that config
flag) -- the other two are skipped for fig4 with a printed reason, same
convention as fig3b's has_solving_times skip. fig4 also uses
diagnostics.csv's own native "wall_time_seconds" column for its time axis
rather than fig3b's reconstructed "seconds" (see
plot_mga_results.load_native_ci_history's docstring) -- it's simpler, real
elapsed time timed directly around each iteration's worker round, and
(unlike "seconds") doesn't depend on per-point benchmarking.json having
synced down, so it's available for all three TS_RUNS regardless of fig3b's
per-run skips.

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

# interval_<N>ts run-folder suffix, same CAPEX-CUM/share/tol002/bbo
# configuration otherwise (see module docstring) -- despite the name, this
# now also holds non-ts comparison runs against the 1ts/7a/5a baseline
# (task_id 0 in parameters_mga.csv): a fixed-seed_rng rerun and two bigger-
# batch_size reruns, added 2026-09-17 (see submit_euler_mga.sh's task_id
# 4-6 header comment) so they land on fig3a/3b once downloaded. All three
# are still #-commented out here: main()'s load_ts_history already skips
# (with a printed reason) any entry whose run_dir isn't on disk yet, so
# each just needs uncommenting once its own _batch_summary/ syncs down from
# Euler -- no other code change needed, same convention "1ts" itself was
# added under before its run finished.
TS_RUNS: dict[str, str] = {
    "1ts": "2020_7a_5a_interval_1ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002",
    "3ts": "2020_7a_5a_interval_3ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002",
    "10ts": "2020_7a_5a_interval_10ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002",
    # task_id 4: same batch4/share/tol002 config as "1ts" above, but with
    # seed_rng=42 pinned (task_id 0/"1ts" itself has no seed_rng set, so
    # this is an explicit-seed run to compare against its unpinned draw).
    # "1ts_seed42": "2020_7a_5a_interval_1ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002_seed42",
    # task_id 5: batch_size=n_workers=16 (vs. 4), solver_threads=2.
    # "batch16": "2020_7a_5a_interval_1ts_MGA_CAPEX_CUM_batch_bbo_share_batch16_tol002",
    # task_id 6: batch_size=n_workers=32 (vs. 4), solver_threads=2.
    # "batch32": "2020_7a_5a_interval_1ts_MGA_CAPEX_CUM_batch_bbo_share_batch32_tol002",
}
TS_COLOR: dict[str, str] = {
    "3ts": SCENARIO_PALETTE[2],
    "10ts": SCENARIO_PALETTE[0],
    "1ts": SCENARIO_PALETTE[3],
    "1ts_seed42": SCENARIO_PALETTE[5],
    "batch16": SCENARIO_PALETTE[4],
    "batch32": SCENARIO_PALETTE[1],
}


def load_ts_history(ts: str, suffix: str):
    """(history, label, convergence_threshold, has_solving_times,
    has_implied_threshold, tolerance_explore) for one TS_RUNS entry, or None
    if its run_dir/polytope.npz isn't on disk yet. history is
    load_native_ci_history's own [n_queries, seconds, ci_lower, ci_upper,
    iteration, wall_time_seconds, implied_threshold_for_tolerance] frame --
    "seconds" already carries the batch-aware wall-clock accounting (see
    module docstring). has_solving_times is False when NONE of this run's
    per-point folders (and therefore their benchmarking.json) were synced
    down from Euler -- only its _batch_summary/ (polytope + diagnostics.csv)
    made it to disk, so every point's own solving_time is NaN and
    load_native_ci_history's "seconds" column is degenerate (stuck at 0.0
    throughout, since _cum_seconds_wallclock's np.nan_to_num floors every
    NaN to 0) -- plotting that against ci_lower would draw a vertical line
    at x=0, not a real time axis, so main() excludes any such mode from
    fig3b (still included in fig3a, which only needs n_queries).
    has_implied_threshold is False when this run's config had
    track_implied_threshold left off (implied_threshold_for_tolerance is
    all-NaN) -- main() excludes any such mode from fig4 (see module
    docstring)."""
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
    has_implied_threshold = history["implied_threshold_for_tolerance"].notna().any()
    if not has_implied_threshold:
        print(f"  {ts}: no implied_threshold_for_tolerance logged under {run_dir.relative_to(REPO_ROOT)} "
              f"(track_implied_threshold was off for this run's config) -- excluding from fig4")
    tolerance_explore = float(run_poly.run.get("tolerance_explore", float("nan")))
    iterations_done = run_poly.run.get("iterations_done", "?")
    iterations_bold = f"$\\mathbf{{{iterations_done}}}$" if isinstance(iterations_done, int) else iterations_done
    label = (
        f"{run_poly.run.get('strategy_mode', '?')}, batch_size={batch_size}, "
        f"tol_explore={run_poly.run.get('tolerance_explore', float('nan')):g}, {ts}, "
        f"iter={batch_size}x{iterations_bold}="
        f"{batch_size * iterations_done if isinstance(iterations_done, int) else '?'}"
    )
    return (history, label, float(run_poly.convergence_threshold), has_solving_times,
            has_implied_threshold, tolerance_explore)


def _figure(histories: dict, x_column: str, x_label: str, name: str, log_x: bool) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 5), constrained_layout=True)
    thresholds = set()
    for ts, (history, label, threshold, *_rest) in histories.items():
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


def _figure_implied_threshold(histories: dict) -> None:
    """fig4_implied_threshold_for_tolerance -- see module docstring for what
    implied_threshold_for_tolerance means. Kept deliberately plain (short
    titles/labels, one small line-style legend): the full explanation lives
    in the module docstring and the chat message that introduced this
    figure, not on the canvas. Only includes TS_RUNS entries with
    has_implied_threshold True (see load_ts_history)."""
    implied = {ts: r for ts, r in histories.items() if r[4]}
    if not implied:
        print("  skipping fig4: no ts-resolution run has implied_threshold_for_tolerance logged")
        return

    CI_LOWER_COLOR = SCENARIO_PALETTE[2]  # ETH green

    fig, (ax_iter, ax_time) = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    for ax, x_column, x_label, title in (
        (ax_iter, "n_queries", "number of evaluations", "vs. number of evaluations"),
        (ax_time, "wall_time_seconds", "wall time [s]", "vs. wall time"),
    ):
        ax_r = ax.twinx()
        for ts, (history, _label, threshold, _hst, _hit, tolerance_explore) in implied.items():
            ax.plot(history[x_column], history["ci_lower"], color=CI_LOWER_COLOR, lw=1.5)
            ax.axhline(threshold, color=CI_LOWER_COLOR, ls="--", lw=1)
            ax_r.plot(history[x_column], history["implied_threshold_for_tolerance"],
                      color=TS_COLOR[ts], lw=1.5, ls="--")
            ax_r.axhline(tolerance_explore, color=TS_COLOR[ts], ls=":", lw=1)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel(x_label)
        ax.set_ylabel("ci_lower")
        ax_r.set_ylabel("implied tolerance")
        ax.set_ylim(-0.03, 1.03)
        ax_r.set_ylim(bottom=0)
        ax.grid(alpha=0.3)
    ax_time.set_xscale("log")

    legend_lines = [
        plt.Line2D([0], [0], color=CI_LOWER_COLOR, lw=1.5, label="ci_lower"),
        plt.Line2D([0], [0], color=CI_LOWER_COLOR, lw=1, ls="--", label="95% target"),
        plt.Line2D([0], [0], color="grey", lw=1.5, ls="--", label="implied tolerance"),
        plt.Line2D([0], [0], color="grey", lw=1, ls=":", label="actual tolerance_explore"),
    ]
    if len(implied) > 1:
        legend_lines += [plt.Line2D([0], [0], color=TS_COLOR[ts], lw=1.5, label=ts) for ts in implied]
    # Placed just right of ax_iter (clear of its twin y-axis ticks/label),
    # vertically centered on that panel -- in the gap between the two
    # panels, where it's readable without covering either one. savefig's
    # bbox_inches="tight" (see plot_mga_results.savefig) keeps it from
    # being clipped even though it sits outside ax_iter's own box.
    ax_iter.legend(handles=legend_lines, fontsize=7.5, frameon=False,
                    loc="center left", bbox_to_anchor=(1.22, 0.5), bbox_transform=ax_iter.transAxes)
    savefig(fig, "fig4_implied_threshold_for_tolerance")


def main() -> None:
    print("Loading ts-resolution runs...")
    histories = {}
    for ts, suffix in TS_RUNS.items():
        result = load_ts_history(ts, suffix)
        if result is not None:
            histories[ts] = result
            history = result[0]
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

    _figure_implied_threshold(histories)

    stale = FIGURES_DIR / "fig4_exploration_coverage_vs_queries.svg"
    if stale.exists():
        stale.unlink()
        print(f"  removed stale {stale.relative_to(REPO_ROOT)} (superseded by fig3a, see module docstring)")


if __name__ == "__main__":
    main()
