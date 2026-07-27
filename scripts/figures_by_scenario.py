"""N-run cost/emissions comparison figures: all runs as x-axis categories on a
single axis, one year at a time (see figures_by_run.py for the small-multiples,
one-axis-per-run, multi-year layout instead). Used by both the Streamlit
dashboard (streamlit/app.py) and standalone scripts (e.g. generate_si_figures.py).

Data helpers use xs-per-entity instead of groupby().sum()[year] because
zen_garden's get_total() may return years as index levels (not columns)
depending on the variable and model type. The xs+sum approach works for
both 1ts and multi-timestep models.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from zen_garden import Results

from figure_settings import SCENARIO_PALETTE, Run, get_available_years, plot_stacked_bars

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

INDUSTRY_PROCESS_TECHS = [
    "cement_kiln", "cement_post_comb", "biomass_to_cement_fuel",
    "coal_to_cement_fuel", "hydrogen_to_cement_fuel", "waste_to_cement_fuel",
    "BF_BOF", "BF_BOF_CCS", "EAF", "NG_DRI", "NG_DRI_CCS", "H2_DRI",
    "glass_production", "ceramic_production", "paper_production", "food_production",
]

INDUSTRY_HEATING_TECHS = [
    # Boilers (consistent across models)
    "natural_gas_boiler_industry", "electrode_boiler_industry", "biomass_boiler_industry",
    "oil_boiler_industry",  # new in v7_0
    # New models (v4_6+): split by temperature + source
    "heat_pump_industry_0_100_waste_heat", "heat_pump_industry_0_100_water",
    "heat_pump_industry_100_150_waste_heat", "heat_pump_industry_100_150_water",
    "heat_pump_industry_150_200_waste_heat", "heat_pump_industry_150_200_water",
    # Intermediate models (v3_0, v4_0-v4_4): split by temperature only
    "heat_pump_industry_0_100", "heat_pump_industry_100_150", "heat_pump_industry_150_200",
    # Older models (v2_0): single generic industry HP
    "heat_pump_industry",
    # Very old models (v1_0): "industrial_" prefix naming
    "industrial_biomass_boiler", "industrial_coal_boiler",
    "industrial_electrode_boiler", "industrial_natural_gas_boiler", "industrial_oil_boiler",
]

HEAT_TECHS = [
    "natural_gas_boiler", "biomass_boiler", "heat_pump",
    "electrode_boiler", "oil_boiler", "district_heating_grid",
]

DISTRICT_HEAT_TECHS = [
    "natural_gas_boiler_DH", "hard_coal_boiler_DH", "waste_boiler_DH",
    "biomass_boiler_DH", "oil_boiler_DH", "heat_pump_DH", "electrode_boiler_DH",
]


# ── Core data access helpers ──────────────────────────────────────────────────

def _xs_get_year(df: pd.DataFrame, level: str, value: str, year: int) -> float:
    """XS-select `value` from `level`, sum all remaining dims, return value for `year`."""
    try:
        s = df.xs(value, level=level).sum()
        if isinstance(s, pd.Series):
            for key in [year, str(year)]:
                if key in s.index:
                    return float(s[key])
            # Try coercing index to int
            try:
                int_idx = {int(k): v for k, v in s.items()}
                return float(int_idx.get(year, 0.0))
            except (TypeError, ValueError):
                pass
        elif isinstance(s, (int, float)):
            return float(s)
    except Exception:
        pass
    return 0.0


def _series_from_level(df: pd.DataFrame, level: str, year: int, threshold: float = 1e-6) -> pd.Series:
    """Build a Series {entity: value_at_year} by xs-ing each unique entity in `level`."""
    try:
        if level not in df.index.names:
            return pd.Series(dtype=float)
        entities = df.index.get_level_values(level).unique()
        results = {e: _xs_get_year(df, level, e, year) for e in entities}
        s = pd.Series({k: v for k, v in results.items() if abs(v) > threshold})
        return s.sort_values(ascending=False)
    except Exception:
        return pd.Series(dtype=float)


def _get_annual_scalar(r: Results, variable: str, year: int) -> float | None:
    """Safely extract a scalar annual metric for a given year."""
    try:
        data = r.get_total(variable)
        if isinstance(data, pd.Series):
            for key in [year, str(year)]:
                if key in data.index:
                    return float(data[key])
            try:
                int_idx = {int(k): v for k, v in data.items()}
                return float(int_idx[year])
            except (KeyError, TypeError, ValueError):
                pass
        elif isinstance(data, pd.DataFrame):
            if year in data.columns:
                return float(data[year].sum())
            elif year in data.index:
                return float(data.loc[year].sum())
    except Exception:
        pass
    return None


# ── Data helpers ──────────────────────────────────────────────────────────────

def get_emissions_by_carrier(r: Results, year: int) -> pd.Series:
    try:
        return _series_from_level(r.get_total("carbon_emissions_carrier"), "carrier", year)
    except Exception:
        return pd.Series(dtype=float)


def get_emissions_by_technology(r: Results, year: int) -> pd.Series:
    try:
        return _series_from_level(r.get_total("carbon_emissions_technology"), "technology", year)
    except Exception:
        return pd.Series(dtype=float)


def get_capex_by_technology(r: Results, year: int) -> pd.Series:
    try:
        return _series_from_level(r.get_total("cost_capex_yearly"), "technology", year)
    except Exception:
        return pd.Series(dtype=float)


def get_opex_by_technology(r: Results, year: int) -> pd.Series:
    try:
        return _series_from_level(r.get_total("cost_opex_yearly"), "technology", year)
    except Exception:
        return pd.Series(dtype=float)


def get_fuel_consumption(r: Results, carrier: str, year: int) -> pd.Series:
    try:
        flow_in = r.get_total("flow_conversion_input")
        if "carrier" not in flow_in.index.names:
            return pd.Series(dtype=float)
        if carrier not in flow_in.index.get_level_values("carrier"):
            return pd.Series(dtype=float)
        sub = flow_in.xs(carrier, level="carrier")
        return _series_from_level(sub, "technology", year, threshold=1e-3)
    except Exception:
        return pd.Series(dtype=float)


def get_fuel_supply(r: Results, carrier: str, year: int) -> pd.Series:
    pieces: dict[str, float] = {}
    try:
        imp = r.get_total("flow_import")
        if "carrier" in imp.index.names and carrier in imp.index.get_level_values("carrier"):
            val = _xs_get_year(imp, "carrier", carrier, year)
            if abs(val) > 1e-3:
                pieces[f"{carrier} import"] = val
    except Exception:
        pass
    try:
        flow_out = r.get_total("flow_conversion_output")
        if "carrier" in flow_out.index.names and carrier in flow_out.index.get_level_values("carrier"):
            sub = flow_out.xs(carrier, level="carrier")
            by_tech = _series_from_level(sub, "technology", year, threshold=1e-3)
            pieces.update(by_tech.to_dict())
    except Exception:
        pass
    return pd.Series(pieces).sort_values(ascending=False)


def _annual_series(r: Results, variable: str, years: list[int]) -> pd.Series:
    """Per-year total of `variable`, summed over all non-year dimensions.

    Handles both shapes zen_garden returns: a Series indexed by year, or a
    DataFrame with years as columns (extra dims on the row index).
    """
    try:
        data = r.get_total(variable)
    except Exception:
        return pd.Series(dtype=float)
    if data is None:
        return pd.Series(dtype=float)
    if isinstance(data, pd.DataFrame):
        s = data.sum(axis=0)            # collapse row dims -> per-year (columns)
    elif isinstance(data, pd.Series):
        s = data
    else:
        return pd.Series(dtype=float)
    lookup: dict[int, float] = {}
    for k, v in s.items():
        try:
            lookup[int(k)] = float(v)   # normalise year keys to int
        except (TypeError, ValueError):
            continue
    return pd.Series({y: lookup[y] for y in years if y in lookup}).sort_index()


def _discount_factors(r: Results, years: list[int]) -> pd.Series:
    """Per-period discount factor = net_present_cost / cost_total.

    zen_garden reports net_present_cost as the discounted, interval-aggregated
    cost of each optimised period and cost_total as its undiscounted
    counterpart, so their ratio converts any undiscounted per-period cost
    component into its net present value.
    """
    npc = _annual_series(r, "net_present_cost", years)
    ct = _annual_series(r, "cost_total", years)
    df = npc.divide(ct).replace([np.inf, -np.inf], np.nan)
    return df.reindex(years).fillna(0.0)


def get_annual_cost(
    r: Results, years: list[int], variable: str, discount: bool = True
) -> pd.Series:
    """Per-year cost for `variable`, optionally converted to net present value."""
    s = _annual_series(r, variable, years)
    if discount and not s.empty:
        s = s.multiply(_discount_factors(r, years)).dropna()
    return s.sort_index()


def get_annual_total_cost(
    r: Results, years: list[int], discount: bool = True
) -> pd.Series:
    """Total system cost per year across ALL components.

    Covers technology CAPEX + OPEX, carrier (fuel/import) cost and carbon
    emission cost — i.e. the full objective, not just technology CAPEX+OPEX.
    Discounted to net present value by default (`net_present_cost`); pass
    discount=False for the raw undiscounted total (`cost_total`).
    """
    return _annual_series(r, "net_present_cost" if discount else "cost_total", years)


def get_summary_metrics(runs: list[Run], year: int) -> dict[str, dict]:
    """Emissions/CAPEX/OPEX for `year`, keyed by run name."""
    return {
        run.name: {
            "label": run.label,
            "em": _get_annual_scalar(run.results, "carbon_emissions_annual", year),
            "capex": _get_annual_scalar(run.results, "cost_capex_yearly_total", year),
            "opex": _get_annual_scalar(run.results, "cost_opex_yearly_total", year),
        }
        for run in runs
    }


# ── Utility functions ─────────────────────────────────────────────────────────

def build_comparison_df(named_series: list[tuple[str, pd.Series]]) -> pd.DataFrame:
    """Combine per-run series into one DataFrame (columns = run labels), sorted
    by the first (baseline) run's values ascending."""
    combined = pd.DataFrame({name: s for name, s in named_series}).fillna(0)
    baseline_name = named_series[0][0]
    return combined.sort_values(baseline_name, ascending=True)


