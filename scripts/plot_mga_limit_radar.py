"""fig63 / fig64 / fig65: the results of fig61 / fig61a / fig61b (one axis limited to the top or
bottom 1% of its range) and fig62 (cost slack tightened) as radar charts, after Pickering et
al. (2022), Fig. 3B. No re-solving of ZEN-garden; the ranges come from the same LPs as in
plot_mga_heat_mandate.py and plot_mga_cost_limit.py.

One radar per scenario:
  main figures (fig63 / fig64), 3 x 2   (a) no limit, (b) heat at max (A), (c) heat at min (B),
                                        (d)-(f) cost limited to 10 / 5 / 1% of the cost slack; legend below
  appendix figures (fig63a / fig64a),   (a) no limit + legend, (b) / (c) CCS at max / min,
  2 x 3                                 (d) / (e) biomass at max / min
Panel (a) carries the key (spoke names, min / max). Seven spokes: heat, CCS and biomass in 2034 and 2050 (2050 in a lighter shade) and cost.
Radius: 0 (inner ring) = minimum and 1 (outer ring) = maximum of the unconstrained
near-optimal range (outer approximation) of that spoke; cost from C* (0) to C* (1 + epsilon).
Each spoke carries the two ranges as in fig61/62:
  wide light bar   outer approximation (cuts A z <= b)
  narrow dark bar  convex hull of the solved designs
The cost-optimal design is not drawn. The limited spokes carry one coloured arc at the
limited end instead of the two bars: their range is the limit itself, the same for outer
approximation and hull. The arc is at least LIMIT_ARC thick (the 1% limits are drawn thicker).

fig63_limit_radar        run 54, the main run (as fig61 / fig61a / fig61b / fig62)
fig63a_limit_radar_ccs_biomass
                         appendix: the CCS and biomass limits of run 54
fig64_run56_57_limit_radar
                         tolerance sensitivity: run 56 (tolerance 0.1) filled, run 57
                         (tolerance 0.01) as dashed outlines, both scaled to run 56's range
fig64a_run56_57_limit_radar_ccs_biomass
                         appendix: the CCS and biomass limits of the same comparison
fig65_run56_57_limit_matrix
                         the same comparison as a matrix (scenario x spoke): shift of the
                         lower / upper end from run 56 to run 57 in % of run 56's unconstrained
                         range; fill = the range gets wider (green), narrower (red) or stays
                         within +-0.5 (grey). Panel (a) outer approximation, (b) hull. All scenarios,
                         including the 20% cost limit.

Usage (zen-garden-plugins-env, PYTHONPATH=../ZEN-garden-plugins):
    python scripts/plot_mga_limit_radar.py [63 63a 64 64a 65]   (default: all)
"""

import sys

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.patches import Patch, Rectangle

from plots.figure_settings import REPORT_WIDTH, SCENARIO_PALETTE, apply_font_mode, eth_tint

apply_font_mode()

import plot_mga_cost_limit as cost_limit
import plot_mga_heat_mandate as heat_mandate
from plot_mga_diffusion_whatif import (
    INK, MUTED, S, YEARS, extra_cost_bn, load_polytope, report_style,
)
from plots.mga_capex_periods_common import (
    MGA_ROOT, MODEL, RUN54_SUFFIX, RUN56_SUFFIX, RUN57_SUFFIX, savefig,
)

RUN_SUFFIX = {"54": RUN54_SUFFIX, "56": RUN56_SUFFIX, "57": RUN57_SUFFIX}
RUN_TOLERANCE = {"56": "0.1", "57": "0.01"}
METRICS = ("heat", "ccs", "biomass")
GREY = heat_mandate.GREY

