"""fig61 / fig61a / fig61b: what happens to the other exploration axes if industrial heat
(fig61), CCS (fig61a) or imported biomass (fig61b) is pushed to its maximum, or to its
minimum? Read from the MGA run's polytope (RUN_SUFFIX in plots/mga_capex_periods_common.py, run 54),
with no re-solving of ZEN-garden.

The limited axis's two limits are the top and bottom 1% of its near-optimal range (the
polytope's scaled axis value >= 0.99 or <= 0.01); for heat that is exactly 99-100% / 0-1%.
For CCS (max 63% in 2034) and biomass (TWh) the bands differ per year and are given in the
legend. The text below describes fig61 (heat); fig61a/b work the same way.

Two limits on the industrial heat electrification share, each in 2034 and in 2050:
  A  99-100%
  B  0-1%
The bands are one tolerance_explore (0.01 = 1 percentage point of heat share) wide, the
resolution of run 57's approximation; many solved designs lie in both corners. Earlier
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
    python scripts/plot_mga_heat_mandate.py [heat|ccs|biomass ...]   (default: all three)
"""

import sys

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from plots.figure_settings import REPORT_WIDTH, SCENARIO_PALETTE, apply_font_mode, eth_tint

apply_font_mode()

SHOW_TITLE = False  # figure suptitle; False for the report

from plot_mga_diffusion_whatif import (
    AXIS_PREFIX, INK, MANDATE_COLOR, MUTED, RUN_PATH, S, TITLE, YEARS, YLABEL, extra_cost_bn, inner_bound,
    load_polytope, outer_bound, report_style, solve_all, style_axes, to_display,
)
from plots.mga_capex_periods_common import METRIC_COLOR, RUN_LABEL, savefig

METRICS = ("heat", "ccs", "biomass")
GREY = SCENARIO_PALETTE[6]
BAND = 0.01  # width of the A / B limits, as a fraction of the limited axis's range
# key -> ((scaled low, scaled high) on the limited axis, or None = no limit; tint; None = grey)
SCENARIO_DEF = {"free": (None, None), "A": ((1 - BAND, 1.0), 0.0), "B": ((0.0, BAND), 0.5)}
TICK_LABEL = {"free": "none", "A": "A", "B": "B"}
LIMITED_NAME = {"heat": "heat", "ccs": "CCS", "biomass": "biomass"}
LIMITED_UNIT = {"heat": "%", "ccs": "%", "biomass": " TWh"}
FIGURE_NAME = {"heat": "fig61_heat_mandate_effects", "ccs": "fig61a_ccs_limit_effects",
               "biomass": "fig61b_biomass_limit_effects"}
SUPTITLE = {"heat": "industrial heat electrification", "ccs": "CCS utilisation", "biomass": "imported biomass"}
# Each panel in its technology's colour (heat magenta, CCS blue, biomass green); the cost
# panel in the limited axis's colour. A full colour, B a light shade.
PANEL_COLOR = {"heat": MANDATE_COLOR["heat"], "ccs": METRIC_COLOR["ccs"], "biomass": METRIC_COLOR["biomass"]}
OUTER_ALPHA = 0.3


def scenario_color(key: str, panel: str, limited: str) -> str:
    tint = SCENARIO_DEF[key][1]
    if tint is None:
        return GREY
    color = PANEL_COLOR[limited if panel == "cost" else panel]
    return eth_tint(color, tint) if tint else color


def physical_band(poly, axis_idx, limited: str, year: int, band: tuple[float, float]) -> tuple[float, float]:
    """Scaled (low, high) on the limited axis -> displayed units (% or TWh)."""
    k = axis_idx[f"{AXIS_PREFIX[limited]}_{year}"]
    return tuple(to_display(limited, poly.offset[k] + poly.scale[k] * v) for v in band)


