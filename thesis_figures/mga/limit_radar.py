"""Near-optimal ranges under additional limits as radar charts (thesis Fig. 7, A6, A7, A11).

One radar per limit scenario, after Pickering et al. (2022), Fig. 3B. Seven spokes: the
electrification share of industrial heat, CO2 storage utilisation and imported biomass in
2034 and 2050 (2050 in a lighter shade), and the total system cost. Radius 0 (inner
ring) / 1 (outer ring) = the run's normalised axis values 0 / 1, i.e. the axis's own minimum /
maximum from the min/max solves (identical to the unconstrained outer and inner ranges, which
contain these solves); cost from C* to C* (1 + epsilon). Each spoke carries two ranges:

  wide light bar   outer approximation
  narrow dark bar  convex hull of the solved designs (inner approximation)

Limited spokes carry one coloured arc at the limited end instead (the range is the limit
itself), at least LIMIT_ARC thick. Main figures: (a) no limit, (b)/(c) heat electrification
at its maximum / minimum, (d)-(f) cost limited to 10 / 5 / 1 % of the cost slack. Main run
T1 only, Fig. A6: (a) no limit and legend, (b)-(e) CO2 storage and biomass at max / min.
The comparison figures use the main layout with a second run as dashed outlines, both on
the filled run's scale: Fig. A7 test run 1 (T2) filled, test run 2 (T3) dashed; Fig. A11
T4 (cost slack 0.2 %) filled, T3 (cost slack 1 %) dashed. In A11, wider T3 bars are clipped
at the outer ring (T3's cost spoke fills it), and the cost panels limit each run to the same
fraction of its own slack, i.e. a different absolute cost.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

from ..style import ETH_BLUE, ETH_GREEN, ETH_GREY, ETH_PURPLE, REPORT_WIDTH, eth_tint, save_figure
from .polytope import (
    AXIS_LIMITS,
    AXIS_PREFIX,
    COST_LIMITS,
    LIMITED_UNIT,
    METRICS,
    RUN_TOLERANCE,
    YEARS,
    MgaRun,
    extra_cost_bn,
    physical_band,
    to_display,
)

INK, MUTED = "#333333", "#6F6F6F"
GREY = ETH_GREY
METRIC_COLOR = {"heat": ETH_PURPLE, "ccs": ETH_BLUE, "biomass": ETH_GREEN}
SIZE = dict(title=9.5, value=7, legend=8)  # font sizes

SPOKES = [(m, y) for m in METRICS for y in YEARS] + ["cost"]  # clockwise from the top
N_SPOKES = len(SPOKES)
STEP = 2 * np.pi / N_SPOKES
THETA = {spoke: i * STEP for i, spoke in enumerate(SPOKES)}
LATE_TINT = 0.45  # 2050 spokes: lighter shade of the technology colour
NAME = {"heat": "Heat", "ccs": "CCS", "biomass": "Biomass", "cost": "Cost"}
SPOKE_LABEL = {s: f"{NAME[s[0]]}\n{s[1]}" for s in SPOKES if s != "cost"} | {"cost": "Cost"}
R_ORIGIN = 0.28  # radius of the empty centre, in units of the scaled range
OUTER_WIDTH, INNER_WIDTH = 0.5 * STEP, 0.2 * STEP
OUTER_ALPHA = 0.3
LIMIT_ARC = 0.03  # minimum thickness of the limit arc, in units of the scaled range (limits are 0.01 wide)
MIN_BAR = 0.03  # minimum radial bar length, in units of the scaled range
OVERLAY_LW = 0.7  # dashed outlines of the comparison run
OVERLAY_DASH = (0, (2.5, 1.5))
KEY_LIFT = 15  # points: room for the spoke labels above panel (a)

# Panel layouts, row by row ("legend" = the legend in that cell; without, legend below the grid).
MAIN_LAYOUT = [["free", ("heat", "A"), ("heat", "B")], [("cost", k) for k in ("10", "5", "1")]]
APPENDIX_LAYOUT = [["free", "legend"], [("ccs", "A"), ("ccs", "B")], [("biomass", "A"), ("biomass", "B")]]


def spoke_color(spoke) -> str:
    if spoke == "cost":
        return INK
    metric, year = spoke
    color = METRIC_COLOR[metric]
    return eth_tint(color, LATE_TINT) if year != YEARS[0] else color


class Scale:
    """Scaled radius per spoke: the run's normalised axis value (0 / 1 = own min / max solve)."""

    def __init__(self, run: MgaRun):
        p = run.poly
        self.span = {"cost": (0.0, 100 * p.epsilon)}
        for metric, year in SPOKES[:-1]:
            k = run.idx[f"{AXIS_PREFIX[metric]}_{year}"]
            self.span[metric, year] = (to_display(metric, p.offset[k]), to_display(metric, p.offset[k] + p.scale[k]))

    def __call__(self, spoke, value: float, clip: bool = True) -> float:
        lo, hi = self.span[spoke]
        r = (value - lo) / (hi - lo) if hi > lo else 1.0
        return float(np.clip(r, 0.0, 1.0)) if clip else float(r)


