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

fig6_polytope_size_vs_resolution answers a different question from fig3a/3b:
not how FAST each ts-resolution's MGA run converges, but how BIG the
near-optimal space it converges to actually is -- does a coarser timestep
resolution make the near-optimal region larger or smaller? pyoNearOpt has no
single polytope-volume function, so this uses two of its metrics on each
run's own outer approximation (the same A/b halfspaces, in the same
share-normalised coordinates, that plot_mga_results.py already builds its
own `approximation` objects from for fig1/fig2 -- see that module's
docstring on the "share" normalisation convention, which already makes the
13 axes comparable across runs without further rescaling):
`effective_variable_ranges()` (13 fast per-axis LPs, min/max projection of
the outer polytope onto each coordinate) and `calc_diameter_outer(norm=
"l2")` (the single max-pairwise-distance scalar over the whole polytope, a
non-convex QCQP). The latter needs a real global solver -- scipy.shgo over
26 dimensions is what pyoNearOpt itself falls back to and warns against --
so this passes a licensed local Gurobi solver (verified available) with
NonConvex=2 explicitly set, since Gurobi's own default handling of a
non-convex quadratic maximisation objective isn't guaranteed across
versions. In practice Gurobi finds a solution within a fraction of a
percent of optimal in seconds but then spends many more minutes closing the
remaining branch-and-bound gap to certify true optimality (verified: each of
the three TS_RUNS entries was still short of a 1% gap after 5 minutes) --
since this diameter is a comparison metric, not a certified bound, TimeLimit
and MIPGap are both set (see DIAMETER_SOLVER_OPTIONS below) so each run
reports Gurobi's best incumbent after a bounded wait rather than blocking
indefinitely; a per-run note prints if the limit was hit before MIPGap was
reached, so a reader can see how tight (or not) that incumbent actually is.
fig6 itself only plots effective_variable_ranges and diameter_l2 (per-axis
ranges panel + diameter panel); _polytope_size_metrics also computes
log10_bbox_volume (log-space sum of each axis's effective range, i.e. log of
the bounding-box volume this bounding box proxy implies -- sidesteps the
float underflow a direct 13-axis product would risk, since each
share-normalised range is well under 1) and prints it to console, but it's a
much weaker/noisier signal than the two plotted metrics (it conflates 13
independent per-axis LPs into one number, ignoring inter-axis correlation)
so it's left out of the figure itself.

Usage:
    python scripts/plot_mga_ts_resolution.py
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import matplotlib.pyplot as plt

from plots.figure_settings import SCENARIO_PALETTE, apply_font_mode

apply_font_mode()

import numpy as np
import pandas as pd
import pyomo.environ as pyo

from pyoNearOpt.polytope_approximation.approximation_class import approximation

from plot_mga_results import (
    FIGURES_DIR,
    MGA_ROOT,
    MODEL,
    load_batch_points,
    load_native_ci_history,
    savefig,
    try_load_run_polytope,
)

# calc_diameter_outer's non-convex QCQP (see module docstring): Gurobi finds
# an incumbent within ~1% of optimal in well under a minute but then spends
# many more minutes closing the branch-and-bound gap the rest of the way to
# a certified optimum -- MIPGap lets it stop as soon as it's within 2% (this
# is a comparison metric across ts-resolutions, not a certified bound;
# verified against the 3ts run, whose gap was already 1.6% at 10s and 0.9%
# at 60s). TimeLimit is a hard safety net in case MIPGap is never reached
# quickly for some run; approximation.calc_diameter_outer raises ValueError
# if that triggers before MIPGap does (its own optimal-termination check),
# which _polytope_size_metrics catches and reports as a per-run skip rather
# than blocking the whole script.
DIAMETER_SOLVER_OPTIONS = {"NonConvex": 2, "MIPGap": 0.02, "TimeLimit": 180}

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


def load_polytope_approx(ts: str, suffix: str) -> approximation | None:
    """This TS_RUNS entry's outer/inner polytope wrapped as a pyoNearOpt
    `approximation`, built the same way plot_mga_results.py's own fig1/fig2
    do (A/X/b/name_list straight off polytope.npz, share-normalised, see
    module docstring), or None (logged) if its polytope.npz isn't on disk
    yet -- same skip convention as load_ts_history. Carries a licensed local
    Gurobi solver with NonConvex=2 set, needed by _polytope_size_metrics'
    calc_diameter_outer call (see module docstring)."""
    run_dir = MGA_ROOT / f"{MODEL}_{suffix}"
    run_poly = try_load_run_polytope(run_dir, ts, folder_mode="batch")
    if run_poly is None:
        print(f"  {ts}: no usable polytope.npz under {run_dir.relative_to(REPO_ROOT)} (skipping fig6)")
        return None
    return approximation(
        A=run_poly.A, X=run_poly.X, b=run_poly.b, name_list=run_poly.names,
        print_lv=0, solver=pyo.SolverFactory("gurobi", options=DIAMETER_SOLVER_OPTIONS),
    )


def _polytope_size_metrics(approx: approximation, ts: str) -> dict:
    """Two of pyoNearOpt's metrics on approx's outer polytope, standing in
    for a volume it has no direct function for (see module docstring):
    per-axis effective_variable_ranges (a DataFrame, one row per axis, with
    an added "range" = max - min column), log10_bbox_volume (sum of
    log10(range) across axes -- the log of the bounding-box volume those
    ranges imply, avoiding the underflow a direct 13-axis product of
    sub-1 shares would risk), and diameter_l2 (calc_diameter_outer's single
    max-pairwise-distance scalar, NaN if DIAMETER_SOLVER_OPTIONS'
    TimeLimit was hit before MIPGap -- see that constant's docstring)."""
    ranges = pd.DataFrame(approx.effective_variable_ranges())
    ranges["range"] = ranges["max"] - ranges["min"]
    log10_bbox_volume = float(np.log10(ranges["range"]).sum())
    try:
        diameter_l2 = float(approx.calc_diameter_outer(norm="l2"))
        diameter_note = f"diameter_l2={diameter_l2:.4g}"
    except ValueError as exc:
        diameter_l2 = float("nan")
        diameter_note = f"diameter_l2 skipped ({exc})"
    print(f"  {ts}: log10_bbox_volume={log10_bbox_volume:.3f}, {diameter_note}")
    return {"ranges": ranges, "log10_bbox_volume": log10_bbox_volume, "diameter_l2": diameter_l2}


def _find_axis_break(values: np.ndarray) -> tuple[float, float] | None:
    """(lo_max, hi_min) to split `values`' range at its single largest gap
    between consecutive sorted values, or None if no gap is large relative
    to the overall span (a quarter of it or more) -- i.e. a plain,
    un-broken axis already shows `values` clearly and a break would just add
    visual noise. Used by _figure_polytope_size's per-axis range panel,
    where most axes' ranges cluster well below 1 but net_present_cost's own
    range sits near 1 (see module docstring's "share" normalisation note),
    so a single linear x-axis wastes most of its width on that one gap."""
    v = np.sort(np.unique(values))
    if len(v) < 2:
        return None
    span = v[-1] - v[0]
    if span <= 0:
        return None
    gaps = np.diff(v)
    i = int(np.argmax(gaps))
    if gaps[i] < 0.25 * span:
        return None
    return float(v[i]), float(v[i + 1])


