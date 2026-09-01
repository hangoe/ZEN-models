"""ZEN-Garden Crystal Ball — Interactive Model Analysis Dashboard.

Run:  streamlit run streamlit/app.py   (from repo root)
  or  streamlit run app.py             (from streamlit/ directory)

Two comparison modes, switchable in the sidebar:
  • Euler — 5 scenarios  (default): all euler_outputs/ scenarios at once.
  • Local — 2 runs: the original two-model local_outputs/ comparison.

9 thematic tabs, each showing every selected run side by side (no per-run tabs):
  1. Heat Flows        — heat carrier production/consumption, boiler/HP output
  2. Product Flows     — product carrier production
  3. Heat Capacity     — heat supply capacity, heat demand by sector (dropdown)
  4. Product Capacity  — production technology capacity
  5. Flexibility       — TES and DSM capacity, charge/discharge, cross-comparison
  6. Costs             — CAPEX/OPEX by technology (year-specific)
  7. Electricity       — generation capacity, production, consumption, net balance
  8. Residual Load     — residual load, storage use
  9. System            — emissions, fuel, NG balance, cost-over-time
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from zen_garden import Results

# All figure-generation logic (color/hatch maps, Results loading, plotting
# primitives, and the figure functions themselves) lives in scripts/ so it's
# shared with standalone scripts (e.g. generate_si_figures.py) instead of
# being dashboard-only. This app is UI/orchestration only.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from plots.figures_by_run import (
    fig_boiler_hp_production,
    fig_capacity_heat_supply,
    fig_capacity_production,
    fig_carrier_energy_all,
    fig_carrier_products_production,
    fig_dsm_capacity_addition,
    fig_dsm_charge_discharge,
    fig_electricity_balance,
    fig_electricity_capacity_production_consumption,
    fig_heat_demand_by_sector,
    fig_residual_load,
    fig_storage_comparison,
    fig_storage_use,
    fig_tes_capacity_addition,
    fig_tes_charge_discharge,
)
from plots.figures_by_scenario import (
    fig_carbon_costs_over_time,
    fig_carrier_costs_over_time,
    fig_costs_flexibility,
    fig_costs_heating,
    fig_costs_industry,
    fig_costs_other_storages,
    fig_costs_over_time,
    fig_costs_total,
    fig_emissions,
    fig_fuel_consumption,
    fig_natural_gas_balance,
    get_summary_metrics,
)
from plots.figure_settings import (
    EULER_ROOT,
    LOCAL_ROOT,
    Run,
    SCENARIO_PALETTE,
    euler_label,
    get_available_models,
    get_available_years,
    load_results,
    sort_euler_scenarios,
)

st.set_page_config(
    page_title="ZEN-Garden Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("ZEN-Garden Crystal Ball")

# On-screen render resolution. Figures are shown at container width regardless,
# so a moderate DPI keeps images small and fast; very high DPI (e.g. 450) makes
# the tall multi-panel figures exceed browser image limits, which breaks the
# tab layout. Raise later if you want sharper exports.
RENDER_DPI = 100


def short(name: str) -> str:
    return name.replace("Crystal_Ball_HG_", "")


def _swatch(color: str) -> str:
    return (f'<span style="display:inline-block;width:10px;height:10px;'
            f'background:{color};border-radius:2px;margin-right:6px;"></span>')


@st.cache_resource(show_spinner="Loading model data…")
def cached_load(comparison_mode: str, model_name: str) -> Results:
    root = LOCAL_ROOT if comparison_mode == "local" else EULER_ROOT
    return load_results(root, model_name)


def build_runs(comparison_mode: str, model_names: list[str]) -> list[Run]:
    """Load each model, skipping (with a sidebar warning) any that fail —
    e.g. a euler scenario whose var_dict.h5 hasn't finished downloading yet."""
    runs = []
    for i, name in enumerate(model_names):
        try:
            results = cached_load(comparison_mode, name)
        except Exception as exc:
            st.sidebar.warning(f"Could not load **{name}**: {exc}")
            continue
        label = euler_label(name) if comparison_mode == "euler" else short(name)
        color = SCENARIO_PALETTE[i % len(SCENARIO_PALETTE)]
        runs.append(Run(name=name, label=label, mode=comparison_mode, results=results, color=color))
    return runs


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Comparison Mode")
    comparison_mode = st.radio(
        "Mode", ["euler", "local"],
        format_func=lambda m: "Euler — 5 scenarios" if m == "euler" else "Local — 2 runs",
        index=0, key="mode_sel", label_visibility="collapsed",
    )
    st.divider()

    if comparison_mode == "euler":
        st.header("Euler Scenarios")
        euler_available = sort_euler_scenarios(get_available_models(EULER_ROOT))
        if not euler_available:
            st.error("No euler model outputs found under `data/outputs/euler_outputs/`.")
            st.stop()
        runs = build_runs("euler", euler_available)
        if not runs:
            st.error("None of the euler scenarios could be loaded yet.")
            st.stop()
        if len(runs) < len(euler_available):
            st.info(f"{len(runs)} of {len(euler_available)} scenarios loaded — showing those. "
                    "Others will appear once their results finish downloading.")
        for r in runs:
            st.markdown(f"{_swatch(r.color)}**{r.label}**", unsafe_allow_html=True)
    else:
        st.header("Model Selection")
        local_available = get_available_models(LOCAL_ROOT)
        if not local_available:
            st.error("No local model outputs found under `data/outputs/local_outputs/`.")
            st.stop()
        model_a = st.selectbox("Model A", local_available, index=0,
                               format_func=short, key="sel_a")
        model_b = st.selectbox("Model B", local_available, index=min(1, len(local_available) - 1),
                               format_func=short, key="sel_b")
        if model_a == model_b:
            st.warning("Both selections are the same model.")
        runs = build_runs("local", [model_a, model_b])
        if not runs:
            st.error("Could not load the selected local models.")
            st.stop()

    years_per_run = [get_available_years(r.results) for r in runs]
    common_years = sorted(set.intersection(*(set(y) for y in years_per_run)))
    all_years = sorted(set.union(*(set(y) for y in years_per_run)))

    # Default to the latest year every run shares; fall back to first in union
    default_idx = all_years.index(common_years[-1]) if common_years else 0

    st.divider()
    st.subheader("Costs & System year")
    year = st.selectbox(
        "Year", all_years, index=default_idx, key="year_sel",
        help="Applies to the Costs and System tabs only",
    )

    st.divider()
    for r, years in zip(runs, years_per_run):
        st.caption(f"**{r.label}** — years: {', '.join(str(y) for y in years)}")


