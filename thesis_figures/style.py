"""Figure style shared by all thesis figures: fonts, sizes, ETH colours, saving.

Two output modes, chosen with the environment variable FIGURE_MODE:

  report        Computer Modern (cmr10, bundled with matplotlib), matching the LaTeX
                body text of the thesis. cmr10 maps some code points to other glyphs
                (OT1 encoding), so every text is rewritten at save time
                (report_text_pass); bold / italic use cmb10 / cmti10.
  presentation  Arial, for slides.

All figures are REPORT_WIDTH wide (the text width of the thesis), so the font sizes in
REPORT_RC are the printed sizes. SVG output is deterministic (fixed hash salt, no date),
so regenerated figures can be compared byte by byte.
"""

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import to_rgb
from matplotlib.figure import Figure

from .paths import FIGURES_DIR, REPO_ROOT

FIGURE_MODES = ("report", "presentation")
FONT_MODE = os.environ.get("FIGURE_MODE", "report")
if FONT_MODE not in FIGURE_MODES:
    raise ValueError(f"FIGURE_MODE must be one of {FIGURE_MODES}, got {FONT_MODE!r}")

OUTPUT_DIR = FIGURES_DIR / FONT_MODE

# ── Size and typography ─────────────────────────────────────────────────────
REPORT_WIDTH = 6.3  # in, text width of the thesis (16 cm)
REPORT_RC = {
    "font.size": 9, "axes.labelsize": 9, "axes.titlesize": 9.5,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
    "legend.frameon": False, "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 3, "ytick.major.size": 3, "hatch.linewidth": 0.5,
}
REPORT_VALUE_SIZE = 7.5  # numbers written on or above bars
SVG_HASH_SALT = "zen-thesis"

# ── ETH Zurich corporate colours ────────────────────────────────────────────
# https://ethz.ch/staffnet/en/service/communication/corporate-design/colours.html
ETH_BLUE, ETH_PETROL, ETH_GREEN, ETH_BRONZE, ETH_RED, ETH_PURPLE, ETH_GREY = (
    "#215CAF", "#007894", "#627313", "#8E6713", "#B7352D", "#A7117A", "#6F6F6F")
SCENARIO_PALETTE = [ETH_BLUE, ETH_PETROL, ETH_GREEN, ETH_BRONZE, ETH_RED, ETH_PURPLE, ETH_GREY]
SOLAR_YELLOW = "#FFCA3A"  # the one non-ETH colour (solar reads wrong in any ETH hue)


def eth_tint(hex_color: str, pct: float) -> str:
    """Blend `hex_color` towards white by `pct` (0 = colour, 1 = white), as in ETH's
    20/40/60/80 % tint system."""
    r, g, b = (c + (1 - c) * pct for c in to_rgb(hex_color))
    return f"#{int(round(r * 255)):02x}{int(round(g * 255)):02x}{int(round(b * 255)):02x}"


def text_color_for_bg(bg_color) -> str:
    """Black or white, whichever reads better on `bg_color`."""
    r, g, b = to_rgb(bg_color)
    return "white" if 0.299 * r + 0.587 * g + 0.114 * b < 0.45 else "black"


# ── Fonts ───────────────────────────────────────────────────────────────────
# cmr10 (TeX OT1 encoding) puts other glyphs on some code points: "<" -> "¡",
# ">" -> "¿", "|" -> em dash, "{" -> en dash, "_" -> dot accent, "°" -> "fl"; inside a
# string with mathtext the non-math part has no glyph fallback at all. In report mode,
# these characters are replaced outside "$...$" by their mathtext form (or by the OT1
# slot that holds the right glyph).
_REPORT_CHAR_MAP = {
    "°": r"$^\circ\!$", "<": r"$\!<\!$", ">": r"$\!>\!$", "≤": r"$\!\leq\!$", "≥": r"$\!\geq\!$",
    "→": r"$\rightarrow$", "←": r"$\leftarrow$", "Δ": r"$\Delta$", "×": r"$\times$",
    "−": r"$-$", "±": r"$\pm$", "·": r"$\cdot$", "≈": r"$\!\approx\!$",
    "–": "{", "—": "|", "_": " ", "€": "EUR", "|": r"$|$",
}
_BOLD_WEIGHTS = ("bold", "heavy", "extra bold", "black", "demibold", "semibold")


