"""Energy input by carrier of the new and the existing industry sectors (thesis Fig. 2).

Average energy input [GW] of each sector's production technologies in the first modelled
year of ZEN-Europe-No-Flex (flow_conversion_input / 8760 h), as horizontal stacked bars:
process heat by temperature band, fuels, electricity. The blended kiln fuel of glass and
ceramic (natural gas in practice, can shift to electricity or hydrogen) is one segment;
the blended cement fuel is split into the raw fuels it is made from.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from ..names import CARRIER_COLORS
from ..results import HOURS_PER_YEAR, Run, get_available_years
from ..style import (
    ETH_BLUE,
    ETH_BRONZE,
    ETH_GREY,
    ETH_PETROL,
    ETH_PURPLE,
    ETH_RED,
    REPORT_WIDTH,
    eth_tint,
    report_legend,
    save_figure,
    text_color_for_bg,
)
from .metrics import cached_total
from .scenarios import NO_FLEX

# The four new industry sectors, in bar order (top to bottom).
NEW_SECTOR_LABELS = {"glass": "Glass", "ceramic": "Ceramic", "paper": "Paper", "food": "Food"}

# Heat bands (< 200 °C) in tints of ETH red, darker = hotter.
HEAT_BAND_LABELS = {"0_100": "0–100 °C", "100_150": "100–150 °C", "150_200": "150–200 °C"}
HEAT_BAND_COLORS = {"0_100": eth_tint(ETH_RED, 0.72), "100_150": eth_tint(ETH_RED, 0.45),
                    "150_200": eth_tint(ETH_RED, 0.2)}
FUEL_CARRIER_COLORS = {"natural_gas": CARRIER_COLORS["natural_gas"], "hard_coal": CARRIER_COLORS["hard_coal"],
                       "oil": CARRIER_COLORS["oil"], "biomass": CARRIER_COLORS["biomass"],
                       "waste": CARRIER_COLORS["waste"], "hydrogen": CARRIER_COLORS["hydrogen"],
                       "naphtha": eth_tint(ETH_BRONZE, 0.5), "methanol": eth_tint(ETH_PURPLE, 0.25),
                       "fuel_to_process": eth_tint(ETH_PETROL, 0.6)}
FUEL_CARRIER_LABELS = {"natural_gas": "Natural gas", "hard_coal": "Hard coal", "oil": "Oil", "biomass": "Biomass",
                       "waste": "Waste", "hydrogen": "Hydrogen", "naphtha": "Naphtha", "methanol": "Methanol",
                       "fuel_to_process": "Kiln fuel (natural gas,\nfuel shift possible)"}
ELECTRICITY_COLOR = ETH_BLUE
ELECTRICITY_LABEL = "Electricity"

# Blended kiln-fuel hub carriers, drawn as one "fuel_to_process" segment.
BLENDED_FUEL_CARRIERS = ("fuel_to_kiln", "fuel_to_process")
# Technologies that make the blended cement fuel from raw fuels (hydrogen route: 0 in 2022).
CEMENT_FUEL_TECHS = ["coal_to_cement_fuel", "waste_to_cement_fuel", "biomass_to_cement_fuel"]
MIN_SEGMENT_GW = 0.05  # carriers below this in every bar are left out (and out of the legend)
LABEL_SHARE = 0.05  # segments narrower than this share of the longest bar get no number


def tech_input_by_carrier(r, techs: list[str], year: int) -> pd.Series:
    """Energy input of `techs` by carrier in `year`, summed over nodes, as average GW."""
    flow_in = cached_total(r, "flow_conversion_input")
    out: dict[str, float] = {}
    for tech in techs:
        if tech not in flow_in.index.get_level_values("technology"):
            continue
        sub = flow_in.xs(tech, level="technology")
        if year not in sub.columns:
            continue
        for carrier, val in sub[year].groupby("carrier").sum().items():
            out[carrier] = out.get(carrier, 0.0) + float(val) / HOURS_PER_YEAR
    return pd.Series(out)


def merge_blended_fuel(s: pd.Series, r=None, year: int | None = None) -> pd.Series:
    """All BLENDED_FUEL_CARRIERS of `s` merged into one "fuel_to_process" entry."""
    present = [c for c in BLENDED_FUEL_CARRIERS if c in s.index]
    if not present:
        return s
    return pd.Series({**s.drop(index=present).to_dict(), "fuel_to_process": s[present].sum()})


def split_cement_fuel(s: pd.Series, r, year: int) -> pd.Series:
    """Blended cement fuel replaced by the raw fuels it is made from, scaled to the
    amount the kiln consumed (raw inputs are larger by the conversion factors)."""
    if "fuel_for_cement" not in s.index:
        return s
    raw = tech_input_by_carrier(r, CEMENT_FUEL_TECHS, year)
    out = s.drop(index="fuel_for_cement")
    if raw.sum() > 0:
        out = out.add(raw * s["fuel_for_cement"] / raw.sum(), fill_value=0.0)
    return out


# Sectors of ZEN-Europe-Legacy: (label, production technologies, post-processing).
# Alternative steel routes keep their own carriers (switching means building another
# route, not substituting fuel).
LEGACY_SECTOR_GROUPS = [
    ("Cement (clinker)", ["cement_kiln"], split_cement_fuel),
    ("Primary steel", ["BF_BOF", "NG_DRI", "H2_DRI"], None),
    ("Secondary steel", ["EAF"], None),
    ("Ammonia (Haber-Bosch)", ["haber_bosch"], None),
    ("Methanol", ["methanol_from_natural_gas", "methanol_from_hydrogen", "methanol_from_biomass"], None),
    ("Olefins", ["olefin_from_naphtha", "olefin_from_methanol"], None),
]


def industry_energy_input(no_flex_run: Run, name: str) -> None:
    r = no_flex_run.results
    year = get_available_years(r)[0]

    rows: list[tuple[str, pd.Series]] = []
    for s, label in NEW_SECTOR_LABELS.items():
        rows.append((label, merge_blended_fuel(tech_input_by_carrier(r, [f"{s}_production"], year))))
    n_new = len(rows)
    for label, techs, post in LEGACY_SECTOR_GROUPS:
        s = tech_input_by_carrier(r, techs, year)
        rows.append((label, post(s, r, year) if post is not None else s))

    segments = ([(f"heat_industry_{b}", HEAT_BAND_COLORS[b]) for b in HEAT_BAND_COLORS]
                + [(c, FUEL_CARRIER_COLORS[c]) for c in FUEL_CARRIER_COLORS]
                + [("electricity", ELECTRICITY_COLOR)])
    present = [(c, col) for c, col in segments if any(v.get(c, 0.0) > MIN_SEGMENT_GW for _, v in rows)]

    # one-row gap between the two groups, top to bottom
    y = np.array([i if i < n_new else i + 1 for i in range(len(rows))], dtype=float)
    totals = np.array([sum(v.get(c, 0.0) for c, _ in present) for _, v in rows])

    fig, ax = plt.subplots(figsize=(REPORT_WIDTH, 4.4))
    left = np.zeros(len(rows))
    min_label = LABEL_SHARE * totals.max()
    for carrier, color in present:
        vals = np.array([v.get(carrier, 0.0) for _, v in rows])
        ax.barh(y, vals, 0.66, left=left, color=color, edgecolor="white", linewidth=0.5)
        for yi, li, vi in zip(y, left, vals):
            if vi >= min_label:
                ax.text(li + vi / 2, yi, f"{vi:.1f}", ha="center", va="center", fontsize=6.5,
                        color=text_color_for_bg(color))
        left += vals
    for yi, total in zip(y, totals):
        ax.text(total + 0.008 * totals.max(), yi, f"{total:.1f}", ha="left", va="center",
                fontsize=7.5, fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels([label for label, _ in rows], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, totals.max() * 1.08)
    ax.axhline(n_new, color="black", linewidth=0.6, alpha=0.6)
    for y_text, text in ((-0.75, "New industry sectors"), (n_new + 0.25, "Sectors of ZEN-Europe-Legacy")):
        ax.text(-0.01, y_text, text, transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=7.5, fontstyle="italic", color=ETH_GREY)
    ax.set_ylim(len(rows) + 0.5, -1.1)

    ax.set_xlabel(f"Average energy input in {year} (GW), {NO_FLEX}")
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", alpha=0.3)
    ax.set_axisbelow(True)

    def header(text: str) -> Patch:
        return Patch(facecolor="none", edgecolor="none", label=text)

    present_carriers = {c for c, _ in present}
    headers = ["Process heat", "Fuels"]
    handles = [header(headers[0])]
    handles += [Patch(facecolor=HEAT_BAND_COLORS[b], label=HEAT_BAND_LABELS[b])
                for b in HEAT_BAND_COLORS if f"heat_industry_{b}" in present_carriers]
    handles += [header(headers[1])]
    handles += [Patch(facecolor=FUEL_CARRIER_COLORS[c], label=FUEL_CARRIER_LABELS[c])
                for c in FUEL_CARRIER_COLORS if c in present_carriers]
    handles += [header(""), Patch(facecolor=ELECTRICITY_COLOR, label=ELECTRICITY_LABEL)]
    leg = report_legend(ax, handles, fontsize=7.5, labelspacing=0.3)
    for t in leg.get_texts():
        if t.get_text() in headers:
            t.set_fontweight("bold")

    fig.tight_layout()
    save_figure(fig, name)
