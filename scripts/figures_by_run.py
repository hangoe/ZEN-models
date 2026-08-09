"""N-run analysis figures: small multiples, one axis per run, multi-year time
series (see figures_by_scenario.py for the single-axis, runs-as-categories,
one-year-snapshot layout instead). Used by both the Streamlit dashboard
(streamlit/app.py) and standalone scripts (e.g. generate_si_figures.py).

Each function takes a list of `Run` objects and returns a matplotlib Figure
where every metric is rendered as N adjacent axes — one per run, in run
order — so all runs can be compared without switching tabs. To avoid
duplicated legends, only the last run's axis of each row shows a legend (see
`plot_stacked_bars_years_n` in figure_settings.py). Works identically for N=2
(local mode) and N up to 5 (euler mode).
"""

import matplotlib.pyplot as plt
import pandas as pd
from zen_garden import Results

from figure_settings import (
    COLOR_MAP,
    HOURS_PER_YEAR,
    Run,
    add_price_line,
    fig_width_for_runs,
    get_available_years,
    plot_stacked_bars_years_n,
)

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
    # New models (v4_6+): split by temperature + source
    "heat_pump_industry_0_100_waste_heat",
    "heat_pump_industry_0_100_water",
    "heat_pump_industry_100_150_waste_heat",
    "heat_pump_industry_100_150_water",
    "heat_pump_industry_150_200_waste_heat",
    "heat_pump_industry_150_200_water",
    # Intermediate models (v3_0, v4_0-v4_4): split by temperature only
    "heat_pump_industry_0_100",
    "heat_pump_industry_100_150",
    "heat_pump_industry_150_200",
    # Older models (v2_0): single generic industry HP
    "heat_pump_industry",
    # Boilers (consistent across models)
    "biomass_boiler_industry",
    "electrode_boiler_industry",
    "natural_gas_boiler_industry",
    "oil_boiler_industry",  # new in v7_0
    "coal_boiler_industry",  # new in v8_0
    "waste_boiler_industry",  # new in v8_0
    # Very old models (v1_0): "industrial_" prefix naming
    "industrial_biomass_boiler",
    "industrial_coal_boiler",
    "industrial_electrode_boiler",
    "industrial_natural_gas_boiler",
    "industrial_oil_boiler",
]

INDUSTRY_HEAT_TECHS_TEMP_CONV = [
    "heat_industry_temp_conversion_150",
    "heat_industry_temp_conversion_100",
]

INDUSTRY_HEAT_TECHS_PRODUCTION = [
    "glass_production",
    "ceramic_production",
    "paper_production",
    "food_production",
]

INDUSTRY_TES_TECHS = [
    "industry_TES_water_0_100",
    "industry_TES_water_100_150",
    "industry_TES_steam_100_150",  # dropped in v7_0 (no medium-temp steam TES); kept for older runs
    "industry_TES_steam_150_200",
]

INDUSTRY_DSM_TECHS = [
    "ammonia_DSM",
    "ceramic_DSM",
    "clinker_DSM",
    "food_DSM",
    "glass_DSM",
    "methanol_DSM",
    "olefin_DSM",
    "paper_DSM",
    "primary_steel_DSM",
    "secondary_steel_DSM",
]


# ── Data helpers ──────────────────────────────────────────────────────────────
# Each helper takes a single Results object; figure functions call these once
# per run in a loop.

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
    r: Results, techs: list[str], capacity_type: str = "power"
) -> pd.DataFrame:
    cap_add = r.get_total("capacity_addition")
    cap_add = cap_add[cap_add.index.get_level_values("capacity_type") == capacity_type]
    rows = {}
    for tech in techs:
        if tech in cap_add.index.get_level_values("technology"):
            s = cap_add.xs(tech, level="technology").sum()
            if (s.abs() > 1e-6).any():
                rows[tech] = s
    return pd.DataFrame(rows).T if rows else pd.DataFrame()


def get_capacity(
    r: Results, techs: list[str], capacity_type: str = "power"
) -> pd.DataFrame:
    cap = r.get_total("capacity")
    cap = cap[cap.index.get_level_values("capacity_type") == capacity_type]
    rows = {}
    for tech in techs:
        if tech in cap.index.get_level_values("technology"):
            s = cap.xs(tech, level="technology").sum()
            if (s.abs() > 1e-6).any():
                rows[tech] = s
    return pd.DataFrame(rows).T if rows else pd.DataFrame()


