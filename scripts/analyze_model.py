"""Analyze a single ZEN-garden model output across multiple time steps.

Produces 10 figures for the industry_heat sector:
  1. carrier_heat_industry_all      — production & consumption for all 3 temp levels
  2. carrier_products_production    — production only for glass/ceramic/paper/food
  3. boiler_hp_production           — boiler & HP output (excl. temp conversion), NG price overlay
  4. capacity_heat_supply           — capacity addition & total for supply techs (split by temp-conversion)
  5. capacity_production            — capacity addition & total for production techs
  6. tes_capacity_addition          — TES energy + power capacity addition
  7. tes_charge_discharge           — TES charge + discharge flows
  8. heat_demand_by_sector          — heat input by temperature level for each production sector
  9. dsm_capacity_addition          — DSM energy + power capacity addition (glass/ceramic/paper/food)
 10. dsm_charge_discharge           — DSM charge + discharge flows (glass/ceramic/paper/food)

Usage:
    python scripts/analyze_model.py [model_name]
"""

import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from zen_garden import Results

from plots.figure_settings import (
    add_price_line,
    apply_font_mode,
    load_results as _load_results,
    plot_stacked_bars_years,
)

# Match the rest of the figure scripts' font -- see figure_settings.FONT_MODE
# for the rationale and for the one-flag toggle that switches every figure
# script in this repo at once.
apply_font_mode()

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"
DEFAULT_MODEL = "Crystal_Ball_HG_v4_6_2025_6a_5a_interval_10ts/Crystal_Ball_HG_v4_6"

INDUSTRY_HEAT_CARRIERS_ENERGY = [
    "heat_industry_0_100",
    "heat_industry_100_150",
    "heat_industry_150_200",
]

INDUSTRY_HEAT_CARRIERS_PRODUCT = [
    "glass",
    "ceramic",
    "paper",
    "food",
]

INDUSTRY_HEAT_TECHS_BOILERS_HP = [
    "heat_pump_industry_0_100_waste_heat",
    "heat_pump_industry_0_100_water",
    "heat_pump_industry_100_150_waste_heat",
    "heat_pump_industry_100_150_water",
    "heat_pump_industry_150_200_waste_heat",
    "heat_pump_industry_150_200_water",
    "biomass_boiler_industry",
    "electrode_boiler_industry",
    "natural_gas_boiler_industry",
]

INDUSTRY_HEAT_TECHS_TEMP_CONV = [
    "heat_industry_temp_conversion_150",
    "heat_industry_temp_conversion_100",
]

INDUSTRY_HEAT_TECHS_SUPPLY = INDUSTRY_HEAT_TECHS_BOILERS_HP + INDUSTRY_HEAT_TECHS_TEMP_CONV

INDUSTRY_HEAT_TECHS_PRODUCTION = [
    "glass_production",
    "ceramic_production",
    "paper_production",
    "food_production",
]

INDUSTRY_TES_TECHS = [
    "industry_TES_water_0_100",
    "industry_TES_water_100_150",
    "industry_TES_steam_100_150",
    "industry_TES_steam_150_200",
]

INDUSTRY_DSM_TECHS = [
    "glass_DSM",
    "ceramic_DSM",
    "paper_DSM",
    "food_DSM",
]

# get_total('price_import') sums over all 8760 h/year; divide + ×1000 → EUR/MWh
HOURS_PER_YEAR = 8760


# -- Data helpers -------------------------------------------------------------

def load_results(model_name: str) -> Results:
    return _load_results(OUTPUT_DIR, model_name)


def get_carrier_production(r: Results, carrier: str) -> pd.DataFrame:
    flow_out = r.get_total("flow_conversion_output")
    if carrier not in flow_out.index.get_level_values("carrier"):
        return pd.DataFrame()
    df = flow_out.xs(carrier, level="carrier").groupby("technology").sum()
    return df[(df.abs() > 1e-3).any(axis=1)]


