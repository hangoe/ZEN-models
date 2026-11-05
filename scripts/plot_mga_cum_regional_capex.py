"""What the own-axis min/max solves of the MGA run show (see
plots/mga_capex_periods_common.py). Everything is read from polytope.npz, which
holds every axis's physical value at every solved point.

  fig10_crosseffects             how pushing one axis moves every other axis
  fig11_range_by_region          each axis's baseline and min/max, by region colour
  fig12_range_by_metric          the same figure, by metric colour

fig10 colours cells by (value - baseline) / that axis's own min-max range, not
by a ratio to baseline: emissions can be negative and shares can be near zero
at baseline, so ratios are undefined or explode. The range makes all units
comparable; the cell text gives the physical change. Total cost has no min/max
solves of its own, so its row is scaled by the cost budget (epsilon * c_star)
and labelled in % above the optimum.

Usage:
    python scripts/plot_mga_cum_regional_capex.py
"""

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import Patch, Rectangle

from plots.figure_settings import apply_font_mode, eth_tint

# See figure_settings.FONT_MODE: one flag switches every figure script's font.
apply_font_mode()
from plots.mga_capex_periods_common import (
    METRIC_COLOR,
    METRIC_COLUMNS,
    METRIC_IS_CUMULATIVE,
    METRIC_LABEL,
    METRICS,
    POLY_PATH,
    REGION_COLOR,
    REGIONS,
    REPO_ROOT,
    RUN_LABEL,
    YEAR_TINT,
    YEARS,
    axis_name,
    display_unit,
    parse_axis,
    savefig,
    year_tint,
)
from zen_garden_plugins.mga.polytope_io import load_polytope


_LABEL_BOX = dict(facecolor="white", alpha=0.75, edgecolor="none", pad=0.6)


def load_data():
    """(poly, axis_idx, origin, phys, base): the polytope, a name->column map,
    each point's origin label, every point in physical units, and the baseline."""
    if not POLY_PATH.exists():
        raise FileNotFoundError(f"polytope not found at {POLY_PATH}")
    poly = load_polytope(POLY_PATH)
    axis_idx = {n: i for i, n in enumerate(poly.names)}
    origin = list(poly.point_origin)
    phys = np.array([poly.to_phys(x) for x in poly.X])
    base = phys[origin.index("z_star")]
    print(f"  loaded {len(origin)} points from {POLY_PATH.relative_to(REPO_ROOT)}")
    return poly, axis_idx, origin, phys, base


def _design_axes() -> list[str]:
    """Design axes grouped by metric, then region, then year."""
    return [axis_name(r, m, y) for m in METRICS for r in REGIONS for y in YEARS]


def _short_axis_label(name: str) -> str:
    info = parse_axis(name)
    return f"{info.region} '{info.year[-2:]}"


def _change_label(delta: float, metric: str) -> str:
    """Physical change as cell text; the unit is in the row label."""
    decimals = 0 if metric in ("capex", "transport", "heating") else 1
    if round(delta, decimals) == 0:
        return "0"
    return f"{delta:+,.{decimals}f}"


