"""Shared constants, helpers, and plotting primitives for the Streamlit dashboard."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from zen_garden import Results

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "outputs"
HOURS_PER_YEAR = 8760

# ── Merged color palette ──────────────────────────────────────────────────────
# Base: compare_models.py (system-wide coverage)
# Added: analyze_model.py entries not present in base (industry heat carriers,
#        temp conversion, TES, DSM)
COLOR_MAP = {
    # Industry heat carriers
    "heat_industry_0_100": "#1a237e",
    "heat_industry_100_150": "#64b5f6",
    "heat_industry_150_200": "#ff7043",
    "heat_industry_temp_conversion_150": "#ffab91",
    "heat_industry_temp_conversion_100": "#ffcc80",
    # TES
    "industry_TES_water_0_100": "#5aacff",
    "industry_TES_water_100_150": "#6495ed",
    "industry_TES_steam_100_150": "#ff7043",
    "industry_TES_steam_150_200": "#ef5350",
    # DSM
    "glass_DSM": "#2e7d32",
    "ceramic_DSM": "#66bb6a",
    "paper_DSM": "#a5d6a7",
    "food_DSM": "#ff8f00",
    # Carriers (emissions plot)
    "crude_oil (carrier)": "#a0795c",
    "natural_gas (carrier)": "#d4a017",
    "hard_coal (carrier)": "#8b6e5a",
    "lng (carrier)": "#e8a838",
    "lignite (carrier)": "#a89070",
    "waste (carrier)": "#a0a0a0",
    # Technologies (emissions plot)
    "cement_kiln (tech)": "#a0a0a0",
    "BF_BOF (tech)": "#4682b4",
    "EAF (tech)": "#87ceeb",
    "NG_DRI (tech)": "#b0c4de",
    "glass_production (tech)": "#9370db",
    # Fossil / fuel technologies
    "natural_gas_boiler": "#d4a017",
    "natural_gas_boiler_DH": "#c49000",
    "natural_gas_boiler_industry": "#b8860b",
    "natural_gas_turbine": "#ffd700",
    "natural_gas_turbine_CCS": "#e6c200",
    "natural_gas_pipeline": "#f0e68c",
    "natural_gas_storage": "#eee8aa",
    "SMR": "#cd853f",
    "SMR_CCS": "#d2a679",
    "methanol_from_natural_gas": "#c9a96e",
    "methanation": "#bdb76b",
    "hard_coal_plant": "#8b6e5a",
    "hard_coal_boiler_DH": "#9c7f6b",
    "lignite_coal_plant": "#a89070",
    "coal_to_cement_fuel": "#9a8070",
    "lng_terminal": "#e8a838",
    "oil_boiler": "#b8956e",
    "oil_boiler_DH": "#c4a07a",
    "oil_plant": "#a0795c",
    "oil_pipeline": "#b08a6e",
    "oil_storage": "#c0a080",
    "oil_to_diesel_conversion": "#b89878",
    "oil_to_gasoline_conversion": "#c4a488",
    "oil_to_kerosene_conversion": "#d0b098",
    "oil_to_naphtha_conversion": "#d8bca0",
    "refining": "#b08a6e",
    "crude_oil": "#a0795c",
    "waste_boiler_DH": "#a0a0a0",
    "waste_plant": "#b0b0b0",
    "waste_to_cement_fuel": "#909090",
    # Renewables
    "photovoltaics": "#f0c040",
    "wind_onshore": "#4ca6a8",
    "wind_offshore": "#5bb0b0",
    "reservoir_hydro": "#5aacff",
    "run-of-river_hydro": "#6a85e8",
    "pumped_hydro": "#6495ed",
    # Nuclear
    "nuclear": "#c850c0",
    # Biomass
    "biomass_plant": "#4caf50",
    "biomass_plant_CCS": "#43a047",
    "biomass_boiler": "#56b870",
    "biomass_boiler_DH": "#3cb371",
    "biomass_boiler_industry": "#4caf50",
    "biomass_to_cement_fuel": "#7cb342",
    "biomethane_conversion": "#76c76e",
    "anaerobic_digestion": "#8fbc8f",
    "methanol_from_biomass": "#9ccc65",
    "gasification": "#8bc34a",
    "pyrolysis": "#7cb342",
    # Hydrogen
    "electrolysis": "#00bcd4",
    "hydrogen_pipeline": "#4dd0e1",
    "fuel_cell": "#26c6da",
    "haber_bosch": "#00acc1",
    "hydrogen_to_cement_fuel": "#00acc1",
    "hydrogen_FC_ship": "#0288d1",
    "salt_cavern_storage": "#4dd0e1",
    "H2_DRI": "#26c6da",
    # Electric / heat pump
    "electrode_boiler": "#ff7043",
    "electrode_boiler_DH": "#f4511e",
    "electrode_boiler_industry": "#e64a19",
    "heat_pump": "#e91e63",
    "heat_pump_DH": "#c2185b",
    "heat_pump_industry_0_100_waste_heat": "#f06292",
    "heat_pump_industry_0_100_water": "#f8bbd0",
    "heat_pump_industry_100_150_waste_heat": "#ec407a",
    "heat_pump_industry_100_150_water": "#f48fb1",
    "heat_pump_industry_150_200_waste_heat": "#c2185b",
    "heat_pump_industry_150_200_water": "#e91e63",
    "battery": "#7e57c2",
    "power_line": "#9575cd",
    "district_heating_grid": "#ef5350",
    # Transport
    "BEV": "#43a047",
    "ICE_petrol": "#bdbdbd",
    "ICE_diesel": "#9e9e9e",
    "HDT_diesel": "#9e9e9e",
    "HDT_BET": "#66bb6a",
    "HDT_FCEV": "#26a69a",
    "ammonia_ICE_ship": "#5c6bc0",
    "methanol_ICE_ship": "#7986cb",
    "diesel_ICE_ship": "#9e9e9e",
    # Steel
    "BF_BOF": "#4682b4",
    "BF_BOF_CCS": "#6a9fc8",
    "EAF": "#87ceeb",
    "NG_DRI": "#b0c4de",
    "NG_DRI_CCS": "#9ab0c8",
    "industrial_gas_consumer": "#d4a017",
    # Carbon
    "DAC": "#b39ddb",
    "carbon_pipeline": "#90a4ae",
    "carbon_storage": "#78909c",
    "cement_post_comb": "#90a4ae",
    # Cement & industry
    "cement_kiln": "#a0a0a0",
    "glass_production": "#9370db",
    "ceramic_production": "#ba68c8",
    "paper_production": "#ce93d8",
    "food_production": "#f48fb1",
    # Supply / imports
    "natural_gas import": "#d4a017",
    "lng import": "#e8a838",
    "hard_coal import": "#8b6e5a",
    "waste import": "#a0a0a0",
    "crude_oil import": "#a0795c",
    # Chemicals
    "fischer_tropsch": "#8d6e63",
    "olefin_from_naphtha": "#a1887f",
    "olefin_from_methanol": "#bcaaa4",
    "methanol_from_hydrogen": "#80cbc4",
}

# ── Hatch map ─────────────────────────────────────────────────────────────────
# Explicit entries for industry-heat techs (from analyze_model.py)
HATCH_MAP: dict[str, str] = {
    "natural_gas_boiler_industry": "//",
    "biomass_boiler_industry": "//",
    "electrode_boiler_industry": "**",
    "heat_pump_industry_0_100_waste_heat": "\\\\",
    "heat_pump_industry_0_100_water": "//",
    "heat_pump_industry_100_150_waste_heat": "\\\\",
    "heat_pump_industry_100_150_water": "//",
    "heat_pump_industry_150_200_waste_heat": "\\\\",
    "heat_pump_industry_150_200_water": "//",
    "heat_industry_temp_conversion_150": "||",
    "heat_industry_temp_conversion_100": "||",
    "glass_production": "oo",
    "ceramic_production": "oo",
    "paper_production": "oo",
    "food_production": "oo",
    "industry_TES_water_0_100": "--",
    "industry_TES_water_100_150": "--",
    "industry_TES_steam_100_150": "--",
    "industry_TES_steam_150_200": "--",
    "glass_DSM": "xx",
    "ceramic_DSM": "xx",
    "paper_DSM": "xx",
    "food_DSM": "xx",
    "battery": "..",
    "pumped_hydro": "//",
}
# Pattern-based for everything else in COLOR_MAP
for _name in COLOR_MAP:
    if _name in HATCH_MAP:
        continue
    if "boiler" in _name and "DH" in _name:
        HATCH_MAP[_name] = "///"
    elif "boiler" in _name:
        HATCH_MAP[_name] = "//"
    elif "turbine" in _name:
        HATCH_MAP[_name] = ".."
    elif "_DH" in _name or "district_heating" in _name:
        HATCH_MAP[_name] = "///"
    elif "_plant" in _name and "CCS" in _name:
        HATCH_MAP[_name] = "xx"
    elif "CCS" in _name:
        HATCH_MAP[_name] = "xx"
    elif "pipeline" in _name:
        HATCH_MAP[_name] = "||"
    elif "storage" in _name:
        HATCH_MAP[_name] = "--"
    elif "heat_pump" in _name:
        HATCH_MAP[_name] = "\\\\"
    elif "electrode" in _name:
        HATCH_MAP[_name] = "**"

FALLBACK_COLORS = plt.cm.tab20.colors + plt.cm.tab20b.colors + plt.cm.tab20c.colors


def _get_color(name: str, fallback_idx: int) -> str | tuple:
    return COLOR_MAP.get(name, FALLBACK_COLORS[fallback_idx % len(FALLBACK_COLORS)])


def _get_hatch(name: str) -> str:
    return HATCH_MAP.get(name, "")


def _text_color_for_bg(bg_color) -> str:
    from matplotlib.colors import to_rgb
    r, g, b = to_rgb(bg_color)
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "white" if luminance < 0.45 else "black"


# ── Model discovery ───────────────────────────────────────────────────────────

def load_results(model_name: str) -> Results:
    path = OUTPUT_DIR / model_name
    if not path.exists():
        raise FileNotFoundError(f"Model output not found: {path}")
    if not (path / "system.json").exists():
        subdirs = [d for d in path.iterdir() if d.is_dir() and not d.name.startswith(".")]
        if len(subdirs) == 1:
            path = subdirs[0]
    return Results(path=str(path))


def get_available_models() -> list[str]:
    if not OUTPUT_DIR.exists():
        return []
    models = []
    for d in sorted(OUTPUT_DIR.iterdir()):
        if not d.is_dir() or d.name == "figures":
            continue
        if (d / "var_dict.h5").exists() or (d / "system.json").exists():
            models.append(d.name)
            continue
        try:
            subdirs = [sd for sd in d.iterdir() if sd.is_dir() and not sd.name.startswith(".")]
            if len(subdirs) == 1 and (
                (subdirs[0] / "var_dict.h5").exists() or (subdirs[0] / "system.json").exists()
            ):
                models.append(d.name)
        except PermissionError:
            continue
    return models


def get_available_years(r: Results) -> list[int]:
    try:
        return sorted(int(y) for y in r.get_years())
    except Exception:
        try:
            df = r.get_total("carbon_emissions_annual")
            return sorted(int(y) for y in df.index)
        except Exception:
            return [2025]


# ── Plotting primitives ───────────────────────────────────────────────────────

def plot_stacked_bars_years(
    df: pd.DataFrame,
    title: str,
    unit: str,
    ax: plt.Axes,
    show_legend: bool = True,
    show_segment_labels: bool = False,
) -> None:
    if df.empty:
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return

    years = df.columns.tolist()
    techs = df.index.tolist()
    bar_width = 0.6
    labeled: set[str] = set()

    for year_idx, year in enumerate(years):
        bottom = 0.0
        for tech_idx, tech in enumerate(techs):
            val = df.loc[tech, year]
            if val < 1e-6:
                continue
            color = _get_color(tech, tech_idx)
            hatch = _get_hatch(tech)
            ax.bar(
                year_idx, val, bar_width, bottom=bottom,
                color=color, label=tech if tech not in labeled else None,
                edgecolor="white", linewidth=0.5, hatch=hatch,
            )
            if show_segment_labels and val > 0:
                ax.text(year_idx, bottom + val / 2, f"{val:,.0f}",
                        ha="center", va="center", fontsize=5,
                        color=_text_color_for_bg(color))
            bottom += val
            labeled.add(tech)
        ax.text(year_idx, bottom, f"{bottom:,.0f}",
                ha="center", va="bottom", fontsize=7, fontweight="bold")

    ax.set_xticks(range(len(years)))
    ax.set_xticklabels([str(y) for y in years], fontsize=9)
    ax.set_ylabel(unit, fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.axhline(0, color="black", linewidth=0.5)

    if show_legend:
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles[::-1], labels[::-1],
                      bbox_to_anchor=(1.02, 1), loc="upper left",
                      fontsize=7, frameon=False)


def add_price_line(ax: plt.Axes, price_series: pd.Series, label: str, color: str) -> None:
    if price_series.empty or (price_series.abs() < 1e-9).all():
        return
    ax2 = ax.twinx()
    ax2.plot(range(len(price_series)), price_series.values,
             color=color, linewidth=2, marker="o", markersize=5, label=label, zorder=5)
    ax2.set_ylabel(label, fontsize=9, color=color)
    ax2.tick_params(axis="y", labelcolor=color)
    ax2.legend(loc="upper right", fontsize=7, frameon=False)


def plot_stacked_bars(
    df: pd.DataFrame,
    title: str,
    unit: str,
    ax: plt.Axes,
    show_legend: bool = True,
    show_segment_labels: bool = False,
) -> None:
    if df.empty:
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return

    bar_width = 0.6
    models = df.columns.tolist()
    positive_df = df.clip(lower=0)
    negative_df = df.clip(upper=0)
    labeled: set[str] = set()

    for model_idx, model in enumerate(models):
        bottom_pos = 0.0
        bottom_neg = 0.0
        for cat_idx, category in enumerate(df.index):
            val_pos = positive_df.loc[category, model]
            val_neg = negative_df.loc[category, model]
            color = _get_color(category, cat_idx)
            hatch = _get_hatch(category)
            add_label = category not in labeled

            if val_pos > 0:
                ax.bar(model_idx, val_pos, bar_width, bottom=bottom_pos,
                       color=color, label=category if add_label else None,
                       edgecolor="white", linewidth=0.5, hatch=hatch)
                if show_segment_labels:
                    ax.text(model_idx, bottom_pos + val_pos / 2, f"{val_pos:,.0f}",
                            ha="center", va="center", fontsize=6,
                            color=_text_color_for_bg(color))
                bottom_pos += val_pos
                labeled.add(category)

            if val_neg < 0:
                ax.bar(model_idx, val_neg, bar_width, bottom=bottom_neg,
                       color=color, label=category if add_label else None,
                       edgecolor="white", linewidth=0.5, hatch=hatch if hatch else "//")
                if show_segment_labels:
                    ax.text(model_idx, bottom_neg + val_neg / 2, f"{val_neg:,.0f}",
                            ha="center", va="center", fontsize=6,
                            color=_text_color_for_bg(color))
                bottom_neg += val_neg
                labeled.add(category)

        ax.text(model_idx, bottom_pos, f"{positive_df[model].sum():,.0f}",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(models, fontsize=9)
    ax.set_ylabel(unit, fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.axhline(0, color="black", linewidth=0.5)

    if show_legend:
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles[::-1], labels[::-1],
                      bbox_to_anchor=(1.02, 1), loc="upper left",
                      fontsize=7, frameon=False)