def get_carrier_consumption(r: Results, carrier: str) -> pd.DataFrame:
    flow_in = r.get_total("flow_conversion_input")
    if carrier not in flow_in.index.get_level_values("carrier"):
        return pd.DataFrame()
    df = flow_in.xs(carrier, level="carrier").groupby("technology").sum()
    return df[(df.abs() > 1e-3).any(axis=1)]


def get_capacity_addition(
    r: Results, techs: list[str], capacity_type: str = "power",
) -> pd.DataFrame:
    cap_add = r.get_total("capacity_addition")
    cap_add = cap_add[cap_add.index.get_level_values("capacity_type") == capacity_type]
    rows = {}
    for tech in techs:
        if tech in cap_add.index.get_level_values("technology"):
            series = cap_add.xs(tech, level="technology").sum()
            if (series.abs() > 1e-6).any():
                rows[tech] = series
    return pd.DataFrame(rows).T if rows else pd.DataFrame()


def get_capacity(
    r: Results, techs: list[str], capacity_type: str = "power",
) -> pd.DataFrame:
    cap = r.get_total("capacity")
    cap = cap[cap.index.get_level_values("capacity_type") == capacity_type]
    rows = {}
    for tech in techs:
        if tech in cap.index.get_level_values("technology"):
            series = cap.xs(tech, level="technology").sum()
            if (series.abs() > 1e-6).any():
                rows[tech] = series
    return pd.DataFrame(rows).T if rows else pd.DataFrame()


def get_heat_demand_by_sector(r: Results, tech: str) -> pd.DataFrame:
    """For a production tech, return heat input [GWh] per temperature carrier × year."""
    flow_in = r.get_total("flow_conversion_input")
    rows = {}
    for carrier in INDUSTRY_HEAT_CARRIERS_ENERGY:
        if carrier not in flow_in.index.get_level_values("carrier"):
            continue
        sub = flow_in.xs(carrier, level="carrier")
        if tech not in sub.index.get_level_values("technology"):
            continue
        s = sub.xs(tech, level="technology").sum()
        if (s.abs() > 1e-3).any():
            rows[carrier] = s
    return pd.DataFrame(rows).T if rows else pd.DataFrame()


def get_storage_flows(r: Results, techs: list[str], flow_type: str) -> pd.DataFrame:
    df = r.get_total(flow_type)
    rows = {}
    for tech in techs:
        if tech in df.index.get_level_values("technology"):
            series = df.xs(tech, level="technology").sum()
            if (series.abs() > 1e-3).any():
                rows[tech] = series
    return pd.DataFrame(rows).T if rows else pd.DataFrame()


def get_import_price_eur_per_mwh(r: Results, carrier: str) -> pd.Series:
    pi = r.get_total("price_import")
    if carrier not in pi.index.get_level_values("carrier"):
        return pd.Series(dtype=float)
    return pi.xs(carrier, level="carrier").mean() / HOURS_PER_YEAR * 1000


# -- Figure functions ---------------------------------------------------------

def fig_carrier_energy_all(r: Results, model_name: str, save_path: Path):
    """Figure 1: 3 rows (one per temp level) × 2 cols (production, consumption)."""
    n = len(INDUSTRY_HEAT_CARRIERS_ENERGY)
    fig, axes = plt.subplots(n, 2, figsize=(18, 5 * n))
    fig.suptitle(
        f"Industry Heat Carriers — Production & Consumption ({model_name})",
        fontsize=14, fontweight="bold",
    )
    for row, carrier in enumerate(INDUSTRY_HEAT_CARRIERS_ENERGY):
        label = carrier.replace("_", " ").title()
        prod = get_carrier_production(r, carrier)
        cons = get_carrier_consumption(r, carrier)
        # Put temp-conversion flows on top so constant end-use consumption is visible at the bottom
        if not cons.empty:
            end_use = [t for t in cons.index if t not in INDUSTRY_HEAT_TECHS_TEMP_CONV]
            conv    = [t for t in cons.index if t in INDUSTRY_HEAT_TECHS_TEMP_CONV]
            cons = cons.loc[end_use + conv]
        plot_stacked_bars_years(prod, f"{label} — Production", "GWh",
                                axes[row, 0], show_segment_labels=True)
        plot_stacked_bars_years(cons, f"{label} — Consumption", "GWh",
                                axes[row, 1], show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path.name}")