# Spokes clockwise from the top: (metric, year), and cost.
SPOKES = [(m, y) for m in METRICS for y in YEARS] + ["cost"]
N_SPOKES = len(SPOKES)
STEP = 2 * np.pi / N_SPOKES
THETA = {spoke: i * STEP for i, spoke in enumerate(SPOKES)}
LATE_TINT = 0.45  # 2050 spokes: lighter shade of the technology colour
NAME = {"heat": "Heat", "ccs": "CCS", "biomass": "Biomass", "cost": "Cost"}
SPOKE_LABEL = {s: f"{NAME[s[0]]}\n{s[1]}" for s in SPOKES if s != "cost"} | {"cost": "Cost"}
R_ORIGIN = 0.28  # radius of the empty centre, in units of the scaled range
OUTER_WIDTH, INNER_WIDTH = 0.5 * STEP, 0.2 * STEP
OUTER_ALPHA = heat_mandate.OUTER_ALPHA
LIMIT_ARC = 0.03  # minimum thickness of the limit arc, in units of the scaled range (limits are 0.01 wide)
MIN_BAR = 0.03  # minimum radial bar length, in units of the scaled range
OVERLAY_LW = 0.7  # dashed outlines of the comparison run

# Scenarios: "free", (limited axis, "A"/"B"), ("cost", key of cost_limit.SCENARIO_DEF).
LIMIT_KEYS = [(m, k) for k in ("A", "B") for m in METRICS]
COST_KEYS = [("cost", k) for k in cost_limit.SCENARIO_DEF if k != "free"]
SCENARIOS = ["free", *LIMIT_KEYS, *COST_KEYS]  # all solved; fig65 shows all of them
# Radar figures, in panel order (three per row).
# Radar figures: rows of panels ("legend" = the legend in that cell; no "legend" = legend below the grid).
MAIN_LAYOUT = [["free", ("heat", "A"), ("heat", "B")], [("cost", k) for k in ("10", "5", "1")]]
APPENDIX_LAYOUT = [["free", "legend"], [("ccs", "A"), ("ccs", "B")], [("biomass", "A"), ("biomass", "B")]]


def spoke_color(spoke) -> str:
    if spoke == "cost":
        return INK
    metric, year = spoke
    color = heat_mandate.PANEL_COLOR[metric]
    return eth_tint(color, LATE_TINT) if year != YEARS[0] else color


class Run:
    """One MGA run: its polytope and the ranges of all scenarios (solved on creation)."""

    def __init__(self, run: str):
        self.run = run
        self.poly = load_polytope(MGA_ROOT / f"{MODEL}_{RUN_SUFFIX[run]}" / f"{MODEL}_batch_summary" / "polytope.npz")
        self.idx = {name: i for i, name in enumerate(self.poly.names)}
        print(f"run {run}: {self.poly.X.shape[0]} points, C* = {self.poly.c_star:,.0f}, eps = {self.poly.epsilon}")
        p, idx = self.poly, self.idx
        self.results = {"free": heat_mandate.scenario_ranges(p, idx, "heat", None)}
        for limited, key in LIMIT_KEYS:
            self.results[limited, key] = heat_mandate.scenario_ranges(
                p, idx, limited, heat_mandate.SCENARIO_DEF[key][0])
        for _, key in COST_KEYS:
            self.results["cost", key] = cost_limit.scenario_ranges(p, idx, cost_limit.SCENARIO_DEF[key][0])


class Scale:
    """Scaled radius per spoke: 0/1 = min/max of a run's unconstrained outer range."""

    def __init__(self, run: Run):
        free = run.results["free"]["outer"]
        self.span = {spoke: free[spoke] for spoke in SPOKES if spoke != "cost"}
        self.span["cost"] = (0.0, 100 * run.poly.epsilon)

    def __call__(self, spoke, value: float, clip: bool = True) -> float:
        lo, hi = self.span[spoke]
        r = (value - lo) / (hi - lo) if hi > lo else 1.0
        return float(np.clip(r, 0.0, 1.0)) if clip else float(r)


# ---------------------------------------------------------------- radar drawing

