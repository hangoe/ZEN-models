"""fig62: what happens to the exploration axes if the near-optimal cost slack is tightened?
Read from run 54's polytope (5 ts, tolerance 0.1; RUN54_SUFFIX in
plots/mga_capex_periods_common.py), and from run 57 (1 ts, tolerance 0.01) for
fig62_run57_cost_limit_effects, with no re-solving of ZEN-garden.

Run 54 allows costs up to C* (1 + epsilon), epsilon = 1%. The cost limits keep a fraction
f of that slack: cost <= C* (1 + f epsilon), f = 20%, 10%, 5%, 1% (+0.2%, +0.1%, +0.05%,
+0.01% above C*; 50% changed nothing). The polytope's cost axis is scaled so that 0 = C* and 1 = C* (1 + epsilon), so each
limit is a ceiling f on that axis.

For each limit, industrial heat electrification, CCS utilisation and imported biomass in
2034 and 2050 get their min and max, next to the unconstrained near-optimal range (100%).
Each edge is one LP, as in fig61 (inner_bound / outer_bound from plot_mga_diffusion_whatif.py):
  wide light bar   outer approximation (cuts A z <= b): the widest the range can be
  narrow dark bar  convex hull of the solved designs: ranges certainly reachable
The true range lies between the two. Panel (d) shows the cost range reachable under each
limit in the same way, as a check (the upper end should sit on the limit).

Usage (zen-garden-plugins-env, PYTHONPATH=../ZEN-garden-plugins):
    python scripts/plot_mga_cost_limit.py [54|57 ...]   (default: both)
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
    AXIS_PREFIX, INK, MANDATE_COLOR, MUTED, S, TITLE, YEARS, YLABEL, extra_cost_bn, inner_bound,
    load_polytope, outer_bound, report_style, solve_all, style_axes, to_display,
)
from plots.mga_capex_periods_common import (
    METRIC_COLOR, MGA_ROOT, MODEL, RUN54_LABEL, RUN54_SUFFIX, RUN57_LABEL, RUN57_SUFFIX, savefig,
)

# run -> (run-folder suffix, label, figure name). Run 54 is the main version.
RUNS = {
    "54": (RUN54_SUFFIX, RUN54_LABEL, "fig62_cost_limit_effects"),
    "57": (RUN57_SUFFIX, RUN57_LABEL, "fig62_run57_cost_limit_effects"),
}
METRICS = ("heat", "ccs", "biomass")
GREY = SCENARIO_PALETTE[6]
# key -> (fraction of the cost slack kept, or None = no limit; ETH tint, None = grey).
# The tighter the limit, the darker the shade.
SCENARIO_DEF = {"free": (None, None), "20": (0.2, 0.7), "10": (0.1, 0.5), "5": (0.05, 0.25), "1": (0.01, 0.0)}
TICK_LABEL = {"free": "100", "20": "20", "10": "10", "5": "5", "1": "1"}  # % of the cost slack kept
PANEL_COLOR = {"heat": MANDATE_COLOR["heat"], "ccs": METRIC_COLOR["ccs"], "biomass": METRIC_COLOR["biomass"],
               "cost": INK}
OUTER_ALPHA = 0.3


def scenario_color(key: str, panel: str) -> str:
    tint = SCENARIO_DEF[key][1]
    if tint is None:
        return GREY
    return eth_tint(PANEL_COLOR[panel], tint) if tint else PANEL_COLOR[panel]


def scenario_labels(poly) -> dict[str, str]:
    labels = {"free": "100%: full near-optimal space (cost slack +1%)"}
    for key, (fraction, _) in SCENARIO_DEF.items():
        if fraction is not None:
            extra = extra_cost_bn(100 * fraction * poly.epsilon, poly.c_star)
            labels[key] = (f"{TICK_LABEL[key]}%: cost $\\leq$ +{100 * fraction * poly.epsilon:g}% "
                           f"(+{extra:,.0f} bn EUR) above $C^*$")
    return labels


def scenario_ranges(poly, axis_idx, fraction) -> dict:
    """{"inner"/"outer": ranges as from solve_all (None if the limit cannot be met)}."""
    ceilings = [] if fraction is None else [(poly.cost_col, fraction)]
    return {name: solve_all(poly, axis_idx, [], ceilings, bound, METRICS)
            for name, bound in (("inner", inner_bound), ("outer", outer_bound))}


def report(results: dict, labels: dict) -> None:
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


def _bar(ax, x, width, span, color, alpha, zorder):
    if span is not None:
        ax.bar(x, span[1] - span[0], bottom=span[0], width=width, color=color, alpha=alpha,
               edgecolor="white", linewidth=0.4, zorder=zorder)


def _bar_pair(ax, x, width, outer, inner, color, fmt, label_low=True):
    """Outer (wide, light) and inner (narrow, dark) bar with the inner limits labelled
    (only the upper one if label_low is False, none if it is None)."""
    _bar(ax, x, width * 0.9, outer, color, OUTER_ALPHA, 3)
    _bar(ax, x, width * 0.4, inner, color, 0.95, 4)
    if inner is not None and label_low is not None:
        edges = ((inner[0], "top", -2), (inner[1], "bottom", 2)) if label_low else ((inner[1], "bottom", 2),)
        for value, va, dy in edges:
            ax.annotate(fmt.format(value), (x, value), xytext=(0, dy), textcoords="offset points",
                        ha="center", va=va, fontsize=S["value"] - 1, color=INK, zorder=6)


def _finish(ax, ticks, labels, title, ylabel):
    ax.set_xticks(ticks, labels, fontsize=S["tick"] - 1)
    ax.use_sticky_edges = False
    ax.margins(y=0.08)
    ax.grid(axis="y", alpha=0.25)
    style_axes(ax, title, ylabel)
    ax.tick_params(axis="x", colors=INK)


def draw_metric(ax, poly, axis_idx, metric: str, results: dict, fmt: str, title: str) -> None:
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
            if outer is None:
                ax.text(x, 0, "x", ha="center", va="bottom", fontsize=8, color=MUTED)
                continue
            _bar_pair(ax, x, width, outer[metric, year], inner[metric, year] if inner else None,
                      scenario_color(key, metric), fmt)
        baseline = to_display(metric, poly.z_star_phys[axis_idx[f"{AXIS_PREFIX[metric]}_{year}"]])
        ax.plot([g - 0.45, g + 0.45], [baseline] * 2, color="black", linestyle="--", linewidth=1.0, zorder=5)
        ax.annotate(str(year), (g, 0), xycoords=("data", "axes fraction"), xytext=(0, -14),
                    textcoords="offset points", ha="center", va="top", fontsize=S["tick"], fontweight="bold",
                    color=INK)
    ax.set_xlim(-0.55, len(YEARS) - 0.45)
    _finish(ax, ticks, tick_labels, title, YLABEL[metric])
    ax.set_ylim(bottom=min(0, ax.get_ylim()[0]))


def draw_cost(ax, poly, results: dict, title: str) -> None:
    """Cost range reachable under each limit (outer / inner), with the limits as dotted lines."""
    slack = 100 * poly.epsilon
    keys = list(SCENARIO_DEF)
    for x, key in enumerate(keys):
        fraction = SCENARIO_DEF[key][0]
        limit = slack * (1.0 if fraction is None else fraction)
        ax.plot([x - 0.35, x + 0.35], [limit] * 2, color=INK, linewidth=0.8, linestyle=":", zorder=2)
        outer, inner = results[key]["outer"], results[key]["inner"]
        if outer is None:
            ax.text(x, slack / 2, "not\nreachable", ha="center", va="center", fontsize=S["value"], color=MUTED)
            continue
        inner_cost = inner["cost"] if inner else None
        _bar_pair(ax, x, 0.84, outer["cost"], inner_cost, scenario_color(key, "cost"), "", label_low=None)
        top = (inner_cost or outer["cost"])[1]
        ax.annotate(f"+{top:.2g}%\n+{extra_cost_bn(top, poly.c_star):,.0f} bn", (x, max(top, limit)),
                    xytext=(0, 2), textcoords="offset points", ha="center", va="bottom",
                    fontsize=S["value"] - 1, color=INK, zorder=6)
    ax.set_xlim(-0.6, len(keys) - 0.4)
    _finish(ax, range(len(keys)), [TICK_LABEL[key] for key in keys], title, "Cost above optimum")
    ax.set_ylim(0, slack * 1.2)
    ax.yaxis.set_major_formatter(lambda v, _: "$C^*$" if v == 0 else f"+{v:.1f}%")
    # Same axis in bn EUR above C* on the right.
    to_bn = 1e-3 * poly.c_star / 100
    right = ax.secondary_yaxis("right", functions=(lambda v: v * to_bn, lambda b: b / to_bn))
    right.tick_params(labelsize=S["tick"], colors=MUTED)
    right.set_ylabel("bn EUR above $C^*$", fontsize=S["label"], color=MUTED)
    right.spines["right"].set_color("#BBBBBB")
    ax.annotate("% of cost slack kept", (0.5, 0), xycoords="axes fraction", xytext=(0, -14),
                textcoords="offset points", ha="center", va="top", fontsize=S["tick"], fontweight="bold",
                color=INK)


def plot(run: str) -> None:
    suffix, run_label, figure_name = RUNS[run]
    print(f"\n=== run {run} ===")
    poly = load_polytope(MGA_ROOT / f"{MODEL}_{suffix}" / f"{MODEL}_batch_summary" / "polytope.npz")
    print(f"loaded {poly.X.shape[0]} points, converged={poly.converged}, C* = {poly.c_star:,.0f}, "
          f"epsilon = {poly.epsilon}")
    axis_idx = {name: i for i, name in enumerate(poly.names)}
    labels = scenario_labels(poly)
    results = {key: scenario_ranges(poly, axis_idx, fraction) for key, (fraction, _) in SCENARIO_DEF.items()}
    report(results, labels)

    with report_style():  # report figure: REPORT_WIDTH, report font sizes, 2 x 2 panels
        height = 6.0
        fig, axes = plt.subplots(2, 2, figsize=(REPORT_WIDTH, height))
        fig.subplots_adjust(left=0.1, right=0.93, top=0.95, bottom=1.35 / height, wspace=0.38, hspace=0.5)
        for ax, letter, metric, fmt in zip(axes.flat, "abc", METRICS, ("{:.0f}", "{:.0f}", "{:,.0f}")):
            draw_metric(ax, poly, axis_idx, metric, results, fmt, f"({letter}) {TITLE[metric]}")
        draw_cost(axes[1, 1], poly, results, "(d) Reachable cost")
        if SHOW_TITLE:
            fig.suptitle(f"ZEN-Europe MGA, {run_label}: cost slack tightened, effect on the axes",
                         fontsize=11, fontweight="bold", color=INK, x=0.1, ha="left")
        # The colour depends on the panel (darker = tighter limit, grey = none), so the
        # scenario entries carry no swatch.
        handles = [Line2D([0], [0], color="none", label=label) for label in labels.values()] + [
            Patch(facecolor=GREY, alpha=OUTER_ALPHA, label="Wide light bar: outer approximation"),
            Patch(facecolor=GREY, label="Narrow dark bar: hull of solved designs"),
            Line2D([0], [0], color="black", linestyle="--", linewidth=1.0, label="Cost-optimal baseline"),
            Line2D([0], [0], color=INK, linestyle=":", linewidth=0.8, label="Cost limit"),
        ]
        fig.legend(handles=handles, loc="lower center", ncol=2, fontsize=S["legend"], frameon=False,
                   bbox_to_anchor=(0.5, 0.0), handlelength=1.2, handletextpad=0.5, columnspacing=2.0)
        savefig(fig, figure_name)


def main() -> None:
    for run in sys.argv[1:] or list(RUNS):
        plot(run)


if __name__ == "__main__":
    main()
