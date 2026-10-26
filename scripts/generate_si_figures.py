"""Generate print-ready figures for the MT_report SI Results section.

As of 2026-10-12 the figures are generated from the zen-europe runs
(zen_europe_ind_heat_v1_*, current ZEN-garden output format), not the
ZEN-Europe v9_0 runs the history below describes; the previous figures are
in SI_results/archive/. zen-europe's per-sector industry techs/carriers are
aggregated back to the ZEN-Europe names at load time
(figure_settings.SectorAggregatedResults), and the hardcoded snapshot years
below are snapped to each run's modeled years in main() (_snap_years).
Scenarios that haven't been run yet are skipped, as before.

Covers the SI Results subsections in `MT_report_HG/Sections/03_SI.tex`
(`\\label{sec:si-results}`), across the 7
case-study scenarios in that section's Table~SIScenarios — 6
Crystal_Ball_HG_v7_0 euler runs (Full flexibility, No flexibility, DSM only,
TES only, Single temperature level, DSM pessimistic) plus the unmodified
"ZEN-Europe (base)" reference case (dataset `Crystal_Ball`, plain — no
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
fig4b_industry_fuel_demand_comparison, etc.) purely as stable internal identifiers
for cross-referencing in comments throughout this file; only the actual
output filename/folder (the savefig() call at the end of each function)
uses the new per-folder numbering — see each entry's "-> " below for where
it actually lands on disk.

SI_results/ (results; removed/superseded figures are kept in SI_results/archive/,
the zen-europe versions of removed ones in archive/zen_europe/):
  fig1_cost_composition (was fig0a)            — CAPEX/OPEX/carrier/carbon-cost breakdown of each v7_0
                                          scenario's cost increase vs ZEN-Europe base
  fig2_emissions_source_comparison (was fig0b) — Full flex vs ZEN-Europe base, year 2025: where the
                                          emissions increase comes from vs. only a modest cost delta
  fig5b_dsm_discharge_by_product        — annual DSM throughput per product: optimistic vs pessimistic
  fig6_heat_pathway (was fig3b)        — direct vs temp-conversion heat production, 2050
  fig7_retrofit_ccs_comparison (was fig5) — CO2 captured by retrofit-CCS technology, No flexibility vs ZEN-Europe base
  fig8a_diffusion_mechanisms_heat_pumps — technology-diffusion limit decomposition for the industry heat pumps
  fig9_heat_supply_trajectory_noflex_vs_fullflex — industry heat output / capacity stock / capacity
                                          additions over every modeled year, No flexibility (left) next
                                          to Full flexibility (right); replaces the former fig9 + fig9b
  fig15a_heat_supply_output_no_flexibility_twh — standalone copy of fig9's top ("Industry heat
                                          supply") panel only, in TWh
  fig15b_heat_supply_output_full_flexibility_twh — same as fig15a, for the Full flexibility scenario
  fig12_capacity_and_storage_base_and_delta — power generation capacity & storage annual energy
                                          discharged at 2030/2040/2050, as ZEN-Europe base (absolute
                                          stack) + a floating Δ No flexibility bar per year
  fig14a_heat_supply_electrification_singletemp_vs_full — "electrified" industry heat share (heat
                                          pump + electrode boiler, stacked) at 2030/2040/2050, as 2
                                          grouped-bar panels — one per model option (No flexibility /
                                          Full flexibility) — each contrasting that option's normal run
                                          (solid) against its single-temp-band counterpart (hatched); the
                                          combined total barely moves, but the HP/electrode-boiler split
                                          within it shifts sharply; only singletemp-vs-not is ever
                                          compared, never the 2 model options against each other
  fig14b_cost_emissions_totals_singletemp_vs_full — cost & emissions totals (_cost_and_emissions_totals)
                                          for 2 independent baselines side by side: No
                                          flexibility's own totals in grey vs. its single-temp
                                          counterpart's difference, and (separately) Full flexibility's
                                          own totals in grey vs. its single-temp counterpart's difference
  fig30_matrix                         — fig14b's 4 runs as a 2x2 matrix (flexibility x temperature
                                          resolution), 2x3 panels (cost, HP share / VRE, bulk storage
                                          discharge), cells shaded by value, with arrows from the
                                          cheapest cell (Full flexibility, 3 temp levels) giving each
                                          other cell's extra cost in % and bn EUR
  fig31_matrix_tsa                     — fig30 with 10 / 20 representative time steps as rows instead
                                          of temperature resolution, ETH green cells
  fig20_cost_breakdown_sector_industry_heating — total system cost drilled down sector ->
                                          industries -> low-temperature heat
  fig40_flex_scenarios                 — flexibility scenarios (DSM pessimistic/DSM only/TES only/
                                          No flexibility) as horizontal-bar differences to Full
                                          flexibility on fig30's 4 dimensions + DSM and TES discharge (2x3)
  fig41_flex_scenarios_table           — fig40's data as a heatmap table: absolute values, cells
                                          shaded by the difference to Full flexibility (per column)
  fig42_flex_decomposition             — fig40's data as steps No flexibility -> TES only / DSM only
                                          -> Full flexibility, per metric
  fig43_flex_scenarios_table_curtailment — fig41 transposed plus a 2050 curtailment row (derived:
                                          capacity * max_load - output, see _curtailment_twh)
  fig50_dsm_no_cost_vs_full_flex       — Full flexibility vs. DSM no cost (336 h) on fig43's metrics
                                          + cost excl. DSM storage cost; difference column shaded by %
  fig51_capacity_and_storage_dsm_no_cost_vs_full_flex — fig12 with Full flexibility as the absolute
                                          stack and a floating Δ DSM no cost (336 h) bar per year
  fig60_full_flex_20ts_vs_10ts         — fig50's table for Full flexibility 10 ts vs. 20 ts
                                          (fig43's metrics)
  fig61_capacity_and_storage_full_flex_20ts_vs_10ts — fig51 for Full flexibility 10 ts vs. 20 ts

SI_results/method/ (no results — methodological/context only; removed ones in archive/method/):
  fig2_industry_fuel_demand_comparison (was fig4b) — new-sector heat/fuel demand vs. pre-existing cement/steel fuel mix
  fig3_industry_sector_emissions_context (was fig8) — European industry CO2 emissions by
                                          subsector (JRC-IDEES-2023), colored by ZEN-Europe scope
  fig4_model_scope_coverage (was fig9)  — ZEN-Europe's (+ its industry-heat extension's) share of
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
  fig7_mga_axis_construction (was fig13) — conceptual, non-data schematic of the MGA axes:
                                          the real north/west/south/east map (left) and the
                                          region x metric axis matrix (investment cost, mobility /
                                          heating electrification, cum. emissions), stacked over the
                                          2030/2040/2050 cumulative-to-year horizons (right)
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

fig4b (now method/fig2) and fig8/fig9 (now method/fig3, method/fig4) live
in method/ because none of them plot a SOLVED MODEL RESULT: fig4b is an
input-vs-context comparison, and fig8/fig9 plot external JRC-IDEES-2023/
UNFCCC input data establishing ZEN-Europe's scope. fig11/fig13/fig14
(now method/fig5, fig7, fig8) are method figures by construction (see
below).

fig11 (method/fig5) is a pure method illustration: hand-picked, unitless 2D
geometry (no model run, no external data at all), generated unconditionally
in main() like fig8/fig9. It intentionally uses a toy feasible region (not
the model's actual 6-D MGA exploration space plotted in
data/outputs/figures/mga_tests/) so both axes can be labeled generically
("Variable A/B") for a textbook-style explainer, independent of which
specific technologies the real MGA runs explored.

fig13 (method/fig7), like fig11, is a pure method illustration with no
solved points: the region map on the left, and on the right one column per
region x one row per metric (investment cost, mobility electrification,
heating electrification, cumulative emissions), stacked three deep for the
2030/2040/2050 cumulative-to-year horizons. Region identity is always color
(same palette as the map), metric identity a pictogram in each cell. The map
pulls in geopandas + the cached Natural Earth shapefile in
data/naturalearth/ — it falls back to a hand-drawn 4-wedge compass if
geopandas or the shapefile aren't available, so it still generates
unconditionally in main() either way.

fig8 and fig9 plot real-world INPUT data (JRC-IDEES-2023 subsector
emissions; Mannhardt's documented 90.0% sector-coverage figure plus UNFCCC CRF
data via sector_emissions_2022.csv), not solved-model results — generated
unconditionally in main(), independent of which Euler runs are loaded. fig8's
JSON is produced by extract_industry_sector_emissions.py (run under
zen-creator-env, same env-split reason as extract_heat_demand_by_sector.py);
fig9 reads sector_emissions_2022.csv directly (a plain CSV, no openpyxl
needed) from the sibling ZEN-creator repo.

The planned "Emissions" subsection (fig3b) is intentionally NOT built as a
standalone comparison across the 6 v7_0 scenarios: their horizon-total
emissions only span ~2.3% of each other (headline_metrics.csv), so an
absolute-scale trajectory or decomposition just shows six overlapping lines/
bars. fig0b covers a single-scenario ("Full flexibility") emissions
comparison against ZEN-Europe base instead — see
fig0b_emissions_source_comparison's docstring — without a dedicated,
mostly-flat fig3b-only pairing.

"ZEN-Europe (base)" only feeds fig0a/0b. `load_base_scenario()` still skips
them gracefully (with a printed note) if Crystal_Ball_2025_10a_5a_interval_10ts/
isn't present under EULER_ROOT, but as of v7_0 it has converged and is loaded
normally. It's deliberately NOT a 7th entry in SCENARIOS below or
in any other figure: it has no industry heat/DSM/TES sector at all, so
capacity/utilization figures (3b, 5b)
would show a misleading 0 for it rather than a meaningful
absence. Cost and emissions totals, by contrast, are well-defined for any
run regardless of sector structure, which is what makes it fig0a/0b material.

CAUTION on fig0a's headline numbers (found while building it): each v7_0
scenario's cost increase vs ZEN-Europe base is NOT evenly spread across the
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
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import FancyArrow, FancyBboxPatch, Patch, Polygon, Rectangle, Wedge
from matplotlib.path import Path as MplPath
from matplotlib.lines import Line2D

from plots.figures_by_run import (
    BULK_STORAGE_TECHS,
    INDUSTRY_DSM_TECHS,
    INDUSTRY_HEAT_CARRIERS_ENERGY,
    INDUSTRY_HEAT_TECHS_BOILERS_HP,
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
    _discount_factors,
    INDUSTRY_HEATING_TECHS,
    INDUSTRY_TES_TECHS,
    get_capex_by_technology,
    get_opex_by_technology,
    get_emissions_by_carrier,
    get_emissions_by_technology,
    plot_stacked_bars,
)
from plots.figure_settings import (
    EULER_ROOT,
    HOURS_PER_YEAR,
    Run,
    SCENARIO_PALETTE,
    COLOR_MAP,
    _apply_shared_ylim,
    _text_color_for_bg,
    apply_font_mode,
    eth_tint,
    get_available_years,
    load_results,
)

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

# Thesis-consistent scenario order/labels (Table~SIScenarios) — matches the
# dashboard's own "Full Flexibility" label for this run (figure_settings.
# EULER_SCENARIO_LABELS; the dashboard separately labels the true
# "ZEN-Europe (base)" run "Baseline" — a different run from this one, not
# to be confused with each other despite the overlapping word). Order matches
# Table SIScenarios (excluding "ZEN-Europe (base)", handled separately via
# BASE_SCENARIO below) and figure_settings.EULER_SCENARIO_ORDER, so the same
# scenario gets the same SCENARIO_PALETTE slot 0-5 everywhere; slot 6 (grey)
# is reserved for "ZEN-Europe (base)" — see the module docstring for why it
# isn't a 7th entry here.
# zen-europe: "No flexibility" is the full-horizon run (parameters.csv task 50,
# 2022-2050, time steps per system.yaml). The other entries use the folder
# names those scenarios are expected to get and self-skip until run.
SCENARIOS = [
    ("zen_europe_ind_heat_v1_no_flexibility_2022_8a_4a_interval_10ts", "No flexibility"),
    ("zen_europe_ind_heat_v1_full_flexibility_2022_8a_4a_interval_10ts", "Full flexibility"),
    ("zen_europe_ind_heat_v1_DSM_pessimistic_2022_8a_4a_interval_10ts", "DSM pessimistic"),
    ("zen_europe_ind_heat_v1_DSM_only_2022_8a_4a_interval_10ts", "DSM only"),
    ("zen_europe_ind_heat_v1_TES_only_2022_8a_4a_interval_10ts", "TES only"),
    ("zen_europe_ind_heat_v1_full_flexibility_single_temp", "Single temperature level"),
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
BASE_SCENARIO = ("zen_europe_base", "ZEN-Europe (base)")

# Single-temperature-band counterpart of "No flexibility", loaded separately
# from SCENARIOS (like BASE_SCENARIO) since it isn't one of the 6 case-study
# scenarios in Table~SIScenarios — it exists purely so fig14a/fig14b can
# compare singletemp vs. not for BOTH model options (No flexibility and
# Full flexibility), not just Full flexibility as before, per user request.
NO_FLEX_SINGLE_TEMP_SCENARIO = (
    "zen_europe_ind_heat_v1_no_flexibility_single_temp_2022_8a_4a_interval_10ts",
    "No flexibility (single temp)")

# fig50 only: Full flexibility with all 10 *_DSM storage techs made (nearly)
# free (opex_specific_variable/capex_specific_storage energy 0.001) AND their
# energy_to_power_ratio_max raised to 336 h (was 2/48 h for 7 of them) —
# parameters.csv row 8. Loaded separately (like NO_FLEX_SINGLE_TEMP_SCENARIO)
# so it doesn't enter the flexibility-scenario figures or shift palette slots.
DSM_NO_COST_SCENARIO = ("zen_europe_ind_heat_v1_dsm_no_cost_2022_8a_4a_interval_10ts",
                        "DSM no cost (336 h)")

# fig31/fig60/fig61 only: Full flexibility / No flexibility with 20 instead of
# 10 representative time steps per year (parameters.csv row 9 for Full
# flexibility). Loaded separately like DSM_NO_COST_SCENARIO. If the No
# flexibility 20 ts run is missing, fig31 falls back to the 10 ts No
# flexibility run as a marked placeholder (see main()).
FULL_FLEX_20TS_SCENARIO = ("zen_europe_ind_heat_v1_full_flexibility_2022_8a_4a_interval_20ts",
                           "Full flexibility (20 ts)")
NO_FLEX_20TS_SCENARIO = ("zen_europe_ind_heat_v1_no_flexibility_2022_8a_4a_interval_20ts",
                         "No flexibility (20 ts)")


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


def load_no_flex_single_temp_scenario() -> Run | None:
    """Returns None (rather than raising) if the run hasn't landed yet. Not
    in SCENARIOS/load_scenarios() — see NO_FLEX_SINGLE_TEMP_SCENARIO."""
    folder, label = NO_FLEX_SINGLE_TEMP_SCENARIO
    try:
        results = load_results(EULER_ROOT, folder)
    except FileNotFoundError:
        return None
    # Color unused: fig14a/fig14b pick their own colors by hand (HP/e-boiler
    # share vs. singletemp-or-not), never r.color.
    return Run(name=folder, label=label, mode="euler", results=results,
               color=SCENARIO_PALETTE[0])


def load_dsm_no_cost_scenario() -> Run | None:
    """Returns None (rather than raising) if the run hasn't landed yet. Not
    in SCENARIOS/load_scenarios() — see DSM_NO_COST_SCENARIO."""
    folder, label = DSM_NO_COST_SCENARIO
    try:
        results = load_results(EULER_ROOT, folder)
    except FileNotFoundError:
        return None
    # Color unused: fig50 is a table with its own shading.
    return Run(name=folder, label=label, mode="euler", results=results,
               color=SCENARIO_PALETTE[1])


def load_extra_scenario(scenario: tuple[str, str]) -> Run | None:
    """Like load_dsm_no_cost_scenario for any (folder, label) outside
    SCENARIOS. Returns None if the run hasn't landed yet."""
    folder, label = scenario
    try:
        results = load_results(EULER_ROOT, folder)
    except FileNotFoundError:
        return None
    # Color unused: fig31/fig60 shade by value, fig61 by technology.
    return Run(name=folder, label=label, mode="euler", results=results,
               color=SCENARIO_PALETTE[1])


def _snap_years(wanted: list[int], available: list[int]) -> list[int]:
    """Map hardcoded snapshot years onto the years a run actually models:
    each to its nearest available year; if that collapses several onto the
    same year (short test horizons), use the last len(wanted) available ones."""
    snapped = list(dict.fromkeys(min(available, key=lambda a: abs(a - y)) for y in wanted))
    if len(snapped) < len(wanted) and len(available) > len(snapped):
        snapped = available[-len(wanted):]
    return snapped


def snap_snapshot_years(runs: list[Run]) -> None:
    """Rebind the module-level snapshot-year constants to the loaded runs'
    modeled years (common to all of them)."""
    global YEAR, COMPARISON_YEARS, SNAPSHOT_YEARS_POWER, FIG30_YEAR
    if not runs:
        return
    available = sorted(set.intersection(*(set(get_available_years(r.results)) for r in runs)))
    YEAR = _snap_years([YEAR], available)[0]
    COMPARISON_YEARS = _snap_years(COMPARISON_YEARS, available)
    SNAPSHOT_YEARS_POWER = _snap_years(SNAPSHOT_YEARS_POWER, available)
    FIG30_YEAR = _snap_years([FIG30_YEAR], available)[0]
    print(f"  snapshot years: YEAR={YEAR}, COMPARISON_YEARS={COMPARISON_YEARS}, "
          f"SNAPSHOT_YEARS_POWER={SNAPSHOT_YEARS_POWER}")


def by_label(runs: list[Run], label: str) -> Run:
    return next(r for r in runs if r.label == label)