def style_radar(ax, labels: bool = False) -> None:
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rorigin(-R_ORIGIN)
    ax.set_ylim(0, 1)
    ax.set_xticks([THETA[s] for s in SPOKES])
    ax.set_xticklabels([SPOKE_LABEL[s] for s in SPOKES] if labels else [])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels([])
    ax.grid(color="#CCCCCC", linewidth=0.5)
    for ring in ("polar", "inner"):
        ax.spines[ring].set_color("#BBBBBB")
        ax.spines[ring].set_linewidth(0.6)
    ax.tick_params(pad=1)


def radar_title(ax, title: str, subtitle: str = "", lift: float = 0) -> None:
    """lift: extra space (points) above the radar, e.g. for the spoke labels of the key panel."""
    ax.set_title(title, fontsize=S["title"] - 1, fontweight="bold", color=INK, pad=(13 if subtitle else 6) + lift)
    if subtitle:
        ax.annotate(subtitle, (0.5, 1.0), xycoords="axes fraction", xytext=(0, 4 + lift), textcoords="offset points",
                    ha="center", va="bottom", fontsize=S["value"], color=MUTED)


def _radial_span(scale, spoke, span) -> tuple[float, float]:
    """(bottom, height) of a radial bar, at least MIN_BAR long."""
    lo, hi = (scale(spoke, v) for v in span)
    height = max(hi - lo, MIN_BAR)
    return min(lo, 1 - height), height


def draw_limit_arc(ax, scenario, scale: Scale, result) -> None:
    """One coloured arc across the limited spokes, at the limited end (max: outer ring, else inner ring)."""
    limited = limited_spokes(scenario)
    thetas = [THETA[s] for s in limited]
    lo, hi = (scale(limited[0], v) for v in result[limited[0]])
    height = max(hi - lo, LIMIT_ARC)
    ax.bar(np.mean(thetas), height, bottom=min(lo, 1 - height), width=STEP * (len(thetas) - 1) + 0.8 * STEP,
           color=spoke_color(limited[0]), linewidth=0, zorder=4)


def draw_radar(ax, run: Run, scenario, scale: Scale) -> None:
    """Filled bars of one run, and the limit arc on the limited spokes."""
    style_radar(ax)
    outer, inner = run.results[scenario]["outer"], run.results[scenario]["inner"]
    if outer is None:
        ax.text(0, -R_ORIGIN, "not\nreachable", ha="center", va="center", fontsize=S["value"], color=MUTED)
        return
    limited = limited_spokes(scenario)
    if limited:
        draw_limit_arc(ax, scenario, scale, outer)
    for spoke in SPOKES:
        theta, color = THETA[spoke], spoke_color(spoke)
        for result, width, alpha, z in ((outer, OUTER_WIDTH, OUTER_ALPHA, 3), (inner, INNER_WIDTH, 0.95, 4)):
            if result is not None and spoke not in limited:
                bottom, height = _radial_span(scale, spoke, result[spoke])
                ax.bar(theta, height, bottom=bottom, width=width, color=color, alpha=alpha, linewidth=0, zorder=z)
    if inner is None:  # the outer approximation allows the limit, but no solved design meets it
        ax.text(0, -R_ORIGIN, "no\nhull", ha="center", va="center", fontsize=S["value"] - 1.5, color=MUTED,
                zorder=7)


def draw_overlay(ax, run: Run, scenario, scale: Scale) -> None:
    """Dashed outlines of a comparison run's bars and baseline."""
    outer, inner = run.results[scenario]["outer"], run.results[scenario]["inner"]
    if outer is None:
        ax.text(0, -R_ORIGIN, "\n\n\n(not reachable,\ndashed run)", ha="center", va="center",
                fontsize=S["value"] - 1, color=MUTED)
        return
    for spoke in SPOKES:
        theta = THETA[spoke]
        for result, width in ((outer, OUTER_WIDTH), (inner, INNER_WIDTH)):
            if result is not None and spoke not in limited_spokes(scenario):  # same limit in both runs
                bottom, height = _radial_span(scale, spoke, result[spoke])
                ax.bar(theta, height, bottom=bottom, width=width, fill=False, edgecolor=INK, linewidth=OVERLAY_LW,
                       linestyle=(0, (2.5, 1.5)), zorder=6)


