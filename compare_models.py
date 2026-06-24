"""Compare two ZEN-garden model outputs side by side.

Produces stacked bar plots for:
  1. Total system emissions (carrier + technology)
  2. Total system costs (CAPEX + OPEX)
  3. Industry process costs
  4. Industry heating costs
  5. Fuel consumption breakdown (natural_gas, hard_coal, lng, waste)

Usage:
    python compare_models.py [model_a] [model_b]
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from zen_garden import Results

OUTPUT_DIR = Path(__file__).parent / "data" / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"
DEFAULT_MODEL_A = "Crystal_Ball_HG_v2_3"
DEFAULT_MODEL_B = "Crystal_Ball_HG_v3_0"
YEAR = 2025

INDUSTRY_PROCESS_TECHS = [
    "cement_kiln", "cement_post_comb", "biomass_to_cement_fuel",
    "coal_to_cement_fuel", "hydrogen_to_cement_fuel", "waste_to_cement_fuel",
    "BF_BOF", "BF_BOF_CCS", "EAF", "NG_DRI", "NG_DRI_CCS", "H2_DRI",
    "glass_production", "ceramic_production", "paper_production", "food_production",
]

INDUSTRY_HEATING_TECHS = [
    "natural_gas_boiler_industry", "electrode_boiler_industry", "biomass_boiler_industry",
    "heat_pump_industry_0_100", "heat_pump_industry_100_150", "heat_pump_industry_150_200",  
]

HEAT_TECHS = [
    "natural_gas_boiler", "biomass_boiler", "heat_pump",
    "electrode_boiler", "oil_boiler", "district_heating_grid",
]

DISTRICT_HEAT_TECHS = [
    "natural_gas_boiler_DH", "hard_coal_boiler_DH", "waste_boiler_DH",
    "biomass_boiler_DH", "oil_boiler_DH", "heat_pump_DH",
    "electrode_boiler_DH",
]

# ── Consistent color palette ────────────────────────────────────────────────
COLOR_MAP = {
    # Carriers (emissions plot)
    "crude_oil (carrier)":    "#a0795c",
    "natural_gas (carrier)":  "#d4a017",
    "hard_coal (carrier)":    "#8b6e5a",
    "lng (carrier)":          "#e8a838",
    "lignite (carrier)":      "#a89070",
    "waste (carrier)":        "#a0a0a0",
    # Technologies (emissions plot)
    "cement_kiln (tech)":     "#a0a0a0",
    "BF_BOF (tech)":          "#4682b4",
    "EAF (tech)":             "#87ceeb",
    "NG_DRI (tech)":          "#b0c4de",
    "glass_production (tech)": "#9370db",
    # Fossil / fuel technologies
    "natural_gas_boiler":     "#d4a017",
    "natural_gas_boiler_DH":  "#c49000",
    "natural_gas_boiler_industry":   "#b8860b",
    "natural_gas_turbine":    "#ffd700",
    "natural_gas_turbine_CCS": "#e6c200",
    "natural_gas_pipeline":   "#f0e68c",
    "natural_gas_storage":    "#eee8aa",
    "SMR":                    "#cd853f",
    "SMR_CCS":                "#d2a679",
    "methanol_from_natural_gas": "#c9a96e",
    "methanation":            "#bdb76b",
    "hard_coal_plant":        "#8b6e5a",
    "hard_coal_boiler_DH":    "#9c7f6b",
    "lignite_coal_plant":     "#a89070",
    "coal_to_cement_fuel":    "#9a8070",
    "lng_terminal":           "#e8a838",
    "oil_boiler":             "#b8956e",
    "oil_boiler_DH":          "#c4a07a",
    "oil_plant":              "#a0795c",
    "oil_pipeline":           "#b08a6e",
    "oil_storage":            "#c0a080",
    "oil_to_diesel_conversion":    "#b89878",
    "oil_to_gasoline_conversion":  "#c4a488",
    "oil_to_kerosene_conversion":  "#d0b098",
    "oil_to_naphtha_conversion":   "#d8bca0",
    "refining":               "#b08a6e",
    "crude_oil":              "#a0795c",
    "waste_boiler_DH":        "#a0a0a0",
    "waste_plant":            "#b0b0b0",
    "waste_to_cement_fuel":   "#909090",
    # Renewables
    "photovoltaics":          "#f0c040",
    "wind_onshore":           "#4ca6a8",
    "wind_offshore":          "#5bb0b0",
    "reservoir_hydro":        "#5aacff",
    "run-of-river_hydro":     "#6a85e8",
    "pumped_hydro":           "#6495ed",
    # Nuclear
    "nuclear":                "#c850c0",
    # Biomass
    "biomass_plant":          "#4caf50",
    "biomass_plant_CCS":      "#43a047",
    "biomass_boiler":         "#56b870",
    "biomass_boiler_DH":      "#3cb371",
    "biomass_boiler_industry":   "#4caf50",
    "biomass_to_cement_fuel": "#7cb342",
    "biomethane_conversion":  "#76c76e",
    "anaerobic_digestion":    "#8fbc8f",
    "methanol_from_biomass":  "#9ccc65",
    "gasification":           "#8bc34a",
    "pyrolysis":              "#7cb342",
    # Hydrogen
    "electrolysis":           "#00bcd4",
    "hydrogen_pipeline":      "#4dd0e1",
    "fuel_cell":              "#26c6da",
    "haber_bosch":            "#00acc1",
    "hydrogen_to_cement_fuel": "#00acc1",
    "hydrogen_FC_ship":       "#0288d1",
    "salt_cavern_storage":    "#4dd0e1",
    "H2_DRI":                 "#26c6da",
    # Electric / heat pump
    "electrode_boiler":       "#ff7043",
    "electrode_boiler_DH":    "#f4511e",
    "electrode_boiler_industry":   "#e64a19",
    "heat_pump":              "#e91e63",
    "heat_pump_DH":           "#c2185b",
    "heat_pump_industry_0_100":   "#f06292",
    "heat_pump_industry_100_150":  "#ec407a",
    "heat_pump_industry_150_200": "#f48fb1",
    "battery":                "#7e57c2",
    "power_line":             "#9575cd",
    "district_heating_grid":  "#ef5350",
    # Transport
    "BEV":                    "#43a047",
    "ICE_petrol":             "#bdbdbd",
    "ICE_diesel":             "#9e9e9e",
    "HDT_diesel":             "#9e9e9e",
    "HDT_BET":                "#66bb6a",
    "HDT_FCEV":               "#26a69a",
    "ammonia_ICE_ship":       "#5c6bc0",
    "methanol_ICE_ship":      "#7986cb",
    "diesel_ICE_ship":        "#9e9e9e",
    # Steel
    "BF_BOF":                 "#4682b4",
    "BF_BOF_CCS":             "#6a9fc8",
    "EAF":                    "#87ceeb",
    "NG_DRI":                 "#b0c4de",
    "NG_DRI_CCS":             "#9ab0c8",
    "industrial_gas_consumer": "#d4a017",
    # Carbon
    "DAC":                    "#b39ddb",
    "carbon_pipeline":        "#90a4ae",
    "carbon_storage":         "#78909c",
    "cement_post_comb":       "#90a4ae",
    # Cement & industry
    "cement_kiln":            "#a0a0a0",
    "glass_production":       "#9370db",
    "ceramic_production":     "#ba68c8",
    "paper_production":       "#ce93d8",
    "food_production":        "#f48fb1",
    # Supply / imports
    "natural_gas import":     "#d4a017",
    "lng import":             "#e8a838",
    "hard_coal import":       "#8b6e5a",
    "waste import":           "#a0a0a0",
    "crude_oil import":       "#a0795c",
    # Chemicals
    "fischer_tropsch":        "#8d6e63",
    "olefin_from_naphtha":    "#a1887f",
    "olefin_from_methanol":   "#bcaaa4",
    "methanol_from_hydrogen": "#80cbc4",
}

HATCH_MAP = {}
for _name in COLOR_MAP:
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
    elif "_plant" in _name:
        HATCH_MAP[_name] = ""
    elif "CCS" in _name:
        HATCH_MAP[_name] = "xx"
    elif "pipeline" in _name:
        HATCH_MAP[_name] = "||"
    elif "storage" in _name:
        HATCH_MAP[_name] = "--"
    elif "import" in _name:
        HATCH_MAP[_name] = ""
    elif "production" in _name:
        HATCH_MAP[_name] = "oo"
    elif "heat_pump" in _name:
        HATCH_MAP[_name] = "\\\\"
    elif "electrode" in _name:
        HATCH_MAP[_name] = "**"

FALLBACK_COLORS = (
    plt.cm.tab20.colors + plt.cm.tab20b.colors + plt.cm.tab20c.colors
)


def _get_color(name: str, fallback_idx: int) -> str | tuple:
    if name in COLOR_MAP:
        return COLOR_MAP[name]
    return FALLBACK_COLORS[fallback_idx % len(FALLBACK_COLORS)]


def _get_hatch(name: str) -> str:
    if name in HATCH_MAP:
        return HATCH_MAP[name]
    return ""


def _text_color_for_bg(bg_color) -> str:
    from matplotlib.colors import to_rgb
    r, g, b = to_rgb(bg_color)
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "white" if luminance < 0.45 else "black"


# ── Data helpers ─────────────────────────────────────────────────────────────

def load_results(model_name: str) -> Results:
    path = OUTPUT_DIR / model_name
    if not path.exists():
        raise FileNotFoundError(f"Model output not found: {path}")
    return Results(path=str(path))


def get_emissions_by_carrier(r: Results) -> pd.Series:
    df = r.get_total("carbon_emissions_carrier")
    series = df.groupby("carrier").sum()[YEAR]
    return series[series.abs() > 1e-6].sort_values(ascending=False)


def get_emissions_by_technology(r: Results) -> pd.Series:
    df = r.get_total("carbon_emissions_technology")
    series = df.groupby("technology").sum()[YEAR]
    return series[series.abs() > 1e-6].sort_values(ascending=False)


def get_capex_by_technology(r: Results) -> pd.Series:
    df = r.get_total("cost_capex_yearly")
    series = df.groupby("technology").sum()[YEAR]
    return series[series.abs() > 1e-6].sort_values(ascending=False)


def get_opex_by_technology(r: Results) -> pd.Series:
    df = r.get_total("cost_opex_yearly")
    series = df.groupby("technology").sum()[YEAR]
    return series[series.abs() > 1e-6].sort_values(ascending=False)


def get_fuel_consumption(r: Results, carrier: str) -> pd.Series:
    flow_in = r.get_total("flow_conversion_input")
    if carrier not in flow_in.index.get_level_values("carrier"):
        return pd.Series(dtype=float)
    series = flow_in.xs(carrier, level="carrier").groupby("technology").sum()[YEAR]
    return series[series.abs() > 1e-3].sort_values(ascending=False)


def get_fuel_supply(r: Results, carrier: str) -> pd.Series:
    pieces = {}
    imp = r.get_total("flow_import")
    if carrier in imp.index.get_level_values("carrier"):
        total_import = imp.xs(carrier, level="carrier").sum()[YEAR]
        if abs(total_import) > 1e-3:
            pieces[f"{carrier} import"] = total_import
    flow_out = r.get_total("flow_conversion_output")
    if carrier in flow_out.index.get_level_values("carrier"):
        by_tech = flow_out.xs(carrier, level="carrier").groupby("technology").sum()[YEAR]
        for tech, val in by_tech.items():
            if abs(val) > 1e-3:
                pieces[tech] = val
    return pd.Series(pieces).sort_values(ascending=False)


def get_carrier_production(r: Results, carrier: str) -> pd.Series:
    flow_out = r.get_total("flow_conversion_output")
    if carrier not in flow_out.index.get_level_values("carrier"):
        return pd.Series(dtype=float)
    series = flow_out.xs(carrier, level="carrier").groupby("technology").sum()[YEAR]
    return series[series.abs() > 1e-3].sort_values(ascending=False)


def filter_techs(series: pd.Series, tech_list: list[str]) -> pd.Series:
    present = [t for t in tech_list if t in series.index]
    filtered = series.loc[present]
    return filtered[filtered.abs() > 1e-6].sort_values(ascending=False)


def build_comparison_df(
    series_a: pd.Series, series_b: pd.Series, name_a: str, name_b: str
) -> pd.DataFrame:
    combined = pd.DataFrame({name_a: series_a, name_b: series_b}).fillna(0)
    return combined.sort_values(name_a, ascending=True)


# ── Plotting ─────────────────────────────────────────────────────────────────

def plot_stacked_bars(
    df: pd.DataFrame,
    title: str,
    unit: str,
    ax: plt.Axes,
    show_legend: bool = True,
    show_segment_labels: bool = False,
):
    bar_width = 0.6
    models = df.columns.tolist()

    positive_df = df.clip(lower=0)
    negative_df = df.clip(upper=0)

    labeled = set()
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
                ax.bar(
                    model_idx, val_pos, bar_width, bottom=bottom_pos,
                    color=color, label=category if add_label else None,
                    edgecolor="white", linewidth=0.5, hatch=hatch,
                )
                if show_segment_labels:
                    mid = bottom_pos + val_pos / 2
                    ax.text(model_idx, mid, f"{val_pos:,.0f}",
                            ha="center", va="center", fontsize=6,
                            color=_text_color_for_bg(color))
                bottom_pos += val_pos
                labeled.add(category)
            if val_neg < 0:
                neg_hatch = hatch if hatch else "//"
                ax.bar(
                    model_idx, val_neg, bar_width, bottom=bottom_neg,
                    color=color, label=category if add_label else None,
                    edgecolor="white", linewidth=0.5, hatch=neg_hatch,
                )
                if show_segment_labels:
                    mid = bottom_neg + val_neg / 2
                    ax.text(model_idx, mid, f"{val_neg:,.0f}",
                            ha="center", va="center", fontsize=6,
                            color=_text_color_for_bg(color))
                bottom_neg += val_neg
                labeled.add(category)

        total = positive_df[model].sum()
        ax.text(model_idx, bottom_pos, f"{total:,.0f}",
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


def plot_cost_figure(
    df_capex: pd.DataFrame,
    df_opex: pd.DataFrame,
    title: str,
    save_path: Path,
    show_segment_labels: bool = False,
):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(title, fontsize=14, fontweight="bold")
    plot_stacked_bars(df_capex, "CAPEX by Technology", "MEUR", axes[0],
                      show_legend=False, show_segment_labels=show_segment_labels)
    plot_stacked_bars(df_opex, "OPEX by Technology", "MEUR", axes[1],
                      show_legend=False, show_segment_labels=show_segment_labels)

    handles_all, labels_all = {}, {}
    for ax in axes:
        for h, l in zip(*ax.get_legend_handles_labels()):
            if l not in labels_all:
                handles_all[l] = h
                labels_all[l] = l
    ordered = sorted(labels_all.keys())
    ncol = 2 if len(ordered) > 10 else 1
    fig.legend(
        [handles_all[l] for l in reversed(ordered)],
        list(reversed(ordered)),
        loc="upper center", bbox_to_anchor=(0.5, -0.02),
        fontsize=7, frameon=False, ncol=ncol,
    )
    fig.tight_layout(rect=[0, 0.05 + 0.02 * len(ordered) / ncol / 10, 1, 0.93])
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved to {save_path}")
    return fig


def plot_fuel_consumption(
    r_a: Results,
    r_b: Results,
    model_a: str,
    model_b: str,
    carriers: list[str],
    save_path: Path,
):
    n = len(carriers)
    fig, axes = plt.subplots(1, n, figsize=(6 * n, 7))
    if n == 1:
        axes = [axes]
    fig.suptitle(
        f"Fuel Consumption by Technology: {model_a} vs {model_b}  (Year {YEAR})",
        fontsize=14, fontweight="bold",
    )
    for ax, carrier in zip(axes, carriers):
        fa = get_fuel_consumption(r_a, carrier)
        fb = get_fuel_consumption(r_b, carrier)
        df = build_comparison_df(fa, fb, model_a, model_b)
        plot_stacked_bars(df, carrier.replace("_", " ").title(), "GWh",
                          ax, show_segment_labels=True)

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved to {save_path}")
    return fig


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    model_a = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL_A
    model_b = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MODEL_B

    print(f"Loading {model_a} ...")
    r_a = load_results(model_a)
    print(f"Loading {model_b} ...")
    r_b = load_results(model_b)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Comparing year {YEAR} across Europe ...\n")

    # --- Emissions ---
    em_carrier_a = get_emissions_by_carrier(r_a)
    em_carrier_b = get_emissions_by_carrier(r_b)
    em_tech_a = get_emissions_by_technology(r_a)
    em_tech_b = get_emissions_by_technology(r_b)

    # --- Costs ---
    capex_a = get_capex_by_technology(r_a)
    capex_b = get_capex_by_technology(r_b)
    df_capex = build_comparison_df(capex_a, capex_b, model_a, model_b)
    opex_a = get_opex_by_technology(r_a)
    opex_b = get_opex_by_technology(r_b)
    df_opex = build_comparison_df(opex_a, opex_b, model_a, model_b)

    df_capex_ind = build_comparison_df(
        filter_techs(capex_a, INDUSTRY_PROCESS_TECHS),
        filter_techs(capex_b, INDUSTRY_PROCESS_TECHS), model_a, model_b)
    df_opex_ind = build_comparison_df(
        filter_techs(opex_a, INDUSTRY_PROCESS_TECHS),
        filter_techs(opex_b, INDUSTRY_PROCESS_TECHS), model_a, model_b)

    df_capex_heat = build_comparison_df(
        filter_techs(capex_a, INDUSTRY_HEATING_TECHS),
        filter_techs(capex_b, INDUSTRY_HEATING_TECHS), model_a, model_b)
    df_opex_heat = build_comparison_df(
        filter_techs(opex_a, INDUSTRY_HEATING_TECHS),
        filter_techs(opex_b, INDUSTRY_HEATING_TECHS), model_a, model_b)

    # --- Print summary ---
    annual_em_a = r_a.get_total("carbon_emissions_annual")[YEAR]
    annual_em_b = r_b.get_total("carbon_emissions_annual")[YEAR]
    capex_total_a = r_a.get_total("cost_capex_yearly_total")[YEAR]
    capex_total_b = r_b.get_total("cost_capex_yearly_total")[YEAR]
    opex_total_a = r_a.get_total("cost_opex_yearly_total")[YEAR]
    opex_total_b = r_b.get_total("cost_opex_yearly_total")[YEAR]

    print(f"{'':30s} {model_a:>20s} {model_b:>20s}")
    print("-" * 72)
    print(f"{'Annual emissions (Mton CO2)':30s} {annual_em_a:>20,.1f} {annual_em_b:>20,.1f}")
    print(f"{'Total CAPEX (MEUR)':30s} {capex_total_a:>20,.1f} {capex_total_b:>20,.1f}")
    print(f"{'Total OPEX (MEUR)':30s} {opex_total_a:>20,.1f} {opex_total_b:>20,.1f}")

    # --- Figure 1: Total system emissions ---
    em_all_a = pd.concat([
        em_carrier_a.rename(lambda c: f"{c} (carrier)"),
        em_tech_a.rename(lambda t: f"{t} (tech)"),
    ])
    em_all_b = pd.concat([
        em_carrier_b.rename(lambda c: f"{c} (carrier)"),
        em_tech_b.rename(lambda t: f"{t} (tech)"),
    ])
    df_em_all = build_comparison_df(em_all_a, em_all_b, model_a, model_b)

    fig1, ax1 = plt.subplots(figsize=(8, 8))
    fig1.suptitle(
        f"Total System Emissions: {model_a} vs {model_b}  (Year {YEAR})",
        fontsize=14, fontweight="bold",
    )
    plot_stacked_bars(df_em_all, "", "Mton CO2eq", ax1, show_segment_labels=True)
    fig1.tight_layout(rect=[0, 0, 1, 0.95])
    fig1.savefig(FIGURES_DIR / f"emissions_{model_a}_vs_{model_b}.png",
                 dpi=150, bbox_inches="tight")
    print(f"\nEmissions plot saved")

    # --- Figure 2: Total system costs ---
    plot_cost_figure(
        df_capex, df_opex,
        f"Total System Costs: {model_a} vs {model_b}  (Year {YEAR})",
        FIGURES_DIR / f"costs_total_{model_a}_vs_{model_b}.png",
    )

    # --- Figure 3: Industry process costs ---
    plot_cost_figure(
        df_capex_ind, df_opex_ind,
        f"Industry Process Costs: {model_a} vs {model_b}  (Year {YEAR})",
        FIGURES_DIR / f"costs_industry_{model_a}_vs_{model_b}.png",
        show_segment_labels=True,
    )

    # --- Figure 4: Heating costs (industry heating + heat + district heat) ---
    df_capex_ht = build_comparison_df(
        filter_techs(capex_a, HEAT_TECHS),
        filter_techs(capex_b, HEAT_TECHS), model_a, model_b)
    df_opex_ht = build_comparison_df(
        filter_techs(opex_a, HEAT_TECHS),
        filter_techs(opex_b, HEAT_TECHS), model_a, model_b)
    df_capex_dh = build_comparison_df(
        filter_techs(capex_a, DISTRICT_HEAT_TECHS),
        filter_techs(capex_b, DISTRICT_HEAT_TECHS), model_a, model_b)
    df_opex_dh = build_comparison_df(
        filter_techs(opex_a, DISTRICT_HEAT_TECHS),
        filter_techs(opex_b, DISTRICT_HEAT_TECHS), model_a, model_b)

    heating_groups = [
        ("Heat", df_capex_ht, df_opex_ht),
        ("District Heat", df_capex_dh, df_opex_dh),
        ("Industry Heating", df_capex_heat, df_opex_heat),
    ]
    fig4, axes4 = plt.subplots(2, 3, figsize=(20, 10))
    fig4.suptitle(
        f"Heating Costs: {model_a} vs {model_b}  (Year {YEAR})",
        fontsize=14, fontweight="bold",
    )
    for col, (label, df_cx, df_ox) in enumerate(heating_groups):
        plot_stacked_bars(df_cx, f"{label} — CAPEX", "MEUR",
                          axes4[0, col], show_segment_labels=True)
        plot_stacked_bars(df_ox, f"{label} — OPEX", "MEUR",
                          axes4[1, col], show_segment_labels=True)
    fig4.tight_layout(rect=[0, 0, 1, 0.95])
    heat_path = FIGURES_DIR / f"costs_heating_{model_a}_vs_{model_b}.png"
    fig4.savefig(heat_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved to {heat_path}")

    # --- Figure 5: Fuel consumption shift ---
    plot_fuel_consumption(
        r_a, r_b, model_a, model_b,
        ["natural_gas", "hard_coal", "lng", "waste"],
        FIGURES_DIR / f"fuel_consumption_{model_a}_vs_{model_b}.png",
    )

    # --- Figure 6: Natural gas supply vs consumption ---
    ng_supply_a = get_fuel_supply(r_a, "natural_gas")
    ng_supply_b = get_fuel_supply(r_b, "natural_gas")
    df_ng_supply = build_comparison_df(ng_supply_a, ng_supply_b, model_a, model_b)

    ng_cons_a = get_fuel_consumption(r_a, "natural_gas")
    ng_cons_b = get_fuel_consumption(r_b, "natural_gas")
    df_ng_cons = build_comparison_df(ng_cons_a, ng_cons_b, model_a, model_b)

    fig6, axes6 = plt.subplots(1, 2, figsize=(14, 7))
    fig6.suptitle(
        f"Natural Gas Balance: {model_a} vs {model_b}  (Year {YEAR})",
        fontsize=14, fontweight="bold",
    )
    plot_stacked_bars(df_ng_supply, "Supply (imports + conversion)", "GWh",
                      axes6[0], show_segment_labels=True)
    plot_stacked_bars(df_ng_cons, "Consumption by Technology", "GWh",
                      axes6[1], show_segment_labels=True)
    fig6.tight_layout(rect=[0, 0, 1, 0.93])
    fig6.savefig(FIGURES_DIR / f"natural_gas_balance_{model_a}_vs_{model_b}.png",
                 dpi=150, bbox_inches="tight")
    print(f"Plot saved to {FIGURES_DIR / 'natural_gas_balance_...'}")

    plt.show()


if __name__ == "__main__":
    main()