def report_text(s: str) -> str:
    """`s` made cmr10-safe (see _REPORT_CHAR_MAP); math segments are kept."""
    if not s or s.strip() == "€":  # a lone "€" is an icon, not a unit
        return s
    parts = s.split("$")
    if len(parts) % 2 == 0:  # unbalanced "$": leave untouched
        return s
    out = []
    for i, seg in enumerate(parts):
        if i % 2:  # inside $...$
            out.append(f"${seg}$")
            continue
        seg = seg.replace(" °", "\x00")  # "100 °C": thin space instead of a word space
        out.append("".join(r"$\,^\circ\!$" if ch == "\x00" else _REPORT_CHAR_MAP.get(ch, ch) for ch in seg))
    return "".join(out).replace("$$", "")  # merge adjacent math groups


def report_text_pass(fig: Figure) -> None:
    """Rewrite every text of `fig` with report_text() and map bold / italic to
    cmb10 / cmti10. No-op outside report mode."""
    if FONT_MODE != "report":
        return
    from matplotlib.category import StrCategoryFormatter
    from matplotlib.text import Text
    from matplotlib.ticker import FixedFormatter, FuncFormatter
    for ax in fig.axes:  # string tick labels are re-applied from the formatter at draw time
        for axis in (ax.xaxis, ax.yaxis):
            for fmt in (axis.get_major_formatter(), axis.get_minor_formatter()):
                if isinstance(fmt, FixedFormatter) and not getattr(fmt, "_report_done", False):
                    fmt.seq = [report_text(str(x)) for x in fmt.seq]
                    fmt._report_done = True
            fmt = axis.get_major_formatter()
            if isinstance(fmt, StrCategoryFormatter):
                axis.set_major_formatter(FuncFormatter(lambda x, pos, f=fmt: report_text(f(x, pos))))
    for t in fig.findobj(Text):
        if getattr(t, "_report_done", False):
            continue
        t._report_done = True
        s = t.get_text()
        if s:
            t.set_text(report_text(s))
        weight = t.get_fontweight()
        if weight in _BOLD_WEIGHTS or (isinstance(weight, (int, float)) and weight >= 600):
            t.set_fontfamily(["cmb10", "DejaVu Serif"])
            t.set_fontweight("normal")
        elif t.get_fontstyle() in ("italic", "oblique"):
            t.set_fontfamily(["cmti10", "DejaVu Serif"])
            t.set_fontstyle("normal")


def presentation_text_pass(fig: Figure) -> None:
    """Arial counterpart of report_text_pass(): "EUR" as in the report, and "C*" as plain
    text (mathtext's asterisk operator has no Arial glyph)."""
    from matplotlib.text import Text
    for t in fig.findobj(Text):
        s = t.get_text()
        new = s if s.strip() == "€" else s.replace("€", "EUR").replace("$C^*$", "C*")
        if new != s:
            t.set_text(new)


def _patch_savefig(text_pass) -> None:
    """Apply `text_pass` on every Figure.savefig, so no figure reaches a file unconverted."""
    if getattr(Figure.savefig, "_text_pass_wrapped", False):
        return
    original = Figure.savefig

    def savefig(self, *args, **kwargs):
        text_pass(self)
        return original(self, *args, **kwargs)

    savefig._text_pass_wrapped = True
    Figure.savefig = savefig