def scenario_labels(poly, axis_idx, limited: str) -> dict[str, str]:
    """Legend label per scenario, with the limit in displayed units for each year."""
    labels = {"free": "none: no limit (near-optimal space)"}
    for key, which in (("A", "max"), ("B", "min")):
        bands = [physical_band(poly, axis_idx, limited, y, SCENARIO_DEF[key][0]) for y in YEARS]
        texts = [f"{low:,.0f}-{high:,.0f}{LIMITED_UNIT[limited]}" for low, high in bands]
        years = " and ".join(map(str, YEARS))
        if len(set(texts)) == 1:
            where = f"{texts[0]} in {years}"
        else:
            where = ", ".join(f"{t} in {y}" for t, y in zip(texts, YEARS))
        prefix = f"{LIMITED_NAME[limited]} " if limited == "heat" else f"{LIMITED_NAME[limited]} at {which}: "
        labels[key] = f"{key}: {prefix}{where}"
    return labels


def scenario_ranges(poly, axis_idx, limited: str, band) -> dict:
    """{"inner"/"outer": ranges as from solve_all (None if the limits cannot be met)}.
    A limit at the axis's own min or max adds no constraint."""
    floors, ceilings = [], []
    if band is not None:
        low, high = band
        for year in YEARS:
            k = axis_idx[f"{AXIS_PREFIX[limited]}_{year}"]
            if low > 0:
                floors.append((k, low))
            if high < 1:
                ceilings.append((k, high))
    return {name: solve_all(poly, axis_idx, floors, ceilings, bound, METRICS)
            for name, bound in (("inner", inner_bound), ("outer", outer_bound))}


def report(results: dict, poly, labels: dict) -> None:
    for key, ranges in results.items():
        print(f"{labels[key]}:")
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


def draw_metric(ax, poly, axis_idx, metric: str, limited: str, results: dict, fmt: str, title: str) -> None:
    keys = list(SCENARIO_DEF)
    n = len(keys)
    width = 0.84 / n
    ticks, tick_labels = [], []
    for g, year in enumerate(YEARS):
        for b, key in enumerate(keys):
            x = g + (b - (n - 1) / 2) * width
            ticks.append(x)
            tick_labels.append(TICK_LABEL[key])
            outer, inner = results[key]["outer"], results[key]["inner"]
            color = scenario_color(key, metric, limited)
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
                                ha="center", va=va, fontsize=S["value"] - 1, color=INK, zorder=6)
        baseline = to_display(metric, poly.z_star_phys[axis_idx[f"{AXIS_PREFIX[metric]}_{year}"]])
        ax.plot([g - 0.45, g + 0.45], [baseline] * 2, color="black", linestyle="--", linewidth=1.0, zorder=5)
        if metric == limited:  # shade the A and B limits behind this year's bars
            for band, _ in SCENARIO_DEF.values():
                if band is not None:
                    low, high = physical_band(poly, axis_idx, limited, year, band)
                    ax.fill_between([g - 0.45, g + 0.45], low, high, color=PANEL_COLOR[limited], alpha=0.08,
                                    linewidth=0, zorder=1)
    ax.set_xticks(ticks, tick_labels, fontsize=S["tick"] - 1)
    for g, year in enumerate(YEARS):
        ax.annotate(str(year), (g, 0), xycoords=("data", "axes fraction"), xytext=(0, -14),
                    textcoords="offset points", ha="center", va="top", fontsize=S["tick"], fontweight="bold",
                    color=INK)
    ax.set_xlim(-0.55, len(YEARS) - 0.45)
    ax.use_sticky_edges = False
    ax.margins(y=0.08)
    ax.set_ylim(bottom=min(0, ax.get_ylim()[0]))
    ax.grid(axis="y", alpha=0.25)
    style_axes(ax, title, YLABEL[metric])
    ax.tick_params(axis="x", colors=INK)