def limit_subtitle(run: Run, limited: str, band) -> str:
    unit = heat_mandate.LIMITED_UNIT[limited].strip()
    texts = []
    for year in YEARS:
        lo, hi = heat_mandate.physical_band(run.poly, run.idx, limited, year, band)
        digits = 1 if round(lo) == round(hi) else 0
        texts.append(f"{lo:,.{digits}f}-{hi:,.{digits}f}")
    return f"{texts[0]} {unit}" if len(set(texts)) == 1 else f"{' / '.join(texts)} {unit}"


def scenario_title(scenario, run: Run, letter: str) -> tuple[str, str]:
    if scenario == "free":
        return f"({letter}) No limit", "near-optimal space"
    axis, key = scenario
    if axis == "cost":
        percent = 100 * cost_limit.SCENARIO_DEF[key][0] * run.poly.epsilon
        return (f"({letter}) Cost $\\leq$ +{percent:g}%",
                f"+{extra_cost_bn(percent, run.poly.c_star):,.0f} bn EUR above $C^*$")
    which = "max" if key == "A" else "min"
    return f"({letter}) {NAME[axis]} at {which}", limit_subtitle(run, axis, heat_mandate.SCENARIO_DEF[key][0])


def limited_spokes(scenario) -> list:
    if scenario == "free":
        return []
    return ["cost"] if scenario[0] == "cost" else [(scenario[0], y) for y in YEARS]


KEY_LIFT = 15  # points: room for the "Heat 2034" spoke label above panel (a)


def add_key(ax) -> None:
    """Spoke names and the radial scale (min / max) on a radar (panel (a))."""
    ax.set_xticklabels([SPOKE_LABEL[s] for s in SPOKES])
    ax.tick_params(axis="x", labelsize=S["value"] - 1, pad=3)
    for label, spoke in zip(ax.get_xticklabels(), SPOKES):
        label.set_color(INK if spoke == "cost" else heat_mandate.PANEL_COLOR[spoke[0]])
        label.set_linespacing(0.95)
    theta = THETA["cost"] + STEP / 2
    for r, text in ((0, "min"), (1, "max")):
        ax.text(theta, r, text, ha="center", va="center", fontsize=S["value"] - 2, color=MUTED, zorder=7,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.2))


def legend_handles(extra_handles: list) -> list:
    return [
        Patch(facecolor=GREY, alpha=OUTER_ALPHA, label="Outer approximation\n(wide light bar)"),
        Patch(facecolor=GREY, label="Hull of solved designs\n(narrow dark bar)"),
        Patch(facecolor=INK, label="Imposed limit\n(coloured arc)"),
        *extra_handles,
    ]


def radar_grid(name: str, layout: list, run: Run, scale: Scale, extra_handles: list = (),
               overlay: Run | None = None, overlay_scale: Scale | None = None) -> None:
    """Radars in the rows of `layout`, lettered row by row; overlay drawn dashed on top, if given."""
    n_rows, n_cols = len(layout), max(len(row) for row in layout)
    legend_in_cell = any("legend" in row for row in layout)
    handles = legend_handles(list(extra_handles))
    side = 0.08 if n_cols == 3 else 0.18  # horizontal margin; 2 columns: radars slightly larger than with 3
    cell = 1.95
    legend_h = 0 if legend_in_cell else 0.1 + 0.33 * -(-len(handles) // n_cols)
    height = n_rows * cell + legend_h + 0.25
    with report_style():
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(REPORT_WIDTH, height), subplot_kw={"projection": "polar"},
                                 squeeze=False)
        fig.subplots_adjust(left=side, right=1 - side, top=1 - 0.75 / height,
                            bottom=(legend_h + (0.3 if legend_in_cell else 0.2)) / height, wspace=0.6 if n_cols == 3 else 0.45, hspace=0.45)
        legend_kw = dict(handles=handles, fontsize=S["legend"] - 0.5, frameon=False,
                         handlelength=1.3, handletextpad=0.5, labelspacing=0.7)
        letters = iter("abcdefghijk")
        for i, row in enumerate(layout):
            for j in range(n_cols):
                ax = axes[i, j]
                scenario = row[j] if j < len(row) else None
                if scenario is None or scenario == "legend":
                    ax.set_visible(False)
                    if scenario == "legend":
                        pos = ax.get_position()
                        fig.legend(loc="center", bbox_to_anchor=(pos.x0 + pos.width / 2, pos.y0 + pos.height / 2),
                                   ncol=1, **legend_kw)
                    continue
                draw_radar(ax, run, scenario, scale)
                if overlay is not None:
                    draw_overlay(ax, overlay, scenario, overlay_scale)
                if scenario == "free":
                    add_key(ax)
                lift = KEY_LIFT if "free" in row else 0  # same title height across the row of (a)
                radar_title(ax, *scenario_title(scenario, run, next(letters)), lift=lift)
        if not legend_in_cell:
            fig.legend(loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=n_cols, columnspacing=1.5, **legend_kw)
        savefig(fig, name)