def limited_spokes(scenario) -> list:
    if scenario == "free":
        return []
    return ["cost"] if scenario[0] == "cost" else [(scenario[0], y) for y in YEARS]


def style_radar(ax) -> None:
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rorigin(-R_ORIGIN)
    ax.set_ylim(0, 1)
    ax.set_xticks([THETA[s] for s in SPOKES])
    ax.set_xticklabels([])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels([])
    ax.grid(color="#CCCCCC", linewidth=0.5)
    for ring in ("polar", "inner"):
        ax.spines[ring].set_color("#BBBBBB")
        ax.spines[ring].set_linewidth(0.6)
    ax.tick_params(pad=1)


def radar_title(ax, title: str, subtitle: str = "", lift: float = 0) -> None:
    """lift: extra space (points) above the radar, e.g. for the spoke labels of the key panel."""
    ax.set_title(title, fontsize=SIZE["title"] - 1, fontweight="bold", color=INK, pad=(13 if subtitle else 6) + lift)
    if subtitle:
        ax.annotate(subtitle, (0.5, 1.0), xycoords="axes fraction", xytext=(0, 4 + lift), textcoords="offset points",
                    ha="center", va="bottom", fontsize=SIZE["value"], color=MUTED)


def _radial_span(scale, spoke, span) -> tuple[float, float]:
    """(bottom, height) of a radial bar, at least MIN_BAR long."""
    lo, hi = (scale(spoke, v) for v in span)
    height = max(hi - lo, MIN_BAR)
    return min(lo, 1 - height), height


def draw_limit_arc(ax, scenario, scale: Scale, result) -> None:
    """One coloured arc across the limited spokes, at the limited end."""
    limited = limited_spokes(scenario)
    thetas = [THETA[s] for s in limited]
    lo, hi = (scale(limited[0], v) for v in result[limited[0]])
    height = max(hi - lo, LIMIT_ARC)
    ax.bar(np.mean(thetas), height, bottom=min(lo, 1 - height), width=STEP * (len(thetas) - 1) + 0.8 * STEP,
           color=spoke_color(limited[0]), linewidth=0, zorder=4)


def draw_radar(ax, run: MgaRun, scenario, scale: Scale) -> None:
    """Filled bars of one run, and the limit arc on the limited spokes."""
    style_radar(ax)
    outer, inner = run.results[scenario]["outer"], run.results[scenario]["inner"]
    if outer is None:
        ax.text(0, -R_ORIGIN, "not\nreachable", ha="center", va="center", fontsize=SIZE["value"], color=MUTED)
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
        ax.text(0, -R_ORIGIN, "no\nhull", ha="center", va="center", fontsize=SIZE["value"] - 1.5, color=MUTED,
                zorder=7)


def draw_overlay(ax, run: MgaRun, scenario, scale: Scale) -> None:
    """Dashed outlines of a comparison run's bars (limited spokes: same limit in both runs)."""
    outer, inner = run.results[scenario]["outer"], run.results[scenario]["inner"]
    if outer is None:
        ax.text(0, -R_ORIGIN, "\n\n\n(not reachable,\ndashed run)", ha="center", va="center",
                fontsize=SIZE["value"] - 1, color=MUTED)
        return
    for spoke in SPOKES:
        theta = THETA[spoke]
        for result, width in ((outer, OUTER_WIDTH), (inner, INNER_WIDTH)):
            if result is not None and spoke not in limited_spokes(scenario):
                bottom, height = _radial_span(scale, spoke, result[spoke])
                ax.bar(theta, height, bottom=bottom, width=width, fill=False, edgecolor=INK, linewidth=OVERLAY_LW,
                       linestyle=OVERLAY_DASH, zorder=6)


def limit_subtitle(run: MgaRun, limited: str, band) -> str:
    unit = LIMITED_UNIT[limited]
    texts = []
    for year in YEARS:
        lo, hi = physical_band(run.poly, run.idx, limited, year, band)
        digits = 1 if round(lo) == round(hi) else 0
        texts.append(f"{lo:,.{digits}f}-{hi:,.{digits}f}")
    return f"{texts[0]} {unit}" if len(set(texts)) == 1 else f"{' / '.join(texts)} {unit}"