def draw_cost(ax, poly, results: dict, limited: str, title: str) -> None:
    """Cheapest extra cost per scenario: the range between outer (lower) and inner (upper)
    limit, labelled in bn EUR."""
    slack = 100 * poly.epsilon
    for x, key in enumerate(SCENARIO_DEF):
        outer, inner = results[key]["outer"], results[key]["inner"]
        color = scenario_color(key, "cost", limited)
        if outer is None:
            ax.text(x, slack / 2, "not\nreachable", ha="center", va="center", fontsize=S["value"], color=MUTED)
            continue
        low = outer["cost"][0]
        high = inner["cost"][0] if inner else slack
        ax.bar(x, max(high - low, slack * 0.004), bottom=low, width=0.5, color=color, alpha=0.6,
               edgecolor=color, linewidth=0.8, zorder=3)
        label = (f"+{max(0.0, extra_cost_bn(low, poly.c_star)):,.0f} to "
                 f"+{max(0.0, extra_cost_bn(high, poly.c_star)):,.0f} bn")
        ax.annotate(label, (x, high), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    fontsize=S["value"], color=INK)
    ax.axhline(slack, color=INK, linewidth=0.8, linestyle=":", zorder=2)
    ax.set_xticks(range(len(SCENARIO_DEF)), [TICK_LABEL[key] for key in SCENARIO_DEF], fontsize=S["tick"])
    ax.set_xlim(-0.6, len(SCENARIO_DEF) - 0.4)
    ax.set_ylim(0, slack * 1.08)
    ax.yaxis.set_major_formatter(lambda v, _: "$C^*$" if v == 0 else f"+{v:g}%")
    ax.grid(axis="y", alpha=0.25)
    style_axes(ax, title, "Cost above optimum")
    ax.tick_params(axis="x", colors=INK)


def plot(poly, axis_idx, limited: str) -> None:
    labels = scenario_labels(poly, axis_idx, limited)
    print(f"\n=== limited axis: {limited} ===")
    results = {key: scenario_ranges(poly, axis_idx, limited, band) for key, (band, _) in SCENARIO_DEF.items()}
    report(results, poly, labels)

    with report_style():  # report figure: REPORT_WIDTH, report font sizes, 2 x 2 panels
        height = 5.4
        fig, axes = plt.subplots(2, 2, figsize=(REPORT_WIDTH, height))
        fig.subplots_adjust(left=0.1, right=0.99, top=0.95, bottom=0.92 / height, wspace=0.38, hspace=0.5)
        for ax, letter, metric, fmt in zip(axes.flat, "abc", METRICS, ("{:.0f}", "{:.0f}", "{:,.0f}")):
            draw_metric(ax, poly, axis_idx, metric, limited, results, fmt, f"({letter}) {TITLE[metric]}")
        draw_cost(axes[1, 1], poly, results, limited, "(d) Cheapest extra cost")
        if SHOW_TITLE:  # off for the thesis figures (caption carries the title)
            fig.suptitle(f"{RUN_LABEL}: {SUPTITLE[limited]} limited to the top or bottom 1% of its range, "
                         "effect on the other axes", fontsize=11, fontweight="bold", color=INK, x=0.1, ha="left")
        # Scenarios are named under each bar; the legend spells them out (no swatch, since the
        # colour depends on the panel: full colour = A, light shade = B, grey = none).
        handles = [Line2D([0], [0], color="none", label=label) for label in labels.values()] + [
            Patch(facecolor=GREY, alpha=OUTER_ALPHA, label="Wide light bar: outer approximation"),
            Patch(facecolor=GREY, label="Narrow dark bar: hull of solved designs"),
            Line2D([0], [0], color="black", linestyle="--", linewidth=1.0, label="Cost-optimal baseline"),
        ]
        fig.legend(handles=handles, loc="lower center", ncol=2, fontsize=S["legend"], frameon=False,
                   bbox_to_anchor=(0.5, 0.0), handlelength=1.2, handletextpad=0.5, columnspacing=2.0)
        savefig(fig, FIGURE_NAME[limited])


def main() -> None:
    limited_axes = sys.argv[1:] or list(METRICS)
    poly = load_polytope(RUN_PATH)
    print(f"loaded {poly.X.shape[0]} points, converged={poly.converged}")
    axis_idx = {name: i for i, name in enumerate(poly.names)}
    for limited in limited_axes:
        plot(poly, axis_idx, limited)


if __name__ == "__main__":
    main()
