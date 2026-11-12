"""fig61: what happens to the other exploration axes if industrial heat is (nearly) fully
electrified, or (nearly) not at all? Read from the MGA run's polytope (run 47, see
plots/mga_capex_periods_common.py), with no re-solving of ZEN-garden.

Two limits on the industrial heat electrification share, each in 2034 and in 2050:
  A  99-100%
  B  0-1%
The bands are one tolerance_explore (0.01 = 1 percentage point of heat share) wide, the
resolution of run 47's approximation; many solved designs lie in both corners. Earlier
versions (95-100% / 0-5%, and 95-100% in 2050 only) are in git history; they gave the
same picture.
For each, CCS utilisation and imported biomass in 2034 and 2050 and the net present cost
get their min and max under the limit, next to the unconstrained near-optimal range. Each edge is one LP (inner_bound / outer_bound from
plot_mga_diffusion_whatif.py):
  wide light bar   outer approximation (cuts A z <= b): the widest the range can be
  narrow dark bar  convex hull of the solved designs: ranges certainly reachable
The true range lies between the two. For cost, the lower end is the cheapest way to meet the
mandate (outer = lower limit, inner = upper limit of that minimum); the upper end is always
the cost slack.

Usage (zen-garden-plugins-env, PYTHONPATH=../ZEN-garden-plugins):
    python scripts/plot_mga_heat_mandate.py
"""

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from plots.figure_settings import SCENARIO_PALETTE, apply_font_mode, eth_tint

apply_font_mode()

from plot_mga_diffusion_whatif import (
    AXIS_PREFIX, INK, MANDATE_COLOR, MUTED, RUN_PATH, TITLE, YEARS, YLABEL, extra_cost_bn, inner_bound,
    load_polytope, outer_bound, solve_all, style_axes, to_display,
)
from plots.mga_capex_periods_common import METRIC_COLOR, RUN_LABEL, savefig

METRICS = ("heat", "ccs", "biomass")
GREY = SCENARIO_PALETTE[6]
SCENARIOS = {  # key -> (legend label, {year: (min share, max share)}, tint; None = grey)
    "free": ("none: no limit (near-optimal space)", {}, None),
    "A": ("A: heat 99-100% in 2034 and 2050", {2034: (0.99, 1.0), 2050: (0.99, 1.0)}, 0.0),
    "B": ("B: heat 0-1% in 2034 and 2050", {2034: (0.0, 0.01), 2050: (0.0, 0.01)}, 0.5),
}
TICK_LABEL = {"free": "none", "A": "A", "B": "B"}
# Each panel in its technology's colour (heat magenta, CCS blue, biomass green); the cost
# panel in heat's, since the limits are on heat. A full colour, B a light shade.
PANEL_COLOR = {"heat": MANDATE_COLOR["heat"], "ccs": METRIC_COLOR["ccs"], "biomass": METRIC_COLOR["biomass"],
               "cost": MANDATE_COLOR["heat"]}


def scenario_color(key: str, panel: str) -> str:
    tint = SCENARIOS[key][2]
    if tint is None:
        return GREY
    return eth_tint(PANEL_COLOR[panel], tint) if tint else PANEL_COLOR[panel]
OUTER_ALPHA = 0.3


def scenario_ranges(poly, axis_idx, limits: dict) -> dict:
    """{"inner"/"outer": ranges as from solve_all (None if the limits cannot be met)}.
    A limit at the axis's own min or max adds no constraint."""
    floors, ceilings = [], []
    for year, (low, high) in limits.items():
        k = axis_idx[f"{AXIS_PREFIX['heat']}_{year}"]
        if low > 0:
            floors.append((k, (low - poly.offset[k]) / poly.scale[k]))
        if high < 1:
            ceilings.append((k, (high - poly.offset[k]) / poly.scale[k]))
    return {name: solve_all(poly, axis_idx, floors, ceilings, bound, METRICS)
            for name, bound in (("inner", inner_bound), ("outer", outer_bound))}


def report(results: dict, poly) -> None:
    for key, ranges in results.items():
        print(f"{SCENARIOS[key][0]}:")
        inner, outer = ranges["inner"], ranges["outer"]
        if outer is None:
            print("  not reachable")
            continue
        for item in outer:
            o = outer[item]
            i = inner[item] if inner else (np.nan, np.nan)
            name = "cost [% above C*]" if item == "cost" else f"{item[0]} {item[1]}"
            print(f"  {name:22s} outer [{o[0]:8.2f}, {o[1]:8.2f}]  inner [{i[0]:8.2f}, {i[1]:8.2f}]")
        if inner:
            print(f"  cheapest extra cost: {extra_cost_bn(outer['cost'][0], poly.c_star):,.1f} (outer) to "
                  f"{extra_cost_bn(inner['cost'][0], poly.c_star):,.1f} bn EUR (inner)")


def _bar(ax, x, width, span, color, alpha, zorder):
    if span is not None:
        ax.bar(x, span[1] - span[0], bottom=span[0], width=width, color=color, alpha=alpha,
               edgecolor="white", linewidth=0.4, zorder=zorder)