def scenario_title(scenario, run: MgaRun, letter: str) -> tuple[str, str]:
    if scenario == "free":
        return f"({letter}) No limit", "near-optimal space"
    axis, key = scenario
    if axis == "cost":
        percent = 100 * COST_LIMITS[key] * run.poly.epsilon
        return (f"({letter}) Cost $\\leq$ +{percent:g}%",
                f"+{extra_cost_bn(percent, run.poly.c_star):,.0f} bn EUR above $C^*$")
    which = "max" if key == "A" else "min"
    return f"({letter}) {NAME[axis]} at {which}", limit_subtitle(run, axis, AXIS_LIMITS[key])


def add_key(ax) -> None:
    """Spoke names and the radial scale (min / max) on panel (a)."""
    ax.set_xticklabels([SPOKE_LABEL[s] for s in SPOKES])
    ax.tick_params(axis="x", labelsize=SIZE["value"] - 1, pad=3)
    for label, spoke in zip(ax.get_xticklabels(), SPOKES):
        label.set_color(INK if spoke == "cost" else METRIC_COLOR[spoke[0]])
        label.set_linespacing(0.95)
    theta = THETA["cost"] + STEP / 2
    for r, text in ((0, "min"), (1, "max")):
        ax.text(theta, r, text, ha="center", va="center", fontsize=SIZE["value"] - 2, color=MUTED, zorder=7,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.2))


def legend_handles(extra_handles: list) -> list:
    return [
        Patch(facecolor=GREY, alpha=OUTER_ALPHA, label="Outer approximation\n(wide light bar)"),
        Patch(facecolor=GREY, label="Hull of solved designs\n(narrow dark bar)"),
        Patch(facecolor=INK, label="Imposed limit\n(coloured arc)"),
        *extra_handles,
    ]


def radar_grid(name: str, layout: list, run: MgaRun, scale: Scale, extra_handles: list = (),
               overlay: MgaRun | None = None, overlay_scale: Scale | None = None) -> None:
    """Radars in the rows of `layout`, lettered row by row; `overlay` drawn dashed on top."""
    n_rows, n_cols = len(layout), max(len(row) for row in layout)
    legend_in_cell = any("legend" in row for row in layout)
    handles = legend_handles(list(extra_handles))
    side = 0.08 if n_cols == 3 else 0.18  # horizontal margin; 2 columns: radars slightly larger
    cell = 1.95
    legend_h = 0 if legend_in_cell else 0.1 + 0.33 * -(-len(handles) // n_cols)
    height = n_rows * cell + legend_h + 0.25
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(REPORT_WIDTH, height), subplot_kw={"projection": "polar"},
                             squeeze=False)
    fig.subplots_adjust(left=side, right=1 - side, top=1 - 0.75 / height,
                        bottom=(legend_h + (0.3 if legend_in_cell else 0.2)) / height,
                        wspace=0.6 if n_cols == 3 else 0.45, hspace=0.45)
    legend_kw = dict(handles=handles, fontsize=SIZE["legend"] - 0.5, frameon=False,
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
    save_figure(fig, name, dpi=200)


def main_run_radar(name: str, appendix: bool = False) -> None:
    """Main run T1."""
    run = MgaRun("T1")
    radar_grid(name, APPENDIX_LAYOUT if appendix else MAIN_LAYOUT, run, Scale(run))


def overlay_radar(name: str, filled_id: str, dashed_id: str, labels: tuple[str, str]) -> None:
    """Run `filled_id` filled, run `dashed_id` dashed, both on the filled run's scale."""
    filled, dashed = MgaRun(filled_id), MgaRun(dashed_id)
    handles = [
        Patch(facecolor=GREY, label=f"Filled: {labels[0]}"),
        Patch(facecolor="none", edgecolor=INK, linewidth=OVERLAY_LW, linestyle=OVERLAY_DASH,
              label=f"Dashed: {labels[1]}"),
    ]
    scale = Scale(filled)
    radar_grid(name, MAIN_LAYOUT, filled, scale, handles, overlay=dashed, overlay_scale=scale)


def test_runs_radar(name: str) -> None:
    """Test run 1 (T2) filled, test run 2 (T3) dashed, both on T2's scale."""
    overlay_radar(name, "T2", "T3", (f"test run 1\n(tolerance {RUN_TOLERANCE['T2']})",
                                     f"test run 2\n(tolerance {RUN_TOLERANCE['T3']})"))


def cost_slack_radar(name: str) -> None:
    """T4 (cost slack 0.2 %) filled, test run 2 (T3, cost slack 1 %) dashed, both on T4's scale."""
    overlay_radar(name, "T4", "T3", (f"cost slack 0.2%\n(tolerance {RUN_TOLERANCE['T4']})",
                                     "test run 2\n(cost slack 1%)"))