def fig63(runs, layout=MAIN_LAYOUT, name="fig63_limit_radar") -> None:
    r54 = runs("54")
    radar_grid(name, layout, r54, Scale(r54))


def fig63a(runs) -> None:
    fig63(runs, APPENDIX_LAYOUT, "fig63a_limit_radar_ccs_biomass")


def fig64(runs, layout=MAIN_LAYOUT, name="fig64_run56_57_limit_radar") -> None:
    r56, r57 = runs("56"), runs("57")
    handles = [
        Patch(facecolor=GREY, label=f"Filled: test run 1\n(tolerance {RUN_TOLERANCE['56']})"),
        Patch(facecolor="none", edgecolor=INK, linewidth=OVERLAY_LW, linestyle=(0, (2.5, 1.5)),
              label=f"Dashed: test run 2\n(tolerance {RUN_TOLERANCE['57']})"),
    ]
    radar_grid(name, layout, r56, Scale(r56), handles, overlay=r57, overlay_scale=Scale(r56))


def fig64a(runs) -> None:
    fig64(runs, APPENDIX_LAYOUT, "fig64a_run56_57_limit_radar_ccs_biomass")


# ---------------------------------------------------------------- fig65: difference matrix

MATRIX_SAME = 0.5  # |change of range width| below this (% of the unconstrained range) counts as unchanged
MATRIX_FILL = {"same": eth_tint(SCENARIO_PALETTE[6], 0.72), "wider": eth_tint(SCENARIO_PALETTE[2], 0.55),
               "narrower": eth_tint(SCENARIO_PALETTE[4], 0.55), "n/a": "white"}


def matrix_rows(scenario, run: Run, letter: str) -> str:
    title, subtitle = scenario_title(scenario, run, letter)
    return title.split(") ", 1)[1] + ("" if scenario == "free" else f"  ({subtitle})")


def range_changes(ref: Run, other: Run, scale: Scale, which: str) -> dict:
    """{(scenario, spoke): (d_low, d_high) in % of ref's unconstrained range, or None}."""
    out = {}
    for scenario in SCENARIOS:
        a, b = ref.results[scenario][which], other.results[scenario][which]
        for spoke in SPOKES:
            if a is None or b is None:
                out[scenario, spoke] = None
                continue
            lo_a, hi_a = (scale(spoke, v, clip=False) for v in a[spoke])
            lo_b, hi_b = (scale(spoke, v, clip=False) for v in b[spoke])
            out[scenario, spoke] = (100 * (lo_b - lo_a), 100 * (hi_b - hi_a))
    return out