def _runs_desc() -> str:
    return " vs ".join(f"**{r.label}**" for r in runs)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _compare(fig_fn, title: str = "", with_year: bool = True) -> None:
    """Render a comparison figure at full width.

    Every such figure already places all selected runs side by side as
    adjacent axes, so no per-run tabs are needed.
    """
    if title:
        st.markdown(f"##### {title}")
    try:
        fig = fig_fn(runs, year) if with_year else fig_fn(runs)
        st.pyplot(fig, width="stretch", dpi=RENDER_DPI)
        plt.close(fig)
    except Exception as exc:
        st.warning(f"Could not render: {exc}")


# ── 9 tabs ────────────────────────────────────────────────────────────────────
(tab_heat_flows, tab_product_flows, tab_heat_cap, tab_product_cap,
 tab_flex, tab_costs, tab_electricity, tab_residual, tab_system) = st.tabs([
    "🔥 Heat Flows",
    "📦 Product Flows",
    "🏭 Heat Capacity",
    "🧱 Product Capacity",
    "🔋 Flexibility",
    "💰 Costs",
    "⚡ Electricity",
    "📉 Residual Load",
    "🌍 System",
])


# ── Tab 1: Heat Flows ─────────────────────────────────────────────────────────
with tab_heat_flows:
    st.caption(f"Industry heat carrier production, consumption, and boiler/HP output — "
               f"{_runs_desc()}.")
    _compare(fig_carrier_energy_all, "Carrier Energy — Production & Consumption", with_year=False)
    _compare(fig_boiler_hp_production, "Boiler & HP Production",                  with_year=False)


# ── Tab 2: Product Flows ──────────────────────────────────────────────────────
with tab_product_flows:
    st.caption(f"Industry product carrier annual production — {_runs_desc()}.")
    _compare(fig_carrier_products_production, "Product Carriers — Annual Production", with_year=False)