def filter_techs(series: pd.Series, tech_list: list[str], threshold: float = 1e-6) -> pd.Series:
    present = [t for t in tech_list if t in series.index]
    if not present:
        return pd.Series(dtype=float)
    filtered = series.loc[present]
    return filtered[filtered.abs() > threshold].sort_values(ascending=False)


# ── Figure functions ──────────────────────────────────────────────────────────

def fig_emissions(runs: list[Run], year: int) -> plt.Figure:
    """Total system emissions: carriers + technologies, one column per run."""
    names = [r.label for r in runs]
    em_all = []
    for r in runs:
        em_carrier = get_emissions_by_carrier(r.results, year)
        em_tech = get_emissions_by_technology(r.results, year)
        em_all.append(pd.concat([
            em_carrier.rename(lambda c: f"{c} (carrier)"),
            em_tech.rename(lambda t: f"{t} (tech)"),
        ]))
    df = build_comparison_df(list(zip(names, em_all)))

    fig, ax = plt.subplots(figsize=(10, 9))
    fig.suptitle(f"Total System Emissions — Year {year}", fontsize=13, fontweight="bold")
    plot_stacked_bars(df, "", "Mton CO₂eq", ax, show_segment_labels=False)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_costs_total(runs: list[Run], year: int) -> plt.Figure:
    """Total system CAPEX & OPEX, one column per run."""
    names = [r.label for r in runs]
    capexes = [get_capex_by_technology(r.results, year) for r in runs]
    opexes = [get_opex_by_technology(r.results, year) for r in runs]

    # Tall figure so the long per-technology legend fits without dominating.
    fig, axes = plt.subplots(1, 2, figsize=(16, 16))
    fig.suptitle(f"Total System Costs — Year {year}", fontsize=13, fontweight="bold")
    plot_stacked_bars(build_comparison_df(list(zip(names, capexes))),
                      "CAPEX by Technology", "MEUR", axes[0])
    plot_stacked_bars(build_comparison_df(list(zip(names, opexes))),
                      "OPEX by Technology", "MEUR", axes[1])
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    return fig