def savefig(fig: plt.Figure, name: str, subdir: str | None = None, extra_artists=None) -> None:
    """subdir=None writes straight into FIGURES_DIR (SI_results/) as before;
    subdir="method" (or "archive") writes into that subfolder instead — see
    the module docstring's "Figure organization" note for which figures use
    which.

    extra_artists: pass any Legend created via ax.add_artist() (i.e. every
    legend after the first on a given axes) here. bbox_inches="tight"'s own
    tight-bbox pass only walks each axes' *current* ax.legend_, so a second
    legend added via add_artist is silently excluded from the sizing
    calculation — its content still renders but gets cropped off by the
    canvas bbox_inches="tight" computes. bbox_extra_artists is matplotlib's
    documented fix: it folds these into that same bbox calculation. Found via
    fig7_retrofit_ccs_comparison's two side-by-side (Scenario/Year) legends
    being clipped despite fitting comfortably within the figure's own size."""
    directory = FIGURES_DIR / subdir if subdir else FIGURES_DIR
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.svg"
    fig.savefig(path, bbox_inches="tight", bbox_extra_artists=extra_artists)
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
    """Decomposes each v7_0 scenario's cost increase vs ZEN-Europe base into
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
    others = others.drop(index="Single temperature level", errors="ignore")
    delta = others.subtract(baseline, axis=1)
    # Percentages are relative to "No flexibility" (first scenario), not the ZEN-Europe base.
    ref_label = SCENARIOS[0][1]
    ref_total_cost = others.loc[ref_label].sum()  # all 4 components, i.e. full net_present_cost

    fig, ax = plt.subplots(figsize=(11, 6.5))
    x = np.arange(len(delta))
    bottom_pos = np.zeros(len(delta))
    bottom_neg = np.zeros(len(delta))
    for (_, comp_label), color in zip(PLOTTED_COST_COMPONENTS, PLOTTED_COST_COMPONENT_COLORS):
        vals = delta[comp_label].to_numpy()
        bottoms = np.where(vals >= 0, bottom_pos, bottom_neg)
        ax.bar(x, vals, bottom=bottoms, label=comp_label, color=color, edgecolor="white")
        carrier_center = bottoms + vals / 2  # last plotted component = carrier (brown)
        bottom_pos += np.clip(vals, 0, None)
        bottom_neg += np.clip(vals, None, 0)
    totals = delta[[label for _, label in PLOTTED_COST_COMPONENTS]].sum(axis=1)
    pct_vs_ref = (totals - totals[ref_label]) / ref_total_cost * 100
    for xi, lbl, t, pct in zip(x, delta.index, carrier_center, pct_vs_ref):
        txt = "baseline" if lbl == ref_label else f"{pct:+.2f}%"
        ax.text(xi, t, txt, ha="center", va="center", fontsize=9, fontweight="bold",
                color="white", bbox=dict(boxstyle="round,pad=0.2", fc="black", ec="none", alpha=0.45))
    ax.axhline(totals[ref_label], color="black", linewidth=1.0, linestyle="--",
               label=f"{ref_label} (baseline for %)")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(delta.index, rotation=25, ha="right", fontsize=9)
    ax.set_ylabel(r"$\Delta$ discounted system cost vs ZEN-Europe base [MEUR]")
    ax.set_title("Non-Carbon Cost Increase vs ZEN-Europe Base\n(% labels relative to No flexibility)",
                 fontsize=12, fontweight="bold")
    ax.set_ylim(top=ax.get_ylim()[1] * 1.15)  # headroom so the legend clears the bars
    ax.legend(fontsize=9, frameon=True, facecolor="white", framealpha=0.9, loc="upper center", ncol=3)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig1_cost_composition")


# ── Print palettes (heat supply / production) ───────────────────────────────

_eth_tint = eth_tint  # alias -- eth_tint itself now lives in figure_settings.py


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


# ── 9: Heat-supply trajectory, No flexibility vs Full flexibility ──────────

def fig9_heat_supply_trajectory(no_flex_run: Run, full_run: Run) -> None:
    """Industry heat supply over every modeled year, No flexibility (left
    column) next to Full flexibility (right column), rows sharing their y
    axis: operated output (TWh), capacity stock (GW), capacity additions
    (GW/period). Replaces the former separate fig9 (No flexibility) and
    fig9b (Full flexibility). The mechanism notes below were written for the
    No flexibility case (ZEN-Europe v9_0 numbers).

    Middle row: capacity stock per period. Bottom row: capacity
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
    runs = [no_flex_run, full_run]
    panels = []
    for r in runs:
        years = get_available_years(r.results)
        panels.append([
            _stack_ordered(_output_annual_twh(r, INDUSTRY_HEAT_TECHS_BOILERS_HP), HEAT_SUPPLY_STACK_ORDER, years),
            _stack_ordered(get_capacity(r.results, INDUSTRY_HEAT_TECHS_BOILERS_HP, "power"),
                           HEAT_SUPPLY_STACK_ORDER, years),
            _stack_ordered(get_capacity_addition(r.results, INDUSTRY_HEAT_TECHS_BOILERS_HP, "power"),
                           HEAT_SUPPLY_STACK_ORDER, years),
        ])
    row_specs = [("Industry heat supply", "TWh supplied"),
                 ("Capacity (stock)", "GW"),
                 ("Capacity additions (new builds/period)", "GW added")]

    n_years = max(len(p[1].columns) for p in panels)
    fig, axes = plt.subplots(3, 2, figsize=(2 * (0.8 * n_years + 3), 16), sharey="row")
    with plt.rc_context({"hatch.linewidth": 0.5}):
        for col, (r, dfs) in enumerate(zip(runs, panels)):
            for row, (df, (title, ylabel)) in enumerate(zip(dfs, row_specs)):
                plot_stacked_bars(df, f"{title} - {r.label}", ylabel if col == 0 else "", axes[row, col],
                                  show_segment_labels=False, show_legend=(row == 0 and col == 1),
                                  color_map=HEAT_SUPPLY_COLOR_MAP, hatch_map=HEAT_SUPPLY_HATCH_MAP)
    for ax in axes.flat:
        plt.setp(ax.get_xticklabels(), rotation=0)
    fig.tight_layout()
    savefig(fig, "fig9_heat_supply_trajectory_noflex_vs_fullflex")


_TOTAL_CACHE: dict[tuple[int, str], pd.DataFrame] = {}


def _cached_total(results, component: str) -> pd.DataFrame:
    """results.get_total(component), memoized per Results object — several
    figures re-read the same large flow_conversion_* frames for the same run.
    Callers must not mutate the returned frame."""
    key = (id(results), component)
    if key not in _TOTAL_CACHE:
        _TOTAL_CACHE[key] = results.get_total(component)
    return _TOTAL_CACHE[key]


def _stack_ordered(df: pd.DataFrame, order: list[str], years: list[int] | None = None) -> pd.DataFrame:
    """Rows reordered bottom-to-top per `order` (techs not in it appended
    after, so nothing is dropped); columns restricted to `years` if given."""
    df = df.reindex([t for t in order if t in df.index] + [t for t in df.index if t not in order])
    return df if years is None else df[[y for y in years if y in df.columns]]


def _output_avg_gw(r: Run, techs: list[str]) -> pd.DataFrame:
    """Actual OPERATED output per tech, as average GW (flow_conversion_output
    summed over the year's hours / HOURS_PER_YEAR) — directly comparable to
    nameplate capacity GW, their ratio being that tech's implied capacity
    factor. Shared by fig9's top ("Industry heat supply") panel and fig14a's
    same-quantity scenario comparison."""
    flow_out = _cached_total(r.results, "flow_conversion_output")
    rows = {}
    for t in techs:
        if t not in flow_out.index.get_level_values("technology"):
            continue
        s = flow_out.xs(t, level="technology").sum(axis=0) / HOURS_PER_YEAR
        if (s.abs() > 1e-6).any():
            rows[t] = s
    return pd.DataFrame(rows).T if rows else pd.DataFrame()


def _output_annual_twh(r: Run, techs: list[str]) -> pd.DataFrame:
    """Same quantity as _output_avg_gw (actual OPERATED output), expressed as
    total annual energy in TWh (avg GW * HOURS_PER_YEAR / 1000) instead of an
    averaged-power rate — used by fig9's top row and fig15a/b."""
    return _output_avg_gw(r, techs) * HOURS_PER_YEAR / 1000


def fig15_heat_supply_output_twh_for(runs: list[Run], label: str, fig_name: str) -> None:
    """Standalone version of fig9's top ("Industry heat supply") row for a
    single scenario, in annual TWh (see _output_annual_twh). Parameterized
    over `label`/`fig_name` so the same panel can be produced for both "No flexibility" (fig15a) and "Full
    flexibility" (fig15b)."""
    r = by_label(runs, label)
    years = get_available_years(r.results)
    output_df = _stack_ordered(_output_annual_twh(r, INDUSTRY_HEAT_TECHS_BOILERS_HP),
                               HEAT_SUPPLY_STACK_ORDER, years)

    fig, ax = plt.subplots(1, 1, figsize=(0.8 * len(output_df.columns) + 3, 6))
    with plt.rc_context({"hatch.linewidth": 0.5}):
        plot_stacked_bars(output_df, f"Industry heat supply (TWh) - {label}",
                          "TWh supplied", ax, show_segment_labels=False, show_legend=True,
                          color_map=HEAT_SUPPLY_COLOR_MAP, hatch_map=HEAT_SUPPLY_HATCH_MAP)
    plt.setp(ax.get_xticklabels(), rotation=0)
    fig.tight_layout()
    savefig(fig, fig_name)


# fig14a-specific: one color per TEMPERATURE BAND, not per source — unlike
# HEAT_SUPPLY_COLOR_MAP (fig9/fig1b), which hues by source (water=blue vs.
# waste heat=turquoise) and tints by band, fig14a merges water and waste-heat
# into a single heat-pump color per band per user request, so the two
# same-temp segments read as one solid block instead of two shades. Bands
# get only a very slight tint step apart (user: "only very slightly") since
# the point is one shared color family, not a highlighted gradient.
_FIG14A_HP_COLOR_MAP = {
    "heat_pump_industry_150_200_water": _ETH_BLUE,
    "heat_pump_industry_150_200_waste_heat": _ETH_BLUE,
    "heat_pump_industry_100_150_water": _eth_tint(_ETH_BLUE, 0.15),
    "heat_pump_industry_100_150_waste_heat": _eth_tint(_ETH_BLUE, 0.15),
    "heat_pump_industry_0_100_water": _eth_tint(_ETH_BLUE, 0.30),
    "heat_pump_industry_0_100_waste_heat": _eth_tint(_ETH_BLUE, 0.30),
    "electrode_boiler_industry": _ETH_GREEN,
}
# Per-tech labels for the legend below — only the "electrified" subset
# (electrode boiler + all 6 heat-pump variants) appears here since those are
# the only techs fig14a stacks. Water/waste-heat variants of the same band
# share one label (they now also share a color, see _FIG14A_HP_COLOR_MAP),
# deduplicated when the legend is built.
_ELECTRIFIED_TECH_LABELS = {
    "electrode_boiler_industry": "Electrode boiler",
    "heat_pump_industry_150_200_water": r"HP 150-200$^\circ$C",
    "heat_pump_industry_150_200_waste_heat": r"HP 150-200$^\circ$C",
    "heat_pump_industry_100_150_water": r"HP 100-150$^\circ$C",
    "heat_pump_industry_100_150_waste_heat": r"HP 100-150$^\circ$C",
    "heat_pump_industry_0_100_water": r"HP 0-100$^\circ$C",
    "heat_pump_industry_0_100_waste_heat": r"HP 0-100$^\circ$C",
}


def _electrification_stack(r: Run) -> pd.DataFrame:
    """Per-TECH share of total industry heat output for the "electrified"
    subset (electrode boiler + every heat-pump temperature/source variant —
    the same techs, colors and stack order fig9's top panel uses via
    HEAT_SUPPLY_COLOR_MAP/HEAT_SUPPLY_STACK_ORDER), rather than
    _heat_supply_shares' 2 pre-aggregated categories — per user request, so
    fig14a's heat-pump segment shows each variant's own correct color
    instead of one flat blue. Indexed by year, columns in stack order
    (bottom to top)."""
    df = _output_avg_gw(r, INDUSTRY_HEAT_TECHS_BOILERS_HP)
    total = df.sum(axis=0)
    electrified = [t for t in df.index if t == "electrode_boiler_industry" or t.startswith("heat_pump")]
    shares = 100 * df.loc[electrified].div(total, axis=1)
    return _stack_ordered(shares, HEAT_SUPPLY_STACK_ORDER).T


