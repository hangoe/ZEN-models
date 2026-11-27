"""Share of global GHG emissions by sector, vertical bars (presentation).

Static data, not a model result: the shares are copied from the horizontal bar chart
used before (global GHG emissions by sector; add the original source to the slide).
Left bar: all emissions by type; right bar: the energy part broken down by end use,
connected to it by dashed lines. Energy is blue, industry green, everything else grey.
"""

import matplotlib.pyplot as plt

from .style import ETH_BLUE, ETH_GREEN, ETH_GREY, eth_tint, save_figure, text_color_for_bg

# (label, share %, colour), bottom to top
TOTAL = [
    ("Energy", 76.7, ETH_BLUE),
    ("Industrial\nprocesses", 6.2, ETH_GREEN),
    ("Agriculture, waste\n& land use", 17.1, eth_tint(ETH_GREY, 0.45)),
]
# energy by end use; everything except industry merged into one segment (non-industry
# electricity & heat 9.3, manufacturing & construction 12.2, transportation 14.3,
# buildings 6.3, other energy 10.3)
ENERGY = [
    ("Industry\n(electricity & heat)", 24.3, ETH_GREEN),
    ("Other energy use", 9.3 + 12.2 + 14.3 + 6.3 + 10.3, eth_tint(ETH_GREY, 0.25)),
]
X_TOTAL, X_ENERGY, WIDTH = 0.0, 1.6, 1.0
FIG_SIZE = (5.0, 5.6)  # in
SMALL_SHARE = 7.0  # %, segments below this get a one-line label


def _bar(ax, x: float, segments) -> None:
    bottom = 0.0
    for label, share, color in segments:
        ax.bar(x, share, WIDTH, bottom=bottom, color=color, edgecolor="white", linewidth=0.8)
        # segments too short for a multi-line label get one line
        text = (f"{label.replace(chr(10), ' ')} {share:.1f}%" if share < SMALL_SHARE and "\n" in label
                else f"{label}\n{share:.1f}%")
        ax.text(x, bottom + share / 2, text, ha="center", va="center",
                fontsize=7 if share < SMALL_SHARE else 8, fontweight="bold",
                color=text_color_for_bg(color), linespacing=1.15)
        bottom += share


def global_ghg_shares(name: str) -> None:
    energy_total = TOTAL[0][1]
    if abs(sum(s for _, s, _ in ENERGY) - energy_total) > 0.05:
        raise ValueError("energy breakdown does not add up to the energy share")

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    _bar(ax, X_TOTAL, TOTAL)
    _bar(ax, X_ENERGY, ENERGY)
    for y in (0.0, energy_total):   # dashed connectors from the energy segment to its breakdown
        ax.plot([X_TOTAL + WIDTH / 2, X_ENERGY - WIDTH / 2], [y, y], color=ETH_GREY, linestyle=(0, (3, 2)),
                linewidth=0.9)

    ax.set_xlim(X_TOTAL - WIDTH / 2 - 0.1, X_ENERGY + WIDTH / 2 + 0.1)
    ax.set_xticks([X_TOTAL, X_ENERGY])
    ax.set_xticklabels(["All sectors", "Energy by sector"])
    ax.tick_params(axis="x", length=0)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Share of total global GHG emissions (%)")
    ax.spines["bottom"].set_visible(False)
    fig.tight_layout()
    save_figure(fig, name)
