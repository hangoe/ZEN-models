"""fig60: minimum possible net present cost over diffusion rate bands, for industrial heat
electrification and CCS in one plot (parameters_mga.csv task_id 47).

For each technology group and each 5% band of r_diff (0-5%, 5-10%, ..., 95-100%), the
share in 2034 and 2050 is held between the trajectories of the band's two rates
(see plot_mga_diffusion_whatif.py, fig51, for the trajectory and the 2022 starts). The
0-5% band has no lower limit: it means "at most the 5% trajectory". The other share and
biomass imports stay free. Two values are drawn per band. The solid line is the cheapest blend of solved designs
that meets the band, an LP over the convex hull of the polytope's points: an upper limit
on the true minimum cost. The dashed line is the same LP over the outer approximation
(the polytope's cuts A z <= b): a lower limit. The true minimum lies in the shaded range
between them. An x at the top means not even the outer approximation meets the band; where
only the hull fails, the range runs up to the cost slack.

Fast bands converge: once the lower trajectory is at 100% in 2030, 2038 and 2050, all
faster bands impose the same limits. min_cost_curve is reused by fig73
(plot_mga_run_comparison.py) to draw the same curves for the two compared runs.

Usage (zen-garden-plugins-env, PYTHONPATH=../ZEN-garden-plugins):
    python scripts/plot_mga_npc_vs_diffusion.py
"""

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from plot_mga_diffusion_whatif import (
    AXIS_PREFIX, INK, MANDATE_COLOR, MUTED, RUN_PATH, SHARE_METRICS, YEARS, diffusion_trajectory,
    extra_cost_bn, initial_values, inner_bound, load_polytope, mandate_start, outer_bound, style_axes,
)
from plots.figure_settings import apply_font_mode
from plots.mga_capex_periods_common import savefig

apply_font_mode()

STEP = 0.05
BANDS = [(round(k * STEP, 2), round((k + 1) * STEP, 2)) for k in range(20)]
NAMES = {"heat": "Industrial heat electrification", "ccs": "CCS"}
CENTRES = np.array([100 * (low + high) / 2 for low, high in BANDS])


def band_limits(poly, axis_idx, metric: str, start: tuple[float, float], low: float, high: float):
    """Floors and ceilings in normalised units for one band; no floor for low == 0."""
    floors, ceilings = [], []
    lower = diffusion_trajectory(low, start[0], k_free=start[1]) if low > 0 else None
    upper = diffusion_trajectory(high, start[0], k_free=start[1])
    for year in YEARS:
        k = axis_idx[f"{AXIS_PREFIX[metric]}_{year}"]
        if lower:
            floors.append((k, (lower[year] - poly.offset[k]) / poly.scale[k]))
        if upper[year] < 1.0:
            ceilings.append((k, (upper[year] - poly.offset[k]) / poly.scale[k]))
    return floors, ceilings


def min_cost(poly, floors, ceilings, bound) -> float | None:
    """Minimum cost in % above c_star, or None if the band cannot be met."""
    value = bound(poly, floors, ceilings, poly.cost_col, "min")
    return None if value is None else 100 * (value / poly.c_star - 1)


def min_cost_curve(poly, axis_idx, metric: str, start: tuple[float, float]) -> tuple[list, list]:
    """(inner, outer) minimum cost in % above c_star for each band in BANDS (None = not met)."""
    inner, outer = [], []
    for low, high in BANDS:
        floors, ceilings = band_limits(poly, axis_idx, metric, start, low, high)
        inner.append(min_cost(poly, floors, ceilings, inner_bound))
        outer.append(min_cost(poly, floors, ceilings, outer_bound))
    print(f"{metric}: " + ", ".join(
        f"{100 * lo:.0f}-{100 * hi:.0f}% " + ("n/a" if c is None else f"+{c:.2f}% (outer +{o:.2f}%)")
        for (lo, hi), c, o in zip(BANDS, inner, outer)))
    return inner, outer