def get_heat_demand_by_sector(r: Results, tech: str) -> pd.DataFrame:
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
    try:
        df = r.get_total(flow_type)
        if df.empty or "technology" not in df.index.names:
            return pd.DataFrame()
        rows = {}
        for tech in techs:
            if tech in df.index.get_level_values("technology"):
                s = df.xs(tech, level="technology").sum()
                if (s.abs() > 1e-3).any():
                    rows[tech] = s
        return pd.DataFrame(rows).T if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def get_import_price_eur_per_mwh(r: Results, carrier: str) -> pd.Series:
    pi = r.get_total("price_import")
    if carrier not in pi.index.get_level_values("carrier"):
        return pd.Series(dtype=float)
    return pi.xs(carrier, level="carrier").mean() / HOURS_PER_YEAR * 1000


def _reorder_conversion_last(cons: pd.DataFrame) -> pd.DataFrame:
    """Push temp-conversion techs to the end of the stack order."""
    if cons.empty:
        return cons
    end_use = [t for t in cons.index if t not in INDUSTRY_HEAT_TECHS_TEMP_CONV]
    conv = [t for t in cons.index if t in INDUSTRY_HEAT_TECHS_TEMP_CONV]
    return cons.loc[end_use + conv]


def _filter_boiler_hp(prod: pd.DataFrame) -> pd.DataFrame:
    if prod.empty:
        return prod
    prod = prod[prod.index.isin(INDUSTRY_HEAT_TECHS_BOILERS_HP)]
    return prod[(prod.abs() > 1e-3).any(axis=1)]


# ── Figure functions ──────────────────────────────────────────────────────────
# Every metric is drawn as len(runs) adjacent axes, one per run.

def fig_carrier_energy_all(runs: list[Run]) -> plt.Figure:
    """One row per carrier per metric (production, then consumption), one axis per run."""
    names = [r.label for r in runs]
    n = len(INDUSTRY_HEAT_CARRIERS_ENERGY)
    rows = n * 2
    fig, axes = plt.subplots(rows, len(runs), figsize=(fig_width_for_runs(len(runs)), 6.5 * rows),
                             squeeze=False)
    fig.suptitle("Industry Heat Carriers — Production & Consumption",
                 fontsize=13, fontweight="bold")
    for i, carrier in enumerate(INDUSTRY_HEAT_CARRIERS_ENERGY):
        label = carrier.replace("_", " ").title()
        prod_dfs = [get_carrier_production(r.results, carrier) for r in runs]
        cons_dfs = [_reorder_conversion_last(get_carrier_consumption(r.results, carrier)) for r in runs]
        row_prod, row_cons = i * 2, i * 2 + 1
        plot_stacked_bars_years_n(list(axes[row_prod, :]), prod_dfs,
                                  f"{label} — Production", "GWh", names)
        plot_stacked_bars_years_n(list(axes[row_cons, :]), cons_dfs,
                                  f"{label} — Consumption", "GWh", names)
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    return fig


def fig_carrier_products_production(runs: list[Run]) -> plt.Figure:
    """One row per product (glass, ceramic, paper, food): annual production, one axis per run."""
    names = [r.label for r in runs]
    n = len(INDUSTRY_HEAT_CARRIERS_PRODUCT)
    # Half-height rows (3.25 * n instead of 6.5 * n) so product plots stay compact.
    fig, axes = plt.subplots(n, len(runs), figsize=(fig_width_for_runs(len(runs)), 3.25 * n),
                             squeeze=False)
    fig.suptitle("Industry Product Carriers — Annual Production",
                 fontsize=13, fontweight="bold")
    for row, carrier in enumerate(INDUSTRY_HEAT_CARRIERS_PRODUCT):
        prod_dfs = [get_carrier_production(r.results, carrier) for r in runs]
        plot_stacked_bars_years_n(list(axes[row, :]), prod_dfs, carrier.title(), "GWh-eq", names)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    return fig


def fig_boiler_hp_production(runs: list[Run]) -> plt.Figure:
    """One row per temperature level: boiler & HP output (one axis per run), with NG price overlay."""
    names = [r.label for r in runs]
    ng_prices = [get_import_price_eur_per_mwh(r.results, "natural_gas") for r in runs]
    n = len(INDUSTRY_HEAT_CARRIERS_ENERGY)
    fig, axes = plt.subplots(n, len(runs), figsize=(fig_width_for_runs(len(runs)), 6.5 * n),
                             squeeze=False)
    fig.suptitle("Industry Heat — Boiler & HP Production (excl. temp conversion)\n"
                 "Right axis: natural gas import price [EUR/MWh]",
                 fontsize=12, fontweight="bold")
    for row, carrier in enumerate(INDUSTRY_HEAT_CARRIERS_ENERGY):
        prod_dfs = [_filter_boiler_hp(get_carrier_production(r.results, carrier)) for r in runs]
        label = carrier.replace("_", " ").title()
        plot_stacked_bars_years_n(list(axes[row, :]), prod_dfs, label, "GWh", names)
        for i, price in enumerate(ng_prices):
            add_price_line(axes[row, i], price, "NG import [EUR/MWh]", "#8b0000")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    return fig