def _cost_over_time_figure(
    series_by_run: list[tuple[str, pd.Series]], suptitle: str,
) -> plt.Figure:
    """2×2 over-time figure for N per-year cost series (series_by_run[0] = baseline).

    Top row: annual and cumulative cost (absolute), one line per run. Bottom
    row: each non-baseline run's delta vs the baseline (annual and
    cumulative). Each run's horizon total (the sum over all years) is shown
    in the legends, so the discounted grand totals can be compared directly.
    The crossover annotation (marks the year the cheaper run switches) only
    applies when there is exactly one delta series (2 runs total) — with
    more than one it would clutter the chart.
    """
    baseline_name, baseline_s = series_by_run[0]
    other_runs = series_by_run[1:]
    totals = {name: float(s.sum()) for name, s in series_by_run}

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle(suptitle, fontsize=13, fontweight="bold")

    baseline_cum = baseline_s.cumsum()
    for i, (name, s) in enumerate(series_by_run):
        color = SCENARIO_PALETTE[i % len(SCENARIO_PALETTE)]
        cum = s.cumsum()
        ax1.plot(s.index, s.values, marker="o", color=color,
                 label=f"{name}  (Σ = {totals[name]:,.0f})")
        ax2.plot(cum.index, cum.values, marker="o", color=color,
                 label=f"{name}  (total = {totals[name]:,.0f})")
    ax1.set_title("Annual Cost", fontsize=11, fontweight="bold")
    ax1.set_ylabel("MEUR")
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.3)
    ax2.set_title("Cumulative Cost", fontsize=11, fontweight="bold")
    ax2.set_ylabel("MEUR")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)

    # Delta vs baseline — annual and cumulative. Bars for a single delta
    # series (2-run mode, matches the original A/B look); lines when there
    # are several (euler mode) so they stay distinguishable.
    for i, (name, s) in enumerate(other_runs):
        color = SCENARIO_PALETTE[(i + 1) % len(SCENARIO_PALETTE)]
        common_years = sorted(set(baseline_s.index) & set(s.index))
        if not common_years:
            continue
        cum = s.cumsum()
        d_annual = (s - baseline_s).loc[common_years]
        d_cum = (cum - baseline_cum).loc[common_years]
        if len(other_runs) == 1:
            width = (min(3, (common_years[1] - common_years[0]) * 0.6)
                     if len(common_years) > 1 else 0.8)
            ax3.bar(common_years, d_annual.values, color=color, width=width)
            ax4.bar(common_years, d_cum.values, color=color, width=width)
        else:
            ax3.plot(common_years, d_annual.values, marker="o", color=color,
                     label=f"{name} − {baseline_name}")
            ax4.plot(common_years, d_cum.values, marker="o", color=color,
                     label=f"{name} − {baseline_name}")

    ax3.axhline(0, color="black", linewidth=0.8)
    ax3.set_ylabel("MEUR")
    ax3.grid(alpha=0.3)
    ax4.axhline(0, color="black", linewidth=0.8)
    ax4.set_ylabel("MEUR")
    ax4.grid(alpha=0.3)

    if len(other_runs) == 1:
        name_b = other_runs[0][0]
        total_delta = totals[name_b] - totals[baseline_name]
        ax3.set_title(f"Δ Annual ({name_b} − {baseline_name})", fontsize=11, fontweight="bold")
        ax4.set_title(
            f"Δ Cumulative ({name_b} − {baseline_name})   |   total Δ = {total_delta:,.0f}",
            fontsize=11, fontweight="bold")
    else:
        ax3.set_title(f"Δ Annual (vs {baseline_name})", fontsize=11, fontweight="bold")
        ax4.set_title(f"Δ Cumulative (vs {baseline_name})", fontsize=11, fontweight="bold")
        ax3.legend(fontsize=7)
        ax4.legend(fontsize=7)

    # Mark the year where the cheaper run switches, if it does (2-run mode only).
    if len(series_by_run) == 2:
        name_b, s_b = series_by_run[1]
        common_years = sorted(set(baseline_s.index) & set(s_b.index))
        if len(common_years) >= 2:
            cum_b = s_b.cumsum()
            diff = (cum_b - baseline_cum).loc[common_years]
            sign_changes = diff.values[:-1] * diff.values[1:]
            cross_idx = next((i for i, v in enumerate(sign_changes) if v < 0), None)
            if cross_idx is not None:
                cross_year = common_years[cross_idx + 1]
                for ax in (ax2, ax4):
                    ax.axvline(cross_year, color="gray", linestyle="--", linewidth=1)
                ax2.annotate(
                    f"Crossover\n{cross_year}", xy=(cross_year, baseline_cum.loc[cross_year]),
                    xytext=(5, 10), textcoords="offset points", fontsize=8, color="gray",
                )

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_costs_over_time(runs: list[Run]) -> plt.Figure:
    """Discounted total system cost (all components) over all years.

    Uses net present cost — technology CAPEX+OPEX *plus* carrier and carbon
    costs — so the ranking here matches the optimiser's objective.
    """
    series_by_run = [
        (r.label, get_annual_total_cost(r.results, get_available_years(r.results), discount=True))
        for r in runs
    ]
    return _cost_over_time_figure(
        series_by_run,
        "Total System Cost Over Time (Discounted — Net Present Cost, all components)")