def draw_metric(ax, poly, axis_idx, metric: str, results: dict, fmt: str) -> None:
    keys = list(SCENARIOS)
    n = len(keys)
    width = 0.84 / n
    ticks, tick_labels = [], []
    for g, year in enumerate(YEARS):
        for b, key in enumerate(keys):
            x = g + (b - (n - 1) / 2) * width
            ticks.append(x)
            tick_labels.append(TICK_LABEL[key])
            outer, inner = results[key]["outer"], results[key]["inner"]
            color = scenario_color(key, metric)
            if outer is None:
                ax.text(x, 0, "x", ha="center", va="bottom", fontsize=8, color=MUTED)
                continue
            o = outer[metric, year]
            _bar(ax, x, width * 0.9, o, color, OUTER_ALPHA, 3)
            i = inner[metric, year] if inner else None
            _bar(ax, x, width * 0.4, i, color, 0.95, 4)
            if i is not None:
                for value, va, dy in ((i[0], "top", -2), (i[1], "bottom", 2)):
                    ax.annotate(fmt.format(value), (x, value), xytext=(0, dy), textcoords="offset points",
                                ha="center", va=va, fontsize=6.5, color=INK, zorder=6)
        baseline = to_display(metric, poly.z_star_phys[axis_idx[f"{AXIS_PREFIX[metric]}_{year}"]])
        ax.plot([g - 0.45, g + 0.45], [baseline] * 2, color="black", linestyle="--", linewidth=1.0, zorder=5)
    if metric == "heat":
        for _, limits, _ in SCENARIOS.values():
            for low, high in set(limits.values()):
                ax.axhspan(100 * low, 100 * high, color=MANDATE_COLOR["heat"], alpha=0.08, linewidth=0, zorder=1)
    ax.set_xticks(ticks, tick_labels, fontsize=8)
    for g, year in enumerate(YEARS):
        ax.annotate(str(year), (g, 0), xycoords=("data", "axes fraction"), xytext=(0, -20),
                    textcoords="offset points", ha="center", va="top", fontsize=9.5, fontweight="bold", color=INK)
    ax.set_xlim(-0.55, len(YEARS) - 0.45)
    ax.use_sticky_edges = False
    ax.margins(y=0.08)
    ax.set_ylim(bottom=min(0, ax.get_ylim()[0]))
    ax.grid(axis="y", alpha=0.25)
    style_axes(ax, TITLE[metric], YLABEL[metric])
    ax.tick_params(axis="x", colors=INK)


def draw_cost(ax, poly, results: dict) -> None:
    """Cheapest extra cost per scenario: the range between outer (lower) and inner (upper)
    limit, labelled in bn EUR."""
    slack = 100 * poly.epsilon
    for x, key in enumerate(SCENARIOS):
        outer, inner = results[key]["outer"], results[key]["inner"]
        color = scenario_color(key, "cost")
        if outer is None:
            ax.text(x, slack / 2, "not\nreachable", ha="center", va="center", fontsize=8, color=MUTED)
            continue
        low = outer["cost"][0]
        high = inner["cost"][0] if inner else slack
        ax.bar(x, max(high - low, slack * 0.004), bottom=low, width=0.5, color=color, alpha=0.6,
               edgecolor=color, linewidth=0.8, zorder=3)
        label = (f"+{max(0.0, extra_cost_bn(low, poly.c_star)):,.0f} to "
                 f"+{max(0.0, extra_cost_bn(high, poly.c_star)):,.0f} bn")
        ax.annotate(label, (x, high), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    fontsize=7.5, color=INK)
    ax.axhline(slack, color=INK, linewidth=0.8, linestyle=":", zorder=2)
    ax.set_xticks(range(len(SCENARIOS)), [TICK_LABEL[key] for key in SCENARIOS], fontsize=9)
    ax.set_xlim(-0.6, len(SCENARIOS) - 0.4)
    ax.set_ylim(0, slack * 1.08)
    ax.yaxis.set_major_formatter(lambda v, _: "$C^*$" if v == 0 else f"+{v:g}%")
    ax.grid(axis="y", alpha=0.25)
    style_axes(ax, "Cheapest extra cost", "Cost above optimum")
    ax.tick_params(axis="x", colors=INK)


def main() -> None:
    poly = load_polytope(RUN_PATH)
    print(f"loaded {poly.X.shape[0]} points, converged={poly.converged}")
    axis_idx = {name: i for i, name in enumerate(poly.names)}
    results = {key: scenario_ranges(poly, axis_idx, limits) for key, (_, limits, _) in SCENARIOS.items()}
    report(results, poly)

    fig, axes = plt.subplots(1, 4, figsize=(15, 4.9), gridspec_kw={"width_ratios": [1, 1, 1, 0.75]})
    fig.subplots_adjust(left=0.05, right=0.99, top=0.84, bottom=0.25, wspace=0.32)
    for ax, metric, fmt in zip(axes, METRICS, ("{:.0f}", "{:.0f}", "{:,.0f}")):
        draw_metric(ax, poly, axis_idx, metric, results, fmt)
    draw_cost(axes[3], poly, results)
    fig.suptitle(f"{RUN_LABEL}: industrial heat electrification limited to 99-100% or 0-1%, effect on the other axes",
                 fontsize=13, fontweight="bold", color=INK, x=0.05, ha="left")
    # Scenarios are named under each bar; the legend spells them out (no swatch, since the
    # colour depends on the panel: full colour = A, light shade = B, grey = none).
    handles = [Line2D([0], [0], color="none", label=label) for label, _, _ in SCENARIOS.values()] + [
        Patch(facecolor=GREY, alpha=OUTER_ALPHA, label="wide light bar: outer approximation (widest possible)"),
        Patch(facecolor=GREY, label="narrow dark bar: hull of solved designs (certainly reachable)"),
        Line2D([0], [0], color="black", linestyle="--", linewidth=1.0, label="Cost-optimal baseline"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=2, fontsize=8.5, frameon=False, bbox_to_anchor=(0.5, 0.0),
               handlelength=1.2, columnspacing=3.0)
    savefig(fig, "fig61_heat_mandate_effects")


if __name__ == "__main__":
    main()
