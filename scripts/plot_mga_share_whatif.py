"""Share "what-if" figures, laid out like fig20/21: the transport (fig30-33) or
heating (fig40-43) share of ONE region is limited, in 2030 in the upper block and
in 2050 in the lower block. Within a block, rows are the affected region (north
above south) and columns the affected metric, so the other region's row shows
whether it compensates.

    fig30 / fig31: north / south transport share at most 10%
    fig32 / fig33: north / south transport share at least 90%
    fig40 - fig43: the same for the heating share

Like fig20/21 this is answered from the polytope of the MGA run, with no
re-solving of ZEN-garden. Each bound is one LP over the 17 axes, solved twice:

- inner (filled ribbon): over the convex hull of the solved designs in poly.X.
  Every point in it is a blend of near-optimal designs, so it is achievable.
- outer (dashed lines): over the cutting planes poly.A x <= poly.b. Everything
  outside it is ruled out.

The true bound lies between the two. Blending is valid for the share axes too:
they divide by a denominator frozen at its baseline value, so they are linear.

The lower and upper edge of a ribbon come from separate LPs, so they generally
belong to different designs and need not be reachable at the same time.

Usage:
    python scripts/plot_mga_share_whatif.py
"""

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.optimize import linprog

from plot_mga_regional_investment_whatif import _draw_ribbon, compute_ranges, load_data
from plots.mga_capex_periods_common import (
    METRIC_COLOR,
    METRIC_COLUMNS,
    METRIC_IS_CUMULATIVE,
    METRIC_LABEL,
    REGION_COLOR,
    REGIONS,
    YEARS,
    axis_name,
    display_unit,
    savefig,
)

SHARE_LABEL = {"transport": "EV share of passenger road", "heating": "Electrified share of industrial heat"}
FIRST_FIGURE = {"transport": 30, "heating": 40}
# (sense, limit as a fraction, marker pressing on the limit from the far side)
LIMITS = [("max", 0.10, "v"), ("min", 0.90, "^")]
RIBBON_ALPHA = 0.6


def share_constraint(poly, axis_idx, region: str, metric: str, year: str, limit: float) -> list:
    """[(axis index, normalised limit)] for this region's share in this year."""
    k = axis_idx[axis_name(region, metric, year)]
    return [(k, (limit - poly.offset[k]) / poly.scale[k])]


def inner_bound(poly, constraints, sense: str, j: int, target_sense: str) -> float:
    """Min or max of axis j over the convex hull of poly.X, in physical units."""
    X = poly.X
    sign = 1.0 if sense == "max" else -1.0
    res = linprog(
        X[:, j] * (1.0 if target_sense == "min" else -1.0),
        A_ub=np.array([sign * X[:, k] for k, _ in constraints]),
        b_ub=[sign * value for _, value in constraints],
        A_eq=np.ones((1, X.shape[0])),
        b_eq=[1.0],
        bounds=(0, None),
        method="highs",
    )
    if not res.success:
        raise RuntimeError(f"inner LP failed for axis {poly.names[j]} ({target_sense}): {res.message}")
    return float(X[:, j] @ res.x) * poly.scale[j] + poly.offset[j]