# ── Tab 3: Heat Capacity ──────────────────────────────────────────────────────
with tab_heat_cap:
    st.caption(f"Installed capacity additions/totals for heat supply, plus sector-level "
               f"heat demand by temperature level — {_runs_desc()}.")
    _compare(fig_capacity_heat_supply, "Heat Supply Capacity", with_year=False)

    st.divider()
    hd_years = common_years if common_years else all_years
    heat_year = st.selectbox("Year", hd_years, index=len(hd_years) - 1, key="heat_demand_year",
                             help="Heat input by temperature level, one bar per sector, for this year")
    st.markdown("##### Heat Demand by Sector")
    try:
        fig = fig_heat_demand_by_sector(runs, heat_year)
        st.pyplot(fig, width="stretch", dpi=RENDER_DPI)
        plt.close(fig)
    except Exception as exc:
        st.warning(f"Could not render: {exc}")


# ── Tab 4: Product Capacity ───────────────────────────────────────────────────
with tab_product_cap:
    st.caption(f"Installed capacity additions and totals for production technologies — "
               f"{_runs_desc()}.")
    _compare(fig_capacity_production, "Production Technology Capacity", with_year=False)


# ── Tab 5: Flexibility ────────────────────────────────────────────────────────
with tab_flex:
    st.caption(f"Thermal energy storage and demand-side management — capacity, "
               f"charge/discharge flows, and cross-technology comparison — "
               f"{_runs_desc()}.")
    _compare(fig_tes_capacity_addition, "TES Capacity Addition",                       with_year=False)
    _compare(fig_tes_charge_discharge,  "TES Charge & Discharge",                      with_year=False)
    _compare(fig_dsm_capacity_addition, "DSM Capacity Addition",                       with_year=False)
    _compare(fig_dsm_charge_discharge,  "DSM Charge & Discharge",                      with_year=False)
    _compare(fig_storage_comparison,    "Storage Technologies — Cross-type Comparison", with_year=False)


# ── Tab 6: Costs ──────────────────────────────────────────────────────────────
with tab_costs:
    st.caption(f"CAPEX and OPEX comparison for year **{year}** — {_runs_desc()}")

    missing = [r.label for r, years in zip(runs, years_per_run) if year not in years]
    if missing:
        st.warning(f"Year {year} missing in: {', '.join(missing)}. Those bars will be empty.")

    _compare(fig_costs_total,          "Total System Costs (CAPEX & OPEX)")
    _compare(fig_costs_industry,       "Industry Process Costs")
    _compare(fig_costs_heating,        "Heating Costs — Industry Heating")
    _compare(fig_costs_flexibility,    "Flexibility Costs — TES & DSM")
    _compare(fig_costs_other_storages, "Other Storage Costs — Battery, Pumped Hydro, Gas/Oil/Salt-Cavern")


# ── Tab 7: Electricity ────────────────────────────────────────────────────────
with tab_electricity:
    st.caption(f"Electricity system — generation capacity, production mix, consumption, "
               f"and per-year net balance (production vs consumption, net import, battery) — "
               f"{_runs_desc()}.")
    _compare(fig_electricity_capacity_production_consumption,
             "Capacity, Production & Consumption", with_year=False)
    _compare(fig_electricity_balance, "Net Balance", with_year=False)


# ── Tab 8: Residual Load ──────────────────────────────────────────────────────
with tab_residual:
    st.caption(
        "**Residual load = electricity load − non-dispatchable renewable "
        "generation (PV + wind), each hour.** It is the load left for "
        "dispatchable plants, storage, imports and flexibility to cover. Below "
        "zero means a renewable surplus (curtailment / storage-charging / export "
        f"opportunity) — {_runs_desc()}."
    )
    st.info(
        "These runs use time-series aggregation (10 representative steps/year), "
        "so the curves are a ~10-step approximation mapped back onto 8760 hours — "
        "the *shape* is meaningful but not a smooth hourly profile. For a smooth "
        "curve, re-run a scenario with `conduct_time_series_aggregation: false`."
    )
    rl_years = common_years if common_years else all_years
    rl_year = st.selectbox("Year", rl_years, index=len(rl_years) - 1,
                           key="residual_year",
                           help="Residual load is computed for this year")

    def _residual(load_mode: str, title: str) -> None:
        st.markdown(f"##### {title}")
        try:
            fig = fig_residual_load(runs, rl_year, load_mode)
            st.pyplot(fig, width="stretch", dpi=RENDER_DPI)
            plt.close(fig)
        except Exception as exc:
            st.warning(f"Could not render: {exc}")

    _residual("total",
              "Total electricity demand (incl. heat pumps, electrolysis, EVs, …)")

    st.divider()
    st.markdown("##### Storage Use")
    st.caption(
        "Which storages balance this system. **Top:** annual energy discharged by "
        "each bulk storage over the horizon. **Bottom:** net electricity-storage "
        "power for the selected year, sorted high→low (a duration curve) — "
        "positive hours = discharging to the grid (covering a residual-load "
        "deficit), negative hours = charging from a renewable surplus. (TES & DSM "
        "flexibility are in the Flexibility tab.)"
    )
    try:
        fig = fig_storage_use(runs, rl_year)
        st.pyplot(fig, width="stretch", dpi=RENDER_DPI)
        plt.close(fig)
    except Exception as exc:
        st.warning(f"Could not render: {exc}")


# ── Tab 9: System ─────────────────────────────────────────────────────────────
with tab_system:
    st.caption(f"System-level metrics for year **{year}** — {_runs_desc()}")

    # Summary metrics
    try:
        m = get_summary_metrics(runs, year)

        if len(runs) == 2:
            # 2-run mode: keep the original side-by-side + delta metric layout.
            run_a, run_b = runs
            ma, mb = m[run_a.name], m[run_b.name]

            def _metric_row(label: str, key: str, unit: str) -> None:
                val_a, val_b = ma[key], mb[key]
                if val_a is None and val_b is None:
                    return
                c1, c2, c3 = st.columns(3)
                c1.metric(f"{label} — {run_a.label}", f"{val_a:,.0f} {unit}" if val_a is not None else "n/a")
                c2.metric(f"{label} — {run_b.label}", f"{val_b:,.0f} {unit}" if val_b is not None else "n/a")
                if val_a is not None and val_b is not None:
                    delta = val_b - val_a
                    pct = delta / val_a * 100 if val_a else 0
                    c3.metric(f"Δ ({run_b.label} − {run_a.label})", f"{delta:+,.0f} {unit}",
                              delta=f"{pct:+.1f}%", delta_color="inverse")

            _metric_row("Emissions",   "em",    "Mton CO₂")
            _metric_row("Total CAPEX", "capex", "MEUR")
            _metric_row("Total OPEX",  "opex",  "MEUR")
        else:
            # N-run mode: one column per run.
            table = pd.DataFrame({
                m[r.name]["label"]: {
                    "Emissions [Mton CO₂]": m[r.name]["em"],
                    "Total CAPEX [MEUR]": m[r.name]["capex"],
                    "Total OPEX [MEUR]": m[r.name]["opex"],
                }
                for r in runs
            })
            st.dataframe(table.style.format("{:,.0f}"), width="stretch")
    except Exception:
        pass

    st.divider()
    _compare(fig_emissions,           "Total System Emissions")
    _compare(fig_fuel_consumption,    "Fuel Consumption by Technology")
    _compare(fig_natural_gas_balance, "Natural Gas Balance (Supply vs Consumption)")

    st.divider()
    st.caption("**Discounted (net present) cost over the full horizon.** The total cost now "
               "covers ALL objective components — technology CAPEX + OPEX **plus carrier "
               "(fuel/import) and carbon-emission costs** — and is discounted, so the ranking "
               "here matches the optimiser's objective. The Σ / total figures in the legends are "
               "the discounted grand totals (each flexible scenario should not exceed the "
               "no-flexibility one). Carrier and carbon costs — where flexibility pays off — are "
               "broken out separately below.")
    _compare(fig_costs_over_time, "Total System Cost Over Time (discounted, all components)",
             with_year=False)
    _compare(fig_carrier_costs_over_time, "Carrier (Fuel / Import) Cost Over Time (discounted)",
             with_year=False)
    _compare(fig_carbon_costs_over_time, "Carbon Emission Cost Over Time (discounted)",
             with_year=False)