def fig_capacity_heat_supply(runs: list[Run]) -> plt.Figure:
    """4 rows x len(runs) cols: capacity addition & total for boilers+HPs and temp-conversion."""
    names = [r.label for r in runs]
    fig, axes = plt.subplots(4, len(runs), figsize=(fig_width_for_runs(len(runs)), 26),
                             squeeze=False)
    fig.suptitle("Industry Heat Supply — Capacity Addition & Total",
                 fontsize=13, fontweight="bold")
    plot_stacked_bars_years_n(
        list(axes[0, :]),
        [get_capacity_addition(r.results, INDUSTRY_HEAT_TECHS_BOILERS_HP) for r in runs],
        "Capacity Addition — Boilers & HPs", "GW", names,
    )
    plot_stacked_bars_years_n(
        list(axes[1, :]),
        [get_capacity_addition(r.results, INDUSTRY_HEAT_TECHS_TEMP_CONV) for r in runs],
        "Capacity Addition — Temp Conversion", "GW", names,
    )
    plot_stacked_bars_years_n(
        list(axes[2, :]),
        [get_capacity(r.results, INDUSTRY_HEAT_TECHS_BOILERS_HP) for r in runs],
        "Total Capacity — Boilers & HPs", "GW", names,
    )
    plot_stacked_bars_years_n(
        list(axes[3, :]),
        [get_capacity(r.results, INDUSTRY_HEAT_TECHS_TEMP_CONV) for r in runs],
        "Total Capacity — Temp Conversion", "GW", names,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    return fig


def fig_capacity_production(runs: list[Run]) -> plt.Figure:
    """2 rows x len(runs) cols: capacity addition and total for production techs."""
    names = [r.label for r in runs]
    fig, axes = plt.subplots(2, len(runs), figsize=(fig_width_for_runs(len(runs)), 13),
                             squeeze=False)
    fig.suptitle("Industry Production Technologies — Capacity",
                 fontsize=13, fontweight="bold")
    plot_stacked_bars_years_n(
        list(axes[0, :]),
        [get_capacity_addition(r.results, INDUSTRY_HEAT_TECHS_PRODUCTION) for r in runs],
        "Capacity Addition", "ton/h", names,
    )
    plot_stacked_bars_years_n(
        list(axes[1, :]),
        [get_capacity(r.results, INDUSTRY_HEAT_TECHS_PRODUCTION) for r in runs],
        "Total Capacity", "ton/h", names,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_tes_capacity_addition(runs: list[Run]) -> plt.Figure:
    """2 rows x len(runs) cols: TES energy and power capacity addition."""
    names = [r.label for r in runs]
    fig, axes = plt.subplots(2, len(runs), figsize=(fig_width_for_runs(len(runs)), 13),
                             squeeze=False)
    fig.suptitle("Industry TES — Capacity Addition", fontsize=13, fontweight="bold")
    plot_stacked_bars_years_n(
        list(axes[0, :]),
        [get_capacity_addition(r.results, INDUSTRY_TES_TECHS, "energy") for r in runs],
        "Energy Capacity Addition", "GWh", names,
    )
    plot_stacked_bars_years_n(
        list(axes[1, :]),
        [get_capacity_addition(r.results, INDUSTRY_TES_TECHS, "power") for r in runs],
        "Power Capacity Addition", "GW", names,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_tes_charge_discharge(runs: list[Run]) -> plt.Figure:
    """2 rows x len(runs) cols: TES charge and discharge."""
    names = [r.label for r in runs]
    fig, axes = plt.subplots(2, len(runs), figsize=(fig_width_for_runs(len(runs)), 13),
                             squeeze=False)
    fig.suptitle("Industry TES — Charge & Discharge", fontsize=13, fontweight="bold")
    plot_stacked_bars_years_n(
        list(axes[0, :]),
        [get_storage_flows(r.results, INDUSTRY_TES_TECHS, "flow_storage_charge") for r in runs],
        "Charge", "GWh", names,
    )
    plot_stacked_bars_years_n(
        list(axes[1, :]),
        [get_storage_flows(r.results, INDUSTRY_TES_TECHS, "flow_storage_discharge") for r in runs],
        "Discharge", "GWh", names,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


# Display label -> production technology, used by the Heat Capacity sector dropdown.
PRODUCTION_SECTORS = {
    "Glass": "glass_production",
    "Ceramic": "ceramic_production",
    "Paper": "paper_production",
    "Food": "food_production",
}


def fig_heat_demand_by_sector(runs: list[Run], year: int) -> plt.Figure:
    """Heat input by temperature level for all production sectors in ONE chosen year.

    One stacked bar per sector (x-axis: Glass / Ceramic / Paper / Food), each
    stacked by heat-carrier temperature level, one axis per run. The user
    picks the year via a dropdown in the app.
    """
    def build(r: Results) -> pd.DataFrame:
        """DataFrame indexed by temperature carrier, one column per sector, for `year`."""
        cols: dict[str, pd.Series] = {}
        for label, tech in PRODUCTION_SECTORS.items():
            df = get_heat_demand_by_sector(r, tech)  # index=carrier, columns=years
            if df.empty:
                continue
            col = None
            for key in (year, str(year)):
                if key in df.columns:
                    col = df[key]
                    break
            if col is not None and (col.abs() > 1e-3).any():
                cols[label] = col
        return pd.DataFrame(cols).fillna(0) if cols else pd.DataFrame()

    names = [r.label for r in runs]
    dfs = [build(r.results) for r in runs]

    fig, axes = plt.subplots(1, len(runs), figsize=(fig_width_for_runs(len(runs)), 7), squeeze=False)
    fig.suptitle(f"Industry Sectors — Heat Input by Temperature Level ({year})",
                 fontsize=13, fontweight="bold")
    plot_stacked_bars_years_n(list(axes[0, :]), dfs, "Heat Input by Sector", "GWh", names)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    return fig


def fig_dsm_capacity_addition(runs: list[Run]) -> plt.Figure:
    """2 rows x len(runs) cols: DSM energy and power capacity addition."""
    names = [r.label for r in runs]
    fig, axes = plt.subplots(2, len(runs), figsize=(fig_width_for_runs(len(runs)), 13),
                             squeeze=False)
    fig.suptitle("Industry DSM — Capacity Addition", fontsize=13, fontweight="bold")
    plot_stacked_bars_years_n(
        list(axes[0, :]),
        [get_capacity_addition(r.results, INDUSTRY_DSM_TECHS, "energy") for r in runs],
        "Energy Capacity Addition", "ktproduct", names,
    )
    plot_stacked_bars_years_n(
        list(axes[1, :]),
        [get_capacity_addition(r.results, INDUSTRY_DSM_TECHS, "power") for r in runs],
        "Power Capacity Addition", "ktproduct/h", names,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_dsm_charge_discharge(runs: list[Run]) -> plt.Figure:
    """2 rows x len(runs) cols: DSM charge and discharge."""
    names = [r.label for r in runs]
    fig, axes = plt.subplots(2, len(runs), figsize=(fig_width_for_runs(len(runs)), 13),
                             squeeze=False)
    fig.suptitle("Industry DSM — Charge & Discharge", fontsize=13, fontweight="bold")
    plot_stacked_bars_years_n(
        list(axes[0, :]),
        [get_storage_flows(r.results, INDUSTRY_DSM_TECHS, "flow_storage_charge") for r in runs],
        "Charge", "ktproduct", names,
    )
    plot_stacked_bars_years_n(
        list(axes[1, :]),
        [get_storage_flows(r.results, INDUSTRY_DSM_TECHS, "flow_storage_discharge") for r in runs],
        "Discharge", "ktproduct", names,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_storage_comparison(runs: list[Run]) -> plt.Figure:
    """3 rows x len(runs) cols: capacity addition comparison across TES, battery, and DSM."""
    names = [r.label for r in runs]
    fig, axes = plt.subplots(3, len(runs), figsize=(fig_width_for_runs(len(runs)), 19.5),
                             squeeze=False)
    fig.suptitle("Storage Technologies — Capacity Addition", fontsize=13, fontweight="bold")
    plot_stacked_bars_years_n(
        list(axes[0, :]),
        [get_capacity_addition(r.results, INDUSTRY_TES_TECHS + ["battery"], "energy") for r in runs],
        "Energy Capacity\nTES + Battery", "GWh", names,
    )
    plot_stacked_bars_years_n(
        list(axes[1, :]),
        [get_capacity_addition(r.results, INDUSTRY_TES_TECHS + ["battery", "pumped_hydro"], "power")
         for r in runs],
        "Power Capacity\nTES + Battery + Pumped Hydro", "GW", names,
    )
    plot_stacked_bars_years_n(
        list(axes[2, :]),
        [get_capacity_addition(r.results, INDUSTRY_DSM_TECHS, "power") for r in runs],
        "DSM Power Capacity", "ktproduct/h", names,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


# ── Electricity system ────────────────────────────────────────────────────────

def get_electricity_producing_techs(r: Results) -> list[str]:
    """Technologies whose conversion output includes the electricity carrier."""
    prod = get_carrier_production(r, "electricity")
    return prod.index.tolist() if not prod.empty else []


def _carrier_year_series(r: Results, variable: str, carrier: str) -> pd.Series:
    """Per-year total for a carrier from `variable` (summing all other dims)."""
    try:
        df = r.get_total(variable)
        if df is None or df.empty or "carrier" not in df.index.names:
            return pd.Series(dtype=float)
        if carrier not in df.index.get_level_values("carrier"):
            return pd.Series(dtype=float)
        sub = df.xs(carrier, level="carrier")
        s = sub.sum()  # sum over remaining index dims -> per-year (columns) totals
        return s if isinstance(s, pd.Series) else pd.Series(dtype=float)
    except Exception:
        return pd.Series(dtype=float)


def get_electricity_balance(r: Results) -> pd.DataFrame:
    """Per-year electricity balance: production, consumption, net import, battery net.

    Rows = years, columns = components. Missing components (e.g. no export
    variable, no battery) are tolerated and simply contribute zeros.
    """
    prod = get_carrier_production(r, "electricity")
    cons = get_carrier_consumption(r, "electricity")
    prod_tot = prod.sum() if not prod.empty else pd.Series(dtype=float)
    cons_tot = cons.sum() if not cons.empty else pd.Series(dtype=float)

    imp = _carrier_year_series(r, "flow_import", "electricity")
    exp = _carrier_year_series(r, "flow_export", "electricity")
    if imp.empty and exp.empty:
        net_imp = pd.Series(dtype=float)
    else:
        net_imp = imp.subtract(exp, fill_value=0.0)

    dis = get_storage_flows(r, ["battery"], "flow_storage_discharge")
    cha = get_storage_flows(r, ["battery"], "flow_storage_charge")
    dis_tot = dis.sum() if not dis.empty else pd.Series(dtype=float)
    cha_tot = cha.sum() if not cha.empty else pd.Series(dtype=float)
    if dis_tot.empty and cha_tot.empty:
        bat_net = pd.Series(dtype=float)
    else:
        bat_net = dis_tot.subtract(cha_tot, fill_value=0.0)

    df = pd.DataFrame({
        "Production": prod_tot,
        "Consumption": cons_tot,
        "Net Import": net_imp,
        "Battery Net": bat_net,
    }).fillna(0.0)
    # Keep only real calendar-year rows.
    df = df[[isinstance(i, (int, float)) and float(i) > 1000 for i in df.index]]
    return df.sort_index()


_BALANCE_COLORS = {
    "Production": "#4caf50",
    "Consumption": "#ef5350",
    "Net Import": "#42a5f5",
    "Battery Net": "#7e57c2",
}


def _plot_electricity_balance(
    ax: plt.Axes, df: pd.DataFrame, title: str, name: str, compact: bool = False
) -> None:
    title_fs = 10 if compact else 12
    tick_fs = 8 if compact else 9
    label_fs = 9 if compact else 11
    legend_fs = 7 if compact else 9
    if df.empty:
        ax.set_title(f"{title}\n{name}", fontsize=title_fs, fontweight="bold")
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return
    years = df.index.tolist()
    comps = df.columns.tolist()
    n = len(comps)
    width = 0.8 / max(n, 1)
    x = list(range(len(years)))
    for i, comp in enumerate(comps):
        offsets = [xi + (i - (n - 1) / 2) * width for xi in x]
        ax.bar(offsets, df[comp].values, width, label=comp,
               color=_BALANCE_COLORS.get(comp), edgecolor="white", linewidth=0.4)
    ax.axhline(0, color="black", linewidth=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years], fontsize=tick_fs)
    ax.set_ylabel("GWh", fontsize=label_fs)
    ax.set_title(f"{title}\n{name}", fontsize=title_fs, fontweight="bold")
    ax.legend(fontsize=legend_fs, frameon=False)


def fig_electricity_capacity_production_consumption(runs: list[Run]) -> plt.Figure:
    """3 rows x len(runs) cols: electricity generation capacity, production, consumption."""
    names = [r.label for r in runs]
    techs = [get_electricity_producing_techs(r.results) for r in runs]
    fig, axes = plt.subplots(3, len(runs), figsize=(fig_width_for_runs(len(runs)), 19.5),
                             squeeze=False)
    fig.suptitle("Electricity System — Capacity, Production & Consumption",
                 fontsize=13, fontweight="bold")
    plot_stacked_bars_years_n(
        list(axes[0, :]),
        [get_capacity(r.results, t, "power") for r, t in zip(runs, techs)],
        "Generation Capacity", "GW", names,
    )
    plot_stacked_bars_years_n(
        list(axes[1, :]),
        [get_carrier_production(r.results, "electricity") for r in runs],
        "Production (Generation Mix)", "GWh", names,
    )
    plot_stacked_bars_years_n(
        list(axes[2, :]),
        [get_carrier_consumption(r.results, "electricity") for r in runs],
        "Consumption by Technology", "GWh", names,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    return fig


def fig_electricity_balance(runs: list[Run]) -> plt.Figure:
    """1 row x len(runs) cols: per-year electricity net balance (grouped bars)."""
    fig, axes = plt.subplots(1, len(runs), figsize=(fig_width_for_runs(len(runs)), 6.5),
                             squeeze=False)
    fig.suptitle("Electricity — Net Balance (Production vs Consumption, Import, Battery)",
                 fontsize=13, fontweight="bold")
    compact = len(runs) > 2
    for i, r in enumerate(runs):
        _plot_electricity_balance(axes[0, i], get_electricity_balance(r.results),
                                  "Net Balance", r.label, compact=compact)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


# ── Residual load curve ───────────────────────────────────────────────────────
# Residual load = electricity load − non-dispatchable renewable generation, at
# every hour. It is the load left for dispatchable plants, storage, imports and
# flexibility to cover. Two "load" definitions are offered:
#   • "total"       — exogenous electricity demand + ALL electricity consumed by
#                     conversion technologies (heat pumps, electrode boilers,
#                     electrolysis, EVs, DAC, …). This is the load the power
#                     system actually sees in a sector-coupled model.
#   • "demand_only" — exogenous electricity demand alone (the fixed final demand).
# Battery charging and exports are treated as balancing, not load, so they are
# excluded from both.
#
# NOTE ON TIME RESOLUTION: these runs use time-series aggregation
# (aggregated_time_steps_per_year = 10). get_full_ts() maps the representative
# steps back onto all 8760 hours, so the series is chronologically meaningful but
# contains only ~10 distinct values per year — the curves are a step
# approximation, not a smooth hourly profile. Rendered with step drawstyle to
# stay honest about this.

VRE_TECHS = ["photovoltaics", "wind_onshore", "wind_offshore"]

_RESIDUAL_CACHE: dict = {}


def _elec_ts(df: pd.DataFrame, cols: list[int], techs: list[str] | None = None) -> pd.Series:
    """Sum the electricity rows of a full-ts frame over nodes (and techs) for the
    given year columns, returning an hour-indexed (0..8759) GW series."""
    zeros = pd.Series(0.0, index=range(len(cols)))
    if df is None or df.empty or "carrier" not in (df.index.names or []):
        return zeros
    if "electricity" not in df.index.get_level_values("carrier"):
        return zeros
    sub = df.xs("electricity", level="carrier")
    if techs is not None:
        if "technology" not in (sub.index.names or []):
            return zeros
        sub = sub[sub.index.get_level_values("technology").isin(techs)]
    if sub.empty:
        return zeros
    s = sub[cols].sum(axis=0)
    s.index = range(len(cols))
    return s


def get_residual_load_components(r: Results, year: int) -> pd.DataFrame:
    """Hour-indexed (0..8759) electricity components for one calendar year.

    Columns: vre, exo_demand, conv_input, total_demand. Residual load is derived
    by the caller as (load − vre). Returns an empty frame if the year is absent.
    """
    key = (id(r), year)
    if key in _RESIDUAL_CACHE:
        return _RESIDUAL_CACHE[key]

    years = get_available_years(r)
    if year not in years:
        return pd.DataFrame()
    yi = years.index(year)
    cols = list(range(yi * HOURS_PER_YEAR, (yi + 1) * HOURS_PER_YEAR))

    try:
        out = r.get_full_ts("flow_conversion_output")
        inp = r.get_full_ts("flow_conversion_input")
        dem = r.get_full_ts("demand")
    except Exception:
        return pd.DataFrame()

    vre = _elec_ts(out, cols, VRE_TECHS)
    exo = _elec_ts(dem, cols)
    conv = _elec_ts(inp, cols)
    df = pd.DataFrame({
        "vre": vre,
        "exo_demand": exo,
        "conv_input": conv,
        "total_demand": exo.add(conv, fill_value=0.0),
    })
    _RESIDUAL_CACHE[key] = df
    return df


_LOAD_COLS = {
    "total": ("total_demand",
              "Total electricity demand (incl. heat pumps, electrolysis, EVs, …)"),
    "demand_only": ("exo_demand",
                    "Exogenous electricity demand only"),
}
_C_LOAD = "#37474f"      # dark grey — load
_C_VRE = "#f0a020"       # amber — VRE generation
_C_POS = "#ef5350"       # red — positive residual (must be covered)
_C_NEG = "#4caf50"       # green — negative residual (renewable surplus)
_C_RESID = "#b71c1c"     # dark red — residual duration line


def _plot_residual_chrono(
    ax: plt.Axes, comp: pd.DataFrame, load_col: str, title: str, name: str,
    compact: bool = False,
) -> None:
    title_fs = 10 if compact else 11
    label_fs = 9 if compact else 10
    legend_fs = 7 if compact else 8
    if comp.empty:
        ax.set_title(f"{title}\n{name}", fontsize=title_fs, fontweight="bold")
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return
    hrs = comp.index
    load = comp[load_col]
    vre = comp["vre"]
    resid = load - vre
    ax.fill_between(hrs, 0, resid, where=(resid >= 0), step="post",
                    color=_C_POS, alpha=0.55, label="Residual load (> 0)")
    ax.fill_between(hrs, 0, resid, where=(resid < 0), step="post",
                    color=_C_NEG, alpha=0.55, label="Renewable surplus (< 0)")
    ax.plot(hrs, load, color=_C_LOAD, lw=0.8, drawstyle="steps-post", label="Load")
    ax.plot(hrs, vre, color=_C_VRE, lw=0.9, drawstyle="steps-post", label="VRE generation")
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xlim(0, HOURS_PER_YEAR)
    ax.set_xlabel("Hour of year", fontsize=label_fs)
    ax.set_ylabel("GW", fontsize=label_fs)
    ax.set_title(f"{title}\n{name}", fontsize=title_fs, fontweight="bold")
    ax.legend(fontsize=legend_fs, frameon=False, ncol=2, loc="upper right")


def _plot_residual_duration(
    ax: plt.Axes, comp: pd.DataFrame, load_col: str, title: str, name: str,
    compact: bool = False,
) -> None:
    title_fs = 10 if compact else 11
    label_fs = 9 if compact else 10
    legend_fs = 7 if compact else 8
    annot_fs = 7 if compact else 8
    if comp.empty:
        ax.set_title(f"{title}\n{name}", fontsize=title_fs, fontweight="bold")
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return
    load_sorted = comp[load_col].sort_values(ascending=False).to_numpy()
    resid_sorted = (comp[load_col] - comp["vre"]).sort_values(ascending=False).to_numpy()
    x = range(len(load_sorted))
    ax.plot(x, load_sorted, color=_C_LOAD, lw=1.3, drawstyle="steps-post",
            label="Load duration curve")
    ax.fill_between(x, 0, resid_sorted, where=(resid_sorted >= 0), step="post",
                    color=_C_POS, alpha=0.45)
    ax.fill_between(x, 0, resid_sorted, where=(resid_sorted < 0), step="post",
                    color=_C_NEG, alpha=0.45)
    ax.plot(x, resid_sorted, color=_C_RESID, lw=1.4, drawstyle="steps-post",
            label="Residual load duration curve")
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xlim(0, HOURS_PER_YEAR)
    ax.set_xlabel("Hours (sorted, descending)", fontsize=label_fs)
    ax.set_ylabel("GW", fontsize=label_fs)
    ax.set_title(f"{title}\n{name}", fontsize=title_fs, fontweight="bold")
    # Annotate peak residual and surplus hours.
    surplus_h = int((resid_sorted < 0).sum())
    ax.text(0.98, 0.06,
            f"peak residual {resid_sorted.max():,.0f} GW\n"
            f"surplus in {surplus_h:,} h/yr",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=annot_fs,
            bbox=dict(boxstyle="round", fc="white", ec="0.7", alpha=0.8))
    ax.legend(fontsize=legend_fs, frameon=False, loc="upper right")


def fig_residual_load(runs: list[Run], year: int, mode: str = "total") -> plt.Figure:
    """2 rows x len(runs) cols residual-load figure for one year, one column per run.

    Row 1: chronological residual load (with load & VRE reference lines).
    Row 2: load duration curve + residual load duration curve.
    `mode` selects the load definition: "total" or "demand_only".
    """
    load_col, load_label = _LOAD_COLS[mode]
    comps = [get_residual_load_components(r.results, year) for r in runs]
    fig, axes = plt.subplots(2, len(runs), figsize=(fig_width_for_runs(len(runs)), 12),
                             squeeze=False)
    fig.suptitle(f"Residual Load — {load_label}  ·  {year}",
                 fontsize=13, fontweight="bold")
    compact = len(runs) > 2
    for i, (run, comp) in enumerate(zip(runs, comps)):
        _plot_residual_chrono(axes[0, i], comp, load_col, "Chronological", run.label, compact=compact)
        _plot_residual_duration(axes[1, i], comp, load_col, "Duration curve", run.label, compact=compact)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


# ── Storage use ───────────────────────────────────────────────────────────────
# Which storages balance the residual load, and how they operate.
#   • Bulk storages (all carriers) — annual energy discharged, per year.
#   • Electricity storages — chronological net dispatch for the selected year:
#     positive = discharging to the grid (covering deficit), negative = charging
#     from a renewable surplus. This mirrors the residual load curve above.
# TES/DSM flexibility is shown in the Flexibility tab and omitted here.

BULK_STORAGE_TECHS = [
    "battery", "pumped_hydro", "natural_gas_storage",
    "oil_storage", "salt_cavern_storage",
]
ELEC_STORAGE_TECHS = ["battery", "pumped_hydro"]


def _tech_ts(df: pd.DataFrame, cols: list[int], tech: str) -> pd.Series:
    """Sum one technology's rows of a full-ts frame over nodes for the given
    year columns, returning an hour-indexed (0..8759) GW series."""
    zeros = pd.Series(0.0, index=range(len(cols)))
    if df is None or df.empty or "technology" not in (df.index.names or []):
        return zeros
    if tech not in df.index.get_level_values("technology"):
        return zeros
    s = df.xs(tech, level="technology")[cols].sum(axis=0)
    s.index = range(len(cols))
    return s


def get_storage_net_ts(r: Results, techs: list[str], year: int) -> pd.DataFrame:
    """Hour-indexed (0..8759) net storage output (discharge − charge) per tech
    for one calendar year. Positive = to grid, negative = from grid."""
    years = get_available_years(r)
    if year not in years:
        return pd.DataFrame()
    yi = years.index(year)
    cols = list(range(yi * HOURS_PER_YEAR, (yi + 1) * HOURS_PER_YEAR))
    try:
        cha = r.get_full_ts("flow_storage_charge")
        dis = r.get_full_ts("flow_storage_discharge")
    except Exception:
        return pd.DataFrame()
    data = {}
    for tech in techs:
        net = _tech_ts(dis, cols, tech) - _tech_ts(cha, cols, tech)
        if (net.abs() > 1e-3).any():
            data[tech] = net
    return pd.DataFrame(data)


def _plot_storage_dispatch(
    ax: plt.Axes, net: pd.DataFrame, title: str, name: str, compact: bool = False
) -> None:
    """Net-power duration curve: each series sorted high→low. Battery cycles
    charge↔discharge every hour, so a chronological line is unreadable; sorting
    turns it into a monotonic curve showing how many hours it discharges (>0) vs
    charges (<0) and at what power."""
    title_fs = 10 if compact else 11
    label_fs = 9 if compact else 10
    legend_fs = 7 if compact else 8
    if net.empty:
        ax.set_title(f"{title}\n{name}", fontsize=title_fs, fontweight="bold")
        ax.text(0.5, 0.5, "No electricity-storage use", ha="center", va="center",
                transform=ax.transAxes)
        return
    total_sorted = net.sum(axis=1).sort_values(ascending=False).to_numpy()
    x = range(len(total_sorted))
    ax.fill_between(x, 0, total_sorted, where=(total_sorted >= 0), step="post",
                    color="#42a5f5", alpha=0.4, label="Discharging (to grid)")
    ax.fill_between(x, 0, total_sorted, where=(total_sorted < 0), step="post",
                    color="#ff9800", alpha=0.4, label="Charging (from surplus)")
    for tech in net.columns:
        s = net[tech].sort_values(ascending=False).to_numpy()
        ax.plot(x, s, lw=1.3, color=COLOR_MAP.get(tech), label=tech.replace("_", " "))
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xlim(0, HOURS_PER_YEAR)
    ax.set_xlabel("Hours (sorted, descending)", fontsize=label_fs)
    ax.set_ylabel("GW", fontsize=label_fs)
    ax.set_title(f"{title}\n{name}", fontsize=title_fs, fontweight="bold")
    ax.legend(fontsize=legend_fs, frameon=False, ncol=2, loc="upper right")


def fig_storage_use(runs: list[Run], year: int) -> plt.Figure:
    """2 rows x len(runs) cols storage figure, one column per run.

    Row 1: annual energy discharged per storage technology (all bulk storages).
    Row 2: chronological net electricity-storage dispatch for `year`.
    """
    names = [r.label for r in runs]
    fig, axes = plt.subplots(2, len(runs), figsize=(fig_width_for_runs(len(runs)), 12),
                             squeeze=False)
    fig.suptitle(f"Storage Use  ·  net-power duration panel for {year}",
                 fontsize=13, fontweight="bold")
    plot_stacked_bars_years_n(
        list(axes[0, :]),
        [get_storage_flows(r.results, BULK_STORAGE_TECHS, "flow_storage_discharge") for r in runs],
        "Annual Energy Discharged by Storage", "GWh", names,
    )
    compact = len(runs) > 2
    for i, r in enumerate(runs):
        _plot_storage_dispatch(axes[1, i], get_storage_net_ts(r.results, ELEC_STORAGE_TECHS, year),
                               "Electricity Storage — Net Power Duration", r.label, compact=compact)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    return fig
