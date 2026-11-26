"""Flexibility scenarios compared with ZEN-Europe as a table (thesis Fig. A3).

Metrics as rows, scenarios as columns (ZEN-Europe-No-Flex right of a dashed line). Each
cell gives the absolute value and its difference to ZEN-Europe (absolute and in %; pp for
the heat-pump share), shaded by that difference (increase green, decrease red), scaled
per row to its largest difference: cost changes by about 0.1 %, DSM and TES discharge by
up to 100 %, so a shared scale would leave most cells white.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

from ..results import Run
from ..style import ETH_GREEN, ETH_RED, REPORT_WIDTH, eth_tint, save_figure
from .flexibility_matrix import MATRIX_STYLE
from .metrics import METRICS_YEAR, flexibility_metrics_with_curtailment
from .scenarios import FULL, NO_DSM, NO_FLEX, NO_TES, NO_TES_DSM_PESS

# Rows: metric -> (title, unit of the difference, number format); the heat-pump share
# itself is in %.
ROWS = {"cost": ("Total cumulative cost", "bn €", "{:,.0f}"),
        "hp_share": (f"Heat-pump share {METRICS_YEAR}", "pp", "{:.1f}"),
        "vre": (f"Variable renewables {METRICS_YEAR}", "GW", "{:,.0f}"),
        "storage": (f"Storage discharge {METRICS_YEAR}", "TWh", "{:,.0f}"),
        "dsm": (f"DSM discharge {METRICS_YEAR}", "TWh", "{:,.0f}"),
        "tes": (f"TES discharge {METRICS_YEAR}", "TWh", "{:,.1f}"),
        "curtailment": (f"Curtailment {METRICS_YEAR}", "TWh", "{:,.0f}")}
SCENARIO_ORDER = [FULL, NO_TES_DSM_PESS, NO_TES, NO_DSM, NO_FLEX]


def _cell_color(x: float) -> str:
    """x = difference / largest |difference| of the metric, in [-1, 1]."""
    if abs(x) < 1e-9:
        return "white"
    return eth_tint(ETH_GREEN if x > 0 else ETH_RED, 0.92 + (0.55 - 0.92) * abs(x))


def flexibility_scenarios_table(runs: list[Run], name: str) -> None:
    by = {r.label: r for r in runs}
    order = [lbl for lbl in SCENARIO_ORDER if lbl in by]
    metrics = {lbl: flexibility_metrics_with_curtailment(by[lbl]) for lbl in order}
    base = metrics[FULL]
    n_metrics, n_scen = len(ROWS), len(order)

    fig, ax = plt.subplots(figsize=(REPORT_WIDTH, 0.56 * n_metrics + 0.9))
    for y, (key, (title, unit, fmt)) in enumerate(ROWS.items()):
        abs_unit = "%" if key == "hp_share" else unit
        ax.text(-0.06, y + 0.5, f"{title}\n({abs_unit})", ha="right", va="center", fontsize=8, fontweight="bold")
        max_abs = max(abs(metrics[lbl][key] - base[key]) for lbl in order) or 1.0
        pct_fmt = "{:.2f}" if key == "cost" else "{:.1f}"
        for x, lbl in enumerate(order):
            val = metrics[lbl][key]
            d = val - base[key]
            color = MATRIX_STYLE["baseline"] if lbl == FULL else _cell_color(d / max_abs)
            ax.add_patch(Rectangle((x, y), 1, 1, facecolor=color, edgecolor="white", linewidth=1.5, zorder=1))
            cx = x + 0.5
            if lbl == FULL:
                ax.text(cx, y + 0.36, fmt.format(val), ha="center", va="center",
                        fontsize=8.5, fontweight="bold", color="black")
                ax.text(cx, y + 0.7, "baseline", ha="center", va="center", fontsize=7,
                        style="italic", color="black")
            else:
                sign = "+" if d >= 0 else "−"
                ax.text(cx, y + 0.28, fmt.format(val), ha="center", va="center",
                        fontsize=8.5, fontweight="bold", color="black")
                ax.text(cx, y + 0.58, f"{sign}{fmt.format(abs(d))} {unit}", ha="center", va="center",
                        fontsize=6.5, color="black")
                ax.text(cx, y + 0.82, f"({sign}{pct_fmt.format(abs(d) / base[key] * 100)} %)",
                        ha="center", va="center", fontsize=6.5, color="black")
    for x, lbl in enumerate(order):
        label = lbl.replace("ZEN-Europe-", "ZEN-Europe-\n") if lbl != FULL else lbl
        ax.text(x + 0.5, -0.08, label, ha="center", va="bottom", fontsize=7.5, fontweight="bold")
    ax.plot([n_scen - 1] * 2, [-0.6, n_metrics], color="#1F2A3A", linestyle="--",
            linewidth=0.8, clip_on=False, zorder=3)
    ax.set_xlim(0, n_scen)
    ax.set_ylim(n_metrics, 0)
    ax.axis("off")
    handles = [Patch(facecolor=MATRIX_STYLE["baseline"], label=f"Baseline ({FULL})"),
               Patch(facecolor=MATRIX_STYLE["decrease"], label=f"Lower than {FULL}"),
               Patch(facecolor=MATRIX_STYLE["increase"], label=f"Higher than {FULL}")]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=3, fontsize=7.5,
              frameon=False, handlelength=1.2, title="Shade scaled per row to its largest difference",
              title_fontsize=7.5)
    fig.tight_layout()
    save_figure(fig, name)