def fig_crosseffects(poly, axis_idx, origin, phys, base) -> None:
    axes_order = _design_axes()
    columns = [(ax, sense) for ax in axes_order for sense in ("max", "min")]
    rows = axes_order + ["net_present_cost"]

    own_range = {ax: phys[origin.index(f"max:{ax}"), axis_idx[ax]] - phys[origin.index(f"min:{ax}"), axis_idx[ax]]
                 for ax in axes_order}
    own_range["net_present_cost"] = poly.epsilon * poly.c_star

    scaled = np.full((len(rows), len(columns)), np.nan)
    text = [["" for _ in columns] for _ in rows]
    is_own = np.zeros_like(scaled, dtype=bool)
    for i, row in enumerate(rows):
        j_row = axis_idx[row]
        metric = parse_axis(row).metric
        factor, _ = display_unit(poly.units[j_row])
        for j, (ax, sense) in enumerate(columns):
            delta = phys[origin.index(f"{sense}:{ax}"), j_row] - base[j_row]
            is_own[i, j] = row == ax
            if own_range[row] > 0:
                scaled[i, j] = delta / own_range[row]
            if metric == "cost":
                text[i][j] = _change_label(100 * delta / base[j_row], metric)
            else:
                text[i][j] = _change_label(delta * factor, metric)

    fig, ax = plt.subplots(figsize=(0.52 * len(columns) + 3.2, 0.44 * len(rows) + 2.4))
    im = ax.imshow(np.where(is_own, np.nan, scaled), cmap="RdBu_r",
                   norm=TwoSlopeNorm(vmin=-1, vcenter=0, vmax=1), aspect="auto")
    for i in range(len(rows)):
        for j in range(len(columns)):
            if is_own[i, j]:
                ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor="#dddddd", edgecolor="#777777",
                                       hatch="///", linewidth=0.4))
                continue
            value = scaled[i, j]
            color = "white" if np.isfinite(value) and abs(value) > 0.6 else "black"
            ax.text(j, i, text[i][j], ha="center", va="center", fontsize=6.3, color=color)

    ax.set_xticks(range(len(columns)))
    ax.set_xticklabels([f"{_short_axis_label(a)}\n{s}" for a, s in columns], fontsize=6.5)
    ax.set_yticks(range(len(rows)))
    row_labels = []
    for row in rows:
        info = parse_axis(row)
        _, unit_label = display_unit(poly.units[axis_idx[row]])
        if info.metric == "cost":
            row_labels.append("Total cost [% above optimum]")
        else:
            unit = "pp" if unit_label == "%" else unit_label
            row_labels.append(f"{METRIC_LABEL[info.metric]}, {_short_axis_label(row)} [{unit}]")
    ax.set_yticklabels(row_labels, fontsize=8)
    for label, row in zip(ax.get_yticklabels(), rows):
        label.set_color(METRIC_COLOR[parse_axis(row).metric])
    ax.tick_params(length=0)
    ax.set_xticks(np.arange(-0.5, len(columns), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(rows), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.8)
    ax.tick_params(which="minor", length=0)

    block_cols = len(REGIONS) * len(YEARS) * 2
    block_rows = len(REGIONS) * len(YEARS)
    for k in range(1, len(METRICS)):
        ax.axvline(block_cols * k - 0.5, color="black", linewidth=1.4)
    for k in range(1, len(METRICS) + 1):
        ax.axhline(block_rows * k - 0.5, color="black", linewidth=1.4)
    for k in range(len(METRICS)):
        ax.axvline(block_cols * k + block_cols / 2 - 0.5, color="black", linewidth=0.6, ls="--", alpha=0.6)
        x0 = block_cols * k - 0.5
        ax.add_patch(Rectangle((x0, -1.15), block_cols, 0.55, facecolor=METRIC_COLOR[METRICS[k]],
                               edgecolor="white", linewidth=1.5, clip_on=False))
        ax.text(x0 + block_cols / 2, -0.875, f"pushing {METRIC_LABEL[METRICS[k]]}", color="white",
                ha="center", va="center", fontsize=9, fontweight="bold")
    ax.set_xlim(-0.5, len(columns) - 0.5)
    ax.set_ylim(len(rows) - 0.5, -0.5)

    cbar = fig.colorbar(im, ax=ax, fraction=0.018, pad=0.012)
    cbar.set_label("change / axis's own min-max range (cost row: / cost budget)", fontsize=8)
    cbar.ax.tick_params(labelsize=7)
    ax.set_title(f"{RUN_LABEL}: response of every axis to each own-axis min/max solve "
                 f"(cell text = physical change; hatched = pushed axis)",
                 fontsize=11, fontweight="bold", pad=32)
    fig.tight_layout()
    savefig(fig, "fig10_crosseffects")


def _metric_ylabel(metric: str, unit_label: str) -> str:
    scope = "cumulative until year" if METRIC_IS_CUMULATIVE[metric] else "in year"
    return f"{scope} [{unit_label}]"


def _fig_ranges(poly, axis_idx, origin, phys, base, *, by_region: bool, name: str) -> None:
    """One panel per metric: baseline bars per region and year, own-axis min/max
    whiskers, and every value labelled at its position (baseline in bold)."""
    fig, axes = plt.subplots(1, len(METRIC_COLUMNS), figsize=(3.8 * len(METRIC_COLUMNS), 4.4))
    n_years = len(YEARS)
    width = 0.8 / n_years
    x_regions = np.arange(len(REGIONS))
    for ax, metric in zip(axes, METRIC_COLUMNS):
        ticks, tick_labels = [], []
        unit_label = ""
        for r_i, region in enumerate(REGIONS):
            for y_i, year in enumerate(YEARS):
                axis = axis_name(region, metric, year)
                j = axis_idx[axis]
                factor, unit_label = display_unit(poly.units[j])
                value = base[j] * factor
                lo = phys[origin.index(f"min:{axis}"), j] * factor
                hi = phys[origin.index(f"max:{axis}"), j] * factor
                x = x_regions[r_i] + (y_i - (n_years - 1) / 2) * width
                color = year_tint(REGION_COLOR[region] if by_region else METRIC_COLOR[metric], year)
                ax.bar(x, value, width * 0.92, color=color, zorder=3)
                ax.errorbar(x, value, yerr=[[value - lo], [hi - value]], fmt="none", ecolor="black",
                            capsize=3, linewidth=1.0, zorder=4)
                fmt = "{:,.0f}" if metric != "emissions" else "{:,.1f}"
                ax.annotate(fmt.format(hi), (x, hi), xytext=(0, 2), textcoords="offset points",
                            ha="center", va="bottom", fontsize=7, zorder=5, bbox=_LABEL_BOX)
                ax.annotate(fmt.format(lo), (x, lo), xytext=(0, -2), textcoords="offset points",
                            ha="center", va="top", fontsize=7, zorder=5, bbox=_LABEL_BOX)
                # Beside the whisker at the baseline's height, nudged away from
                # a min/max label when the baseline sits next to one.
                near = 0.08 * (hi - lo)
                va, dy = ("top", -1) if hi - value < near else ("bottom", 1) if value - lo < near else ("center", 0)
                ax.annotate(fmt.format(value), (x, value), xytext=(3, dy), textcoords="offset points",
                            ha="left", va=va, fontsize=7, fontweight="bold", zorder=6, bbox=_LABEL_BOX)
                ticks.append(x)
                tick_labels.append(year)
        ax.set_xticks(ticks)
        ax.set_xticklabels(tick_labels, fontsize=7.5)
        for r_i, region in enumerate(REGIONS):
            ax.annotate(region.capitalize(), (x_regions[r_i], 0), xycoords=("data", "axes fraction"),
                        xytext=(0, -24), textcoords="offset points",
                        ha="center", va="top", fontsize=10, fontweight="bold")
        if metric == "emissions":
            ax.axhline(0, color="black", linewidth=0.8, zorder=2)
        # Room for the whisker labels at both ends, including below zero.
        ax.use_sticky_edges = False
        ax.margins(y=0.1)
        ax.set_title(METRIC_LABEL[metric], fontsize=11, fontweight="bold", color=METRIC_COLOR[metric])
        ax.set_ylabel(_metric_ylabel(metric, unit_label), fontsize=9)
        ax.tick_params(axis="y", labelsize=8)
        ax.grid(axis="y", alpha=0.3, zorder=0)
    neutral = "#555555"
    handles = [Patch(facecolor=eth_tint(neutral, YEAR_TINT[y]) if YEAR_TINT[y] else neutral, label=f"baseline, {y}")
               for y in YEARS]
    handles.append(plt.Line2D([0], [0], color="black", linewidth=1.0, marker="_", markersize=7,
                              label="own-axis min/max solve"))
    fig.legend(handles=handles, loc="lower center", ncol=len(handles), fontsize=9, frameon=False,
               bbox_to_anchor=(0.5, -0.04))
    fig.suptitle(f"{RUN_LABEL}: baseline (bold) and near-optimal range of each axis", fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0.05, 1, 0.98))
    savefig(fig, name)


def main() -> None:
    poly, axis_idx, origin, phys, base = load_data()
    fig_crosseffects(poly, axis_idx, origin, phys, base)
    _fig_ranges(poly, axis_idx, origin, phys, base, by_region=True, name="fig11_range_by_region")
    _fig_ranges(poly, axis_idx, origin, phys, base, by_region=False, name="fig12_range_by_metric")


if __name__ == "__main__":
    main()