def draw_matrix(ax, changes: dict, row_labels: list, title: str) -> None:
    n_rows, n_cols = len(SCENARIOS), len(SPOKES)
    for i, scenario in enumerate(SCENARIOS):
        for j, spoke in enumerate(SPOKES):
            change = changes[scenario, spoke]
            if change is None:
                kind, text = "n/a", "n/a"
            else:
                d_lo, d_hi = change
                d_width = d_hi - d_lo
                kind = "same" if abs(d_width) < MATRIX_SAME else ("wider" if d_width > 0 else "narrower")
                parts = ["0" if abs(d) < MATRIX_SAME else f"{d:+.0f}" for d in (d_lo, d_hi)]
                text = "0" if parts == ["0", "0"] else " / ".join(parts)
            ax.add_patch(Rectangle((j, i), 1, 1, facecolor=MATRIX_FILL[kind], edgecolor="white", linewidth=1.2))
            ax.text(j + 0.5, i + 0.5, text, ha="center", va="center", fontsize=S["value"] - 0.5,
                    color=MUTED if kind == "n/a" else "black")
    for i in (1, 1 + len(LIMIT_KEYS)):  # separate no limit / axis limits / cost limits
        ax.axhline(i, color=INK, linewidth=0.8)
    ax.set_xlim(0, n_cols)
    ax.set_ylim(n_rows, 0)
    ax.set_xticks(np.arange(n_cols) + 0.5, [SPOKE_LABEL[s] for s in SPOKES], fontsize=S["tick"] - 0.5)
    ax.xaxis.tick_top()
    for label, spoke in zip(ax.get_xticklabels(), SPOKES):
        label.set_color(INK if spoke == "cost" else heat_mandate.PANEL_COLOR[spoke[0]])
    ax.set_yticks(np.arange(n_rows) + 0.5, row_labels, fontsize=S["tick"] - 0.5, color=INK)
    ax.tick_params(length=0, pad=2)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(title, fontsize=S["title"], fontweight="bold", color=INK, loc="left", pad=24)


def fig65(runs) -> None:
    r56, r57 = runs("56"), runs("57")
    s56 = Scale(r56)
    rows = [matrix_rows(s, r56, l) for l, s in zip("abcdefghijk", SCENARIOS)]
    print("\nfig65: change run 56 -> 57, % of run 56's unconstrained range (d_low, d_high)")
    for which in ("outer", "inner"):
        for (scenario, spoke), change in range_changes(r56, r57, s56, which).items():
            if change and max(abs(change[0]), abs(change[1])) >= MATRIX_SAME:
                print(f"  {which:5s} {str(scenario):18s} {str(spoke):18s} {change[0]:+7.1f} {change[1]:+7.1f}")
    with report_style():
        height = 7.6
        fig, axes = plt.subplots(2, 1, figsize=(REPORT_WIDTH, height))
        fig.subplots_adjust(left=0.36, right=0.99, top=0.93, bottom=0.75 / height, hspace=0.32)
        for ax, which, title in zip(axes, ("outer", "inner"),
                                    ("(a) Outer approximation", "(b) Hull of solved designs")):
            draw_matrix(ax, range_changes(r56, r57, s56, which), rows, title)
        handles = [Patch(facecolor=MATRIX_FILL["wider"], label="range wider in run 57"),
                   Patch(facecolor=MATRIX_FILL["narrower"], label="range narrower in run 57"),
                   Patch(facecolor=MATRIX_FILL["same"], label=f"width within $\\pm${MATRIX_SAME:g}")]
        fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=S["legend"], frameon=False,
                   bbox_to_anchor=(0.5, 0.25 / height), handlelength=1.2, columnspacing=1.5)
        fig.text(0.5, 0.0, "Cell: shift of the lower / upper end from run 56 (tolerance 0.1) to run 57 "
                 "(tolerance 0.01), in % of run 56's unconstrained range (cost: of the cost slack).",
                 ha="center", va="bottom", fontsize=S["legend"] - 1, color=MUTED)
        savefig(fig, "fig65_run56_57_limit_matrix")


FIGURES = {"63": fig63, "63a": fig63a, "64": fig64, "64a": fig64a, "65": fig65}


def main() -> None:
    cache = {}

    def runs(run: str) -> Run:
        if run not in cache:
            cache[run] = Run(run)
        return cache[run]

    for fig in sys.argv[1:] or FIGURES:
        FIGURES[fig](runs)


if __name__ == "__main__":
    main()
