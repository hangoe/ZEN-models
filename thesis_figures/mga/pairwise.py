"""Solved near-optimal designs of two runs projected on every axis pair (thesis Fig. A13,
corner plot as in Steen 2026).

Axes: heat electrification, CO2 storage utilisation and imported biomass in 2034 / 2050, and
the total cost in % above C*. Each panel shows the 2D convex hull of the reference run's
designs (filled light) and of the comparison run's (filled dark, with its designs as points);
the number is the comparison run's hull area relative to the reference run's.

Earlier version: scripts/plot_mga_run_comparison.py (fig72_*_pairwise_hulls), removed in
commit 9390c9c0.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.spatial import ConvexHull, QhullError

from ..style import ETH_GREY, REPORT_WIDTH, eth_tint, save_figure
from .limit_radar import INK, METRIC_COLOR, NAME
from .polytope import AXIS_PREFIX, LIMITED_UNIT, METRICS, YEARS, load_run_polytope, to_display

REFERENCE_FILL = eth_tint(ETH_GREY, 0.45)
COMPARE_COLOR = "#333333"
AXES = [(m, y) for m in METRICS for y in YEARS] + ["cost"]  # plot order


def display_values(poly) -> np.ndarray:
    """Solved designs in display units, columns in AXES order (cost in % above C*)."""
    phys = poly.X * poly.scale + poly.offset
    idx = {name: i for i, name in enumerate(poly.names)}
    cols = []
    for axis in AXES:
        if axis == "cost":
            cols.append(100 * (phys[:, poly.cost_col] / poly.c_star - 1))
        else:
            metric, year = axis
            cols.append(to_display(metric, phys[:, idx[f"{AXIS_PREFIX[metric]}_{year}"]]))
    return np.column_stack(cols)


def axis_label(axis) -> tuple[str, str]:
    if axis == "cost":
        return "Cost\n[% above $C^*$]", INK
    metric, year = axis
    return f"{NAME[metric]} {year}\n[{LIMITED_UNIT[metric]}]", METRIC_COLOR[metric]


def corner_grid():
    """Lower-triangle grid of (n-1) x (n-1) panels: the figure and [(ax, x axis, y axis)]."""
    n = len(AXES)
    fig, axes = plt.subplots(n - 1, n - 1, figsize=(REPORT_WIDTH, REPORT_WIDTH), squeeze=False)
    fig.subplots_adjust(left=0.1, right=0.99, bottom=0.09, top=0.99, wspace=0.12, hspace=0.12)
    panels = []
    for row in range(1, n):
        for col in range(n - 1):
            ax = axes[row - 1, col]
            if col >= row:
                ax.axis("off")
                continue
            ax.grid(alpha=0.25, linewidth=0.4)
            ax.tick_params(labelsize=5.5, length=2, pad=1)
            if row == n - 1:
                text, color = axis_label(AXES[col])
                ax.set_xlabel(text, fontsize=6.5, color=color, labelpad=2)
            else:
                ax.set_xticklabels([])
            if col == 0:
                text, color = axis_label(AXES[row])
                ax.set_ylabel(text, fontsize=6.5, color=color, labelpad=2)
            else:
                ax.set_yticklabels([])
            panels.append((ax, col, row))
    return fig, panels


def hull_outline(points: np.ndarray) -> tuple[np.ndarray, float]:
    """Closed outline of the 2D convex hull and its area (a segment if degenerate)."""
    try:
        hull = ConvexHull(points)
    except QhullError:
        order = np.lexsort(points.T[::-1])
        return points[[order[0], order[-1]]], 0.0
    return points[np.append(hull.vertices, hull.vertices[0])], hull.volume


def pairwise_hulls(name: str, reference: str = "T3", compare: str = "T4",
                   labels: tuple[str, str] = ("Test run 2 (cost slack 1%)", "Cost slack 0.2%")) -> None:
    ref, comp = (display_values(load_run_polytope(r)) for r in (reference, compare))
    fig, panels = corner_grid()
    for ax, i, j in panels:
        outline_ref, area_ref = hull_outline(ref[:, [i, j]])
        outline_cmp, area_cmp = hull_outline(comp[:, [i, j]])
        ax.fill(*outline_ref.T, color=REFERENCE_FILL, linewidth=0, zorder=1)
        ax.plot(*outline_ref.T, color=ETH_GREY, linewidth=0.5, zorder=1)
        ax.fill(*outline_cmp.T, color=COMPARE_COLOR, alpha=0.25, linewidth=0, zorder=2)
        ax.plot(*outline_cmp.T, color=COMPARE_COLOR, linewidth=0.6, zorder=3)
        ax.scatter(comp[:, i], comp[:, j], s=0.2, color=COMPARE_COLOR, linewidths=0, alpha=0.2,
                   rasterized=True, zorder=2)
        if area_ref > 0:
            ax.text(0.96, 0.05, f"$\\times${area_cmp / area_ref:.2f}", transform=ax.transAxes, ha="right",
                    va="bottom", fontsize=5.5, color=INK,
                    bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 0.4})
    handles = [
        Patch(facecolor=REFERENCE_FILL, edgecolor=ETH_GREY, linewidth=0.5, label=f"{labels[0]}, hull"),
        Patch(facecolor=eth_tint(COMPARE_COLOR, 0.25), edgecolor=COMPARE_COLOR, linewidth=0.6,
              label=f"{labels[1]}, hull and designs"),
        Line2D([], [], color="none", label=f"$\\times$ = hull area relative to\n{labels[0].lower()}"),
    ]
    fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.97, 0.95), fontsize=7.5, frameon=False)
    save_figure(fig, name, dpi=300)