def fig14a_heat_supply_electrification_singletemp_vs_full(no_flex_run: Run, no_flex_single_run: Run,
                                                           full_run: Run, single_run: Run) -> None:
    """Companion to fig14b. Plots the "electrified" share of total industry
    heat output — electrode boiler + every heat-pump variant, the
    technologies that draw on electricity rather than a fossil/biomass fuel
    — as a stacked bar, broken down by INDIVIDUAL tech (see
    _electrification_stack) but colored via _FIG14A_HP_COLOR_MAP: one color
    per heat-pump TEMPERATURE BAND (not per source), with water and
    waste-heat variants of the same band sharing that color so they read as
    one solid block, and only a very slight tint step between bands (per
    user request — this replaced an earlier version with 6 distinct
    per-source-and-band colors), at COMPARISON_YEARS' 3 snapshot years
    (2030/2040/2050) instead of the full 2020-2050 horizon, PLUS the
    non-electrified remainder (coal/oil/biomass/natural-gas/waste boilers,
    not broken out individually) stacked on top in grey ("Other heat
    carriers") so every bar reaches a full 100% rather than stopping at the
    electrified share with implicit blank space above — the boundary with
    that grey segment itself reads as the electrified total, without a
    numeric "XX%" label there, and no per-segment value labels either (both
    removed per user request). Instead, each bar gets its TOTAL heat-pump
    share (sum of the 3 temperature-band segments, excluding the electrode
    boiler and the grey remainder) labeled above it — per user request,
    replacing the old per-segment labels with the one number that actually
    matters for the comparison (an earlier version also showed the
    full-resolution-minus-single-temp delta above each year's pair; removed
    per user request to keep just the per-bar totals). Two
    panels, one per model option (No flexibility / Full flexibility); within each,
    every year has 2 adjacent bars — solid for that option's normal
    (multi-temp-band) run, thinly hatched ("/", hatch.linewidth 0.5 —
    lighter than fig3b_heat_pathway's own "//" so the texture cue doesn't
    compete visually with the tech-color fills; kept separate from
    HEAT_SUPPLY_HATCH_MAP's own per-tech hatch, which would otherwise
    collide with it) for its single-temp counterpart — so, per user
    instruction, the only comparison drawn is singletemp vs. not, never "No
    flexibility" against "Full flexibility" directly.

    The electrified total (readable as where the grey "Others" segment
    begins) is the headline finding: it is only mildly depressed by
    collapsing to a single temperature band
    (e.g. Full flexibility 2050: 99.3% -> 97.9%, barely 1.4pp) — total
    electrification of industry heat supply happens almost regardless of
    temperature-band resolution. What resolution actually controls is the
    MIX within that total: singletemp runs only ever have the 150-200 water/
    waste-heat variants (confirmed directly — see _electrification_stack's
    docstring), so their heat-pump color band collapses to 2 dark segments
    instead of 6 tinted ones, and electrode boiler (green) grows to fill the
    gap — see the previous line-chart version's docstring (git history) for
    the full 2020/2030/2040/2050 trajectory and mechanism.
    -> SI_results/fig14a_heat_supply_electrification_singletemp_vs_full.svg
    """
    groups = [("No flexibility", no_flex_run, no_flex_single_run),
              ("Full flexibility", full_run, single_run)]
    # Thin ("/" not "//", hatch.linewidth 0.5 not matplotlib's default 1.0)
    # per user request — the singletemp/full-res distinction should read as
    # a light texture cue, not compete visually with the tech-color fills.
    variants = [("Full resolution", -0.19, ""), ("Single temp", 0.19, "/")]
    OTHERS_LABEL = "Other heat carriers (fossil/biomass boilers)"

    # Sized to leave headroom above the 0-100% bars for the per-bar HP-total
    # label added below; y-ticks pinned to 0-100 (see ax.set_yticks below) so
    # that headroom carries no gridlines of its own and reads as label space.
    HP_LABEL_Y, YLIM_TOP = 103, 114
    LABEL_FONTSIZE = 11  # large enough per user request (was 6.5 for the old inline segment labels)

    fig, axes = plt.subplots(1, 2, figsize=(11, 6), sharey=True)
    x = np.arange(len(COMPARISON_YEARS))
    techs_present: list[str] = []
    with plt.rc_context({"hatch.linewidth": 0.5}):
        for ax, (title, base, single) in zip(axes, groups):
            dfs = {"Full resolution": _electrification_stack(base).loc[COMPARISON_YEARS],
                   "Single temp": _electrification_stack(single).loc[COMPARISON_YEARS]}
            for variant, dx, hatch in variants:
                df = dfs[variant].copy()
                techs_present += [t for t in df.columns if t not in techs_present]
                hp_cols = [c for c in df.columns if c.startswith("heat_pump")]
                hp_total = df[hp_cols].sum(axis=1).to_numpy()
                # Remainder (coal/oil/biomass/natural-gas/waste boilers, not
                # individually broken out) stacked on top in grey, so every
                # bar reaches a full 100% — per user request — rather than
                # stopping at the electrified share with implicit blank space.
                df[OTHERS_LABEL] = (100 - df.sum(axis=1)).clip(lower=0)
                bottom = np.zeros(len(COMPARISON_YEARS))
                for tech in df.columns:
                    vals = df[tech].to_numpy()
                    color = _ETH_GREY if tech == OTHERS_LABEL else _FIG14A_HP_COLOR_MAP[tech]
                    ax.bar(x + dx, vals, width=0.36, bottom=bottom, color=color,
                           hatch=hatch, edgecolor="white", zorder=2)
                    bottom += vals
                # Total heat-pump share (all 3 bands combined) above each bar
                # — the number that actually matters, replacing the old
                # per-segment inline labels.
                for xi, hp_val in zip(x, hp_total):
                    ax.text(xi + dx, HP_LABEL_Y, f"{hp_val:.0f}%", ha="center", va="bottom",
                            fontsize=LABEL_FONTSIZE, fontweight="bold")
            ax.set_title(title, fontsize=12, fontweight="bold")
            ax.set_xticks(x)
            ax.set_xticklabels(COMPARISON_YEARS)
            ax.set_xlabel("Year")
            ax.set_ylim(0, YLIM_TOP)
            ax.set_yticks(range(0, 101, 20))
            ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("Share of total industry heat output [%]")

    # Color legend follows HEAT_SUPPLY_STACK_ORDER (top-to-bottom, matching
    # the visual stack) over whichever techs actually appear in any of the 4
    # runs, with the grey "Others" remainder listed first (it sits above
    # everything else in the stack); hatch legend is separate, 2 entries,
    # since it encodes singletemp-or-not rather than technology. Water/
    # waste-heat variants of the same band share a label+color (see
    # _FIG14A_HP_COLOR_MAP), so dedupe by label to avoid two identical
    # legend entries per band.
    tech_order = [t for t in reversed(HEAT_SUPPLY_STACK_ORDER) if t in techs_present]
    legend_handles = [Patch(facecolor=_ETH_GREY, label=OTHERS_LABEL)]
    seen_labels: set[str] = set()
    for t in tech_order:
        label = _ELECTRIFIED_TECH_LABELS[t]
        if label in seen_labels:
            continue
        seen_labels.add(label)
        legend_handles.append(Patch(facecolor=_FIG14A_HP_COLOR_MAP[t], label=label))
    legend_handles += [
        Patch(facecolor="white", edgecolor="black", label="Full resolution"),
        Patch(facecolor="white", edgecolor="black", hatch="/", label="Single temp"),
    ]
    # Legend pulled closer to the plots (smaller reserved rect + bbox_to_anchor
    # nudged up from the figure's bottom edge) per user request — the previous
    # 0.18 reservation left more empty vertical space above the legend than
    # the legend itself needed.
    fig.legend(handles=legend_handles, loc="lower center", ncol=3, fontsize=8, bbox_to_anchor=(0.5, 0.02))
    fig.tight_layout(rect=[0, 0.12, 1, 1])
    savefig(fig, "fig14a_heat_supply_electrification_singletemp_vs_full")


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
# flexibility" and "ZEN-Europe (base)" (steel/cement/power-sector CCS
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
    flow_out = _cached_total(r, "flow_conversion_output")
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
    """CO2 actually captured (kt CO2eq) by each retrofit-CCS technology,
    "No flexibility" (v9_0) vs. "ZEN-Europe (base)", for 2030/2040/2050 —
    one axes, grouped bars (per tech: base 2030/2040/2050, then no-flex
    2030/2040/2050). See RETROFIT_CCS_TECHS above for which technologies
    count as "retrofit" and why DAC/carbon_storage/carbon_pipeline are
    excluded.

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
    years = [2030, 2040, 2050]
    year_alphas = [0.45, 0.7, 1.0]  # lighter = earlier year, full color = 2050

    dfs = {year: pd.DataFrame({label: _ccs_captured_by_tech(run.results, year) for label, run, _ in runs})
                   .reindex(RETROFIT_CCS_TECHS).fillna(0.0)
           for year in years}
    keep_techs = [t for t in RETROFIT_CCS_TECHS if any((dfs[y].loc[t].abs() > 1e-6).any() for y in years)]

    # 6 narrow bars per tech cluster: base 2030/2040/2050, gap, no-flex 2030/2040/2050.
    bar_w = 0.11
    pad = 0.02
    group_gap = 0.08
    unit = bar_w + pad
    raw_positions = np.array([0, 1, 2, 3, 4, 5], dtype=float)
    raw_positions[3:] += group_gap / unit
    raw_positions -= raw_positions.mean()
    offsets = raw_positions * unit

    x = np.arange(len(keep_techs))
    fig, ax = plt.subplots(figsize=(13, 5.5))
    for s, (label, _, color) in enumerate(runs):
        for j, (year, alpha) in enumerate(zip(years, year_alphas)):
            vals = dfs[year].loc[keep_techs, label].to_numpy()
            ax.bar(x + offsets[s * 3 + j], vals, bar_w, color=color, alpha=alpha, edgecolor="white", linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([RETROFIT_CCS_LABELS[t] for t in keep_techs], fontsize=8.5)
    ax.set_ylabel("CO$_2$ captured [ktCO$_2$eq]")
    ax.grid(axis="y", alpha=0.3)

    scenario_handles = [Patch(facecolor=color, alpha=1.0, label=label) for label, _, color in runs]
    year_handles = [Patch(facecolor="#555555", alpha=a, label=str(year)) for year, a in zip(years, year_alphas)]
    leg1 = ax.legend(handles=scenario_handles, fontsize=9, frameon=False,
                      loc="upper left", bbox_to_anchor=(1.01, 1.0), title="Scenario", title_fontsize=9)
    ax.add_artist(leg1)
    leg2 = ax.legend(handles=year_handles, fontsize=9, frameon=False,
                      loc="upper left", bbox_to_anchor=(1.01, 0.72), title="Year", title_fontsize=9)

    fig.suptitle("Retrofit Carbon-Capture: CO$_2$ Capture", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 0.8, 0.96])
    savefig(fig, "fig7_retrofit_ccs_comparison", extra_artists=[leg1, leg2])


# ── 5b: DSM throughput by product ─────────────────────────────────────────────

# ammonia_DSM/methanol_DSM store an energy carrier (GWh); the other 8
# INDUSTRY_DSM_TECHS store a mass carrier (kt-of-product) — confirmed via
# Results.get_unit() against a solved run.
DSM_ENERGY_CARRIER_TECHS = {"ammonia_DSM", "methanol_DSM"}


# Literature lower heating values used to express the two energy-carrier DSM
# products (ammonia, methanol — stored natively in GWh) in kt of product, so
# all 10 products share one unit in fig5b. 1 GWh / (MWh/t) = 1 kt.
DSM_LHV_MWH_PER_T = {"ammonia_DSM": 18.6 / 3.6,    # 18.6 MJ/kg
                     "methanol_DSM": 19.9 / 3.6}   # 19.9 MJ/kg


def fig5b_dsm_discharge_by_product(runs: list[Run]) -> None:
    # Companion to fig5: absolute annual DSM throughput per product over the
    # whole horizon, stacked by product, optimistic vs pessimistic. Charge and
    # discharge are identical (no storage losses), so only discharge is shown.
    # Products keep their ETH COLOR_MAP colors; ammonia/methanol are stored in
    # GWh and converted to kt via DSM_LHV_MWH_PER_T (hatched as in fig5 to
    # flag that they are LHV-derived).
    scenarios = ["Full flexibility", "DSM pessimistic"]
    titles = {"Full flexibility": "Optimistic (Full flexibility)",
              "DSM pessimistic": "Pessimistic (DSM pessimistic)"}
    pretty = lambda t: t.replace("_DSM", "").replace("_", " ")
    color_map = {pretty(t): COLOR_MAP[t] for t in INDUSTRY_DSM_TECHS}
    hatch_map = {pretty(t): "//" for t in DSM_ENERGY_CARRIER_TECHS}

    dfs = []
    for label in scenarios:
        r = by_label(runs, label).results
        df = get_storage_flows(r, INDUSTRY_DSM_TECHS, "flow_storage_discharge")
        years = get_available_years(r)
        df = df.reindex(columns=years).fillna(0.0)
        for t, mwh_per_t in DSM_LHV_MWH_PER_T.items():
            if t in df.index:
                df.loc[t] = df.loc[t] / mwh_per_t
        df.index = [pretty(t) for t in df.index]
        dfs.append(df)
    # Stack order: largest total over both scenarios at the bottom.
    order = pd.concat(dfs).groupby(level=0).sum().sum(axis=1).sort_values(ascending=False).index
    dfs = [d.reindex([t for t in order if t in d.index]) for d in dfs]

    fig, axes = plt.subplots(2, 1, figsize=(0.8 * len(dfs[0].columns) + 3, 11))
    with plt.rc_context({"hatch.linewidth": 0.5}):
        for i, (ax, df, label) in enumerate(zip(axes, dfs, scenarios)):
            plot_stacked_bars(df, f"DSM Charge/Discharge by Product - {titles[label]}",
                              "Annual charge = discharge (kt product)",
                              ax, show_segment_labels=False, show_legend=(i == 0),
                              color_map=color_map, hatch_map=hatch_map)
    _apply_shared_ylim(list(axes), dfs)
    for ax in axes:
        plt.setp(ax.get_xticklabels(), rotation=0)
        ax.set_ylabel(ax.get_ylabel(), fontsize=10)
    fig.tight_layout()
    savefig(fig, "fig5b_dsm_discharge_by_product")


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


# ── fig2 (method): industry energy input by carrier, all sectors ──────────

# The four industry-heat sectors, in bar order (top to bottom).
HEAT_DEMAND_SECTOR_LABELS = {"glass": "Glass", "ceramic": "Ceramic", "paper": "Paper", "food": "Food"}

# Carrier encoding (ETH palette only): one hue per carrier FAMILY, so the
# eye reads "heat / fuel / electricity" first and the individual carrier
# second. Heat bands (<200°C, supplied via heat_industry_* carriers) are
# tints of ETH red, darker = hotter; >200°C fuels (direct combustion, a
# different supply pathway) each get their own solid ETH color, with the
# consolidated blended "fuel to process" as a neutral light grey;
# electricity is ETH blue (drawio system-overview convention).
HEAT_DEMAND_BAND_LABELS = {"0_100": "0-100 °C", "100_150": "100-150 °C", "150_200": "150-200 °C"}
HEAT_BAND_COLORS = {"0_100": _eth_tint(_ETH_RED, 0.6), "100_150": _eth_tint(_ETH_RED, 0.3), "150_200": _ETH_RED}
FUEL_CARRIER_COLORS = {"natural_gas": _ETH_TURQUOISE, "hard_coal": _ETH_GREY, "oil": _ETH_BRONZE,
                       "biomass": _ETH_GREEN, "waste": _eth_tint(_ETH_GREEN, 0.5), "hydrogen": _ETH_PURPLE,
                       "fuel_to_process": _eth_tint(_ETH_GREY, 0.6)}
FUEL_CARRIER_LABELS = {"natural_gas": "Natural gas", "hard_coal": "Hard coal", "oil": "Oil", "biomass": "Biomass",
                       "waste": "Waste", "hydrogen": "Hydrogen", "fuel_to_process": "Natural gas\n(fuel shift possible)"}

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

# Electricity: not temperature-banded and not part of the >200°C fuel mix —
# every X_production tech has a fixed electricity input alongside both.
_ELECTRICITY_COLOR = _ETH_BLUE
_ELECTRICITY_LABEL = "Electricity"


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
    ("Cement (clinker)", ["cement_kiln"], _consolidate_series),
    ("Primary steel (BF-BOF/DRI)", ["BF_BOF", "NG_DRI", "H2_DRI"], _merge_dri_fuel),
    ("Secondary steel (EAF)", ["EAF"], None),
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
    flow_in = _cached_total(r, "flow_conversion_input")
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
    """Solved energy input by carrier for the four industry-heat sectors
    (glass/ceramic/paper/food) next to the pre-existing cement/steel sectors,
    so the new sectors' scale can be read against sectors already in the
    model. Every bar is the SAME source: the "No flexibility" ZEN-europe run's
    flow_conversion_input in its first modeled year (2022), as average GW.

    Horizontal stacked bars, one per sector: heat bands (red tints), then
    >200°C fuels (one solid color each), then electricity. Blended hub fuels
    (fuel_to_kiln/fuel_for_cement) and NG_DRI/H2_DRI's fuels are merged into
    one "Natural gas (fuel shift possible)" segment — see _consolidate_blended_fuel/
    _merge_dri_fuel and FIG4B_SECTOR_GROUPS' comment.
    """
    r = by_label(runs, "No flexibility").results
    year = get_available_years(r)[0]

    rows: list[tuple[str, pd.Series]] = []
    for s, label in HEAT_DEMAND_SECTOR_LABELS.items():
        rows.append((label, _consolidate_series(_tech_fuel_by_carrier(r, [f"{s}_production"], year))))
    n_new = len(rows)
    for label, techs, post in FIG4B_SECTOR_GROUPS:
        s = _tech_fuel_by_carrier(r, techs, year)
        rows.append((label, post(s) if post is not None else s))

    segments = ([(f"heat_industry_{b}", HEAT_BAND_COLORS[b]) for b in HEAT_BAND_COLORS]
                + [(c, FUEL_CARRIER_COLORS[c]) for c in FUEL_CARRIER_COLORS]
                + [("electricity", _ELECTRICITY_COLOR)])
    present = [(c, col) for c, col in segments if any(v.get(c, 0.0) > 0 for _, v in rows)]

    # One-row gap between the two groups, top to bottom.
    y = np.array([i if i < n_new else i + 1 for i in range(len(rows))], dtype=float)
    totals = np.array([sum(v.get(c, 0.0) for c, _ in present) for _, v in rows])
    min_label = 0.035 * totals.max()

    fig, ax = plt.subplots(figsize=(11, 5.6))
    left = np.zeros(len(rows))
    for carrier, color in present:
        vals = np.array([v.get(carrier, 0.0) for _, v in rows])
        ax.barh(y, vals, 0.62, left=left, color=color, edgecolor="white", linewidth=0.8)
        for yi, li, vi in zip(y, left, vals):
            if vi >= min_label:
                ax.text(li + vi / 2, yi, f"{vi:.1f}", ha="center", va="center", fontsize=7.5,
                        color=_text_color_for_bg(color))
        left += vals
    for yi, total in zip(y, totals):
        ax.text(total + 0.006 * totals.max(), yi, f"{total:.1f}", ha="left", va="center",
                fontsize=9, fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels([label for label, _ in rows], fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlim(0, totals.max() * 1.08)
    ax.axhline(n_new, color="black", linewidth=0.6, alpha=0.6)
    for y_text, text in ((-0.6, "Additional in extended model"), (n_new + 0.4, "Base model sectors")):
        ax.text(-0.01, y_text, text, transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=8.5, fontstyle="italic", color=_ETH_GREY)
    ax.set_ylim(len(rows) + 0.5, -1.0)

    ax.set_xlabel("Average energy input [GW]")
    ax.set_title(f"Industrial energy input by carrier in {year}", fontsize=12, fontweight="bold", loc="left", pad=20)
    ax.text(0, 1.015, "ZEN-europe without flexibility",
            transform=ax.transAxes, fontsize=9, color=_ETH_GREY, va="bottom")
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", alpha=0.3)
    ax.set_axisbelow(True)

    def header(text: str) -> Patch:
        return Patch(facecolor="none", edgecolor="none", label=text)

    present_carriers = {c for c, _ in present}
    headers = ["Heat (<200 °C)", "Other fuel"]
    handles = [header(headers[0])]
    handles += [Patch(facecolor=HEAT_BAND_COLORS[b], label=HEAT_DEMAND_BAND_LABELS[b])
                for b in HEAT_BAND_COLORS if f"heat_industry_{b}" in present_carriers]
    handles += [header(headers[1])]
    handles += [Patch(facecolor=FUEL_CARRIER_COLORS[c], label=FUEL_CARRIER_LABELS[c])
                for c in FUEL_CARRIER_COLORS if c in present_carriers]
    handles += [header(""), Patch(facecolor=_ELECTRICITY_COLOR, label=_ELECTRICITY_LABEL)]
    leg = ax.legend(handles=handles, fontsize=8.5, frameon=False, loc="upper right",
                    handlelength=1.4, handleheight=1.0, labelspacing=0.35)
    for t in leg.get_texts():
        if t.get_text() in headers:
            t.set_fontweight("bold")

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


# ── 8a: Same diffusion-limit decomposition, for the 6 industry heat pumps ──
# Built to diagnose the "0-100/100-150 °C HPs jump to full deployment in
# 2022" pattern. Finding (verified by reconstructing the constraint RHS
# exactly - HPs have no existing capacity and a zero unbounded floor, so
# unlike fig8's wind/PV case the reconstruction has no approximation and
# matches the solver to rounding wherever it binds, e.g. 150-200 °C: 0.65 GW
# in 2020 = 0.02 x 32.7 GW of boilers): the diffusion constraint itself is
# implemented as documented, but the MARKET-SHARE term for the 0-100 and
# 100-150 °C bands is fed by heat_industry_temp_conversion_100/150. Those
# share the HPs' reference carrier and conversion class, have capex=0 and
# max_diffusion_rate=inf, so their capacity is degenerate (any size is
# cost-free) and the solver returns 54,000-150,000 GW - ~5,000x their actual
# peak flow (~11-31 GW). 2% of that makes the HP constraint inactive from
# 2022 on. In 2020 temp-conversion has no existing capacity, so the same term
# is exactly 0 and the HPs are blocked - hence "nothing in 2020, everything
# economic in 2022". The size of the 2022 jump is then set by the waste-heat
# HPs' capacity_limit and by band demand, not by diffusion. The 150-200 °C
# band has a real boiler fleet as its peer group and is correctly
# diffusion-bound. Same loophole exists for natural_gas_to_kilnfuel vs. the
# electricity/hydrogen kiln-fuel techs (not plotted here).
DIFFUSION_HP_TECHS = [
    ("heat_pump_industry_0_100_waste_heat", "HP 0-100 °C (waste heat)", _ETH_BLUE),
    ("heat_pump_industry_0_100_water", "HP 0-100 °C (water)", _ETH_BLUE),
    ("heat_pump_industry_100_150_waste_heat", "HP 100-150 °C (waste heat)", _ETH_TURQUOISE),
    ("heat_pump_industry_100_150_water", "HP 100-150 °C (water)", _ETH_TURQUOISE),
    ("heat_pump_industry_150_200_waste_heat", "HP 150-200 °C (waste heat)", _ETH_RED),
    ("heat_pump_industry_150_200_water", "HP 150-200 °C (water)", _ETH_RED),
]


def _zero_cost_unlimited_techs(r) -> set[str]:
    """Conversion techs with capex_specific_conversion=0 AND
    max_diffusion_rate=inf - i.e. pure bookkeeping/pass-through techs whose
    installed capacity is cost-free and therefore degenerate (the solver may
    return any value >= peak flow). In this dataset: the 2 temp-conversion
    techs and natural_gas_to_kilnfuel."""
    capex = r.get_total("capex_specific_conversion").groupby(level="technology").mean().iloc[:, 0]
    mdr = r.get_total("max_diffusion_rate").iloc[:, 0]
    return {t for t, c in capex.items() if c == 0 and not np.isfinite(mdr.get(t, np.inf))}


def _market_share_term_split(r, tech: str, years: list[int]) -> tuple[pd.Series, pd.Series, list[str]]:
    """Same quantity as _market_share_term, split into (real peers, zero-cost/
    unlimited peers) so the degenerate-capacity contribution can be shown
    separately. Also returns the zero-cost peer names. Unlike
    _market_share_term, the peer set INCLUDES `tech` itself - matching
    technology.py, whose class set contains the technology's own
    capacity_previous (immaterial for fig8's wind/PV, not for a cold-start HP)."""
    msu = float(r.get_total("market_share_unbounded").iloc[0])
    ref_carriers = r.get_df("set_reference_carriers")
    peers = [t for t, c in ref_carriers.items() if c == ref_carriers.get(tech)]
    free = _zero_cost_unlimited_techs(r)
    real, artifact = pd.Series(0.0, index=years), pd.Series(0.0, index=years)
    for peer in peers:
        s = _series_by_tech(r, "capacity_previous", peer).reindex(years).fillna(0.0)
        if peer in free:
            artifact += s
        else:
            real += s
    return real * msu, artifact * msu, [p for p in peers if p in free]


def _peak_output_by_year(r, tech: str, years: list[int]) -> pd.Series:
    """Sum over nodes of each node's maximum hourly flow_conversion_output,
    per year: the capacity `tech` would need if it were sized to what it
    actually delivers (i.e. if its capacity were not cost-free/degenerate)."""
    fo = r.get_full_ts("flow_conversion_output")
    sub = fo[fo.index.get_level_values("technology") == tech]
    n = sub.shape[1] // len(years)
    assert n * len(years) == sub.shape[1], "full time series not evenly divisible into years"
    return pd.Series({y: float(sub.iloc[:, i * n:(i + 1) * n].max(axis=1).sum()) for i, y in enumerate(years)})


def fig8a_diffusion_mechanisms_heat_pumps(runs: list[Run]) -> None:
    """fig8's layout applied to the 6 industry heat pumps, "No flexibility".

    Row 1: installed capacity vs. capacity_limit (finite only for the
    waste-heat HPs - a waste-heat-source potential, not a diffusion bound).

    Row 2: actual capacity addition vs. the exact diffusion-limit RHS,
    stacked: knowledge/history term, market-share term from real peers
    (boilers, the HPs themselves) and market-share term from zero-cost/
    unlimited peers (temp-conversion - grey, hatched). The unbounded-addition
    floor is 0 for every HP and omitted. Bars above the y-limit are clipped
    and their range annotated (they are 100-1000x the axis). Dashed line, 0-
    150 °C bands only: the market-share term if temp-conversion were sized to
    its actual peak flow instead of its degenerate capacity - what the
    constraint would allow with a physically meaningful peer capacity.

    Row 3: annual heat output per temperature band (TWh) - shows the 0-100 °C
    band switching 100% from temp-conversion (cascaded boiler heat) to HPs
    within one period (2020 -> 2022). 150-200 °C output includes heat later
    cascaded down to the lower bands.

    See the module comment above DIFFUSION_HP_TECHS for the finding."""
    run = by_label(runs, "No flexibility")
    r = run.results
    years = get_available_years(r)
    msu = float(r.get_total("market_share_unbounded").iloc[0])
    xw = 1.6

    fig = plt.figure(figsize=(22, 13))
    gs = fig.add_gridspec(3, 6, height_ratios=[1, 1.15, 1], hspace=0.55, wspace=0.28)
    for col, (tech, label, color) in enumerate(DIFFUSION_HP_TECHS):
        installed = _series_by_tech(r, "capacity", tech).reindex(years).fillna(0.0)
        addition = _series_by_tech(r, "capacity_addition", tech).reindex(years).fillna(0.0)
        potential = _site_potential(r, tech)
        tint = 0.0 if "waste_heat" in tech else 0.35

        ax1 = fig.add_subplot(gs[0, col])
        ax1.bar(years, installed, width=xw, color=_eth_tint(color, tint),
                label="Installed capacity" if col == 0 else None)
        if np.isfinite(potential):
            ax1.axhline(potential, color=color, linestyle="--", linewidth=1.2,
                        label="capacity_limit" if col == 0 else None)
            ax1.set_title(f"{label}\n(capacity_limit: {potential:,.2f} GW)", fontsize=9.5)
        else:
            ax1.set_title(f"{label}\n(capacity_limit = inf)", fontsize=9.5)
        if col == 0:
            ax1.set_ylabel("Installed capacity [GW]")
            ax1.legend(fontsize=7.5, frameon=True, facecolor="white", framealpha=0.9,
                       edgecolor="none", loc="lower right")
        ax1.grid(axis="y", alpha=0.25)

        ax2 = fig.add_subplot(gs[1, col])
        knowledge = _knowledge_history_term(r, tech, years).reindex(years).fillna(0.0)
        real, artifact, free_peers = _market_share_term_split(r, tech, years)
        segments = [
            (knowledge.to_numpy(), "Knowledge/history term", _eth_tint(color, 0.05), None),
            (real.to_numpy(), "Market-share term: real peers", _eth_tint(color, 0.5), None),
            (artifact.to_numpy(), "Market-share term: zero-cost temp-conversion capacity",
             _eth_tint(_ETH_GREY, 0.55), "////"),
        ]
        stack_top = knowledge + real + artifact
        clipped = artifact.max() > 0
        ylim = (max(addition.max(), (knowledge + real).max()) * 1.6) if clipped else None
        bottom = np.zeros(len(years))
        with plt.rc_context({"hatch.linewidth": 0.5}):
            for vals, comp_label, comp_color, hatch in segments:
                ax2.bar(years, vals, width=xw, bottom=bottom, color=comp_color, hatch=hatch,
                        edgecolor="white", linewidth=0.4, label=comp_label if col in (0, 2) else None)
                bottom += vals
        ax2.plot(years, addition.to_numpy(), color="black", marker="o", markersize=3.5,
                 linewidth=1.2, label="Actual capacity addition" if col == 0 else None)
        if clipped:
            ax2.set_ylim(0, ylim)
            off = stack_top[stack_top > ylim]
            if not off.empty:
                ax2.text(0.97, 0.97,
                         f"bars off-scale from {off.index[0]}:\n{off.min():,.0f}-{off.max():,.0f} GW\n"
                         f"({artifact[off.index].sum() / off.sum():.1%} from {', '.join(free_peers)})",
                         transform=ax2.transAxes, ha="right", va="top", fontsize=7,
                         bbox=dict(facecolor="white", edgecolor="none", alpha=0.85))
            for peer in free_peers:
                peak = _peak_output_by_year(r, peer, years)
                hp_prev = (real / msu)  # real peers' capacity_previous
                ax2.plot(years, msu * (peak + hp_prev).to_numpy(), color=_ETH_GREY,
                         linestyle="--", linewidth=1.2,
                         label="Market-share term if temp-conversion\nsized to its actual peak flow"
                         if col == 0 else None)
        if col == 0:
            ax2.set_ylabel("Capacity added per period [GW]")
        ax2.set_xlabel("Year")
        ax2.grid(axis="y", alpha=0.25)
        if col == 0:
            row2_axes = [ax2]
        else:
            row2_axes.append(ax2)

    # One shared row-2 legend (collected across columns: the zero-cost
    # segment only exists for columns 0-3) placed between rows 2 and 3, so
    # it never covers the off-scale annotation.
    handles, labels = {}, []
    for ax in row2_axes:
        for h, lbl in zip(*ax.get_legend_handles_labels()):
            if lbl not in handles:
                handles[lbl] = h
                labels.append(lbl)
    fig.legend([handles[l] for l in labels], labels, loc="center", ncol=len(labels),
               bbox_to_anchor=(0.5, 0.345), fontsize=8, frameon=False)

    # Temp-conversion is (near-)lossless 1:1, so a band's own net heat =
    # supplier output minus the output of the temp-conversion tech that
    # passes heat on to the next-lower band. Without this, 2020's 100-150 °C
    # bar would also contain the 0-100 °C band's entire cascaded heat.
    band_specs = [
        ("0-100 °C", ["heat_industry_temp_conversion_100"], None,
         DIFFUSION_HP_TECHS[0:2], _ETH_BLUE),
        ("100-150 °C", ["heat_industry_temp_conversion_150"], "heat_industry_temp_conversion_100",
         DIFFUSION_HP_TECHS[2:4], _ETH_TURQUOISE),
        ("150-200 °C", [t for t in INDUSTRY_HEAT_TECHS_BOILERS_HP if "boiler" in t],
         "heat_industry_temp_conversion_150", DIFFUSION_HP_TECHS[4:6], _ETH_RED),
    ]
    for i, (band, other_techs, cascade_out, hp_specs, color) in enumerate(band_specs):
        ax3 = fig.add_subplot(gs[2, 2 * i:2 * i + 2])
        other = _output_annual_twh(run, other_techs).sum(axis=0).reindex(years).fillna(0.0)
        hps = _output_annual_twh(run, [t for t, _, _ in hp_specs]).reindex(
            [t for t, _, _ in hp_specs]).fillna(0.0)
        if cascade_out is not None:
            passed_on = _output_annual_twh(run, [cascade_out]).sum(axis=0).reindex(years).fillna(0.0)
            # Attribute the passed-on heat to the non-HP supplier first (HPs
            # are 100% of a band's net output only if they exceed it).
            other = (other - passed_on).clip(lower=0.0)
        other_label = "Temp-conversion (cascaded boiler heat)" if i < 2 else "Boilers (all fuels)"
        ax3.bar(years, other, width=xw, color=_eth_tint(_ETH_GREY, 0.55), label=other_label)
        bottom = other.to_numpy().copy()
        for t, lbl, _ in hp_specs:
            vals = hps.loc[t].reindex(years).fillna(0.0).to_numpy() if t in hps.index else np.zeros(len(years))
            ax3.bar(years, vals, width=xw, bottom=bottom,
                    color=_eth_tint(color, 0.0 if "waste_heat" in t else 0.35), label=lbl)
            bottom += vals
        ax3.set_title(f"Annual heat output, {band} band"
                      + (" (net of heat cascaded to lower bands)" if cascade_out else ""), fontsize=9.5)
        if i == 0:
            ax3.set_ylabel("Heat output [TWh/yr]")
        ax3.set_xlabel("Year")
        ax3.legend(fontsize=7, frameon=True, facecolor="white", framealpha=0.9,
                   edgecolor="none", loc="upper right")
        ax3.grid(axis="y", alpha=0.25)

    fig.suptitle("Technology-Diffusion Limit for Industrial Heat Pumps\n"
                 f"No flexibility, {years[0]}-{years[-1]} - row 2 is the exact diffusion-limit RHS "
                 "(no approximation: HPs have no existing capacity)", fontsize=12.5)
    fig.text(0.5, 0.035,
             "Temp-conversion techs have capex = 0 and max_diffusion_rate = inf, so their capacity is "
             "degenerate (~5,000x peak flow). Because they share the 0-100/100-150 °C HPs' reference "
             "carrier, 2% of that capacity enters the HPs' market-share term and makes the diffusion "
             "limit non-binding from 2022 on.",
             ha="center", va="bottom", fontsize=8, style="italic", color="#555555", wrap=True)
    savefig(fig, "fig8a_diffusion_mechanisms_heat_pumps")


# ── 0b: Emissions-source comparison, Full flexibility vs ZEN-Europe base ──

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
    "ZEN-Europe (base)" being much larger (proportionally) than the cost
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
    is petrol/turquoise elsewhere (fig11 etc. never key off
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

    Root cause of the gap itself: "ZEN-Europe (base)" has NO industry-heat
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

    ZEN-Europe's scope (README.md: EU27+NO+CH+UK-MT-CY, electricity/heat/
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


def _grey_delta_bar(ax, labels: list[str], values: dict[str, float], base_for: dict[str, str],
                     delta_color: dict[str, float], value_fmt: str = "{:,.0f}",
                     top: float | None = None, bottom: float | None = None,
                     delta_fmt: str | None = None, x: np.ndarray | None = None) -> None:
    """One bar per label: a baseline value in grey, and each bar's
    difference from ITS OWN baseline (`base_for[label]`, another label whose
    value supplies the grey height — itself for a baseline bar, so its own
    delta is 0) stacked on top (or hanging below, hatched, if negative) in
    that run's own color — so only the DELTA reads as "the interesting
    part" and the (usually much larger, near-identical-across-scenarios)
    baseline stays visually de-emphasized. `base_for` mapping more than one
    label to itself supports multiple independent baselines in one chart
    (fig14b's 2 model-option groups, each compared only against its own
    single-temp counterpart, never against the other group) — pass `x` with
    gaps between such groups so they don't read as one continuous
    comparison. Pairs with the y-axis truncation + break marks the caller
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

    x = np.arange(len(labels)) if x is None else x
    for xi, label in zip(x, labels):
        base_val = values[base_for[label]]
        val = values[label]
        delta = val - base_val
        grey_height = min(val, base_val)
        ax.bar(xi, grey_height, width=0.6, color=_ETH_GREY, edgecolor="white", zorder=2)
        if delta != 0:
            ax.bar(xi, abs(delta), width=0.6, bottom=grey_height, color=delta_color[label],
                   edgecolor="white", zorder=2, hatch="//" if delta < 0 else None)
        ax.text(xi, val, value_fmt.format(val), ha="center",
                 va="bottom" if delta >= 0 else "top", fontsize=8.5, fontweight="bold")
        if label != base_for[label]:
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


def fig14b_cost_and_emissions_totals_singletemp_vs_full(no_flex_run: Run, no_flex_single_run: Run,
                                                         full_run: Run, single_temp_run: Run) -> None:
    """Fig1b's template applied to 2 INDEPENDENT baselines side by side, per
    user request to bring fig14a and fig14b in line with each other: "No
    flexibility"'s own totals as the grey base of its own pair (vs. "No
    flexibility (single temp)"), and separately "Full flexibility"'s own
    totals as the grey base of ITS pair (vs. "Single temperature level") —
    a visible gap between the two pairs (via `x`) keeps them from reading as
    one continuous 4-bar comparison, since (per user instruction) the figure
    should only ever compare singletemp vs. not within a model option, never
    "No flexibility" against "Full flexibility" directly (fig1a/fig1b already
    cover that comparison).

    All 4 runs share the exact same binding carbon budget (cumulative
    emissions identical to the last digit across all 4 — confirmed
    directly), so the temperature-band resolution changes HOW the budget is
    met, not how much of it is used, in BOTH model options. Cost deltas are
    similarly small in both pairs (No flexibility: +86.7 bn EUR = +0.33%;
    Full flexibility: +88.8 bn EUR = +0.34%), so the y-limits are pinned
    tight around all 4 bars (derived from their totals) instead of the automatic 0.9x
    truncation, which at this delta size would leave the cost deltas a
    1-pixel sliver. `delta_fmt` keeps 1 decimal on the delta labels for the
    same reason. Emissions panel dropped per user request — all 4 runs share
    the identical binding carbon budget noted above, so that panel showed 4
    visually-identical bars with no information; only Total System Cost is
    plotted now, single-panel.
    -> SI_results/fig14b_cost_emissions_totals_singletemp_vs_full.svg
    """
    base_for = {no_flex_run.label: no_flex_run.label, no_flex_single_run.label: no_flex_run.label,
                full_run.label: full_run.label, single_temp_run.label: full_run.label}
    delta_color = {no_flex_run.label: _ETH_GREY, no_flex_single_run.label: _ETH_BLUE,
                   full_run.label: _ETH_GREY, single_temp_run.label: _ETH_PURPLE}
    # Extra gap (0.6 instead of the usual 1.0 spacing) between the 2 pairs so
    # they read as visually distinct groups, not one continuous 4-bar comparison.
    x = np.array([0, 1, 2.6, 3.6])
    # Tight y-limits derived from the 4 totals (rounded out to 50 bn EUR):
    # one data-span of headroom below the lowest bar and 0.6 above the
    # highest for the value/delta labels. Previously hardcoded to
    # 24,300-24,650, which silently pushed every bar off-axis once a re-run
    # shifted the totals (zen-europe runs: ~26,250-26,370).
    runs = [no_flex_run, no_flex_single_run, full_run, single_temp_run]
    costs = [_discounted_total_cost_bn(r) for r in runs]
    lo, hi = min(costs), max(costs)
    span = max(hi - lo, 1.0)
    bottom = np.floor((lo - span) / 50) * 50
    top = np.ceil((hi + 0.6 * span) / 50) * 50
    _cost_and_emissions_totals(runs, base_for,
                               delta_color, "fig14b_cost_emissions_totals_singletemp_vs_full",
                               bottom=bottom, top=top, delta_fmt="{:,.1f}", x=x, figsize=(7.5, 4.6),
                               cost_only=True)


def _discounted_total_cost_bn(run: Run) -> float:
    """Horizon-total discounted system cost in bn EUR (MEUR / 1000) — the
    same number fig1b/fig14b/fig30 plot."""
    years = get_available_years(run.results)
    return float(get_annual_total_cost(run.results, years, discount=True).sum()) / 1000


FIG30_YEAR = 2050  # snapshot year for fig30's capacity/storage panels (cost is horizon-cumulative)
FIG30_SHOW_ARROWS = False  # arrows off for a look without them (user request); True restores them
FIG30_VRE_TECHS = ["photovoltaics", "wind_onshore", "wind_offshore",
                   "reservoir_hydro", "run-of-river_hydro"]


def _fig30_matrix_panel(fig: plt.Figure, ax: plt.Axes, values: dict[tuple[int, int], float],
                        title: str, unit: str, cbar_label: str, row_labels: bool = True,
                        value_fmt: str = "{:,.0f}", delta_fmt: str = "{:,.1f}",
                        delta_unit: str | None = None,
                        ramp: tuple[str, str, str] = (_eth_tint(_ETH_BLUE, 0.85), _ETH_BLUE,
                                                      "#0F2A52"),
                        col_names: tuple[str, str] = ("Full flexibility", "No flexibility"),
                        row_names: tuple[str, str] = ("3 temp. levels", "Single temp. level"),
                        placeholders: frozenset = frozenset()):
    """One 2x2 flexibility x temperature-resolution matrix of fig30: `values`
    keyed by (row, col) — row 0 = 3 temp levels (top), col 0 = Full
    flexibility (left). Cells shaded by value (light -> dark blue,
    normalised min..max, own colourbar), unlabelled arrows from the baseline
    cell (Full flexibility, 3 temp levels) to the other 3; each target cell
    carries its own absolute and relative difference to the baseline in
    `unit` under its value (signed — the baseline need not be the smallest
    value outside the cost panel). `delta_unit` overrides `unit` for the
    absolute difference only (e.g. "pp" for a share given in "%"). Returns
    the colourbar so the caller can
    centre `title` over cells + colourbar once the layout is final — the
    title itself is NOT drawn here. `ramp` (light, mid, dark) sets the cell
    colours; `col_names`/`row_names` the matrix labels; cells in
    `placeholders` are hatched and marked "placeholder" (fig31)."""
    base_rc = (0, 0)
    base = values[base_rc]

    size, gap = 1.0, 0.12
    def corner(rc):  # lower-left corner of a cell, row 0 on top
        row, col = rc
        return col * (size + gap), (1 - row) * (size + gap)
    def center(rc):
        x0, y0 = corner(rc)
        return x0 + size / 2, y0 + size / 2

    # Cost -> continuous colour fade, normalised between the cheapest (light
    # ETH blue) and most expensive (dark ETH blue) cell; a colourbar documents it.
    cmap = LinearSegmentedColormap.from_list("fig30_cost", list(ramp))
    norm = Normalize(vmin=min(values.values()), vmax=max(values.values()))

    for rc, c in values.items():
        x0, y0 = corner(rc)
        t = norm(c)
        ax.add_patch(Rectangle((x0, y0), size, size, facecolor=cmap(t), edgecolor="#1F2A3A",
                               linewidth=1.2, zorder=1, hatch="//" if rc in placeholders else None))
        cx, cy = center(rc)
        # Value + its change vs. the baseline sit at each cell's outer
        # (top/bottom) edge, leaving the middle for the arrows.
        ty = y0 + (0.82 if rc[0] == 0 else 0.3) * size
        # Pick by the cell colour's relative luminance (WCAG cross-over 0.179),
        # not by t: mid-ramp blues are already dark enough to need white.
        r_, g_, b_ = (v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
                      for v in cmap(t)[:3])
        text_color = "white" if 0.2126 * r_ + 0.7152 * g_ + 0.0722 * b_ < 0.179 else "black"
        ax.text(cx, ty, f"{value_fmt.format(c)} {unit}", ha="center", va="center", fontsize=11,
                color=text_color, zorder=4)
        if rc == base_rc:
            sub = "baseline"
        else:
            delta = c - base
            sign = "+" if delta >= 0 else "−"
            sub = (f"{sign}{delta_fmt.format(abs(delta))} {delta_unit or unit}  "
                   f"({sign}{abs(delta) / base * 100:.2f} %)")
        ax.text(cx, ty - 0.12, sub, ha="center", va="center", fontsize=11.5,
                style="italic" if rc == base_rc else "normal",
                fontweight="normal" if rc == base_rc else "bold", color=text_color, zorder=4)
        if rc in placeholders:
            ax.text(cx, y0 + 0.5 * size, "placeholder", ha="center", va="center", fontsize=11,
                    style="italic", color=text_color, zorder=4,
                    bbox=dict(facecolor=cmap(t), edgecolor="none", pad=2))

    # ETH bronze: warm complement to the blue cell ramp, so the arrows stand
    # out equally on the lightest and darkest cells.
    arrow_color = _ETH_BRONZE
    bx0, by0 = corner(base_rc)
    # Each arrow gets its own start/end (fractions of a cell, relative to the
    # baseline cell's lower-left corner) so the 3 don't pile up on one point:
    # horizontal from the lower-middle-right, vertical from the left, diagonal
    # from the inner corner.
    arrows = {(0, 1): ((0.7, 0.42), (1.4, 0.42)),
              (1, 0): ((0.28, 0.3), (0.28, -0.4)),
              (1, 1): ((0.9, 0.1), (1.42, -0.42))}
    head_len = 0.13
    # Arrow width encodes |delta| within this panel: proportional to the
    # panel's largest |delta| (NOT min-max — that would always draw the
    # smallest change as the thinnest arrow even when all 3 are near-equal),
    # with a floor so a tiny change still reads as an arrow. Length can't
    # carry magnitude: each arrow has to reach its own target cell.
    max_abs = max(abs(values[rc] - base) for rc in arrows) or 1.0
    w_min, w_max = 0.04, 0.28
    for rc, ((fx0, fy0), (fx1, fy1)) in (arrows.items() if FIG30_SHOW_ARROWS else []):
        sx, sy = bx0 + fx0 * size, by0 + fy0 * size
        ex, ey = bx0 + fx1 * size, by0 + fy1 * size
        dx, dy = ex - sx, ey - sy
        delta = values[rc] - base
        width = max(w_min, w_max * abs(delta) / max_abs)
        ax.add_patch(FancyArrow(sx, sy, dx, dy, width=width, head_width=width + 0.12,
                                head_length=head_len, length_includes_head=True,
                                facecolor=arrow_color, edgecolor="white", linewidth=1.2, zorder=3))

    top_y = 2 * size + gap
    for col, label in enumerate(col_names):
        ax.text(col * (size + gap) + size / 2, top_y + 0.06, label, ha="center", va="bottom",
                fontsize=11, color="black")
    for row, label in enumerate(row_names if row_labels else []):
        ax.text(-0.06, (1 - row) * (size + gap) + size / 2, label, ha="right", va="center",
                rotation=90, fontsize=11, color="black")

    ax.set_xlim(-0.2, 2 * size + gap + 0.02)
    ax.set_ylim(-0.02, top_y + 0.2)
    ax.set_aspect("equal")
    ax.axis("off")
    cbar = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax, fraction=0.04, pad=0.03,
                        shrink=0.8)
    cbar.set_label(cbar_label, fontsize=10)
    cbar.ax.tick_params(labelsize=9)
    cbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    return cbar


_FIG30_METRICS_CACHE: dict[tuple[int, int], dict[str, float]] = {}


def _fig30_metrics(r: Run) -> dict[str, float]:
    """The 6 dimensions fig30 (and fig40) compare, for one run: discounted
    total system cost [bn EUR]; FIG30_YEAR total heat-pump share of industry
    heat output [%] (all temperature bands and sources, same
    _electrification_stack data as fig14a); FIG30_YEAR variable renewable
    capacity [GW]; and FIG30_YEAR annual discharge [TWh, GWh -> TWh] split
    three ways — bulk storage (BULK_STORAGE_TECHS), industry DSM energy
    equivalent (get_dsm_energy_equivalent) and industry TES
    (INDUSTRY_TES_TECHS). DSM/TES are 0 in runs without them."""
    key = (id(r.results), FIG30_YEAR)  # memoized: fig30/40/41/42 all need it
    if key in _FIG30_METRICS_CACHE:
        return _FIG30_METRICS_CACHE[key]

    def discharge_twh(techs: list[str]) -> float:
        return float(get_storage_flows(r.results, techs, "flow_storage_discharge")
                     .get(FIG30_YEAR, pd.Series(dtype=float)).sum()) / 1000.0
    vre = float(get_capacity(r.results, FIG30_VRE_TECHS, "power")
                .get(FIG30_YEAR, pd.Series(dtype=float)).sum())
    dsm = get_dsm_energy_equivalent(r.results, DSM_ENERGY_STACK_ORDER, [FIG30_YEAR]).sum() \
        .get(FIG30_YEAR, 0.0)
    stack = _electrification_stack(r)
    hp_cols = [c for c in stack.columns if c.startswith("heat_pump")]
    _FIG30_METRICS_CACHE[key] = {"cost": _discounted_total_cost_bn(r),
                                 "hp_share": float(stack.loc[FIG30_YEAR, hp_cols].sum()),
                                 "vre": vre,
                                 "storage": discharge_twh(BULK_STORAGE_TECHS),
                                 "dsm": float(dsm) / 1000.0,
                                 "tes": discharge_twh(INDUSTRY_TES_TECHS)}
    return _FIG30_METRICS_CACHE[key]


# Fixed-profile renewables whose unused potential counts as curtailment —
# FIG30_VRE_TECHS without reservoir_hydro (dispatchable, its unused inflow
# is reservoir storage/spillage, not curtailment).
CURTAILMENT_TECHS = ["photovoltaics", "wind_onshore", "wind_offshore", "run-of-river_hydro"]


def _curtailment_twh(r: Run, year: int = FIG30_YEAR) -> float:
    """Renewable curtailment in `year` [TWh]: ZEN-garden has no curtailment
    variable (shed_demand is unmet DEMAND — 0 in every run, since the
    electricity price peaks at ~1,300-1,600 EUR/MWh, far below the 10,000
    EUR/MWh price_shed_demand), so it is derived as available minus actually
    generated electricity, summed over CURTAILMENT_TECHS and nodes n:

        curtailment_y = sum_{i,n} [ capacity_{i,n,y} * sum_{h in y} max_load_{i,n,h}
                                    - sum_{h in y} flow_conversion_output_{i,electricity,n,h} ]

    capacity = installed power capacity [GW] (get_total("capacity"),
    capacity_type "power"); max_load = hourly availability factor [-]
    (get_full_ts, the representative time steps mapped back onto the year's
    8760 h), so capacity * sum_h max_load is the available energy [GWh];
    flow_conversion_output from get_total (already duration-weighted, GWh);
    GWh -> TWh. Equivalently with the raw time-series-aggregated data:
    sum_t duration_t * (capacity * max_load_t - output_t) over the 10
    representative steps — same numbers. With 10 representative steps the
    VRE peaks are smoothed, so absolute levels are likely underestimates;
    differences between scenarios are the robust part.

    Values [TWh] (share of available PV/wind/run-of-river energy):
        Full flexibility   2038: 348 (5.9 %)  2050: 392 (4.7 %)
        DSM pessimistic    2038: 352 (6.0 %)  2050: 482 (5.8 %)
        DSM only           2038: 347 (5.9 %)  2050: 460 (5.5 %)
        TES only           2038: 353 (6.0 %)  2050: 401 (4.8 %)
        No flexibility     2038: 355 (6.0 %)  2050: 489 (5.8 %)
        ZEN-Europe (base)  2038: 263 (5.1 %)  2050: 253 (3.6 %)
    2050 is mostly wind onshore (254-293 TWh) and offshore (104-141), then
    run-of-river (34-52); PV <= 3.5 TWh. ZEN-Europe (base) has ~17 % less
    available VRE in 2050 (6,934 vs ~8,300 TWh) and is the only run whose
    curtailment falls from 2038 to 2050."""
    key = (id(r.results), "curtailment", year)  # memoized: max_load is a large frame
    if key in _FIG30_METRICS_CACHE:
        return _FIG30_METRICS_CACHE[key]
    max_load = r.results.get_full_ts("max_load", year=year,
                                     index={"technology": CURTAILMENT_TECHS})
    cap = r.results.get_total("capacity")
    cap = cap[cap.index.get_level_values("capacity_type") == "power"].droplevel("capacity_type")
    available = (cap[year].reindex(max_load.index) * max_load.sum(axis=1)).sum()
    flow_out = _cached_total(r.results, "flow_conversion_output")
    generated = flow_out[flow_out.index.get_level_values("technology").isin(CURTAILMENT_TECHS)
                         & (flow_out.index.get_level_values("carrier") == "electricity")][year].sum()
    _FIG30_METRICS_CACHE[key] = float(available - generated) / 1000.0
    return _FIG30_METRICS_CACHE[key]


def _fig43_metrics(r: Run) -> dict[str, float]:
    """_fig30_metrics plus FIG30_YEAR curtailment (_curtailment_twh), for fig43."""
    return {**_fig30_metrics(r), "curtailment": _curtailment_twh(r)}


# fig30 panels in grid order (row-major, 2x2): metric key (_fig30_metrics)
# -> (title, unit, colourbar label, _fig30_matrix_panel kwargs). Storage is
# bulk storage only — DSM/TES discharge are 0 in No flexibility, so a matrix
# against it says nothing; fig40 shows them per scenario instead.
FIG30_PANELS = {
    "cost": ("Total cumulative costs in bn €", "bn €",
             "Discounted total system cost [bn EUR]", {}),
    "hp_share": (f"Heat-pump share of industrial heat {FIG30_YEAR} in %", "%",
                 f"Heat-pump share of industry heat output {FIG30_YEAR} [%]",
                 dict(value_fmt="{:.1f}", delta_unit="pp")),
    "vre": (f"Variable renewable capacity {FIG30_YEAR} in GW", "GW",
            f"Solar + wind + hydro capacity {FIG30_YEAR} [GW]", {}),
    "storage": (f"Storage discharge {FIG30_YEAR} in TWh", "TWh",
                f"Annual bulk storage discharge {FIG30_YEAR} [TWh]", {}),
}


def fig30_matrix(no_flex_run: Run, no_flex_single_run: Run, full_run: Run,
                 single_temp_run: Run) -> None:
    """fig14b's 4 runs laid out as 2x2 matrices — columns Full flexibility /
    No flexibility, rows 3 temperature levels / single level — per user
    sketch, 3 panels side by side (see _fig30_matrix_panel). Each cell is
    shaded by its value, and arrows from the cheapest cell, Full flexibility
    with 3 temp levels, point to each of the other 3 cells labelled with the
    difference relative to that baseline in % and absolute terms. Unlike
    fig14b, No flexibility is compared against Full flexibility here too
    (the diagonal + horizontal arrows) — the whole point of the matrix is a
    single shared baseline.

    Panels (2x2, row-major, see _fig30_metrics): top row discounted total
    system cost [bn EUR] | 2050 total heat-pump share of industry heat
    output [%] (change in pp); bottom row 2050 variable renewable power
    capacity [GW] (solar + wind on/offshore + reservoir/run-of-river hydro)
    | 2050 annual bulk storage discharge [TWh], without DSM and TES (per
    user: DSM/TES are 0 in No flexibility, so their matrix cells say
    nothing — fig40 shows them per flexibility scenario). Discharge rather than storage ENERGY
    capacity per user choice: energy capacity is ~98% natural_gas_storage
    (~1,015 TWh, essentially all existing stock and identical across
    scenarios), whereas discharge is what fig12 already shows
    (battery-dominated).
    -> SI_results/fig30_matrix.svg
    """
    cells = {(0, 0): full_run, (0, 1): no_flex_run,
             (1, 0): single_temp_run, (1, 1): no_flex_single_run}
    _matrix_figure(cells, "fig30_matrix")


def fig31_matrix_tsa(no_flex_run: Run, no_flex_20ts_run: Run, full_run: Run,
                     full_20ts_run: Run, no_flex_20ts_placeholder: bool = False) -> None:
    """fig30 with the time-series aggregation as the second dimension: rows
    10 / 20 representative time steps per year instead of 3 / single
    temperature level, same baseline (Full flexibility, 10 ts), panels and
    metrics; ETH green instead of blue cells to tell it apart from fig30.
    `no_flex_20ts_placeholder` hatches the No flexibility 20 ts cell and
    marks it "placeholder" — set while that run is still on Euler and
    `no_flex_20ts_run` is the 10 ts run standing in for it.
    -> SI_results/fig31_matrix_tsa.svg
    """
    cells = {(0, 0): full_run, (0, 1): no_flex_run,
             (1, 0): full_20ts_run, (1, 1): no_flex_20ts_run}
    _matrix_figure(cells, "fig31_matrix_tsa",
                   ramp=(_eth_tint(_ETH_GREEN, 0.85), _ETH_GREEN, "#2F3709"),
                   row_names=("10 time steps", "20 time steps"),
                   placeholders=frozenset({(1, 1)} if no_flex_20ts_placeholder else ()))


def _matrix_figure(cells: dict[tuple[int, int], Run], fig_name: str, **panel_kw) -> None:
    """fig30's body for any 2x2 `cells` (row, col) -> run, (0, 0) the
    baseline; `panel_kw` goes to every _fig30_matrix_panel."""
    metrics = {rc: _fig30_metrics(r) for rc, r in cells.items()}
    vals = {k: {rc: m[k] for rc, m in metrics.items()} for k in FIG30_PANELS}

    # 2x2 grid of panels: cost | HP share over VRE | storage.
    fig, axes = plt.subplots(2, 2, figsize=(15, 14))
    panels = [(vals[k], *FIG30_PANELS[k]) for k in FIG30_PANELS]
    cbars = [_fig30_matrix_panel(fig, ax, vals, title, unit, cbar_label, row_labels=(i % 2 == 0),
                                 **kw, **panel_kw)
             for i, (ax, (vals, title, unit, cbar_label, kw)) in enumerate(zip(axes.flat, panels))]
    fig.subplots_adjust(hspace=0.1, wspace=0.12)
    # Centre each title over its cells + colourbar (incl. its label) — only
    # possible after a draw, since set_aspect("equal") shrinks each axes and
    # the colourbar label's extent is only known once rendered.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    to_fig = fig.transFigure.inverted()
    for ax, cbar, (_, title, *_rest) in zip(axes.flat, cbars, panels):
        left = ax.transData.transform((0, 0))[0]  # left edge of the cells
        right = cbar.ax.get_tightbbox(renderer).x1
        top = ax.get_window_extent(renderer).y1
        x, y = to_fig.transform(((left + right) / 2, top))
        fig.text(x, y + 0.003, title, ha="center", va="bottom", fontsize=12.5, fontweight="bold")
    bottom = to_fig.transform((0, axes[1, 0].get_window_extent(renderer).y0))[1]
    if FIG30_SHOW_ARROWS:
        fig.text(0.5, bottom - 0.012, "Arrow width is proportional to the size of the change relative to "
                 "the largest change within each panel.", ha="center", va="top", fontsize=10,
                 style="italic", color="black")
    if panel_kw.get("placeholders"):
        fig.text(0.5, bottom - 0.012, "Hatched cell: placeholder — shows the 10 time step run "
                 "until the 20 time step run is available.", ha="center", va="top", fontsize=10,
                 style="italic", color="black")
    savefig(fig, fig_name)


# fig40 panels — fig30's 4 plus DSM and TES discharge: key -> (title, Δ unit,
# value format). The baseline's absolute value is shown in "%" for hp_share.
FIG40_PANELS = {"cost": ("Total cumulative costs", "bn €", "{:,.0f}"),
                "hp_share": (f"Heat-pump share {FIG30_YEAR}", "pp", "{:.1f}"),
                "vre": (f"Variable renewables {FIG30_YEAR}", "GW", "{:,.0f}"),
                "storage": (f"Storage discharge {FIG30_YEAR}", "TWh", "{:,.0f}"),
                "dsm": (f"DSM discharge {FIG30_YEAR}", "TWh", "{:,.0f}"),
                "tes": (f"TES discharge {FIG30_YEAR}", "TWh", "{:,.1f}")}
# Full flexibility on top (the zero line), No flexibility at the bottom,
# behind a dashed separator.
FIG40_ORDER = ["Full flexibility", "DSM pessimistic", "DSM only", "TES only", "No flexibility"]


def fig40_flex_scenarios(runs: list[Run]) -> None:
    """The flexibility scenarios compared on fig30's 4 dimensions plus DSM
    and TES discharge (2x3 panels), per user sketch rotated to horizontal: scenarios down the
    y-axis, one bar per scenario giving its difference to Full flexibility
    (the vertical zero line, labelled with its absolute value), with No
    flexibility set apart at the bottom behind a dashed line. Bars in each
    run's SCENARIO_PALETTE colour; each carries its absolute and relative
    difference. Heat-pump share differences are in percentage points.
    -> SI_results/fig40_flex_scenarios.svg
    """
    by = {r.label: r for r in runs}
    order = [lbl for lbl in FIG40_ORDER if lbl in by]
    metrics = {lbl: _fig30_metrics(by[lbl]) for lbl in order}
    base = metrics["Full flexibility"]
    y = np.arange(len(order))

    fig, axes = plt.subplots(2, 3, figsize=(16, 8), sharey=True)
    for ax, (key, (title, unit, fmt)) in zip(axes.flat, FIG40_PANELS.items()):
        deltas = [metrics[lbl][key] - base[key] for lbl in order]
        ax.barh(y, deltas, height=0.6, color=[by[lbl].color for lbl in order],
                edgecolor="#1F2A3A", linewidth=1.0, zorder=2)
        ax.axvline(0, color="#1F2A3A", linewidth=1.2, zorder=3)
        lo, hi = min(0.0, *deltas), max(0.0, *deltas)
        span = (hi - lo) or 1.0
        # Room beside the bar ends for the labels.
        ax.set_xlim(lo - (0.6 if lo < 0 else 0.1) * span, hi + (0.6 if hi > 0 else 0.1) * span)
        pct_fmt = "{:.2f}" if key == "cost" else "{:.1f}"
        for yi, lbl, d in zip(y, order, deltas):
            if lbl == "Full flexibility":
                abs_unit = "%" if key == "hp_share" else unit
                left = hi <= 0  # put it on whichever side has room
                ax.text(-0.03 * span if left else 0.03 * span, yi,
                        f"{fmt.format(base[key])} {abs_unit}", ha="right" if left else "left",
                        va="center", fontsize=9, style="italic")
                continue
            sign = "+" if d >= 0 else "−"
            pct = f" ({sign}{pct_fmt.format(abs(d) / base[key] * 100)} %)" if base[key] else ""
            ax.text(d + (0.03 if d >= 0 else -0.03) * span, yi,
                    f"{sign}{fmt.format(abs(d))} {unit}\n{pct.strip()}",
                    ha="left" if d >= 0 else "right", va="center", fontsize=8.5)
        ax.axhline(len(order) - 1.5, color="#1F2A3A", linestyle="--", linewidth=1.0)
        ax.set_title(title, fontsize=11.5, fontweight="bold")
        ax.set_xlabel(f"Δ {unit}", fontsize=10)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _, span=span: f"{v:,.0f}"
                                                       if span >= 10 else f"{v:,.1f}"))
        ax.tick_params(axis="x", labelsize=9)
        ax.tick_params(axis="y", length=0, labelsize=10.5)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
    axes[0, 0].set_yticks(y)
    axes[0, 0].set_yticklabels(order)
    axes[0, 0].invert_yaxis()
    fig.tight_layout()
    savefig(fig, "fig40_flex_scenarios")


def fig41_flex_scenarios_table(runs: list[Run], panels: dict = FIG40_PANELS,
                               metrics_fn=_fig30_metrics,
                               fig_name: str = "fig41_flex_scenarios_table",
                               transpose: bool = False) -> None:
    """fig40's data as an annotated heatmap table (alternative to fig40, per
    user): scenarios as rows (FIG40_ORDER, No flexibility below a dashed
    line), the FIG40_PANELS metrics as columns. Each cell gives the absolute
    value and, under it, the difference to Full flexibility (absolute and
    %; pp for the heat-pump share), and is shaded by that difference — ETH
    blue below / red above Full flexibility, scaled per column to its
    largest |difference| (cost moves by ~0.1 %, DSM/TES by up to 100 %, so a
    shared scale would leave most columns white). `panels`/`metrics_fn`/
    `fig_name` let fig43 reuse it with an extra curtailment metric;
    `transpose` puts the metrics in rows and the scenarios in columns (No
    flexibility right of a dashed line), shading then scaled per row.
    -> SI_results/fig41_flex_scenarios_table.svg
    """
    by = {r.label: r for r in runs}
    order = [lbl for lbl in FIG40_ORDER if lbl in by]
    metrics = {lbl: metrics_fn(by[lbl]) for lbl in order}
    base = metrics["Full flexibility"]
    cmap = LinearSegmentedColormap.from_list("fig41_delta", [_ETH_BLUE, "white", _ETH_RED])
    norm = Normalize(vmin=-1, vmax=1)

    n_metrics, n_scen = len(panels), len(order)

    def xy(i_metric: int, i_scen: int) -> tuple[int, int]:
        """Lower-left (x, y) of a cell: metrics along x (columns), or along y if transposed."""
        return (i_scen, i_metric) if transpose else (i_metric, i_scen)

    n_x, n_y = xy(n_metrics, n_scen)
    fig, ax = plt.subplots(figsize=(2.5 * n_x + (2.5 if transpose else 0), 5.6 if not transpose
                                    else 1.0 * n_y + 1.2))
    for i_m, (key, (title, unit, fmt)) in enumerate(panels.items()):
        abs_unit = "%" if key == "hp_share" else unit
        if transpose:
            # Inside the (white) Full flexibility cell's left margin, nearer its values
            # (which sit right of centre, x + 0.6, to balance the gaps either side).
            ax.text(0.15, i_m + 0.5, f"{title}\n[{abs_unit}]", ha="right", va="center",
                    fontsize=10.5, fontweight="bold")
        else:
            ax.text(i_m + 0.5, -0.12, f"{title}\n[{abs_unit}]", ha="center", va="bottom",
                    fontsize=10.5, fontweight="bold")
        max_abs = max(abs(metrics[lbl][key] - base[key]) for lbl in order) or 1.0
        pct_fmt = "{:.2f}" if key == "cost" else "{:.1f}"
        for i_s, lbl in enumerate(order):
            x, y = xy(i_m, i_s)
            val = metrics[lbl][key]
            d = val - base[key]
            color = cmap(norm(d / max_abs))
            ax.add_patch(Rectangle((x, y), 1, 1, facecolor=color, edgecolor="white",
                                   linewidth=2, zorder=1))
            text_color = _text_color_for_bg(color)
            cx = x + (0.6 if transpose and lbl == "Full flexibility" else 0.5)
            ax.text(cx, y + 0.4, fmt.format(val), ha="center", va="center",
                    fontsize=12, fontweight="bold", color=text_color)
            if lbl == "Full flexibility":
                sub = "baseline"
            else:
                sign = "+" if d >= 0 else "−"
                sub = (f"{sign}{fmt.format(abs(d))} {unit} "
                       f"({sign}{pct_fmt.format(abs(d) / base[key] * 100)} %)")
            ax.text(cx, y + 0.72, sub, ha="center", va="center", fontsize=9,
                    style="italic" if lbl == "Full flexibility" else "normal", color=text_color)
    for i_s, lbl in enumerate(order):
        if transpose:
            ax.text(i_s + (0.6 if lbl == "Full flexibility" else 0.5), -0.12, lbl, ha="center",
                    va="bottom", fontsize=11,
                    fontweight="bold")
        else:
            ax.text(-0.08, i_s + 0.5, lbl, ha="right", va="center", fontsize=11)
    if transpose:
        ax.plot([n_scen - 1] * 2, [-0.5, n_metrics], color="#1F2A3A", linestyle="--",
                linewidth=1.2, clip_on=False, zorder=3)
    else:
        ax.plot([-0.9, n_metrics], [n_scen - 1] * 2, color="#1F2A3A", linestyle="--",
                linewidth=1.2, clip_on=False, zorder=3)
    ax.set_xlim(0, n_x)
    ax.set_ylim(n_y, 0)
    ax.axis("off")
    cbar = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax, fraction=0.025, pad=0.02,
                        ticks=[-1, 0, 1])
    cbar.ax.set_yticklabels(["largest\ndecrease", "same as\nFull flex.", "largest\nincrease"],
                            fontsize=9)
    cbar.set_label(f"Difference to Full flexibility (scaled per {'row' if transpose else 'column'})",
                   fontsize=10)
    savefig(fig, fig_name)


# fig41's columns plus curtailment (_curtailment_twh).
FIG43_PANELS = {**FIG40_PANELS, "curtailment": (f"Curtailment {FIG30_YEAR}", "TWh", "{:,.0f}")}


def fig43_flex_scenarios_table_curtailment(runs: list[Run]) -> None:
    """fig41 transposed (metrics as rows, scenarios as columns — taller, less
    wide) with a 7th metric: FIG30_YEAR renewable curtailment [TWh] — see
    _curtailment_twh for how it is computed (available PV/wind/run-of-river
    energy capacity * max_load minus flow_conversion_output; ZEN-garden has
    no curtailment variable and shed_demand is 0 in every run).

    ZEN-Europe (base) on the same metrics, for reference (not plotted — it
    has no industry-heat sectors, so it is not a flexibility scenario):
    discounted total cost 24,480 bn EUR (Full flexibility 26,257), VRE
    capacity 2050 3,106 GW (3,735), bulk storage discharge 2050 249 TWh
    (264), curtailment 2050 253 TWh (392) / 3.6 % of available VRE energy
    (4.7 %), 2038 263 TWh (348); heat-pump share, DSM and TES discharge do
    not apply (no industry heat).
    -> SI_results/fig43_flex_scenarios_table_curtailment.svg
    """
    fig41_flex_scenarios_table(runs, FIG43_PANELS, _fig43_metrics,
                               "fig43_flex_scenarios_table_curtailment", transpose=True)


def _dsm_storage_cost_bn(r: Run) -> float:
    """Horizon-total discounted cost of the *_DSM storage techs [bn EUR]:
    cost_capex_yearly + cost_opex_yearly of every technology ending in
    "_DSM", per year, times _discount_factors (net_present_cost /
    cost_total, so discounted exactly like _discounted_total_cost_bn),
    MEUR -> bn EUR. Full flexibility ~1,281 MEUR undiscounted opex + ~5 capex;
    DSM no cost ~0.6."""
    years = get_available_years(r.results)
    total = pd.Series(0.0, index=years)
    for var in ("cost_capex_yearly", "cost_opex_yearly"):
        df = r.results.get_total(var)
        per_year = df[df.index.get_level_values("technology").str.endswith("_DSM")].sum()
        per_year.index = per_year.index.astype(int)
        total = total.add(per_year.reindex(years).fillna(0.0))
    return float((total * _discount_factors(r.results, years)).sum()) / 1000


def _fig50_metrics(r: Run) -> dict[str, float]:
    """_fig43_metrics plus total cost without the DSM storage techs' own cost."""
    m = _fig43_metrics(r)
    return {"cost": m["cost"], "cost_ex_dsm": m["cost"] - _dsm_storage_cost_bn(r),
            **{k: v for k, v in m.items() if k != "cost"}}


# fig43's rows with "cost excl. DSM storage cost" right under total cost.
FIG50_ROWS = {"cost": FIG43_PANELS["cost"],
              "cost_ex_dsm": ("Total costs excl. DSM storage cost", "bn €", "{:,.0f}"),
              **{k: v for k, v in FIG43_PANELS.items() if k != "cost"}}
FIG50_PCT_CAP = 50.0  # shading saturates at ±50 % change


def fig50_dsm_no_cost_vs_full_flex(full_run: Run, no_cost_run: Run) -> None:
    """Full flexibility vs. DSM no cost (336 h) on fig43's metrics plus total
    cost excluding the DSM storage techs' own cost (_dsm_storage_cost_bn —
    separates the mechanical drop from making DSM free from the rest of the
    system getting cheaper). Table with metrics as rows and three columns:
    both runs' absolute values (white) and the difference (absolute, pp for
    the heat-pump share, and %), shaded ETH blue (decrease) / red
    (increase) by the % change on ONE shared scale saturating at
    ±FIG50_PCT_CAP — unlike fig43's per-row scaling, which with a single
    comparison would colour every non-zero cell fully.
    Note the two runs differ in DSM cost AND DSM energy_to_power_ratio_max
    (2/48 h -> 336 h for ammonia, ceramic, clinker, food, glass, olefin,
    primary steel; methanol/paper/secondary steel already 336 h) — all other
    inputs and settings identical (checked 2026-10-22).
    -> SI_results/fig50_dsm_no_cost_vs_full_flex.svg
    """
    _comparison_table(full_run, no_cost_run, FIG50_ROWS, _fig50_metrics,
                      "DSM no cost: DSM storage cost ≈ 0 and max. energy-to-power ratio 336 h for "
                      "all DSM technologies\n(Full flexibility: 2–48 h for 7 of 10).",
                      "fig50_dsm_no_cost_vs_full_flex")


def fig60_full_flex_20ts_vs_10ts(full_run: Run, full_20ts_run: Run) -> None:
    """fig50's table for Full flexibility with 10 (baseline) vs. 20
    representative time steps per year, on fig43's metrics (no "excl. DSM
    storage cost" row — both runs have the same DSM cost).
    -> SI_results/fig60_full_flex_20ts_vs_10ts.svg
    """
    _comparison_table(full_run, full_20ts_run, FIG43_PANELS, _fig43_metrics,
                      "20 ts: 20 instead of 10 representative time steps per year; all other "
                      "inputs identical.", "fig60_full_flex_20ts_vs_10ts",
                      base_label="Full flexibility (10 ts)")


def _comparison_table(base_run: Run, other_run: Run, rows: dict, metrics_fn, footnote: str,
                      fig_name: str, base_label: str = "Full flexibility") -> None:
    """fig50's body for any run pair: `rows` key -> (title, unit, format) of
    `metrics_fn`'s metrics; `base_run` is the baseline column."""
    m_base, m_other = metrics_fn(base_run), metrics_fn(other_run)
    cmap = LinearSegmentedColormap.from_list("fig50_delta", [_ETH_BLUE, "white", _ETH_RED])
    norm = Normalize(vmin=-FIG50_PCT_CAP, vmax=FIG50_PCT_CAP)
    # Column x-extents: two value columns, a wider difference column.
    cols = [(0.0, 1.0), (1.0, 2.0), (2.0, 3.5)]
    n_rows = len(rows)

    fig, ax = plt.subplots(figsize=(9.5, 0.75 * n_rows + 1.4))
    for (x0, x1), head in zip(cols, [base_label, other_run.label, "Difference"]):
        ax.text((x0 + x1) / 2, -0.12, head, ha="center", va="bottom", fontsize=11,
                fontweight="bold")
    for i, (key, (title, unit, fmt)) in enumerate(rows.items()):
        abs_unit = "%" if key == "hp_share" else unit
        ax.text(-0.08, i + 0.5, f"{title}\n[{abs_unit}]", ha="right", va="center",
                fontsize=10.5, fontweight="bold")
        base, val = m_base[key], m_other[key]
        d = val - base
        pct = d / base * 100 if base else 0.0
        for (x0, x1), v in zip(cols[:2], (base, val)):
            ax.add_patch(Rectangle((x0, i), x1 - x0, 1, facecolor="white", edgecolor="#D0D0D0",
                                   linewidth=1, zorder=1))
            ax.text((x0 + x1) / 2, i + 0.5, fmt.format(v), ha="center", va="center", fontsize=12,
                    fontweight="bold")
        x0, x1 = cols[2]
        color = cmap(norm(np.clip(pct, -FIG50_PCT_CAP, FIG50_PCT_CAP)))
        ax.add_patch(Rectangle((x0, i), x1 - x0, 1, facecolor=color, edgecolor="#D0D0D0",
                               linewidth=1, zorder=1))
        sign = "+" if d >= 0 else "−"
        pct_fmt = "{:.2f}" if key.startswith("cost") else "{:.1f}"
        ax.text((x0 + x1) / 2, i + 0.5,
                f"{sign}{fmt.format(abs(d))} {unit}  ({sign}{pct_fmt.format(abs(pct))} %)",
                ha="center", va="center", fontsize=11, fontweight="bold",
                color=_text_color_for_bg(color))
    ax.set_xlim(0, cols[-1][1])
    ax.set_ylim(n_rows, 0)
    ax.axis("off")
    cbar = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax, fraction=0.03, pad=0.02,
                        ticks=[-FIG50_PCT_CAP, 0, FIG50_PCT_CAP])
    cbar.ax.set_yticklabels([f"≤ −{FIG50_PCT_CAP:.0f} %", "0 %", f"≥ +{FIG50_PCT_CAP:.0f} %"],
                            fontsize=9)
    cbar.set_label(f"Change vs. {base_label}", fontsize=10)
    ax.text(cols[-1][1] / 2, n_rows + 0.15, footnote, ha="center", va="top", fontsize=9,
            style="italic")
    savefig(fig, fig_name)


