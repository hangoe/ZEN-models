"""Pairwise projections of every solved point of the MGA run (see
plots/mga_capex_periods_common.py), one figure per snapshot year (fig1a, fig1b, ...
in YEARS order, e.g. fig1a_pairwise_2034), each pairing that year's axes plus total cost,
and fig1c_pairwise_all_years with those figures side by side.

Also holds the polytope and diagnostics loaders plot_mga_ts_resolution.py
imports. Earlier versions of this script compared several modes and drew a
rejection-sampled interior (fig2); see git history.

Usage:
    python scripts/plot_mga_results.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from plots.figure_settings import SCENARIO_PALETTE, apply_font_mode

# See figure_settings.FONT_MODE: one flag switches every figure script's font.
apply_font_mode()
from zen_garden_plugins.mga.polytope_io import Polytope, load_polytope

from plots.mga_capex_periods_common import (
    FIGURES_DIR,
    METRIC_COLOR,
    METRIC_LABEL,
    MGA_ROOT,
    MODEL,
    NEAR_BLACK,
    POLY_PATH,
    REGIONS,
    REPO_ROOT,
    RUN_LABEL,
    YEARS,
    display_unit,
    parse_axis,
    savefig,
)

__all__ = ["FIGURES_DIR", "MGA_ROOT", "MODEL", "REPO_ROOT", "savefig",
           "load_native_ci_history", "try_load_run_polytope"]

ITERATE_COLOR = "#B0B0B0"
VMM_COLOR = "#555555"
BASELINE_COLOR = SCENARIO_PALETTE[4]  # ETH red


def try_load_run_polytope(run_dir: Path, mode: str, folder_mode: str | None = None) -> Polytope | None:
    """The run's polytope.npz, or None (logged) if missing or unreadable."""
    summary = run_dir / f"{MODEL}_{folder_mode or mode}_summary"
    poly_files = sorted(summary.glob("polytope*.npz")) if summary.exists() else []
    if not poly_files:
        return None
    try:
        return load_polytope(poly_files[0])
    except Exception as exc:
        print(f"  {mode}: polytope present at {summary.relative_to(REPO_ROOT)} but unreadable ({exc!r})")
        return None


def load_native_ci_history(run_dir: Path, poly: Polytope, folder_mode: str) -> pd.DataFrame:
    """[iteration, n_queries, ci_lower, ci_upper, wall_time_seconds,
    implied_threshold_for_tolerance], one row per logged iteration of the
    run's diagnostics.csv. Nothing is re-sampled here.

    wall_time_seconds is cumulative and only covers the parallel solve rounds,
    not the gap sampling and BBO between them, so it understates the job's
    elapsed time. A row reflects the approximation before that iteration's
    batch was added, hence n_queries = initial points + iteration * batch_size.
    The final convergence check has no row of its own: batch mode reads it
    from batch_oracle's history after the last logged iteration
    (zen_garden_plugins/mga/modes/support_function.py).
    """
    diagnostics = pd.read_csv(run_dir / f"{MODEL}_{folder_mode}_summary" / "diagnostics.csv")
    n_initial = sum(1 for origin in poly.point_origin if origin != "iterate")
    batch_size = int(poly.run["batch_size"])
    history = pd.DataFrame({
        "iteration": diagnostics["iteration"],
        "n_queries": n_initial + diagnostics["iteration"] * batch_size,
        "ci_lower": diagnostics["ci_lower"],
        "ci_upper": diagnostics["ci_upper"],
        "wall_time_seconds": diagnostics["wall_time_seconds"].cumsum(),
    })
    history["implied_threshold_for_tolerance"] = diagnostics.get("implied_threshold_for_tolerance", np.nan)
    return history


def _axis_label(name: str, unit: str) -> str:
    info = parse_axis(name)
    _, unit_label = display_unit(unit)
    if info.metric == "cost":
        return f"{METRIC_LABEL['cost']}\n[{unit_label}]"
    region = f"{info.region.capitalize()} " if len(REGIONS) > 1 else ""
    return f"{region}{METRIC_LABEL[info.metric]}\n[{unit_label}]"