def style_cost_axis(ax, poly) -> None:
    """y axis from C* to the cost slack, in % (left) and bn EUR (right); x axis = bands."""
    slack = 100 * poly.epsilon
    ax.axhline(0, color="#BBBBBB", linewidth=0.8, zorder=2)
    ax.axhline(slack, color=INK, linewidth=0.8, linestyle=":", zorder=2)
    ax.set_ylim(-slack * 0.04, slack * 1.1)
    ax.set_yticks([0, slack], [f"$C^*$\n{poly.c_star * 1e-3:,.0f} bn EUR", f"$C^*(1+\\varepsilon)$\n+{slack:g}%"])
    # Same scale in absolute terms: % above C* -> bn EUR above C*.
    bn_per_pct = extra_cost_bn(1.0, poly.c_star)
    top_bn = extra_cost_bn(slack, poly.c_star)
    step_bn = next(step for step in (25, 50, 100, 250, 500, 1000) if top_bn / step <= 6)
    right = ax.secondary_yaxis("right", functions=(lambda p: p * bn_per_pct, lambda b: b / bn_per_pct))
    right.set_yticks(np.arange(0, top_bn, step_bn))
    right.set_yticklabels([f"+{v:,.0f}" for v in np.arange(0, top_bn, step_bn)])
    right.set_ylabel("Cost above optimum [bn EUR]", fontsize=9, color=MUTED)
    right.tick_params(labelsize=8, colors=MUTED)
    right.spines["right"].set_color("#BBBBBB")
    step_pct = slack / 4 if slack < 4 else 1.0
    minor = np.arange(step_pct, slack - 1e-9, step_pct)
    ax.set_yticks(minor, [f"+{v:g}%" for v in minor], minor=True)
    ax.tick_params(axis="y", which="minor", labelsize=8, colors=MUTED, length=2)
    ax.grid(axis="y", which="both", alpha=0.2)
    ax.set_xticks(np.arange(0, 101, 10))
    ax.set_xticks(np.arange(0, 101, 5), minor=True)
    ax.set_xlim(0, 100)
    ax.set_xlabel(r"Diffusion rate band $r^{\mathrm{diff}}$ [%]",
                  fontsize=9, color=MUTED)


def plot_curve(ax, poly, inner: list, color: str, label: str, linestyle: str = "-",
               outer: list | None = None) -> None:
    """One metric's inner curve, its cheapest band (open dot) and unmet bands (x at the top).
    With `outer`, also the outer approximation's curve (dashed) and the range between the
    two (shaded; up to the cost slack where the hull cannot meet the band)."""
    slack = 100 * poly.epsilon
    values = np.array([np.nan if c is None else c for c in inner])
    if outer is not None:
        lower = np.array([np.nan if c is None else c for c in outer])
        upper = np.where(np.isfinite(values), values, slack)
        ax.fill_between(CENTRES, lower, upper, where=np.isfinite(lower), color=color, alpha=0.18, linewidth=0,
                        zorder=3)
        ax.plot(CENTRES, lower, color=color, linewidth=1.3, linestyle="--", zorder=4)
        unmet = [x for x, o in zip(CENTRES, outer) if o is None]
    else:
        unmet = [x for x, c in zip(CENTRES, inner) if c is None]
    ax.plot(CENTRES, values, color=color, linewidth=2.0, linestyle=linestyle, label=label, zorder=4)
    if np.isfinite(values).any():
        best = int(np.nanargmin(values))
        ax.plot(CENTRES[best], values[best], marker="o", markersize=8, markerfacecolor="white",
                markeredgecolor=color, markeredgewidth=2.0, zorder=5)
    if unmet:
        ax.plot(unmet, [slack * 1.04] * len(unmet), linestyle="none", marker="x", color=color, zorder=4)


def main() -> None:
    poly = load_polytope(RUN_PATH)
    print(f"loaded {poly.X.shape[0]} points, converged={poly.converged}, final_gap={poly.final_gap:.3f}")
    axis_idx = {name: i for i, name in enumerate(poly.names)}
    starts = mandate_start(poly, initial_values(poly))

    fig, ax = plt.subplots(figsize=(9, 5.2))
    for metric in SHARE_METRICS:
        inner, outer = min_cost_curve(poly, axis_idx, metric, starts[metric])
        plot_curve(ax, poly, inner, MANDATE_COLOR[metric], NAMES[metric], outer=outer)
    style_cost_axis(ax, poly)
    style_axes(ax, "Minimum possible net present cost per diffusion rate band", "Net present cost (min. possible)")
    handles, _ = ax.get_legend_handles_labels()
    handles += [Line2D([0], [0], color=MUTED, linewidth=2.0, label="Inner hull (upper limit)"),
                Line2D([0], [0], color=MUTED, linewidth=1.3, linestyle="--", label="Outer approximation (lower limit)"),
                Patch(facecolor=MUTED, alpha=0.18, label="Range of the true minimum")]
    ax.legend(handles=handles, frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(0.0, 0.88))
    savefig(fig, "fig60_min_npc_vs_diffusion")


if __name__ == "__main__":
    main()