def fig_carrier_costs_over_time(runs: list[Run]) -> plt.Figure:
    """Discounted carrier (fuel / import) cost over all years."""
    series_by_run = [
        (r.label, get_annual_cost(r.results, get_available_years(r.results), "cost_carrier", discount=True))
        for r in runs
    ]
    return _cost_over_time_figure(series_by_run, "Carrier (Fuel / Import) Cost Over Time (Discounted)")


def fig_carbon_costs_over_time(runs: list[Run]) -> plt.Figure:
    """Discounted carbon-emission cost over all years."""
    series_by_run = [
        (r.label, get_annual_cost(r.results, get_available_years(r.results),
                                  "cost_carbon_emissions_total", discount=True))
        for r in runs
    ]
    return _cost_over_time_figure(series_by_run, "Carbon Emission Cost Over Time (Discounted)")


def fig_costs_industry(runs: list[Run], year: int) -> plt.Figure:
    """Industry process CAPEX & OPEX, one column per run."""
    names = [r.label for r in runs]
    capexes = [filter_techs(get_capex_by_technology(r.results, year), INDUSTRY_PROCESS_TECHS) for r in runs]
    opexes = [filter_techs(get_opex_by_technology(r.results, year), INDUSTRY_PROCESS_TECHS) for r in runs]

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle(f"Industry Process Costs — Year {year}", fontsize=13, fontweight="bold")
    plot_stacked_bars(build_comparison_df(list(zip(names, capexes))),
                      "CAPEX", "MEUR", axes[0], show_segment_labels=True)
    plot_stacked_bars(build_comparison_df(list(zip(names, opexes))),
                      "OPEX", "MEUR", axes[1], show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_costs_heating(runs: list[Run], year: int) -> plt.Figure:
    """Industry heating CAPEX & OPEX, one column per run."""
    names = [r.label for r in runs]
    techs = INDUSTRY_HEATING_TECHS
    capexes = [filter_techs(get_capex_by_technology(r.results, year), techs) for r in runs]
    opexes = [filter_techs(get_opex_by_technology(r.results, year), techs) for r in runs]

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle(f"Industry Heating Costs — Year {year}", fontsize=13, fontweight="bold")
    plot_stacked_bars(build_comparison_df(list(zip(names, capexes))),
                      "CAPEX", "MEUR", axes[0], show_segment_labels=True)
    plot_stacked_bars(build_comparison_df(list(zip(names, opexes))),
                      "OPEX", "MEUR", axes[1], show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


OTHER_STORAGE_TECHS = [
    "battery",
    "pumped_hydro",
    "natural_gas_storage",
    "oil_storage",
    "salt_cavern_storage",
]


def fig_costs_other_storages(runs: list[Run], year: int) -> plt.Figure:
    """CAPEX & OPEX for non-TES/DSM storages (battery, pumped hydro, gas/oil/salt-cavern)."""
    names = [r.label for r in runs]
    techs = OTHER_STORAGE_TECHS
    threshold = 1e-12
    capexes = [filter_techs(get_capex_by_technology(r.results, year), techs, threshold) for r in runs]
    opexes = [filter_techs(get_opex_by_technology(r.results, year), techs, threshold) for r in runs]

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle(f"Other Storage Costs — Year {year}", fontsize=13, fontweight="bold")
    plot_stacked_bars(build_comparison_df(list(zip(names, capexes))),
                      "CAPEX", "MEUR", axes[0], show_segment_labels=True)
    plot_stacked_bars(build_comparison_df(list(zip(names, opexes))),
                      "OPEX", "MEUR", axes[1], show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_costs_flexibility(runs: list[Run], year: int) -> plt.Figure:
    """TES + DSM CAPEX & OPEX, one column per run."""
    names = [r.label for r in runs]
    # Use a low threshold so near-zero costs still appear
    threshold = 1e-12
    tes_capexes = [filter_techs(get_capex_by_technology(r.results, year), INDUSTRY_TES_TECHS, threshold) for r in runs]
    tes_opexes = [filter_techs(get_opex_by_technology(r.results, year), INDUSTRY_TES_TECHS, threshold) for r in runs]
    dsm_capexes = [filter_techs(get_capex_by_technology(r.results, year), INDUSTRY_DSM_TECHS, threshold) for r in runs]
    dsm_opexes = [filter_techs(get_opex_by_technology(r.results, year), INDUSTRY_DSM_TECHS, threshold) for r in runs]

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle(f"Flexibility Costs (TES & DSM) — Year {year}", fontsize=13, fontweight="bold")
    plot_stacked_bars(build_comparison_df(list(zip(names, tes_capexes))),
                      "TES — CAPEX", "MEUR", axes[0, 0], show_segment_labels=True)
    plot_stacked_bars(build_comparison_df(list(zip(names, tes_opexes))),
                      "TES — OPEX", "MEUR", axes[0, 1], show_segment_labels=True)
    plot_stacked_bars(build_comparison_df(list(zip(names, dsm_capexes))),
                      "DSM — CAPEX", "MEUR", axes[1, 0], show_segment_labels=True)
    plot_stacked_bars(build_comparison_df(list(zip(names, dsm_opexes))),
                      "DSM — OPEX", "MEUR", axes[1, 1], show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_fuel_consumption(runs: list[Run], year: int) -> plt.Figure:
    """Fuel consumption breakdown for natural_gas, hard_coal, lng, waste (2×2 grid)."""
    names = [r.label for r in runs]
    carriers = ["natural_gas", "hard_coal", "lng", "waste"]
    fig, axes = plt.subplots(2, 2, figsize=(14, 14))
    fig.suptitle(f"Fuel Consumption by Technology — Year {year}",
                 fontsize=13, fontweight="bold")
    for ax, carrier in zip(axes.flat, carriers):
        series = [get_fuel_consumption(r.results, carrier, year) for r in runs]
        df = build_comparison_df(list(zip(names, series)))
        plot_stacked_bars(df, carrier.replace("_", " ").title(), "GWh", ax,
                          show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_natural_gas_balance(runs: list[Run], year: int) -> plt.Figure:
    """Natural gas supply sources vs consumption by technology."""
    names = [r.label for r in runs]
    supply = [get_fuel_supply(r.results, "natural_gas", year) for r in runs]
    consumption = [get_fuel_consumption(r.results, "natural_gas", year) for r in runs]

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle(f"Natural Gas Balance — Year {year}", fontsize=13, fontweight="bold")
    plot_stacked_bars(build_comparison_df(list(zip(names, supply))),
                      "Supply (imports + conversion)", "GWh", axes[0], show_segment_labels=True)
    plot_stacked_bars(build_comparison_df(list(zip(names, consumption))),
                      "Consumption by Technology", "GWh", axes[1], show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig
