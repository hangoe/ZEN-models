"""Generate print-ready figures for the MT_report SI Results section.

Covers the SI Results subsections in `MT_report_HG/Sections/03_SI.tex`
(`\\label{sec:si-results}`), across the 7
case-study scenarios in that section's Table~SIScenarios — 6
Crystal_Ball_HG_v7_0 euler runs (Full flexibility, No flexibility, DSM only,
TES only, Single temperature level, DSM pessimistic) plus the unmodified
"Crystal Ball (base)" reference case (dataset `Crystal_Ball`, plain — no
`Crystal_Ball_HG_v7_0` prefix, staged from data/Crystal_Ball, see
run_model.py):

Figure organization (as of the SI_results/method split): every figure below
that shows actual model RESULTS is written straight into SI_results/,
renumbered fig1..fig10 in the same relative order the old fig0a..fig10
numbering had. Every figure that is purely METHODOLOGICAL — no solved
model results, either hand-typeset/illustrative or plotting input
assumptions/context data rather than model output — is written into
SI_results/method/ instead, renumbered fig1..fig7 within that subfolder.
Function names below keep their OLD fig-N labels (fig11_mga_method,
fig4a_heat_demand_by_sector, etc.) purely as stable internal identifiers
for cross-referencing in comments throughout this file; only the actual
output filename/folder (the savefig() call at the end of each function)
uses the new per-folder numbering — see each entry's "-> " below for where
it actually lands on disk.

SI_results/ (results, renumbered fig1-fig10):
  fig1_cost_composition (was fig0a)            — CAPEX/OPEX/carrier/carbon-cost breakdown of each v7_0
                                          scenario's cost increase vs Crystal Ball base
  fig2_emissions_source_comparison (was fig0b) — Full flex vs Crystal Ball base, year 2025: where the
                                          emissions increase comes from vs. only a modest cost delta
  fig3_cost_delta (was fig1a)          — discounted system cost delta vs Full flexibility
  fig4_industry_capacity (was fig1b)   — industry heat-supply & production capacity, 2050
  fig5_dsm_cycles_by_product (was fig2) — DSM utilization (cycles/yr) by product: optimistic vs pessimistic
  fig6_heat_pathway (was fig3b)        — direct vs temp-conversion heat production, 2050
  fig7_retrofit_ccs_comparison (was fig5) — CO2 captured by retrofit-CCS technology, No flexibility vs Crystal Ball base
  fig8_diffusion_mechanisms (was fig6) — ZEN-garden technology-diffusion/learning mechanisms compared
  fig9_heat_supply_trajectory_no_flexibility (was fig7) — No flexibility heat-supply capacity, every modeled year 2020-2050
  fig9b_heat_supply_trajectory_full_flexibility — same layout as fig9, for the Full flexibility scenario
  fig10_power_and_storage_impact — power generation capacity (top) & storage annual energy discharged
                                          (bottom), each a single plot with Crystal Ball base / No flexibility /
                                          Full flexibility as 3 adjacent bars per year, 3 snapshot years
                                          (2030/2040/2050) — generation fleet SCALES UP with mix barely
                                          shifting; storage capacity stays near-identical across scenarios
                                          but discharge (utilization) doesn't
  fig11_power_and_storage_impact_with_dsm — exactly fig10's template, with Full flexibility's storage bars
                                          also stacking its DSM discharge (all 10 products; ammonia/methanol
                                          natively GWh, the other 8 mass-carrier products converted via their
                                          own system-wide production energy intensity that year) on top of
                                          the same 5 power-sector storage techs — see fig11's own section
                                          comment for the per-product methodology
  fig12_capacity_and_storage_base_and_delta — same 2 quantities as fig10, but as Crystal Ball base
                                          (absolute stack) + a floating Δ No flexibility bar per year
  fig13_regional_capacity_delta_map      — that same Δ No flexibility, per node, as area-scaled pie
                                          glyphs on a map of the modeled European regions
  fig14a_heat_supply_output_full_vs_single_temp — fig9's top ("Industry heat supply" operated-output)
                                          panel, side by side for Full flexibility vs. Single
                                          temperature level at 2020/2030/2040/2050, with each bar's
                                          heat-pump share of total output called out — total output is
                                          near-identical between the two, but Full flexibility's HP
                                          share climbs to 82% by 2050 vs. Single temperature level's 54%
  fig14b_cost_emissions_totals_full_vs_single_temp — fig1b's (fig1b_cost_emissions_totals) template
                                          applied to Full flexibility vs. Single temperature level:
                                          Full flexibility's cost/emissions totals in grey, Single
                                          temperature level's difference on top

SI_results/method/ (no results — methodological/context only, fig1-fig9):
  fig1_heat_demand_by_sector (was fig4a) — low-temp input heat demand by sector/band, +high-temp fuel by carrier (2023):
                                          an exogenous INPUT ASSUMPTION, not a solved-model result (see below)
  fig2_industry_fuel_demand_comparison (was fig4b) — new-sector heat/fuel demand vs. pre-existing cement/steel fuel mix
  fig3_industry_sector_emissions_context (was fig8) — European industry CO2 emissions by
                                          subsector (JRC-IDEES-2023), colored by Crystal Ball scope
  fig4_model_scope_coverage (was fig9)  — Crystal Ball's (+ its industry-heat extension's) share of
                                          total European direct CO2 emissions (Mannhardt 2026 + UNFCCC CRF)
  fig9_global_ghg_sector_breakdown (new, fig15) — global GHG emissions by sector (WRI/Climate Watch):
                                          Energy -> Electricity & Heat / industry energy use, plus
                                          industry's direct (non-energy) process emissions added on top,
                                          motivating why industry needs BOTH an energy-side model
                                          (this work's scope) and remains partly out of reach of one
  fig5_mga_method (was fig11)           — conceptual, non-data schematic of the Modeling-to-Generate-
                                          Alternatives (MGA) method: (left) feasible region, objective
                                          direction, optimum z*, near-optimality slack ε and the
                                          resulting near-optimal space; (right) that space explored via
                                          inner (IO) / outer (AO) polytope approximations refined by
                                          directional solves — a mid-exploration SNAPSHOT (solve order
                                          starts with the farthest/most-prominent corner); see fig8 for
                                          the same toy geometry run to full completion
  fig6_lp_formulation (was fig12)       — energy system optimization as an LP: the general cost-min
                                          capacity-expansion formulation (left) next to this work's
                                          actual "No flexibility" model's size and ZEN-garden-specific
                                          formulation details (right), read from that run's
                                          benchmarking.json/system.json/solver.json
  fig7_mga_axis_construction (was fig13) — conceptual, non-data schematic of how the NUMBER of
                                          candidate MGA axes grows as dimensions are crossed, left to
                                          right: (1) 3 technology-group axes alone; (2) x 4 regions
                                          (the real north/west/south/east map) = 12 axes; (3) x 3
                                          cumulative-CAPEX horizons too, all three dimensions crossed
                                          on one chart = 36 axes
  fig8_mga_exploration_sequence (was fig14) — companion to fig5: the same toy near-optimal space,
                                          run through ALL 5 directional solves as 5 small-multiple
                                          panels (largest-gap direction first) instead of fig5's
                                          mid-exploration snapshot, ending with the discovered
                                          polytope matching the true near-optimal space exactly. Per
                                          pyoNearOpt's actual direction selection (support-function
                                          gap h_out(d)-h_in(d) against the CURRENT inner hull, not
                                          against z*), each solve's arrow is anchored at whichever
                                          already-found vertex is extremal toward the new direction -
                                          only solve 1 starts at z* itself

fig4a/fig4b (now method/fig1, method/fig2), fig8/fig9 (now method/fig3,
method/fig4) moved into method/ because none of them plot a SOLVED MODEL
RESULT: fig4a is the exogenous heat-demand ASSUMPTION fed into the model
(see its own docstring below), fig4b is largely the same kind of
input-vs-context comparison, and fig8/fig9 plot external JRC-IDEES-2023/
UNFCCC input data establishing Crystal Ball's scope — none of the 4 touch
EULER_ROOT run output. fig11/fig12/fig13 (now method/fig5-7) were already
method figures by construction (see below).

fig11 (method/fig5) is a pure method illustration: hand-picked, unitless 2D
geometry (no model run, no external data at all), generated unconditionally
in main() like fig8/fig9. It intentionally uses a toy feasible region (not
the model's actual 6-D MGA exploration space plotted in
data/outputs/figures/mga_tests/) so both axes can be labeled generically
("Variable A/B") for a textbook-style explainer, independent of which
specific technologies the real MGA runs explored.

fig12's (method/fig6) left side (the general LP formulation) is likewise
hand-typeset, not derived from anything solvable. Its right side, unlike
fig11, IS real: the variable/constraint counts and solver stats are read
directly from the "No flexibility" scenario's own
benchmarking.json/system.json/solver.json (found via _search_var_dict under
SCENARIOS[0], the same lookup load_results() uses) rather than hardcoded,
so they can't silently drift from that run. Generated unconditionally in
main(); skipped gracefully (like fig10) if that scenario isn't under
EULER_ROOT yet.

fig13 (method/fig7), like fig11, is a pure method illustration with no
solved points — but deliberately does NOT use 2D coordinate frames (an
earlier version did; per user feedback that read as "the near-optimal-space
plot" and was confusing, since that's fig11's job, not this figure's).
Instead it just COUNTS candidate axes as dimensions are crossed: panel 1 is
3 pictogram boxes (power/hydrogen/carbon technology groups); panel 2 is the
real north/west/south/east map crossed with a 4x3 grid of colored cells
(regions x technology groups); panel 3 crosses all three dimensions at once
on a single region x group x horizon chart (12 curves, 3 markers each = 36
points/axes). Region identity is always color, technology-group identity is
always a pictogram (lightning = power, "H2" = hydrogen, "C" = carbon) —
consistent across all 3 panels. Every count is read directly off this
repo's real MGA axis configs rather than invented — see the constant block
above fig13_mga_axis_construction() for exactly which config_mga_axes_*.json
file each panel's number comes from. Unlike fig11/fig12, fig13's map DOES
pull in a new dependency (geopandas + the cached Natural Earth shapefile in
data/naturalearth/) per user request for the real geography instead of an
abstract icon — it falls back to a hand-drawn 4-wedge compass if geopandas
or the shapefile aren't available, so it still generates unconditionally in
main() either way.

fig8 and fig9, like fig4a, plot real-world INPUT data (JRC-IDEES-2023 subsector
emissions; Mannhardt's documented 90.0% sector-coverage figure plus UNFCCC CRF
data via sector_emissions_2022.csv), not solved-model results — generated
unconditionally in main(), independent of which Euler runs are loaded. fig8's
JSON is produced by extract_industry_sector_emissions.py (run under
zen-creator-env, same env-split reason as extract_heat_demand_by_sector.py);
fig9 reads sector_emissions_2022.csv directly (a plain CSV, no openpyxl
needed) from the sibling ZEN-creator repo, the same cross-repo convention
plot_carrier_flows.py uses for ZEN-creator's outputs/.

fig4a is the odd one out: unlike every other figure here, it does NOT come from
a solved model run. It plots the exogenous low-temperature heat-demand
ASSUMPTION that ZEN-creator computes for glass/ceramic/paper/food
(ProcessParametrizationDataset._heat_cfs × each sector's own demand volume,
FEC_YEAR=2023) — i.e. what goes INTO the model as `demand` on
heat_industry_0_100/100_150/150_200, not what the solved model does with it
(that's fig3b's territory) — plus, stacked on top in grey and split by
carrier (including "oil" for ceramic as of ZEN-creator commit 1f3f708), each
sector's high-temperature (>200°C) fuel demand (direct combustion, no
heat_industry_* carrier involved — a different supply pathway, shown only for
scale against the colored low-temperature bands), plus a final green
electricity segment (not temperature-banded, not part of the fuel mix — a
separate fixed input every production tech has). Values are aggregated across
all MODEL_NODES (EU27+CH+NO+UK), not per-country. Since
ZEN-creator needs openpyxl/xlrd (zen-creator-env) and this script needs
matplotlib (zen-garden-env) — the two conda envs are disjoint — the
extraction is a separate script (scripts/extract_heat_demand_by_sector.py,
run under zen-creator-env) that writes heat_demand_by_sector_input.json into
this same FIGURES_DIR; fig4a_heat_demand_by_sector() here just reads and
plots it, and is skipped gracefully (like fig0a/fig0b vs. Crystal Ball base)
if that JSON hasn't been generated yet. See extract_heat_demand_by_sector.
py's docstring for the full provenance/validation chain (Rehfeldt2017.csv ->
compute_sector_params(), cross-checked against a materialized dataset's own
demand.csv and attributes.json).

fig2 used to be a pair (fig2a_tes_dsm_utilization, fig2b_dsm_cycles_by_product).
fig2a summed flow_storage_charge/discharge across all INDUSTRY_DSM_TECHS, but
those techs are NOT unit-homogeneous: ammonia_DSM/methanol_DSM are
energy-carrier storage (GWh, confirmed via Results.get_unit()), while the
other 8 (ceramic/clinker/food/glass/olefin/paper/primary_steel/
secondary_steel) are mass-carrier storage (kt-of-product) — its
"[GWh+kt]" axis label was already an admission of an invalid mixed-unit sum.
Removed outright (per user decision) rather than fixed, since its message
(TES negligible vs. DSM once DSM is available) is carried by prose alone in
03_SI.tex. fig2b was renamed to fig2 (dropping the now-meaningless "b"
suffix) and gained hatching to flag which of its bars are the 2
energy-carrier products (ammonia, methanol) vs. the 8 mass-carrier ones —
its "cycles/year" metric was already unit-safe (each product's discharge is
divided by its OWN capacity in the same native unit), but had no visual cue
for readers that the underlying carriers differ in kind.

The planned "Emissions" subsection (fig3b) is intentionally NOT built as a
standalone comparison across the 6 v7_0 scenarios: their horizon-total
emissions only span ~2.3% of each other (headline_metrics.csv), so an
absolute-scale trajectory or decomposition just shows six overlapping lines/
bars. fig0b covers a single-scenario ("Full flexibility") emissions
comparison against Crystal Ball base instead — see
fig0b_emissions_source_comparison's docstring — without a dedicated,
mostly-flat fig3b-only pairing.

fig3a_temp_sensitivity_summary (cost/emissions/capacity delta bars, Single
temperature level vs Full flexibility) was deleted per user request: its cost
and capacity bars only repeated what fig0a/fig1b already show, and the one
new number it carried (emissions delta, ~+0.9%) is reported as prose in
03_SI.tex instead. fig3b (heat pathway) is unchanged and keeps its original
name/label — it was NOT renamed down to "fig3" the way fig2b was, since the
user only asked to drop fig3a this time, not collapse the pair.

"Crystal Ball (base)" only feeds fig0a/0b. `load_base_scenario()` still skips
them gracefully (with a printed note) if Crystal_Ball_2025_10a_5a_interval_10ts/
isn't present under EULER_ROOT, but as of v7_0 it has converged and is loaded
normally. It's deliberately NOT a 7th entry in SCENARIOS below or
in any other figure: it has no industry heat/DSM/TES sector at all, so
capacity/utilization figures (1b, 2, 3b)
would show a misleading 0 for it rather than a meaningful
absence. Cost and emissions totals, by contrast, are well-defined for any
run regardless of sector structure, which is what makes it fig0a/0b material.

CAUTION on fig0a's headline numbers (found while building it): each v7_0
scenario's cost increase vs Crystal Ball base is NOT evenly spread across the
horizon or across cost components — see fig0a_cost_composition's docstring
for the full breakdown. In short: (1) ~half the cost delta is concentrated
in the single final year 2070, which behaves very differently between the
base run (a smooth declining tail) and every v7_0 scenario (a sharp
late-horizon spike) — a likely end-of-horizon/terminal-value artifact, not a
flexibility-extension cost; (2) of the remaining delta, the majority is
`cost_carbon_emissions_total`, not CAPEX/OPEX — and that variable itself is
~0 in every year except 2050 and 2070, i.e. it behaves like a carbon-BUDGET
shadow price at specific checkpoint years (see carbon_emissions_annual_limit.
csv, identical 0-limit-at-2050 in both datasets) rather than a smooth $/ton
price. This is very likely a real ZEN-garden framework/dataset behavior, not
a bug in this script — the % deltas exactly reproduce the model's own
net_present_cost/carbon_emissions_annual outputs — but it means fig0a's
percentages should not be read as "the extension costs X% more to
build/operate" without this context.

Reuses the data-access helpers and color/plotting primitives shared with the
Streamlit dashboard (`figure_settings.py`, `figures_by_run.py`,
`figures_by_scenario.py`, all in this same scripts/ folder) rather than
re-deriving them.

Usage:
    python scripts/generate_si_figures.py
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch, Patch, Polygon, Rectangle, Wedge
from matplotlib.path import Path as MplPath
from matplotlib.lines import Line2D

from plots.figures_by_run import (
    BULK_STORAGE_TECHS,
    INDUSTRY_DSM_TECHS,
    INDUSTRY_HEAT_CARRIERS_ENERGY,
    INDUSTRY_HEAT_TECHS_BOILERS_HP,
    INDUSTRY_HEAT_TECHS_PRODUCTION,
    INDUSTRY_HEAT_TECHS_TEMP_CONV,
    get_capacity,
    get_capacity_addition,
    get_carrier_production,
    get_storage_flows,
)
from plots.figures_by_scenario import (
    _annual_series,
    build_comparison_df,
    get_annual_cost,
    get_annual_total_cost,
    get_emissions_by_carrier,
    get_emissions_by_technology,
    plot_stacked_bars,
)
from plots.figure_settings import (
    EULER_ROOT,
    HOURS_PER_YEAR,
    Run,
    SCENARIO_PALETTE,
    _apply_shared_ylim,
    _search_var_dict,
    _text_color_for_bg,
    apply_font_mode,
    eth_tint,
    get_available_years,
    load_results,
)
from plots.natural_earth import EUROPE_EXTENT, ISO_A2_EH_OVERRIDES, NATURALEARTH_SHP

# Font family (Arial for presentations vs. cmr10/Computer Modern matching
# MT_report_HG's LaTeX, for the report) is toggled in ONE place for every
# figure script in this repo — see figure_settings.FONT_MODE. Figure-specific
# fontsize=N calls throughout this file are unaffected by this toggle either way.
apply_font_mode()

FIGURES_DIR = REPO_ROOT / "data" / "outputs" / "figures" / "SI_results"
# Single-year snapshot used throughout (horizon totals used where noted).
# As of the v8_0 re-run the horizon changed from 2025-2070/step5 to
# 2020-2048/step2 (reference_year=2020, interval_between_years=2,
# optimized_years=15), then as of the 2026-09 "add 2050" re-sync all runs
# were re-solved with optimized_years=16 (2020-2050) — 2036 is left as-is
# here (still a real modeled year, still mid-horizon, not the terminal year
# fig0a's docstring flags as prone to terminal-value/budget-repayment
# artifacts); it no longer needs to stand in for 2050 since 2050 is now a
# real snapshot option (see COMPARISON_YEARS below).
YEAR = 2036

# Multi-year snapshot set shared by fig0b (panel A), fig1b, and fig4b.
# 2030/2040/2050 are all directly modeled years under the 16a horizon
# (2020, 2022, ..., 2050) — 2050 replaces the previous 2048 stand-in now
# that the actual final year is modeled.
COMPARISON_YEARS = [2030, 2040, 2050]

# Thesis-consistent scenario order/labels (Table~SIScenarios), distinct from
# the dashboard's shorter "Baseline" label for the same run. Order matches
# Table SIScenarios (excluding "Crystal Ball (base)", handled separately via
# BASE_SCENARIO below) and figure_settings.EULER_SCENARIO_ORDER, so the same
# scenario gets the same SCENARIO_PALETTE slot 0-5 everywhere; slot 6 (grey)
# is reserved for "Crystal Ball (base)" — see the module docstring for why it
# isn't a 7th entry here.
SCENARIOS = [
    ("Crystal_Ball_ind_heat_v9_0_no_flexibility_2020_16a_2a_interval_10ts", "No flexibility"),
    ("Crystal_Ball_ind_heat_v9_0_2020_16a_2a_interval_10ts", "Full flexibility"),
    ("Crystal_Ball_ind_heat_v9_0_DSM_pessimistic_2020_16a_2a_interval_10ts", "DSM pessimistic"),
    ("Crystal_Ball_ind_heat_v9_0_DSM_only_2020_16a_2a_interval_10ts", "DSM only"),
    ("Crystal_Ball_ind_heat_v9_0_TES_only_2020_16a_2a_interval_10ts", "TES only"),
    ("Crystal_Ball_ind_heat_v9_0_single_temp_2020_16a_2a_interval_10ts", "Single temperature level"),
]

# fig0a/fig0b only. Uses SCENARIO_PALETTE slot 6 (grey) — see the comment there.
# Path is under EULER_ROOT's top level, NOT archive/. History of this path
# getting stale twice now: (1) as of "add results of v7.0..." (7697b97) this
# run was moved out of EULER_ROOT's top level into archive/, which silently
# broke load_base_scenario() (it just prints the "not yet under EULER_ROOT"
# skip note and moves on) — fig0a/fig0b on disk were stale from the old
# v6_1-era run for months until that was corrected. (2) As of the
# 2026-07-29 "run model until 2050 only" re-sync (all v7_1 scenarios AND the
# base case re-run with optimized_years=6, i.e. 2025-2050, replacing the
# previous optimized_years=10 / 2025-2070 runs), a FRESH base run landed at
# this top-level path while BASE_SCENARIO still pointed at the archived,
# now-superseded 10-year run — fig0a was silently comparing the v7_1
# scenarios' 6-year (2025-2050) horizon totals against the base run's 10-year
# (2025-2070) horizon totals, an apples-to-oranges sum that produced
# nonsensical deltas. Verify BASE_SCENARIO's optimized_years matches the
# SCENARIOS list's (system.json's "optimized_years") if fig0a/fig0b numbers
# ever look inconsistent with headline_metrics.csv again — this path tends to
# drift whenever the base case gets independently re-run.
#
# 2026-09 "add 2050" re-sync: base case re-run with optimized_years=16
# (2020-2050, matching the SCENARIOS list's new 16a runs) — see the
# COMPARISON_YEARS comment above for the same re-sync.
BASE_SCENARIO = ("Crystal_Ball_2020_16a_2a_interval_10ts", "Crystal Ball (base)")


def load_scenarios() -> list[Run]:
    """Skips (rather than raising on) any scenario whose euler run hasn't
    landed/finished yet — same tolerance load_base_scenario() already has for
    the base run — printing a note so a partial run set isn't silently mistaken
    for a complete one. Figures that need a specific missing scenario (e.g.
    fig3b needs "Single temperature level") self-skip in turn; see main()."""
    runs = []
    for i, (folder, label) in enumerate(SCENARIOS):
        try:
            results = load_results(EULER_ROOT, folder)
        except FileNotFoundError:
            print(f"  skipping {label!r}: {folder} not found/incomplete under {EULER_ROOT}")
            continue
        runs.append(Run(name=folder, label=label, mode="euler", results=results,
                         color=SCENARIO_PALETTE[i % len(SCENARIO_PALETTE)]))
    return runs


def load_base_scenario() -> Run | None:
    """Returns None (rather than raising) if the run hasn't landed yet."""
    folder, label = BASE_SCENARIO
    try:
        results = load_results(EULER_ROOT, folder)
    except FileNotFoundError:
        return None
    return Run(name=folder, label=label, mode="euler", results=results,
               color=SCENARIO_PALETTE[6])


def by_label(runs: list[Run], label: str) -> Run:
    return next(r for r in runs if r.label == label)


def savefig(fig: plt.Figure, name: str, subdir: str | None = None) -> None:
    """subdir=None writes straight into FIGURES_DIR (SI_results/) as before;
    subdir="method" (or "archive") writes into that subfolder instead — see
    the module docstring's "Figure organization" note for which figures use
    which."""
    directory = FIGURES_DIR / subdir if subdir else FIGURES_DIR
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.svg"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {path.relative_to(REPO_ROOT)}")


# ── Shared metrics (feed figures 1a, 3a, 4) ────────────────────────────────

def industry_heat_capacity(r, year: int) -> float:
    """Total industry heat-supply capacity (boilers + HPs only), GW.

    Deliberately excludes heat_industry_temp_conversion_*: that pathway is a
    near-zero-cost, effectively unconstrained lossless conversion, so its
    "capacity" is a modeling artifact (~37,700 GW, three orders of magnitude
    above the real boiler/HP capacity) rather than a meaningful investment —
    it is examined separately in fig3b's direct-vs-conversion pathway split.
    """
    cap = get_capacity(r, INDUSTRY_HEAT_TECHS_BOILERS_HP, "power")
    return float(cap[year].sum()) if year in cap.columns else 0.0


def compute_headline_metrics(runs: list[Run]) -> pd.DataFrame:
    """Horizon-total discounted cost, horizon-total emissions, and 2050 industry
    heat-supply capacity, one row per scenario."""
    rows = {}
    for r in runs:
        years = get_available_years(r.results)
        npc_total = float(get_annual_total_cost(r.results, years, discount=True).sum())
        em_total = float(_annual_series(r.results, "carbon_emissions_annual", years).sum())
        cap = industry_heat_capacity(r.results, YEAR)
        rows[r.label] = {
            "npc_total_meur": npc_total,
            "emissions_total_mton": em_total,
            "industry_heat_capacity_gw": cap,
        }
    return pd.DataFrame(rows).T


# ── 0a: Cost-increase composition (CAPEX/OPEX/carrier/carbon) ──────────────

# (variable, display label). Matches the Streamlit dashboard's own CAPEX/OPEX
# metrics (figures_by_scenario.get_summary_metrics) plus the two remaining
# components (carrier, carbon) needed to fully reconstruct net_present_cost —
# verified to sum exactly to it (see the caution note in the module docstring).
COST_COMPONENTS = [
    ("cost_capex_yearly_total", "CAPEX"),
    ("cost_opex_yearly_total", "OPEX"),
    ("cost_carrier", "Carrier (fuel/import)"),
    ("cost_carbon_emissions_total", "Carbon emissions cost"),
]
COST_COMPONENT_COLORS = ["#215CAF", "#007894", "#8E6713", "#B7352D"]  # ETH blue/petrol/bronze/red


def compute_cost_components(runs: list[Run]) -> pd.DataFrame:
    """Discounted, horizon-total cost by component, one row per scenario."""
    rows = {}
    for r in runs:
        years = get_available_years(r.results)
        rows[r.label] = {
            label: float(get_annual_cost(r.results, years, var, discount=True).sum())
            for var, label in COST_COMPONENTS
        }
    return pd.DataFrame(rows).T


# Carbon emissions cost is computed (see compute_cost_components) but
# deliberately excluded from this figure's bars/legend: at ~60% of the total
# delta and behaving like a 2050/2070 budget-checkpoint shadow cost rather
# than a smooth $/ton price (see docstring below), it dwarfs and obscures the
# CAPEX/OPEX/carrier story this figure exists to show.
PLOTTED_COST_COMPONENTS = COST_COMPONENTS[:3]
PLOTTED_COST_COMPONENT_COLORS = COST_COMPONENT_COLORS[:3]


def fig0a_cost_composition(components_with_base: pd.DataFrame) -> None:
    """Decomposes each v7_0 scenario's cost increase vs Crystal Ball base into
    CAPEX/OPEX/carrier (carbon emissions cost excluded — see
    PLOTTED_COST_COMPONENTS above), to show what's actually driving the
    non-carbon part of the increase.

    Built after a real surprise: the total increase is NOT primarily new
    CAPEX/OPEX from the added industry-heat/flexibility technologies (each
    contributes only ~600-800k MEUR here, a few % of baseline total cost) —
    it's overwhelmingly `cost_carbon_emissions_total` (~60% of the total
    delta), which is why that component is excluded from this plot rather
    than swamping it. That variable itself is ~0 in every year except 2050
    and 2070: at 2050 both the base and every v7_0 scenario pay a matching
    ~6712 EUR/ton shadow price for exceeding the shared
    carbon_emissions_annual_limit.csv (limit=0 in 2050, identical file in
    both datasets); at 2070 there is no explicit limit in that file at all,
    yet every v7_0 scenario pays a large cost there (base pays ~0) despite
    NEGATIVE (net-removal) emissions that year — consistent with a
    cumulative/horizon-level carbon-budget cost being attributed entirely to
    the final period, not a real 2070 emissions price. Treat this figure's
    percentages (and fig0b_emissions_source_comparison's) with that in mind.
    """
    base_label = BASE_SCENARIO[1]
    baseline = components_with_base.loc[base_label]
    others = components_with_base.drop(base_label)
    delta = others.subtract(baseline, axis=1)
    baseline_total_cost = baseline.sum()  # all 4 components, i.e. full net_present_cost

    fig, ax = plt.subplots(figsize=(11, 6.5))
    x = np.arange(len(delta))
    bottom_pos = np.zeros(len(delta))
    bottom_neg = np.zeros(len(delta))
    for (_, comp_label), color in zip(PLOTTED_COST_COMPONENTS, PLOTTED_COST_COMPONENT_COLORS):
        vals = delta[comp_label].to_numpy()
        bottoms = np.where(vals >= 0, bottom_pos, bottom_neg)
        ax.bar(x, vals, bottom=bottoms, label=comp_label, color=color, edgecolor="white")
        bottom_pos += np.clip(vals, 0, None)
        bottom_neg += np.clip(vals, None, 0)
    totals = delta[[label for _, label in PLOTTED_COST_COMPONENTS]].sum(axis=1)
    pct_of_baseline_total = totals / baseline_total_cost * 100
    for xi, t, pct in zip(x, totals, pct_of_baseline_total):
        ax.text(xi, t, f"{pct:+.2f}%", ha="center", va="bottom" if t >= 0 else "top",
                fontsize=9, fontweight="bold")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(delta.index, rotation=25, ha="right", fontsize=9)
    ax.set_ylabel(r"$\Delta$ discounted system cost vs Crystal Ball base [MEUR]")
    ax.set_title("Non-Carbon Cost Increase vs Crystal Ball Base", fontsize=12, fontweight="bold")
    ax.set_ylim(top=ax.get_ylim()[1] * 1.15)  # headroom so the legend clears the bars
    ax.legend(fontsize=9, frameon=True, facecolor="white", framealpha=0.9, loc="upper center", ncol=3)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig1_cost_composition")


# ── 1a: Cost delta vs Full flexibility ─────────────────────────────────────

def fig1a_cost_delta(metrics: pd.DataFrame) -> None:
    baseline = metrics.loc["Full flexibility", "npc_total_meur"]
    others = metrics.drop("Full flexibility")
    delta = others["npc_total_meur"] - baseline
    pct = delta / baseline * 100

    fig, ax = plt.subplots(figsize=(7, 5))
    colors = [SCENARIO_PALETTE[list(metrics.index).index(lbl) % len(SCENARIO_PALETTE)]
              for lbl in others.index]
    bars = ax.bar(others.index, delta.values, color=colors, edgecolor="white")
    for bar, p in zip(bars, pct.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"+{p:.2f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel(r"$\Delta$ discounted system cost vs Full flexibility [MEUR]")
    ax.set_title("System Cost Delta vs Full Flexibility\n(discounted, full horizon)",
                  fontsize=12, fontweight="bold")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    fig.tight_layout()
    savefig(fig, "fig3_cost_delta")


# ── 1b: Industry capacity, 2050 ─────────────────────────────────────────────

_eth_tint = eth_tint  # moved to figure_settings.py so plot_carrier_flows.py can share it


# Print-figure-specific palette (does NOT touch the shared, dashboard-wide
# COLOR_MAP in figure_settings.py) — see plot_stacked_bars(color_map=...).
# Heat supply: heat source (water vs. waste heat) sets the hue — blue vs.
# turquoise — since that is the more physically meaningful distinction (waste
# heat is a byproduct/free input, water is an ambient draw); temperature band
# sets the shade within that hue, lighter for lower bands; ALL heat pumps
# get a hatch, so "textured = heat pump" reads at a glance regardless of hue.
# Boilers: each fuel gets its OWN hue from the full 7-color ETH swatch
# (SCENARIO_PALETTE) rather than tints of a single red family — an earlier
# version tinted coal/oil/natural_gas/biomass/waste all within the same red
# hue (15/28/0/55/70% tints), which read as near-identical at print size
# (user feedback: "coal, oil and NG look very similar, and waste and biomass
# aswell"). Now: electrode=green (electricity), natural_gas=red (its
# original base color, kept as the "reference" fossil boiler),
# coal=grey (ETH's neutral swatch — coal has no natural fossil-red
# association the way gas/oil do), oil=bronze (also "crude oil (carrier)"'s
# color in fig0b's EMISSIONS_COLOR_MAP — cross-figure consistency),
# waste=purple (ditto, matches "waste (carrier)" there). Biomass reuses
# electrode's green hue (both are the "non-fossil" boilers) but as a light
# tint PLUS a hatch, so it can't be confused with electrode's solid green.
_ETH_BLUE, _ETH_TURQUOISE, _ETH_GREEN, _ETH_RED = "#215CAF", "#007894", "#627313", "#B7352D"
_ETH_BRONZE, _ETH_PURPLE, _ETH_GREY = "#8E6713", "#A7117A", "#6F6F6F"  # full 7-color ETH swatch (SCENARIO_PALETTE)
_HP_HATCH = "/"  # subtle, sparse diagonal — repeat the character (e.g. "//") for denser hatching
_BIOMASS_HATCH = "xx"  # denser/different pattern from the HP hatch, so the two hatched families stay distinguishable
HEAT_SUPPLY_COLOR_MAP = {
    # water source: ETH blue, darker at higher temperature
    "heat_pump_industry_150_200_water": _ETH_BLUE,
    "heat_pump_industry_100_150_water": _eth_tint(_ETH_BLUE, 0.3),
    "heat_pump_industry_0_100_water": _eth_tint(_ETH_BLUE, 0.55),
    # waste heat source: ETH turquoise/petrol, darker at higher temperature
    "heat_pump_industry_150_200_waste_heat": _ETH_TURQUOISE,
    "heat_pump_industry_100_150_waste_heat": _eth_tint(_ETH_TURQUOISE, 0.3),
    "heat_pump_industry_0_100_waste_heat": _eth_tint(_ETH_TURQUOISE, 0.55),
    # boilers: one distinct ETH hue per fuel (see comment above) — no two
    # boilers now share a hue, let alone a tint of the same hue.
    "electrode_boiler_industry": _ETH_GREEN,
    "natural_gas_boiler_industry": _ETH_RED,
    "coal_boiler_industry": _ETH_GREY,
    "oil_boiler_industry": _ETH_BRONZE,
    "biomass_boiler_industry": _eth_tint(_ETH_GREEN, 0.55),
    "waste_boiler_industry": _ETH_PURPLE,
}
HEAT_SUPPLY_HATCH_MAP = {tech: _HP_HATCH for tech in [
    "heat_pump_industry_150_200_water", "heat_pump_industry_100_150_water", "heat_pump_industry_0_100_water",
    "heat_pump_industry_150_200_waste_heat", "heat_pump_industry_100_150_waste_heat", "heat_pump_industry_0_100_waste_heat",
]}
HEAT_SUPPLY_HATCH_MAP["biomass_boiler_industry"] = _BIOMASS_HATCH
# Explicit stack order (bottom → top, per user request): waste boiler at the
# very bottom, then coal/oil/biomass/natural-gas/electrode boilers, then heat
# pumps ordered high→low temperature band (150-200, then 100-150, then 0-100
# at the very top), waste-heat source before water source within each band.
# Top-to-bottom (i.e. reverse of this list, matching both the stack visually
# and the legend, which is also drawn top-to-bottom): 0-100 (water/waste),
# 100-150 (water/waste), 150-200 (water/waste), electrode, natural gas,
# biomass, oil, coal, waste. Any tech not listed here (future additions) is
# appended at the end in whatever order build_comparison_df produced, so
# nothing is dropped.
HEAT_SUPPLY_STACK_ORDER = [
    "waste_boiler_industry",
    "coal_boiler_industry",
    "oil_boiler_industry",
    "biomass_boiler_industry",
    "natural_gas_boiler_industry",
    "electrode_boiler_industry",
    "heat_pump_industry_150_200_waste_heat",
    "heat_pump_industry_150_200_water",
    "heat_pump_industry_100_150_waste_heat",
    "heat_pump_industry_100_150_water",
    "heat_pump_industry_0_100_waste_heat",
    "heat_pump_industry_0_100_water",
]
# Production techs: solid ETH colors only, no hatching (hatch_map={} below).
# Reassigned off blue/petrol/bronze/purple (user request) once electricity
# switched to ETH blue (_ELECTRICITY_COLOR below) — glass_production sat in
# the same fig4a/fig4b stacked bars as the electricity segment and shared its
# hue, so glass moved to grey and the other 3 sectors shifted to keep all 4
# mutually distinct.
PRODUCTION_COLOR_MAP = {
    "glass_production": "#6F6F6F",    # ETH grey
    "ceramic_production": "#8E6713",  # ETH bronze
    "paper_production": "#007894",    # ETH petrol/turquoise
    "food_production": "#627313",     # ETH green
}


def _year_group_labels(ax, n_groups: int, group_labels: list[str], years: list[int]) -> None:
    """Overwrites plot_stacked_bars' own xticklabels (which show the composite
    "scenario__year" column keys) with just the year, then adds one
    scenario-spanning label per group below the year ticks — same 2-tier
    labeling pattern fig4b uses for its year pairs."""
    n_yr = len(years)
    ax.set_xticks(range(n_groups * n_yr))
    ax.set_xticklabels([str(y) for _ in range(n_groups) for y in years], fontsize=8, rotation=0)
    for gi, label in enumerate(group_labels):
        center = gi * n_yr + (n_yr - 1) / 2
        ax.text(center, -0.1, label, transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=9.5, fontweight="bold")
    for gi in range(1, n_groups):
        ax.axvline(gi * n_yr - 0.5, color="#cccccc", linewidth=0.7, zorder=0)


def fig1b_industry_capacity(runs: list[Run]) -> None:
    """3 columns (COMPARISON_YEARS) x 2 rows (heat supply, production)
    small-multiples grid — reverted from two earlier layouts that didn't
    work: a 3-row/A4-portrait-tall version (shrank too small once fit to a
    document page width) and a single-row version with all 3 years' bars
    crammed per scenario (18 bars in one row read as chaotic). Here each
    subplot holds just 6 scenario bars for one year, and each ROW shares one
    y-axis scale across its 3 year-columns (_apply_shared_ylim) so capacity
    changes over time are still directly comparable, just split across
    panels instead of packed into one.

    CAVEAT on the "Heat Supply" row's 2050 column: capacity there is
    noticeably LOWER than at 2040 in every single scenario (e.g. "No
    flexibility": ~94 GW at 2040 vs ~72 GW at 2050 — a ~24% drop), even
    though the "Production Technologies" row stays essentially FLAT across
    the whole horizon (~60 ton/h throughout, confirmed directly) — this is
    NOT a declining-demand story. Checked directly against the solved model:
    it's driven by boiler-fleet lifetime retirement. natural_gas/biomass/
    electrode/coal/waste boilers all have 25-30yr lifetimes, and the model
    built most of its boiler fleet in a large initial spike (~15 GW in 2020
    + ~29 GW in 2022 alone, "No flexibility") which starts retiring right
    around 2045-2047; replacement capacity_addition in 2044-2050 combined is
    only a small fraction of what's retiring in the same window (biomass
    boiler capacity alone falls from ~11 GW at 2040 to ~1 GW at 2050). Heat
    pumps (20yr lifetime) show no such drop. Reads as a finite-horizon/
    myopic-foresight under-investment artifact near the model's terminal
    periods — the same family of terminal-year artifact fig0a/fig0b's
    docstrings already flag for cost/budget behavior — not new information
    about industry heat demand shrinking.
    """
    # temp-conversion capacity excluded here — see industry_heat_capacity() docstring;
    # its own direct-vs-conversion pathway is the subject of fig3b instead.
    heat_dfs, prod_dfs = [], []
    for year in COMPARISON_YEARS:
        heat_series = [(r.label, get_capacity(r.results, INDUSTRY_HEAT_TECHS_BOILERS_HP, "power")
                        .get(year, pd.Series(dtype=float))) for r in runs]
        prod_series = [(r.label, get_capacity(r.results, INDUSTRY_HEAT_TECHS_PRODUCTION, "power")
                        .get(year, pd.Series(dtype=float))) for r in runs]

        heat_df = build_comparison_df(heat_series)
        # See HEAT_SUPPLY_STACK_ORDER: boilers drawn first -> bottom of the
        # stack, below all heat pumps, which are then ordered high->low temperature.
        heat_df = heat_df.reindex(
            [t for t in HEAT_SUPPLY_STACK_ORDER if t in heat_df.index]
            + [t for t in heat_df.index if t not in HEAT_SUPPLY_STACK_ORDER])
        heat_dfs.append(heat_df)
        prod_dfs.append(build_comparison_df(prod_series))

    n_yr = len(COMPARISON_YEARS)
    fig, axes = plt.subplots(2, n_yr, figsize=(6 * n_yr, 11))
    fig.suptitle("Industry Technology Capacity Over Time", fontsize=14, fontweight="bold")
    with plt.rc_context({"hatch.linewidth": 0.5}):  # subtler hatch lines than the 1.0 default
        for col, year in enumerate(COMPARISON_YEARS):
            plot_stacked_bars(heat_dfs[col], f"Heat Supply (boilers & heat pumps) - {year}",
                              "GW", axes[0, col], show_segment_labels=True, show_legend=(col == n_yr - 1),
                              color_map=HEAT_SUPPLY_COLOR_MAP, hatch_map=HEAT_SUPPLY_HATCH_MAP)
    for col, year in enumerate(COMPARISON_YEARS):
        plot_stacked_bars(prod_dfs[col], f"Production Technologies - {year}",
                          "ton/h", axes[1, col], show_segment_labels=True, show_legend=(col == n_yr - 1),
                          color_map=PRODUCTION_COLOR_MAP, hatch_map={})
    _apply_shared_ylim(list(axes[0, :]), heat_dfs)
    _apply_shared_ylim(list(axes[1, :]), prod_dfs)
    for ax in axes.flat:
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    fig.text(0.5, 0.005,
             "Heat-supply 2050 dip: boiler-fleet lifetime retirement (25-30yr) outpacing late-horizon "
             "replacement investment - not a demand decline (Production row is flat). See docstring.",
             ha="center", va="bottom", fontsize=8, style="italic", color="#555555")
    fig.tight_layout(rect=[0, 0.02, 1, 0.95])
    savefig(fig, "fig4_industry_capacity")


# ── 7: Heat-supply capacity trajectory, No flexibility, full horizon ───────

def fig7_heat_supply_trajectory(runs: list[Run]) -> None:
    """Full-horizon version of fig1b's "Heat Supply" row (same techs, stack
    order, color/hatch map) for the "No flexibility" scenario only, plotting
    every modeled year (2020-2050, 2yr steps) instead of the 3-year
    COMPARISON_YEARS snapshot — lets the buildout/retirement pattern fig1b's
    docstring already flags (a ~24% capacity dip at 2050 from boiler-fleet
    lifetime retirement outpacing late-horizon replacement) be read directly
    off the trajectory rather than inferred from 3 points.

    Top panel: capacity stock per period (as fig1b). Bottom panel: capacity
    ADDITIONS per period (capacity_addition, i.e. new builds only, not net of
    retirements) — added per user request to see whether the persistently
    large natural_gas_boiler_industry stock is legacy fleet coasting on its
    25yr lifetime or actively being re-invested in.

    natural_gas_boiler_industry's SHARE of total heat-supply capacity does
    steadily fall (48% in 2020 -> ~17-22% from 2038 on, computed directly
    from get_capacity) — it just looks flat in the stock panel because total
    heat-supply capacity itself grows 2x over the same window (48->96 GW), so
    a shrinking share still occupies a similar-looking absolute band
    (~24-40 GW). Two different mechanisms are visible in the additions panel:
    coal_boiler_industry gets ONE addition, ever (2.14 GW in 2020 only, 0 in
    every subsequent period) — its whole stock is the real 2020 existing
    fleet (capacity_existing=4.26 GW) plus that one build, coasting on its
    25yr lifetime until it collapses from 12.7% share (2020) to <1% by 2044,
    with no reinvestment. natural_gas_boiler_industry instead gets repeated
    (if individually small) additions across the whole horizon — a large
    initial pair (7.2/5.5 GW, 2020/2022, on top of a real ~17.4 GW
    pre-existing 2020 fleet, while heat pumps start from a genuine 0 GW
    existing base and face the technology-diffusion S-curve ramp limit, see
    project memory addendum #9/#10), a near-zero trickle 2024-2038, then a
    small late-horizon replacement wave (1.9-2.7 GW/period, 2040-2046) as
    the original fleet starts retiring — visually dwarfed in the stacked
    additions bars by the much larger simultaneous heat-pump buildout, but
    enough to keep a nonzero natural_gas_boiler_industry floor from ever
    reaching zero within this horizon, unlike coal.

    Why gas, never coal, gets re-invested in: capex_specific_conversion is
    90 EUR/kW (natural_gas_boiler_industry) vs. 538.6 EUR/kW (coal_boiler_
    industry) vs. 1,461 EUR/kW (heat_pump_industry_150_200_water, the
    cheapest heat-pump alternative) — coal is dominated by gas on CAPEX alone
    while carrying the same fossil-emissions problem, so it is never the
    marginal fossil choice once new capacity is needed. Why gas isn't
    penalized out of existence by its emissions: natural_gas_boiler_industry
    has NO CCS retrofit option anywhere in this dataset (confirmed: no
    *_boiler*_CCS tech exists; only power-sector natural_gas_turbine_CCS
    does), so its emissions are never captured directly — but
    carbon_emissions_budget is a single pooled cumulative cap across the
    WHOLE system (all sectors/years combined, not a per-technology or
    per-sector sub-budget, see project memory addendum #7/#8), so it remains
    cheaper for the optimizer to keep some cheap gas boilers and offset their
    emissions via decarbonization elsewhere (retrofit CCS on other
    processes, power-sector renewables/CCS, DAC — see fig5) than to pay the
    >16x CAPEX premium to fully electrify industry heat within this
    horizon.

    Bottom panel: actual OPERATED output (flow_conversion_output summed
    per tech / HOURS_PER_YEAR, i.e. the average GW each tech actually
    delivers — directly comparable to the top panel's nameplate GW, their
    ratio is each tech's implied capacity factor) — added per user request
    ("why is capacity growing so much, shouldn't it only build what's
    needed / which techs are actually operated"). Total industry-heat
    OUTPUT is essentially flat at ~46 GW average across the ENTIRE horizon
    (confirmed directly, matching the flat glass/ceramic/paper/food product
    demand already established in fig1b's docstring) while nameplate
    capacity nearly doubles (48->96 GW, 2020->2028) before falling back.

    SUPERSEDES an earlier, WRONG explanation of this gap (a "baseload vs.
    peaking capacity" story) that assumed the underlying demand had
    intra-year peakiness a "No flexibility" system would need extra
    capacity to cover. Checked directly and disproven: the hourly demand
    time series (Results.get_full_ts("demand")) for glass/ceramic/paper/
    food is perfectly flat within every year (std ~1e-12 across all 8760
    hours of 2020, i.e. genuinely zero intra-year variability, no daily/
    seasonal shape at all) — there is no peak for any capacity to cover in
    this dataset.

    The real mechanism, confirmed directly in ZEN-garden's own formulation
    (constraint_technology_lifetime, zen_garden/model/technology/
    technology.py:1471): a technology's `capacity` in year y is a purely
    DETERMINISTIC sum of past `capacity_addition`s that haven't yet aged
    past their lifetime — `capacity_addition` itself is bounded (0, inf),
    i.e. STRICTLY NON-NEGATIVE. There is no decision variable anywhere in
    the model that lets the optimizer voluntarily/early-decommission
    capacity. Once built (or present as real-world capacity_existing),
    capacity stays on the books at full nameplate for its ENTIRE lifetime
    (25-30yr for boilers) regardless of whether running it is still
    economical.

    So the true sequence is a slow FLEET OVERLAP during a one-way
    technology transition, not a peak/baseload split: (1) 2020 — the real
    legacy fossil/biomass fleet covers the flat demand almost entirely,
    ~100% capacity factor, nameplate ~ output. (2) Heat pumps turn out
    far cheaper to OPERATE (near-zero marginal cost) despite a >16x CAPEX
    premium (natural_gas_boiler_industry: 90 EUR/kW vs. heat_pump_
    industry_150_200_water: 1,461 EUR/kW, capex_specific_conversion), so as
    the technology-diffusion ramp allows, the model builds heat-pump
    capacity and shifts nearly all actual output onto it — natural_gas_
    boiler_industry's capacity factor falls from 100% (2020) to 4-13%
    (2030+); coal/oil/waste boilers fall to fully idle (0%) by 2022. (3) But
    the still-young fossil/biomass vintage from 2020-2022 CANNOT be retired
    early, so it sits on the books doing almost nothing for two decades —
    this idle-but-still-counted old fleet, stacked on top of the new
    heat-pump fleet that's actually doing the work, is the entire source of
    the 48->96 GW apparent "growth." The 96->70 GW drop from 2044 is exactly
    when that original 2020-2022 vintage finally exhausts its 25-30yr
    lifetime and leaves the stock (matches fig1b's docstring finding).
    Not overbuilding, and not a peak-capacity artifact — a mechanical
    consequence of ZEN-garden having no early-decommissioning decision,
    combined with a technology cost-crossover partway through the
    horizon."""
    fig7_heat_supply_trajectory_for(runs, "No flexibility",
                                     "fig9_heat_supply_trajectory_no_flexibility")


def _output_avg_gw(r: Run, techs: list[str]) -> pd.DataFrame:
    """Actual OPERATED output per tech, as average GW (flow_conversion_output
    summed over the year's hours / HOURS_PER_YEAR) — directly comparable to
    nameplate capacity GW, their ratio being that tech's implied capacity
    factor. Shared by fig9's top ("Industry heat supply") panel and fig14a's
    same-quantity scenario comparison."""
    flow_out = r.results.get_total("flow_conversion_output")
    rows = {}
    for t in techs:
        if t not in flow_out.index.get_level_values("technology"):
            continue
        s = flow_out.xs(t, level="technology").sum(axis=0) / HOURS_PER_YEAR
        if (s.abs() > 1e-6).any():
            rows[t] = s
    return pd.DataFrame(rows).T if rows else pd.DataFrame()


def fig7_heat_supply_trajectory_for(runs: list[Run], label: str, fig_name: str) -> None:
    """Generic engine behind fig7_heat_supply_trajectory (see its docstring
    for the "No flexibility" mechanics). Parameterized over `label`/`fig_name`
    so the same plot can be produced for other scenarios, e.g. fig9b for
    "Full flexibility", added per user request to compare buildout/retirement
    trajectories side by side with the no-flexibility case."""
    r = by_label(runs, label)
    years = get_available_years(r.results)

    def _ordered(df: pd.DataFrame) -> pd.DataFrame:
        df = df.reindex(
            [t for t in HEAT_SUPPLY_STACK_ORDER if t in df.index]
            + [t for t in df.index if t not in HEAT_SUPPLY_STACK_ORDER])
        return df[[y for y in years if y in df.columns]]

    heat_df = _ordered(get_capacity(r.results, INDUSTRY_HEAT_TECHS_BOILERS_HP, "power"))
    add_df = _ordered(get_capacity_addition(r.results, INDUSTRY_HEAT_TECHS_BOILERS_HP, "power"))
    output_df = _ordered(_output_avg_gw(r, INDUSTRY_HEAT_TECHS_BOILERS_HP))

    fig, axes = plt.subplots(3, 1, figsize=(0.8 * len(heat_df.columns) + 3, 16))
    with plt.rc_context({"hatch.linewidth": 0.5}):
        plot_stacked_bars(output_df, "Industry heat supply (GW)",
                          "GW supplied", axes[0], show_segment_labels=False, show_legend=True,
                          color_map=HEAT_SUPPLY_COLOR_MAP, hatch_map=HEAT_SUPPLY_HATCH_MAP)
        plot_stacked_bars(heat_df, f"Industry Heat Supply Capacity (stock) - {label}",
                          "GW", axes[1], show_segment_labels=False, show_legend=False,
                          color_map=HEAT_SUPPLY_COLOR_MAP, hatch_map=HEAT_SUPPLY_HATCH_MAP)
        plot_stacked_bars(add_df, f"Industry Heat Supply Capacity Additions (new builds/period) - {label}",
                          "GW added", axes[2], show_segment_labels=False, show_legend=False,
                          color_map=HEAT_SUPPLY_COLOR_MAP, hatch_map=HEAT_SUPPLY_HATCH_MAP)
    for ax in axes:
        plt.setp(ax.get_xticklabels(), rotation=0)
    fig.tight_layout()
    savefig(fig, fig_name)


# fig14a snapshot years: 2020 (pre-buildout) + fig9's COMPARISON_YEARS-style
# trio (2030/2040/2050) rather than fig9's own full 2yr-step horizon — per
# user request, a 4-point before/during/after comparison of the same
# quantity fig9's TOP panel plots (actual operated output, not nameplate
# capacity — the panel that shows what's actually delivering heat, since
# fig7's own docstring already establishes nameplate capacity as a
# retirement-lag artifact that doesn't track real utilization).
FIG14A_YEARS = [2020, 2030, 2040, 2050]


def fig14a_heat_supply_output_full_vs_single(runs: list[Run]) -> None:
    """Companion to fig14b: fig9's top ("Industry heat supply", i.e. actual
    operated output not nameplate capacity — see fig7_heat_supply_trajectory's
    docstring for why output rather than capacity is the meaningful
    quantity here) panel, side by side for "Full flexibility" and "Single
    temperature level" at 2020/2030/2040/2050, with each bar's heat-pump
    share of total output called out above it — per user request, to make
    the difference in heat-pump UTILIZATION between the two scenarios
    directly readable rather than requiring the reader to sum stack
    segments themselves.

    Both scenarios deliver essentially the SAME total output at every year
    (~46 GW average throughout, confirmed directly — matches fig7's own
    flat-industrial-demand finding) — collapsing the 3 industry-heat
    temperature bands into one doesn't change how much heat is delivered,
    only how it's delivered. What differs sharply is the heat-pump SHARE of
    that output: Full flexibility's HP share climbs 2020's ~3% -> 53%
    (2030) -> 75% (2040) -> 82% (2050), while Single temperature level's
    plateaus far lower: ~3% -> 30% -> 55% -> 54% (actually DROPS slightly
    2040->2050). The mechanism is visible directly in which HP techs each
    scenario even has available: Full flexibility can dispatch all 6
    temperature/source-split heat-pump variants (0-100/100-150/150-200,
    water/waste-heat each), so cheap LOW-temperature heat pumps cover the
    low-temperature share of demand directly. Single temperature level
    collapses everything into ONE heat-supply pathway, so only the
    150-200 water/waste-heat HP variants exist at all in that scenario's
    technology set (confirmed directly: no 0-100 or 100-150 heat-pump techs
    have ANY nonzero output in this run, any year) — every unit of demand
    that in Full flexibility would have been served by a cheaper low-temp
    heat pump instead has to be served by boilers (electrode/gas) or the
    one remaining high-temp heat pump running at a less favorable COP, so
    the optimizer leans more heavily on boilers to fill the gap instead of
    building out heat-pump capacity as aggressively.
    -> SI_results/fig14a_heat_supply_output_full_vs_single_temp.svg
    """
    full_run = by_label(runs, "Full flexibility")
    single_run = by_label(runs, "Single temperature level")

    def _snapshot_output(r: Run) -> pd.DataFrame:
        df = _output_avg_gw(r, INDUSTRY_HEAT_TECHS_BOILERS_HP)
        df = df.reindex(
            [t for t in HEAT_SUPPLY_STACK_ORDER if t in df.index]
            + [t for t in df.index if t not in HEAT_SUPPLY_STACK_ORDER])
        return df[[y for y in FIG14A_YEARS if y in df.columns]]

    dfs = {full_run.label: _snapshot_output(full_run), single_run.label: _snapshot_output(single_run)}

    fig, axes = plt.subplots(1, 2, figsize=(2.0 * len(FIG14A_YEARS) + 2, 6.5))
    with plt.rc_context({"hatch.linewidth": 0.5}):
        for ax, (label, df) in zip(axes, dfs.items()):
            plot_stacked_bars(df, label, "GW supplied", ax, show_segment_labels=False,
                              show_legend=(label == single_run.label),
                              color_map=HEAT_SUPPLY_COLOR_MAP, hatch_map=HEAT_SUPPLY_HATCH_MAP)
    # Extra headroom (vs. _apply_shared_ylim's usual 0.08 default) so the
    # "HP: XX%" annotation, itself placed above plot_stacked_bars' own bar-
    # total label, has room without the two overlapping.
    _apply_shared_ylim(list(axes), list(dfs.values()), headroom=0.22)
    for ax, df in zip(axes, dfs.values()):
        hp_total = df.loc[[t for t in df.index if t.startswith("heat_pump")]].sum()
        total = df.sum()
        for xi, year in enumerate(df.columns):
            pct = 100 * hp_total[year] / total[year] if total[year] else 0.0
            ax.annotate(f"HP: {pct:.0f}%", xy=(xi, total[year]), xytext=(0, 15),
                        textcoords="offset points", ha="center", va="bottom",
                        fontsize=8.5, fontweight="bold", color=_ETH_BLUE)
        plt.setp(ax.get_xticklabels(), rotation=0)
    fig.suptitle("Industry Heat Supply Output and Heat-Pump Utilization: "
                 "Full Flexibility vs. Single Temperature Level",
                 fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    savefig(fig, "fig14a_heat_supply_output_full_vs_single_temp")


# ── 5: Retrofit carbon-capture tech usage, No flexibility vs. base ─────────

# Retrofit/add-on carbon-capture technologies: each one captures CO2 FROM an
# existing production/generation process (either a "_CCS" variant of the base
# tech, or a "_post_comb" add-on unit), as opposed to DAC (a standalone
# direct-air-capture plant that isn't attached to any other process) or
# carbon_storage/carbon_pipeline (storage/transport infrastructure, not
# capture itself) — those 3 are deliberately excluded here. Confirmed via a
# solved v8_0 run: all 8 output onto the "carbon" carrier (ktonCO2eq/h, same
# unit as their own "power" capacity — unlike fig4b's flow_conversion_input
# case, get_total("flow_conversion_output") summing this carrier across the
# year's hours gives a genuine annual kt-CO2-captured total, not something
# needing a HOURS_PER_YEAR correction). cement_post_comb/BF_BOF_CCS/NG_DRI_
# CCS/SMR_CCS/biomass_plant_CCS/natural_gas_turbine_CCS exist in both "No
# flexibility" and "Crystal Ball (base)" (steel/cement/power-sector CCS
# predates the industry-heat extension); ceramic_post_comb/glass_post_comb
# exist ONLY in "No flexibility" (ceramic/glass production don't exist in
# base at all — see project memory) and so show as 0 for base, by design.
RETROFIT_CCS_TECHS = [
    "cement_post_comb", "ceramic_post_comb", "glass_post_comb",
    "BF_BOF_CCS", "NG_DRI_CCS", "SMR_CCS",
    "biomass_plant_CCS", "natural_gas_turbine_CCS",
]
RETROFIT_CCS_LABELS = {
    "cement_post_comb": "Cement\n(post-comb.)",
    "ceramic_post_comb": "Ceramic\n(post-comb.)",
    "glass_post_comb": "Glass\n(post-comb.)",
    "BF_BOF_CCS": "BF-BOF\n(CCS)",
    "NG_DRI_CCS": "NG-DRI\n(CCS)",
    "SMR_CCS": "SMR\n(CCS)",
    "biomass_plant_CCS": "Biomass plant\n(CCS)",
    "natural_gas_turbine_CCS": "Nat. gas turbine\n(CCS)",
}


def _ccs_captured_by_tech(r, year: int) -> pd.Series:
    """Actual CO2 captured that year (kt CO2eq) per retrofit tech — see the
    module-level RETROFIT_CCS_TECHS comment on why no unit conversion is
    needed here despite fig4b's flow_conversion_input caveat."""
    flow_out = r.get_total("flow_conversion_output")
    if "carbon" not in flow_out.index.get_level_values("carrier"):
        return pd.Series(dtype=float)
    carbon = flow_out.xs("carbon", level="carrier")
    rows = {}
    for tech in RETROFIT_CCS_TECHS:
        if tech not in carbon.index.get_level_values("technology"):
            continue
        s = carbon.xs(tech, level="technology")
        if year in s.columns:
            rows[tech] = float(s[year].sum())
    return pd.Series(rows)


def fig5_retrofit_ccs_comparison(no_flex_run: Run, base_run: Run) -> None:
    """CO2 actually captured that year (kt CO2eq) by each retrofit-CCS
    technology, "No flexibility" (v9_0) vs. "Crystal Ball (base)", year YEAR.
    See RETROFIT_CCS_TECHS above for which technologies count as "retrofit"
    and why DAC/carbon_storage/carbon_pipeline are excluded.

    This used to be a 2-panel figure (installed capture CAPACITY alongside
    captured CO2). The capacity panel was dropped per user question ("are you
    sure about these numbers? is the cost of CCS very low? why is so much
    installed?") after directly verifying two separate findings against the
    dataset, both of which make installed capacity a misleading number to
    plot here:

    (1) Installed capacity is NOT economically chosen: at YEAR=2036, all 8
    technologies land within a few % of each other's capacity WITHIN a given
    run (~14.3 for "No flexibility", ~11.9 for base), despite being
    completely different processes (a blast furnace vs. a gas turbine vs. a
    cement kiln). Root cause: `capacity_limit`=inf (unconstrained) for all 8,
    but they share an IDENTICAL default technology-diffusion parameter pair
    (`capacity_addition_unbounded`~=0.0114 GW/node/period,
    `max_diffusion_rate`=0.13/yr) AND all start from `capacity_previous`=0 in
    2020 (no real-world existing retrofit-CCS fleet for ANY of them) — same
    cold-start deployment-rate mechanism as the industry heat pumps in
    project memory's diffusion investigation (see fig6_diffusion_mechanisms).
    With capacity_previous=0 the diffusion constraint's growth term vanishes,
    so early buildout is governed almost entirely by the shared
    capacity_addition_unbounded floor — identical for every tech regardless
    of what it captures from or what it costs.

    (2) "Is the cost of CCS very low" — yes, for 2 of the 8, literally:
    checked capex_specific_conversion/opex_specific_fixed/opex_specific_
    variable directly in data/Crystal_Ball/set_technologies' attributes.json
    files. biomass_plant_CCS and natural_gas_turbine_CCS are all-zero on
    every one of those three parameters (a real data artifact — free
    capture), while cement_post_comb/BF_BOF_CCS/NG_DRI_CCS/SMR_CCS instead
    carry large, nonzero capex (~3.8-7.4M EUR per tCO2eq/h of capacity). So
    the "why is so much installed" answer is actually two independent
    effects stacking: a shared diffusion-rate ceiling that installs SOME
    capacity for every retrofit tech regardless of cost (see (1)), on top of
    which 2 of the 8 techs additionally cost nothing to build. Installed
    capacity therefore conflates "diffusion-allowed" and "free" builds with
    genuine cost-effective ones — CO2 actually captured is the only number
    here where dispatch/utilization (not those two artifacts) drives the
    result, e.g. SMR_CCS captures ~80x more than BF_BOF_CCS despite
    near-identical installed capacity.
    """
    runs = [(base_run.label, base_run, SCENARIO_PALETTE[6]),
            (no_flex_run.label, no_flex_run, SCENARIO_PALETTE[0])]

    df = pd.DataFrame({label: _ccs_captured_by_tech(run.results, YEAR) for label, run, _ in runs})
    df = df.reindex(RETROFIT_CCS_TECHS).fillna(0.0)
    df = df[(df.abs() > 1e-6).any(axis=1)]

    fig, ax = plt.subplots(figsize=(9, 6))
    n = len(runs)
    width = 0.8 / n
    x = np.arange(len(df))
    for i, (label, _, color) in enumerate(runs):
        offsets = x + (i - (n - 1) / 2) * width
        ax.bar(offsets, df[label].to_numpy(), width, label=label, color=color, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels([RETROFIT_CCS_LABELS[t] for t in df.index], fontsize=8.5)
    ax.set_ylabel(f"CO$_2$ captured, {YEAR} [ktCO$_2$eq]")
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=9, frameon=False, loc="upper left")
    fig.suptitle(f"Retrofit Carbon-Capture: CO$_2$ Actually Captured - Year {YEAR}", fontsize=13, fontweight="bold")
    ax.text(0.5, -0.14,
             "Installed capacity omitted: shared regardless of cost by a deployment-rate ceiling from a zero\n"
             "real-world base, and 2 of 8 techs cost literally $0 to build in this dataset - see docstring.",
             transform=ax.transAxes, ha="center", va="top", fontsize=7.5, style="italic", color="#555555")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    savefig(fig, "fig7_retrofit_ccs_comparison")


# ── 2: DSM cycles by product, 2050 ──────────────────────────────────────────

# ammonia_DSM/methanol_DSM store an energy carrier (GWh); the other 8
# INDUSTRY_DSM_TECHS store a mass carrier (kt-of-product) — confirmed via
# Results.get_unit() against a solved run. dsm_cycles()'s discharge/capacity
# ratio is unit-safe regardless (each tech divides by its OWN capacity in its
# own native unit, so the resulting cycles/year is dimensionless either way),
# but fig2_dsm_cycles_by_product hatches these two bars so a reader isn't left
# assuming all 10 products are moving directly comparable physical quantities.
DSM_ENERGY_CARRIER_TECHS = {"ammonia_DSM", "methanol_DSM"}


def dsm_cycles(r, year: int) -> pd.Series:
    discharge = get_storage_flows(r, INDUSTRY_DSM_TECHS, "flow_storage_discharge")
    capacity = get_capacity(r, INDUSTRY_DSM_TECHS, "energy")
    cycles = {}
    for tech in INDUSTRY_DSM_TECHS:
        cap = capacity.loc[tech, year] if tech in capacity.index and year in capacity.columns else 0.0
        dis = discharge.loc[tech, year] if tech in discharge.index and year in discharge.columns else 0.0
        cycles[tech] = dis / cap if cap > 1e-9 else 0.0
    return pd.Series(cycles)


def fig2_dsm_cycles_by_product(runs: list[Run]) -> None:
    # "Full flexibility" (opt.) vs "DSM pessimistic" (pess.) isolates the
    # demand-shiftability-assumption effect on utilization directly, since
    # both scenarios otherwise share the same industry heat / TES setup
    # (Table SIScenarios, Table SIDSMCategorization) — unlike the previous
    # comparison against "Single temperature level", which also changes the
    # temperature-band resolution and so conflated two different effects.
    scenarios = ["Full flexibility", "DSM pessimistic"]
    legend_labels = {"Full flexibility": "Optimistic (Full flexibility)",
                      "DSM pessimistic": "Pessimistic (DSM pessimistic)"}
    df = pd.DataFrame({label: dsm_cycles(by_label(runs, label).results, YEAR) for label in scenarios})
    is_energy_carrier = {t: t in DSM_ENERGY_CARRIER_TECHS for t in df.index}
    df.index = [t.replace("_DSM", "").replace("_", " ") for t in df.index]
    is_energy_carrier = {t.replace("_DSM", "").replace("_", " "): v for t, v in is_energy_carrier.items()}
    df = df.sort_values(scenarios[0], ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    n = len(scenarios)
    width = 0.8 / n
    x = np.arange(len(df))
    with plt.rc_context({"hatch.linewidth": 0.5}):  # subtler hatch lines than the 1.0 default
        for i, label in enumerate(scenarios):
            offsets = x + (i - (n - 1) / 2) * width
            color = SCENARIO_PALETTE[[l for _, l in SCENARIOS].index(label)]
            bars = ax.bar(offsets, df[label].values, width, label=legend_labels[label],
                          color=color, edgecolor="white")
            for bar, t in zip(bars, df.index):
                if is_energy_carrier[t]:
                    bar.set_hatch("//")
    ax.set_xticks(x)
    ax.set_xticklabels(df.index, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Discharge cycles / year")
    ax.set_title(f"DSM Utilization by Product, {YEAR}\n"
                 "Demand-Shiftability Assumption (DSM Categories)", fontsize=12, fontweight="bold")
    scenario_handles, scenario_labels = ax.get_legend_handles_labels()
    energy_handle = Patch(facecolor="white", edgecolor="black", hatch="//",
                          label="Energy carrier (GWh): ammonia, methanol")
    mass_handle = Patch(facecolor="white", edgecolor="black",
                        label="Mass carrier (kt): others")
    ax.legend(scenario_handles + [energy_handle, mass_handle],
             scenario_labels + [energy_handle.get_label(), mass_handle.get_label()],
             fontsize=9, frameon=False)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig5_dsm_cycles_by_product")


# ── 3b: Direct vs temperature-conversion heat pathway, 2050 ─────────────────
# (no more 3a: fig3a_temp_sensitivity_summary was deleted per user request —
# its cost and capacity bars duplicated fig0a/fig1b, and the one new number it
# carried, the emissions delta, is reported as prose in 03_SI.tex instead of a
# standalone chart. Recompute via metrics.loc["Single temperature level"] vs
# metrics.loc["Full flexibility"] on "emissions_total_mton" if that % ever
# needs to be regenerated.)

def heat_pathway_split_by_band(r, year: int) -> pd.DataFrame:
    """Net (non-double-counted) end-use heat demand met per temperature band,
    split into direct (boiler/HP) vs. conversion-cascade-sourced.

    `get_carrier_production` per carrier is GROSS output onto that carrier,
    which for a mid/high band includes energy that gets immediately consumed
    again as input to the next-lower conversion technology (lossless, 1:1).
    Naively summing gross production across bands therefore double- (or
    triple-) counts any energy that cascades down more than one step — see
    fig3b's module-level note for the numbers this produced. This function
    nets that out: for each band, the amount forwarded to the band below
    (`downstream_draw`, = the conversion-sourced gross production of that
    lower band) is subtracted before splitting into direct/conversion, so
    summing the result across bands gives actual net end-use demand met, not
    an inflated pass-through total. INDUSTRY_HEAT_CARRIERS_ENERGY must be
    ordered low-to-high for the downstream-draw lookup below to be correct.
    """
    bands = INDUSTRY_HEAT_CARRIERS_ENERGY
    gross = {}
    for carrier in bands:
        prod = get_carrier_production(r, carrier)
        if prod.empty or year not in prod.columns:
            gross[carrier] = (0.0, 0.0)
            continue
        direct = prod.loc[prod.index.isin(INDUSTRY_HEAT_TECHS_BOILERS_HP), year].sum()
        conversion = prod.loc[prod.index.isin(INDUSTRY_HEAT_TECHS_TEMP_CONV), year].sum()
        gross[carrier] = (direct, conversion)

    rows = {}
    for i, carrier in enumerate(bands):
        direct, conversion = gross[carrier]
        total = direct + conversion
        downstream_draw = gross[bands[i - 1]][1] if i > 0 else 0.0
        frac_forwarded = downstream_draw / total if total > 1e-9 else 0.0
        rows[carrier] = {
            "Direct (boiler/HP)": direct * (1 - frac_forwarded),
            "Via conversion cascade": conversion * (1 - frac_forwarded),
        }
    return pd.DataFrame(rows).T  # index: carrier (low to high); columns: Direct, Via conversion cascade


# cmr10 (this module's serif font) has no degree-sign glyph, so a raw "°"
# renders as a garbled substitute character — the superscript-circle is built
# in mathtext instead (mathtext.fontset "cm" covers \circ correctly).
BAND_LABELS = {"heat_industry_0_100": r"0-100$^\circ$C", "heat_industry_100_150": r"100-150$^\circ$C",
               "heat_industry_150_200": r"150-200$^\circ$C"}


def fig3b_heat_pathway(runs: list[Run]) -> None:
    # Fixed at 2050 (not the module-level YEAR=2036 snapshot used elsewhere)
    # per the figure's documented intent (see module docstring above).
    year = 2050
    scenarios = ["Full flexibility", "Single temperature level"]
    bands = INDUSTRY_HEAT_CARRIERS_ENERGY
    dfs = {label: heat_pathway_split_by_band(by_label(runs, label).results, year) for label in scenarios}
    colors = {"Direct (boiler/HP)": "#215CAF", "Via conversion cascade": "#8E6713"}  # ETH blue / bronze
    hatches = {"Full flexibility": "", "Single temperature level": "//"}

    fig, ax = plt.subplots(figsize=(5, 7.5))
    n = len(scenarios)
    bar_h = 0.8 / n
    y = np.arange(len(bands))
    for i, label in enumerate(scenarios):
        offsets = y + (i - (n - 1) / 2) * bar_h
        df = dfs[label]
        left = np.zeros(len(bands))
        for col in ["Direct (boiler/HP)", "Via conversion cascade"]:
            vals = df.loc[bands, col].to_numpy()
            ax.barh(offsets, vals, left=left, height=bar_h, color=colors[col], edgecolor="white",
                     hatch=hatches[label], label=col if i == 0 else None)
            left += vals
        for yi, t in zip(offsets, left):
            ax.text(t, yi, f" {label}", va="center", fontsize=7.5)
    ax.set_yticks(y)
    ax.set_yticklabels([BAND_LABELS[b] for b in bands], fontsize=9)
    ax.set_xlim(right=ax.get_xlim()[1] * 1.35)  # headroom for the end-of-bar labels
    ax.set_xlabel("Net end-use heat demand met [GWh]")
    ax.set_title(f"Heat Demand Met by Temperature Band, {year}", fontsize=11, fontweight="bold")
    ax.legend(fontsize=9, frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig6_heat_pathway")


# ── 4: Low-temperature input heat demand by sector and temperature band ────

HEAT_DEMAND_INPUT_JSON = FIGURES_DIR / "heat_demand_by_sector_input.json"

# Same 4 sectors/hues as PRODUCTION_COLOR_MAP above, reused here so a sector
# reads as the same color across every SI figure it appears in. Within each
# sector's bar, temperature band sets the tint (darker = higher band), the
# same hue-for-identity / tint-for-temperature convention HEAT_SUPPLY_COLOR_
# MAP uses (source sets hue, band sets tint) — 0.55/0.3/0 tints mirror that
# map's own 0_100/100_150/150_200 tint values exactly.
HEAT_DEMAND_SECTOR_LABELS = {"glass": "Glass", "ceramic": "Ceramic", "paper": "Paper", "food": "Food"}
HEAT_DEMAND_BAND_TINTS = {"0_100": 0.55, "100_150": 0.3, "150_200": 0.0}
HEAT_DEMAND_BAND_LABELS = {"0_100": r"0-100$^\circ$C", "100_150": r"100-150$^\circ$C", "150_200": r"150-200$^\circ$C"}

# High-temperature fuel demand, stacked on top — a DIFFERENT supply pathway
# (direct combustion, no heat_industry_* carrier involved), not a 4th heat-
# demand band, hence one flat grey (not a sector/band hue) rather than a tint
# scale. Carrier sets the HATCH pattern instead (fixed per carrier, so e.g.
# natural_gas has the same pattern in every sector's bar) — hue/tint is
# reserved for "which sector, which temperature band" (the actual question
# this figure answers); hatch alone is enough to tell carriers apart within
# the single "how much fuel, for scale" grey.
_ETH_GREY = "#6F6F6F"
FUEL_CARRIER_HATCHES = {"natural_gas": ".", "hard_coal": "x", "oil": "+", "biomass": "/",
                        "waste": "\\", "hydrogen": "o", "fuel_to_process": ""}
# Denser than FUEL_CARRIER_HATCHES: a legend swatch is a small fraction of a
# bar segment's area, so the same single-character hatch that reads fine on a
# bar all but disappears at swatch size — legend patches get their own,
# denser pattern (plus a thicker hatch linewidth, applied via rc_context
# where the legend is built) purely so the pattern itself stays visible;
# bars keep the lighter version so labels drawn on top stay readable.
FUEL_CARRIER_LEGEND_HATCHES = {"natural_gas": "...", "hard_coal": "xxx", "oil": "+++", "biomass": "///",
                               "waste": "\\\\\\", "hydrogen": "ooo", "fuel_to_process": ""}
FUEL_CARRIER_LABELS = {"natural_gas": "Natural gas", "hard_coal": "Hard coal", "oil": "Oil", "biomass": "Biomass",
                       "waste": "Waste", "hydrogen": "Hydrogen", "fuel_to_process": "Fuel to process"}


def _fuel_legend_label(carrier: str) -> str:
    """"Fuel: {label}" for every real carrier, but "fuel_to_process" already
    reads as a complete legend entry on its own -- prefixing it too would
    read as "Fuel: Fuel to process"."""
    label = FUEL_CARRIER_LABELS[carrier]
    return label if carrier == "fuel_to_process" else f"Fuel: {label}"
# fuel_to_kiln (glass/ceramic, ZEN-creator commit 1687533) and fuel_for_cement
# (cement_kiln's own input_carrier) are both intermediate, blended-fuel hub
# carriers with no real-world identity of their own -- produced from actual
# raw fuels by dedicated X_to_kilnfuel/X_to_cement_fuel conversion techs, each
# with its OWN conversion factor. Splitting THOSE raw fuels back out (as an
# earlier version of this figure did for cement) either double-counts the
# blending tech's own efficiency loss, or -- for fig4b's steel bar, where
# NG_DRI/H2_DRI's natural_gas/hydrogen inputs are real and already correct --
# just recreates the early-buildout NG-vs-H2 diffusion-limit-artifact
# confusion documented in this figure's old CAVEAT. User feedback: stop
# splitting all three by carrier; consolidate into one flat, unhatched grey
# "Fuel to process" segment instead -- _consolidate_blended_fuel does this for
# fuel_to_kiln/fuel_for_cement, _merge_dri_fuel for NG_DRI/H2_DRI.
_BLENDED_FUEL_CARRIERS = ("fuel_to_kiln", "fuel_for_cement", "fuel_to_process")


def _consolidate_blended_fuel(fuel_by_carrier: dict) -> dict:
    """Merges every _BLENDED_FUEL_CARRIERS key present in `fuel_by_carrier`
    into one shared "fuel_to_process" entry, so the generic per-carrier
    rendering loop draws (and labels) all of them identically regardless of
    which blended-fuel hub they came from. No-op if none are present."""
    present = [c for c in _BLENDED_FUEL_CARRIERS if c in fuel_by_carrier]
    if not present:
        return fuel_by_carrier
    out = {k: v for k, v in fuel_by_carrier.items() if k not in _BLENDED_FUEL_CARRIERS}
    out["fuel_to_process"] = sum(fuel_by_carrier[c] for c in present)
    return out


def _merge_dri_fuel(fuel_by_carrier: pd.Series) -> pd.Series:
    """Merges NG_DRI/H2_DRI's natural_gas/hydrogen entries into one
    "fuel_to_process" entry -- unlike fuel_to_kiln/fuel_for_cement these are
    real, correctly-computed primary-carrier flows (no blending tech
    involved), so this is a pure presentation choice, not a conversion-factor
    fix. BF_BOF's hard_coal is untouched (a real, unambiguous carrier -- see
    _BLENDED_FUEL_CARRIERS' docstring)."""
    dri_carriers = [c for c in ("natural_gas", "hydrogen") if c in fuel_by_carrier.index]
    if not dri_carriers:
        return fuel_by_carrier
    out = fuel_by_carrier.drop(index=dri_carriers)
    out["fuel_to_process"] = fuel_by_carrier[dri_carriers].sum()
    return out
# Single-character hatches (sparser than the "xx"/".." used elsewhere in this
# module) plus a white label backing (below) — a dense hatch under white text
# was illegible; a light hatch + opaque label background reads cleanly at both
# small and large segment sizes.
_FUEL_LABEL_BBOX = dict(facecolor="white", edgecolor="none", alpha=0.75, pad=1.5)

# Electricity: not temperature-banded and not part of the >200°C fuel mix —
# every X_production tech has a fixed electricity input alongside both (SectorParams.
# cf_elec). ETH blue, matching drawio's system-overview diagrams (user
# request) — this is the CARRIER's color, deliberately independent of
# electrode_boiler_industry's own green in HEAT_SUPPLY_COLOR_MAP (that map
# colors boiler/heat-pump IDENTITY, not the carrier they consume; see that
# section's own header comment).
_ELECTRICITY_COLOR = _ETH_BLUE
_ELECTRICITY_LABEL = "Electricity"


def fig4a_heat_demand_by_sector() -> None:
    """Low-temperature industry heat-demand assumption by sector and temperature
    band (FEC_YEAR=2023), i.e. the `demand` ZEN-creator writes onto
    heat_industry_0_100/100_150/150_200 for glass/ceramic/paper/food — NOT a
    solved-model result (contrast fig3b, which shows how the model then meets
    this demand). Grey segments on top add each sector's high-temperature
    (>200°C) fuel demand, split by carrier, for scale: that demand is met by
    DIRECT FUEL COMBUSTION, not any heat_industry_* carrier, so it is a
    different supply pathway rather than a 4th heat-demand band — shown here
    only so the colored low-temperature bands can be read against each
    sector's full process-energy intensity, not in isolation. Ceramic's fuel
    mix includes "oil" (JRC-IDEES "Other liquids", 15.2% of its 2023 thermal
    FEC) since ZEN-creator commit 1f3f708 added the MODEL_CARRIER_MAP entry —
    previously that share was dropped entirely rather than shown. Glass/
    ceramic's fuel mix also includes "Fuel to process" (ZEN-creator commit
    1687533's fuel_to_kiln carrier, consolidated here via
    _consolidate_blended_fuel — see _BLENDED_FUEL_CARRIERS' docstring for
    why this is shown as one flat grey segment rather than split by the
    fuel_to_kiln-switching techs' own raw carriers). A final green segment
    adds each sector's electricity demand (not temperature-banded, not part
    of the fuel mix — a separate, fixed input every X_production tech has
    alongside both).

    All three pieces are demand_volume[sector].sum() (tonproduct/hour) times a
    GW/(tonproduct/hour) conversion factor, from ProcessParametrizationDataset
    itself (self._heat_cfs, self._sector_params[s].cf_fuel/cf_elec,
    self._fuel_shares) — the exact same object/attributes that build each
    production tech's real conversion_factor, not a re-derivation. See
    extract_heat_demand_by_sector.py's docstring for the full provenance chain
    (Rehfeldt2017.csv per-sub-process temperature distributions ->
    compute_sector_params(), JRC-IDEES thermal FEC -> fuel_shares) and for the
    cross-check against a materialized dataset (Crystal_Ball_ind_heat_v7_3):
    this script's numbers match that dataset's demand.csv sums and
    glass_production's attributes.json conversion factors exactly.

    Values are AGGREGATED (summed) ACROSS ALL MODEL_NODES — EU27 (minus MT,
    CY) + CH + NO + UK — not a per-country breakdown. In GW, the same unit as
    each heat_industry_* carrier's own `demand` attribute (energy carrier,
    unit "GW"), so bar heights are directly comparable to fig1b's
    heat-supply-capacity panel.
    """
    if not HEAT_DEMAND_INPUT_JSON.exists():
        print(f"  skipping fig4a_heat_demand_by_sector: {HEAT_DEMAND_INPUT_JSON.relative_to(REPO_ROOT)} "
              "not found — run scripts/extract_heat_demand_by_sector.py under zen-creator-env first")
        return
    import json
    data = json.loads(HEAT_DEMAND_INPUT_JSON.read_text())
    sectors = list(HEAT_DEMAND_SECTOR_LABELS)
    for s in sectors:
        data[s]["fuel_by_carrier"] = _consolidate_blended_fuel(data[s]["fuel_by_carrier"])
    bands = list(HEAT_DEMAND_BAND_TINTS)
    fuel_carriers = [c for c in FUEL_CARRIER_HATCHES if any(c in data[s]["fuel_by_carrier"] for s in sectors)]

    fig, ax = plt.subplots(figsize=(12, 7))
    x = np.arange(len(sectors))
    heat_vals = {band: np.array([data[s]["heat"][band] for s in sectors]) for band in bands}
    fuel_vals = {c: np.array([data[s]["fuel_by_carrier"].get(c, 0.0) for s in sectors]) for c in fuel_carriers}
    electricity_vals = np.array([data[s]["electricity"] for s in sectors])
    totals = sum(heat_vals.values()) + sum(fuel_vals.values()) + electricity_vals
    label_threshold = 0.025 * totals.max()  # segments smaller than this would overlap their own text

    bottom = np.zeros(len(sectors))
    for band in bands:
        vals = heat_vals[band]
        colors = [_eth_tint(PRODUCTION_COLOR_MAP[f"{s}_production"], HEAT_DEMAND_BAND_TINTS[band]) for s in sectors]
        for xi, bi, vi, ci in zip(x, bottom, vals, colors):
            ax.bar(xi, vi, 0.6, bottom=bi, color=ci, edgecolor="white", linewidth=0.5)
            if vi > label_threshold:
                ax.text(xi, bi + vi / 2, f"{vi:.2f}", ha="center", va="center", fontsize=8,
                        color=_text_color_for_bg(ci))
        bottom += vals
    heat_top = bottom.copy()
    with plt.rc_context({"hatch.linewidth": 0.5}):
        for carrier in fuel_carriers:
            vals = fuel_vals[carrier]
            hatch = FUEL_CARRIER_HATCHES[carrier]
            for xi, bi, vi in zip(x, bottom, vals):
                ax.bar(xi, vi, 0.6, bottom=bi, color=_ETH_GREY, edgecolor="white", linewidth=0.5, hatch=hatch)
                if vi > label_threshold:
                    ax.text(xi, bi + vi / 2, f"{vi:.2f}", ha="center", va="center", fontsize=8,
                            color="black", bbox=_FUEL_LABEL_BBOX)
            bottom += vals
    fuel_top = bottom.copy()
    for xi, bi, vi in zip(x, bottom, electricity_vals):
        ax.bar(xi, vi, 0.6, bottom=bi, color=_ELECTRICITY_COLOR, edgecolor="white", linewidth=0.5)
        if vi > label_threshold:
            ax.text(xi, bi + vi / 2, f"{vi:.2f}", ha="center", va="center", fontsize=8,
                    color=_text_color_for_bg(_ELECTRICITY_COLOR))
    bottom += electricity_vals
    for xi, hi in zip(x, heat_top):
        if hi > 0:
            ax.plot([xi - 0.3, xi + 0.3], [hi, hi], color="black", linewidth=1.0, linestyle=":")
    for xi, fi in zip(x, fuel_top):
        if fi > 0:
            ax.plot([xi - 0.3, xi + 0.3], [fi, fi], color="black", linewidth=1.0, linestyle=":")
    for xi, total in zip(x, bottom):
        ax.text(xi, total, f"{total:.2f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([HEAT_DEMAND_SECTOR_LABELS[s] for s in sectors], fontsize=10)
    ax.set_ylabel("Heat / fuel demand [GW]")
    ax.set_title("Low-Temperature Industry Heat Demand by Sector and Temperature Band\n"
                  "(input assumption, ZEN-creator base year 2023, aggregated across all nodes)",
                  fontsize=12, fontweight="bold")
    band_handles = [Patch(facecolor=_eth_tint(_ETH_GREY, HEAT_DEMAND_BAND_TINTS[b]),
                           edgecolor="white", label=f"Heat carrier: {HEAT_DEMAND_BAND_LABELS[b]}") for b in bands]
    fuel_handles = [Patch(facecolor=_ETH_GREY, edgecolor="white", linewidth=0.4,
                           hatch=FUEL_CARRIER_LEGEND_HATCHES[c],
                           label=_fuel_legend_label(c)) for c in fuel_carriers]
    electricity_handle = [Patch(facecolor=_ELECTRICITY_COLOR, edgecolor="white", label=_ELECTRICITY_LABEL)]
    with plt.rc_context({"hatch.linewidth": 1.3}):
        ax.legend(handles=band_handles + fuel_handles + electricity_handle, fontsize=8.5, frameon=True,
                  facecolor="white", framealpha=0.9, edgecolor="none", loc="upper left", ncol=2,
                  handlelength=3.0, handleheight=1.8, columnspacing=1.2)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig1_heat_demand_by_sector", subdir="method")


# ── 4b: New-sector heat demand vs. pre-existing cement/steel fuel mix ──────

# Reconstruction: this figure (and fig6, originally numbered "fig99") originally existed only as a
# raw SVG under data/outputs/euler_outputs/ and data/outputs/figures/SI_
# results/, committed without a generating script anywhere in the repo or
# any branch (verified via `git log --all --diff-filter=A` /
# `git ls-tree -r <branch>` across every local+remote branch) — added
# directly in commit f3c6c1e ("add results and 2 new figure for anaylsis").
# Both were built from the old v7_1-era, 2025-2070/5yr-interval run grid and
# went stale once results moved to v8_0's 2020-2048/2yr-interval grid. Per
# user decision, reconstructed here (not just re-copied) from the rendered
# SVGs' own visible structure/values/labels plus direct verification against
# a solved v8_0 run, rather than left as an unreproducible artifact.

# Cement/primary-steel each get a post-processing step applied to
# _tech_fuel_by_carrier's raw per-carrier Series, both towards the same goal
# as _consolidate_blended_fuel above -- one flat "Fuel to process" segment
# instead of a per-carrier split -- but for two DIFFERENT underlying reasons:
#
# Cement: cement_kiln's own input_carrier is ["fuel_for_cement",
# "electricity"] -- "fuel_for_cement" is an intermediate, blended carrier
# with no real-world identity, produced from the ACTUAL raw fuels by 4
# dedicated conversion techs (coal/waste/hydrogen/biomass_to_cement_fuel),
# each with its OWN conversion factor. An earlier version of this figure
# read those 4 techs' own raw-carrier inputs instead of cement_kiln's
# "fuel_for_cement" directly, to show a real per-fuel split -- but summing
# raw inputs across techs with different efficiencies doesn't cleanly equal
# "how much fuel_for_cement cement_kiln actually consumed", i.e. exactly the
# conversion-factor mismatch _BLENDED_FUEL_CARRIERS' docstring describes.
# Reading cement_kiln's own input directly (via plain _tech_fuel_by_carrier,
# then _consolidate_series to rename "fuel_for_cement" -> "fuel_to_process")
# sidesteps that mismatch entirely.
#
# Primary steel: BF_BOF (hard_coal) and NG_DRI/H2_DRI (natural_gas/hydrogen)
# are three real, alternative primary-steel production pathways grouped into
# one bar (matching how the original figure grouped "BF-BOF/DRI") -- their
# carrier flows are each already correct on their own (no blending tech, no
# conversion-factor issue). But NG_DRI vs H2_DRI's split is a diffusion-limit
# artifact of early tech buildout, not a genuine fuel preference (both hit
# the same shared technology-diffusion ceiling from ~zero real-world
# capacity -- see fig6_diffusion_mechanisms), so showing hydrogen/natural_gas
# as separate segments invited exactly that ("is that much steel from H2
# really right?") misreading. _merge_dri_fuel merges the two into
# "fuel_to_process" too, purely for clarity -- BF_BOF's hard_coal is left
# untouched (a real, unambiguous segment).
def _consolidate_series(s: pd.Series) -> pd.Series:
    return pd.Series(_consolidate_blended_fuel(s.to_dict()))


FIG4B_SECTOR_GROUPS = [
    ("Cement\n(clinker)", ["cement_kiln"], _consolidate_series),
    ("Primary steel\n(BF-BOF/DRI)", ["BF_BOF", "NG_DRI", "H2_DRI"], _merge_dri_fuel),
    ("Secondary steel\n(EAF)", ["EAF"], None),
]


def _tech_fuel_by_carrier(r, techs: list[str], year: int) -> pd.Series:
    """Sums flow_conversion_input across `techs` (and across all nodes, via
    get_total's own default), split by carrier, for a single year, converted
    from ZEN-garden's annual-total GWh (get_total sums the full-resolution
    hourly GW flow across the year, but get_unit() still reports the
    pre-summation "GW" label without flagging that implicit integration — see
    project memory on get_unit()/convert_to_yearly_unit) down to an average-
    GW figure, so it's directly comparable to fig4a's heat-demand bars (a true
    GW capacity-equivalent figure, not an annual energy total)."""
    flow_in = r.get_total("flow_conversion_input")
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


def fig4b_industry_fuel_demand_comparison(runs: list[Run]) -> None:
    """Puts the new sectors' low-temperature heat-demand assumption (fig4a,
    left of the divider — same JSON, same bars) next to the pre-existing
    cement/steel sectors' actual SOLVED fuel/electricity input (right of the
    divider), so the new sectors' scale can be read against sectors already
    in the model before the industry-heat extension.

    Cement/steel bars are pulled from a single representative run ("Full
    flexibility") — per project memory, cement_kiln/BF_BOF/EAF/NG_DRI/H2_DRI's
    flows are scenario-invariant (unaffected by the industry-heat flexibility
    scenarios), so the choice of run doesn't materially matter here, only
    which techs/carriers do. Primary steel groups BF_BOF (blast-furnace
    route, hard_coal only) with NG_DRI/H2_DRI (direct-reduction routes) into
    one bar, matching how the original figure grouped "BF-BOF/DRI" — all
    three are alternative primary-steel production pathways, not separate
    demand sectors.

    Cement/steel are each shown as ONE bar, at the LATEST year COMPARISON_YEARS
    (2030/2040/2050, see that constant's own comment) has solved results for —
    not one bar per year: cement_kiln/BF_BOF/EAF/NG_DRI/H2_DRI's flows do
    change somewhat year to year, but showing all three years turned this
    into 9 densely-hatched, per-carrier-split mini-bars — user feedback: too
    much visual complexity for what these bars are here to do (show
    new-sector scale against existing-sector scale), not to trace cement/
    steel's own trajectory (fig1b/fig6 already do that). One representative
    snapshot, fuel simplified to a single flat segment (see
    FIG4B_SECTOR_GROUPS' own comment on _consolidate_series/_merge_dri_fuel),
    keeps the comparison legible.
    """
    run = by_label(runs, "Full flexibility")
    r = run.results
    years_available = get_available_years(r)
    solved_years = [y for y in COMPARISON_YEARS if y in years_available]
    solved_year = solved_years[-1]

    if not HEAT_DEMAND_INPUT_JSON.exists():
        print(f"  skipping fig4b_industry_fuel_demand_comparison: {HEAT_DEMAND_INPUT_JSON.relative_to(REPO_ROOT)} "
              "not found — run scripts/extract_heat_demand_by_sector.py under zen-creator-env first")
        return
    import json
    data = json.loads(HEAT_DEMAND_INPUT_JSON.read_text())
    new_sectors = list(HEAT_DEMAND_SECTOR_LABELS)
    for s in new_sectors:
        data[s]["fuel_by_carrier"] = _consolidate_blended_fuel(data[s]["fuel_by_carrier"])
    bands = list(HEAT_DEMAND_BAND_TINTS)

    solved = {}
    for label, techs, post in FIG4B_SECTOR_GROUPS:
        s = _tech_fuel_by_carrier(r, techs, solved_year)
        solved[label] = post(s) if post is not None else s
    solved_fuel_carriers = [c for c in FUEL_CARRIER_HATCHES
                             if any(c in s.index for s in solved.values()) and c != "electricity"]

    new_x = np.arange(len(new_sectors))
    # One bar per sector group now (not one per COMPARISON_YEARS year — see
    # docstring), so group centers are just evenly spaced same as new_x;
    # +1 after new_x still leaves the divider gap.
    solved_x = np.arange(len(FIG4B_SECTOR_GROUPS)) + len(new_sectors) + 1
    fig, ax = plt.subplots(figsize=(14, 7))

    # Left group: identical to fig4a's stacking (heat bands, then fuel-by-
    # carrier, then electricity) — see fig4a_heat_demand_by_sector's docstring.
    heat_vals = {band: np.array([data[s]["heat"][band] for s in new_sectors]) for band in bands}
    fuel_vals = {c: np.array([data[s]["fuel_by_carrier"].get(c, 0.0) for s in new_sectors])
                 for c in FUEL_CARRIER_HATCHES if any(c in data[s]["fuel_by_carrier"] for s in new_sectors)}
    electricity_vals = np.array([data[s]["electricity"] for s in new_sectors])
    bottom = np.zeros(len(new_sectors))
    for band in bands:
        vals = heat_vals[band]
        colors = [_eth_tint(PRODUCTION_COLOR_MAP[f"{s}_production"], HEAT_DEMAND_BAND_TINTS[band]) for s in new_sectors]
        ax.bar(new_x, vals, 0.6, bottom=bottom, color=colors, edgecolor="white", linewidth=0.5)
        bottom += vals
    with plt.rc_context({"hatch.linewidth": 0.5}):
        for carrier, vals in fuel_vals.items():
            ax.bar(new_x, vals, 0.6, bottom=bottom, color=_ETH_GREY, edgecolor="white",
                   linewidth=0.5, hatch=FUEL_CARRIER_HATCHES[carrier])
            bottom += vals
    ax.bar(new_x, electricity_vals, 0.6, bottom=bottom, color=_ELECTRICITY_COLOR, edgecolor="white", linewidth=0.5)
    bottom += electricity_vals
    for xi, total in zip(new_x, bottom):
        ax.text(xi, total, f"{total:.2f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

    # Right group: solved-model fuel/electricity input, ONE bar per sector
    # group (see docstring) at solved_year, same grey-hatched-by-carrier +
    # green-electricity convention as the left group and as fig4a — except
    # the fuel_to_process carrier (cement/steel's consolidated blended fuel,
    # see FIG4B_SECTOR_GROUPS' comment), which stays a flat, unhatched grey.
    bottom = np.zeros(len(solved_x))
    with plt.rc_context({"hatch.linewidth": 0.5}):
        for carrier in solved_fuel_carriers:
            vals = np.array([solved[label].get(carrier, 0.0) for label, _, _ in FIG4B_SECTOR_GROUPS])
            ax.bar(solved_x, vals, 0.6, bottom=bottom, color=_ETH_GREY, edgecolor="white",
                   linewidth=0.5, hatch=FUEL_CARRIER_HATCHES[carrier])
            for xi, bi, vi in zip(solved_x, bottom, vals):
                if vi > 0.5:
                    ax.text(xi, bi + vi / 2, f"{vi:.2f}", ha="center", va="center", fontsize=8,
                            color="black", bbox=_FUEL_LABEL_BBOX)
            bottom += vals
    elec_vals = np.array([solved[label].get("electricity", 0.0) for label, _, _ in FIG4B_SECTOR_GROUPS])
    ax.bar(solved_x, elec_vals, 0.6, bottom=bottom, color=_ELECTRICITY_COLOR, edgecolor="white", linewidth=0.5)
    for xi, bi, vi in zip(solved_x, bottom, elec_vals):
        if vi > 0.5:
            ax.text(xi, bi + vi / 2, f"{vi:.2f}", ha="center", va="center", fontsize=8,
                    color=_text_color_for_bg(_ELECTRICITY_COLOR))
    bottom += elec_vals
    for xi, total in zip(solved_x, bottom):
        ax.text(xi, total, f"{total:.2f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

    divider_x = (new_x[-1] + solved_x.min()) / 2
    ax.axvline(divider_x, color="black", linewidth=0.8)

    ax.set_xticks(np.concatenate([new_x, solved_x]))
    ax.set_xticklabels([HEAT_DEMAND_SECTOR_LABELS[s] + "\n(2023 assumption)" for s in new_sectors]
                       + [label.replace("\n", " ") + f"\n({solved_year} solved)" for label, _, _ in FIG4B_SECTOR_GROUPS],
                       fontsize=9)
    ax.set_ylabel("Heat / fuel / electricity demand [GW]")
    ax.set_title(f"Industry Fuel & Heat Demand: New Sectors vs. Pre-Existing Cement/Steel\n"
                 f"(new sectors: ZEN-creator input assumption, 2023; cement/steel: solved model flow, {solved_year})",
                 fontsize=12, fontweight="bold")

    band_handles = [Patch(facecolor=_eth_tint(_ETH_GREY, HEAT_DEMAND_BAND_TINTS[b]),
                           edgecolor="white", label=f"Heat carrier: {HEAT_DEMAND_BAND_LABELS[b]}") for b in bands]
    all_fuel_carriers = sorted(set(fuel_vals) | set(solved_fuel_carriers), key=list(FUEL_CARRIER_HATCHES).index)
    fuel_handles = [Patch(facecolor=_ETH_GREY, edgecolor="white", linewidth=0.4,
                           hatch=FUEL_CARRIER_LEGEND_HATCHES[c],
                           label=_fuel_legend_label(c)) for c in all_fuel_carriers]
    electricity_handle = [Patch(facecolor=_ELECTRICITY_COLOR, edgecolor="white", label=_ELECTRICITY_LABEL)]
    with plt.rc_context({"hatch.linewidth": 1.3}):
        ax.legend(handles=band_handles + fuel_handles + electricity_handle, fontsize=8, frameon=True,
                  facecolor="white", framealpha=0.9, edgecolor="none", loc="upper left", ncol=2,
                  handlelength=3.0, handleheight=1.8, columnspacing=1.2)
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    savefig(fig, "fig2_industry_fuel_demand_comparison", subdir="method")


# ── 6: Technology-diffusion / capacity-growth mechanisms ───────────────────
# (See fig4b's docstring above for the shared "reconstructed, no original
# script" backstory — this is the other of the 2 figures affected. Numbered
# "99" per user request in the original build, now folded into the main 0-6
# sequence as the final figure; a side investigation into deployment-rate
# feasibility, not one of the Table~SIScenarios comparison figures the rest
# of this module builds.)
#
# Full mechanism inventory (read directly from zen_garden/model/technology/
# technology.py, not just docs — see project memory, diffusion-mechanism
# research): ZEN-garden's ONLY capacity-growth-limiting/enabling mechanisms
# are the ones enumerated below. Each is tagged ACTIVE (has a real, nonzero
# effect somewhere in the Crystal_Ball dataset, verified directly) or
# INACTIVE (implemented in the code, but every relevant parameter is left at
# its zero/off default, or no override file exists, in this dataset):
#
#   ACTIVE   1. Technology diffusion limit (constraint_technology_diffusion_
#               limit_total — the "_total", node-summed variant applies here
#               since knowledge_spillover_rate=inf, confirmed directly).
#               Bounds each period's capacity_addition by 3 additive terms,
#               all reconstructed below:
#                 (a) knowledge/history term: growth compounds off a
#                     knowledge-DEPRECIATED sum of past capacity_addition
#                     (knowledge_depreciation_rate=0.1/yr here), scaled by
#                     tdr = (1+max_diffusion_rate)^interval_between_years - 1
#                 (b) market-share term: market_share_unbounded (=0.02, a
#                     GLOBAL default here) times the summed capacity_previous
#                     of every OTHER technology sharing the same reference
#                     carrier (e.g. every electricity-generating tech for
#                     wind/PV; every carbon-carrier tech - the other 7 CCS
#                     retrofits, DAC, carbon_storage, carbon_pipeline - for
#                     SMR_CCS)
#                 (c) capacity_addition_unbounded floor: a flat per-period
#                     addition allowance regardless of (a)/(b), the ONLY
#                     term that lets a technology grow at all from a
#                     completely zero real-world base (0 for RE techs here;
#                     ~0.0114 GW/node/period for the CCS retrofit family -
#                     see fig5's docstring)
#   ACTIVE   5. Capacity limit / site potential (constraint_technology_
#               capacity_limit): a hard cap on cumulative installed capacity,
#               independent of the diffusion RATE above. Finite (and
#               binding-relevant) for wind/PV; capacity_limit=inf for the CCS
#               retrofit family (no site-potential ceiling at all).
#   INACTIVE 2/3. Learning curve / Wright's law (cumulative-capacity-
#               dependent capex reduction): NOT IMPLEMENTED anywhere in
#               ZEN-garden's source (`grep -rni "learning" zen_garden/`
#               returns zero hits outside tests). Since this mechanism does
#               not exist, "negative learning" (costs that INCREASE with
#               deployment) is not a distinct mechanism either — it would
#               only be a sign flip of a learning-rate parameter that has no
#               implementation to flip. Included here only as an explicit
#               negative result, not silently omitted.
#   INACTIVE 4. Piecewise-linear (PWA) capex (constraint_capex_pwa): a
#               within-period nonlinear capex(capacity_addition) curve
#               (economies/diseconomies of scale for ONE investment) - not a
#               cross-period learning/diffusion mechanism. Implemented, but
#               no nonlinear_capex*.csv override exists anywhere in this
#               dataset, so it is inactive (linear capex throughout).
#   INACTIVE 6. Per-period capacity_addition_min/max bounds
#               (constraint_technology_min/max_capacity_addition):
#               implemented, but every technology here uses the defaults
#               (min=0, max=inf) - no override CSVs found.
#
# DIFFUSION_EXAMPLE_TECHS below picks one tech per REGIME so all 3 active
# diffusion-limit terms are actually visible somewhere: wind_onshore/
# wind_offshore/photovoltaics (real existing capacity + large market-share
# peer group + zero unbounded floor + finite site potential) vs. SMR_CCS
# (near-zero existing capacity + smaller market-share peer group + a real
# unbounded floor + infinite site potential) — see fig5's docstring for why
# SMR_CCS specifically (it captures ~80x more CO2 than BF_BOF_CCS despite
# near-identical diffusion-bound capacity, i.e. a representative, non-trivial
# member of that family).
DIFFUSION_EXAMPLE_TECHS = [
    ("wind_onshore", "Wind onshore", _ETH_BLUE),
    ("wind_offshore", "Wind offshore", _ETH_TURQUOISE),
    ("photovoltaics", "Solar PV", _ETH_GREEN),
    ("SMR_CCS", "SMR (CCS retrofit)", _ETH_RED),
]


def _site_potential(r, tech: str) -> float:
    """Total capacity_limit (site potential, GW) for `tech`, summed across
    nodes; np.inf if unconstrained (e.g. every CCS retrofit tech). Static
    input data - identical across scenarios/years."""
    cl = r.get_total("capacity_limit")
    cl = cl[cl.index.get_level_values("capacity_type") == "power"]
    if tech not in cl.index.get_level_values("technology"):
        return np.inf
    sub = cl.xs(tech, level="technology").droplevel("capacity_type")
    total = float(sub.iloc[:, 0].sum())
    return np.inf if total > 1e11 else total  # ZEN-garden's own "inf" sentinel is a very large finite float


def _series_by_tech(r, component: str, tech: str, cap_type: str = "power") -> pd.Series:
    """get_total(component), filtered to `cap_type`, summed across locations, for one technology."""
    df = r.get_total(component)
    df = df[df.index.get_level_values("capacity_type") == cap_type]
    if tech not in df.index.get_level_values("technology"):
        return pd.Series(dtype=float)
    return df.xs(tech, level="technology").droplevel("capacity_type").sum(axis=0)


def _knowledge_history_term(r, tech: str, years: list[int]) -> pd.Series:
    """Reconstructs term (a) of constraint_technology_diffusion_limit_total:
    tdr(y) * sum_{py<y} vintage_capacity[py] * (1-knowledge_depreciation_rate)^(y-py-dy).

    One documented, IMPERFECT approximation: the true constraint depreciates
    each EXISTING-capacity vintage individually, using its own per-location
    lifetime/lifetime_existing (constraint_technology_diffusion_limit_total's
    separate `capacity_existing * kdr_existing` term) - exact per-vintage,
    per-location bookkeeping this script doesn't carry. Instead, all of the
    technology's pre-model capacity is lumped into a single "vintage" dated
    one period BEFORE the first modeled year (capacity_previous at years[0],
    which already equals total existing capacity there, given a full period
    of undepreciated headroom AT years[0] rather than needing a period to
    "ramp in") and depreciated uniformly from that one date onward, same as
    every later period's own solved capacity_addition.

    Checked directly against the solved model: this closes most, but not
    all, of the gap to the true ceiling - reconstructed
    knowledge+market+floor terms combined still fall visibly short of actual
    capacity_addition in a handful of early periods for wind/PV (largest
    observed shortfall: photovoltaics 2022, ~78 GW), where the real
    per-location lifetime_existing spread (observed directly: -5 to +26
    years within a single wind_onshore vintage bucket) matters most and a
    single lumped, uniformly-depreciated vintage cannot capture it. Read the
    row-2 stacked bars as "reconstructed order-of-magnitude contributions,"
    NOT a guaranteed exact upper bound - the actual capacity-addition line
    occasionally sitting above the stack is this approximation's known
    limitation, not a modeling inconsistency."""
    dy = r.get_system().interval_between_years
    kdr = float(r.get_total("knowledge_depreciation_rate").iloc[0])
    mdr_series = r.get_total("max_diffusion_rate")
    if tech not in mdr_series.index:
        return pd.Series(0.0, index=years)
    mdr = float(mdr_series.loc[tech].iloc[0])
    tdr = (1 + mdr) ** dy - 1

    add_series = _series_by_tech(r, "capacity_addition", tech)
    prev_series = _series_by_tech(r, "capacity_previous", tech)

    y0 = years[0]
    vintages = {y0 - dy: float(prev_series.get(y0, 0.0))}
    for y in years[1:]:
        vintages[y] = float(add_series.get(y, 0.0))

    out = {}
    for y in years:
        total = sum(v * (1 - kdr) ** (y - py - dy) for py, v in vintages.items() if py < y)
        out[y] = tdr * total
    return pd.Series(out)


def _market_share_term(r, tech: str, years: list[int]) -> pd.Series:
    """Reconstructs term (b): market_share_unbounded * sum(capacity_previous
    of every OTHER technology sharing `tech`'s reference carrier), exactly
    (no approximation) - reference-carrier peers come straight from
    Results.get_df("set_reference_carriers"), the same lookup ZEN-garden's
    own postprocessing uses (Results.extract_carrier)."""
    msu = float(r.get_total("market_share_unbounded").iloc[0])
    ref_carriers = r.get_df("set_reference_carriers")
    ref = ref_carriers.get(tech)
    peers = [t for t, c in ref_carriers.items() if c == ref and t != tech]
    total = pd.Series(0.0, index=years)
    for peer in peers:
        s = _series_by_tech(r, "capacity_previous", peer)
        if s.empty:
            continue
        total = total.add(s.reindex(years).fillna(0.0), fill_value=0.0)
    return total * msu


def _unbounded_floor_term(r, tech: str) -> float:
    """Term (c): capacity_addition_unbounded (a per-node rate) times the
    number of nodes where `tech` can be built at all (approximated as the
    number of distinct locations in its own capacity_addition index - the
    technology's full modeled footprint, whether or not it ends up used at
    every one)."""
    cau_series = r.get_total("capacity_addition_unbounded")
    if tech not in cau_series.index:
        return 0.0
    cau = float(cau_series.loc[tech])
    ca = r.get_total("capacity_addition")
    ca = ca[ca.index.get_level_values("capacity_type") == "power"]
    if tech not in ca.index.get_level_values("technology"):
        return cau
    n_nodes = len(ca.xs(tech, level="technology").index.get_level_values("location").unique())
    return cau * n_nodes


def fig6_diffusion_mechanisms(runs: list[Run]) -> None:
    """Row 1: installed capacity vs. site potential (capacity_limit) per
    technology, "No flexibility" scenario, every modeled year - mechanism 5
    above. SMR_CCS has no site-potential bar (capacity_limit=inf).

    Row 2: actual capacity ADDED per period vs. a reconstruction of the
    3-term diffusion-limit ceiling, STACKED so all 3 active terms of
    mechanism 1 are visible at once (knowledge/history, market-share,
    unbounded-addition floor) - see _knowledge_history_term/
    _market_share_term/_unbounded_floor_term for each term's reconstruction.
    This is an approximate reconstruction, not an exact replication of the
    solver's own per-location/per-vintage constraint (see
    _knowledge_history_term's docstring for the one known gap and its
    largest observed size) - read the stacked bars as showing the relative
    SHAPE and ORDER OF MAGNITUDE of each mechanism's contribution, not a
    literal, always-binding ceiling; the black line occasionally poking
    above the stack in early periods is that approximation's known
    limitation, not a sign the underlying model is inconsistent.
    wind_onshore/offshore/PV show the "large existing base + market-share
    headroom" regime (floor term ~0, invisible); SMR_CCS shows the opposite
    "cold-start" regime (knowledge/market terms start near 0, floor term is
    what lets it grow at all) - the same mechanism that inflates ALL 8 CCS
    retrofit techs' capacity roughly equally, per fig5's docstring.

    The 2 confirmed-INACTIVE cost/growth mechanisms (learning curve / "
    negative learning", PWA nonlinear capex) and the 1 confirmed-inactive
    per-period bound (capacity_addition_min/max) are deliberately not given
    plot space - see the module-level comment above this function for why,
    and to keep this an explicit, checked negative result rather than a
    silent omission.

    "No flexibility" is used (matching the original figure) since these are
    exogenous/structural mechanisms, not meaningfully scenario-dependent for
    the industry-heat-flexibility axis this SI section otherwise studies.
    """
    run = by_label(runs, "No flexibility")
    r = run.results
    years = get_available_years(r)

    fig, axes = plt.subplots(2, 4, figsize=(19, 9))
    for col, (tech, label, color) in enumerate(DIFFUSION_EXAMPLE_TECHS):
        potential = _site_potential(r, tech)
        installed = _series_by_tech(r, "capacity", tech).reindex(years).fillna(0.0)
        addition = _series_by_tech(r, "capacity_addition", tech).reindex(years).fillna(0.0)

        ax1 = axes[0, col]
        ax1.bar(years, installed, width=1.6, color=color, label="Installed capacity" if col == 0 else None)
        if np.isfinite(potential):
            ax1.bar(years, potential - installed, width=1.6, bottom=installed,
                    color=_eth_tint(color, 0.75), label="Unused site potential" if col == 0 else None)
            ax1.axhline(potential, color=color, linestyle="--", linewidth=1.2)
            pct_used = installed.iloc[-1] / potential * 100 if potential > 0 else 0.0
            ax1.text(0.97, 0.55, f"{pct_used:.0f}% of potential\nused by {years[-1]}",
                     transform=ax1.transAxes, ha="right", va="top", fontsize=8.5, color=color)
            ax1.set_title(f"{label}\n(site potential: {potential:,.0f} GW)", fontsize=10)
        else:
            ax1.set_title(f"{label}\n(capacity_limit = inf: no site-potential cap)", fontsize=10)
        if col == 0:
            ax1.set_ylabel("Installed capacity [GW]")
            ax1.legend(fontsize=8, frameon=True, facecolor="white", framealpha=0.9,
                       edgecolor="none", loc="upper left")

        ax2 = axes[1, col]
        knowledge = _knowledge_history_term(r, tech, years)
        market = _market_share_term(r, tech, years)
        floor = np.full(len(years), _unbounded_floor_term(r, tech))
        bottom = np.zeros(len(years))
        for vals, comp_label, comp_color in [
            (knowledge.to_numpy(), "Knowledge/history term", _eth_tint(color, 0.05)),
            (market.reindex(years).fillna(0.0).to_numpy(), "Market-share term", _eth_tint(color, 0.4)),
            (floor, "Unbounded-addition floor", _eth_tint(color, 0.72)),
        ]:
            ax2.bar(years, vals, width=1.6, bottom=bottom, color=comp_color,
                    edgecolor="white", linewidth=0.4, label=comp_label if col == 0 else None)
            bottom += vals
        ax2.plot(years, addition.to_numpy(), color="black", marker="o", markersize=3.5,
                 linewidth=1.2, label="Actual capacity addition" if col == 0 else None)
        if col == 0:
            ax2.set_ylabel("Capacity added per period [GW]")
            ax2.legend(fontsize=7, frameon=True, facecolor="white", framealpha=0.9,
                       edgecolor="none", loc="upper left")
        ax2.set_xlabel("Year")
        ax2.grid(axis="y", alpha=0.25)

    fig.suptitle("Technology-Diffusion / Capacity-Growth Mechanisms\n"
                 f"No flexibility, {years[0]}-{years[-1]} (Crystal Ball ind heat v8 0) - row 2 stacks show "
                 "all 3 active diffusion-limit terms", fontsize=12.5)
    fig.text(0.5, 0.005,
             "Row 2 stacks are an approximate reconstruction of the solver's own constraint (order of "
             "magnitude, not an exact/always-binding ceiling) - see _knowledge_history_term's docstring.",
             ha="center", va="bottom", fontsize=8, style="italic", color="#555555")
    fig.tight_layout(rect=[0, 0.02, 1, 0.93])
    savefig(fig, "fig8_diffusion_mechanisms")


# ── 0b: Emissions-source comparison, Full flexibility vs Crystal Ball base ──

# Print-figure-specific ETH palette (does NOT touch the shared, dashboard-wide
# COLOR_MAP in figure_settings.py — see plot_stacked_bars(color_map=...)),
# built from the same 7 ETH Zurich corporate-design colors used everywhere
# else in these SI figures (SCENARIO_PALETTE, COST_COMPONENT_COLORS,
# HEAT_SUPPLY_COLOR_MAP/PRODUCTION_COLOR_MAP above) rather than the generic,
# off-brand hues COLOR_MAP happens to hold for some of these same categories
# (e.g. a plain purple for glass_production). glass_production keeps ETH
# blue here — NOT the same as its current PRODUCTION_COLOR_MAP entry (grey,
# since fig4a/fig4b's electricity segment moved to blue) — blue is otherwise
# unused among this map's carriers, and fig0b never plots electricity, so no
# in-chart clash results from the two figures disagreeing on glass's color.
# Carriers (the larger, primary stacked segments) each get one solid base
# hue; technologies (smaller, secondary segments) get a lighter tint of a
# related hue via _eth_tint (defined above, fig1b's section) — the tint
# makes "technology" read as visually distinct from "carrier" at a glance.
# The " (carrier)"/" (tech)" suffix below only disambiguates dict keys/legend
# lookup internally — fig0b strips it from the displayed legend text (per
# user request, it was legend clutter given the tint already carries the
# same distinction visually).
EMISSIONS_COLOR_MAP = {
    # Carriers (fuel combustion)
    "crude oil (carrier)": _ETH_BRONZE,
    "natural gas (carrier)": _ETH_TURQUOISE,
    "lng (carrier)": _ETH_GREEN,
    "hard coal (carrier)": _ETH_GREY,
    "lignite (carrier)": _ETH_RED,
    "waste (carrier)": _ETH_PURPLE,
    # Technologies (process + carbon capture)
    "glass production (tech)": _ETH_BLUE,
    "cement kiln (tech)": _eth_tint(_ETH_BRONZE, 0.45),
    "BF BOF (tech)": _eth_tint(_ETH_GREY, 0.35),
    "EAF (tech)": _eth_tint(_ETH_BLUE, 0.45),
    "NG DRI (tech)": _eth_tint(_ETH_TURQUOISE, 0.45),
    "carbon storage (tech)": _eth_tint(_ETH_GREEN, 0.45),
}


def fig0b_emissions_source_comparison(base_run: Run, no_flex_run: Run, full_run: Run) -> None:
    """Panel A explains the emissions increase for "Full flexibility" vs
    "Crystal Ball (base)" being much larger (proportionally) than the cost
    increase (fig0a): decomposes each run's year-2025 emissions into carrier
    (fuel combustion) and technology (process + carbon capture) components.
    Panel B then shows WHY the system can't just decarbonize its way out of
    that gap: each run's true cumulative emissions vs. its own carbon budget,
    2025-2070.

    Both panels compare all 3 scenarios (base / no flexibility / full
    flexibility, per user request) rather than just base vs. full flex.
    Panel A's stacked-bar segments stay colored by carrier/technology
    CATEGORY (EMISSIONS_COLOR_MAP) — that's the actual content being
    compared — while Panel B's per-run identity (line + budget dashline)
    uses the requested grey/dark-blue/magenta ETH triad
    (_ETH_GREY/_ETH_BLUE/_ETH_PURPLE) instead of each run's globally
    assigned SCENARIO_PALETTE slot, since "Full flexibility"'s global slot
    is petrol/turquoise elsewhere (fig10/fig11 etc. never key off
    run.color, so this local override has no cross-figure effect).

    Panel A originally used a single year (the earliest one present in both
    runs) — per user request it now shows COMPARISON_YEARS (2030/2040/2050)
    for each run side by side instead, so the composition's evolution over
    the horizon is visible directly rather than a single cross-section. The
    original single-year rationale (kept below for context on why year
    choice matters here at all) still explains why an early, WRI-comparable
    year anchors this panel rather than a horizon-total sum:

    Originally, Panel A used year 2025 (the earliest year present in both
    runs), not a horizon-total sum: WRI's own sector-share figures
    (https://www.wri.org/insights/4-charts-explain-greenhouse-gas-emissions-
    countries-and-sectors) are a single year (2023), so a single-year cut is
    the apples-to-apples comparison, not a multi-year sum. It also sidesteps
    a separate distortion — carbon_storage (CCS) captures ~45-50% of GROSS
    emissions by full-horizon totals in both runs, so a horizon-total NET
    percentage (the original ~21% headline figure) is a % change in the
    small residual of two much larger, near-offsetting numbers and comes out
    mechanically inflated vs. a % change in gross emissions. In 2025, CCS has
    barely ramped up (~-15 Mton out of ~2,269 Mton gross, ~0.7%), so gross
    and net nearly coincide here anyway (~+12.1% vs ~+12.2%) — this single
    year is simultaneously the fair comparison on the WRI single-year
    dimension AND avoids needing the gross/net distinction at all.

    Root cause of the gap itself: "Crystal Ball (base)" has NO industry-heat
    or production sector demand at all — no glass/ceramic/paper/food, no
    heat_industry_0_100/100_150/150_200 (confirmed via `results.get_total
    ("demand")`: these carriers are entirely absent from the base run's
    index, not just zero). The "Full flexibility" extension therefore adds
    genuinely new final energy-service demand, not a re-representation of
    demand the base model already met some other way. Meeting that new
    demand pulls in more fossil-carrier combustion (natural_gas/lng/
    hard_coal/crude_oil/waste — mostly industry boilers) plus a small amount
    of new direct process emissions (glass_production). Because that extra
    boiler CAPEX/OPEX is cheap relative to total system cost (see fig0a's
    docstring), this emissions increase shows up as only a modest cost
    increase — the two are not expected to move in the same proportion, and
    the size of the gap here is a real modeling consequence of extending
    scope, not an error.

    Crystal Ball's scope (README.md: EU27+NO+CH+UK-MT-CY, electricity/heat/
    transport/steel/cement/ammonia/methanol/olefins) maps onto WRI's
    "Energy" (76.7%) + "Industrial processes" (6.2%) categories but excludes
    agriculture (12.3%) and land use (0.9%) — so the ~12% figure here is
    plausible next to WRI's ~18.4% global industry share, especially since
    steel/cement/chemicals (already in the base model, and typically the
    dominant slice of that 18.4%) leave a smaller remainder for the
    genuinely new glass/ceramic/paper/food demand modeled here.

    Panel B plots each run's true, interval-weighted cumulative emissions
    (`carbon_emissions_cumulative`, ZEN-garden's own recursive
    E_y^cum = E_{y-1}^cum + (dy-1)*E_{y-1} + E_y, dy=5 here) against each
    run's own `carbon_emissions_budget` cap. This is NOT the same number as
    Panel A's or the naive per-year sum used in compute_headline_metrics:
    that naive sum badly understates true cumulative emissions because it
    never credits the (dy-1)=4 "skipped" years between representative model
    years.

    As of the 2026-07-29 re-sync, ALL scenarios (base included) were re-run
    with a shortened horizon (`optimized_years=6`, i.e. 2025-2050, down from
    the previous 2025-2070 / optimized_years=10). This changes Panel B's
    story: BOTH runs' true cumulative emissions are still transiently above
    their own budget line at the final modeled year (2050) — base is not
    exempt anymore. Under the old 2025-2070 horizon, base fully repaid its
    budget by 2070 (cumulative == budget to 6 sig figs) via a late-horizon
    swing to net-negative annual emissions (heavy CCS/DAC ramping up from
    ~2055 on) that this shorter horizon simply doesn't reach yet: at 2050
    both runs' `carbon_emissions_annual` are still positive (base +72.5,
    full +119.3 Mton), i.e. neither has started its late-horizon repayment
    swing. So the "front-load now, repay later" pattern from the 2070-run is
    still the underlying mechanism, but the repayment leg now falls outside
    the modeled window — both overshoots shown here are a horizon-truncation
    artifact of stopping at 2050, not evidence that base has stopped fully
    decarbonizing. `constraint_carbon_emissions_budget`'s overshoot variable
    is only priced in the FINAL horizon year (`constraint_cost_carbon_
    emissions_total`'s `mask_last_year`) — with 2050 now being that final
    year for every scenario, both runs incur a real (if small, since
    `price_carbon_emissions_budget_overshoot`=5,000 EUR/ton is finite, a SOFT
    constraint) carbon cost at 2050 that a 2070-horizon run would not have
    shown for base. Verified directly: base overshoot 2,525.7 Mton -> carbon
    cost 12.99M EUR; full overshoot 3,889.7 Mton -> carbon cost 20.05M EUR
    (`cost_carbon_emissions_total[2050]`, matches
    `budget_overshoot*5,000 + annual_overshoot*5,000` exactly, the latter
    from the separate `carbon_emissions_annual_limit=0` constraint at 2050
    only, identical in both runs).

    Full's overshoot is still larger than base's in both absolute (+1,364.0
    Mton) and relative terms, consistent with the pre-existing finding that
    the new industry sectors' real cumulative footprint outgrows the
    ZEN-creator-credited budget top-up (see project memory, traced to
    Mannhardt (2026)'s deployment-barrier mechanism: the new sectors' clean
    heat-supply alternative starts from zero real-world existing capacity,
    while their fossil alternative does not) — that mechanism is unaffected
    by the horizon change and still holds. What's new is only that base
    itself is no longer a clean/zero-cost reference point at this horizon;
    any reading of this figure should treat both overshoot numbers as
    "not yet repaid by 2050", not "failed to decarbonize".
    """
    fr, nfr, br = full_run.results, no_flex_run.results, base_run.results
    years_common = sorted(set(get_available_years(fr)) & set(get_available_years(nfr))
                           & set(get_available_years(br)))
    panel_a_years = [y for y in COMPARISON_YEARS if y in years_common]

    # cmr10 (this module's serif font, see the plt.rcParams block up top) has
    # no underscore glyph, so raw "_"-joined category names render as a
    # garbled substitute character — display labels use spaces instead.
    def disp(name: str) -> str:
        return name.replace("_", " ")

    # Panel A: full emissions composition per run PER YEAR (carrier +
    # technology stacked together, suffix-disambiguated) so each bar's
    # height reproduces that run's true net total for that year — grouped
    # model-major/year-minor ("base 2030/2040/2050, no-flex 2030/2040/2050,
    # full 2030/2040/2050"), same convention as fig1b/fig4b.
    composition_series = []
    for run, results in [(base_run, br), (no_flex_run, nfr), (full_run, fr)]:
        for year in panel_a_years:
            carrier = get_emissions_by_carrier(results, year)
            # H2_DRI is dropped: its emissions are ~0 in every run/year here
            # (no delta to show), so it only adds clutter to the legend.
            tech = get_emissions_by_technology(results, year).drop("H2_DRI", errors="ignore")
            key = f"{run.label}__{year}"
            composition_series.append((key, pd.concat([carrier.rename(lambda c: f"{disp(c)} (carrier)"),
                                                         tech.rename(lambda t: f"{disp(t)} (tech)")])))
    composition = build_comparison_df(composition_series)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), gridspec_kw={"width_ratios": [1.4, 1.3]})
    # bar_width=0.85 (vs. the shared 0.6 default) packs the now-9 bars (was
    # 6, before the 3rd scenario was added) closer together per user request.
    plot_stacked_bars(composition, "Emissions Composition by Source",
                      "Mton CO$_2$eq", ax1, show_segment_labels=False,
                      color_map=EMISSIONS_COLOR_MAP, bar_width=0.85)
    # Strip the " (carrier)"/" (tech)" disambiguation suffix from the legend
    # text only — EMISSIONS_COLOR_MAP's keys (and the color/tint they drive)
    # still need it, but the tint already distinguishes carrier vs. tech
    # visually, so the suffix is legend clutter per user request.
    legend = ax1.get_legend()
    if legend is not None:
        for text in legend.get_texts():
            text.set_text(text.get_text().replace(" (carrier)", "").replace(" (tech)", ""))
    _year_group_labels(ax1, 3, [base_run.label, no_flex_run.label, full_run.label], panel_a_years)

    # Panel B: cumulative emissions vs. each run's own carbon budget, 2025-2070.
    def _series(r, name):
        s = r.get_total(name)
        return {int(k): float(v) for k, v in s.items()}

    cum_full = _series(fr, "carbon_emissions_cumulative")
    cum_no_flex = _series(nfr, "carbon_emissions_cumulative")
    cum_base = _series(br, "carbon_emissions_cumulative")
    budget_full = float(fr.get_total("carbon_emissions_budget").iloc[0])
    budget_no_flex = float(nfr.get_total("carbon_emissions_budget").iloc[0])
    budget_base = float(br.get_total("carbon_emissions_budget").iloc[0])
    years = sorted(cum_full)
    base_vals = [cum_base[y] for y in years]
    no_flex_vals = [cum_no_flex[y] for y in years]
    full_vals = [cum_full[y] for y in years]

    # Per-run identity color for this panel only — the requested
    # grey/dark-blue/magenta ETH triad, NOT each run's globally assigned
    # SCENARIO_PALETTE slot (see docstring).
    panel_b_color = {base_run.label: _ETH_GREY, no_flex_run.label: _ETH_BLUE,
                      full_run.label: _ETH_PURPLE}

    # Transient mid-horizon excess above each run's OWN budget line — real,
    # but costs nothing except at the final year (see docstring). Shown
    # muted/shared so it doesn't read as "this is the penalised amount".
    for label, vals, budget, legend_label in [
        (base_run.label, base_vals, budget_base, "excess above own budget, not yet repaid"),
        (no_flex_run.label, no_flex_vals, budget_no_flex, "_nolegend_"),
        (full_run.label, full_vals, budget_full, "_nolegend_"),
    ]:
        over = np.array([v > budget for v in vals])
        ax2.fill_between(years, vals, budget, where=over, color=panel_b_color[label],
                          alpha=0.12, interpolate=True, label=legend_label)

    # "No flexibility" and "Full flexibility" turn out to have nearly
    # identical cumulative-emissions trajectories AND budgets (same industry
    # sectors/demand scope, only the flexibility options differ — base gets
    # a different budget because it lacks those sectors entirely). Solid,
    # same-width lines would make one fully occlude the other, so each run
    # also gets its own marker/linestyle (not just color) and "No
    # flexibility" is drawn last/on top with a dashed line so the overlap
    # itself stays visible instead of erasing one run.
    line_style = {base_run.label: dict(marker="o", linestyle="-"),
                  full_run.label: dict(marker="^", linestyle="-"),
                  no_flex_run.label: dict(marker="s", linestyle="--", markersize=5)}
    budget_style = {base_run.label: "--", full_run.label: "--", no_flex_run.label: ":"}
    for label, vals, budget in [
        (base_run.label, base_vals, budget_base),
        (full_run.label, full_vals, budget_full),
        (no_flex_run.label, no_flex_vals, budget_no_flex),
    ]:
        color = panel_b_color[label]
        ax2.plot(years, vals, color=color, linewidth=2,
                  label=f"{label} - cumulative emissions", **line_style[label])
        ax2.axhline(budget, color=color, linestyle=budget_style[label], linewidth=1.5,
                    label=f"{label} - carbon budget ({budget:,.0f} Mton)")

    # Budget delta: the two runs are handed DIFFERENT total carbon budgets
    # (carbon_emissions_budget) by ZEN-creator to begin with — a distinct
    # number from Panel A's net-emissions comparison (a single year's actual
    # combustion/process emissions), this is the two dashed BUDGET lines'
    # own gap, i.e. how much more headroom "Full flexibility" was allotted
    # over the run's full horizon before even solving. Placed near the left
    # edge (early years), where the rising cumulative-emissions lines are
    # still well clear of both dashed budget lines.
    delta_budget = budget_full - budget_base
    sign = "+" if delta_budget >= 0 else ""
    bracket_x = years[0] + 0.03 * (years[-1] - years[0])  # far left, where both cumulative-emissions lines are still near 0
    ax2.annotate("", xy=(bracket_x, budget_full), xytext=(bracket_x, budget_base),
                 arrowprops=dict(arrowstyle="<->", color="black", linewidth=1.0))
    ax2.text(bracket_x + 0.015 * (years[-1] - years[0]), (budget_full + budget_base) / 2,
             f"$\\Delta$ budget = {sign}{delta_budget:,.0f} Mton",
             ha="left", va="center", fontsize=8.5, fontweight="bold")

    ax2.set_xlabel("Year")
    ax2.set_ylabel("Cumulative carbon emissions [Mton CO$_2$eq]")
    ax2.set_title("Cumulative Emissions vs. Carbon Budget", fontsize=11, fontweight="bold")
    ax2.set_ylim(top=max(base_vals + no_flex_vals + full_vals) * 1.1)
    ax2.legend(fontsize=7.5, loc="upper left")
    ax2.grid(alpha=0.3)

    fig.suptitle("Emission Increase Attributable to the Newly Implemented Industry Sectors",
                 fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    savefig(fig, "fig2_emissions_source_comparison")


def _grey_delta_bar(ax, labels: list[str], values: dict[str, float], base_label: str,
                     delta_color: dict[str, float], value_fmt: str = "{:,.0f}",
                     top: float | None = None, bottom: float | None = None,
                     delta_fmt: str | None = None) -> None:
    """One bar per label: the shared baseline value (base_label's own total)
    in grey, and each other bar's difference from that baseline stacked on
    top (or hanging below, hatched, if negative) in that run's own color —
    so only the DELTA reads as "the interesting part" and the (usually much
    larger, near-identical-across-scenarios) baseline stays visually
    de-emphasized. Pairs with the y-axis truncation + break marks the caller
    adds, since the baseline otherwise dwarfs the delta (see fig0a's
    docstring: deltas here are a few % of the baseline total).

    `bottom`/`top` override the automatic y-limits — needed when the deltas
    are a fraction of a percent (fig14b) rather than fig1b's several
    percent, where the automatic 0.9x truncation still leaves the delta a
    sliver. `delta_fmt` defaults to `value_fmt` and only differs where the
    delta needs finer precision than the (much larger) totals do."""
    # Both limits are needed BEFORE the bars are drawn, since a delta too
    # thin to hold its own inline label gets that label placed outside the
    # bar instead — see below.
    if bottom is None:
        # Truncate the y-axis just below the smallest bar value (rather than
        # starting at 0) so the small delta isn't visually swamped by the much
        # larger shared baseline, and mark the truncation with the standard
        # diagonal "break" convention so it isn't mistaken for a from-zero axis.
        bottom = min(values.values()) * 0.9
    if top is None:
        top = max(values.values()) * 1.12
    span = top - bottom
    delta_fmt = delta_fmt or value_fmt

    base_val = values[base_label]
    x = np.arange(len(labels))
    for xi, label in zip(x, labels):
        val = values[label]
        delta = val - base_val
        grey_height = min(val, base_val)
        ax.bar(xi, grey_height, width=0.6, color=_ETH_GREY, edgecolor="white", zorder=2)
        if delta != 0:
            ax.bar(xi, abs(delta), width=0.6, bottom=grey_height, color=delta_color[label],
                   edgecolor="white", zorder=2, hatch="//" if delta < 0 else None)
        ax.text(xi, val, value_fmt.format(val), ha="center",
                 va="bottom" if delta >= 0 else "top", fontsize=8.5, fontweight="bold")
        if label != base_label:
            sign = "+" if delta >= 0 else ""
            pct = delta / base_val * 100
            text = f"{sign}{delta_fmt.format(delta)} ({sign}{pct:.2f}%)"
            if abs(delta) / span >= 0.04:
                ax.text(xi, grey_height + abs(delta) / 2, text, ha="center", va="center",
                         fontsize=7.5, color="white", fontweight="bold")
            else:
                # Segment too thin for a legible label inside it: stack the
                # delta above (below, for a negative one) the bar's own value
                # label instead, in the delta's color so it still reads as
                # belonging to the colored segment rather than to the total.
                ax.annotate(text, xy=(xi, val), xytext=(0, 12 if delta >= 0 else -12),
                             textcoords="offset points", ha="center",
                             va="bottom" if delta >= 0 else "top",
                             fontsize=7.5, color=delta_color[label], fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.5)

    ax.set_ylim(bottom, top)
    d = 0.012
    kwargs = dict(transform=ax.transAxes, color="black", clip_on=False, linewidth=1)
    for xoff in (0, 1):
        ax.plot((xoff - d, xoff + d), (-d, +d), **kwargs)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="x", length=0)


def fig1b_cost_and_emissions_totals(base_run: Run, no_flex_run: Run, full_run: Run) -> None:
    """Companion to fig0a/fig0b, requested as a single at-a-glance pair: for
    all 3 scenarios (base / no flexibility / full flexibility), show the
    TOTAL (not just the delta) discounted system cost (left) and TOTAL true
    cumulative emissions (right) — but with "Crystal Ball (base)"'s own
    value rendered as the shared grey base of every bar, and only each other
    scenario's difference from that base value drawn in color, so the
    figure reads as fig0a/fig0b's deltas without hiding how small they are
    relative to the totals they sit on top of.

    Cost uses the same horizon-total discounted `get_annual_total_cost` as
    compute_headline_metrics's npc_total_meur. Emissions deliberately do
    NOT use compute_headline_metrics's emissions_total_mton — that's a naive
    per-year sum which badly understates true cumulative emissions (see
    fig0b's docstring) — instead using the same
    `carbon_emissions_cumulative` value (at the final modeled year) that
    fig0b's Panel B plots, for consistency with that figure's numbers.
    """
    delta_color = {base_run.label: _ETH_GREY, no_flex_run.label: _ETH_BLUE,
                   full_run.label: _ETH_PURPLE}
    # Capped at 26,000 on both panels (vs. the auto ~1.12x headroom, which
    # reached ~27,000 / ~27,500) per user request — still enough headroom
    # above the ~24,400 max bar for its value label.
    _cost_and_emissions_totals([base_run, no_flex_run, full_run], base_run, delta_color,
                               "fig1b_cost_emissions_totals", top=26000)


def fig14b_cost_and_emissions_totals_full_vs_single(full_run: Run, single_temp_run: Run) -> None:
    """Exactly fig1b's template with the scenario PAIR swapped, per user
    request: Full flexibility's own totals as the shared grey base of both
    bars, Single temperature level drawn as its difference from them. Only
    2 bars per panel instead of fig1b's 3.

    These two runs differ far less than fig1b's do (+83 bn EUR = +0.34% on
    cost; emissions IDENTICAL to the last digit, both runs spending exactly
    the same binding cumulative carbon budget — the temperature-band
    resolution changes HOW the budget is met, not how much of it is used),
    so the y-limits are pinned tight around the bars (24,300-24,650)
    instead of fig1b's automatic 0.9x truncation, which at this delta size
    would leave the cost delta a 1-pixel sliver. `delta_fmt` keeps 1 decimal
    on the delta labels for the same reason.
    -> SI_results/fig14b_cost_emissions_totals_full_vs_single_temp.svg
    """
    delta_color = {full_run.label: _ETH_GREY, single_temp_run.label: _ETH_PURPLE}
    _cost_and_emissions_totals([full_run, single_temp_run], full_run, delta_color,
                               "fig14b_cost_emissions_totals_full_vs_single_temp",
                               bottom=24300, top=24650, delta_fmt="{:,.1f}")


def _cost_and_emissions_totals(runs: list[Run], base_run: Run, delta_color: dict[str, str],
                                fig_name: str, top: float | None = None,
                                bottom: float | None = None,
                                delta_fmt: str | None = None) -> None:
    """Shared body of fig1b/fig14b — `base_run` supplies the grey shared
    baseline every bar is drawn on top of, `runs` (which must include it)
    the bars themselves, in order. `top`/`bottom`/`delta_fmt` pass straight
    through to _grey_delta_bar (same limits on both panels)."""
    base_label = base_run.label

    # bn EUR (billion EUR) rather than MEUR per user request — MEUR values
    # here run ~2.3e7 (i.e. ~23 trillion EUR); dividing by 1000 gives a
    # legible ~23,000 bn EUR without scientific-notation axis ticks.
    cost = {}
    for r in runs:
        years = get_available_years(r.results)
        cost[r.label] = float(get_annual_total_cost(r.results, years, discount=True).sum()) / 1000

    def _series(r, name):
        s = r.get_total(name)
        return {int(k): float(v) for k, v in s.items()}

    emissions = {}
    for r in runs:
        cum = _series(r.results, "carbon_emissions_cumulative")
        emissions[r.label] = cum[max(cum)]

    labels = [r.label for r in runs]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))
    _grey_delta_bar(ax1, labels, cost, base_label, delta_color, value_fmt="{:,.0f}",
                    top=top, bottom=bottom, delta_fmt=delta_fmt)
    ax1.set_ylabel("Discounted total system cost [bn EUR]")
    ax1.set_title("Total System Cost", fontsize=12, fontweight="bold")

    _grey_delta_bar(ax2, labels, emissions, base_label, delta_color, value_fmt="{:,.0f}",
                    top=top, bottom=bottom, delta_fmt=delta_fmt)
    ax2.set_ylabel("Cumulative carbon emissions [Mton CO$_2$eq]")
    ax2.set_title("Total Cumulative Emissions", fontsize=12, fontweight="bold")

    fig.tight_layout()
    savefig(fig, fig_name)


# ── 8/9: Real-world industry-emissions context (input data, no model results) ──
# Neither figure below depends on a solved ZEN-garden run: both plot exogenous,
# real-world emissions data (JRC-IDEES-2023 / UNFCCC CRF, reached via
# ZEN-creator's input_data) that motivate/contextualize Crystal Ball's
# sectoral scope, per user request — generated unconditionally in main().

INDUSTRY_SECTOR_EMISSIONS_JSON = FIGURES_DIR / "industry_sector_emissions_input.json"
# Sibling-repo convention (see plot_carrier_flows.py's ZEN_CREATOR_OUTPUTS):
# a plain CSV, so no openpyxl/env-split bridge is needed unlike fig8's JSON.
MODEL_SCOPE_CSV = REPO_ROOT.parent / "ZEN-creator" / "input_data" / "Emissionbudget" / "sector_emissions_2022.csv"

_SCOPE_COLOR = {"old": _ETH_BLUE, "new": _ETH_GREEN, None: _ETH_GREY}
_SCOPE_LABEL = {"old": "Existing Crystal Ball sectors (Mannhardt, 2026)",
                "new": "Industry-heat extension (this work)",
                None: "Not modeled by Crystal Ball"}


def fig8_industry_sector_emissions_context() -> None:
    """European industrial CO2 emissions by subsector (JRC-IDEES-2023, EU27,
    2022) — pure real-world input-data context, no solved model results.
    Answers "how big are the industry sectors Crystal Ball (and its
    industry-heat extension) model, relative to the rest of European
    industry": each bar is colored/stacked by whether that slice is inside
    Mannhardt's original 11-sector scope (blue), the four new industry-heat
    sectors added here (turquoise), or not modeled at all (grey). Three
    subsectors are split into their JRC-IDEES second-level components so this
    line can be drawn correctly INSIDE a bar rather than per whole subsector:
    "Non-metallic minerals" -> cement (old) + glass/ceramics (new); "Paper,
    pulp & printing" -> paper (new) + pulp/printing (not modeled). See
    extract_industry_sector_emissions.py for the extraction and the full
    scope-mapping rationale.

    CAVEAT: these are JRC-IDEES's energy-related (fuel combustion) emissions
    only — the IPCC 1.A methodology JRC-IDEES itself uses — and do NOT
    include IPCC 2.x process emissions (cement calcination, steel ore
    reduction, glass/ceramic carbonate decomposition). Steel and non-metallic
    minerals both have a substantial process-emissions component not counted
    here, so their bars understate those two sectors' full footprint
    relative to sector_emissions_2022.csv (fig9's source), which DOES fold
    UNFCCC process-emission CRF categories in on top of combustion for the
    specific sectors Crystal Ball models. Not comparable 1:1 with fig9's Mt
    figures for that reason — this figure's job is relative subsector SCALE
    across ALL of European industry, fig9's is the model's total coverage
    SHARE of all-sector European emissions.
    """
    if not INDUSTRY_SECTOR_EMISSIONS_JSON.exists():
        print(f"  skipping fig8_industry_sector_emissions_context: "
              f"{INDUSTRY_SECTOR_EMISSIONS_JSON.relative_to(REPO_ROOT)} not found — "
              "run scripts/extract_industry_sector_emissions.py under zen-creator-env first")
        return
    import json
    data = json.loads(INDUSTRY_SECTOR_EMISSIONS_JSON.read_text())
    sectors = data["sectors"]

    # Each sector -> list of (scope, Mt) segments, ordered old/new/unmodeled
    # for consistent bottom-to-top stacking.
    _scope_order = {"old": 0, "new": 1, None: 2}
    rows = []
    for s in sectors:
        if "subsplit" in s:
            segs = [(sub["scope"], sub["emissions_kt_co2"] / 1000) for sub in s["subsplit"]]
        else:
            segs = [(s["scope"], s["emissions_kt_co2"] / 1000)]
        segs.sort(key=lambda seg: _scope_order[seg[0]])
        rows.append((s["label"], sum(v for _, v in segs), segs))
    rows.sort(key=lambda r: -r[1])

    fig, ax = plt.subplots(figsize=(12, 6.5))
    x = np.arange(len(rows))
    label_offset = 0.015 * max(r[1] for r in rows)
    for xi, (label, total, segs) in zip(x, rows):
        bottom = 0.0
        for scope, val in segs:
            ax.bar(xi, val, 0.65, bottom=bottom, color=_SCOPE_COLOR[scope],
                   edgecolor="white", linewidth=0.5)
            bottom += val
        ax.text(xi, bottom + label_offset, f"{total:.0f}", ha="center", va="bottom", fontsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels([r[0] for r in rows], rotation=35, ha="right", fontsize=9)
    ax.set_ylabel("Energy-related CO$_2$ emissions [Mt CO$_2$/yr]")
    ax.set_title(f"European Industrial CO$_2$ Emissions by Subsector (EU27, {data['year']})",
                 fontsize=12, fontweight="bold")
    handles = [Patch(facecolor=_SCOPE_COLOR[k], label=_SCOPE_LABEL[k]) for k in ("old", "new", None)]
    ax.legend(handles=handles, fontsize=8.5, frameon=False, loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(top=ax.get_ylim()[1] * 1.08)
    fig.text(0.01, 0.01, f"Source: {data['source']}", fontsize=7, color="grey")
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    savefig(fig, "fig3_industry_sector_emissions_context", subdir="method")


# Mannhardt (2026) Appendix A.2: her carbon budget is calibrated to the
# ~90.0% share of the 28 countries' 2021 direct CO2 emissions attributable to
# her 11 modeled sectors (see ASSUMPTIONS.md, "Carbon emissions budget") —
# the only documented anchor for "what % of total European CO2 does Crystal
# Ball's ORIGINAL scope cover". Not independently re-derived here (no local
# total-emissions dataset spanning all sectors/countries at once) — treated
# as a citation, not a computed figure, hence its own named constant here
# rather than a CSV field.
MANNHARDT_OLD_SECTORS_SHARE_OF_TOTAL = 0.900


def fig9_model_scope_coverage() -> None:
    """How much of total European (28-country: EU27+CH+NO-MT-CY) direct CO2
    emissions Crystal Ball's modeled sectors cover, and how much of that
    coverage the industry-heat extension (this work) adds on top of
    Mannhardt (2026)'s original 11-sector scope.

    Two numbers come from different places:
      - Mannhardt's 11 sectors = ~90.0% of the 28-country total (her own
        reported figure, 2021 basis, ASSUMPTIONS.md "Carbon emissions
        budget" / dissertation Appendix A.2) — MANNHARDT_OLD_SECTORS_SHARE_
        OF_TOTAL above.
      - The 4 new industry-heat sectors' emissions relative to those same 11
        sectors (E_new/E_old, 2022 UNFCCC CRF data, Variant B "naive
        full-add" — the variant actually implemented in
        CrystalBallIndustryEnergySystem, see ASSUMPTIONS.md) come from
        sector_emissions_2022.csv directly.
    The extension's ADDITIONAL percentage-point coverage is then
    (E_new/E_old) x 90.0%, i.e. it inherits the same total-emissions
    denominator as Mannhardt's own share rather than an independently
    computed absolute total (no all-sector, all-28-country total is
    available locally) — so the implied total (E_old / 0.900) and the "not
    covered" remainder are approximate, order-of-magnitude figures, not
    exact ones. Variant B's known caveat (it re-adds the shared cement/glass/
    ceramic combustion bucket already counted once under "cement" — see
    ASSUMPTIONS.md) means the extension's true additional coverage is
    somewhat below what's shown here; shown anyway since it is the
    documented, implemented choice (DEFAULT_VARIANT = "B").
    """
    df = pd.read_csv(MODEL_SCOPE_CSV)
    e_old = df.loc[df.bucket == "old", "emissions_kt_co2_28countries"].sum()
    new_b = df[(df.bucket == "new") & df.variant_tags.str.contains("B")]
    e_new = (new_b["emissions_kt_co2_28countries"] + new_b["emissions_kt_co2_uk"]).sum()

    share_old = MANNHARDT_OLD_SECTORS_SHARE_OF_TOTAL
    share_new = share_old * e_new / e_old
    share_uncovered = 1 - share_old - share_new
    total_mt = e_old / share_old / 1000

    segments = [("Existing Crystal Ball sectors\n(Mannhardt, 2026)", share_old, _ETH_BLUE, e_old / 1000),
                ("+ Industry-heat extension\n(this work)", share_new, _ETH_GREEN, e_new / 1000),
                ("Not covered by Crystal Ball", share_uncovered, _ETH_GREY, None)]

    fig, ax = plt.subplots(figsize=(10, 3.4))
    left = 0.0
    outside_slot = 0  # alternates up/down for the two small segments' outside labels
    for label, share, color, mt in segments:
        ax.barh(0, share * 100, left=left * 100, height=0.55, color=color, edgecolor="white")
        text = f"{share * 100:.1f}%" + (f"\n({mt:,.0f} Mt CO$_2$)" if mt is not None else "")
        center = left * 100 + share * 50
        if share > 0.08:
            ax.text(center, 0, text, ha="center", va="center", fontsize=9,
                    color=_text_color_for_bg(color), fontweight="bold")
        else:
            y_text = 0.62 if outside_slot == 0 else -0.62
            va = "bottom" if outside_slot == 0 else "top"
            ax.annotate(text, xy=(center, 0.275 if outside_slot == 0 else -0.275),
                        xytext=(center, y_text), fontsize=8.5, ha="center", va=va,
                        arrowprops=dict(arrowstyle="-", color=color))
            outside_slot += 1
        left += share

    handles = [Patch(facecolor=c, label=l.replace("\n", " ")) for l, _, c, _ in segments]
    ax.legend(handles=handles, fontsize=8, frameon=False, loc="upper center",
              bbox_to_anchor=(0.5, -0.3), ncol=3)
    ax.set_xlim(0, 100)
    ax.set_ylim(-1.0, 1.0)
    ax.set_yticks([])
    ax.set_xlabel("Share of total European direct CO$_2$ emissions [%]  "
                  f"(28 countries $\\approx$ {total_mt:,.0f} Mt CO$_2$/yr, approx.)")
    ax.set_title("Crystal Ball's Coverage of Total European Direct CO$_2$ Emissions",
                 fontsize=12, fontweight="bold")
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    fig.text(0.01, 0.01, "Source: Mannhardt (2026) Appendix A.2 + UNFCCC CRF, Variant B",
              fontsize=7, color="grey")
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    savefig(fig, "fig4_model_scope_coverage", subdir="method")


# Global GHG sector breakdown (WRI, "World Greenhouse Gas Emissions in 2023
# (Sector | End Use | Gas)", Climate Watch data via IEA 2025 — the Sankey at
# https://www.wri.org/data/world-greenhouse-gas-emissions-2023, the one
# actually giving the numbers below; the companion article
# https://www.wri.org/insights/4-charts-explain-greenhouse-gas-emissions-countries-and-sectors
# only has the 5 top-level shares). TWO independent partitions of the same
# 76.7% Energy total are read off that Sankey's first two columns:
#  - Source sector (left column): Electricity & Heat 33.6%, Buildings 6.3%,
#    Other Fuel Combustion 1.2%, Manufacturing & Construction 12.2%,
#    Transportation 14.3%, International Bunker 2.4%, Fugitive Emissions
#    6.8% — mutually exclusive, sums to 76.8% (~76.7%, rounding).
#  - End use (middle column): who the energy was ultimately for — Iron &
#    steel 5.8%, Chemical & petrochemical 6.5%, Non-metallic minerals
#    (cement/glass/ceramics) 2.9%, Food & tobacco 1.3%, Non-ferrous metals
#    1.8%, Machinery 1.6%, Other Industry 4.4%, Residential/Commercial
#    Buildings, Road/Air/Ship, Unallocated, Vented/Flared — also mutually
#    exclusive, sums to the same 76.7%. Every industrial end use draws from
#    BOTH source sectors above (Manufacturing & Construction's own on-site
#    fuel combustion AND its share of grid electricity/heat) — the Sankey
#    doesn't publish that per-industry electricity-vs-fuel split, so it
#    can't be read exactly off the source-sector column alone.
#
# Per user instruction: this is NOT filtered down to Crystal Ball's own
# modeled sectors (sector_emissions_2022.csv's list) — it's every end-use
# category the WRI Sankey itself labels as industry: Iron & steel, Chemical
# & petrochemical, Non-ferrous metals, Non-metallic minerals (cement/glass/
# ceramics), Machinery, Food & tobacco, and "Other Industry" (WRI's own
# catch-all for the remaining industrial subsectors it doesn't break out
# individually — textiles & leather, mining & quarrying, construction,
# wood products, etc.). Together these sum to 24.3%, ALL of Manufacturing &
# Construction's/Electricity & Heat's industrial end uses, not a Crystal-
# Ball-scope subset. That whole 24.3% end-use total is shown carved out of
# Electricity & Heat's 33.6% alone (not split proportionally across both
# source sectors, since the Sankey doesn't publish that per-industry
# electricity-vs-fuel split) — a known simplification, not a claim that
# zero of it comes from Manufacturing & Construction's direct fuel
# combustion.
_GHG_TOTAL_GT = 50.8  # GtCO2e, 2023 (Sankey title)
_GHG_ENERGY_TOTAL_SHARE = 0.767
_GHG_ELECTRICITY_HEAT_SHARE = 0.336
_GHG_MANUFACTURING_CONSTRUCTION_SHARE = 0.122  # WRI's own category — NOT "industry" (see docstring), shown as "Others"
_GHG_TRANSPORT_SHARE = 0.143
_GHG_BUILDINGS_SHARE = 0.063
_GHG_INDUSTRIAL_PROCESS_SHARE = 0.062
_GHG_AGRICULTURE_SHARE = 0.123
_GHG_WASTE_SHARE = 0.038
_GHG_LULUCF_SHARE = 0.009
# Every industrial end-use category in the WRI Sankey (see comment above) —
# not filtered to Crystal Ball's own modeled sector list.
_GHG_INDUSTRY_ENDUSE = {
    "Iron & steel": 0.058,
    "Chemical & petrochemical": 0.065,
    "Non-metallic minerals\n(cement, glass, ceramics)": 0.029,
    "Non-ferrous metals": 0.018,
    "Machinery": 0.016,
    "Food & tobacco": 0.013,
    "Other industry\n(textiles, mining, etc.)": 0.044,
}
_GHG_INDUSTRY_ENDUSE_SHARE = sum(_GHG_INDUSTRY_ENDUSE.values())  # 24.3%


def fig15_global_ghg_sector_breakdown() -> None:
    """Two stacked horizontal bars, top-down drill-in: (1) all global GHG
    emissions (100%) split into Energy (76.7%, blue), Industrial processes
    (6.2%, green — cement calcination/steel ore reduction/chemical
    reactions, non-combustion) and everything else (~17.1%, grey:
    agriculture, waste, land use); (2) directly below, Energy's own 76.7%
    split by SOURCE SECTOR (Electricity & Heat, Manufacturing &
    Construction relabeled "Others", Transportation, Buildings, other) —
    with a green wedge carved out of Electricity & Heat sized to EVERY
    industrial end-use category in the WRI Sankey (24.3% — iron & steel,
    chemicals, non-ferrous metals, non-metallic minerals, machinery, food &
    tobacco, other industry; NOT filtered to Crystal Ball's own modeled
    sectors — see the module comment above for exactly which categories and
    why). Dashed guide lines tie bar 2's span to bar 1's Energy segment so
    the drill-down relationship reads immediately.

    The two green wedges are industry's two-part global footprint: process
    emissions (top bar, 6.2%, uncapturable by any energy-system model) and
    industry's energy-side footprint (bottom bar, 24.3%, most — not all —
    of which is Crystal Ball's industry-heat extension's actual target,
    since it also models cement/glass/ceramics as heat-supply sectors)
    together approach a QUARTER of all global GHG emissions.

    A pure global-reference-data figure like fig3/fig4 above (no solved
    model results, no local dataset) — generated unconditionally in main().
    """
    elec_heat_other = _GHG_ELECTRICITY_HEAT_SHARE - _GHG_INDUSTRY_ENDUSE_SHARE
    other_energy = (_GHG_ENERGY_TOTAL_SHARE - _GHG_ELECTRICITY_HEAT_SHARE
                     - _GHG_MANUFACTURING_CONSTRUCTION_SHARE - _GHG_TRANSPORT_SHARE - _GHG_BUILDINGS_SHARE)
    other_sectors = 1.0 - _GHG_ENERGY_TOTAL_SHARE - _GHG_INDUSTRIAL_PROCESS_SHARE

    top_segments = [
        ("Energy", _GHG_ENERGY_TOTAL_SHARE, _ETH_BLUE),
        ("Industrial\nprocesses", _GHG_INDUSTRIAL_PROCESS_SHARE, _ETH_GREEN),
        ("Agriculture, waste\n& land use", other_sectors, _eth_tint(_ETH_GREY, 0.5)),
    ]
    bottom_segments = [
        ("Industry\n(electricity & heat)", _GHG_INDUSTRY_ENDUSE_SHARE, _ETH_GREEN),
        ("Non-Industry\n(electricity & heat)", elec_heat_other, _ETH_BLUE),
        ("Manufacturing &\nConstruction", _GHG_MANUFACTURING_CONSTRUCTION_SHARE, _ETH_GREY),
        ("Transportation", _GHG_TRANSPORT_SHARE, _eth_tint(_ETH_GREY, 0.25)),
        ("Buildings", _GHG_BUILDINGS_SHARE, _eth_tint(_ETH_GREY, 0.45)),
        ("Other energy", other_energy, _eth_tint(_ETH_GREY, 0.65)),
    ]

    fig, ax = plt.subplots(figsize=(11.5, 5.0))
    y_top, y_bot, bar_h = 1.0, 0.0, 0.55

    def _draw_bar(y: float, segments: list) -> dict:
        left, bounds = 0.0, {}
        for label, share, color in segments:
            ax.barh(y, share * 100, left=left * 100, height=bar_h, color=color,
                     edgecolor="white", linewidth=0.7)
            center = left * 100 + share * 50
            text = f"{label}\n{share * 100:.1f}%"
            if share >= 0.06:
                ax.text(center, y, text, ha="center", va="center", fontsize=8,
                        color=_text_color_for_bg(color), fontweight="bold", linespacing=1.2)
            else:
                ax.annotate(text, xy=(center, y - bar_h / 2), xytext=(center, y - 1.05), fontsize=7.3,
                            ha="center", va="top", arrowprops=dict(arrowstyle="-", color=color),
                            linespacing=1.15)
            bounds[label] = (left * 100, (left + share) * 100)
            left += share
        return bounds

    top_bounds = _draw_bar(y_top, top_segments)
    _draw_bar(y_bot, bottom_segments)

    # Dashed guides from Energy's edges (top bar) down to the full span of
    # the source-sector breakdown (bottom bar) — makes the "this second bar
    # IS what's inside Energy" relationship explicit rather than implied.
    x0, x1 = top_bounds["Energy"]
    for x in (x0, x1):
        ax.plot([x, x], [y_top - bar_h / 2, y_bot + bar_h / 2], color=_ETH_GREY,
                 linestyle="--", linewidth=0.9, zorder=0)

    ax.set_xlim(0, 100)
    ax.set_ylim(-0.65, 1.55)
    ax.set_yticks([])
    ax.set_xlabel("Share of total global GHG emissions [%]")
    ax.set_title("Total Global GHG Emissions", fontsize=12, fontweight="bold")
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    savefig(fig, "fig9_global_ghg_sector_breakdown", subdir="method")


# ── 10: Power-sector impact of industry-heat flexibility ───────────────────
# No flexibility vs Crystal Ball base isolates the power-sector cost of
# electrifying industry heat WITHOUT any flexibility (DSM/TES) to shape that
# new load — Crystal Ball base has no industry-heat sector at all (see
# BASE_SCENARIO's comment), so it's the "before electrification" reference.
# Full flexibility is added as a 3rd bar throughout, to see whether
# flexibility elsewhere in the system changes how much fleet buildout /
# storage cycling is needed to absorb that same new load.
#
# 3 snapshot years, each drawn as a 3-scenario bar cluster on one shared axis
# per row (see _plot_grouped_stacked_bars) rather than one subplot per year
# or per scenario; all directly modeled years under the v9_0 horizon (2020,
# 2022, ..., 2050 — reference_year=2020, interval_between_years=2, see
# get_available_years()).
SNAPSHOT_YEARS_POWER = [2030, 2040, 2050]


# ── 10: Power generation capacity mix ───────────────────────────────────────

POWER_GEN_TECHS = [
    "photovoltaics", "wind_onshore", "wind_offshore",
    "reservoir_hydro", "run-of-river_hydro",
    "nuclear",
    "natural_gas_turbine", "natural_gas_turbine_CCS",
    "hard_coal_plant", "lignite_coal_plant", "oil_plant",
    "biomass_plant", "biomass_plant_CCS",
    "waste_plant",
]

# NOTE ON PALETTE: this figure is ETH-7-colors-only (see
# [[feedback-si-figure-colors]]), same as every other SI figure in this
# script, with exactly ONE true exception: photovoltaics uses a non-ETH
# yellow, since the corporate palette has no yellow/gold at all and "solar"
# reads as wrong in any other hue. wind_onshore/wind_offshore are "2 shades
# of blue" per user request, but achieved by TINTING _ETH_BLUE itself (via
# _eth_tint(), same mechanism HEAT_SUPPLY_COLOR_MAP already uses) rather than
# a separate non-ETH blue — so wind stays on-palette. That puts 4 shades of
# the same ETH_BLUE hue in this figure (reservoir_hydro darkest, then
# run-of-river_hydro, wind_offshore, wind_onshore lightest) — distinguishable
# by lightness, the same convention HEAT_SUPPLY_COLOR_MAP uses for its
# multiple heat-pump temperature bands.
_SOLAR_YELLOW = "#FFCA3A"
POWER_GEN_COLOR_MAP = {
    "photovoltaics": _SOLAR_YELLOW,
    "wind_onshore": _eth_tint(_ETH_BLUE, 0.65),
    "wind_offshore": _eth_tint(_ETH_BLUE, 0.45),
    "reservoir_hydro": _ETH_BLUE,
    "run-of-river_hydro": _eth_tint(_ETH_BLUE, 0.25),
    "nuclear": _ETH_PURPLE,
    "natural_gas_turbine": _ETH_TURQUOISE,
    "natural_gas_turbine_CCS": _ETH_TURQUOISE,
    "hard_coal_plant": _ETH_GREY,
    "lignite_coal_plant": _eth_tint(_ETH_GREY, 0.3),
    "oil_plant": _ETH_BRONZE,
    "biomass_plant": _ETH_GREEN,
    "biomass_plant_CCS": _ETH_GREEN,
    "waste_plant": _ETH_RED,
}
POWER_GEN_HATCH_MAP = {"natural_gas_turbine_CCS": _HP_HATCH, "biomass_plant_CCS": _HP_HATCH}
# Fossil (dirtiest first) at the bottom of the stack, then biomass/waste,
# nuclear, hydro, VRE on top — same "cleaner = higher in the stack"
# convention HEAT_SUPPLY_STACK_ORDER uses.
POWER_GEN_STACK_ORDER = [
    "hard_coal_plant", "lignite_coal_plant", "oil_plant",
    "natural_gas_turbine", "natural_gas_turbine_CCS",
    "waste_plant", "biomass_plant", "biomass_plant_CCS",
    "nuclear",
    "reservoir_hydro", "run-of-river_hydro",
    "wind_onshore", "wind_offshore", "photovoltaics",
]


# BULK_STORAGE_TECHS (figures_by_run.py) is power-sector storage that exists
# in every run, including Crystal Ball base — unlike industry TES/DSM, which
# only exist once the industry-heat extension is loaded. ETH-7-colors-only
# (see the palette note above POWER_GEN_COLOR_MAP), keyed to what each tech
# stores: electricity=ETH_BLUE (battery=full strength, "hydro shade" tint for
# pumped_hydro so the two are distinguishable within the same stack), natural
# gas=ETH_TURQUOISE (matching natural_gas_turbine), oil=the same ETH_BRONZE
# as oil_plant (and oil_boiler_industry elsewhere), hydrogen=ETH_PURPLE
# (matching nuclear; no analog in the generation row, free to reuse).
STORAGE_COLOR_MAP = {
    "battery": _ETH_BLUE,
    "pumped_hydro": _eth_tint(_ETH_BLUE, 0.35),
    "natural_gas_storage": _ETH_TURQUOISE,
    "oil_storage": _ETH_BRONZE,
    "salt_cavern_storage": _ETH_PURPLE,
}
STORAGE_STACK_ORDER = ["battery", "pumped_hydro", "natural_gas_storage", "oil_storage", "salt_cavern_storage"]


def _plot_grouped_stacked_bars(
    dfs_by_year: dict[int, pd.DataFrame],
    title: str,
    unit: str,
    ax: plt.Axes,
    color_map: dict,
    hatch_map: dict,
    show_segment_labels: bool = False,
    show_legend: bool = True,
) -> None:
    """Like plot_stacked_bars, but draws one cluster of adjacent bars per
    year (dfs_by_year keys), all on a single axis, so scenarios (df columns —
    same columns/order in every year) can be compared side by side within
    each year AND across years in one glance. A 1-bar-width gap separates
    each year's cluster from the next; scenario labels sit on the bar ticks,
    year labels are annotated centered below each cluster. Unlike
    plot_stacked_bars, color_map/hatch_map are required (every caller here
    already passes a print-figure-specific palette)."""
    years = sorted(dfs_by_year)
    scenarios = dfs_by_year[years[0]].columns.tolist()
    n_scen = len(scenarios)
    bar_width = 0.8
    labeled: set[str] = set()
    positions_all: list[float] = []
    tick_labels_all: list[str] = []
    year_centers: list[float] = []

    for yi, year in enumerate(years):
        df = dfs_by_year[year]
        base = yi * (n_scen + 1)
        positions = [base + i for i in range(n_scen)]
        positions_all.extend(positions)
        tick_labels_all.extend(scenarios)
        year_centers.append((positions[0] + positions[-1]) / 2)
        positive_df = df.clip(lower=0)
        negative_df = df.clip(upper=0)
        for scen, pos in zip(scenarios, positions):
            bottom_pos = 0.0
            bottom_neg = 0.0
            for cat_idx, category in enumerate(df.index):
                val_pos = positive_df.loc[category, scen]
                val_neg = negative_df.loc[category, scen]
                color = color_map[category]
                hatch = hatch_map.get(category, "")
                add_label = category not in labeled
                if val_pos > 0:
                    ax.bar(pos, val_pos, bar_width, bottom=bottom_pos, color=color,
                           label=category if add_label else None,
                           edgecolor="white", linewidth=0.5, hatch=hatch)
                    if show_segment_labels:
                        ax.text(pos, bottom_pos + val_pos / 2, f"{val_pos:,.0f}",
                                ha="center", va="center", fontsize=6,
                                color=_text_color_for_bg(color))
                    bottom_pos += val_pos
                    labeled.add(category)
                if val_neg < 0:
                    ax.bar(pos, val_neg, bar_width, bottom=bottom_neg, color=color,
                           label=category if add_label else None,
                           edgecolor="white", linewidth=0.5, hatch=hatch if hatch else "//")
                    if show_segment_labels:
                        ax.text(pos, bottom_neg + val_neg / 2, f"{val_neg:,.0f}",
                                ha="center", va="center", fontsize=6,
                                color=_text_color_for_bg(color))
                    bottom_neg += val_neg
                    labeled.add(category)
            ax.text(pos, bottom_pos, f"{positive_df[scen].sum():,.0f}",
                    ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax.set_xticks(positions_all)
    ax.set_xticklabels(tick_labels_all, fontsize=8, rotation=30, ha="right")
    for yc, year in zip(year_centers, years):
        ax.annotate(str(year), xy=(yc, 0), xycoords=("data", "axes fraction"),
                    xytext=(0, -46), textcoords="offset points",
                    ha="center", va="top", fontsize=11, fontweight="bold")
    ax.set_ylabel(unit, fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.axhline(0, color="black", linewidth=0.5)

    if show_legend:
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles[::-1], labels[::-1],
                      bbox_to_anchor=(1.02, 1), loc="upper left",
                      fontsize=10, frameon=False)


def _power_and_storage_dfs(
    runs: list[Run], full_run: Run, include_dsm: bool,
) -> tuple[dict[int, pd.DataFrame], dict[int, pd.DataFrame]]:
    """Shared data prep for fig10/fig11: gen_by_year (generation capacity,
    GW) and disch_by_year (storage annual discharge, GWh), each {year:
    DataFrame(index=technology, columns=scenario label)}. include_dsm=True
    appends a single aggregated "DSM" row (summed across all 10
    DSM_ENERGY_STACK_ORDER techs) to disch_by_year, nonzero only in
    full_run's column (Base/No flexibility have no industry-heat sector) —
    via get_dsm_energy_equivalent, see that section's comment for the
    per-product methodology behind the number being summed here."""
    gen_by_year: dict[int, pd.DataFrame] = {}
    disch_by_year: dict[int, pd.DataFrame] = {}
    dsm_total_by_year = get_dsm_energy_equivalent(full_run.results, DSM_ENERGY_STACK_ORDER, SNAPSHOT_YEARS_POWER) \
        .sum() if include_dsm else None
    for year in SNAPSHOT_YEARS_POWER:
        gen_series = [(r.label, get_capacity(r.results, POWER_GEN_TECHS, "power")
                       .get(year, pd.Series(dtype=float))) for r in runs]
        gen_df = build_comparison_df(gen_series)
        gen_df = gen_df.reindex([t for t in POWER_GEN_STACK_ORDER if t in gen_df.index]
                                 + [t for t in gen_df.index if t not in POWER_GEN_STACK_ORDER])
        gen_by_year[year] = gen_df

        disch_series = [(r.label, get_storage_flows(r.results, BULK_STORAGE_TECHS, "flow_storage_discharge")
                         .get(year, pd.Series(dtype=float))) for r in runs]
        stack_order = STORAGE_STACK_ORDER + ["DSM"] if include_dsm else STORAGE_STACK_ORDER
        disch_df = build_comparison_df(disch_series).reindex(stack_order).fillna(0.0)
        if include_dsm:
            disch_df.loc["DSM", full_run.label] = dsm_total_by_year[year]
        disch_by_year[year] = disch_df
    return gen_by_year, disch_by_year


def _render_power_and_storage_figure(
    gen_by_year: dict[int, pd.DataFrame], disch_by_year: dict[int, pd.DataFrame],
    filename: str, storage_color_map: dict, storage_hatch_map: dict,
) -> None:
    """Shared 2-row (generation top, storage discharge bottom) rendering for
    fig10/fig11 — wide, ~16:9-ish (PowerPoint-slide-ish) aspect ratio. No
    figure-level suptitle (each row's own title carries it); segment labels
    are off on both rows (only the bar's total, matching the generation
    row) since the storage row's segments are dense enough to overlap."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 9))
    with plt.rc_context({"hatch.linewidth": 0.5}):
        _plot_grouped_stacked_bars(gen_by_year, "Power Generation Capacity", "GW", axes[0],
                                   show_segment_labels=False, show_legend=True,
                                   color_map=POWER_GEN_COLOR_MAP, hatch_map=POWER_GEN_HATCH_MAP)
        _plot_grouped_stacked_bars(disch_by_year, "Storage Annual Energy Discharged", "GWh", axes[1],
                                   show_segment_labels=False, show_legend=True,
                                   color_map=storage_color_map, hatch_map=storage_hatch_map)
    fig.tight_layout()
    fig.subplots_adjust(hspace=0.55)
    savefig(fig, filename)


def fig10_power_and_storage_impact(base_run: Run, no_flex_run: Run, full_run: Run) -> None:
    """Power-sector generation capacity (top) and storage annual energy
    discharged (bottom), Crystal Ball base / No flexibility / Full
    flexibility shown as 3 adjacent bars per year, in a single combined
    figure spanning 3 snapshot years (2030/2040/2050) — one plot per row,
    not one per scenario, so all 9 (scenario x year) bars are directly
    comparable at a glance.

    Isolates finding #1 (top row): adding electrified (but inflexible)
    industry heat demand does NOT change the generation TECHNOLOGY mix —
    every technology's SHARE of total capacity stays roughly the same across
    scenarios — it just scales the whole fleet up (+11% total capacity at
    2036 for No flexibility vs base, driven almost entirely by proportionally
    more VRE: +19% PV, +12% offshore wind, +4% onshore wind, vs. essentially
    flat dispatchable/fossil capacity). Capacity factors on the existing
    fleet barely move either (e.g. wind onshore 0.191 vs 0.192, nuclear 0.523
    vs 0.529 at 2036) — confirming this is a pure scale effect, not a
    dispatch-pattern change. The mechanism: the added load is a flat,
    non-dispatchable draw with no diurnal/seasonal shape at all (see fig7's
    docstring for the same underlying fact about the industry-heat carriers),
    so the optimizer meets it by building more of whatever is already
    cheapest at the margin (predominantly VRE), not by adding new
    technologies or new dispatchable/peaking capacity. Full flexibility is
    included as a 3rd bar to see whether shifting the industry load itself
    (via DSM/TES) reduces this fleet scale-up relative to No flexibility.

    Isolates finding #3 (bottom row): No flexibility DISCHARGES ~16% more
    from battery and ~16% more from salt-cavern (H2) storage than Crystal
    Ball base at 2036 — the existing storage fleet is cycled harder to
    buffer the added flat industry-heat electricity load. (Storage POWER
    CAPACITY itself barely differs across scenarios — battery/pumped-hydro
    within a few % everywhere — so that panel is omitted here; utilization
    is where the difference actually shows up.) Full flexibility's discharge
    sitting between No flexibility and base would mean industry-side
    flexibility substitutes for power-sector storage cycling; sitting
    at/above No flexibility would mean it doesn't. fig11 is exactly this
    figure with Full flexibility's DSM discharge added on top of its storage
    bars — see fig11_power_and_storage_impact_with_dsm.
    """
    runs = [base_run, no_flex_run, full_run]
    gen_by_year, disch_by_year = _power_and_storage_dfs(runs, full_run, include_dsm=False)
    _render_power_and_storage_figure(
        gen_by_year, disch_by_year,
        "fig10_power_and_storage_impact", STORAGE_COLOR_MAP, {},
    )


# ── SI fig11: DSM discharge translated into an energy (GWh) equivalent ─────
# ammonia_DSM/methanol_DSM already store an energy carrier (GWh) natively —
# used as-is. The other 8 INDUSTRY_DSM_TECHS store a MASS carrier
# (kt-of-product, see fig10's/fig2's docstrings for why they can't just be
# summed into a GWh total): this figure instead converts each product's
# DSM-shifted kt into an implied GWh using that PRODUCT's own system-wide
# energy intensity in the same year — total energy input (GWh, summed across
# every input carrier) across every technology that produces it, divided by
# its total output (kt) that year — rather than an assumed external energy
# density/LHV (contrast the ammonia/methanol kt-conversion reported as prose
# earlier, which HAD to borrow a literature LHV since ammonia/methanol have
# no kt-tracked production technology anywhere in this model). This makes
# the intensity specific to this model's own technology mix and efficiency
# assumptions, and lets it shift across snapshot years if that mix changes
# (e.g. primary_steel's BF_BOF/NG_DRI/H2_DRI split).
#
# fig11 sums all 10 into a SINGLE "DSM" bar segment (one color, no
# per-product breakdown) — get_dsm_energy_equivalent below still computes
# the per-product numbers first (needed to apply each product's own
# intensity/native-GWh treatment), _power_and_storage_dfs just sums them
# before handing the result to the plotter.
_PRODUCT_CARRIER_OF_DSM_TECH = {
    "primary_steel_DSM": "primary_steel",
    "secondary_steel_DSM": "secondary_steel",
    "clinker_DSM": "clinker",
    "ceramic_DSM": "ceramic",
    "glass_DSM": "glass",
    "food_DSM": "food",
    "paper_DSM": "paper",
    "olefin_DSM": "olefin",
}
DSM_ENERGY_STACK_ORDER = [
    "primary_steel_DSM", "secondary_steel_DSM", "clinker_DSM", "ceramic_DSM",
    "glass_DSM", "food_DSM", "paper_DSM", "olefin_DSM", "ammonia_DSM", "methanol_DSM",
]
# fig11 stacks this ON TOP OF STORAGE_COLOR_MAP's 5 techs in the same panel,
# so pick a shade STORAGE_COLOR_MAP doesn't already use (BLUE, TURQUOISE,
# BRONZE, PURPLE) to avoid rendering as the same color as a storage segment.
DSM_TOTAL_COLOR = _eth_tint(_ETH_GREY, 0.55)


def _production_energy_intensity(r, carrier: str, flow_in_all: pd.DataFrame) -> pd.Series:
    """GWh input energy per kt output for `carrier`, by year — summed across
    every technology that actually produces it that year (its real
    technology mix), using each producer's TOTAL energy input (every input
    carrier summed; already confirmed unit-homogeneous, all GWh, via
    Results.get_unit())."""
    prod = get_carrier_production(r, carrier)  # kt, index=technology, columns=year
    if prod.empty:
        return pd.Series(dtype=float)
    output_kt = prod.sum()
    input_gwh = pd.Series(0.0, index=output_kt.index)
    for tech in prod.index:
        if tech in flow_in_all.index.get_level_values("technology"):
            input_gwh = input_gwh.add(flow_in_all.xs(tech, level="technology").sum(), fill_value=0.0)
    return (input_gwh / output_kt).replace([np.inf, -np.inf], 0.0).fillna(0.0)


def get_dsm_energy_equivalent(r, dsm_techs: list[str], years: list[int]) -> pd.DataFrame:
    """DSM discharge (index=dsm_techs, columns=years) expressed in GWh — see
    module comment above this section for the two different methods used."""
    flow_in_all = r.get_total("flow_conversion_input")
    intensity_cache: dict[str, pd.Series] = {}
    rows = {}
    for tech in dsm_techs:
        discharge_kt_or_gwh = get_storage_flows(r, [tech], "flow_storage_discharge")
        if tech in DSM_ENERGY_CARRIER_TECHS:
            rows[tech] = {y: discharge_kt_or_gwh.get(y, pd.Series(dtype=float)).sum() for y in years}
            continue
        carrier = _PRODUCT_CARRIER_OF_DSM_TECH[tech]
        if carrier not in intensity_cache:
            intensity_cache[carrier] = _production_energy_intensity(r, carrier, flow_in_all)
        intensity = intensity_cache[carrier]
        rows[tech] = {y: discharge_kt_or_gwh.get(y, pd.Series(dtype=float)).sum() * intensity.get(y, 0.0)
                      for y in years}
    return pd.DataFrame(rows).T[years]


def fig11_power_and_storage_impact_with_dsm(base_run: Run, no_flex_run: Run, full_run: Run) -> None:
    """Exactly fig10_power_and_storage_impact's template (same 2-row layout,
    same 3-scenario x 3-year grouped bars, same generation panel on top) —
    the only difference is that Full flexibility's storage-discharge bars
    here also stack a single "DSM" segment on top of the same 5
    power-sector storage techs fig10 shows alone: all 10 DSM products
    summed into one number via get_dsm_energy_equivalent (see that
    section's comment for the per-product methodology behind the sum), one
    color, no per-product breakdown. Base / No flexibility get 0 (no
    industry-heat sector)."""
    runs = [base_run, no_flex_run, full_run]
    gen_by_year, disch_by_year = _power_and_storage_dfs(runs, full_run, include_dsm=True)
    combined_color_map = {**STORAGE_COLOR_MAP, "DSM": DSM_TOTAL_COLOR}
    _render_power_and_storage_figure(
        gen_by_year, disch_by_year,
        "fig11_power_and_storage_impact_with_dsm", combined_color_map, {},
    )


# ── 12-13: Base vs. DELTA (RQ1 — how does the config actually reshape) ─────
# Per user feedback on a first attempt (two side-by-side absolute-value
# panels, one per scenario, requiring the reader to subtract by eye): every
# figure below plots the DIFFERENCE itself as a first-class quantity — the
# same "plot the delta directly" fix already applied once before in this
# repo (compare_version_v8_v9.py's fig_crude_oil_transport_shift, replacing
# an earlier "two near-identical absolute curves" draft per the same kind
# of feedback).
#
# fig12 (capacity | storage discharge, side by side) went through 2 rounds
# of this feedback: v1 put base/no-flex/full-flex as 3 absolute bars
# (fig10's own template) — too much eyeballing required. v2 added a 2nd,
# separate delta bar starting at y=0 next to the base bar — better, but the
# delta bar was visually dwarfed sitting next to a much taller base bar
# (e.g. +250 GW next to a 2,707 GW base). v3 (this one): the delta bar
# still stands separately (so its own internal stack/composition/hatching
# stays legible) but FLOATS starting at the TOP of that year's base bar
# instead of at 0 — it lands at the height where it actually attaches to
# the existing system, with a thin dashed guide connecting the two, plus a
# "+X.X%" label. A "%change" is the natural complement to an absolute GW
# delta here (unlike fig13's per-node choice below) because there's exactly
# ONE meaningful denominator (that year's own EU-wide base total) — no
# small-base blow-up risk.
#
# fig13 is the only spatial figure in this file. Went through 2 rounds too:
# v1 was a single-hue choropleth (one flat color per node) — didn't show
# WHAT changed, only how much. v2 replaced that with small stacked-bar
# glyphs per node (magnitude + composition) — functional, but bars read as
# slightly ad hoc map decoration. v3 (this one): proportional pie charts —
# a standard cartographic convention for exactly this data shape (one
# value + a categorical breakdown, per point location) — AREA (not radius)
# scaled to each node's own total |delta|, wedges = technology-category
# share. Sized in GW, not % of that node's own base: with node populations
# this uneven (Germany's base capacity is ~50x Slovakia's), a small
# country's small absolute change would read as a huge, misleading %,
# while GW stays directly comparable to fig12's own EU-total number and to
# real grid-planning relevance (a country adding 250 GW matters more for
# transmission/siting than one "doubling" from 2 GW to 4 GW).
DELTA_LABEL = r"$\Delta$ No flexibility"


def _base_and_delta_df(base_series: pd.Series, no_flex_series: pd.Series) -> pd.DataFrame:
    """Two-column DataFrame: [Crystal Ball (base) absolute, Δ No flexibility
    minus base — signed, both directions] — index is the union of both
    series' technologies, missing entries filled with 0 before subtracting
    so a tech present in only one run still gets a correct (not NaN) delta."""
    all_idx = base_series.index.union(no_flex_series.index)
    base = base_series.reindex(all_idx, fill_value=0.0)
    no_flex = no_flex_series.reindex(all_idx, fill_value=0.0)
    return pd.DataFrame({BASE_SCENARIO[1]: base, DELTA_LABEL: no_flex - base})


def _plot_base_and_floating_delta(
    dfs_by_year: dict[int, pd.DataFrame], title: str, unit: str, ax: plt.Axes,
    color_map: dict, hatch_map: dict, show_legend: bool = True, decimals: int = 0,
) -> None:
    """Per year: 2 adjacent bars — Crystal Ball base (stacked normally from
    0) and the delta (stacked from the TOP of that same year's base bar
    instead of from 0: positive segments extend up from there, negative
    extend down from there) — so the delta is drawn at the height where it
    actually lands on top of the existing system, with a dashed guide
    connecting the two bars, plus a "+X.X%" (delta total / base total)
    label. Not built on _plot_grouped_stacked_bars (that one always stacks
    every column from 0 — the whole point here is that the 2nd column
    doesn't). `decimals` controls the numeric label precision (0 for GW-
    scale values in the thousands; 1 for TWh-scale storage values, where a
    whole-number round-off would hide a real ~1-digit swing)."""
    years = sorted(dfs_by_year)
    base_label, delta_label = dfs_by_year[years[0]].columns.tolist()
    bar_width = 0.8
    labeled: set[str] = set()
    positions_all: list[float] = []
    tick_labels_all: list[str] = []
    year_centers: list[float] = []

    for yi, year in enumerate(years):
        df = dfs_by_year[year]
        base_pos = yi * 3
        delta_pos = base_pos + 1
        positions_all.extend([base_pos, delta_pos])
        tick_labels_all.extend([base_label, delta_label])
        year_centers.append((base_pos + delta_pos) / 2)

        bottom = 0.0
        for category in df.index:
            val = df.loc[category, base_label]
            if abs(val) < 1e-6:
                continue
            color = color_map[category]
            ax.bar(base_pos, val, bar_width, bottom=bottom, color=color,
                   label=category if category not in labeled else None,
                   edgecolor="white", linewidth=0.5, hatch=hatch_map.get(category, ""))
            bottom += val
            labeled.add(category)
        base_total = bottom
        ax.text(base_pos, base_total, f"{base_total:,.{decimals}f}", ha="center", va="bottom",
                 fontsize=8, fontweight="bold")

        top, bot = base_total, base_total
        for category in df.index:
            val = df.loc[category, delta_label]
            color = color_map[category]
            hatch = hatch_map.get(category, "")
            if val > 0:
                ax.bar(delta_pos, val, bar_width, bottom=top, color=color,
                       label=category if category not in labeled else None,
                       edgecolor="white", linewidth=0.5, hatch=hatch)
                top += val
                labeled.add(category)
            elif val < 0:
                ax.bar(delta_pos, val, bar_width, bottom=bot, color=color,
                       label=category if category not in labeled else None,
                       edgecolor="white", linewidth=0.5, hatch=hatch if hatch else "//")
                bot += val
                labeled.add(category)
        delta_total = df[delta_label].sum()
        pct = (delta_total / base_total * 100) if base_total else 0.0
        label_y, va = (top, "bottom") if delta_total >= 0 else (bot, "top")
        ax.text(delta_pos, label_y, f"{delta_total:+,.{decimals}f} ({pct:+.1f}%)",
                 ha="center", va=va, fontsize=8, fontweight="bold")
        ax.plot([base_pos + bar_width / 2, delta_pos - bar_width / 2], [base_total, base_total],
                color="#888888", linestyle="--", linewidth=0.8, zorder=0)

    ax.set_xticks(positions_all)
    ax.set_xticklabels(tick_labels_all, fontsize=8, rotation=30, ha="right")
    for yc, year in zip(year_centers, years):
        ax.annotate(str(year), xy=(yc, 0), xycoords=("data", "axes fraction"),
                    xytext=(0, -46), textcoords="offset points",
                    ha="center", va="top", fontsize=11, fontweight="bold")
    ax.set_ylabel(unit, fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.axhline(0, color="black", linewidth=0.5)
    if show_legend:
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles[::-1], labels[::-1], bbox_to_anchor=(1.02, 1),
                      loc="upper left", fontsize=8, frameon=False)


def fig12_capacity_and_storage_base_and_delta(base_run: Run, no_flex_run: Run) -> None:
    """Power generation capacity (left) and storage annual energy discharged
    (right), side by side, 3 snapshot years each (2030/2040/2050, same
    SNAPSHOT_YEARS_POWER/tech scope as fig10) — each year cluster is base
    (absolute stack) + delta (floating from the base bar's own top, see
    _plot_base_and_floating_delta) with a "+X.X%" label. Replaces 2 earlier
    separate figures (one per panel) per user request to show both side by
    side in one figure instead.
    -> SI_results/fig12_capacity_and_storage_base_and_delta.svg
    """
    gen_by_year: dict[int, pd.DataFrame] = {}
    disch_by_year: dict[int, pd.DataFrame] = {}
    for year in SNAPSHOT_YEARS_POWER:
        base_gen = get_capacity(base_run.results, POWER_GEN_TECHS, "power").get(year, pd.Series(dtype=float))
        nf_gen = get_capacity(no_flex_run.results, POWER_GEN_TECHS, "power").get(year, pd.Series(dtype=float))
        gen_df = _base_and_delta_df(base_gen, nf_gen)
        gen_by_year[year] = gen_df.reindex(
            [t for t in POWER_GEN_STACK_ORDER if t in gen_df.index]
            + [t for t in gen_df.index if t not in POWER_GEN_STACK_ORDER])

        # GWh -> TWh per user request (raw GWh totals like "522,721" are
        # unwieldy at print size; TWh keeps 3-4 significant digits instead).
        base_disch = get_storage_flows(base_run.results, BULK_STORAGE_TECHS, "flow_storage_discharge") \
            .get(year, pd.Series(dtype=float)) / 1000.0
        nf_disch = get_storage_flows(no_flex_run.results, BULK_STORAGE_TECHS, "flow_storage_discharge") \
            .get(year, pd.Series(dtype=float)) / 1000.0
        disch_by_year[year] = _base_and_delta_df(base_disch, nf_disch).reindex(STORAGE_STACK_ORDER).fillna(0.0)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    with plt.rc_context({"hatch.linewidth": 0.5}):
        _plot_base_and_floating_delta(gen_by_year, "Power Generation Capacity", "GW", axes[0],
                                      color_map=POWER_GEN_COLOR_MAP, hatch_map=POWER_GEN_HATCH_MAP)
        _plot_base_and_floating_delta(disch_by_year, "Storage Annual Energy Discharged", "TWh", axes[1],
                                      color_map=STORAGE_COLOR_MAP, hatch_map={}, decimals=1)
    fig.tight_layout()
    savefig(fig, "fig12_capacity_and_storage_base_and_delta")


# ── fig13: regional map — per-node capacity | storage bar glyphs ───────────
# Went through several rounds: v1 was a single flat-color choropleth (no
# composition); v2 was one small stacked-bar glyph per node, 3 broad
# categories (VRE/other-gen/storage); v3 was proportional pie charts, one
# per node; v4 (this one) is back to bar glyphs (per user follow-up, pies
# for both capacity AND storage at once read as "messy") — TWO bars per
# node side by side, capacity (left) and storage (right), each stacked by
# INDIVIDUAL technology (techs under 5% of that node's own bar total
# grouped into a single "Other" segment). A "+X.X%" capacity label sits
# below each node's bar pair (node's own Δcapacity / node's own base
# capacity).
#
# Storage is DISCHARGE (GWh), not capacity (GW) — same quantity as fig12's
# storage panel / fig10's bottom row, for consistency, and for a real
# reason: storage POWER capacity barely differs across scenarios (see
# fig10's own docstring) and salt_cavern_storage/natural_gas_storage's
# power capacity specifically has capex_specific_storage == 0 EUR/GW
# (confirmed directly against a solved run) — an unconstrained, free
# "artifact" dimension, same pattern already documented for
# heat_industry_temp_conversion_*'s ~37,700 GW capacity elsewhere in this
# file, that swamped every real signal in an earlier capacity-based draft
# of this map by 2 orders of magnitude. Discharge doesn't have this
# problem (it's bounded by each tech's real, costed ENERGY/reservoir
# capacity) and is what fig10/11/fig12 already use for storage throughout.
_REGIONAL_YEAR = 2050  # final modeled year: full build-out, clearest spatial signal
_NODE_BAR_MIN_SHARE = 0.05  # techs below this share of a node's own bar total are grouped into "Other"
_NODE_BAR_OTHER_COLOR = "#bbbbbb"
# BE/LU sit close enough to NL/DE that their default (at-node) bar+label
# position collides with the neighboring country's bar/label at print font
# size -- manual (dlon, dlat) nudges for just this cluster, found by
# inspection (a general auto-declutter isn't worth it for 2 nodes). Applied
# to BOTH the bar glyph and the text label (via the same dict) so they move
# together rather than drifting apart.
_NODE_POSITION_NUDGE = {"BE": (-1.6, -0.2), "LU": (1.5, -0.6)}


def _node_capacity_by_tech(r, techs: list[str], year: int) -> pd.DataFrame:
    """Per-node, per-technology capacity (GW) — index=node, columns=
    technology. capacity's location level is named "location" (confirmed
    directly against a solved run — flows use "node" instead), so this
    can't reuse get_capacity (it collapses that level entirely)."""
    cap = r.get_total("capacity")
    cap = cap[cap.index.get_level_values("capacity_type") == "power"]
    sub = cap[cap.index.get_level_values("technology").isin(techs)]
    if sub.empty or year not in sub.columns:
        return pd.DataFrame()
    return sub[year].groupby(["location", "technology"]).sum().unstack("technology").fillna(0.0)


def _node_storage_discharge_by_tech(r, techs: list[str], year: int) -> pd.DataFrame:
    """Per-node, per-technology storage annual discharge (GWh) — index=node,
    columns=technology. flow_storage_discharge's location level is named
    "node" (unlike capacity's "location" — confirmed directly)."""
    disch = r.get_total("flow_storage_discharge")
    sub = disch[disch.index.get_level_values("technology").isin(techs)]
    if sub.empty or year not in sub.columns:
        return pd.DataFrame()
    return sub[year].groupby(["node", "technology"]).sum().unstack("technology").fillna(0.0)


def _group_small_shares(values: pd.Series, min_share: float = _NODE_BAR_MIN_SHARE) -> pd.Series:
    """Techs below `min_share` of THIS node's own bar total are summed into
    one "Other" bucket — applied per node/per bar independently, so which
    real techs end up inside "Other" can differ node to node (a tech
    dominant in one country may be a rounding error in another)."""
    total = values.sum()
    if total <= 0:
        return values
    share = values / total
    small, big = values[share < min_share], values[share >= min_share]
    if not small.empty and small.sum() > 1e-6:
        big = pd.concat([big, pd.Series({"Other": small.sum()})])
    return big


def _nice_round(value: float) -> float:
    """Round to a visually clean size-legend reference number: nearest 50
    above 100, nearest 10 above 20, nearest 5 above 5, else nearest 1 — e.g.
    257 -> 250, 38.7 -> 40, matching the "round numbers like 250 and 50"
    convention requested for the legend."""
    if value <= 0:
        return 0.0
    step = 50 if value >= 100 else 10 if value >= 20 else 5 if value >= 5 else 1
    return round(value / step) * step


def _draw_node_two_bars(
    ax: plt.Axes, coords: pd.DataFrame, cap_deltas: pd.DataFrame, storage_deltas: pd.DataFrame,
    cap_color_map: dict, storage_color_map: dict,
    max_height_deg: float = 2.6, bar_width_deg: float = 0.75, gap_deg: float = 0.15,
    cap_minor_ref: float = 20.0, storage_minor_ref: float = 10_000.0,
) -> tuple[float, float, float, float, float, float]:
    """Two adjacent small stacked-bar glyphs per node — capacity (left) and
    storage (right) — each independently scaled (own max node total ->
    max_height_deg) since the two quantities aren't on the same scale.
    max_height_deg is deliberately generous (rather than just enough for
    the single largest node) so smaller-but-real changes stay visible
    rather than shrinking toward the minimum-visibility floor below.
    Returns (cap_major_ref, cap_minor_ref, storage_major_ref,
    storage_minor_ref, cap_scale, storage_scale) for the size legend:
    major is the nice-rounded actual max (what the tallest bar means),
    minor is a fixed, requested reference (20 GW / 10,000 GWh — smaller,
    round numbers a reader can judge any bar against) rather than an
    auto-derived fraction of major. Scale factors let the legend be drawn
    at the exact same scale as these real bars (see _draw_size_legend_on_map
    — an earlier draft's legend used a separate inset axes with its own
    independent coordinate system, NOT visually calibrated to the map's
    real degrees-per-GW scale, making the legend numerically correct but
    visually misleading)."""
    cap_pos = cap_deltas.clip(lower=0)
    storage_pos = storage_deltas.clip(lower=0)
    cap_totals = cap_pos.sum(axis=1)
    storage_totals = storage_pos.sum(axis=1)
    cap_max = float(cap_totals.max()) if len(cap_totals) else 0.0
    storage_max = float(storage_totals.max()) if len(storage_totals) else 0.0
    cap_scale = max_height_deg / cap_max if cap_max > 0 else 0.0
    storage_scale = max_height_deg / storage_max if storage_max > 0 else 0.0

    # Below this degree-height, a rectangle's own outline (a fixed line
    # width in points, not degrees) is thicker than the rectangle itself —
    # rendering as a small dark smudge rather than a genuine bar. Skip
    # drawing that side entirely below the threshold (the "+X%" text label
    # is unaffected, still drawn from the real, un-rounded value) rather
    # than let near-zero nodes clutter the map with noise instead of signal.
    _MIN_VISIBLE_DEG = 0.05

    all_nodes = cap_deltas.index.union(storage_deltas.index)
    for node in all_nodes:
        if node not in coords.index:
            continue
        cap_total = cap_totals.get(node, 0.0)
        storage_total = storage_totals.get(node, 0.0)
        cap_h_total = cap_total * cap_scale
        storage_h_total = storage_total * storage_scale
        draw_cap = cap_h_total >= _MIN_VISIBLE_DEG
        draw_storage = storage_h_total >= _MIN_VISIBLE_DEG
        if not draw_cap and not draw_storage:
            continue
        dlon, dlat = _NODE_POSITION_NUDGE.get(node, (0.0, 0.0))
        lon, lat = coords.loc[node, "lon"] + dlon, coords.loc[node, "lat"] + dlat
        cap_cx = lon - gap_deg / 2 - bar_width_deg / 2
        stor_cx = lon + gap_deg / 2 + bar_width_deg / 2

        if draw_cap:
            bottom = 0.0
            for cat, val in _group_small_shares(cap_pos.loc[node]).items():
                h = val * cap_scale
                color = cap_color_map.get(cat, _NODE_BAR_OTHER_COLOR)
                ax.add_patch(Rectangle((cap_cx - bar_width_deg / 2, lat + bottom), bar_width_deg, h,
                                        facecolor=color, edgecolor="black", linewidth=0.25, zorder=5))
                bottom += h
        if draw_storage:
            bottom = 0.0
            for cat, val in _group_small_shares(storage_pos.loc[node]).items():
                h = val * storage_scale
                color = storage_color_map.get(cat, _NODE_BAR_OTHER_COLOR)
                ax.add_patch(Rectangle((stor_cx - bar_width_deg / 2, lat + bottom), bar_width_deg, h,
                                        facecolor=color, edgecolor="black", linewidth=0.25, zorder=5))
                bottom += h
        # Baseline only spans the side(s) actually drawn -- a single narrow
        # tick under a bar-less node reads as a stray mark, not a glyph.
        if draw_cap and draw_storage:
            x0, x1 = cap_cx - bar_width_deg / 2, stor_cx + bar_width_deg / 2
        elif draw_cap:
            x0, x1 = cap_cx - bar_width_deg / 2, cap_cx + bar_width_deg / 2
        else:
            x0, x1 = stor_cx - bar_width_deg / 2, stor_cx + bar_width_deg / 2
        ax.plot([x0, x1], [lat, lat], color="black", linewidth=0.5, zorder=6)

    cap_major = _nice_round(cap_max)
    storage_major = _nice_round(storage_max)
    return cap_major, cap_minor_ref, storage_major, storage_minor_ref, cap_scale, storage_scale


def _draw_size_legend_on_map(
    ax: plt.Axes, anchor_lon: float, anchor_lat: float,
    cap_major: float, cap_minor: float, cap_scale: float,
    storage_major: float, storage_minor: float, storage_scale: float,
    bar_width_deg: float = 0.75, gap_deg: float = 4.8,
) -> None:
    """Reference bars for the size legend, drawn directly on the map in the
    SAME (lon, lat) data coordinates and the SAME cap_scale/storage_scale
    as the real per-node bars (_draw_node_two_bars) — guarantees the
    legend is visually true to the map, unlike an earlier draft's separate
    inset axes (its own independent y-range stretched to fill its box,
    completely decoupled from the map's real degrees-per-GW scale — so a
    "200 GW" legend bar did not actually render at the same height per GW
    as a real 200 GW bar on the map)."""
    entries = [("Capacity", cap_major, cap_minor, cap_scale, "GW"),
               ("Storage", storage_major, storage_minor, storage_scale, "GWh")]
    for i, (label, major, minor, scale, unit) in enumerate(entries):
        if major <= 0:
            continue
        x = anchor_lon + i * gap_deg
        major_h, minor_h = major * scale, minor * scale
        ax.add_patch(Rectangle((x - bar_width_deg / 2, anchor_lat), bar_width_deg, major_h,
                                facecolor="none", edgecolor="black", linewidth=0.8, zorder=5))
        ax.text(x, anchor_lat + major_h + 0.1, f"{major:,.0f} {unit}",
                ha="center", va="bottom", fontsize=8.5, zorder=5)
        ax.add_patch(Rectangle((x - bar_width_deg / 2, anchor_lat), bar_width_deg, minor_h,
                                facecolor="black", edgecolor="black", linewidth=0.8, zorder=5))
        if minor > 0 and minor_h < major_h - 0.08:
            ax.text(x + bar_width_deg / 2 + 0.1, anchor_lat + minor_h, f"{minor:,.0f}",
                    ha="left", va="center", fontsize=8, zorder=5)
        ax.text(x, anchor_lat - 0.15, label, ha="center", va="top",
                fontsize=8.5, fontweight="bold", zorder=5)
    top = anchor_lat + max(cap_major * cap_scale, storage_major * storage_scale, 0.0)
    ax.text(anchor_lon + gap_deg / 2, top + 0.9, "Bar height",
            ha="center", va="bottom", fontsize=9.5, zorder=5)


def fig13_regional_capacity_delta_map(base_run: Run, no_flex_run: Run) -> None:
    """Europe map, year 2050: at each of the 28 nodes, two small bar glyphs
    — Δ capacity (left, GW) and Δ storage annual discharge (right, GWh),
    No flexibility minus Crystal Ball base — each stacked by individual
    technology (techs under 5% of that node's own bar grouped into
    "Other"), plus a "+X.X%" label below showing that node's own capacity
    increase relative to ITS OWN base capacity. Scope is POWER_GEN_TECHS /
    BULK_STORAGE_TECHS, i.e. the PRE-EXISTING power system's own regional
    reshaping — not where the new industry-heat demand itself happens to
    sit (an exogenous input fact, not a modeled response).

    Skipped gracefully (with a printed note) if geopandas or the cached
    Natural Earth shapefile (data/naturalearth/, see plots/natural_earth.py)
    aren't available — same fallback convention as fig13_mga_axis_construction.
    -> SI_results/fig13_regional_capacity_delta_map.svg
    """
    if not NATURALEARTH_SHP.exists():
        print("  skipping fig13_regional_capacity_delta_map: Natural Earth shapefile not "
              f"cached under {NATURALEARTH_SHP.parent.relative_to(REPO_ROOT)} — run "
              "scripts/plot_country_groups_map.py once to download it")
        return
    try:
        import geopandas as gpd
    except ImportError:
        print("  skipping fig13_regional_capacity_delta_map: geopandas not installed")
        return

    world = gpd.read_file(NATURALEARTH_SHP)[["ISO_A2_EH", "geometry"]]
    minx, maxx = EUROPE_EXTENT["lon"]
    miny, maxy = EUROPE_EXTENT["lat"]
    world = world.cx[minx:maxx, miny:maxy]
    coords = no_flex_run.results.get_coords()

    cap_base = _node_capacity_by_tech(base_run.results, POWER_GEN_TECHS, _REGIONAL_YEAR)
    cap_nf = _node_capacity_by_tech(no_flex_run.results, POWER_GEN_TECHS, _REGIONAL_YEAR)
    cap_deltas = cap_nf.sub(cap_base, fill_value=0.0).fillna(0.0)
    cap_base_total = cap_base.sum(axis=1)

    storage_base = _node_storage_discharge_by_tech(base_run.results, BULK_STORAGE_TECHS, _REGIONAL_YEAR)
    storage_nf = _node_storage_discharge_by_tech(no_flex_run.results, BULK_STORAGE_TECHS, _REGIONAL_YEAR)
    storage_deltas = storage_nf.sub(storage_base, fill_value=0.0).fillna(0.0)

    cap_pos_totals = cap_deltas.clip(lower=0).sum(axis=1)
    pct = pd.Series({
        node: cap_pos_totals[node] / cap_base_total.get(node, 0.0) * 100
        for node in cap_pos_totals.index
        if cap_pos_totals[node] > 1e-3 and cap_base_total.get(node, 0.0) > 1e-6
    })

    # EUROPE_EXTENT's lon/lat span is ~1.84:1 (wide) -- figsize matched to
    # that so equal-aspect geopandas doesn't leave large blank margins (the
    # same fix already applied once to fig14 in an earlier round). Sized up
    # again per user request for larger text/glyphs overall.
    fig, ax = plt.subplots(figsize=(15, 9))
    world.plot(ax=ax, color="#f7f7f7", edgecolor="#B0B0B0", linewidth=0.4)

    # Per-node capacity-increase % shown as a light grey country fill too
    # (in addition to the bars/text label) — per user request, so the
    # highest-% nodes are visible at a glance even before reading any
    # label. Kept deliberately subtle/light-grey-only (never colorful, never
    # dark) so it stays a background cue and doesn't compete with the
    # bars' own technology colors, which carry the primary information.
    # Colorbar lives in the bottom-left legend cluster with everything else
    # (per user request to consolidate all legends into one corner).
    if len(pct):
        node_to_iso = {n: ISO_A2_EH_OVERRIDES.get(n, n) for n in pct.index}
        pct_df = pd.DataFrame({"iso_a2_eh": [node_to_iso[n] for n in pct.index], "pct": pct.values})
        shaded = world.merge(pct_df, left_on="ISO_A2_EH", right_on="iso_a2_eh", how="inner")
        pct_cmap = LinearSegmentedColormap.from_list("pct_grey", ["#f7f7f7", "#8f8f8f"])
        pct_vmax = float(pct.max())
        shaded.plot(ax=ax, column="pct", cmap=pct_cmap, vmin=0, vmax=pct_vmax,
                    edgecolor="#B0B0B0", linewidth=0.4)
        sm = plt.cm.ScalarMappable(cmap=pct_cmap, norm=plt.Normalize(vmin=0, vmax=pct_vmax))
        sm.set_array([])
        cax = ax.inset_axes([0.02, 0.62, 0.20, 0.022])
        cbar = fig.colorbar(sm, cax=cax, orientation="horizontal")
        cbar.set_label("Node shading: capacity increase [%]", fontsize=8.5, labelpad=3)
        cbar.ax.tick_params(labelsize=7.5)

    cap_major, cap_minor, storage_major, storage_minor, cap_scale, storage_scale = _draw_node_two_bars(
        ax, coords, cap_deltas, storage_deltas, POWER_GEN_COLOR_MAP, STORAGE_COLOR_MAP)

    for node in cap_pos_totals.index:
        if node not in coords.index or cap_pos_totals[node] <= 1e-3:
            continue
        label = node if node not in pct.index else f"{node}\n+{pct[node]:.0f}%"
        dlon, dlat = _NODE_POSITION_NUDGE.get(node, (0.0, 0.0))
        ax.text(coords.loc[node, "lon"] + dlon, coords.loc[node, "lat"] - 0.45 + dlat, label,
                fontsize=11, ha="center", va="top", color="#222222", linespacing=1.2, zorder=6)

    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_axis_off()
    ax.set_title(f"Difference: Crystal Ball Base vs. No Flexibility ({_REGIONAL_YEAR})",
                 fontsize=17, fontweight="bold")

    # Two separate legends (conversion vs. storage technologies, ZEN-garden's
    # own vocabulary for the two technology classes) rather than one
    # combined list, plus the size legend and the % colorbar — all 4 in the
    # bottom-left corner per user request, stacked so none overlap: bar-
    # height reference bars lowest (real lon/lat, in the open Atlantic west
    # of Portugal -- must stay in real map coordinates, not axes-fraction,
    # to remain visually true to the map's own scale, see
    # _draw_size_legend_on_map), technology legends above that, colorbar on
    # top (placed further above, near the pct-shading section above).
    all_used = pd.concat([cap_deltas.clip(lower=0), storage_deltas.clip(lower=0)]).sum()
    all_used = all_used[all_used > 1e-3].index.tolist()
    used_cap_techs = [t for t in POWER_GEN_STACK_ORDER if t in all_used]
    used_storage_techs = [t for t in STORAGE_STACK_ORDER if t in all_used]

    cap_handles = [Patch(facecolor=POWER_GEN_COLOR_MAP[t], edgecolor="black", label=t) for t in used_cap_techs]
    cap_handles.append(Patch(facecolor=_NODE_BAR_OTHER_COLOR, edgecolor="black", label="Other"))
    storage_handles = [Patch(facecolor=STORAGE_COLOR_MAP[t], edgecolor="black", label=t) for t in used_storage_techs]
    storage_handles.append(Patch(facecolor=_NODE_BAR_OTHER_COLOR, edgecolor="black", label="Other"))

    conv_legend = ax.legend(handles=cap_handles, loc="lower left", bbox_to_anchor=(0.01, 0.18),
                             fontsize=9.5, frameon=False, title="Conversion technologies",
                             title_fontsize=10, ncol=2, columnspacing=1.0, handletextpad=0.6)
    ax.add_artist(conv_legend)
    storage_legend = ax.legend(handles=storage_handles, loc="lower left", bbox_to_anchor=(0.01, 0.32),
                                fontsize=9.5, frameon=False, title="Storage technologies", title_fontsize=10)
    ax.add_artist(storage_legend)

    # Bar-height size legend — placed in real (lon, lat) map coordinates, in
    # the open Atlantic west of Portugal/Ireland (no modeled node sits
    # there) — see _draw_size_legend_on_map's docstring for why this can't
    # be a separate inset axes like the two technology legends above.
    _draw_size_legend_on_map(ax, anchor_lon=-24.0, anchor_lat=35.0,
                              cap_major=cap_major, cap_minor=cap_minor, cap_scale=cap_scale,
                              storage_major=storage_major, storage_minor=storage_minor,
                              storage_scale=storage_scale)

    fig.tight_layout()
    savefig(fig, "fig13_regional_capacity_delta_map")


# ── 11: MGA method schematic (no data) ──────────────────────────────────────
# Purely illustrative 2D geometry, hand-picked below (not derived from any
# solved model). Left panel: a toy feasible region under a linear objective,
# its cost-optimal vertex x*, and the near-optimal space X_eps = {x in X |
# c^T x <= (1+eps)C*} - the "wedge" cut off by the slack bound. Letters and
# minimal in-plot-label style (no legend) follow M. Steen's thesis (Steen
# 2026, in mga_tests/Steen2026_Thesis.pdf), Section 2.1 / Figure 1 - this
# work uses a different support-function algorithm than his ORACLE, so only
# this near-optimal-space definition (common background, not method-specific)
# is adopted from it. Right panel: the same wedge (now treated as an unknown
# polytope) approximated from both sides - an outer approximation (AO, a
# bounding box, cheap to get from per-axis min/max solves) and an inner
# approximation (IO, the convex hull of whatever vertices directional solves
# have actually found so far, starting from just z*) - refined by solving in
# new directions until IO closes the gap to AO. This panel documents our own
# algorithm, not ORACLE, so it keeps its original generic IO/AO vocabulary.

# Toy feasible region (hexagon) and its cost-optimal vertex under a linear
# objective cost(x, y) = x + y (minimized). Chosen so z* is a genuine corner
# solution (every other vertex has a strictly higher x+y).
_MGA_FEASIBLE = [(1, 1), (5, 0.5), (8, 2), (7, 6), (3, 7), (0.5, 4)]
_MGA_Z_STAR = (1.0, 1.0)  # argmin of x + y over _MGA_FEASIBLE
_MGA_EPS = 0.4  # illustrative near-optimality slack (fraction of C*), not a real value

# Where the two iso-cost lines (x+y = C*, x+y = (1+eps)*C*) cross the hexagon,
# hand-solved from the edges adjacent to z* (line-segment intersection, see
# module comment above): the slack line cuts the (1,1)-(5,0.5) edge at
# (1.914, 0.886) and the (0.5,4)-(1,1) edge at (0.84, 1.96). Together with z*
# these 3 points bound the near-optimal wedge - the same shape zoomed into on
# the right.
_MGA_NEAR_OPT_WEDGE = [_MGA_Z_STAR, (1.914, 0.886), (0.840, 1.960)]


def _mga_iso_cost_line(cost: float, span: float = 1.0) -> tuple[list[float], list[float]]:
    """Two points spanning the line x + y = cost, for plotting."""
    return [-span, cost + span], [cost + span, -span]


def fig11_mga_method() -> None:
    """Conceptual, non-data schematic of Modeling to Generate Alternatives
    (MGA): how the near-optimal space is defined (left) and how this work's
    algorithm explores it via inner/outer polytope approximation (right).
    Left panel's letters/style follow M. Steen's thesis (Figure 1); the
    right panel documents our own (non-ORACLE) algorithm and shows a
    mid-exploration SNAPSHOT (3 of 4 non-optimum vertices solved, 1 still
    unexplored) - solve order starts with the farthest/most-prominent
    corner (biggest single gain in discovered near-optimal volume), not an
    arbitrary or nearest-first order. See fig14_mga_exploration_sequence
    (method/fig8) for the same toy geometry run to full completion instead
    of a snapshot, and the module-level comment above this function and
    above _MGA_FEASIBLE for the (hand-picked, unitless) geometry used.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))

    # ── Left: X, x*, and the near-optimal wedge X_eps (Steen Fig. 1 style,
    #    minimal in-plot labels, no legend) ─────────────────────────────────
    ax1.add_patch(Polygon(_MGA_FEASIBLE, closed=True, facecolor=eth_tint(_ETH_GREY, 0.82),
                           edgecolor=_ETH_GREY, linewidth=1.3, zorder=1))
    ax1.add_patch(Polygon(_MGA_NEAR_OPT_WEDGE, closed=True, facecolor=eth_tint(_ETH_RED, 0.85),
                           edgecolor=_ETH_GREY, linewidth=1.3, zorder=3))

    c_star = sum(_MGA_Z_STAR)  # = 2.0
    slack_cost = c_star * (1 + _MGA_EPS)  # = 2.8
    xs, ys = _mga_iso_cost_line(slack_cost, span=0.55)
    ax1.plot(xs, ys, color=_ETH_RED, linestyle="--", linewidth=1.3, zorder=2)

    ax1.plot(*_MGA_Z_STAR, "o", color=_ETH_RED, markersize=7, zorder=5)
    ax1.annotate("$x^*$", xy=_MGA_Z_STAR, xytext=(0.1, 1.6),
                 fontsize=11, ha="right", va="bottom",
                 arrowprops=dict(arrowstyle="-", color="black", linewidth=0.9), zorder=4)

    ax1.text(5.4, 4.6, r"feasible space $\mathcal{X}$", fontsize=10.5, ha="center", va="center")

    # Approaches the wedge's interior centroid (not a vertex) from below, so
    # the straight leader line's cost sum x+y stays strictly below the
    # (1+eps)C* bound throughout - it never touches the dashed line - while
    # only briefly crossing the (unremarkable) solid hexagon edge on the way
    # in. Also clear of x*'s leader line above it (disjoint x-ranges).
    wedge_mid = (sum(p[0] for p in _MGA_NEAR_OPT_WEDGE) / 3, sum(p[1] for p in _MGA_NEAR_OPT_WEDGE) / 3)
    ax1.annotate(r"near-optimal space $\mathcal{X}_\varepsilon$", xy=wedge_mid, xytext=(2.3, -0.15),
                 fontsize=9.5, ha="left", va="bottom",
                 arrowprops=dict(arrowstyle="-", color="black", linewidth=0.9), zorder=4)

    line_anchor = ((1.914 + 0.840) / 2, (0.886 + 1.960) / 2)
    ax1.annotate(r"$\mathbf{c}^\top\mathbf{x} = (1+\varepsilon)\,C^*$", xy=line_anchor, xytext=(2.7, 2.6),
                 fontsize=10, ha="left", va="bottom", color=_ETH_RED,
                 arrowprops=dict(arrowstyle="-", color=_ETH_RED, linewidth=0.9), zorder=4)

    # Simple arrow axes (Steen's style) instead of boxed spines.
    origin, x_end, y_end = (-1.5, -0.4), (8.6, -0.4), (-1.5, 7.3)
    ax1.annotate("", xy=x_end, xytext=origin,
                 arrowprops=dict(arrowstyle="-|>", color="black", linewidth=1.0), annotation_clip=False)
    ax1.annotate("", xy=y_end, xytext=origin,
                 arrowprops=dict(arrowstyle="-|>", color="black", linewidth=1.0), annotation_clip=False)
    ax1.text(x_end[0] + 0.15, x_end[1], "$x_1$", fontsize=10.5, ha="left", va="center")
    ax1.text(y_end[0], y_end[1] + 0.2, "$x_2$", fontsize=10.5, ha="center", va="bottom")

    ax1.legend(handles=[
        Patch(facecolor=eth_tint(_ETH_GREY, 0.82), edgecolor=_ETH_GREY, label=r"feasible space $\mathcal{X}$"),
        Patch(facecolor=eth_tint(_ETH_RED, 0.85), edgecolor=_ETH_GREY, label=r"near-optimal space $\mathcal{X}_\varepsilon$"),
        plt.Line2D([0], [0], color=_ETH_RED, linestyle="--", linewidth=1.3, label=r"cost bound $\mathbf{c}^\top\mathbf{x}=(1+\varepsilon)C^*$"),
        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=_ETH_RED, markeredgecolor=_ETH_RED,
                   markersize=7, label="$x^*$ (cost-optimal design)"),
    ], loc="upper left", fontsize=8, frameon=False, bbox_to_anchor=(0.08, 0.93))

    ax1.set_xlim(-2.0, 8.9)
    ax1.set_ylim(-0.9, 7.6)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_title("The Near-Optimal Space", fontsize=11, fontweight="bold")
    for spine in ax1.spines.values():
        spine.set_visible(False)

    # ── Right: exploring the near-optimal space via IO / AO ────────────────
    # A 5-vertex toy polytope (not the same shape as the left wedge - this
    # panel is a generic zoom-in, not a pixel-exact continuation) so a
    # *partial* exploration state is meaningful: z* is always known (it's the
    # original optimization's result), while the other 4 vertices are only
    # revealed one at a time, each by a separate directional LP solve.
    z_star = (0.0, 0.0)
    v2, v3, v4, v5 = (2.6, -0.3), (3.4, 1.6), (1.8, 3.0), (-0.6, 1.8)
    # Bulge vertex between v3 and v4, pushed up-right beyond the found
    # triangle's v3-v4 edge - just enough extra room to fit a direct
    # "near-optimal space" label inside the (still-unknown) true space,
    # without touching v3/v4 themselves (so the found/inner-approx triangle
    # is unaffected).
    v_bulge = (3.6, 3.3)
    true_space = [z_star, v2, v3, v_bulge, v4, v5]
    # 3 directional solves run so far, beyond z* - crucially starting with
    # v_bulge: the actual farthest/most-prominent corner of the true space,
    # so it is the direction a gap-greedy algorithm would explore FIRST
    # (biggest single gain in discovered volume), not left permanently
    # undiscovered as in an earlier version of this figure. found's vertex
    # order (z*, v3, v_bulge, v4) traces the true_space boundary exactly
    # over this stretch, since all 3 solved points ARE true_space vertices.
    found = [z_star, v3, v_bulge, v4]
    solved_via_direction = [v_bulge, v3, v4]
    unexplored = [v5]

    xs, ys = zip(*true_space)
    ao_box = Rectangle((min(xs), min(ys)), max(xs) - min(xs), max(ys) - min(ys),
                        facecolor="none", edgecolor=_ETH_RED, linestyle="--", linewidth=1.4, zorder=2)
    ax2.add_patch(ao_box)
    ax2.add_patch(Polygon(true_space, closed=True, facecolor=eth_tint(_ETH_GREY, 0.88),
                           edgecolor=_ETH_GREY, linestyle=":", linewidth=1.2, zorder=1))
    ax2.add_patch(Polygon(found, closed=True, facecolor=eth_tint(_ETH_BLUE, 0.35),
                           edgecolor=_ETH_BLUE, linewidth=1.8, zorder=3))
    ax2.text(0.35, 1.75, "near-optimal\nspace", fontsize=8, color=_ETH_GREY, ha="center", va="center", zorder=2)

    # Per pyoNearOpt's actual direction-selection logic (see
    # exploration_methods/shared_direction_oracle.py / bbo_ORACLE.py): each
    # solve targets the direction maximising the gap between the OUTER
    # bound and the support function of the CURRENT INNER hull - so each
    # new solve's arrow starts at whichever already-solved vertex is
    # extremal (in that direction) on the hull found SO FAR, not always at
    # z*. Only solve 1 (hull = {z*} alone) is anchored at z* itself; solve 2
    # and solve 3 both extend outward from v_bulge, since it is the current
    # hull's extremal point in both those directions once solve 1 has run.
    # Per-label offsets (not a uniform +0.12,+0.12 diagonal nudge) since
    # solve 2/3 now run nearly vertical/horizontal out of v_bulge - a
    # uniform offset would crowd their labels against the v_bulge marker
    # and the outer bounding box.
    _solve_segments = [
        ((z_star, v_bulge), 1, (0.12, 0.12)),
        ((v_bulge, v3), 2, (-0.32, -0.05)),
        ((v_bulge, v4), 3, (-0.15, -0.35)),
    ]
    for (anchor, v), i, (ox, oy) in _solve_segments:
        ax2.annotate("", xy=v, xytext=anchor,
                     arrowprops=dict(arrowstyle="-|>", color=_ETH_BLUE, linewidth=1.6, mutation_scale=14),
                     zorder=4)
        mid = ((anchor[0] + v[0]) / 2, (anchor[1] + v[1]) / 2)
        ax2.text(mid[0] + ox, mid[1] + oy, f"solve {i}", fontsize=8, color=_ETH_BLUE)

    # A candidate direction only tells the solver where to search, not where
    # it will land - so, unlike the "solve" arrows above (which connect
    # already-solved points), this arrow stops short of v2 rather than
    # pointing straight at it, and is explicitly marked as an unknown
    # outcome. Anchored at v3 (not z*), matching the same current-hull logic:
    # v3 is the found hull's extremal vertex toward v2.
    next_dir_end = (v3[0] + 0.55 * (v2[0] - v3[0]), v3[1] + 0.55 * (v2[1] - v3[1]))
    ax2.annotate("", xy=next_dir_end, xytext=v3,
                 arrowprops=dict(arrowstyle="-|>", color=_ETH_GREY, linewidth=1.3,
                                 linestyle=(0, (3, 2)), mutation_scale=13), zorder=4)
    # Placed just above the arrow (inside the grey true-space fill, not
    # below it in the white margin) so it reads as labeling the arrow.
    ax2.text(next_dir_end[0] - 0.1, next_dir_end[1] + 0.2, "next direction\nto explore",
              fontsize=7.5, color=_ETH_GREY, ha="right", va="bottom")

    for v in solved_via_direction:
        ax2.plot(*v, "o", color=_ETH_BLUE, markersize=6, zorder=5)
    for v in unexplored:
        ax2.plot(*v, "o", markerfacecolor="white", markeredgecolor=_ETH_GREY, markersize=6, zorder=5)
    ax2.plot(*z_star, "o", color=_ETH_RED, markersize=7, zorder=6)
    ax2.annotate("$z^*$", xy=z_star, xytext=(0.05, 0.85),
                 fontsize=10, ha="left", va="bottom",
                 arrowprops=dict(arrowstyle="-", color=_ETH_RED, linewidth=0.9))

    ax2.legend(handles=[
        Patch(facecolor="none", edgecolor=_ETH_RED, linestyle="--", label="outer approx.: bounding box from per-axis min/max solves"),
        Patch(facecolor=eth_tint(_ETH_BLUE, 0.35), edgecolor=_ETH_BLUE, label="inner approx.: convex hull of solved points"),
        Patch(facecolor=eth_tint(_ETH_GREY, 0.88), edgecolor=_ETH_GREY, linestyle=":", label="true near-optimal space (unknown until fully explored)"),
    ], loc="upper center", fontsize=7.8, frameon=False, bbox_to_anchor=(0.5, 0.92))
    ax2.set_xlim(-1.0, 4.6)
    ax2.set_ylim(-1.6, 5.0)
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_title("Exploring the Near-Optimal Space",
                  fontsize=11, fontweight="bold")
    for spine in ax2.spines.values():
        spine.set_visible(False)

    fig.tight_layout(rect=[0, 0.02, 1, 1])
    savefig(fig, "fig5_mga_method", subdir="method")


# ── 12: LP formulation & problem size ───────────────────────────────────────

def fig12_lp_formulation() -> None:
    """General LP formulation of a cost-minimization energy transition model
    (left, hand-typeset - not derived from a solved model) alongside this
    work's actual "No flexibility" model's (approximate, rounded) problem
    size (right, read directly from that run's own benchmarking.json/
    system.json/solver.json - see the module-level comment above for why
    these aren't hardcoded). Deliberately compact: one plain LP statement,
    one stat block, nothing else.
    """
    model_dir = _search_var_dict(EULER_ROOT / SCENARIOS[0][0], max_depth=3)
    if model_dir is None:
        print(f"  skipping fig12_lp_formulation: {SCENARIOS[0][0]!r} not found under {EULER_ROOT}")
        return
    bench = json.loads((model_dir / "benchmarking.json").read_text())
    system = json.loads((model_dir / "system.json").read_text())
    solver = json.loads((model_dir / "solver.json").read_text())

    fig, ax = plt.subplots(figsize=(11.5, 3.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.add_patch(FancyBboxPatch((0.02, 0.02), 0.45, 0.89, boxstyle="round,pad=0.012,rounding_size=0.02",
                                 facecolor=eth_tint(_ETH_GREY, 0.93), edgecolor=_ETH_GREY, linewidth=1.1))
    ax.add_patch(FancyBboxPatch((0.53, 0.02), 0.45, 0.89, boxstyle="round,pad=0.012,rounding_size=0.02",
                                 facecolor=eth_tint(_ETH_BLUE, 0.90), edgecolor=_ETH_BLUE, linewidth=1.1))

    # ── Left: general formulation ───────────────────────────────────────
    # h(x)=0 / g(x)<=0 - standard equality/inequality-constraint function
    # notation, not tied to any particular linear A x = b form. Equation and
    # its description share one y and va="center" so a big equation and
    # small caption line up on the same visual center instead of one
    # baseline vs. one top-aligned.
    lx = 0.055
    ax.text(lx, 0.83, "General Formulation", fontsize=12.5, fontweight="bold")
    ax.text(lx, 0.71, "energy transition model (cost minimization)", fontsize=9, style="italic", color="#444444")

    ax.text(lx, 0.52, r"$\min_{x \,\geq\, 0} \; c^\top x$", fontsize=15, va="center")
    ax.text(lx, 0.34, "s.t.", fontsize=9.5, style="italic", color="#444444", va="center")
    ax.text(lx + 0.05, 0.26, r"$h(x) = 0$", fontsize=12.5, va="center")
    ax.text(lx + 0.24, 0.26, "energy/mass balance", fontsize=9, va="center")
    ax.text(lx + 0.05, 0.13, r"$g(x) \leq 0$", fontsize=12.5, va="center")
    ax.text(lx + 0.24, 0.13, "capacity, ramping, diffusion", fontsize=9, va="center")

    # ── Right: this work's actual model ─────────────────────────────────
    rx = 0.565
    ax.text(rx, 0.83, "ZEN-garden: \"No Flexibility\" Model", fontsize=12.5, fontweight="bold")
    ax.text(rx, 0.71, "this work, solved model", fontsize=9, style="italic", color="#444444")

    # Rounded to 1 decimal place (≈) rather than the exact benchmarking.json
    # counts - precise to the digit isn't the point here, scale is.
    ax.text(rx, 0.565, f"≈{bench['number_variables'] / 1e6:.1f}M variables", fontsize=13, fontweight="bold",
            color=_ETH_BLUE, va="center")
    ax.text(rx, 0.465, f"≈{bench['number_constraints'] / 1e6:.1f}M constraints", fontsize=13, fontweight="bold",
            color=_ETH_BLUE, va="center")

    dims_line1 = (
        f"{len(system['set_nodes'])} nodes · {len(system['set_technologies'])} technologies · "
        f"{len(system['set_carriers'])} carriers"
    )
    last_year = system["reference_year"] + (system["optimized_years"] - 1) * system["interval_between_years"]
    dims_line2 = (
        f"{system['optimized_years']} years ({system['reference_year']}–{last_year}, "
        f"{system['interval_between_years']}-yr steps) · "
        f"{system['aggregated_time_steps_per_year']} h/yr (of {system['unaggregated_time_steps_per_year']})"
    )
    ax.text(rx, 0.30, dims_line1, fontsize=9, va="center")
    ax.text(rx, 0.21, dims_line2, fontsize=9, va="center")

    ax.text(rx, 0.09, f"Solved with {solver['name'].capitalize()} barrier solver", fontsize=9,
            va="center", color="#444444")

    fig.tight_layout(rect=[0, 0.02, 1, 0.98])
    savefig(fig, "fig6_lp_formulation", subdir="method")


# ── 13: MGA axis-count construction (no data) ───────────────────────────────
# Purely illustrative, like fig11/fig12 — no solved points, hand-picked
# numbers throughout. Each panel just COUNTS candidate axes as dimensions
# are crossed: (1) 3 technology-group axes alone; (2) x 4 regions (the real
# north/west/south/east geography, drawn the same way
# plot_country_groups_map.py / fig_country_groups_map.svg in
# data/outputs/figures/mga_investment/ does — same Natural Earth polygons,
# same region split, same colors — rather than embedding that SVG file
# directly, which would need a working SVG rasterizer this environment
# doesn't have); (3) x 3 cumulative-CAPEX horizons too, all three dimensions
# shown together on one region x group x horizon chart (this work's full
# 3-way crossing, panel 3 has no separate map — just that one chart).
#
# Region/group identity is encoded consistently across all 3 panels so the
# same visual grammar carries through: COLOR = region (_MGA_AXIS_REGION_
# COLOR, same order as REGIONS/REGION_COLOR in mga_capex_periods_common.py),
# PICTOGRAM = technology group (lightning bolt = power, "H2" = hydrogen,
# "C" = carbon — the same 3 groups as config_mga_axes_capex.json's
# technology_groups). Panel 1 has no region yet, so its 3 boxes are drawn
# neutral-grey with just the pictogram identity panels 2-3 reuse.
#
# The map needs geopandas + the cached Natural Earth shapefile (data/
# naturalearth/, already downloaded by the mga_investment scripts) — a new
# dependency for this otherwise data-free figure, added deliberately per
# user request for the real geography instead of an abstract icon. Falls
# back to a simple 4-wedge compass (this figure's previous approach) if
# geopandas/the shapefile aren't available, so fig13 still generates
# unconditionally in main() like fig11/fig12 even without them.
_MGA_AXIS_REGIONS = ["north", "west", "south", "east"]
_MGA_AXIS_REGION_COLOR = dict(zip(_MGA_AXIS_REGIONS, SCENARIO_PALETTE))
# Same node -> region split as config_mga_axes_capex_cum.json's node_capex_cumulative axes.
_MGA_AXIS_REGION_NODES = {
    "north": ["DK", "EE", "FI", "IE", "LT", "LV", "NO", "SE", "UK"],
    "west": ["AT", "BE", "CH", "DE", "FR", "LU", "NL"],
    "south": ["ES", "EL", "HR", "IT", "PT", "SI"],
    "east": ["BG", "CZ", "HU", "PL", "RO", "SK"],
}
_MGA_AXIS_ISO_OVERRIDES = {"EL": "GR", "UK": "GB"}  # Natural Earth's ISO_A2_EH vs. our node codes
_MGA_AXIS_EUROPE_EXTENT = {"lon": (-25, 45), "lat": (34, 72)}
_MGA_AXIS_NATURALEARTH_SHP = REPO_ROOT / "data" / "naturalearth" / "ne_50m_admin_0_countries.shp"

_MGA_AXIS_GROUPS = ["power", "hydrogen", "carbon"]
_MGA_AXIS_GROUP_LABEL = {"power": "Power", "hydrogen": "H2", "carbon": "Carbon"}


def _mga_lightning_marker() -> MplPath:
    """Lightning-bolt Path marker for the 'power' technology group — same
    hand-drawn-Path convention as the wind/sun/gear markers in
    plot_mga_investment_map.py."""
    verts = [(0.15, 1.0), (-0.55, 0.05), (-0.05, 0.05), (-0.35, -1.0),
              (0.55, -0.05), (0.0, -0.05), (0.15, 1.0)]
    codes = [MplPath.MOVETO] + [MplPath.LINETO] * 5 + [MplPath.CLOSEPOLY]
    return MplPath(verts, codes)


# marker = lightning-bolt Path for power, mathtext letter markers ("$H_2$"/
# "$C$") for hydrogen/carbon — matplotlib renders a "$...$" string marker as
# that mathtext's own shape, so these read as crisp letters, not custom paths.
_MGA_AXIS_GROUP_MARKER = {"power": _mga_lightning_marker(), "hydrogen": r"$H_2$", "carbon": "$C$"}
_MGA_AXIS_GROUP_LINESTYLE = {"power": "-", "hydrogen": "--", "carbon": ":"}


def _mga_group_icon(ax, cx: float, cy: float, group: str, size: float, color: str) -> None:
    ax.scatter([cx], [cy], marker=_MGA_AXIS_GROUP_MARKER[group], s=size, color=color,
               linewidth=1.2, zorder=4, clip_on=False)


def _mga_region_compass(ax, cx: float, cy: float, r: float) -> None:
    """Fallback 4-wedge 'compass' standing in for the real geography, used
    only if _mga_region_map() can't load geopandas/the shapefile."""
    for region, (t1, t2) in zip(_MGA_AXIS_REGIONS, [(45, 135), (135, 225), (225, 315), (315, 405)]):
        ax.add_patch(Wedge((cx, cy), r, t1, t2, facecolor=_MGA_AXIS_REGION_COLOR[region],
                            edgecolor="white", linewidth=1.4, zorder=3))
        mid = np.radians((t1 + t2) / 2)
        ax.text(cx + 0.58 * r * np.cos(mid), cy + 0.58 * r * np.sin(mid), region[0].upper(),
                 fontsize=9, ha="center", va="center", color="white", fontweight="bold", zorder=4)


def _mga_region_map(ax, x0: float, y0: float, w: float, h: float) -> bool:
    """Real north/west/south/east map (Natural Earth country polygons,
    colored by region, N/W/S/E labels), inset into `ax` at axes-fraction box
    (x0, y0, w, h) — same geography/colors as plot_country_groups_map.py.
    Returns False (drawing nothing) if geopandas or the cached shapefile
    aren't available, so the caller can fall back to _mga_region_compass."""
    if not _MGA_AXIS_NATURALEARTH_SHP.exists():
        return False
    try:
        import geopandas as gpd
    except ImportError:
        return False
    node_to_region = {n: r for r, nodes in _MGA_AXIS_REGION_NODES.items() for n in nodes}
    iso_to_region = {_MGA_AXIS_ISO_OVERRIDES.get(n, n): r for n, r in node_to_region.items()}
    world = gpd.read_file(_MGA_AXIS_NATURALEARTH_SHP)[["ISO_A2_EH", "geometry"]]
    minx, maxx = _MGA_AXIS_EUROPE_EXTENT["lon"]
    miny, maxy = _MGA_AXIS_EUROPE_EXTENT["lat"]
    europe = world.cx[minx:maxx, miny:maxy].copy()
    europe["region"] = europe["ISO_A2_EH"].map(iso_to_region)

    map_ax = ax.inset_axes([x0, y0, w, h])
    europe.plot(ax=map_ax, color="#f2f2f2", edgecolor="#B0B0B0", linewidth=0.4)
    for region, color in _MGA_AXIS_REGION_COLOR.items():
        sub = europe[europe["region"] == region]
        if sub.empty:
            continue
        sub.plot(ax=map_ax, color=color, edgecolor="white", linewidth=0.3)
        # representative_point() (unlike centroid) is guaranteed to fall
        # INSIDE the region's own dissolved shape — needed since a region's
        # union of countries is often multi-part/concave (islands, fjords),
        # where a plain centroid can land in the sea or a neighboring gap.
        label_point = sub.geometry.union_all().representative_point()
        map_ax.text(label_point.x, label_point.y, region[0].upper(),
                     fontsize=8, ha="center", va="center", color="white", fontweight="bold")
    map_ax.set_xlim(minx, maxx)
    map_ax.set_ylim(miny, maxy)
    map_ax.set_axis_off()
    return True


def _mga_axis_count(ax, x: float, y: float, text: str) -> None:
    ax.text(x, y, text, fontsize=13.5, fontweight="bold", color=_ETH_BLUE, ha="center", va="center")


def fig13_mga_axis_construction() -> None:
    """Conceptual, non-data schematic of how the NUMBER of candidate MGA
    axes grows as dimensions are crossed: 3 technology-group axes alone (1)
    -> x 4 regions (2, the common spatial extension) -> x 3 cumulative-to-
    year horizons too (3, this work's full 3-way crossing). See the
    module-level comment above for the visual grammar and data sources.
    """
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 6))
    for ax in (ax1, ax2, ax3):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")

    # ── 1: technology-group axes ──────────────────────────────────────────
    ax1.set_title("1. Technology (Group) Axes", fontsize=11.5, fontweight="bold")
    for i, group in enumerate(_MGA_AXIS_GROUPS):
        cx = 1.9 + i * 3.1
        ax1.add_patch(FancyBboxPatch((cx - 1.25, 4.9), 2.5, 3.1, boxstyle="round,pad=0.02,rounding_size=0.1",
                                      facecolor=eth_tint(_ETH_GREY, 0.9), edgecolor=_ETH_GREY, linewidth=1.2, zorder=2))
        _mga_group_icon(ax1, cx, 6.9, group, 1500, "#333333")
        ax1.text(cx, 5.4, _MGA_AXIS_GROUP_LABEL[group], fontsize=10, fontweight="bold", ha="center", va="center")
    _mga_axis_count(ax1, 5, 2.6, "3 axes")
    ax1.text(5, 1.55, "one axis per technology group",
              fontsize=8.3, style="italic", color="#555555", ha="center", va="top")

    # ── 2: + regional axes — crossed with 4 regions ─────────────────────
    ax2.set_title("2. + Regional Axes", fontsize=11.5, fontweight="bold")
    if not _mga_region_map(ax2, 0.02, 0.32, 0.42, 0.60):
        _mga_region_compass(ax2, 2.1, 6.9, 1.9)
    # Grid of region x group cells: each cell IS one candidate axis, colored
    # by region with that row's group pictogram drawn directly inside it
    # (white, for contrast) — no separate row-header icon/text and no "x"
    # symbol, since the grid itself already reads as "regions crossed with
    # groups" without needing either.
    grid_x0, grid_y0, cell_w, cell_h = 5.1, 5.35, 1.1, 1.15
    for row, group in enumerate(_MGA_AXIS_GROUPS):
        gy = grid_y0 + (len(_MGA_AXIS_GROUPS) - 1 - row) * cell_h
        for col, region in enumerate(_MGA_AXIS_REGIONS):
            gx = grid_x0 + col * cell_w
            ax2.add_patch(Rectangle((gx, gy), cell_w * 0.85, cell_h * 0.85,
                                     facecolor=_MGA_AXIS_REGION_COLOR[region], edgecolor="white",
                                     linewidth=0.8, zorder=3))
            _mga_group_icon(ax2, gx + cell_w * 0.425, gy + cell_h * 0.425, group, 220, "white")
    for col, region in enumerate(_MGA_AXIS_REGIONS):
        ax2.text(grid_x0 + col * cell_w + cell_w * 0.425, grid_y0 - 0.25, region[0].upper(),
                  fontsize=7.5, ha="center", va="top", fontweight="bold", color=_MGA_AXIS_REGION_COLOR[region])
    _mga_axis_count(ax2, 5, 2.6, "4 $\\times$ 3 = 12 axes")
    ax2.text(5, 1.55, "one axis per (region, technology group)",
              fontsize=8.3, style="italic", color="#555555", ha="center", va="top")

    # ── 3: + temporal axes (this work) — the full 3-way crossing ─────────
    # Region x group x horizon, all on one chart (no separate map here —
    # region identity is carried by line/marker color instead): 4 regions x
    # 3 groups = 12 curves, each sampled (marker) at the 3 config_mga_axes_
    # capex_cum.json until_years -> 4 x 3 x 3 = 36 points/axes total.
    ax3.set_title("3. + Temporal Axes (this work)", fontsize=11.5, fontweight="bold")
    cx0, cy0, cx1, cy1 = 1.3, 3.9, 9.5, 9.1
    ax3.annotate("", xy=(cx1, cy0), xytext=(cx0, cy0),
                 arrowprops=dict(arrowstyle="-|>", color="black", linewidth=1.1))
    ax3.annotate("", xy=(cx0, cy1), xytext=(cx0, cy0),
                 arrowprops=dict(arrowstyle="-|>", color="black", linewidth=1.1))
    ax3.text((cx0 + cx1) / 2, cy0 - 0.55, "year", fontsize=7.5, color="#555555", ha="center", va="top")
    ax3.text(cx0 - 0.45, (cy0 + cy1) / 2, "cumulative CAPEX", fontsize=7.5, color="#555555",
              ha="center", va="center", rotation=90)
    until_years = [2030, 2040, 2050]
    year_x = {yr: cx0 + (yr - 2020) / 30 * (cx1 - cx0) for yr in (2020, *until_years)}
    for yr in until_years:
        ax3.plot([year_x[yr], year_x[yr]], [cy0, cy1 - 0.1], color="#B0B0B0", linestyle=":",
                  linewidth=0.9, zorder=1)
        ax3.text(year_x[yr], cy0 - 0.15, str(yr), fontsize=6.5, ha="center", va="top", color="#555555")

    # Real trends, hand-picked (not solved): total 2050 cumulative investment
    # is highest in west, similar-but-not-identical in north/south, lowest
    # in east — so regions clearly differ by 2050 rather than converging.
    # Within each region, power ramps up earliest (already cheap today),
    # hydrogen mid-late, carbon (DAC/CCS) latest and slowest to scale — same
    # story fig6_diffusion_mechanisms/fig9_heat_supply_trajectory tell for
    # this project's actual technology diffusion.
    region_total_2050 = {"west": 10.0, "north": 6.0, "south": 5.0, "east": 3.0}
    group_share = {"power": 0.5, "hydrogen": 0.3, "carbon": 0.2}
    group_growth_k = {"power": 4.0, "hydrogen": 2.2, "carbon": 1.1}
    # Scale to the tallest SINGLE (region, group) curve (west's power share),
    # not the tallest region TOTAL — the latter is never actually reached by
    # any one line (each region's total is split across 3 curves), which
    # left every curve stuck in the chart's lower half.
    max_series_final = max(region_total_2050[r] * group_share[g]
                            for r in _MGA_AXIS_REGIONS for g in _MGA_AXIS_GROUPS)
    y_scale = (cy1 - cy0 - 0.3) / max_series_final
    # Only the 4 actual points (2020 start + the 3 until_years) — ax.plot
    # already draws straight segments between consecutive points, so NOT
    # densely sampling t is what keeps these as literal linear segments
    # rather than a smoothed/interpolated curve.
    sample_years = [2020, *until_years]
    for region in _MGA_AXIS_REGIONS:
        for group in _MGA_AXIS_GROUPS:
            final = region_total_2050[region] * group_share[group]
            k = group_growth_k[group]
            xs, ys = [], []
            for yr in sample_years:
                ti = (yr - 2020) / 30
                yi = cy0 + 0.10 + final * y_scale * (1 - np.exp(-k * ti)) / (1 - np.exp(-k))
                xs.append(year_x[yr])
                ys.append(yi)
            ax3.plot(xs, ys, color=_MGA_AXIS_REGION_COLOR[region], linestyle=_MGA_AXIS_GROUP_LINESTYLE[group],
                      linewidth=1.4, alpha=0.9, zorder=2)
            ax3.scatter(xs[1:], ys[1:], marker=_MGA_AXIS_GROUP_MARKER[group], s=75,
                        color=_MGA_AXIS_REGION_COLOR[region], edgecolor="black", linewidth=0.4, zorder=4)

    # One combined legend (region = color, group = marker/linestyle), 2
    # columns, single opaque box — two separate legend boxes here read as
    # cluttered; one box top-left, inside the chart, does not.
    region_handles = [Line2D([0], [0], color=_MGA_AXIS_REGION_COLOR[r], lw=2.5, label=r.capitalize())
                       for r in _MGA_AXIS_REGIONS]
    group_handles = [Line2D([0], [0], color="black", lw=1.2, linestyle=_MGA_AXIS_GROUP_LINESTYLE[g],
                             marker=_MGA_AXIS_GROUP_MARKER[g], markersize=8,
                             label=_MGA_AXIS_GROUP_LABEL[g]) for g in _MGA_AXIS_GROUPS]
    ax3.legend(handles=region_handles + group_handles, loc="upper left", fontsize=7, frameon=True,
               facecolor="white", framealpha=0.92, edgecolor="none", ncol=2, columnspacing=1.2,
               handletextpad=0.6, bbox_to_anchor=(0.01, 0.99))

    _mga_axis_count(ax3, 5, 2.6, "4 $\\times$ 3 $\\times$ 3 = 36 axes")
    ax3.text(5, 1.55, "one axis per (region, technology group, cumulative-to-year)",
              fontsize=8.3, style="italic", color="#555555", ha="center", va="top")

    fig.tight_layout(rect=[0, 0.02, 1, 0.97])
    savefig(fig, "fig7_mga_axis_construction", subdir="method")


def fig14_mga_exploration_sequence() -> None:
    """Companion to fig11 (method/fig5): the SAME toy near-optimal space
    (see _MGA_* geometry comments above fig11), but instead of a
    mid-exploration snapshot, shows the FULL sequence of directional solves
    a gap-greedy IO/AO algorithm would actually run, as 5 small-multiple
    panels (one per solve) so the growing inner hull is visible step by
    step.

    Per pyoNearOpt's actual direction-selection logic (see
    near_optimal_tools/src/pyoNearOpt/exploration_methods/
    shared_direction_oracle.py's ``sample_separation``/``_support_gap_from_state``,
    and bbo_ORACLE.py's ``find_best_direction``/``gap_objective``): the next
    direction queried is whichever maximises h_out(d) - h_in(d), the gap
    between the OUTER approximation's support function and the support
    function of the CURRENT INNER approximation (the convex hull of points
    found so far) - h_in(d) is evaluated over the hull, not over z* alone.
    So each arrow below is drawn from the point on the hull found so far
    that is extremal in the new direction, NOT always from z* - only solve 1
    is anchored at z* itself, since the hull is nothing but {z*} at that
    point. Anchors below (z*, v_bulge, v_bulge, v3, v4) were found by taking
    the dot product of each candidate hull vertex with that step's target
    direction and keeping the largest, exactly mirroring h_in(d)'s argmax.
    """
    z_star = (0.0, 0.0)
    v2, v3, v4, v5 = (2.6, -0.3), (3.4, 1.6), (1.8, 3.0), (-0.6, 1.8)
    v_bulge = (3.6, 3.3)
    true_space = [z_star, v2, v3, v_bulge, v4, v5]

    # (anchor, target) per solve - anchor is the CURRENT hull's extremal
    # vertex toward target, per the argmax described above; target is the
    # true_space vertex that solve reveals.
    steps = [
        (z_star, v_bulge),
        (v_bulge, v3),
        (v_bulge, v4),
        (v3, v2),
        (v4, v5),
    ]
    # Cyclic (true_space-consistent) vertex order of the hull AFTER each
    # solve, so Polygon always gets a non-self-intersecting vertex order -
    # every hull here is a subset of true_space's own vertices, so it can
    # only ever need true_space's own cyclic order, just skipping whichever
    # vertices aren't found yet.
    hulls_after = [
        [z_star, v_bulge],
        [z_star, v3, v_bulge],
        [z_star, v3, v_bulge, v4],
        [z_star, v2, v3, v_bulge, v4],
        [z_star, v2, v3, v_bulge, v4, v5],
    ]

    xs, ys = zip(*true_space)
    xlim, ylim = (min(xs) - 0.9, max(xs) + 0.9), (min(ys) - 0.8, max(ys) + 0.8)

    fig, axes = plt.subplots(1, 5, figsize=(15.5, 4.7))
    for i, (ax, (anchor, target), hull_after) in enumerate(zip(axes, steps, hulls_after), start=1):
        hull_before = hulls_after[i - 2] if i > 1 else [z_star]

        ax.add_patch(Rectangle((min(xs), min(ys)), max(xs) - min(xs), max(ys) - min(ys),
                                facecolor="none", edgecolor=_ETH_RED, linestyle="--", linewidth=1.0, zorder=1))
        ax.add_patch(Polygon(true_space, closed=True, facecolor="none",
                              edgecolor=_ETH_GREY, linestyle=":", linewidth=1.0, zorder=2))

        # The hull already found entering this solve - the base the new
        # arrow extends FROM. 2 points can't fill an area (drawn as a
        # line instead); 1 point (only z*, solve 1 only) needs nothing.
        if len(hull_before) >= 3:
            ax.add_patch(Polygon(hull_before, closed=True, facecolor=eth_tint(_ETH_BLUE, 0.55),
                                  edgecolor=_ETH_BLUE, linewidth=1.4, zorder=3))
        elif len(hull_before) == 2:
            bx, by = zip(*hull_before)
            ax.plot(bx, by, color=_ETH_BLUE, linewidth=2.2, zorder=3)

        ax.annotate("", xy=target, xytext=anchor,
                     arrowprops=dict(arrowstyle="-|>", color=_ETH_BLUE, linewidth=1.8, mutation_scale=15),
                     zorder=5)

        for p in hull_before:
            if p == z_star:
                continue
            ax.plot(*p, "o", color=_ETH_BLUE, markersize=6, zorder=6)
        # New vertex this solve: black-ringed so it visually pops against
        # the already-known (plain blue) points.
        ax.plot(*target, "o", color=_ETH_BLUE, markersize=8,
                 markeredgecolor="black", markeredgewidth=1.1, zorder=7)
        # Still-undiscovered true_space vertices: hollow, same convention as
        # fig11's "unexplored" markers.
        for p in true_space:
            if p != z_star and p not in hull_after:
                ax.plot(*p, "o", markerfacecolor="white", markeredgecolor=_ETH_GREY, markersize=6, zorder=6)
        ax.plot(*z_star, "o", color=_ETH_RED, markersize=7, zorder=8)
        if i == 1:
            ax.annotate("$z^*$", xy=z_star, xytext=(z_star[0] + 0.1, z_star[1] - 0.55),
                         fontsize=9, ha="left", va="top",
                         arrowprops=dict(arrowstyle="-", color=_ETH_RED, linewidth=0.8))

        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"Solve {i}", fontsize=10.5, fontweight="bold")
        ax.set_aspect("equal")
        for spine in ax.spines.values():
            spine.set_visible(False)

    fig.subplots_adjust(left=0.02, right=0.98, top=0.80, bottom=0.32, wspace=0.15)
    fig.suptitle("The Full MGA Exploration Sequence", fontsize=12.5, fontweight="bold", y=0.95)
    fig.legend(handles=[
        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=_ETH_RED, markeredgecolor=_ETH_RED,
                   markersize=7, label="$z^*$"),
        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=_ETH_BLUE, markeredgecolor="black",
                   markeredgewidth=1.1, markersize=8, label="vertex found this solve"),
        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor="white", markeredgecolor=_ETH_GREY,
                   markersize=6, label="not yet explored"),
        Patch(facecolor=eth_tint(_ETH_BLUE, 0.55), edgecolor=_ETH_BLUE, label="inner approx. found so far"),
        Patch(facecolor="none", edgecolor=_ETH_GREY, linestyle=":", label="true near-optimal space (unknown until fully explored)"),
        Patch(facecolor="none", edgecolor=_ETH_RED, linestyle="--", label="outer approx. (fixed bounding box)"),
    ], loc="upper center", ncol=2, fontsize=8.3, frameon=False, bbox_to_anchor=(0.5, 0.235),
        columnspacing=1.4, labelspacing=0.7)
    fig.text(0.5, 0.045, "each arrow starts at the point on the hull found so far that is extremal toward the\n"
                          "new direction (not always z*) and ends at the new vertex it reveals",
              fontsize=8.3, style="italic", color="#555555", ha="center", va="center")

    savefig(fig, "fig8_mga_exploration_sequence", subdir="method")


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"Loading {len(SCENARIOS)} euler scenarios...")
    runs = load_scenarios()
    print("Computing headline metrics (cost, emissions, capacity)...")
    metrics = compute_headline_metrics(runs)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(FIGURES_DIR / "headline_metrics.csv")
    print(f"  wrote {(FIGURES_DIR / 'headline_metrics.csv').relative_to(REPO_ROOT)}")

    print(f"Loading base scenario ({BASE_SCENARIO[1]})...")
    base_run = load_base_scenario()

    print("Generating figures...")
    if base_run is not None:
        components_with_base = compute_cost_components([base_run] + runs)
        fig0a_cost_composition(components_with_base)
        if any(r.label == "No flexibility" for r in runs):
            no_flex_run = by_label(runs, "No flexibility")
            fig5_retrofit_ccs_comparison(no_flex_run, base_run)
            # RQ1 ("how does industry-heat integration reshape the optimal
            # configuration") delta figures — only need base + No flexibility.
            fig12_capacity_and_storage_base_and_delta(base_run, no_flex_run)
            fig13_regional_capacity_delta_map(base_run, no_flex_run)
            if any(r.label == "Full flexibility" for r in runs):
                full_run = by_label(runs, "Full flexibility")
                fig0b_emissions_source_comparison(base_run, no_flex_run, full_run)
                fig1b_cost_and_emissions_totals(base_run, no_flex_run, full_run)
                fig10_power_and_storage_impact(base_run, no_flex_run, full_run)
                fig11_power_and_storage_impact_with_dsm(base_run, no_flex_run, full_run)
            else:
                print("  skipping fig0b_emissions_source_comparison/fig1b_cost_and_emissions_totals/"
                      "fig10/fig11_power_and_storage_impact: 'Full flexibility' scenario not loaded")
        else:
            print("  skipping fig0b/fig5/fig10/fig11/fig12/fig13: 'No flexibility' scenario not loaded")
    else:
        print(f"  skipping fig0a/fig0b/fig5/fig10/fig11/fig12/fig13: "
              f"{BASE_SCENARIO[0]} not yet under {EULER_ROOT}")
    fig1a_cost_delta(metrics)
    fig1b_industry_capacity(runs)
    fig2_dsm_cycles_by_product(runs)
    if any(r.label == "Single temperature level" for r in runs):
        fig3b_heat_pathway(runs)
        # fig14a/fig14b: Full flexibility vs. Single temperature level — no
        # base run needed (both are v9_0 runs).
        if any(r.label == "Full flexibility" for r in runs):
            full_flex_run = by_label(runs, "Full flexibility")
            single_temp_run = by_label(runs, "Single temperature level")
            fig14a_heat_supply_output_full_vs_single(runs)
            fig14b_cost_and_emissions_totals_full_vs_single(full_flex_run, single_temp_run)
        else:
            print("  skipping fig14a/fig14b: 'Full flexibility' scenario not loaded")
    else:
        print("  skipping fig3b_heat_pathway/fig14a/fig14b: "
              "'Single temperature level' scenario not loaded")
    fig4a_heat_demand_by_sector()
    fig4b_industry_fuel_demand_comparison(runs)
    if any(r.label == "No flexibility" for r in runs):
        fig6_diffusion_mechanisms(runs)
        fig7_heat_supply_trajectory(runs)
    else:
        print("  skipping fig6_diffusion_mechanisms/fig7_heat_supply_trajectory: 'No flexibility' scenario not loaded")
    if any(r.label == "Full flexibility" for r in runs):
        fig7_heat_supply_trajectory_for(runs, "Full flexibility",
                                         "fig9b_heat_supply_trajectory_full_flexibility")
    else:
        print("  skipping fig9b_heat_supply_trajectory_full_flexibility: 'Full flexibility' scenario not loaded")
    fig8_industry_sector_emissions_context()
    fig9_model_scope_coverage()
    fig15_global_ghg_sector_breakdown()
    fig11_mga_method()
    fig12_lp_formulation()
    fig13_mga_axis_construction()
    fig14_mga_exploration_sequence()
    print(f"Done. Figures in {FIGURES_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