def fig_carrier_products_production(r: Results, model_name: str, save_path: Path):
    """Figure 2: 2×2 grid — production only for glass, ceramic, paper, food."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle(
        f"Industry Product Carriers — Annual Production ({model_name})",
        fontsize=14, fontweight="bold",
    )
    for ax, carrier in zip(axes.flat, INDUSTRY_HEAT_CARRIERS_PRODUCT):
        label = carrier.title()
        prod = get_carrier_production(r, carrier)
        # unit depends on carrier (tonproduct/h × h = tonproduct, but get_total gives annual)
        plot_stacked_bars_years(prod, label, "GWh-eq", ax, show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path.name}")


def fig_boiler_hp_production(r: Results, model_name: str, save_path: Path):
    """Figure 3: Boiler & HP output for all 3 carriers, NG price on secondary axis."""
    ng_price = get_import_price_eur_per_mwh(r, "natural_gas")
    fig, axes = plt.subplots(1, 3, figsize=(22, 7))
    fig.suptitle(
        f"Industry Heat — Boiler & HP Production (excl. temp conversion) ({model_name})\n"
        "Right axis: natural gas import price [EUR/MWh]",
        fontsize=12, fontweight="bold",
    )
    for ax, carrier in zip(axes, INDUSTRY_HEAT_CARRIERS_ENERGY):
        prod = get_carrier_production(r, carrier)
        if not prod.empty:
            prod = prod[prod.index.isin(INDUSTRY_HEAT_TECHS_BOILERS_HP)]
            prod = prod[(prod.abs() > 1e-3).any(axis=1)]
        label = carrier.replace("_", " ").title()
        plot_stacked_bars_years(prod, label, "GWh", ax, show_segment_labels=True)
        add_price_line(ax, ng_price, "NG import [EUR/MWh]", "#8b0000")
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path.name}")


def fig_capacity_heat_supply(r: Results, model_name: str, save_path: Path):
    """Figure 4: 2×2 — rows=addition/total, cols=boilers+HPs / temp-conversion."""
    add_main = get_capacity_addition(r, INDUSTRY_HEAT_TECHS_BOILERS_HP)
    add_conv = get_capacity_addition(r, INDUSTRY_HEAT_TECHS_TEMP_CONV)
    tot_main = get_capacity(r, INDUSTRY_HEAT_TECHS_BOILERS_HP)
    tot_conv = get_capacity(r, INDUSTRY_HEAT_TECHS_TEMP_CONV)

    fig, axes = plt.subplots(2, 2, figsize=(20, 12))
    fig.suptitle(
        f"Industry Heat Supply — Capacity Addition & Total ({model_name})",
        fontsize=14, fontweight="bold",
    )
    plot_stacked_bars_years(add_main, "Capacity Addition — Boilers & HPs", "GW",
                            axes[0, 0], show_segment_labels=True)
    plot_stacked_bars_years(add_conv, "Capacity Addition — Temp Conversion", "GW",
                            axes[0, 1], show_segment_labels=True)
    plot_stacked_bars_years(tot_main, "Total Capacity — Boilers & HPs", "GW",
                            axes[1, 0], show_segment_labels=True)
    plot_stacked_bars_years(tot_conv, "Total Capacity — Temp Conversion", "GW",
                            axes[1, 1], show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path.name}")


def fig_capacity_production(r: Results, model_name: str, save_path: Path):
    """Figure 5: 1×2 — capacity addition (left) and total capacity (right) for production techs."""
    add_prod = get_capacity_addition(r, INDUSTRY_HEAT_TECHS_PRODUCTION)
    tot_prod = get_capacity(r, INDUSTRY_HEAT_TECHS_PRODUCTION)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle(
        f"Industry Production Technologies — Capacity ({model_name})",
        fontsize=14, fontweight="bold",
    )
    plot_stacked_bars_years(add_prod, "Capacity Addition", "ton/h",
                            axes[0], show_segment_labels=True)
    plot_stacked_bars_years(tot_prod, "Total Capacity", "ton/h",
                            axes[1], show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path.name}")


def fig_tes_capacity_addition(r: Results, model_name: str, save_path: Path):
    """Figure 6: TES capacity addition — energy (left) + power (right)."""
    tes_add_energy = get_capacity_addition(r, INDUSTRY_TES_TECHS, capacity_type="energy")
    tes_add_power = get_capacity_addition(r, INDUSTRY_TES_TECHS, capacity_type="power")

    fig, axes = plt.subplots(1, 2, figsize=(18, 6))
    fig.suptitle(
        f"Industry TES — Capacity Addition ({model_name})",
        fontsize=14, fontweight="bold",
    )
    plot_stacked_bars_years(tes_add_energy, "Energy Capacity Addition", "GWh",
                            axes[0], show_segment_labels=True)
    plot_stacked_bars_years(tes_add_power, "Power Capacity Addition", "GW",
                            axes[1], show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path.name}")


def fig_tes_charge_discharge(r: Results, model_name: str, save_path: Path):
    """Figure 7: TES charge (left) + discharge (right)."""
    charge = get_storage_flows(r, INDUSTRY_TES_TECHS, "flow_storage_charge")
    discharge = get_storage_flows(r, INDUSTRY_TES_TECHS, "flow_storage_discharge")

    fig, axes = plt.subplots(1, 2, figsize=(18, 6))
    fig.suptitle(
        f"Industry TES — Charge & Discharge ({model_name})",
        fontsize=14, fontweight="bold",
    )
    plot_stacked_bars_years(charge, "Charge", "GWh", axes[0], show_segment_labels=True)
    plot_stacked_bars_years(discharge, "Discharge", "GWh", axes[1], show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path.name}")


def fig_heat_demand_by_sector(r: Results, model_name: str, save_path: Path):
    """Figure 8: 1×2 — heat input by temperature level for all sectors, 2025 vs 2050."""
    sectors = [
        ("glass_production",   "Glass"),
        ("ceramic_production", "Ceramic"),
        ("paper_production",   "Paper"),
        ("food_production",    "Food"),
    ]

    # Collect per-sector data once, then slice by year
    sector_data = {label: get_heat_demand_by_sector(r, tech) for tech, label in sectors}

    all_years = next(iter(sector_data.values())).columns.tolist()
    year_first, year_last = all_years[0], all_years[-1]

    fig, axes = plt.subplots(1, 2, figsize=(14, 7), sharey=True)
    fig.suptitle(
        f"Industry Sectors — Heat Input by Temperature Level ({model_name})",
        fontsize=14, fontweight="bold",
    )

    for ax, year in zip(axes, [year_first, year_last]):
        df_year = pd.DataFrame(
            {label: sector_data[label][year] for label in [s[1] for s in sectors]}
        ).fillna(0)
        plot_stacked_bars_years(
            df_year, str(year), "GWh", ax,
            show_legend=(ax is axes[-1]), show_segment_labels=True,
        )

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path.name}")


def fig_dsm_capacity_addition(r: Results, model_name: str, save_path: Path):
    """Figure 9: DSM capacity addition — energy (left) + power (right)."""
    dsm_add_energy = get_capacity_addition(r, INDUSTRY_DSM_TECHS, capacity_type="energy")
    dsm_add_power = get_capacity_addition(r, INDUSTRY_DSM_TECHS, capacity_type="power")

    fig, axes = plt.subplots(1, 2, figsize=(18, 6))
    fig.suptitle(
        f"Industry DSM — Capacity Addition ({model_name})",
        fontsize=14, fontweight="bold",
    )
    plot_stacked_bars_years(dsm_add_energy, "Energy Capacity Addition", "ktproduct",
                            axes[0], show_segment_labels=True)
    plot_stacked_bars_years(dsm_add_power, "Power Capacity Addition", "ktproduct/h",
                            axes[1], show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path.name}")


def fig_dsm_charge_discharge(r: Results, model_name: str, save_path: Path):
    """Figure 10: DSM charge (left) + discharge (right)."""
    charge = get_storage_flows(r, INDUSTRY_DSM_TECHS, "flow_storage_charge")
    discharge = get_storage_flows(r, INDUSTRY_DSM_TECHS, "flow_storage_discharge")

    fig, axes = plt.subplots(1, 2, figsize=(18, 6))
    fig.suptitle(
        f"Industry DSM — Charge & Discharge ({model_name})",
        fontsize=14, fontweight="bold",
    )
    plot_stacked_bars_years(charge, "Charge", "ktproduct", axes[0], show_segment_labels=True)
    plot_stacked_bars_years(discharge, "Discharge", "ktproduct", axes[1], show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path.name}")


def fig_storage_comparison(r: Results, model_name: str, save_path: Path):
    """Figure 11: 1×3 — capacity addition for all storage types on comparable axes.

    Panel 1 (GWh)      : TES energy + battery energy
    Panel 2 (GW)       : TES power + battery power + pumped_hydro
    Panel 3 (ktproduct/h): DSM power (all sectors)
    """
    GWH_TECHS  = INDUSTRY_TES_TECHS + ["battery"]
    GW_TECHS   = INDUSTRY_TES_TECHS + ["battery", "pumped_hydro"]
    DSM_TECHS  = INDUSTRY_DSM_TECHS

    energy_add = get_capacity_addition(r, GWH_TECHS,  capacity_type="energy")
    power_add  = get_capacity_addition(r, GW_TECHS,   capacity_type="power")
    dsm_add    = get_capacity_addition(r, DSM_TECHS,  capacity_type="power")

    fig, axes = plt.subplots(1, 3, figsize=(22, 7))
    fig.suptitle(
        f"Storage Technologies — Capacity Addition ({model_name})",
        fontsize=14, fontweight="bold",
    )
    plot_stacked_bars_years(energy_add, "Energy Capacity Addition\nTES + Battery",
                            "GWh", axes[0], show_segment_labels=True)
    plot_stacked_bars_years(power_add,  "Power Capacity Addition\nTES + Battery + Pumped Hydro",
                            "GW",  axes[1], show_segment_labels=True)
    plot_stacked_bars_years(dsm_add,    "DSM Power Capacity Addition",
                            "ktproduct/h", axes[2], show_segment_labels=True)

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path.name}")


# -- Main ---------------------------------------------------------------------

def main():
    model_name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL

    print(f"Loading {model_name} ...")
    r = load_results(model_name)
    print(f"Years: {r.get_years()}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_name = model_name.replace("/", "_")
    run_dir = FIGURES_DIR / f"{timestamp}_analyze_{short_name}"
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Saving figures to {run_dir}\n")

    fig_carrier_energy_all(r, short_name, run_dir / "1_carrier_heat_industry_all.png")
    fig_carrier_products_production(r, short_name, run_dir / "2_carrier_products_production.png")
    fig_boiler_hp_production(r, short_name, run_dir / "3_boiler_hp_production.png")
    fig_capacity_heat_supply(r, short_name, run_dir / "4_capacity_heat_supply.png")
    fig_capacity_production(r, short_name, run_dir / "5_capacity_production.png")
    fig_tes_capacity_addition(r, short_name, run_dir / "6_tes_capacity_addition.png")
    fig_tes_charge_discharge(r, short_name, run_dir / "7_tes_charge_discharge.png")
    fig_heat_demand_by_sector(r, short_name, run_dir / "8_heat_demand_by_sector.png")
    fig_dsm_capacity_addition(r, short_name, run_dir / "9_dsm_capacity_addition.png")
    fig_dsm_charge_discharge(r, short_name, run_dir / "10_dsm_charge_discharge.png")
    fig_storage_comparison(r, short_name, run_dir / "11_storage_comparison.png")

    plt.show()


if __name__ == "__main__":
    main()