def _figure_polytope_size(sizes: dict) -> None:
    """fig6_polytope_size_vs_resolution -- see module docstring. Panel 1
    shows every axis's own effective range (one row per axis, one marker per
    ts) so a resolution effect that only shows up on some axes isn't hidden
    by panel 2's single aggregate diameter scalar; its x-axis is broken (see
    _find_axis_break) when net_present_cost's own near-1 range would
    otherwise squeeze every other axis's much smaller range into a sliver
    near 0. log10_bbox_volume is computed and printed per ts (see
    _polytope_size_metrics) but not plotted here -- a much noisier aggregate
    than either of these two."""
    axis_names = None
    for ts, size in sizes.items():
        names = list(size["ranges"]["variable"])
        if axis_names is None:
            axis_names = names
        elif names != axis_names:
            common = [n for n in axis_names if n in names]
            print(f"  fig6: {ts}'s axes differ from the first loaded run -- "
                  f"aligning all runs to the {len(common)} axes they share")
            axis_names = common
    if not axis_names:
        print("  skipping fig6: no shared axes across the loaded ts-resolution runs")
        return

    all_ranges = np.concatenate([
        size["ranges"].set_index("variable")["range"].reindex(axis_names).to_numpy()
        for size in sizes.values()
    ])
    x_min, x_max = float(np.nanmin(all_ranges)), float(np.nanmax(all_ranges))
    pad = 0.05 * (x_max - x_min)
    split = _find_axis_break(all_ranges)

    fig = plt.figure(figsize=(10, 5), constrained_layout=True)
    outer = fig.add_gridspec(1, 2, width_ratios=[2.2, 1])
    if split is None:
        ax_lo = fig.add_subplot(outer[0])
        ax_hi = None
    else:
        ranges_gs = outer[0].subgridspec(1, 2, width_ratios=[3, 1], wspace=0.08)
        ax_lo = fig.add_subplot(ranges_gs[0])
        ax_hi = fig.add_subplot(ranges_gs[1], sharey=ax_lo)
    ax_diameter = fig.add_subplot(outer[1])

    y = np.arange(len(axis_names))
    for ts, size in sizes.items():
        ranges_by_name = size["ranges"].set_index("variable")["range"].reindex(axis_names)
        ax_lo.scatter(ranges_by_name, y, color=TS_COLOR[ts], label=ts, s=24, zorder=3)
        if ax_hi is not None:
            ax_hi.scatter(ranges_by_name, y, color=TS_COLOR[ts], s=24, zorder=3)
    ax_lo.set_yticks(y)
    ax_lo.set_yticklabels(axis_names, fontsize=7)
    ax_lo.invert_yaxis()
    ax_lo.set_title("per-axis spread", fontsize=10)
    ax_lo.grid(alpha=0.3, axis="x")
    ax_lo.legend(fontsize=8, frameon=False)

    if ax_hi is None:
        ax_lo.set_xlim(x_min - pad, x_max + pad)
        ax_lo.set_xlabel("effective range (share-normalised)")
    else:
        lo_max, hi_min = split
        ax_lo.set_xlim(x_min - pad, lo_max + pad)
        ax_hi.set_xlim(hi_min - pad, x_max + pad)
        ax_hi.grid(alpha=0.3, axis="x")
        ax_lo.spines["right"].set_visible(False)
        ax_hi.spines["left"].set_visible(False)
        ax_hi.tick_params(left=False, labelleft=False)
        ax_hi.set_xticks([1.0])
        ax_hi.set_xticklabels(["1.00"])
        ax_lo.set_xlabel("effective range (share-normalised)", x=1.0)
        # Diagonal "-//-" break marks on the two spines that meet at the cut.
        # ax_lo and ax_hi have very different widths (width_ratios=[3, 1]
        # above) but the same height, so a naive equal-fraction d (same
        # dx=dy in each axes' OWN transAxes units) draws marks at different
        # physical angles on each side -- not parallel. Sizing dx/dy in
        # physical inches instead (via each axes' actual on-figure size)
        # keeps both marks the same physical length and 45-degree slope
        # regardless of that width mismatch.
        fig.canvas.draw()  # finalise constrained_layout's axes positions first
        fig_w, fig_h = fig.get_size_inches()
        mark_in = 0.09  # half-length, in inches, of each mark's x/y extent

        def _mark_d(ax) -> tuple[float, float]:
            bbox = ax.get_position()
            return mark_in / (bbox.width * fig_w), mark_in / (bbox.height * fig_h)

        dx_lo, dy_lo = _mark_d(ax_lo)
        dx_hi, dy_hi = _mark_d(ax_hi)
        kwargs = dict(color="k", clip_on=False, lw=1)
        ax_lo.plot((1 - dx_lo, 1 + dx_lo), (-dy_lo, +dy_lo), transform=ax_lo.transAxes, **kwargs)
        ax_lo.plot((1 - dx_lo, 1 + dx_lo), (1 - dy_lo, 1 + dy_lo), transform=ax_lo.transAxes, **kwargs)
        ax_hi.plot((-dx_hi, +dx_hi), (-dy_hi, +dy_hi), transform=ax_hi.transAxes, **kwargs)
        ax_hi.plot((-dx_hi, +dx_hi), (1 - dy_hi, 1 + dy_hi), transform=ax_hi.transAxes, **kwargs)

    # diameter_l2 can be NaN (see _polytope_size_metrics) if its Gurobi solve
    # hit DIAMETER_SOLVER_OPTIONS' TimeLimit before MIPGap -- drop those ts
    # from this bar chart rather than plotting a NaN-height bar.
    ts_order = [ts for ts in sizes if ts in TS_COLOR]
    plotted = [ts for ts in ts_order if not np.isnan(sizes[ts]["diameter_l2"])]
    plotted_vals = [sizes[ts]["diameter_l2"] for ts in plotted]
    bars = ax_diameter.bar(plotted, plotted_vals, color=[TS_COLOR[ts] for ts in plotted])
    ax_diameter.bar_label(bars, fmt="%.4g", padding=3, fontsize=8)
    if plotted_vals:
        ax_diameter.set_ylim(0, max(plotted_vals) * 1.12)
    ax_diameter.set_ylabel("L2 diameter")
    ax_diameter.set_title("outer-polytope diameter", fontsize=10)
    ax_diameter.grid(alpha=0.3, axis="y")

    savefig(fig, "fig6_polytope_size_vs_resolution")


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

    print("Computing near-optimal-space size (fig6)...")
    sizes = {}
    for ts, suffix in TS_RUNS.items():
        approx = load_polytope_approx(ts, suffix)
        if approx is not None:
            sizes[ts] = _polytope_size_metrics(approx, ts)
    if sizes:
        _figure_polytope_size(sizes)
    else:
        print("  skipping fig6: no ts-resolution run has a usable polytope.npz")

    stale = FIGURES_DIR / "fig4_exploration_coverage_vs_queries.svg"
    if stale.exists():
        stale.unlink()
        print(f"  removed stale {stale.relative_to(REPO_ROOT)} (superseded by fig3a, see module docstring)")


if __name__ == "__main__":
    main()