def outer_bound(poly, constraints, sense: str, j: int, target_sense: str) -> float:
    """Min or max of axis j over the outer approximation, in physical units."""
    n = poly.A.shape[1]
    c = np.zeros(n)
    c[j] = 1.0 if target_sense == "min" else -1.0
    bounds = [(None, None)] * n
    for k, value in constraints:
        bounds[k] = (None, value) if sense == "max" else (value, None)
    res = linprog(c, A_ub=poly.A, b_ub=poly.b, bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError(f"outer LP failed for axis {poly.names[j]} ({target_sense}): {res.message}")
    return float(res.x[j]) * poly.scale[j] + poly.offset[j]


def draw_cell(ax, poly, axis_idx, ranges, constraints, sense, region, metric, limit_marker) -> None:
    """One cell. limit_marker is (year, value in %, marker) on the limited axis itself, else None."""
    x = [int(y) for y in YEARS]
    color = REGION_COLOR[region]
    base_y, lo_full, hi_full = zip(*[ranges[(region, metric, y)] for y in YEARS])
    _draw_ribbon(ax, x, lo_full, hi_full, color, alpha=0.15, zorder=1)

    inner, outer = [], []
    for y in YEARS:
        j = axis_idx[axis_name(region, metric, y)]
        factor, _ = display_unit(poly.units[j])
        inner.append([inner_bound(poly, constraints, sense, j, s) * factor for s in ("min", "max")])
        outer.append([outer_bound(poly, constraints, sense, j, s) * factor for s in ("min", "max")])
    inner, outer = np.array(inner), np.array(outer)
    _draw_ribbon(ax, x, inner[:, 0], inner[:, 1], color, alpha=RIBBON_ALPHA, zorder=3)
    ax.plot(x, outer[:, 0], color=color, linestyle="--", linewidth=1.0, zorder=4)
    ax.plot(x, outer[:, 1], color=color, linestyle="--", linewidth=1.0, zorder=4)
    ax.plot(x, base_y, color="black", marker="*", markersize=8, linewidth=1.0, linestyle="--",
            alpha=0.8, zorder=15)
    if limit_marker:
        year, value, marker = limit_marker
        ax.plot(int(year), value, marker=marker, markersize=10, color=color,
                markeredgecolor="black", markeredgewidth=0.6, linestyle="none", zorder=20)
    print(f"    {region:5s} {metric:9s} " + "  ".join(
        f"{y}: full [{lo_full[i]:,.1f}, {hi_full[i]:,.1f}] inner [{inner[i, 0]:,.1f}, {inner[i, 1]:,.1f}] "
        f"outer [{outer[i, 0]:,.1f}, {outer[i, 1]:,.1f}]"
        for i, y in enumerate(YEARS)))
    ax.set_xticks(x)
    ax.set_xlim(x[0] - 2, x[-1] + 2)
    ax.grid(axis="y", alpha=0.3)


def cost_increase(poly, axis_idx, constraints, sense: str) -> float:
    """Total cost of the cheapest blend under the limit, in % above baseline. An
    upper limit on the true extra cost (the outer lower bound is just the baseline)."""
    j = axis_idx["net_present_cost"]
    return 100 * (inner_bound(poly, constraints, sense, j, "min") / poly.c_star - 1)


def fig_share_limit(poly, axis_idx, ranges, limited, metric, sense, limit, marker, fig_name) -> None:
    relation = "at most" if sense == "max" else "at least"
    n_rows, n_cols = len(REGIONS), len(METRIC_COLUMNS)
    fig = plt.figure(figsize=(3.2 * n_cols, 2.6 * n_rows * len(YEARS) + 1.2))
    outer_grid = fig.add_gridspec(len(YEARS), 1, hspace=0.22, left=0.07, right=0.98, top=0.92, bottom=0.1)
    top_axes = {}
    costs = {}
    col_axes: list = [None] * n_cols
    for block, year in enumerate(YEARS):
        print(f"  {fig_name}: {limited} {metric} {relation} {limit:.0%} in {year}")
        constraints = share_constraint(poly, axis_idx, limited, metric, year, limit)
        inner_grid = outer_grid[block].subgridspec(n_rows, n_cols, hspace=0.1, wspace=0.34)
        for i, region in enumerate(REGIONS):
            for j, column in enumerate(METRIC_COLUMNS):
                ax = fig.add_subplot(inner_grid[i, j], sharey=col_axes[j])
                col_axes[j] = col_axes[j] or ax
                on_limited_axis = region == limited and column == metric
                draw_cell(ax, poly, axis_idx, ranges, constraints, sense, region, column,
                          (year, limit * 100, marker) if on_limited_axis else None)
                ax.tick_params(labelsize=8, labelleft=True, labelbottom=i == n_rows - 1)
                if block == 0 and i == 0:
                    ax.set_title(METRIC_LABEL[column], fontsize=11, fontweight="bold",
                                 color=METRIC_COLOR[column], pad=20)
                if i == 0 and j == 0:
                    top_axes[year] = ax
                _, unit_label = display_unit(poly.units[axis_idx[axis_name(region, column, YEARS[0])]])
                scope = "until year" if METRIC_IS_CUMULATIVE[column] else "in year"
                ylabel = f"{scope} [{unit_label}]"
                if j == 0:
                    ylabel = f"$\\bf{{{region.capitalize()}}}$\n{ylabel}"
                ax.set_ylabel(ylabel, fontsize=8.5)
        costs[year] = cost_increase(poly, axis_idx, constraints, sense)
        print(f"    extra total cost of the cheapest blend: {costs[year]:+.2f}%")

    for year in YEARS:
        position = top_axes[year].get_position()
        fig.text(position.x0, position.y1 + 0.006,
                 f"{limited.capitalize()}: {relation} {limit:.0%} in {year} "
                 f"(extra total cost at most {costs[year]:+.1f}%)",
                 fontsize=9.5, fontweight="bold", ha="left", va="bottom")
    handles = [
        Patch(facecolor="#999999", alpha=0.15, label="full near-optimal range"),
        Patch(facecolor="#999999", alpha=RIBBON_ALPHA, label="with limit: achievable (inner)"),
        Line2D([0], [0], color="#999999", linestyle="--", linewidth=1.0, label="with limit: not ruled out (outer)"),
        Line2D([0], [0], color="black", marker="*", markersize=9, linewidth=1.0, linestyle="--",
               label="cost-optimal baseline"),
        Line2D([0], [0], marker=marker, color="none", markerfacecolor="#999999", markeredgecolor="black",
               markeredgewidth=0.6, markersize=10, label="imposed limit"),
    ]
    fig.suptitle(f"{limited.capitalize()} limited: {SHARE_LABEL[metric]} {relation} {limit:.0%}",
                 fontsize=12, fontweight="bold", y=0.985)
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=9, frameon=False)
    savefig(fig, fig_name)


def main() -> None:
    poly, axis_idx, origin, phys, base = load_data()
    ranges = compute_ranges(poly, axis_idx, origin, phys, base)
    for metric, first in FIRST_FIGURE.items():
        number = first
        for sense, limit, marker in LIMITS:
            for region in REGIONS:
                name = f"fig{number}_{region}_{metric}_{sense}{limit * 100:.0f}"
                fig_share_limit(poly, axis_idx, ranges, region, metric, sense, limit, marker, name)
                number += 1


if __name__ == "__main__":
    main()