def apply_style() -> None:
    """Set fonts (FIGURE_MODE), REPORT_RC and deterministic SVG output. Called once by
    the figure CLI before a figure is built."""
    if FONT_MODE == "presentation":
        plt.rcParams.update({
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "mathtext.fontset": "custom",
            "mathtext.rm": "Arial",
            "mathtext.it": "Arial:italic",
            "mathtext.bf": "Arial:bold",
            "mathtext.sf": "Arial",
            "mathtext.cal": "Arial:italic",
            "mathtext.fallback": "stixsans",
            "axes.formatter.use_mathtext": True,
            "axes.unicode_minus": True,
        })
        _patch_savefig(presentation_text_pass)
    else:
        # cmr10 first, DejaVu Serif only for glyphs cmr10 lacks.
        plt.rcParams.update({
            "font.family": ["cmr10", "DejaVu Serif"],
            "mathtext.fontset": "cm",
            "axes.formatter.use_mathtext": True,
            "axes.unicode_minus": False,
            "svg.fonttype": "path",
        })
        _patch_savefig(report_text_pass)
    plt.rcParams.update(REPORT_RC)
    plt.rcParams["svg.hashsalt"] = SVG_HASH_SALT
    os.environ.setdefault("SOURCE_DATE_EPOCH", "0")  # no date in the SVG metadata


def save_figure(fig: Figure, name: str, extra_artists=None, dpi: float | None = None) -> Path:
    """Save `fig` as figures/<mode>/<name>.svg and close it.

    extra_artists: legends added with ax.add_artist(), which bbox_inches="tight" would
    otherwise crop. dpi only affects rasterised artists."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{name}.svg"
    kwargs = {"bbox_inches": "tight", "bbox_extra_artists": extra_artists}
    if dpi is not None:
        kwargs["dpi"] = dpi
    fig.savefig(path, **kwargs)
    plt.close(fig)
    print(f"  wrote {path.relative_to(REPO_ROOT)}")
    return path


# ── Plotting helpers ────────────────────────────────────────────────────────

def panel_title(ax: plt.Axes, text: str) -> None:
    """Short left-aligned panel header, "(a) ...", instead of a figure title."""
    ax.set_title(text, loc="left", fontsize=9.5, fontweight="bold", pad=5)


def report_legend(ax_or_fig, handles, labels=None, **kw):
    """Frameless legend, outside right of the axes unless `kw` says otherwise."""
    kw = {"loc": "upper left", "bbox_to_anchor": (1.01, 1.0), "fontsize": 8, "frameon": False,
          "handlelength": 1.2, "handleheight": 0.9, "borderaxespad": 0.0, **kw}
    if labels is None:
        return ax_or_fig.legend(handles=handles, **kw)
    return ax_or_fig.legend(handles, labels, **kw)


def signed_stacked_bars(ax: plt.Axes, df: pd.DataFrame, colors: dict, x: np.ndarray,
                        width: float = 0.7, label_fn=None) -> tuple[np.ndarray, np.ndarray]:
    """Stack positive values upwards and negative values downwards from 0.

    df: index = category (bottom to top), columns = years. `label_fn` maps a category
    to its legend label. Returns (top, bottom)."""
    pos = np.zeros(len(df.columns))
    neg = np.zeros(len(df.columns))
    for cat in df.index:
        v = df.loc[cat].to_numpy(dtype=float)
        vp, vn = np.clip(v, 0, None), np.clip(v, None, 0)
        ax.bar(x, vp, width, bottom=pos, color=colors[cat], edgecolor="white", linewidth=0.4,
               label=label_fn(cat) if label_fn else cat)
        ax.bar(x, vn, width, bottom=neg, color=colors[cat], edgecolor="white", linewidth=0.4)
        pos += vp
        neg += vn
    return pos, neg


def comma_axis(ax: plt.Axes, axis: str = "y") -> None:
    """Thousands separators on an axis' tick labels (5,000 instead of 5000)."""
    getattr(ax, f"{axis}axis").set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}"))


def stack_ordered(df: pd.DataFrame, order: list[str], years: list[int] | None = None) -> pd.DataFrame:
    """Rows reordered bottom to top per `order` (others appended, so nothing is
    dropped); columns restricted to `years` if given."""
    df = df.reindex([t for t in order if t in df.index] + [t for t in df.index if t not in order])
    return df if years is None else df[[y for y in years if y in df.columns]]
