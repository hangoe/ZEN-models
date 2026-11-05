"""Convergence of the MGA runs in TS_RUNS, read from each run's diagnostics.csv
(no sampling or solving here):

  fig3a_convergence_vs_queries  ci_lower vs. number of model queries
  fig3b_convergence_vs_time     ci_lower vs. cumulative solve-round time
  fig4_implied_threshold_...    ci_lower and the implied tolerance vs. queries, stacked

ci_lower is the 95% CI lower bound of fraction_well_explored. The implied
tolerance is the smallest tolerance_explore that would already satisfy
tolerance_prob at that iteration (track_implied_threshold in the run config).

The time axis is diagnostics.csv's wall_time_seconds, so it needs no per-solve
folders. It only covers the parallel solve rounds, not the gap sampling and BBO
between them, so the job's real elapsed time is longer.

The final convergence check has no row in diagnostics.csv (see
plot_mga_results.load_native_ci_history), so a converged run's line can end
below the target. The figures say so when that happens.

Earlier versions compared temporal resolutions and drew near-optimal-space size
(fig6); see git history. TS_COLOR keeps those runs' colours because
plot_ts_resolution_benchmark.py still imports them.

Usage:
    python scripts/plot_mga_ts_resolution.py
"""

import matplotlib.pyplot as plt

from plots.figure_settings import SCENARIO_PALETTE, apply_font_mode, eth_tint

apply_font_mode()

from plot_mga_results import load_native_ci_history, savefig, try_load_run_polytope
from plots.mga_capex_periods_common import MGA_ROOT, MODEL, NEAR_BLACK, REPO_ROOT, RUN_LABEL, RUN_SUFFIX

# Label -> run-folder suffix. Add runs 22/23 here once downloaded.
TS_RUNS: dict[str, str] = {
    RUN_LABEL: RUN_SUFFIX,
}
TS_COLOR: dict[str, str] = {
    RUN_LABEL: NEAR_BLACK,
    # Old temporal-resolution runs, used only by plot_ts_resolution_benchmark.py.
    "1ts": SCENARIO_PALETTE[3],
    "1ts_seed42": SCENARIO_PALETTE[5],
    "1ts_batch16": SCENARIO_PALETTE[4],
    "3ts": SCENARIO_PALETTE[2],
    "10ts": SCENARIO_PALETTE[0],
    "1ts_4a_10a": eth_tint(SCENARIO_PALETTE[3], 0.5),
    "1ts_batch32": SCENARIO_PALETTE[1],
}
GREY = SCENARIO_PALETTE[6]


def load_run(label: str, suffix: str) -> dict | None:
    run_dir = MGA_ROOT / f"{MODEL}_{suffix}"
    poly = try_load_run_polytope(run_dir, label, folder_mode="batch")
    if poly is None:
        print(f"  {label}: no usable polytope.npz under {run_dir.relative_to(REPO_ROOT)} (skipping)")
        return None
    history = load_native_ci_history(run_dir, poly, "batch")
    history["wall_time_hours"] = history["wall_time_seconds"] / 3600
    print(f"  {label}: {len(history)} logged iterations, converged={poly.converged}, "
          f"last logged ci_lower={history['ci_lower'].iloc[-1]:.3f}")
    return {
        "history": history,
        "target": float(poly.convergence_threshold),
        "tolerance": float(poly.run["tolerance_explore"]),
        "converged": bool(poly.converged),
    }


def _unlogged_check_note(runs: dict) -> str | None:
    """Caption text if a converged run's logged line ends below its target."""
    hidden = [label for label, r in runs.items()
              if r["converged"] and r["history"]["ci_lower"].iloc[-1] < r["target"]]
    if not hidden:
        return None
    return "Run converged: the final check passed the target but is not logged in diagnostics.csv."


def _plot_ci(ax, runs: dict, x_column: str) -> None:
    for label, run in runs.items():
        history = run["history"]
        ax.plot(history[x_column], history["ci_lower"], color=TS_COLOR[label], linewidth=1.5, label=label)
    target = next(iter(runs.values()))["target"]
    ax.axhline(target, color=GREY, ls="--", lw=1)
    ax.annotate(f"target {target:g}", (0, target), xycoords=("axes fraction", "data"),
                xytext=(4, 4), textcoords="offset points", fontsize=8, color=GREY)
    ax.set_ylim(-0.03, 1.03)
    ax.set_ylabel("ci_lower (well-explored directions)")
    ax.grid(alpha=0.3)


def fig_convergence(runs: dict, x_column: str, x_label: str, name: str) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 4.8), constrained_layout=True)
    _plot_ci(ax, runs, x_column)
    tolerance = next(iter(runs.values()))["tolerance"]
    ax.set_title(f"Directions with gap $\\leq$ {tolerance:g}, 95% CI lower bound", fontsize=11)
    ax.set_xlabel(x_label)
    if len(runs) > 1:
        ax.legend(fontsize=8, frameon=False)
    note = _unlogged_check_note(runs)
    if note:
        ax.text(0.98, 0.04, note, transform=ax.transAxes, ha="right", fontsize=7.5, color=GREY)
    savefig(fig, name)


def fig_implied_threshold(runs: dict) -> None:
    implied = {label: r for label, r in runs.items()
               if r["history"]["implied_threshold_for_tolerance"].notna().any()}
    if not implied:
        print("  skipping fig4: no run has implied_threshold_for_tolerance logged")
        return
    fig, (ax_ci, ax_tol) = plt.subplots(2, 1, figsize=(7.5, 6), sharex=True, constrained_layout=True)
    _plot_ci(ax_ci, implied, "n_queries")
    for label, run in implied.items():
        history = run["history"]
        ax_tol.plot(history["n_queries"], history["implied_threshold_for_tolerance"],
                    color=TS_COLOR[label], linewidth=1.5, label=label)
    tolerance = next(iter(implied.values()))["tolerance"]
    ax_tol.axhline(tolerance, color=GREY, ls=":", lw=1)
    ax_tol.annotate(f"tolerance_explore {tolerance:g}", (1, tolerance), xycoords=("axes fraction", "data"),
                    xytext=(-4, -11), textcoords="offset points", ha="right", fontsize=8, color=GREY)
    ax_tol.set_ylim(bottom=0)
    ax_tol.set_xlabel("number of model queries")
    ax_tol.set_ylabel("implied tolerance")
    ax_tol.grid(alpha=0.3)
    if len(implied) > 1:
        ax_ci.legend(fontsize=8, frameon=False)
    savefig(fig, "fig4_implied_threshold_for_tolerance")


def main() -> None:
    print("Loading runs...")
    runs = {label: run for label, suffix in TS_RUNS.items() if (run := load_run(label, suffix)) is not None}
    if not runs:
        print("  skipping fig3/fig4: no run loaded")
        return
    fig_convergence(runs, "n_queries", "number of model queries", "fig3a_convergence_vs_queries")
    fig_convergence(runs, "wall_time_hours", "cumulative solve-round time [h]", "fig3b_convergence_vs_time")
    fig_implied_threshold(runs)


if __name__ == "__main__":
    main()
