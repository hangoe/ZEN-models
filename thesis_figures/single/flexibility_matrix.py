"""2x2 matrices of flexibility vs. model resolution (thesis Fig. 6 and A5, one presentation figure).

Columns: ZEN-Europe (all flexibility options) and ZEN-Europe-No-Flex. Rows: three vs.
one temperature level (Fig. 6) or ten vs. twenty representative time steps per year
(Fig. A5). Four panels: discounted total system cost, heat-pump share of industrial heat,
variable renewable capacity and curtailment (metrics.flexibility_metrics_with_curtailment).
Each cell gives the value, its difference to the baseline cell (top left) and the
relative difference; cells are shaded by the size of the change relative to the largest
change in the panel (increase: colour ramp, decrease: red, faded for small changes).
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, to_rgba
from matplotlib.patches import Patch, Rectangle

from ..results import Run
from ..style import ETH_BLUE, ETH_GREEN, ETH_GREY, ETH_RED, REPORT_WIDTH, eth_tint, save_figure
from .metrics import METRICS_YEAR, flexibility_metrics_with_curtailment
from .scenarios import FULL, NO_FLEX

# Report matrix and table colours: baseline grey, increase ETH green, decrease ETH red.
MATRIX_STYLE = dict(baseline=eth_tint(ETH_GREY, 0.72), border=1.1,
                    increase=eth_tint(ETH_GREEN, 0.55), decrease=eth_tint(ETH_RED, 0.55))
INCREASE_CMAP_BLUE = LinearSegmentedColormap.from_list(
    "shade_delta_increase", [eth_tint(ETH_BLUE, 0.85), ETH_BLUE, "#0F2A52"])
INCREASE_CMAP_GREEN = LinearSegmentedColormap.from_list(
    "shade_delta_increase_green", [eth_tint(ETH_GREEN, 0.85), ETH_GREEN, "#2F3709"])
DECREASE_MIN_SHADE = 0.2  # the smallest decrease keeps this much of the full decrease colour
EDGE_COLOR = "#1F2A3A"

# Panels in grid order (row-major): metric -> (title, number formats).
PANELS = {
    "cost": ("Total cumulative cost (bn EUR)", {}),
    "hp_share": (f"Heat-pump share {METRICS_YEAR} (%)", dict(value_fmt="{:.1f}", delta_unit="pp")),
    "vre": (f"Variable renewables {METRICS_YEAR} (GW)", {}),
    "curtailment": (f"Curtailment {METRICS_YEAR} (TWh)", {}),
}
SLOT, GAP = 1.0, 0.12  # cell side and gap between cells, in data units
BASE_RC = (0, 0)


def shade_color(frac: float, increase_cmap) -> tuple:
    """Cell colour for a change of `frac` (signed, relative to the panel's largest change)."""
    if frac >= 0:
        return increase_cmap(min(frac, 1.0))
    full = np.array(to_rgba(MATRIX_STYLE["decrease"]))
    w = DECREASE_MIN_SHADE + (1 - DECREASE_MIN_SHADE) * min(abs(frac), 1.0)
    return tuple(w * full + (1 - w) * np.ones(4))


def _text_color(face) -> str:
    """White on dark fills (WCAG relative luminance below 0.179), else black."""
    r, g, b = (v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in face[:3])
    return "white" if 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.179 else "black"


def matrix_panel(ax: plt.Axes, values: dict[tuple[int, int], float], increase_cmap,
                 col_names: tuple[str, ...], row_names: tuple[str, ...], row_labels: bool,
                 value_fmt: str = "{:,.0f}", delta_fmt: str = "{:,.1f}", delta_unit: str | None = None) -> None:
    """One 2x2 matrix; `values` keyed by (row, col), row 0 on top, (0, 0) the baseline."""
    base = values[BASE_RC]
    max_abs = max(abs(v - base) for v in values.values()) or 1.0
    line = 0.15  # line spacing of the cell text
    for rc, c in values.items():
        row, col = rc
        x0, y0 = col * (SLOT + GAP), (1 - row) * (SLOT + GAP)
        face = to_rgba(MATRIX_STYLE["baseline"]) if rc == BASE_RC else shade_color((c - base) / max_abs, increase_cmap)
        ax.add_patch(Rectangle((x0, y0), SLOT, SLOT, facecolor=face, edgecolor=EDGE_COLOR,
                               linewidth=MATRIX_STYLE["border"], zorder=1))
        delta = c - base
        sign = "+" if delta >= 0 else "−"
        lines = [(value_fmt.format(c), dict(fontsize=7.5))]  # units are in the panel title
        if rc == BASE_RC:
            lines.append(("baseline", dict(fontsize=7.5, style="italic")))
        else:
            d_unit = f" {delta_unit}" if delta_unit else ""
            lines += [(f"({sign}{delta_fmt.format(abs(delta))}{d_unit})", dict(fontsize=7.5)),
                      (f"{sign}{abs(delta) / base * 100:.2f} %", dict(fontsize=9, fontweight="bold"))]
        y_first = y0 + SLOT / 2 + (len(lines) - 1) * line / 2
        for i, (txt, kw) in enumerate(lines):
            ax.text(x0 + SLOT / 2, y_first - i * line, txt, ha="center", va="center",
                    color=_text_color(face), zorder=4, **kw)

    label_y = 2 * SLOT + GAP + 0.06
    for col, label in enumerate(col_names):
        ax.text(col * (SLOT + GAP) + SLOT / 2, label_y, label, ha="center", va="bottom", fontsize=8.5,
                color="black")
    for row, label in enumerate(row_names if row_labels else []):
        ax.text(-0.06, (1 - row) * (SLOT + GAP) + SLOT / 2, label, ha="right", va="center", rotation=90,
                fontsize=8.5, color="black")
    top_y = 2 * SLOT + GAP
    ax.set_xlim(-0.2, top_y + 0.2)
    ax.set_ylim(-0.2, top_y + 0.2)
    ax.set_aspect("equal")
    ax.axis("off")


def matrix_legend(increase_cmap, baseline_label: str) -> list[Patch]:
    kw = dict(edgecolor=EDGE_COLOR, linewidth=0.6)
    return [Patch(facecolor=MATRIX_STYLE["baseline"], label=f"Baseline ({baseline_label})", **kw),
            Patch(facecolor=shade_color(-1.0, increase_cmap), label="Decrease below baseline", **kw),
            Patch(facecolor=shade_color(0.1, increase_cmap), label="Small increase over baseline", **kw),
            Patch(facecolor=shade_color(1.0, increase_cmap), label="Largest increase in the panel", **kw)]


def matrix_figure(cells: dict[tuple[int, int], Run], name: str, row_names: tuple[str, str],
                  increase_cmap, baseline_label: str, one_row: bool = False) -> None:
    """The four panels of the 2x2 `cells` (row, col) -> run, as a 2x2 grid (column labels
    only above the top row) or, with `one_row`, side by side; legend below."""
    metrics = {rc: flexibility_metrics_with_curtailment(r) for rc, r in cells.items()}
    if one_row:
        fig, axes = plt.subplots(1, 4, figsize=(4 * 2.45, 2.45))
    else:
        fig, axes = plt.subplots(2, 2, figsize=(REPORT_WIDTH, REPORT_WIDTH))

    def lower(i: int) -> bool:  # panel below another one
        return not one_row and i >= 2

    for i, (ax, (key, (_, fmt))) in enumerate(zip(axes.flat, PANELS.items())):
        matrix_panel(ax, {rc: m[key] for rc, m in metrics.items()}, increase_cmap,
                     col_names=() if lower(i) else (FULL, NO_FLEX), row_names=row_names,
                     row_labels=(i == 0) if one_row else (i % 2 == 0), **fmt)
    if one_row:
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0)
    else:
        fig.subplots_adjust(left=0.115, right=0.885, bottom=0.115, top=0.885, hspace=-0.02, wspace=-0.02)
    # Panel titles centred over the cells; positions are known only after a draw
    # (set_aspect("equal") shrinks the axes).
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    to_fig = fig.transFigure.inverted()
    for i, (ax, (title, _)) in enumerate(zip(axes.flat, PANELS.values())):
        extent = ax.get_window_extent(renderer)
        top = extent.y1
        if lower(i):  # where the column labels would be
            top = ax.transData.transform((0, ax.get_ylim()[1] - 0.2 + 0.06))[1]
        x, y = to_fig.transform(((extent.x0 + extent.x1) / 2, top))
        fig.text(x, y + 0.003, f"({'abcd'[i]}) {title}", ha="center", va="bottom", fontsize=9.5,
                 fontweight="bold")
    bottom = to_fig.transform((0, axes.flat[-1].get_window_extent(renderer).y0))[1]
    x_mid = to_fig.transform(((axes.flat[0].get_window_extent(renderer).x0
                               + axes.flat[-1].get_window_extent(renderer).x1) / 2, 0))[0]
    fig.legend(handles=matrix_legend(increase_cmap, baseline_label), loc="upper center",
               bbox_to_anchor=(x_mid, bottom), ncol=2, frameon=False, fontsize=8)
    save_figure(fig, name)


def temperature_matrix(no_flex_run: Run, no_flex_single_run: Run, full_run: Run, single_temp_run: Run,
                       name: str, one_row: bool = False) -> None:
    """Rows: three temperature levels / a single temperature level."""
    cells = {(0, 0): full_run, (0, 1): no_flex_run, (1, 0): single_temp_run, (1, 1): no_flex_single_run}
    matrix_figure(cells, name, ("3 temp. levels", "Single temp. level"), INCREASE_CMAP_BLUE,
                  f"{FULL}, 3 temp. levels", one_row=one_row)


def time_step_matrix(no_flex_run: Run, no_flex_20ts_run: Run, full_run: Run, full_20ts_run: Run,
                     name: str) -> None:
    """Rows: ten / twenty representative time steps per year."""
    cells = {(0, 0): full_run, (0, 1): no_flex_run, (1, 0): full_20ts_run, (1, 1): no_flex_20ts_run}
    matrix_figure(cells, name, ("10 time steps", "20 time steps"), INCREASE_CMAP_GREEN,
                  f"{FULL}, 10 time steps")