def _draw_pairwise(fig_or_subfig, poly: Polytope, year: str):
    """Lower-triangle pairwise scatter of `year`'s axes plus cost into a new grid of
    subplots on `fig_or_subfig`; returns the axes array."""
    origin = np.array(poly.point_origin)
    phys = np.array([poly.to_phys(x) for x in poly.X])
    columns = [i for i, name in enumerate(poly.names)
               if parse_axis(name).year in (year, None)]
    factors = np.array([display_unit(poly.units[i])[0] for i in columns])
    values = phys[:, columns] * factors
    is_iterate = origin == "iterate"
    is_vmm = np.array([o.startswith(("max:", "min:")) for o in origin])
    baseline = values[origin == "z_star"][0]

    n = len(columns)
    axes = fig_or_subfig.subplots(n - 1, n - 1, squeeze=False)
    for row in range(1, n):
        for col in range(n - 1):
            ax = axes[row - 1, col]
            if col >= row:
                ax.axis("off")
                continue
            ax.scatter(values[is_iterate, col], values[is_iterate, row], s=3, color=ITERATE_COLOR,
                       linewidths=0, alpha=0.5, rasterized=True, label="iterations")
            ax.scatter(values[is_vmm, col], values[is_vmm, row], s=9, color=VMM_COLOR,
                       linewidths=0, rasterized=True, label="min/max solves")
            ax.scatter(baseline[col], baseline[row], marker="D", s=26, color=BASELINE_COLOR,
                       edgecolor="white", linewidth=0.5, zorder=5, label="cost-optimal baseline")
            ax.grid(alpha=0.25, linewidth=0.5)
            ax.tick_params(labelsize=7)
            if row == n - 1:
                name = poly.names[columns[col]]
                ax.set_xlabel(_axis_label(name, poly.units[columns[col]]), fontsize=8,
                              color=METRIC_COLOR[parse_axis(name).metric])
            else:
                ax.set_xticklabels([])
            if col == 0:
                name = poly.names[columns[row]]
                ax.set_ylabel(_axis_label(name, poly.units[columns[row]]), fontsize=8,
                              color=METRIC_COLOR[parse_axis(name).metric])
            else:
                ax.set_yticklabels([])
    return axes


def fig1_pairwise_points(poly: Polytope, year: str, fig_name: str) -> None:
    n = sum(1 for name in poly.names if parse_axis(name).year in (year, None))
    fig = plt.figure(figsize=(2.1 * (n - 1), 2.1 * (n - 1)))
    axes = _draw_pairwise(fig, poly, year)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", bbox_to_anchor=(0.97, 0.9), fontsize=11, frameon=False,
               markerscale=2)
    fig.suptitle(f"{RUN_LABEL}: solved near-optimal designs, {year} axes and total cost",
                 fontsize=14, fontweight="bold", color=NEAR_BLACK)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    savefig(fig, fig_name)


def fig1c_pairwise_all_years(poly: Polytope, fig_name: str = "fig1c_pairwise_all_years") -> None:
    """fig1a and fig1b side by side: one pairwise triangle per year, shared legend."""
    n = sum(1 for name in poly.names if parse_axis(name).year in (YEARS[0], None))
    side = 2.1 * (n - 1)
    fig = plt.figure(figsize=(side * len(YEARS) + 0.6, side + 0.9), layout="constrained")
    subfigs = np.atleast_1d(fig.subfigures(1, len(YEARS), wspace=0.04))
    for subfig, year in zip(subfigs, YEARS):
        axes = _draw_pairwise(subfig, poly, year)
        subfig.suptitle(f"{year} axes and total cost", fontsize=12, fontweight="bold", color=NEAR_BLACK)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    # Upper-right corner of the last triangle is empty: legend there.
    subfigs[-1].legend(handles, labels, loc="upper right", bbox_to_anchor=(0.98, 0.9), fontsize=11,
                       frameon=False, markerscale=2)
    fig.suptitle(f"{RUN_LABEL}: solved near-optimal designs", fontsize=14, fontweight="bold", color=NEAR_BLACK)
    savefig(fig, fig_name)


def main() -> None:
    poly = load_polytope(POLY_PATH)
    print(f"Loaded {poly.X.shape[0]} points, {poly.n_axes} axes, "
          f"converged={poly.converged}, epsilon={poly.epsilon:g}")
    for year, suffix in zip(YEARS, "abc"):
        fig1_pairwise_points(poly, year, f"fig1{suffix}_pairwise_{year}")
    fig1c_pairwise_all_years(poly)


if __name__ == "__main__":
    main()