def fig42_flex_decomposition(runs: list[Run]) -> None:
    """fig40's data as a stepwise decomposition (alternative to fig40, per
    user): per metric (FIG40_PANELS, same 2x3 order), the path from No
    flexibility via one flexibility option to Full flexibility — once via TES
    only (No flex -> TES only -> Full flex, i.e. add TES, then DSM) and once
    via DSM only (add DSM, then TES) — so each step shows what that option
    contributes and whether the two are additive (both paths end in the same
    point by construction). DSM pessimistic is the DSM-only step with the
    pessimistic DSM categories (no TES), drawn as a dotted step from No
    flexibility. Points in each run's SCENARIO_PALETTE colour, arrows in the
    colour of the intermediate scenario.
    -> SI_results/fig42_flex_decomposition.svg
    """
    by = {r.label: r for r in runs}
    needed = ["No flexibility", "TES only", "DSM only", "Full flexibility"]
    if any(lbl not in by for lbl in needed):
        print(f"  skipping fig42_flex_decomposition: needs {', '.join(needed)}")
        return
    labels = needed + (["DSM pessimistic"] if "DSM pessimistic" in by else [])
    metrics = {lbl: _fig30_metrics(by[lbl]) for lbl in labels}
    # (intermediate scenario, x of the intermediate point, line style)
    paths = [("TES only", 1.0, "-"), ("DSM only", 1.0, "-")]
    if "DSM pessimistic" in by:
        paths.append(("DSM pessimistic", 1.0, ":"))

    fig, axes = plt.subplots(2, 3, figsize=(15, 8.5))
    for ax, (key, (title, unit, fmt)) in zip(axes.flat, FIG40_PANELS.items()):
        v = {lbl: metrics[lbl][key] for lbl in labels}
        abs_unit = "%" if key == "hp_share" else unit
        for mid, x_mid, ls in paths:
            color = by[mid].color
            steps = [((0, v["No flexibility"]), (x_mid, v[mid]))]
            if mid != "DSM pessimistic":
                steps.append(((x_mid, v[mid]), (2, v["Full flexibility"])))
            for (x0, y0), (x1, y1) in steps:
                ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                            arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8, linestyle=ls,
                                            shrinkA=7, shrinkB=7, mutation_scale=14), zorder=2)
        for lbl, x in [("No flexibility", 0), ("Full flexibility", 2)] + \
                      [(mid, x_mid) for mid, x_mid, _ in paths]:
            hollow = lbl == "DSM pessimistic"
            ax.scatter(x, v[lbl], s=70, zorder=3, linewidths=1.5,
                       facecolor="white" if hollow else by[lbl].color,
                       edgecolor=by[lbl].color if hollow else "#1F2A3A")
            ha, dx = {0: ("right", -9), 2: ("left", 9)}.get(x, ("left", 9))
            ax.annotate(fmt.format(v[lbl]), (x, v[lbl]), xytext=(dx, 0),
                        textcoords="offset points", ha=ha, va="center", fontsize=8.5,
                        color=by[lbl].color, fontweight="bold")
        lo, hi = min(v.values()), max(v.values())
        pad = 0.12 * ((hi - lo) or abs(hi) or 1.0)
        ax.set_ylim(lo - pad, hi + pad)
        ax.set_xlim(-0.6, 2.6)
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(["No\nflexibility", "One option", "Full\nflexibility"], fontsize=9.5)
        ax.set_title(title, fontsize=11.5, fontweight="bold")
        ax.set_ylabel(f"[{abs_unit}]", fontsize=10)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f"{val:,.0f}"))
        ax.tick_params(axis="y", labelsize=9)
        ax.tick_params(axis="x", length=0)
        ax.grid(axis="y", color="#E0E0E0", linewidth=0.6, zorder=0)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    handles = [Line2D([], [], color=by[mid].color, lw=1.8, linestyle=ls,
                      marker="o", markerfacecolor="white" if mid == "DSM pessimistic" else by[mid].color,
                      markeredgecolor=by[mid].color if mid == "DSM pessimistic" else "#1F2A3A",
                      label=f"via {mid}") for mid, _, ls in paths]
    fig.legend(handles=handles, loc="lower center", ncol=len(handles), frameon=False,
               fontsize=10.5, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    savefig(fig, "fig42_flex_decomposition")


def _cost_and_emissions_totals(runs: list[Run], base_for: dict[str, str], delta_color: dict[str, str],
                                fig_name: str, top: float | None = None,
                                bottom: float | None = None,
                                delta_fmt: str | None = None, x: np.ndarray | None = None,
                                figsize: tuple[float, float] = (11, 4.6),
                                cost_only: bool = False) -> None:
    """Body of fig14b — `base_for` maps each run's label to the
    label supplying ITS grey baseline (see _grey_delta_bar), `runs` the bars
    themselves, in order. `top`/`bottom`/`delta_fmt`/`x` pass straight
    through to _grey_delta_bar (same limits/positions on both panels).
    `cost_only=True` (fig14b, per user request) drops the emissions panel
    entirely and renders a single-axes figure instead of the 2-panel
    cost+emissions layout."""
    # bn EUR (billion EUR) rather than MEUR per user request — MEUR values
    # here run ~2.3e7 (i.e. ~23 trillion EUR); dividing by 1000 gives a
    # legible ~23,000 bn EUR without scientific-notation axis ticks.
    cost = {r.label: _discounted_total_cost_bn(r) for r in runs}

    labels = [r.label for r in runs]

    if cost_only:
        fig, ax1 = plt.subplots(1, 1, figsize=figsize)
    else:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    _grey_delta_bar(ax1, labels, cost, base_for, delta_color, value_fmt="{:,.0f}",
                    top=top, bottom=bottom, delta_fmt=delta_fmt, x=x)
    ax1.set_ylabel("Discounted total system cost [bn EUR]")
    ax1.set_title("Total System Cost", fontsize=12, fontweight="bold")

    if not cost_only:
        def _series(r, name):
            s = r.get_total(name)
            return {int(k): float(v) for k, v in s.items()}

        emissions = {}
        for r in runs:
            cum = _series(r.results, "carbon_emissions_cumulative")
            emissions[r.label] = cum[max(cum)]

        _grey_delta_bar(ax2, labels, emissions, base_for, delta_color, value_fmt="{:,.0f}",
                        top=top, bottom=bottom, delta_fmt=delta_fmt, x=x)
        ax2.set_ylabel("Cumulative carbon emissions [Mton CO$_2$eq]")
        ax2.set_title("Total Cumulative Emissions", fontsize=12, fontweight="bold")

    fig.tight_layout()
    savefig(fig, fig_name)


# ── 8/9: Real-world industry-emissions context (input data, no model results) ──
# Neither figure below depends on a solved ZEN-garden run: both plot exogenous,
# real-world emissions data (JRC-IDEES-2023 / UNFCCC CRF, reached via
# ZEN-creator's input_data) that motivate/contextualize ZEN-Europe's
# sectoral scope, per user request — generated unconditionally in main().

INDUSTRY_SECTOR_EMISSIONS_JSON = FIGURES_DIR / "industry_sector_emissions_input.json"
# Sibling-repo convention: a plain CSV, so no openpyxl/env-split bridge is
# needed unlike fig8's JSON.
MODEL_SCOPE_CSV = REPO_ROOT.parent / "ZEN-creator" / "input_data" / "Emissionbudget" / "sector_emissions_2022.csv"

_SCOPE_COLOR = {"old": _ETH_BLUE, "new": _ETH_GREEN, None: _ETH_GREY}
_SCOPE_LABEL = {"old": "Existing ZEN-Europe sectors (Mannhardt, 2026)",
                "new": "Industry-heat extension (this work)",
                None: "Not modeled by ZEN-Europe"}


def fig8_industry_sector_emissions_context() -> None:
    """European industrial CO2 emissions by subsector (JRC-IDEES-2023, EU27,
    2022) — pure real-world input-data context, no solved model results.
    Answers "how big are the industry sectors ZEN-Europe (and its
    industry-heat extension) model, relative to the rest of European
    industry": each bar is colored/stacked by whether that slice is inside
    Mannhardt's original 11-sector scope (blue), the four new industry-heat
    sectors added here (turquoise), or not modeled at all (grey). One
    subsector, "Non-metallic minerals", is split into its JRC-IDEES
    second-level components so this line can be drawn correctly INSIDE the
    bar rather than per whole subsector: cement (old) + glass/ceramics (new).
    "Paper, pulp & printing" is plotted as a single new-scope bar instead
    (per user request), rather than splitting out its unmodeled pulp/printing
    slice. See extract_industry_sector_emissions.py for the extraction and
    the full scope-mapping rationale.

    CAVEAT: these are JRC-IDEES's energy-related (fuel combustion) emissions
    only — the IPCC 1.A methodology JRC-IDEES itself uses — and do NOT
    include IPCC 2.x process emissions (cement calcination, steel ore
    reduction, glass/ceramic carbonate decomposition). Steel and non-metallic
    minerals both have a substantial process-emissions component not counted
    here, so their bars understate those two sectors' full footprint
    relative to sector_emissions_2022.csv (fig9's source), which DOES fold
    UNFCCC process-emission CRF categories in on top of combustion for the
    specific sectors ZEN-Europe models. Not comparable 1:1 with fig9's Mt
    figures for that reason — this figure's job is relative subsector SCALE
    across ALL of European industry, fig9's is the model's total coverage
    SHARE of all-sector European emissions.
    """
    if not INDUSTRY_SECTOR_EMISSIONS_JSON.exists():
        print(f"  skipping fig8_industry_sector_emissions_context: "
              f"{INDUSTRY_SECTOR_EMISSIONS_JSON.relative_to(REPO_ROOT)} not found — "
              "run scripts/extract_industry_sector_emissions.py under zen-creator-env first")
        return
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
    emissions ZEN-Europe's modeled sectors cover, and how much of that
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

    segments = [("Existing ZEN-Europe sectors\n(Mannhardt, 2026)", share_old, _ETH_BLUE, e_old / 1000),
                ("+ Industry-heat extension\n(this work)", share_new, _ETH_GREEN, e_new / 1000),
                ("Not covered by ZEN-Europe", share_uncovered, _ETH_GREY, None)]

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
    ax.set_title("ZEN-Europe's Coverage of Total European Direct CO$_2$ Emissions",
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
# Per user instruction: this is NOT filtered down to ZEN-Europe's own
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
# not filtered to ZEN-Europe's own modeled sector list.
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
    tobacco, other industry; NOT filtered to ZEN-Europe's own modeled
    sectors — see the module comment above for exactly which categories and
    why). Dashed guide lines tie bar 2's span to bar 1's Energy segment so
    the drill-down relationship reads immediately.

    The two green wedges are industry's two-part global footprint: process
    emissions (top bar, 6.2%, uncapturable by any energy-system model) and
    industry's energy-side footprint (bottom bar, 24.3%, most — not all —
    of which is ZEN-Europe's industry-heat extension's actual target,
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
# No flexibility vs ZEN-Europe base isolates the power-sector cost of
# electrifying industry heat WITHOUT any flexibility (DSM/TES) to shape that
# new load — ZEN-Europe base has no industry-heat sector at all (see
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
# in every run, including ZEN-Europe base — unlike industry TES/DSM, which
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

# Industry flexibility in fig12's storage panel (only non-zero in runs with
# the flexibility options): TES per temperature band in ETH_RED tints (heat,
# hotter = darker), DSM summed over all products as GWh energy equivalent
# (get_dsm_energy_equivalent) in ETH_GREEN — both colors unused by the bulk
# storage techs above.
INDUSTRY_DSM_LABEL = "industry DSM (energy equiv.)"
STORAGE_COLOR_MAP.update({
    "industry_TES_water_0_100": _eth_tint(_ETH_RED, 0.55),
    "industry_TES_water_100_150": _eth_tint(_ETH_RED, 0.25),
    "industry_TES_steam_150_200": _ETH_RED,
    INDUSTRY_DSM_LABEL: _ETH_GREEN,
})
STORAGE_STACK_ORDER += ["industry_TES_water_0_100", "industry_TES_water_100_150",
                        "industry_TES_steam_150_200", INDUSTRY_DSM_LABEL]


# ── DSM discharge translated into an energy (GWh) equivalent (fig30) ──────
# ammonia_DSM/methanol_DSM already store an energy carrier (GWh) natively —
# used as-is. The other 8 INDUSTRY_DSM_TECHS store a MASS carrier
# (kt-of-product, so they can't just be summed into a GWh total):
# get_dsm_energy_equivalent instead converts each product's
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


def _production_energy_intensity(r, carrier: str, flow_in_all: pd.DataFrame) -> pd.Series:
    """GWh input energy per kt output for `carrier`, by year — summed across
    every technology that actually produces it that year (its real
    technology mix), using each producer's TOTAL energy input (every input
    carrier summed; already confirmed unit-homogeneous, all GWh, via
    Results.get_unit())."""
    # kt, index=technology, columns=year — get_carrier_production's logic, but
    # on the memoized flow_conversion_output: it re-reads the frame (~7 s)
    # on every call, and this runs once per DSM product.
    flow_out = _cached_total(r, "flow_conversion_output")
    if carrier not in flow_out.index.get_level_values("carrier"):
        return pd.Series(dtype=float)
    prod = flow_out.xs(carrier, level="carrier").groupby("technology").sum()
    prod = prod[(prod.abs() > 1e-3).any(axis=1)]
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
    flow_in_all = _cached_total(r, "flow_conversion_input")
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
# — too much eyeballing required. v2 added a 2nd,
# separate delta bar starting at y=0 next to the base bar — better, but the
# delta bar was visually dwarfed sitting next to a much taller base bar
# (e.g. +250 GW next to a 2,707 GW base). v3 (this one): the delta bar
# still stands separately (so its own internal stack/composition/hatching
# stays legible) but FLOATS starting at the TOP of that year's base bar
# instead of at 0 — it lands at the height where it actually attaches to
# the existing system, with a thin dashed guide connecting the two, plus a
# "+X.X%" label. A "%change" is the natural complement to an absolute GW
# delta here because there's exactly
# ONE meaningful denominator (that year's own EU-wide base total) — no
# small-base blow-up risk.

DELTA_LABEL = r"$\Delta$ No flexibility"


def _base_and_delta_df(base_series: pd.Series, no_flex_series: pd.Series,
                       base_label: str = BASE_SCENARIO[1],
                       delta_label: str = DELTA_LABEL) -> pd.DataFrame:
    """[ZEN-Europe (base) absolute, Δ No flexibility minus base — signed,
    both directions] — index is the union of both series' technologies,
    missing entries filled with 0 before subtracting so a tech present in
    only one run still gets a correct (not NaN) delta. `base_label`/
    `delta_label` name the columns for other run pairs (fig51)."""
    all_idx = base_series.index.union(no_flex_series.index)
    base = base_series.reindex(all_idx, fill_value=0.0)
    no_flex = no_flex_series.reindex(all_idx, fill_value=0.0)
    return pd.DataFrame({base_label: base, delta_label: no_flex - base})


def _plot_base_and_floating_delta(
    dfs_by_year: dict[int, pd.DataFrame], title: str, unit: str, ax: plt.Axes,
    color_map: dict, hatch_map: dict, show_legend: bool = True, decimals: int = 0,
) -> None:
    """Per year: 2 adjacent bars — ZEN-Europe base (stacked normally from
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
    base_label, *delta_labels = dfs_by_year[years[0]].columns.tolist()
    group = len(delta_labels) + 2  # base + deltas + 1 gap slot
    bar_width = 0.8
    labeled: set[str] = set()
    positions_all: list[float] = []
    tick_labels_all: list[str] = []
    year_centers: list[float] = []
    y_max, y_min = 0.0, 0.0  # bar extents, for headroom above the "+X (+Y%)" labels

    for yi, year in enumerate(years):
        df = dfs_by_year[year]
        base_pos = yi * group
        positions_all.extend(base_pos + i for i in range(len(delta_labels) + 1))
        tick_labels_all.extend([base_label, *delta_labels])
        year_centers.append(base_pos + len(delta_labels) / 2)

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

        for di, delta_label in enumerate(delta_labels):
            delta_pos = base_pos + 1 + di
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
            y_max, y_min = max(y_max, base_total, top), min(y_min, bot)
            delta_total = df[delta_label].sum()
            pct = (delta_total / base_total * 100) if base_total else 0.0
            label_y, va = (top, "bottom") if delta_total >= 0 else (bot, "top")
            ax.text(delta_pos, label_y, f"{delta_total:+,.{decimals}f}\n({pct:+.1f}%)",
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
    # Headroom for the 2-line value labels above the tallest bar (and below
    # the lowest, if any delta goes negative) so they don't hit the title.
    span = y_max - y_min
    ax.set_ylim(y_min - (0.12 * span if y_min < 0 else 0.0), y_max + 0.12 * span)
    ax.axhline(0, color="black", linewidth=0.5)
    if show_legend:
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles[::-1], labels[::-1], bbox_to_anchor=(1.02, 1),
                      loc="upper left", fontsize=8, frameon=False)


def fig12_capacity_and_storage_base_and_delta(base_run: Run, no_flex_run: Run) -> None:
    """Power generation capacity (left) and storage annual energy discharged
    (right), side by side, 3 snapshot years each (2030/2040/2050, same
    SNAPSHOT_YEARS_POWER/tech scope as fig11) — each year cluster is base
    (absolute stack) + delta (floating from the base bar's own top, see
    _plot_base_and_floating_delta) with a "+X.X%" label. Replaces 2 earlier
    separate figures (one per panel) per user request to show both side by
    side in one figure instead. The former 3rd Δ Full flexibility bar was
    dropped per user request — only No flexibility vs. base is compared.
    -> SI_results/fig12_capacity_and_storage_base_and_delta.svg
    """
    _capacity_and_storage_base_and_delta(base_run, no_flex_run, BASE_SCENARIO[1], DELTA_LABEL,
                                         "fig12_capacity_and_storage_base_and_delta")


def fig51_capacity_and_storage_dsm_no_cost_vs_full_flex(full_run: Run, no_cost_run: Run) -> None:
    """fig12 for Full flexibility (absolute stack) vs. DSM no cost (336 h)
    (floating Δ bar) — same panels, years and tech scope as fig12; see
    fig50 for what the DSM no cost run changes.
    -> SI_results/fig51_capacity_and_storage_dsm_no_cost_vs_full_flex.svg
    """
    _capacity_and_storage_base_and_delta(full_run, no_cost_run, full_run.label,
                                         rf"$\Delta$ {no_cost_run.label}",
                                         "fig51_capacity_and_storage_dsm_no_cost_vs_full_flex")


def fig61_capacity_and_storage_full_flex_20ts_vs_10ts(full_run: Run, full_20ts_run: Run) -> None:
    """fig51 for Full flexibility with 10 (absolute stack) vs. 20 (floating
    Δ bar) representative time steps per year.
    -> SI_results/fig61_capacity_and_storage_full_flex_20ts_vs_10ts.svg
    """
    _capacity_and_storage_base_and_delta(full_run, full_20ts_run, "Full flexibility (10 ts)",
                                         rf"$\Delta$ {full_20ts_run.label}",
                                         "fig61_capacity_and_storage_full_flex_20ts_vs_10ts")


def _capacity_and_storage_base_and_delta(base_run: Run, no_flex_run: Run, base_label: str,
                                         delta_label: str, fig_name: str) -> None:
    """fig12's body for any run pair: `base_run` as the absolute stack
    (`base_label`), `no_flex_run` as the floating delta (`delta_label`)."""
    empty = pd.Series(dtype=float)
    base_cap = get_capacity(base_run.results, POWER_GEN_TECHS, "power")
    nf_cap = get_capacity(no_flex_run.results, POWER_GEN_TECHS, "power")
    # GWh -> TWh per user request (raw GWh totals like "522,721" are
    # unwieldy at print size; TWh keeps 3-4 significant digits instead).
    def discharge_twh(r: Run) -> pd.DataFrame:
        dis = get_storage_flows(r.results, BULK_STORAGE_TECHS + INDUSTRY_TES_TECHS, "flow_storage_discharge")
        dsm = get_dsm_energy_equivalent(r.results, DSM_ENERGY_STACK_ORDER, SNAPSHOT_YEARS_POWER)
        if not dsm.empty and dsm.values.sum() > 1e-3:
            dis = pd.concat([dis, dsm.sum().rename(INDUSTRY_DSM_LABEL).to_frame().T])
        return dis / 1000.0

    base_dis, nf_dis = discharge_twh(base_run), discharge_twh(no_flex_run)
    gen_by_year: dict[int, pd.DataFrame] = {}
    disch_by_year: dict[int, pd.DataFrame] = {}
    for year in SNAPSHOT_YEARS_POWER:
        gen_by_year[year] = _stack_ordered(
            _base_and_delta_df(base_cap.get(year, empty), nf_cap.get(year, empty),
                               base_label, delta_label), POWER_GEN_STACK_ORDER)
        disch_by_year[year] = _base_and_delta_df(base_dis.get(year, empty), nf_dis.get(year, empty),
                                                 base_label, delta_label) \
            .reindex(STORAGE_STACK_ORDER).fillna(0.0)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    with plt.rc_context({"hatch.linewidth": 0.5}):
        _plot_base_and_floating_delta(gen_by_year, "Power Generation Capacity", "GW", axes[0],
                                      color_map=POWER_GEN_COLOR_MAP, hatch_map=POWER_GEN_HATCH_MAP)
        _plot_base_and_floating_delta(disch_by_year, "Storage Annual Energy Discharged", "TWh", axes[1],
                                      color_map=STORAGE_COLOR_MAP, hatch_map={}, decimals=1)
    fig.tight_layout()
    savefig(fig, fig_name)


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


# ── 13: MGA axis construction (no data) ─────────────────────────────────────
# Purely illustrative, like fig11/fig12 — no solved points. Left: the real
# north/west/south/east geography (drawn the same way
# plot_country_groups_map.py / fig_country_groups_map.svg in
# data/outputs/figures/mga/ does — same Natural Earth polygons, same region
# split, same colors). Right: the axis matrix — one column per region, one
# row per metric (investment cost, mobility electrification, heating
# electrification, cumulative emissions), stacked three deep for the
# 2030/2040/2050 cumulative-to-year horizons. COLOR = region throughout
# (_MGA_AXIS_REGION_COLOR, same order as REGIONS/REGION_COLOR in
# mga_capex_periods_common.py); each cell carries its metric's pictogram.
#
# The map needs geopandas + the cached Natural Earth shapefile (data/
# naturalearth/, already downloaded by plot_country_groups_map.py). Falls
# back to a simple 4-wedge compass if geopandas/the shapefile aren't
# available, so fig13 still generates unconditionally in main().
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

# (row label, cell pictogram) top to bottom; "pylon" is drawn by _mga_pylon_icon.
_MGA_AXIS_METRICS = [
    ("% investment\ncost", "€"),
    ("% Mobility\nelectrification", "pylon"),
    ("% Heating\nelectrification", "Heat"),
    ("% cum.\nemissions", "C"),
]
_MGA_AXIS_YEARS = [2030, 2040, 2050]


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
                     fontsize=9, ha="center", va="center", color="white", fontweight="bold")
    map_ax.set_xlim(minx, maxx)
    map_ax.set_ylim(miny, maxy)
    map_ax.set_axis_off()
    return True


def _mga_pylon_icon(ax, cx: float, cy: float, h: float, color: str) -> None:
    """Small transmission-tower pictogram (mobility electrification row)."""
    top, bot = cy + h / 2, cy - h / 2
    leg = 0.32 * h
    kw = dict(color=color, linewidth=1.3, solid_capstyle="round", zorder=5)
    ax.plot([cx - leg, cx, cx + leg], [bot, top, bot], **kw)
    for frac, half in ((0.25, 0.30 * h), (0.48, 0.38 * h)):
        y = top - frac * h
        ax.plot([cx - half, cx + half], [y, y], **kw)
    # lattice: X-bracing between the arms and the base
    ys = [top - 0.48 * h, top - 0.74 * h, bot]
    for ya, yb in zip(ys[:-1], ys[1:]):
        wa = leg * (top - ya) / h
        wb = leg * (top - yb) / h
        ax.plot([cx - wa, cx + wb], [ya, yb], **kw)
        ax.plot([cx + wa, cx - wb], [ya, yb], **kw)


def fig13_mga_axis_construction() -> None:
    """Conceptual, non-data schematic of this work's MGA axes: the region
    map (left) and the region x metric axis matrix, stacked over the three
    cumulative-to-year horizons (right). See the module-level comment above
    for the visual grammar and data sources.
    """
    fig, ax = plt.subplots(figsize=(14, 5.6))
    ax.set_xlim(0, 25)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")

    # ── left: region map ────────────────────────────────────────────────
    if not _mga_region_map(ax, 0.0, 0.04, 0.33, 0.92):
        _mga_region_compass(ax, 4.0, 5.0, 3.2)

    # ── right: axis matrix ──────────────────────────────────────────────
    label_x0, label_w = 8.4, 3.0
    plane_x0, plane_w = 11.8, 9.6
    plane_y0, plane_h = 1.5, 6.4
    depth = 0.45  # offset of each later horizon's plane behind the previous one
    col_w, col_gap = 2.0, (plane_w - 4 * 2.0) / 5
    rows_top = plane_y0 + plane_h - 0.25
    row_h = (rows_top - plane_y0 - 0.65) / len(_MGA_AXIS_METRICS)  # leaves room for the year label

    # Back planes first (2050 farthest back), each labelled bottom-left.
    for i, year in reversed(list(enumerate(_MGA_AXIS_YEARS))):
        px, py = plane_x0 + i * depth * 1.6, plane_y0 - i * depth
        ax.add_patch(Rectangle((px, py), plane_w, plane_h, facecolor=eth_tint(_ETH_GREY, 0.8),
                                edgecolor="black", linewidth=1.0, zorder=1 + (2 - i) * 0.1))
        ax.text(px + 0.12, py + 0.05, str(year), fontsize=11, color="#808080",
                ha="left", va="bottom", zorder=1.5)

    for c, region in enumerate(_MGA_AXIS_REGIONS):
        color = _MGA_AXIS_REGION_COLOR[region]
        cx0 = plane_x0 + col_gap + c * (col_w + col_gap)
        cxm = cx0 + col_w / 2
        # region column background
        ax.add_patch(Rectangle((cx0, rows_top - len(_MGA_AXIS_METRICS) * row_h - 0.05), col_w,
                                len(_MGA_AXIS_METRICS) * row_h + 0.15, facecolor=eth_tint(color, 0.85),
                                edgecolor="#333333", linewidth=1.0, zorder=2))
        # region header above the stack
        ax.add_patch(FancyBboxPatch((cxm - 0.8, plane_y0 + plane_h + 0.35), 1.6, 1.0,
                                     boxstyle="round,pad=0.02,rounding_size=0.18",
                                     facecolor=color, edgecolor="#333333", linewidth=1.0, zorder=3))
        ax.text(cxm, plane_y0 + plane_h + 0.85, region.capitalize(), fontsize=12.5, color="white",
                 ha="center", va="center", zorder=4)
        for r, (_, icon) in enumerate(_MGA_AXIS_METRICS):
            cy = rows_top - (r + 0.5) * row_h
            ax.add_patch(FancyBboxPatch((cxm - 0.8, cy - row_h * 0.38), 1.6, row_h * 0.76,
                                         boxstyle="round,pad=0.02,rounding_size=0.18",
                                         facecolor=color, edgecolor="#333333", linewidth=1.0, zorder=3))
            if icon == "pylon":
                _mga_pylon_icon(ax, cxm, cy, row_h * 0.5, "white")
            else:
                ax.text(cxm, cy, icon, fontsize=13, color="white", ha="center", va="center", zorder=5)

    # metric row labels left of the stack
    for r, (label, _) in enumerate(_MGA_AXIS_METRICS):
        cy = rows_top - (r + 0.5) * row_h
        ax.add_patch(FancyBboxPatch((label_x0, cy - row_h * 0.38), label_w, row_h * 0.76,
                                     boxstyle="round,pad=0.02,rounding_size=0.18",
                                     facecolor=_ETH_GREY, edgecolor="#333333", linewidth=1.0, zorder=3))
        ax.text(label_x0 + label_w / 2, cy, label, fontsize=10.5, color="white", ha="center",
                 va="center", linespacing=1.15, zorder=4)

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


# ── fig20: total system cost, drilled down sector → industries → low-T heat ─
# Cumulative, discounted total system cost over the whole horizon (the
# optimisation objective, net_present_cost). Technology CAPEX+OPEX are
# discounted per year (same factor as get_annual_cost) and summed per
# technology, then the ~110 technologies are grouped into sectors. Carrier
# (fuel/import) and carbon-emission costs are not tied to a technology and form
# their own "Imported carriers" group (carbon cost is ~0: the budget is a hard constraint); any technology NOT listed in a sector below
# falls into "Others" (energy conversion/supply, CCS/DAC, hydrogen, heat for
# buildings/district heat, ...).
_FIG20_SECTOR_TECHS = {
    "Transport": ["BEV", "ICE_diesel", "ICE_petrol", "HDT_BET", "HDT_diesel", "HDT_FCEV", "fuel_cell",  # road
                  "ammonia_ICE_ship", "diesel_ICE_ship", "hydrogen_FC_ship", "methanol_ICE_ship"],  # ships
    "Power generation": [
        "photovoltaics", "wind_onshore", "wind_offshore", "nuclear", "reservoir_hydro", "run-of-river_hydro",
        "lignite_coal_plant", "hard_coal_plant", "oil_plant", "natural_gas_turbine", "natural_gas_turbine_CCS",
        "biomass_plant", "biomass_plant_CCS", "waste_plant",
        "battery", "pumped_hydro", "power_line",  # storage + grid grouped with power
    ],
}
# Industries, split by branch. Heating (+TES) and DSM are their own groups so
# the flexibility options stay visible; DSM techs are therefore NOT counted in
# their product's branch.
_FIG20_LOWT_HEAT_TECHS = INDUSTRY_HEATING_TECHS + INDUSTRY_TES_TECHS
_FIG20_INDUSTRY_GROUPS = {
    "Steel": ["BF_BOF", "BF_BOF_CCS", "EAF", "NG_DRI", "NG_DRI_CCS", "H2_DRI"],
    "Cement": ["cement_kiln", "cement_post_comb", "biomass_to_cement_fuel", "coal_to_cement_fuel",
               "hydrogen_to_cement_fuel", "waste_to_cement_fuel"],
    "Chemicals": ["haber_bosch", "olefin_from_methanol", "olefin_from_naphtha", "methanol_from_biomass",
                  "methanol_from_hydrogen", "methanol_from_natural_gas"],
    "Paper": ["paper_production"],
    "Food": ["food_production"],
    "Glass & ceramics": ["glass_production", "ceramic_production", "glass_post_comb", "ceramic_post_comb"],
    "Low-T heating (incl. TES)": _FIG20_LOWT_HEAT_TECHS,
    "DSM (all products)": INDUSTRY_DSM_TECHS,
}
_FIG20_SECTOR_COLORS = {
    "Transport": _ETH_BLUE, "Power generation": _ETH_BRONZE,
    "Industries": _ETH_RED, "Others": _eth_tint(_ETH_GREY, 0.45),
    "Imported carriers": _ETH_GREEN,
}
_FIG20_INDUSTRY_COLORS = {
    "Steel": _ETH_GREY, "Cement": _eth_tint(_ETH_GREY, 0.5), "Chemicals": _ETH_PURPLE,
    "Paper": _ETH_TURQUOISE, "Food": _ETH_GREEN, "Glass & ceramics": _ETH_BRONZE,
    "Low-T heating (incl. TES)": _ETH_RED, "DSM (all products)": _ETH_BLUE,
}


def fig20_cost_breakdown_sector_industry_heating(base_run: Run, no_flex_run: Run, full_run: Run) -> None:
    """Cumulative discounted total system cost (the objective) for ZEN-Europe base / No
    flexibility / Full flexibility, drilled down in 3 panels: (A) the whole
    system split into transport / power generation /
    industries / others; (B) industries only, by branch; (C) low-temperature
    industry heating only, by technology. Every bar is annotated with its
    value and its share of the total system cost (panel C also its share of
    industries); segment labels give the share of THAT panel's bar plus the
    absolute cost in bn EUR. The top bars share one absolute bn-EUR axis; the
    industry and heating rows are each zoomed by their own factor (identical
    across scenarios, shown with a magnifier + scale bar). Each bar's total is
    written behind it.

    The base run has no industry-specific technologies (no paper/food/glass/
    ceramic, no industry-specific heat pumps/boilers), so its industries and
    heating bars are not like-for-like with the two industry-heat scenarios.
    -> SI_results/fig20_cost_breakdown_sector_industry_heating.svg
    """
    runs = [base_run, no_flex_run, full_run]
    labels = [r.label for r in runs]
    costs = []
    npc_totals, carrier_tot = [], []
    for r in runs:
        years = get_available_years(r.results)
        dfac = _discount_factors(r.results, years)
        c = pd.Series(dtype=float)
        for y in years:
            cy = get_capex_by_technology(r.results, y).add(get_opex_by_technology(r.results, y), fill_value=0.0)
            c = c.add(cy * float(dfac.get(y, 0.0)), fill_value=0.0)
        costs.append(c / 1000)  # MEUR -> bn EUR
        npc_totals.append(float(get_annual_total_cost(r.results, years, discount=True).sum()) / 1000)
        carrier_tot.append(float(get_annual_cost(r.results, years, "cost_carrier", discount=True).sum()) / 1000)

    def grp(c: pd.Series, techs: list[str]) -> float:
        return float(c.reindex(techs).fillna(0.0).sum())

    industry_techs = [t for ts in _FIG20_INDUSTRY_GROUPS.values() for t in ts]
    sector_df = pd.DataFrame({
        lab: {**{s: grp(c, ts) for s, ts in _FIG20_SECTOR_TECHS.items()},
              "Industries": grp(c, industry_techs)}
        for lab, c in zip(labels, costs)})
    sector_df.loc["Others"] = [float(c.sum()) for c in costs] - sector_df.sum()
    sector_df.loc["Imported carriers"] = carrier_tot
    sector_df = sector_df.loc[list(_FIG20_SECTOR_COLORS)]
    ind_df = pd.DataFrame({lab: {g: grp(c, ts) for g, ts in _FIG20_INDUSTRY_GROUPS.items()}
                           for lab, c in zip(labels, costs)})
    heat_techs = [t for t in HEAT_SUPPLY_STACK_ORDER if any(t in c.index for c in costs)] \
        + [t for t in INDUSTRY_TES_TECHS if any(t in c.index for c in costs)]
    heat_df = pd.DataFrame({lab: {t: float(c.get(t, 0.0)) for t in heat_techs}
                            for lab, c in zip(labels, costs)})
    # Collapse TES (all ~0) into one row so the legend stays short.
    tes_rows = [t for t in heat_df.index if t in INDUSTRY_TES_TECHS]
    if tes_rows:
        heat_df.loc["industry_TES"] = heat_df.loc[tes_rows].sum()
        heat_df = heat_df.drop(index=tes_rows)
    heat_df = heat_df[heat_df.abs().sum(axis=1) > 1e-6]
    heat_colors = {**HEAT_SUPPLY_COLOR_MAP, "industry_TES": _eth_tint(_ETH_BRONZE, 0.3)}

    from matplotlib.patches import Patch
    heat_pretty = lambda t: (t.replace("heat_pump_industry_", "HP ").replace("_boiler_industry", " boiler")
                              .replace("_waste_heat", " waste heat").replace("_water", " water")
                              .replace("_", "-").replace("industry-TES", "TES"))

    _bn = lambda v: f"{v:,.0f} bn" if abs(v) >= 10 else f"{v:,.1f} bn" if abs(v) >= 0.1 else f"{v:.2f} bn"

    x_max = max(npc_totals) * 1.13  # one shared bn-EUR scale for every bar

    def draw_row(ax, y, df_col, colors, names, hatch_map=None, min_label=0.05, f=1.0):
        """One bar; lengths are value * f (f = zoom factor of this row type, same for
        all scenarios). Returns {name: (left, right)} in axis units.
        Labels: share of THIS bar + absolute value; bar total written behind the bar."""
        tot = df_col.sum()
        pos, left = {}, 0.0
        for n in df_col.index:
            v = float(df_col[n])
            if v <= 0:
                continue
            w = 100 * v / tot
            ax.barh(y, v * f, left=left, height=0.56, color=colors[n], edgecolor="white", linewidth=0.8,
                    hatch=(hatch_map or {}).get(n))
            if v * f / x_max >= min_label:
                ax.text(left + v * f / 2, y, f"{names(n)}\n{w:.1f}%\n{_bn(v)}", ha="center", va="center",
                        fontsize=8, color=_text_color_for_bg(colors[n]), fontweight="bold",
                        bbox=dict(fc=colors[n], ec="none", pad=1.5) if (hatch_map or {}).get(n) else None)
            else:
                pass  # too narrow for an in-bar label; identified via the legend
            pos[n] = (left, left + v * f)
            left += v * f
        x_txt = left + 0.006 * x_max
        ax.text(x_txt, y + (0.14 if f != 1.0 else 0), _bn(tot), ha="left", va="center", fontsize=9, fontweight="bold")
        return pos

    def connector(ax, y_top, y_bot, seg, tot_bot):
        for xa, xb in zip(seg, (0, tot_bot)):
            ax.plot([xa, xb], [y_top - 0.25, y_bot + 0.25], color="#555555", linestyle="--", linewidth=0.8)

    # Lower rows are "zoomed in": one factor per row type, identical across scenarios,
    # chosen so the largest bar of that type spans ~82% of the axis.
    f_ind = 0.82 * x_max / max(float(ind_df[lab].sum()) for lab in labels)
    f_heat = 0.82 * x_max / max(float(heat_df[lab].sum()) for lab in labels)

    def magnifier(ax, y, f, x0):
        """Magnifier icon + zoom factor + scale bar, tucked under the row's total label (at x0)."""
        ax.plot([x0 + 0.008 * x_max], [y - 0.06], marker="o", markersize=10, mfc="none", mec="#333333",
                mew=1.6, clip_on=False)
        ax.plot([x0 + 0.014 * x_max, x0 + 0.022 * x_max], [y - 0.11, y - 0.19], color="#333333", lw=2.2,
                solid_capstyle="round")
        ax.text(x0 + 0.03 * x_max, y - 0.06, f"zoom ×{f:.0f}", fontsize=8, va="center", ha="left")
        L = min([1, 2, 5, 10, 20, 50, 100, 200], key=lambda b: abs(b * f - 0.08 * x_max))
        ax.plot([x0, x0 + L * f], [y - 0.28, y - 0.28], color="#333333", lw=2)
        ax.text(x0 + L * f + 0.005 * x_max, y - 0.28, f"{L} bn", fontsize=7.5, va="center")

    # Panels without a heating row (e.g. base run) are cropped and given less height
    y_lo = [-0.45 if float(heat_df[lab].sum()) > 1e-6 else 0.55 for lab in labels]
    fig, axes = plt.subplots(3, 1, figsize=(15, 13.5),
                             gridspec_kw={"height_ratios": [3.1 - lo for lo in y_lo]})
    for k, (ax, lab) in enumerate(zip(axes, labels)):
        heat_k = float(heat_df[lab].sum())
        ax.text(0, 2.62, lab, fontsize=11.5,
                fontweight="bold", va="bottom")
        pos1 = draw_row(ax, 2, sector_df[lab], _FIG20_SECTOR_COLORS, lambda n: n)
        ind_tot = float(ind_df[lab].sum())
        connector(ax, 2, 1, pos1["Industries"], ind_tot * f_ind)
        pos2 = draw_row(ax, 1, ind_df[lab], _FIG20_INDUSTRY_COLORS,
                        lambda n: n.replace(" (incl. TES)", "").replace(" (all products)", "").replace("Glass & ceramics", "Glass &\nceramics"),
                        f=f_ind, min_label=0.035)
        magnifier(ax, 1, f_ind, ind_tot * f_ind + 0.006 * x_max)
        if heat_k > 1e-6:
            connector(ax, 1, 0, pos2["Low-T heating (incl. TES)"], heat_k * f_heat)
            draw_row(ax, 0, heat_df[lab], heat_colors,
                     lambda t: heat_pretty(t).replace(" waste heat", "\nwaste heat").replace(" water", "\nwater"),
                     hatch_map=HEAT_SUPPLY_HATCH_MAP, min_label=0.06, f=f_heat)
            magnifier(ax, 0, f_heat, heat_k * f_heat + 0.006 * x_max)
        ax.set_xlim(0, x_max); ax.set_ylim(y_lo[k], 3.1)
        ax.set_yticks([])
        ax.spines[["left", "right", "top"]].set_visible(False)
        if k < len(labels) - 1:
            ax.spines["bottom"].set_visible(False)
            ax.set_xticks([])
        else:
            ax.set_xlabel("Cumulative discounted cost [bn EUR] — axis valid for the top bars only; industry and heating rows are zoomed (see scale bars)", fontsize=9)
            ax.tick_params(labelsize=8)
    handles = ([Patch(color=c, label=n) for n, c in _FIG20_SECTOR_COLORS.items()]
               + [Patch(color=c, label=f"(industries) {n}") for n, c in _FIG20_INDUSTRY_COLORS.items()]
               + [Patch(facecolor=heat_colors[n], hatch=HEAT_SUPPLY_HATCH_MAP.get(n), edgecolor="white",
                        label=f"(heating) {heat_pretty(n)}") for n in heat_df.index])
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.955), ncol=5, fontsize=7.5, frameon=False)
    fig.suptitle("Total system cost, cumulative (discounted): system → industries → low-T heating",
                 fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    savefig(fig, "fig20_cost_breakdown_sector_industry_heating")


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"Loading {len(SCENARIOS)} euler scenarios...")
    runs = load_scenarios()
    snap_snapshot_years(runs)
    print("Computing headline metrics (cost, emissions, capacity)...")
    metrics = compute_headline_metrics(runs)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(FIGURES_DIR / "headline_metrics.csv")
    print(f"  wrote {(FIGURES_DIR / 'headline_metrics.csv').relative_to(REPO_ROOT)}")

    print(f"Loading base scenario ({BASE_SCENARIO[1]})...")
    base = load_base_scenario()
    print(f"Loading {NO_FLEX_SINGLE_TEMP_SCENARIO[1]!r} scenario...")
    no_flex_single = load_no_flex_single_temp_scenario()
    print(f"Loading {DSM_NO_COST_SCENARIO[1]!r} scenario...")
    dsm_no_cost = load_dsm_no_cost_scenario()
    print(f"Loading 20 ts scenarios...")
    full_20ts = load_extra_scenario(FULL_FLEX_20TS_SCENARIO)
    no_flex_20ts = load_extra_scenario(NO_FLEX_20TS_SCENARIO)

    by = {r.label: r for r in runs}
    no_flex = by.get("No flexibility")
    full = by.get("Full flexibility")
    single_temp = by.get("Single temperature level")
    dsm_pess = by.get("DSM pessimistic")
    available = {"base": base, "No flexibility": no_flex, "Full flexibility": full,
                 "Single temperature level": single_temp, "DSM pessimistic": dsm_pess,
                 NO_FLEX_SINGLE_TEMP_SCENARIO[1]: no_flex_single,
                 DSM_NO_COST_SCENARIO[1]: dsm_no_cost,
                 FULL_FLEX_20TS_SCENARIO[1]: full_20ts}

    def run_if(needs: list[str], fn, *args) -> None:
        """Call fn(*args) if every scenario in `needs` is loaded, else print a skip line."""
        missing = [n for n in needs if available[n] is None]
        if missing:
            print(f"  skipping {fn.__name__}: {', '.join(missing)} not loaded")
        else:
            fn(*args)

    print("Generating figures...")
    # results
    if base is not None:
        fig0a_cost_composition(compute_cost_components([base] + runs))
    else:
        print("  skipping fig0a_cost_composition: base not loaded")
    run_if(["base", "No flexibility", "Full flexibility"],
           fig0b_emissions_source_comparison, base, no_flex, full)
    run_if(["Full flexibility", "DSM pessimistic"], fig5b_dsm_discharge_by_product, runs)
    run_if(["Single temperature level"], fig3b_heat_pathway, runs)
    run_if(["base", "No flexibility"], fig5_retrofit_ccs_comparison, no_flex, base)
    run_if(["No flexibility"], fig8a_diffusion_mechanisms_heat_pumps, runs)
    run_if(["No flexibility", "Full flexibility"], fig9_heat_supply_trajectory, no_flex, full)
    run_if(["base", "No flexibility"], fig12_capacity_and_storage_base_and_delta, base, no_flex)
    single_temp_set = ["No flexibility", NO_FLEX_SINGLE_TEMP_SCENARIO[1], "Full flexibility",
                       "Single temperature level"]
    for fn in (fig14a_heat_supply_electrification_singletemp_vs_full,
               fig14b_cost_and_emissions_totals_singletemp_vs_full, fig30_matrix):
        run_if(single_temp_set, fn, no_flex, no_flex_single, full, single_temp)
    run_if(["No flexibility"], fig15_heat_supply_output_twh_for,
           runs, "No flexibility", "fig15a_heat_supply_output_no_flexibility_twh")
    run_if(["Full flexibility"], fig15_heat_supply_output_twh_for,
           runs, "Full flexibility", "fig15b_heat_supply_output_full_flexibility_twh")
    run_if(["base", "No flexibility", "Full flexibility"],
           fig20_cost_breakdown_sector_industry_heating, base, no_flex, full)
    run_if(["No flexibility", "Full flexibility"], fig40_flex_scenarios, runs)
    run_if(["No flexibility", "Full flexibility"], fig41_flex_scenarios_table, runs)
    run_if(["No flexibility", "Full flexibility"], fig42_flex_decomposition, runs)
    run_if(["No flexibility", "Full flexibility"], fig43_flex_scenarios_table_curtailment, runs)
    run_if(["Full flexibility", DSM_NO_COST_SCENARIO[1]], fig50_dsm_no_cost_vs_full_flex,
           full, dsm_no_cost)
    run_if(["Full flexibility", DSM_NO_COST_SCENARIO[1]],
           fig51_capacity_and_storage_dsm_no_cost_vs_full_flex, full, dsm_no_cost)
    # No flexibility 20 ts missing -> 10 ts run as a marked placeholder.
    run_if(["No flexibility", "Full flexibility", FULL_FLEX_20TS_SCENARIO[1]], fig31_matrix_tsa,
           no_flex, no_flex_20ts or no_flex, full, full_20ts, no_flex_20ts is None)
    run_if(["Full flexibility", FULL_FLEX_20TS_SCENARIO[1]], fig60_full_flex_20ts_vs_10ts,
           full, full_20ts)
    run_if(["Full flexibility", FULL_FLEX_20TS_SCENARIO[1]],
           fig61_capacity_and_storage_full_flex_20ts_vs_10ts, full, full_20ts)

    # method/
    run_if(["No flexibility"], fig4b_industry_fuel_demand_comparison, runs)
    fig8_industry_sector_emissions_context()
    fig9_model_scope_coverage()
    fig15_global_ghg_sector_breakdown()
    fig11_mga_method()
    fig13_mga_axis_construction()
    fig14_mga_exploration_sequence()
    print(f"Done. Figures in {FIGURES_DIR.relative_to(REPO_ROOT)}/")

if __name__ == "__main__":
    main()
