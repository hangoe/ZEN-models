"""Compare the MGA exploration modes/variants (weights, bbo, sampling,
optionally oracle) run against
Crystal_Ball_ind_heat_v8_0_no_flexibility_nodiffusion on Euler.

As of the CAPEX-axes switchover (2026-08-20), the design-axis set is a
13-axis regional CAPEX system: 4 node clusters (north/west/south/east) x 3
carrier groups (power/hydrogen/carbon) = 12 node_capex_tech axes (each a sum
of CAPEX over that cluster's technologies in that carrier group -- see each
run's own polytope.npz axis_meta_json for the exact technology membership
per group), plus net_present_cost. This replaces an earlier 9-design-axis
cost-axes system (nuclear, photovoltaics, wind_offshore, wind_onshore,
electrolysis, DAC, battery, ccs_lump, net_present_cost) whose runs were
deleted from disk by user request once the CAPEX runs landed -- this script
now has exactly ONE data source, used by every figure including fig3a/b (an
earlier version of this script kept fig3a/b on the old cost-axes runs
specifically; that was reverted the same day once the old runs were
deleted). If a stale comment or docstring elsewhere in this file still
describes the old 9-axis system, treat it as historical background on how
the axis set evolved, not current behaviour.

bbo and sampling were each run once per plugins.mga.normalisation setting --
"relative" (the original per-axis-bounds scaling), "units" (raw
physical-unit scaling), and "minmax" (each axis's own near-optimal [min,
max] mapped onto [0, 1]). Only "units" has been run against the new CAPEX
axes so far -- per user request, "units" IS the normalisation to use for
CAPEX (unlike the old cost-axes system, where "units" was explicitly
excluded and "relative"/"minmax" were the ones plotted instead). So
SUPF_MODES currently holds exactly two real runs: bbo_units, sampling_units.
Both solve the same epsilon=0.1 near-optimal space around the same
baseline, so their results live in one shared coordinate system and overlay
directly; on disk each saves under its own
..._MGA_CAPEX_<mode>_<normalisation>/..._<mode>_summary/ (data/outputs/
euler_outputs_mga/) -- the folder's own name carries the normalisation
suffix, but the Postprocess subfolder inside it is still named after the
bare mode ("..._bbo_summary", "..._sampling_summary"), see BASE_MODE.
CAPEX minmax and batch (BATCH_MODES, both empty for CAPEX right now) runs
are planned but not downloaded yet -- adding one later is just appending to
SUPF_MODES/BATCH_MODES/BATCH_RUN_SUFFIX, no other code changes needed, since
every figure below iterates those tuples rather than hard-coding mode names.

sampling and bbo both run through pyoNearOpt's generic supf_explore harness
(near_optimal_tools' shared support-function polytope bookkeeping) and only
differ in how the next direction to query is picked: sampling scores many
candidate directions and takes the largest observed inner/outer gap; bbo
searches for that direction with a black-box optimiser (SHADE) instead.
normalisation is an orthogonal axis (how directions are scaled while
searching), not a third strategy, hence the naming.

This script picks whichever of the plotted supf-mode runs (SUPF_MODES)
loads first, in SUPF_MODES order, as the canonical shared frame for axis
names/units/z*/scale/offset (used by fig0 and fig1), and prints a sanity
check comparing every pair of loaded runs' baselines (they solve the same
cost-optimal model, so z* should agree to full floating-point precision
regardless of mode or normalisation). For fig2 -- the one this project
actually cares about *comparing* modes on -- each run gets its own
inner-hull sample and its own panel; see that function's docstring.

As of the batch16 switchover (2026-08-25), MODEL/SUPF_MODES/BATCH_MODES
below point at Crystal_Ball_ind_heat_v9_0 (not v8_0) and a single "batch16"
BATCH_MODES entry -- the first batch-mode run downloaded for the CAPEX axis
set, batch_size=16 (see plugin.py's ForkedBatchSupportFunction). There is no
weights mode or bbo_units/sampling_units SUPF_MODES run for v9_0 yet, so
SUPF_MODES=() and the shared coordinate frame (frame_mode, see main()) now
falls back to BATCH_MODES when SUPF_MODES is empty. "weights" mode support
(fig0_weights_axis_bars, WEIGHTS_ITERATIONS, load_weights_points, WEIGHTS_DIR)
was removed entirely rather than left to no-op: it targeted individual
TECHNOLOGIES (photovoltaics/wind/nuclear via capacity_addition, see
zen_garden_plugins.mga.plugin.MGA._build_weight_array), not any region or
CAPEX-money quantity, despite living in a "..._MGA_CAPEX_weights" folder --
misleading enough that this project retired it in favour of the real
per-region/per-carrier-group VMM max/min solves that batch16 (and any future
BATCH_MODES/SUPF_MODES run against config_mga_axes_capex.json) actually
provides. That real regional-CAPEX view (fig0a/b/c: baseline vs each axis's
own VMM max/min, and cross-effects on every other axis) lives in
scripts/plot_mga_batch16_regional_capex.py, not here -- this script no longer
has a fig0 of its own. The pre-batch16 v8_0 CAPEX-weights/bbo_units/
sampling_units figures (including the old fig0_weights_axis_bars) were moved
to data/outputs/figures/mga_tests/archive/ rather than deleted outright.

As of the CAPEX-periods switchover (2026-08-26), RUN_PREFIX/BATCH_MODES
below point at a NEW axis set -- config_mga_axes_capex_periods.json, not
config_mga_axes_capex.json -- run against a full 2020-2050 pathway
("2020_7a_5a_interval_3ts", not the earlier single-2050-year
"2050_1a_5a_interval_5ts"), batch_size=4 ("batch4", not "batch16"). 4 node
clusters (north/west/south/east) x 2 calendar-year periods ([2030, 2039],
[2040, 2049]) = 8 node_capex_period axes, plus net_present_cost -- 9 axes
total now, not 13 (this file's older comments/docstring prose below still
say "13-axis"/"regional CAPEX system" describing the batch16 carrier-group
run; treat those as historical background on how the axis set evolved, same
as this file already does for the pre-batch16 v8_0 system -- nothing about
the *methodology* below changed, only which run's polytope.npz is read).
The old batch16 carrier-group figures live in data/outputs/figures/
mga_tests/archive_v9_0_capex_regional_batch16_groups/ (fig0a/b/c, per
carrier group -- that run's own fig0a/b, per period, which replaced them,
were deleted outright once fig4a/b superseded them in turn -- see the next
switchover paragraph below). axis_value() below has a new
"node_capex_period" branch (kind == NODE_CAPEX_PERIOD in the plugin) to
mirror this run's axes; still exactly follows MGA.axis_value/
_design_axis_terms.

As of the CAPEX-cumulative/share switchover (2026-08-28), RUN_PREFIX/
BATCH_MODES below point at YET ANOTHER new axis set -- config_mga_axes_
capex_cum.json's node_capex_cumulative, not config_mga_axes_capex_
periods.json's node_capex_period -- run with normalisation="share" (see
polytope_io.py's module docstring: one fixed reference total shared by
every node_capex_cumulative axis, rather than each axis's own near-optimal
[min, max] range; this only affects how the solver's search directions
were scaled while exploring, not any physical value plotted here, since
everything below reads poly.to_phys()). Same 4 node clusters
(north/west/south/east), but now x 2 CUMULATIVE horizons (until_year in
[2040, 2050], each summing that region's cost_capex_yearly over every
model year up to and including its own until_year, not a disjoint calendar
period) = 8 node_capex_cumulative axes, plus net_present_cost -- still 9
axes total, batch_size=4 ("batch4"). The old CAPEX-PERIODS batch4 (minmax
normalisation) fig1/fig2/fig3a/fig3b live in data/outputs/figures/
mga_tests/archive_v9_0_capex_periods_batch4_minmax/ -- that run's own
crosseffects figure (fig4a/b, from the now-deleted plot_mga_periods_
regional_capex.py) was deleted outright rather than archived once
plot_mga_cum_regional_capex.py's fig10 (own-axis flexibility + cross-effects
for both until_years merged into one matrix -- an intermediate fig9a/b
split version was itself deleted once fig10 superseded it too) superseded
it; the shared run-loading infra that script also provided now lives in
mga_capex_periods_common.py (still used by plot_mga_regional_investment.py's
fig7/8 and plot_mga_investment_map.py, both independent of fig4's
existence). axis_value()
below has a new "node_capex_cumulative" branch (kind ==
NODE_CAPEX_CUMULATIVE in the plugin, period=(None, until_year)) alongside
the still-present "node_capex_period" branch (kept for historical/
reference use, not exercised by this run); both exactly follow
MGA.axis_value/_design_axis_terms.

oracle has no data under the CAPEX axis set at all right now -- every
oracle-touching code path below degrades to "skip, log why" exactly as it
always did when ORACLE_DIR doesn't exist, so this is a live, ready-to-use
path for a future oracle re-run against the CAPEX axes, not dead code. See
the pre-existing docstrings on load_oracle_points and load_oracle_native_gap
for the full reasoning (best-effort folder reconstruction if only a partial
polytope survives; fig3 would include oracle on max_separation only, via its
own certified max_min_distance, once such a run exists).

Convergence metric (fig3): pyoNearOpt.metrics.fraction_well_explored and
max_separation (the same machinery behind sampling/bbo/batch's own
ci_convergence_metric/batch_oracle convergence check and oracle's own max-min
distance), evaluated on each mode's growing set of known near-optimal points
against ITS OWN live, evolving outer approximation. max_separation (a MILP)
is actually solved here, at sparse checkpoints, against sampling/bbo/batch's
own cut history fully reconstructed (see load_native_outer_at/
load_native_outer_at_batch) or oracle's own certified gap read directly off
its own diagnostics (see load_oracle_native_gap). ci_lower needs no solving
at all for sampling/bbo/batch: it IS each of their own live convergence
checks, already logged into their diagnostics.csv once per iteration, so it
is read straight off disk at full per-iteration density instead (see
load_native_ci_history) -- oracle has no ci_lower equivalent at all (see
that function's docstring). An earlier version of this figure also scored every
mode against one shared, FROZEN initial outer box (the un-cut VMM box before
any refinement) as a second row, so all modes had one common ruler despite
each building a different real approximation. That row was dropped: scoring
against a box that never shrinks conflates "coverage of a fixed region" with
actual convergence, and made every mode look like it stalled well before it
actually had (each mode's real, evolving approximation kept shrinking
substantially past the point the frozen-box metric stopped moving).

Figures (data/outputs/figures/mga_tests/):
  fig1_pairwise_points           pairwise projections of every mode/variant's
                                 actual visited points, colour-coded by mode.
  fig2_polytope_samples          One panel per plotted supf-mode run with its
                                 own polytope (bbo_units, sampling_units, and
                                 oracle once re-downloaded against the CAPEX
                                 axes -- see SUPF_MODES/ALL_SUPF_MODES). Each
                                 panel is a full n_axes x n_axes grid rather
                                 than just a lower triangle: lower triangle =
                                 hexbin density of a uniform sample of THAT
                                 run's own INNER approximation
                                 (rejection-sampled from its own outer body --
                                 see rejection_sample_inner's docstring and
                                 Steen2026_Thesis Sec 3.3) with a green outline
                                 for the exact 2D projection of that run's
                                 inner hull and every mode/variant's actual
                                 points overlaid for context; diagonal =
                                 per-axis marginals; upper triangle = that
                                 pair's Pearson correlation over the same
                                 inner-hull sample (Steen2026_Thesis Figure 7
                                 analog -- which axes substitute (negative) or
                                 move together (positive) across the
                                 near-optimal volume; on physical units purely
                                 for readability, Pearson r is invariant to
                                 per-axis affine rescaling so this doesn't
                                 change a single value). Side-by-side panels
                                 are the actual bbo-vs-sampling comparison
                                 this project wants -- weights never builds a
                                 polytope, so it never gets its own panel.
                                 A mode with too few accepted rejection
                                 samples (<20, see _hull_modes_to_plot) --
                                 e.g. an early-stage/few-iteration run whose
                                 inner hull is still a sliver relative to its
                                 outer approximation, so proposals essentially
                                 never land inside it -- falls back to
                                 plotting its own ACTUAL visited points
                                 directly instead (plain scatter, not hexbin;
                                 no overlay of itself in the lower triangle
                                 since that would just duplicate the primary
                                 scatter): see PANEL_DATA/_hull_panel_data.
                                 Real points, just sparser and noisier than a
                                 dense synthetic sample -- the panel title
                                 says which kind it is.
  fig3a/b_query/time_comparison  Two figures, columns are max_separation
                                 (solved here, sparse checkpoints) and
                                 fraction_well_explored's ci_lower (read
                                 natively off diagnostics.csv, full density,
                                 no solving -- see load_native_ci_history);
                                 fig3a's x-axis is number of model queries,
                                 fig3b's is cumulative real ZEN-garden
                                 solving time (log). One row: each run's own
                                 live, evolving approximation -- every
                                 plotted supf-mode run (currently bbo_units,
                                 sampling_units; reference-equivalent to
                                 near_optimal_tools' docs/examples/
                                 method_comparison.ipynb, see
                                 load_native_outer_at/
                                 load_native_outer_at_batch), oracle on
                                 max_separation only (see
                                 load_oracle_native_gap), weights absent (it
                                 never builds an approximation -- see fig0
                                 instead). fig3b's "seconds" axis is
                                 uncalibrated for both modes right now (see
                                 REAL_ELAPSED_SECONDS -- add a verified sacct
                                 total for bbo_units/sampling_units to fix).
                                 An earlier 2-row version also scored every
                                 mode against one shared frozen initial box;
                                 dropped, see the module docstring's
                                 "Convergence metric" section for why. This
                                 file's only per-mode convergence trace now
                                 (an earlier fig1_convergence and
                                 fig2_axis_range_comparison were dropped too:
                                 the former didn't add much beyond this
                                 figure's own max-separation/query panel, and
                                 the latter mostly just showed which modes
                                 ran VMM -- sampling/bbo/oracle all do, so
                                 they trivially span the full axis range,
                                 while weights doesn't and so trivially
                                 doesn't; not a real exploration comparison).

Usage:
    python scripts/plot_mga_results.py
"""

import json
import re
import warnings
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy.optimize import linprog

from plots.figure_settings import SCENARIO_PALETTE, apply_font_mode, eth_tint

# Match MT_report_HG's font -- see figure_settings.FONT_MODE for the
# rationale and for the one-flag toggle that switches every figure script in
# this repo (report/Computer Modern vs. presentation/Arial) at once.
apply_font_mode()
from zen_garden import Results
from zen_garden_plugins.mga.polytope_io import Polytope, load_polytope
from pyoNearOpt.metrics import max_separation
from pyoNearOpt.polytope_approximation.approximation_class import approximation
from pyoNearOpt.polytope_approximation.polytope_samples import PolytopeSamples

FIGURES_DIR = REPO_ROOT / "data" / "outputs" / "figures" / "mga_tests"
MGA_ROOT = REPO_ROOT / "data" / "outputs" / "euler_outputs_mga"

MODEL = "Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion"

# ── CAPEX-CUMULATIVE-axes run, share normalisation (current, 2026-08-28 --
# the cumulative/share switchover; see module docstring) -- the earlier
# CAPEX-PERIODS batch4 (minmax) fig1/fig2/fig3a/fig3b this script used to
# plot were moved to data/outputs/figures/mga_tests/
# archive_v9_0_capex_periods_batch4_minmax/, not deleted.
#
# 9-axis regional cumulative-CAPEX system: 4 node clusters
# (north/west/south/east) x 2 cumulative horizons (until_year in
# [2040, 2050]) = 8 node_capex_cumulative axes, plus net_present_cost -- see
# each run's own polytope.npz axis_meta_json for the exact node membership
# per region (config_mga_axes_capex_cum.json). batch4_tol002/batch6_tol002
# are the BATCH_MODES entries for this axis set (batch_size=4/6,
# strategy_mode="bbo" per config_mga_batch_bbo.json, normalisation="share",
# tolerance_explore=0.02 -- see the tol002-switchover note below);
# SUPF_MODES is empty
# until a v9_0 bbo_units/sampling_units run against this axis set is
# downloaded. Adding either later is just appending to SUPF_MODES/
# BATCH_MODES/BATCH_RUN_SUFFIX, no other code changes needed (BASE_MODE/
# RUN_DIR/MODE_COLOR/MODE_LABEL all key off these tuples).
RUN_PREFIX = f"{MODEL}_2020_7a_5a_interval_3ts_MGA_CAPEX_CUM"
ORACLE_DIR = MGA_ROOT / f"{RUN_PREFIX}_oracle"

SUPF_MODES: tuple[str, ...] = ()

# As of 2026-09-03, RUN_PREFIX/BATCH_MODES point at the tolerance_explore=0.02
# re-sweep of the same CAPEX-CUM/share axes (batch4_share/batch6_share above
# were tolerance_explore=0.01) -- task_id 15/16 in parameters_mga.csv.
# task_id 15's own job (12374944_15) FAILED on 2026-09-01 (a numerical issue
# in batch_ORACLE's add_cut, not a resource/config problem); task_id 17 is
# its retry under a fresh task_id, writing to the SAME output folder name
# (batch_bbo_share_batch4_tol002) -- that retry is what's actually on disk
# here, and it converged (223 iterations) on 2026-09-03. batch6_tol002
# (task_id 16) was still running on Euler as of this switchover -- left in
# BATCH_MODES so it appears automatically once its own run_dir is synced
# down (main() skips any mode whose polytope.npz isn't present yet).
BATCH_MODES: tuple[str, ...] = ("batch4_tol002", "batch6_tol002")
BATCH_RUN_SUFFIX: dict[str, str] = {
    "batch4_tol002": "batch_bbo_share_batch4_tol002",
    "batch6_tol002": "batch_bbo_share_batch6_tol002",
}
# Every mode with its own polytope.npz + outer approximation -- the set
# fig1/fig2/fig3 iterate over.
ALL_SUPF_MODES = SUPF_MODES + BATCH_MODES

RUN_DIR = {m: MGA_ROOT / f"{RUN_PREFIX}_{m}" for m in SUPF_MODES}
for m, suffix in BATCH_RUN_SUFFIX.items():
    RUN_DIR[m] = MGA_ROOT / f"{RUN_PREFIX}_{suffix}"
RUN_DIR["oracle"] = ORACLE_DIR
BASE_MODE = {m: m.split("_", 1)[0] for m in SUPF_MODES}
BASE_MODE.update({m: "batch" for m in BATCH_MODES})

# Colours reused from figure_settings.SCENARIO_PALETTE (the full 7-color ETH
# corporate swatch: blue, petrol, green, bronze, red, purple, grey), per this
# project's convention of never inventing a separate palette for print
# figures. _ETH_PETROL/_ETH_GREEN go to batch4_tol002/batch6_tol002
# respectively (batch4_share/batch6_share used _ETH_PETROL alone before the
# tol002 switchover, see above).
_ETH_BLUE, _ETH_PETROL, _ETH_GREEN, _ETH_BRONZE, _ETH_RED, _ETH_PURPLE = (
    SCENARIO_PALETTE[0], SCENARIO_PALETTE[1], SCENARIO_PALETTE[2],
    SCENARIO_PALETTE[3], SCENARIO_PALETTE[4], SCENARIO_PALETTE[5],
)
MODE_COLOR = {
    "batch4_tol002": _ETH_PETROL,
    "batch6_tol002": _ETH_GREEN,
    "oracle": _ETH_BRONZE,
}
MODE_LABEL = {
    "batch4_tol002": "Batch (bbo, batch=4, share, tol=0.02)",
    "batch6_tol002": "Batch (bbo, batch=6, share, tol=0.02)",
    "oracle": "Oracle",
}
MODES = (*ALL_SUPF_MODES, "oracle")

UNIT_LABEL = {
    "gigawatt": "GW", "gigawatt * hour": "GWh", "megaEuro": "MEUR",
    # DAC and ccs_lump are captured-emissions axes (capacity_type="power" but
    # physically a CO2 flow rate), not power capacity -- see the new axes'
    # "unit" field in each polytope.npz's meta.
    "kilotCO2eq / hour": "ktCO$_2$eq/h",
}


def savefig(fig: plt.Figure, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.svg"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {path.relative_to(REPO_ROOT)}")


# ── Shared data access ───────────────────────────────────────────────────

def safe_results(path: Path) -> Results | None:
    """Load a Results object, or None (with a logged reason) if the folder
    is missing, empty, or its h5 files are unreadable (e.g. truncated by an
    interrupted download -- see the oracle-mode note in the module docstring)."""
    if not path.exists() or not any(path.iterdir()):
        return None
    try:
        return Results(path=str(path))
    except Exception as exc:
        print(f"    unreadable: {path.name} ({exc!r})")
        return None


def axis_value(r: Results, axis_meta: dict) -> float:
    """One axis's physical value on a solved Results, matching
    zen_garden_plugins.mga.plugin.MGA.axis_value exactly: tech axes sum
    capacity_addition over members at the axis's capacity type; the carrier
    axis sums annual flow_import over members; node_capex_tech axes (the
    CAPEX-axes system, see module docstring) sum cost_capex_yearly over
    member nodes/technologies/years/capacity_types (mirrors
    MGA._design_axis_terms's _NODE_AGG_CAPEX + ["set_location"] reduction --
    every dim except set_location is always aggregated away, and
    set_location is restricted to axis_meta["members"] -- axis.technologies
    additionally restricts set_technologies when not None, same as
    _design_axis_terms's `if axis.technologies is not None` branch); the
    cost axis sums net_present_cost over years."""
    kind, members = axis_meta["kind"], axis_meta["members"]
    if kind == "total_cost":
        return float(r.get_total("net_present_cost").to_numpy().sum())
    if kind == "tech_capacity":
        cap = r.get_total("capacity_addition")
        cap = cap[cap.index.get_level_values("capacity_type") == axis_meta["capacity_type"]]
        vals = cap[cap.index.get_level_values("technology").isin(members)]
        return float(vals.to_numpy().sum()) if not vals.empty else 0.0
    if kind == "carrier_import":
        flow = r.get_total("flow_import")
        vals = flow[flow.index.get_level_values("carrier").isin(members)]
        return float(vals.to_numpy().sum())
    if kind == "node_capex_tech":
        capex = r.get_total("cost_capex_yearly")
        vals = capex[capex.index.get_level_values("location").isin(members)]
        technologies = axis_meta.get("technologies")
        if technologies is not None:
            vals = vals[vals.index.get_level_values("technology").isin(technologies)]
        return float(vals.to_numpy().sum()) if not vals.empty else 0.0
    if kind == "node_capex_period":
        # CAPEX-PERIODS axis set (config_mga_axes_capex_periods.json, see the
        # module docstring's periods-switchover note): same node-restriction
        # as node_capex_tech, but restricted to the axis's own calendar-year
        # period instead of a technology group -- get_total's DataFrame
        # columns are real calendar years (verified: compare_models.py/
        # figures_by_scenario.py both index them as `df[YEAR]` with YEAR an
        # actual year like 2025), matching MGA._axis_year_indices'
        # start <= real_year <= end convention (_year_indices_in_period)
        # exactly, just filtering on the year value directly instead of on
        # set_time_steps_yearly's index.
        capex = r.get_total("cost_capex_yearly")
        vals = capex[capex.index.get_level_values("location").isin(members)]
        start, end = axis_meta["period"]
        vals = vals[[c for c in vals.columns if start <= c <= end]]
        return float(vals.to_numpy().sum()) if not vals.empty else 0.0
    if kind == "node_capex_cumulative":
        # CAPEX-CUM axis set (config_mga_axes_capex_cum.json, see the module
        # docstring's cumulative/share-switchover note): same node-restriction
        # as node_capex_tech/node_capex_period, but summed over every model
        # year UP TO AND INCLUDING the axis's own until_year (axis_meta
        # ["period"] == (None, until_year) -- see plugin.py) rather than a
        # disjoint [start, end] calendar period.
        capex = r.get_total("cost_capex_yearly")
        vals = capex[capex.index.get_level_values("location").isin(members)]
        _, until_year = axis_meta["period"]
        vals = vals[[c for c in vals.columns if c <= until_year]]
        return float(vals.to_numpy().sum()) if not vals.empty else 0.0
    raise ValueError(f"unknown axis kind {kind!r}")


def point_from_results(r: Results, poly: Polytope) -> np.ndarray:
    """Physical-units point (n_axes,) in poly's axis order."""
    return np.array([axis_value(r, a) for a in poly.meta["axes"]], dtype=float)


def solving_time(folder: Path) -> float:
    """This solve's real wall time from ZEN-garden's own benchmarking.json,
    or NaN if the file is missing/unreadable (e.g. no real solve behind a
    point, as for the shared frame's z* borrowed for oracle -- see
    load_oracle_points). Used for fig3's time axis."""
    path = folder / "benchmarking.json"
    if not path.exists():
        return float("nan")
    try:
        return float(json.loads(path.read_text())["solving_time"])
    except Exception:
        return float("nan")


def try_load_run_polytope(run_dir: Path, mode: str, folder_mode: str | None = None) -> Polytope | None:
    """mode's own polytope.npz (sampling/bbo/oracle all save under
    ..._<folder_mode>_summary/, see supf_driver.py/oracle_driver.py), or None
    (logged) if the summary folder or its polytope*.npz is missing/unreadable
    -- e.g. oracle before its download lands, or an interrupted run whose
    summary was never written (see the module docstring). folder_mode
    defaults to mode; pass BASE_MODE[mode] for a bbo_relative/bbo_minmax/
    sampling_relative/sampling_minmax variant, whose Postprocess subfolder
    is still named after the bare mode alone (e.g.
    "..._bbo_summary")."""
    folder_mode = folder_mode or mode
    summary = run_dir / f"{MODEL}_{folder_mode}_summary"
    poly_files = sorted(summary.glob("polytope*.npz")) if summary.exists() else []
    if not poly_files:
        return None
    try:
        return load_polytope(poly_files[0])
    except Exception as exc:
        print(f"  {mode}: polytope present at {summary.relative_to(REPO_ROOT)} but unreadable ({exc!r})")
        return None


def load_supf_points(run_poly: Polytope, run_dir: Path,
                     iter_prefix: str = "supf_iter") -> list[tuple[str, np.ndarray, float]]:
    """[(label, phys_point, solving_time)] for any mode whose own polytope.npz
    point_origin follows the shared z_star/max:<axis>/min:<axis>/iterate
    convention (every mode does -- see polytope_io.py's schema) and whose
    refinement iterates are saved as one Postprocess folder per iterate,
    named ..._<iter_prefix>_<n>. Default iter_prefix="supf_iter" covers
    sampling/bbo (both share supf_explore's folder-naming); pass
    iter_prefix="oracle_iter" for oracle -- same point_origin convention,
    different folder name (oracle_driver.py's own per-iteration label), and
    unlike sampling/bbo it uses a KKT/MILP loop, not supf_explore, but that
    doesn't matter here since this function only maps points to folders and
    reads each one's own benchmarking.json, not the exploration logic."""
    iterate_count = 0
    rows = []
    for lab, pt in zip(run_poly.point_origin, run_poly.X):
        if lab == "z_star":
            folder = run_dir / MODEL
        elif lab == "iterate":
            iterate_count += 1
            folder = run_dir / f"{MODEL}_{iter_prefix}_{iterate_count}"
        else:  # "max:<axis>" / "min:<axis>"
            sense, axis = lab.split(":", 1)
            folder = run_dir / f"{MODEL}_vmm_{sense}_{axis}"
        rows.append((lab, run_poly.to_phys(pt), solving_time(folder)))
    return rows


def load_batch_points(run_poly: Polytope, run_dir: Path, batch_size: int) -> list[tuple[str, np.ndarray, float]]:
    """Same contract as load_supf_points, for a batch-mode run (BATCH_MODES):
    the folder-naming convention differs because batch_size points land per
    outer iteration instead of one -- disk folders are
    "..._iter<N>_<k>/", N the 1-indexed outer iteration, k the 0-indexed
    worker slot within it, in the same left-to-right order the run's own
    diagnostics.csv logged them (verified: iteration 0 in diagnostics.csv
    <-> on-disk "_iter1_*", i.e. disk numbering is diagnostics' iteration+1)."""
    iterate_idx = 0
    rows = []
    for lab, pt in zip(run_poly.point_origin, run_poly.X):
        if lab == "z_star":
            folder = run_dir / MODEL
        elif lab == "iterate":
            iteration_n, k = iterate_idx // batch_size + 1, iterate_idx % batch_size
            folder = run_dir / f"{MODEL}_iter{iteration_n}_{k}"
            iterate_idx += 1
        else:  # "max:<axis>" / "min:<axis>"
            sense, axis = lab.split(":", 1)
            folder = run_dir / f"{MODEL}_vmm_{sense}_{axis}"
        rows.append((lab, run_poly.to_phys(pt), solving_time(folder)))
    return rows


# ── Oracle mode (best-effort reconstruction, no polytope available) ──────
#
# Only used as a fallback when oracle has NO usable polytope.npz at all (see
# main(): whenever try_load_run_polytope succeeds for oracle, load_supf_points
# is used instead -- same as sampling/bbo, with real per-point solving times).
# This function exists for a run interrupted badly enough that even its own
# oracle_summary/ was never written (the scenario this project hit with an
# earlier, unrelated oracle run) -- it reconstructs whatever it can directly
# from the individual vmm_<sense>_<axis> and oracle_iter_N Postprocess
# folders, which survive independently of that summary.

def load_oracle_points(poly: Polytope) -> list[tuple[str, np.ndarray, float]] | None:
    """[("z_star", ...), ("max:<axis>"/"min:<axis>", ...)*, (iter_n, ...)*]
    in solve order, or None if nothing beyond z* is readable. See the
    section comment above for when this is used instead of load_supf_points."""
    design_axes = [a for a in poly.meta["axes"] if a["kind"] != "total_cost"]
    rows: list[tuple[str, np.ndarray, float]] = []
    n_vmm_ok = 0
    for sense in ("max", "min"):
        for a in design_axes:
            folder = ORACLE_DIR / f"{MODEL}_vmm_{sense}_{a['name']}"
            r = safe_results(folder)
            if r is None:
                continue
            n_vmm_ok += 1
            rows.append((f"{sense}:{a['name']}", point_from_results(r, poly), solving_time(folder)))

    iter_dirs = sorted(
        ORACLE_DIR.glob(f"{MODEL}_oracle_iter_*"),
        key=lambda p: int(p.name.rsplit("_", 1)[1]),
    )
    n_iter_ok = 0
    for d in iter_dirs:
        r = safe_results(d)
        if r is None:
            continue
        n_iter_ok += 1
        rows.append((d.name.rsplit("_", 2)[-2] + "_" + d.name.rsplit("_", 1)[1],
                     point_from_results(r, poly), solving_time(d)))

    print(
        f"  oracle: reconstructed from folders -- {n_vmm_ok}/{2 * len(design_axes)} VMM bound "
        f"solves and {n_iter_ok}/{len(iter_dirs)} iterations readable "
        f"(baseline folder is empty; z* taken from the shared frame)"
    )
    if n_vmm_ok == 0 and n_iter_ok == 0:
        print("  oracle: nothing readable -- dropping oracle from every figure")
        return None
    return [("z_star", poly.z_star_phys.copy(), float("nan"))] + rows



# ── fig1: pairwise projections of every mode's actual visited points ────

def _pairwise_grid(names: list[str], units: list[str], title: str, name: str, plot_fn) -> None:
    """plot_fn(ax, j, i) draws axis-pair (x=names[j], y=names[i]) into ax."""
    n = len(names)
    if n < 2:
        print(f"  skipping {name}: fewer than 2 design axes")
        return
    fig, axes = plt.subplots(n - 1, n - 1, figsize=(3.4 * (n - 1), 3.4 * (n - 1)), squeeze=False)
    for i in range(1, n):
        for j in range(0, n - 1):
            ax = axes[i - 1, j]
            if j >= i:
                ax.axis("off")
                continue
            plot_fn(ax, j, i)
            if i == n - 1:
                ax.set_xlabel(f"{names[j]}\n[{UNIT_LABEL.get(units[j], units[j] or 'n/a')}]", fontsize=11)
            else:
                ax.set_xticklabels([])
            if j == 0:
                ax.set_ylabel(f"{names[i]}\n[{UNIT_LABEL.get(units[i], units[i] or 'n/a')}]", fontsize=11)
            else:
                ax.set_yticklabels([])
            ax.tick_params(labelsize=9)
            ax.grid(alpha=0.25)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper right", fontsize=12, frameon=False)
    fig.suptitle(title, fontsize=16, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    savefig(fig, name)


def fig1_pairwise_points(poly: Polytope, points: dict[str, list[tuple[str, np.ndarray, float]]]) -> None:
    n = poly.n_axes
    modes = [m for m in MODES if m in points]

    def plot_fn(ax, j, i):
        for k, mode in enumerate(modes):
            phys = np.vstack([p for _, p, _ in points[mode]])
            ax.scatter(phys[:, j], phys[:, i], s=16, color=MODE_COLOR[mode], alpha=0.65,
                       edgecolor="white", linewidth=0.3,
                       label=MODE_LABEL[mode] if (i, j) == (1, 0) else None)
        ax.scatter(poly.z_star_phys[j], poly.z_star_phys[i], marker="D", s=60, color="black",
                   zorder=5, label="baseline (z*)" if (i, j) == (1, 0) else None)

    _pairwise_grid(poly.names, poly.units,
                   "MGA Explored Design Points by Mode (pairwise projections)",
                   "fig1_pairwise_points", plot_fn)


# ── Rejection sampling of the INNER approximation (Steen2026_Thesis Sec 3.3) ─
#
# The outer approximation O over-covers the true near-optimal space (it still
# contains volume no cut has excluded yet); the inner approximation I -- the
# convex hull of certified near-optimal points -- under-covers it, but every
# point of I is by construction an actual certified near-optimal design (a
# convex combination of real model solves). A first version of fig3 walked O
# directly with PolytopeSamples(use="outer"): fast, but most of the resulting
# cloud is "possibly near-optimal, not yet ruled out" rather than "confirmed
# near-optimal", and in early-converged runs (few points => O much bigger
# than I) that gap is large enough to visibly separate the sample cloud from
# the real certified points overlaid on it -- which read as "outside the
# approximation" even though every real point legitimately satisfies O.
# Following Steen2026_Thesis Sec 3.3 (Max Steen's ORACLE application to a
# larger ZEN-garden model, using the same pyoNearOpt/PolyRound/Vaidya-walk
# machinery as this script), the fix is to sample I instead, via rejection:
# walk O cheaply, keep only proposals that also satisfy I's convex-combination
# membership LP (X^T lambda = z, sum(lambda) = 1, lambda >= 0). The retained
# fraction estimates vol(I)/vol(O) (his Eq. 13) -- Steen's run of the full
# 10-D, 700-iteration ORACLE certificate got 11.6% over 9.3M proposals; see
# each mode's printed acceptance rate for how this run's 6-D sampling/bbo
# hulls compare (both are run separately now -- one cache/one acceptance
# rate per mode, see sampling_cache_path). Steen's own proposal count is well
# beyond this script's purpose; a few tens of thousands is enough for a
# readable density plot at the same statistical validity, just a noisier one.
def _poly_fingerprint(poly: Polytope) -> str:
    """Identifies which polytope a cached sample was drawn from, so a stale
    cache (e.g. after re-downloading a re-run mode) is detected and
    regenerated rather than silently reused."""
    import hashlib
    h = hashlib.sha256()
    h.update(poly.X.tobytes())
    h.update(poly.A.tobytes())
    h.update(poly.b.tobytes())
    return h.hexdigest()


def sampling_cache_path(mode: str) -> Path:
    """One cache file per mode (sampling/bbo/oracle each have their own
    independent polytope now, unlike the old single-"probabilistic" cache) --
    this doubles as the "re-run the sampling for both bbo and sampling
    outputs" step: each mode's inner-hull sample is a local, LP-only
    computation over its already-downloaded polytope.npz, run on this
    machine (not Euler -- there is no HPC-scale work here, just SciPy)."""
    return MGA_ROOT / "mga_inner_sampling" / f"rejection_sample_{mode}_inner.npz"


def cached_rejection_sample_inner(poly: Polytope, mode: str, n_propose: int = 30_000,
                                   seed: int = 0) -> tuple[np.ndarray, float]:
    """rejection_sample_inner, cached to sampling_cache_path(mode): the
    sampling in fig2 depends only on that mode's own polytope (fixed
    once the run is done), so redoing it on every script invocation is pure
    waste. Regenerates automatically if the polytope, n_propose, or seed have
    changed since the cache was written."""
    cache = sampling_cache_path(mode)
    fingerprint = _poly_fingerprint(poly)
    if cache.exists():
        cached = np.load(cache)
        if (str(cached["fingerprint"]) == fingerprint
                and int(cached["n_propose"]) == n_propose
                and int(cached["seed"]) == seed):
            print(f"  {mode}: using cached inner sample from {cache.relative_to(REPO_ROOT)} "
                  f"({len(cached['samples_norm'])} points, {float(cached['rate']):.2%} acceptance)")
            return cached["samples_norm"], float(cached["rate"])
        print(f"  {mode}: cached inner sample is stale (polytope/n_propose/seed changed); regenerating")

    samples_norm, rate = rejection_sample_inner(poly, n_propose, seed)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        cache, samples_norm=samples_norm, rate=rate,
        n_propose=n_propose, seed=seed, fingerprint=fingerprint,
    )
    print(f"  {mode}: cached inner sample to {cache.relative_to(REPO_ROOT)} ({len(samples_norm)} points, {rate:.2%} acceptance)")
    return samples_norm, rate


def rejection_sample_inner(poly: Polytope, n_propose: int, seed: int = 0) -> tuple[np.ndarray, float]:
    approx = approximation(A=poly.A, X=poly.X, b=poly.b, name_list=poly.names, print_lv=0)
    sampler = PolytopeSamples(approx, use="outer", walk_type="vaidya", print_lv=0)
    proposals = sampler.sample(n_steps=n_propose, seed=seed)

    X = poly.X
    m = X.shape[0]
    A_eq = np.vstack([X.T, np.ones(m)])
    bounds = [(0, None)] * m

    def in_inner(z: np.ndarray) -> bool:
        res = linprog(np.zeros(m), A_eq=A_eq, b_eq=np.concatenate([z, [1.0]]),
                       bounds=bounds, method="highs")
        return bool(res.success)

    accepted = np.array([z for z in proposals if in_inner(z)])
    rate = len(accepted) / len(proposals)
    return accepted, rate


# ── fig2: hexbin density (lower triangle) + Pearson correlation (upper
# triangle) of each mode's OWN inner hull ───────────────────────────────────
# Styled after Steen2026_Thesis Figure 6/7, merged into one n_axes x n_axes
# grid per mode instead of two separate square figures: the correlation
# matrix is symmetric (corr(i,j) == corr(j,i)), so the upper triangle would
# otherwise just duplicate the lower one -- putting the hexbin/hull sample
# density there instead (lower triangle) and the correlation cell (upper
# triangle) means every cell in the grid carries distinct information. Lower
# triangle: exact 2D projection of I as a green outline (a linear projection
# of a convex hull is the hull of the projected vertices, so this is just
# ConvexHull on poly.X's projected columns -- no extra approximation),
# per-axis marginal histograms on the diagonal, baseline marked, every mode's
# actual points overlaid for context. Upper triangle: that pair's Pearson
# correlation over the same inner-hull sample (which axes substitute
# (negative) or move together (positive) across the near-optimal volume; on
# physical units purely for readability -- Pearson r is invariant to
# per-axis affine rescaling, verified to agree with normalised draws to
# 1e-14, so this doesn't change a single value). Unlike the old 3-mode
# script (one shared hull, from "probabilistic"), sampling and bbo each get
# their OWN hull now -- neither is more "correct" than the other, they're
# independent runs of different direction-selection strategies over the same
# space -- so this is genuinely a bbo-vs-sampling comparison, not one hull
# with the other mode's points dropped on top. oracle gets a third panel
# automatically once its own oracle_summary/polytope.npz exists (see
# try_load_run_polytope); weights never builds a polytope and so never gets
# a panel here (see fig0 instead).
_HULL_MODE_ORDER = (*ALL_SUPF_MODES, "oracle")


# Minimum real points for the actual-points fallback panel (see
# _hull_panel_data): below this a scatter/histogram/correlation panel is too
# thin to say anything -- 5 is enough for a (very rough) Pearson estimate on
# a handful of axes, not a hard statistical threshold.
_MIN_ACTUAL_POINTS = 5


def _hull_panel_data(mode: str, polys: dict[str, Polytope], points: dict[str, list[tuple[str, np.ndarray, float]]],
                      samples: dict[str, tuple[np.ndarray, float]]):
    """(samples_phys, kind, rate_or_None) for one mode's fig2 panel: prefer
    the accepted rejection-sampled inner hull (kind="inner sample", >=20
    accepted -- see rejection_sample_inner); fall back to the mode's own
    actual visited points (kind="actual points", baseline + VMM + iterates,
    >=_MIN_ACTUAL_POINTS of them) when too few inner samples were accepted --
    e.g. an early-stage/few-iteration run whose inner hull (convex combo of
    only a handful of points) is still a sliver relative to its outer
    approximation, so rejection proposals essentially never land inside it
    (verified directly for one such run: 0/130,000 proposals accepted).
    Returns None if neither is usable for this mode."""
    if mode in samples and len(samples[mode][0]) >= 20:
        samples_norm, rate = samples[mode]
        return polys[mode].to_phys(samples_norm), "inner sample", rate
    if mode in points and len(points[mode]) >= _MIN_ACTUAL_POINTS:
        return np.vstack([p for _, p, _ in points[mode]]), "actual points", None
    return None


def _hull_modes_to_plot(polys: dict[str, Polytope], points: dict[str, list[tuple[str, np.ndarray, float]]],
                         samples: dict[str, tuple[np.ndarray, float]]) -> list[str]:
    return [m for m in _HULL_MODE_ORDER
            if m in polys and _hull_panel_data(m, polys, points, samples) is not None]


def fig2_polytope_samples(polys: dict[str, Polytope], points: dict[str, list[tuple[str, np.ndarray, float]]],
                           samples: dict[str, tuple[np.ndarray, float]]) -> None:
    modes_to_plot = _hull_modes_to_plot(polys, points, samples)
    if not modes_to_plot:
        print(f"  skipping fig2_polytope_samples: no mode has >=20 accepted inner samples "
              f"or >={_MIN_ACTUAL_POINTS} actual points")
        return

    from scipy.spatial import ConvexHull

    n_z = polys[modes_to_plot[0]].n_axes
    if n_z < 2:
        print("  skipping fig2_polytope_samples: fewer than 2 design axes")
        return
    overlay_modes = [m for m in MODES if m in points]

    # +1.3in/panel of extra width reserved (via subplots_adjust(right=...)
    # below) for the correlation colorbar, so it doesn't have to borrow space
    # from the grid's rightmost column -- borrowing squashed that column's
    # cells into rectangles instead of squares.
    colorbar_margin_in = 1.3
    fig = plt.figure(figsize=(3.3 * n_z * len(modes_to_plot) + 1.0 + colorbar_margin_in * len(modes_to_plot),
                               3.3 * n_z + 0.9))
    subfigs = fig.subfigures(1, len(modes_to_plot))
    subfigs = np.atleast_1d(subfigs)
    n_panels = len(modes_to_plot)
    for panel_idx, (subfig, mode) in enumerate(zip(subfigs, modes_to_plot)):
        poly = polys[mode]
        samples_phys, kind, rate = _hull_panel_data(mode, polys, points, samples)
        is_actual = kind == "actual points"
        corr = pd.DataFrame(samples_phys, columns=poly.names).corr(method="pearson")
        # Full n_z x n_z grid (unlike _pairwise_grid's (n-1) x (n-1)
        # off-diagonal-only layout used by fig1): row/col i==j is axis i's
        # own marginal, matching Steen2026_Thesis Figure 6. Reserve the top
        # of the subfig for the panel's own suptitle + (on the last panel)
        # the shared legend, and the right for the correlation colorbar, so
        # neither has to eat into the grid itself.
        axes = subfig.subplots(n_z, n_z, squeeze=False)
        panel_width_in = 3.3 * n_z + 1.0 / n_panels + colorbar_margin_in
        subfig.subplots_adjust(top=0.92, right=1 - colorbar_margin_in / panel_width_in)
        first_legend_done = False
        # Only the rightmost (last) panel keeps its legend -- with one panel
        # per mode, every panel's legend is otherwise identical (same overlay
        # modes/baseline/hull-outline label), so repeating it on every panel
        # only added clutter.
        show_legend = panel_idx == n_panels - 1
        corr_im = None
        for i in range(n_z):
            for j in range(n_z):
                ax = axes[i, j]
                if j > i:  # upper triangle: that pair's Pearson correlation, symmetric to (j, i)'s
                    # panel -- never on the grid's outer border (j>i implies j>=1 and i<=n_z-2), so
                    # it needs no axis-name labels of its own; those already come from (j, i)'s panel.
                    v = corr.iloc[i, j]
                    corr_im = ax.imshow([[v]], cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
                    ax.text(0, 0, f"{v:.2f}", ha="center", va="center", fontsize=26,
                            color="white" if abs(v) > 0.6 else "black")
                    ax.set_xticks([])
                    ax.set_yticks([])
                    continue
                if j == i:  # diagonal: per-axis marginal of the inner-body sample
                    n_bins = 25 if not is_actual else max(5, min(25, len(samples_phys) // 3))
                    ax.hist(samples_phys[:, i], bins=n_bins, color="#6b1f5c", alpha=0.8)
                    ax.set_yticks([])
                    ax.tick_params(labelsize=13)
                else:  # lower triangle: hexbin density (or, for the actual-points
                    # fallback, a plain scatter -- a hexbin of a few dozen real
                    # points is misleadingly sparse, see _hull_panel_data) + exact
                    # hull outline
                    if is_actual:
                        ax.scatter(samples_phys[:, j], samples_phys[:, i], s=18, color="#6b1f5c",
                                   alpha=0.85, edgecolor="white", linewidth=0.3)
                    else:
                        ax.hexbin(samples_phys[:, j], samples_phys[:, i], gridsize=22, cmap="magma_r",
                                  mincnt=1, linewidths=0.1)
                    proj = poly.X[:, [j, i]]
                    try:
                        hull = ConvexHull(proj)
                        loop = np.append(hull.vertices, hull.vertices[0])
                        ax.plot(proj[loop, 0] * poly.scale[j] + poly.offset[j],
                                proj[loop, 1] * poly.scale[i] + poly.offset[i],
                                color="#2ca02c", linewidth=1.2,
                                label="exact 2D projection of this mode's inner hull" if not first_legend_done else None)
                    except Exception:
                        pass  # degenerate projection (e.g. collinear points); skip the outline
                    # Skip overlaying this panel's OWN mode when it's already the
                    # primary (actual-points) scatter above -- would just draw the
                    # same points twice.
                    for m in overlay_modes:
                        if is_actual and m == mode:
                            continue
                        phys = np.vstack([p for _, p, _ in points[m]])
                        ax.scatter(phys[:, j], phys[:, i], s=14, color=MODE_COLOR[m], alpha=0.8,
                                   edgecolor="white", linewidth=0.3,
                                   label=MODE_LABEL[m] if not first_legend_done else None)
                    ax.scatter(poly.z_star_phys[j], poly.z_star_phys[i], marker="D", s=55, color="black",
                               zorder=5, label="baseline (z*)" if not first_legend_done else None)
                    first_legend_done = True
                if i == n_z - 1:
                    ax.set_xlabel(f"{poly.names[j]}\n[{UNIT_LABEL.get(poly.units[j], poly.units[j] or 'n/a')}]", fontsize=17)
                else:
                    ax.set_xticklabels([])
                if j == 0:
                    ax.set_ylabel(f"{poly.names[i]}\n[{UNIT_LABEL.get(poly.units[i], poly.units[i] or 'n/a')}]", fontsize=17)
                else:
                    ax.set_yticklabels([])
                ax.tick_params(labelsize=13)
        if corr_im is not None:
            # Dedicated axis in the right margin reserved above -- not
            # borrowed from the grid -- so every grid cell stays square.
            # Vertically matched to the grid's own top/bottom (axes[0,0]/
            # axes[-1,-1] corners), not a fixed guess -- otherwise it reads
            # as "kind of low" whenever the grid's actual vertical extent
            # (set by n_z and the xlabel/tick margins below it) doesn't
            # match whatever fraction was hand-picked.
            grid_top = axes[0, 0].get_position().y1
            grid_bottom = axes[-1, -1].get_position().y0
            cax = subfig.add_axes((1 - colorbar_margin_in / panel_width_in + 0.015, grid_bottom,
                                    0.02, grid_top - grid_bottom))
            cbar = subfig.colorbar(corr_im, cax=cax)
            cbar.set_label("Pearson r", fontsize=15)
            cbar.ax.tick_params(labelsize=12)
        if show_legend:
            handles, labels = axes[1, 0].get_legend_handles_labels()
            if handles:
                subfig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.945),
                              ncol=len(handles), fontsize=15, frameon=False)
        # One combined title row per panel (mode + point count folded into
        # the same line) instead of a shared figure-level title with each
        # panel's own stats as a separate row underneath -- that stacked
        # layout read as a title-plus-subtitle pair; this is a single line.
        subtitle = f"n={len(samples_phys)} actual points" if is_actual else f"n={len(samples_phys)} ({rate:.1%} accepted)"
        subfig.suptitle(
            f"MGA Near-Optimal Interior: {MODE_LABEL[mode]} ({subtitle})",
            fontsize=20, fontweight="bold", y=0.975,
        )
    savefig(fig, "fig2_polytope_samples")


# ── fig3: model-query and time comparison, matching near_optimal_tools' ────
# docs/examples/method_comparison.ipynb (2 metrics x 2 x-axes). max_separation
# is the oracle-style max-min L-inf distance -- needs a MILP per evaluation
# (query_time_scores), so it's only evaluated at sparse checkpoints, as the
# reference notebook itself does via its "eval_every" config. ci_lower
# (fraction_well_explored's CI lower bound) does NOT need solving here at
# all any more: every supf/batch-mode run already evaluates this exact
# metric against its own live approximation once per iteration during the
# run itself (ci_convergence_metric/batch_oracle's own convergence check)
# and logs the result straight into its diagnostics.csv -- so, like oracle's
# max_min_distance (see load_oracle_native_gap), it is read directly off
# disk at full per-iteration density rather than resampled (see
# load_native_ci_history; this used to be resampled here too, 500 fresh LP
# solves per checkpoint per mode, until this project noticed the run itself
# already recorded it). Both metrics are evaluated against each mode's own
# live, evolving outer approximation (outer_at(k), see load_native_outer_at)
# -- see the module docstring's "Convergence metric" section for why an
# earlier, shared frozen-box version was dropped. "seconds" started out as
# just the cumulative ZEN-garden solving_time from each solve's
# benchmarking.json (deliberately not wall-clock around the whole loop like
# the reference notebook's TimedCallback), but that alone turned out to be
# wrong in two separate ways this project verified directly against Euler's
# own SLURM job accounting -- see _cum_seconds_wallclock (BATCH_MODES'
# concurrent solves need a max, not a sum, per outer iteration) and
# _calibrate_cum_seconds (benchmarking.json never captures model-
# construction/I/O/direction-search overhead, undercounting EVERY mode's
# real elapsed time, batch or not, by 2.3x-3.7x) immediately below.

def _cum_seconds_wallclock(points: list[tuple[str, np.ndarray, float]],
                           batch_size: int | None) -> np.ndarray:
    """Cumulative elapsed wall-clock time after each of `points` (same order
    as the mode's own X/A/b) -- the array query_time_scores/
    load_native_ci_history index into for fig3b's x-axis.

    For a sequential mode (batch_size=None -- SUPF_MODES, oracle), every
    point really was solved one after another, so summing each point's own
    solving_time straightforwardly IS the real elapsed time.

    For a BATCH_MODES run this is NOT true for the "iterate" points: each
    outer iteration solves batch_size directions concurrently via a worker
    pool (ForkedBatchSupportFunction in zen_garden_plugins/mga/
    parallel_solve.py -- one ProcessPoolExecutor worker per direction, all
    batch_size futures submitted together and gathered together every
    iteration), and the whole group only lands in the polytope once every
    worker in it finishes (_apply_batch_updates applies all batch_size
    points atomically, after every future.result() returns) -- so summing
    the group's individual solving_times would overcount real elapsed time
    by roughly batch_size. The group's real wall-clock contribution is
    instead approximated as its SLOWEST member (the group can't finish
    before its slowest worker does), and every point within a group shares
    that same cumulative timestamp -- which also matches the atomic-commit
    semantics: none of the batch_size points existed in the approximation
    before the whole group did. The initial VMM/z* prefix is still summed
    point-by-point in both kinds of run: solve_axis_bounds (bounds + extreme
    designs) always runs single-process, before the worker pool is even
    constructed."""
    secs = np.nan_to_num([t for _, _, t in points], nan=0.0)
    if not batch_size:
        return np.cumsum(secs)

    labels = [lab for lab, _, _ in points]
    n_initial = sum(1 for lab in labels if lab != "iterate")
    cum = np.empty(len(secs))
    cum[:n_initial] = np.cumsum(secs[:n_initial])
    base = cum[n_initial - 1] if n_initial > 0 else 0.0
    iter_secs = secs[n_initial:]
    for start in range(0, len(iter_secs), batch_size):
        group = iter_secs[start:start + batch_size]
        base = base + (group.max() if len(group) else 0.0)
        cum[n_initial + start: n_initial + start + len(group)] = base
    return cum


# ── Calibrating cum_seconds against Euler's own SLURM job accounting ────
#
# benchmarking.json (what _cum_seconds_wallclock sums/maxes) only logs the
# solver's own LP/MILP time -- it does NOT capture model construction, this
# solve's own output I/O, or (for bbo/sampling) the direction-search
# overhead between solves. Comparing _cum_seconds_wallclock's own totals
# against each run's REAL elapsed time (Euler's `sacct`, ground truth,
# verified directly -- see below) confirmed this gap is large AND present
# in every mode, not just BATCH_MODES: sampling_relative/bbo_relative
# undercounted their own real elapsed time by 2.8x/3.7x respectively;
# batch_bbo_relative/batch_sampling_relative (even with the parallelism-
# aware fix above) still undercounted theirs by 2.4x/2.3x. There is no way
# to close this gap from data already on disk -- benchmarking.json simply
# never recorded the missing time -- so each mode's own real total is
# looked up here instead, once per run, and the whole cum_seconds curve is
# rescaled to match it exactly at its endpoint (assumes the missing
# overhead tracks solving_time roughly proportionally through the run --
# unverified at checkpoint granularity, only at the final total, but far
# closer to real elapsed time than leaving the raw undercount in place).
#
# HOW TO ADD A NEW MODE'S OWN VERIFIED TOTAL (do this for every future MGA
# mode/re-run this script is extended to plot): on Euler, run
#     sacct -u $USER --name=zen_run_mga --format=JobID,State,Elapsed,Start,End -S <run start date> -P
# find that mode's task_id (see submit_euler_mga.sh's own header comment for
# the task_id -> mode mapping) among the `_<task_id>` suffixes, take its
# final COMPLETED row's Elapsed (HH:MM:SS or D-HH:MM:SS), convert to
# seconds, and add an entry below with the job ID/dates as a citation. A
# mode missing from this dict is left uncalibrated (a printed warning
# flags it) rather than silently wrong -- but it WILL keep understating its
# own real elapsed time on fig3b until an entry is added.
# Empty as of the CAPEX-axes switchover (2026-08-20, see SUPF_MODES): the
# old cost-axes runs' verified entries (sampling_relative/bbo_relative/
# batch_bbo_relative/batch_sampling_relative) were removed from disk along
# with the runs themselves, so no verified total exists yet for bbo_units/
# sampling_units -- fig3b's "seconds" axis will print the uncalibrated
# warning below until an entry is added for each via the sacct recipe above.
REAL_ELAPSED_SECONDS: dict[str, int] = {}


def _calibrate_cum_seconds(mode: str, cum_seconds: np.ndarray) -> np.ndarray:
    """Rescales cum_seconds (see _cum_seconds_wallclock) so its endpoint
    matches `mode`'s own REAL total elapsed time from REAL_ELAPSED_SECONDS
    -- see the section comment above for why this is necessary and how to
    extend it. Returns cum_seconds unchanged (with a warning) if `mode` has
    no verified entry yet, or if its own raw total is <= 0 (nothing to
    scale against)."""
    if mode not in REAL_ELAPSED_SECONDS or len(cum_seconds) == 0 or cum_seconds[-1] <= 0:
        print(f"  {mode}: WARNING -- no verified real elapsed time in REAL_ELAPSED_SECONDS; "
              f"fig3b's 'seconds' axis for this mode is uncalibrated and will understate its "
              f"real wall-clock time (see _calibrate_cum_seconds's docstring for how to add one).")
        return cum_seconds
    return cum_seconds * (REAL_ELAPSED_SECONDS[mode] / cum_seconds[-1])


def _gurobi_maxsep_solver(time_limit: float = 15.0):
    import pyomo.environ as pyo
    solver = pyo.SolverFactory("gurobi", solver_io="python", manage_env=True)
    solver.set_options(f"MIPGap=0.05 TimeLimit={time_limit} Threads=4 OutputFlag=0")
    return solver


def query_time_scores(poly: Polytope, X_norm: np.ndarray, cum_seconds: np.ndarray,
                       eval_every: int, outer_at) -> pd.DataFrame:
    """[n_queries, seconds, max_separation] at sparse checkpoints -- the one
    fig3 metric that genuinely needs solving here (no run logs an exact
    max-min MILP distance for itself except oracle, see
    load_oracle_native_gap; ci_lower does not belong here any more, see
    load_native_ci_history). outer_at(k) -> (A_k, b_k), the outer
    approximation to score checkpoint k against -- pass
    load_native_outer_at's result to score against a run's own evolving,
    cut-refined outer approximation, as the reference notebook's own
    score_run does. cum_seconds -- see _cum_seconds_wallclock -- is each
    point's own cumulative elapsed wall-clock time, precomputed by the
    caller (not derived here) so both this function and
    load_native_ci_history share the exact same batch-aware accounting."""
    n = len(X_norm)
    checkpoints = sorted({0, n - 1} | set(range(0, n, eval_every)))
    rows = []
    solver = _gurobi_maxsep_solver()
    for k in checkpoints:
        X_k = X_norm[: k + 1]
        A_k, b_k = outer_at(k)
        approx = approximation(A=A_k, b=b_k, X=X_k, name_list=poly.names, print_lv=0)
        try:
            sep = max_separation(approx, pyomo_solver=solver, print_lv=0)
            distance = sep.distance
        except Exception as exc:
            print(f"    max_separation failed at k={k + 1}: {exc!r}")
            distance = np.nan
        rows.append({"n_queries": k + 1, "seconds": cum_seconds[k], "max_separation": distance})
    return pd.DataFrame(rows)


def fig3_cache_path(mode: str) -> Path:
    """One cache file per supf-mode run, mirroring sampling_cache_path
    (rejection_sample_inner's own cache): query_time_scores is a
    deterministic function of that mode's own polytope + eval_every, and its
    MILP-heavy checkpoints are slow enough (each max_separation call is a
    Gurobi solve) that a full run can take hours -- long enough to hit
    real-world interruptions (this project has seen background runs killed
    mid-way twice in a row, likely the host machine sleeping, not a script
    bug). Caching per mode means a re-run after an interruption only redoes
    whichever mode was still in flight, not every mode from zero."""
    return MGA_ROOT / "mga_inner_sampling" / f"fig3_native_scores_{mode}.npz"


def cached_query_time_scores(mode: str, poly: Polytope, X_norm: np.ndarray, cum_seconds: np.ndarray,
                             eval_every: int, outer_at) -> pd.DataFrame:
    """query_time_scores, cached to fig3_cache_path(mode); regenerates
    automatically if the polytope or eval_every have changed since the cache
    was written (same staleness check as cached_rejection_sample_inner).
    "seconds" is deliberately NOT part of what's cached/staleness-checked:
    it's cheap to derive (index cum_seconds, itself just cumulative sums and
    a scalar rescale -- see _cum_seconds_wallclock/_calibrate_cum_seconds),
    unlike max_separation's MILP solves, which are the only reason this
    cache exists at all -- so it's always recomputed fresh from whatever
    cum_seconds the caller passes in, cache hit or not. This sidesteps a
    staleness class of bug this project hit directly: cum_seconds'
    accounting logic changed twice in one session (the batch-aware
    parallelism fix, then real-elapsed-time calibration), and a cached
    "seconds" column would have silently kept serving pre-fix values on
    every subsequent cache hit, since fig3_cache_path's fingerprint is
    purely a function of poly.X/A/b, not of how cum_seconds itself is
    computed. Older cache files may still carry now-unused seconds/
    ci_lower/ci_upper columns (from before this and an earlier refactor)
    -- harmless, just ignored on read."""
    cache = fig3_cache_path(mode)
    fingerprint = _poly_fingerprint(poly)
    if cache.exists():
        cached = np.load(cache)
        if str(cached["fingerprint"]) == fingerprint and int(cached["eval_every"]) == eval_every:
            print(f"  {mode}: using cached fig3 scores from {cache.relative_to(REPO_ROOT)} "
                  f"({len(cached['n_queries'])} checkpoints)")
            n_queries = cached["n_queries"]
            return pd.DataFrame({
                "n_queries": n_queries, "seconds": cum_seconds[n_queries - 1],
                "max_separation": cached["max_separation"],
            })
        print(f"  {mode}: cached fig3 scores are stale (polytope/eval_every changed); regenerating")

    df = query_time_scores(poly, X_norm, cum_seconds, eval_every, outer_at=outer_at)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        cache, fingerprint=fingerprint, eval_every=eval_every,
        n_queries=df["n_queries"].to_numpy(),
        max_separation=df["max_separation"].to_numpy(),
    )
    print(f"  {mode}: cached fig3 scores to {cache.relative_to(REPO_ROOT)} ({len(df)} checkpoints)")
    return df


def load_native_ci_history(run_dir: Path, mode: str, folder_mode: str,
                           points: list[tuple[str, np.ndarray, float]],
                           batch_size: int | None = None) -> pd.DataFrame:
    """[n_queries, seconds, ci_lower, ci_upper], read directly off run_dir's
    own diagnostics.csv at full per-iteration density -- no LP solving here
    at all. "seconds" is batch-aware wall-clock via _cum_seconds_wallclock
    (batch_size's parallel workers, not a plain per-point sum -- see that
    function), then calibrated against `mode`'s own real elapsed time via
    _calibrate_cum_seconds -- see that function's docstring for why. Every
    supf-mode run already evaluates ci_convergence_metric
    (pyoNearOpt.metrics.fraction_well_explored) against its own live
    approximation once per iteration as its convergence check, and every
    batch-mode run does the same via batch_ORACLE's own per-iteration
    sample_statistics -- both log the resulting ci_lower/ci_upper straight
    into diagnostics.csv, so reading that column back is exact, not an
    approximation of a re-sampled version (same treatment as oracle's own
    max_min_distance, see load_oracle_native_gap).

    Same "checked before this iteration's own point(s) are added" convention
    as oracle's max_min_distance: diagnostics row `iteration=i` (0-indexed)
    reflects the approximation as it stood after n_initial_points + i*step
    points -- verified directly against source: supf_explore.explore calls
    self.metric.evaluate(...) before that iteration's add_point/add_cut
    (step=1, one point per iteration); batch_ORACLE.explore computes
    stats/_update_iteration_histories before that iteration's
    _apply_batch_updates (step=batch_size, batch_size points per iteration
    -- pass the run's own batch_size for a BATCH_MODES run, None/1 for a
    plain supf-mode run)."""
    summary = run_dir / f"{MODEL}_{folder_mode}_summary"
    diagnostics = pd.read_csv(summary / "diagnostics.csv")
    step = batch_size or 1
    n_initial_points = sum(1 for lab, _, _ in points if lab != "iterate")
    cum_seconds = _calibrate_cum_seconds(mode, _cum_seconds_wallclock(points, batch_size))

    rows = []
    for _, row in diagnostics.iterrows():
        n_queries = n_initial_points + int(row["iteration"]) * step
        if not (1 <= n_queries <= len(cum_seconds)):
            continue
        rows.append({
            "n_queries": n_queries, "seconds": cum_seconds[n_queries - 1],
            "ci_lower": float(row["ci_lower"]), "ci_upper": float(row["ci_upper"]),
        })
    return pd.DataFrame(rows)


# ── Native (own evolving) outer approximation, supf modes only ──────────
#
# The reference notebook's own score_run scores each method against ITS OWN
# stored approximation state at each checkpoint (oracle_states/direction_
# states keep a full A/b/X snapshot per iteration) -- not a shared frozen
# box. query_time_scores above deliberately does NOT do that (see its
# docstring and the module docstring's "Convergence metric" section): oracle's
# own cut history is lost if its oracle_summary/ was never written, and
# weights never builds an outer approximation at all, so a fair *shared*
# comparison across every mode needs everyone evaluated against the same
# fixed initial box.
#
# But for sampling and bbo specifically, the cut history is NOT lost:
# supf_explore.explore calls poly_approx.add_point(new_point) and
# poly_approx.add_cut(direction, support_value) exactly once per iteration
# (near_optimal_tools/src/pyoNearOpt/exploration_methods/supf_explore.py),
# and each run's own diagnostics.csv logs precisely those two raw arguments
# every iteration. Replaying them in order therefore reconstructs each
# iteration's own live A_k/b_k exactly -- verified directly (on the old
# 3-mode script's single "probabilistic" run this was based on):
# reconstructing a run's full cut history this way and comparing against its
# own saved final A/b gives an identical feasible region (same shape, and
# every one of 20,000 random test points agrees on which polytope contains
# it). So this project CAN add a faithful, reference-notebook-equivalent "own
# approximation" row for BOTH sampling and bbo now (same shared
# supf_explore/_run_supf_mode harness, see the module docstring); it still
# cannot for oracle (no surviving cut data at all) or weights (no such object
# exists for that mode).
def _parse_diagnostics_vector(s: str) -> np.ndarray:
    """Parses one diagnostics.csv cut_direction cell -- numpy's default
    array repr (e.g. '[ 0.36 -0.62 ... ]', occasionally wrapped over several
    lines for wide vectors), not JSON/literal-eval-able."""
    return np.array([float(x) for x in s.strip().lstrip("[").rstrip("]").split()])


def _parse_diagnostics_matrix(s: str) -> np.ndarray:
    """Parses one batch-mode diagnostics.csv batch_directions cell -- numpy's
    default 2D array repr, one row per batch worker (each row's own values
    may still wrap across lines like _parse_diagnostics_vector's 1D case,
    but rows never nest further, so splitting on single-bracket groups is
    unambiguous)."""
    return np.array([[float(x) for x in row.split()] for row in re.findall(r"\[([^\[\]]+)\]", s)])


def load_native_outer_at(run_dir: Path, run_poly: Polytope, mode: str, folder_mode: str | None = None):
    """outer_at(k) callable (see query_time_scores) that reconstructs
    run_dir's own evolving outer approximation at checkpoint k from its
    diagnostics.csv cut history, falling back to this run's own un-cut
    initial VMM box for any k before its first iterate. Works for any
    supf-mode run (sampling or bbo, any normalisation -- all save the same
    diagnostics.csv schema via supf_driver.py's shared _run_supf_mode).
    folder_mode defaults to mode; pass BASE_MODE[mode] for a
    bbo_relative/bbo_minmax/sampling_relative/sampling_minmax variant
    (see try_load_run_polytope)."""
    folder_mode = folder_mode or mode
    summary = run_dir / f"{MODEL}_{folder_mode}_summary"
    diagnostics = pd.read_csv(summary / "diagnostics.csv")
    cuts_m = np.vstack([_parse_diagnostics_vector(s) for s in diagnostics["cut_direction"]])
    cuts_b = diagnostics["cut_support_value"].to_numpy(dtype=float)

    A0, b0 = run_poly.A[: run_poly.n_initial_rows], run_poly.b[: run_poly.n_initial_rows]
    n_initial_points = sum(1 for origin in run_poly.point_origin if origin != "iterate")

    def outer_at(k: int) -> tuple[np.ndarray, np.ndarray]:
        n_cuts = max(0, min(len(cuts_b), (k + 1) - n_initial_points))
        if n_cuts == 0:
            return A0, b0
        return np.vstack([A0, cuts_m[:n_cuts]]), np.concatenate([b0, cuts_b[:n_cuts]])

    return outer_at


def load_native_outer_at_batch(run_dir: Path, run_poly: Polytope):
    """load_native_outer_at's counterpart for a batch-mode run (BATCH_MODES):
    same cut-replay idea (pyoNearOpt's batch harness calls add_cut once per
    worker per outer iteration, so replaying every logged cut in order
    reconstructs the live outer approximation exactly, same as supf modes),
    but batch-mode's diagnostics.csv logs batch_size cuts per row instead of
    one -- "batch_directions" (a batch_size x n_axes matrix per row) and
    "batch_support_values" (batch_size values per row) -- so cuts are
    flattened across rows before replay instead of read one-per-row."""
    summary = run_dir / f"{MODEL}_batch_summary"
    diagnostics = pd.read_csv(summary / "diagnostics.csv")
    cuts_m = np.vstack([_parse_diagnostics_matrix(s) for s in diagnostics["batch_directions"]])
    cuts_b = np.concatenate([_parse_diagnostics_vector(s) for s in diagnostics["batch_support_values"]])

    A0, b0 = run_poly.A[: run_poly.n_initial_rows], run_poly.b[: run_poly.n_initial_rows]
    n_initial_points = sum(1 for origin in run_poly.point_origin if origin != "iterate")

    def outer_at(k: int) -> tuple[np.ndarray, np.ndarray]:
        n_cuts = max(0, min(len(cuts_b), (k + 1) - n_initial_points))
        if n_cuts == 0:
            return A0, b0
        return np.vstack([A0, cuts_m[:n_cuts]]), np.concatenate([b0, cuts_b[:n_cuts]])

    return outer_at


# ── Oracle's OWN native gap (max_min_distance), not a reconstructed approx ─
#
# oracle can't get a full "own evolving approximation" row like sampling/bbo
# (see load_native_outer_at's docstring: no OA_A/OA_b snapshots saved), but
# it does not need one for max_separation specifically: near_optimal_tools'
# ORACLE.explore() calls self.poly_approx.add_cut(mu_cut, b_cut) once per
# iteration (near_optimal_tools/src/pyoNearOpt/exploration_methods/ORACLE.py)
# and, immediately before that, computes and logs max_distance = d_IO -- the
# EXACT max-min L-inf distance between the current inner and outer
# approximations (an exact MILP solve, `calculate_outer_inner_distance`).
# That is not an approximation of max_separation; it IS max_separation,
# computed by the run itself, natively, every iteration -- pyoNearOpt.metrics
# .max_separation (what query_time_scores calls for every OTHER line on this
# panel) solves the exact same d_IO formula. So oracle's own diagnostics.csv
# already contains this row's one usable metric with no reconstruction risk
# at all -- more faithful than sampling/bbo's replayed-cut lines sharing the
# panel with it, if anything.
#
# There is no oracle line on the ci_lower panel here, but NOT because the
# metric is conceptually inapplicable to oracle -- the reference notebook
# proves this directly: near_optimal_tools' own docs/examples/
# method_comparison.ipynb runs its ORACLE with save_intermediate=True
# precisely so it can rebuild an `approximation` object per iteration and
# run BOTH max_separation and fraction_well_explored on it, exactly like
# every direction-based method there. Sampling/bbo/batch here don't need
# that rebuilding trick at all any more, though: their own convergence
# check IS fraction_well_explored (ci_convergence_metric/batch_oracle),
# logged into diagnostics.csv every iteration, so ci_lower is read straight
# off disk (see load_native_ci_history) rather than recomputed from a
# snapshot. oracle's own convergence check is a different, CI-free
# quantity -- calculate_outer_inner_distance's exact max_min_distance, read
# below -- so its diagnostics.csv was never going to have a ci_lower column
# to read in the first place, independent of save_intermediate or any
# other download-specific gap.
def load_oracle_native_gap(run_dir: Path, run_poly: Polytope,
                           points_oracle: list[tuple[str, np.ndarray, float]]) -> pd.DataFrame | None:
    """[n_queries, seconds, max_separation] for oracle's own max_min_distance
    trajectory -- same column shape as query_time_scores' output, so it can
    be overlaid on the same axes via _comparison_figure, but sourced directly
    from diagnostics.csv rather than recomputed. None if diagnostics.csv is
    missing/unreadable (e.g. oracle_summary/ never written -- see the module
    docstring's data-loss note)."""
    summary = run_dir / f"{MODEL}_oracle_summary"
    try:
        diagnostics = pd.read_csv(summary / "diagnostics.csv")
    except Exception as exc:
        print(f"  oracle: no native gap available ({exc!r})")
        return None

    iterations_done = int(run_poly.run.get("iterations_done", len(diagnostics)))
    n_initial_points = sum(1 for origin in run_poly.point_origin if origin != "iterate")
    cum_seconds = np.cumsum(np.nan_to_num([t for _, _, t in points_oracle], nan=0.0))

    rows = []
    for _, row in diagnostics.iterrows():
        it = int(row["iteration"])
        if it > iterations_done or pd.isna(row["max_min_distance"]):
            continue
        # calculate_outer_inner_distance() runs BEFORE this iteration's own
        # point is added (see ORACLE.py's explore loop), so max_min_distance
        # at iteration `it` reflects the approximation as it stood after
        # `it - 1` oracle iterates -- same "checked before add_point"
        # convention documented for supf modes elsewhere in this file.
        n_queries = n_initial_points + it - 1
        if not (1 <= n_queries <= len(cum_seconds)):
            continue
        rows.append({
            "n_queries": n_queries, "seconds": cum_seconds[n_queries - 1],
            "max_separation": float(row["max_min_distance"]),
        })
    return pd.DataFrame(rows) if rows else None


def _compute_fig3_scores(points: dict[str, list[tuple[str, np.ndarray, float]]],
                         polys: dict[str, Polytope]):
    """Two native (own evolving approximation) scores for every plotted
    CAPEX-axes supf-mode run (bbo_units, sampling_units -- see
    ALL_SUPF_MODES; minmax/batch CAPEX variants will join this set once
    downloaded, no code change needed here): max_separation, actually
    solved here (MILP, sparse checkpoints -- see query_time_scores), and
    ci_lower, read directly off diagnostics.csv at full density with no
    solving at all (see load_native_ci_history) -- plus oracle's own
    certified max_separation-only gap (see load_oracle_native_gap). weights
    has no representation here at all -- see the module docstring's
    "Convergence metric" section. Shared by both fig3a (vs queries) and
    fig3b (vs time) so the MILP solves only run once."""
    # 100 rather than the original 10: with 13 axes (vs. the original 6, then
    # 9) each checkpoint's max_separation MILP is markedly slower, and repeated
    # background-run interruptions (see fig3_cache_path's docstring) meant
    # even eval_every=25 didn't reliably finish -- this trades a much
    # coarser convergence curve for a run that actually completes. Only
    # applies to max_separation -- ci_lower is read at full per-iteration
    # density regardless (see load_native_ci_history), it doesn't need
    # sparsifying since nothing is solved for it. BATCH_MODES runs get an
    # even coarser 300 rather than 100: batch_size points land per outer
    # iteration (batch16: 16/iteration, 2841 points total vs. the few
    # hundred a sequential supf mode accumulates over the same wall-clock
    # budget), so 100 would mean ~29 checkpoints x up to 30s/MILP. This
    # project hit that directly, twice: a background run of this script was
    # killed mid-fig3 both times (once at checkpoint ~19/29 with
    # eval_every=300 and TimeLimit=30, once earlier than that with
    # eval_every=100) -- this environment appears to cap a single
    # long-running process well under the ~15min a full batch16 fig3 pass
    # would otherwise take, independent of whether it's run in the
    # foreground or backgrounded. 700 cuts batch16's checkpoint count to ~5;
    # combined with _gurobi_maxsep_solver's TimeLimit (also cut, 30s -> 15s),
    # a full pass is well under 2 minutes.
    eval_every = {m: (700 if m in BATCH_MODES else 100) for m in ALL_SUPF_MODES}

    # Each supf mode scored against its OWN evolving, cut-refined outer
    # approximation -- i.e. the reference notebook's own score_run
    # methodology exactly (see load_native_outer_at's docstring). Only
    # possible for sampling/bbo/batch variants: their diagnostics.csv logs
    # the incremental cut_direction/cut_support_value (or batch_directions/
    # batch_support_values for BATCH_MODES, see load_native_outer_at_batch)
    # each iteration adds, letting outer_at(k) be replayed exactly; oracle's
    # diagnostics.csv logs its own certified max_min_distance instead (no
    # recomputation needed for that quantity, but no OA_A/OA_b snapshots
    # either, so its OWN evolving box can't be reconstructed here), and
    # weights never builds an outer approximation at all. Each mode is scored
    # against ITS OWN polytope (polys[mode]), not the shared frame -- their
    # own X/A/b differ even though the axes/units they're expressed in are
    # the same.
    native_sep = {}
    native_ci = {}
    tolerance_prob = {}
    for mode in ALL_SUPF_MODES:
        run_dir = RUN_DIR[mode]
        if mode not in points or mode not in polys:
            continue
        run_poly = polys[mode]
        is_batch = mode in BATCH_MODES
        tolerance_prob[mode] = float(run_poly.convergence_threshold)
        outer_at = (load_native_outer_at_batch(run_dir, run_poly) if is_batch
                    else load_native_outer_at(run_dir, run_poly, mode, BASE_MODE[mode]))
        batch_size = int(run_poly.run.get("batch_size", 4)) if is_batch else None
        phys = [p for _, p, _ in points[mode]]
        X_norm = run_poly.to_norm(np.vstack(phys))
        cum_seconds = _calibrate_cum_seconds(mode, _cum_seconds_wallclock(points[mode], batch_size))
        print(f"  fig3: scoring {mode} max_separation ({len(X_norm)} points, "
              f"every {eval_every.get(mode, 5)}th checkpoint, own evolving approximation)...")
        native_sep[mode] = cached_query_time_scores(mode, run_poly, X_norm, cum_seconds, eval_every.get(mode, 5),
                                                     outer_at=outer_at)
        native_ci[mode] = load_native_ci_history(run_dir, mode, BASE_MODE[mode], points[mode], batch_size=batch_size)

    # oracle's own certified gap -- max_separation only, no ci_lower; see
    # load_oracle_native_gap's docstring for why this is a legitimate,
    # non-recomputed addition rather than a stretch to match sampling/bbo.
    # oracle_tol is its own real target for THIS metric (convergence_threshold
    # is a max_min_distance/L-inf bound for oracle -- see polytope_io.py's
    # schema docstring), exactly like the reference notebook's ORACLE gets a
    # `cfg["separation_tol"]` axhline on its max_separation panel (its
    # comparison_figure draws that line for every method from one shared
    # config value; here only oracle actually targets this metric natively,
    # so only oracle gets the line -- sampling/bbo's tolerance_prob is a
    # ci_lower-type target, not a max_separation-type one).
    oracle_native_gap = None
    oracle_tol = None
    if "oracle" in points and "oracle" in polys:
        oracle_native_gap = load_oracle_native_gap(ORACLE_DIR, polys["oracle"], points["oracle"])
        if oracle_native_gap is not None:
            oracle_tol = float(polys["oracle"].convergence_threshold)

    return native_sep, native_ci, tolerance_prob, oracle_native_gap, oracle_tol


def _comparison_figure(x_column: str, x_label: str, name: str, title: str,
                       native_sep: dict, native_ci: dict, tolerance_prob: dict, log_x: bool,
                       oracle_native_gap: pd.DataFrame | None = None, oracle_tol: float | None = None) -> None:
    """One query-time comparison figure, columns matching the reference
    notebook's own comparison_figure (near_optimal_tools/docs/examples/
    method_comparison.ipynb): max_separation | fraction_well_explored's
    ci_lower. Every mode shown is scored against ITS OWN live approximation
    -- sampling/bbo/batch's max_separation solved here at sparse checkpoints
    (native_sep, see query_time_scores) but ci_lower read directly, at full
    density, off each run's own diagnostics.csv (native_ci, see
    load_native_ci_history -- no LP solving involved at all), oracle's own
    certified max_separation likewise read directly off its diagnostics (see
    load_oracle_native_gap) with no ci_lower equivalent (see that function's
    docstring for why). weights never appears here: it never builds an
    outer approximation at all -- see fig0 for weights' own behaviour. An
    earlier version also scored every mode against one shared frozen initial
    box; dropped, see the module docstring's "Convergence metric" section."""
    fig, (ax_sep, ax_ci) = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)

    for mode, df in native_sep.items():
        color = MODE_COLOR[mode]
        group = df[df[x_column] > 0] if log_x else df  # "the initial state sits at zero"
        ax_sep.plot(group[x_column], group["max_separation"], marker="o", markersize=4,
                   color=color, label=MODE_LABEL[mode])
    for mode, df in native_ci.items():
        color = MODE_COLOR[mode]
        group = df[df[x_column] > 0] if log_x else df
        # markersize=2 (smaller than ax_sep's sparse-checkpoint markers): one
        # marker per logged iteration, not per eval_every-th checkpoint, so
        # this line is far denser.
        ax_ci.plot(group[x_column], group["ci_lower"], marker="o", markersize=2, color=color)
        # Each run's own real convergence target for THIS metric: its own
        # tolerance_prob (see README), colour-matched, exactly like the
        # reference's cfg["tolerance_prob"] axhline. No target line on the
        # max_separation panel: unlike ORACLE's own "tol" in the reference
        # notebook, sampling/bbo never target an exact worst-case
        # max_separation bound at all.
        ax_ci.axhline(tolerance_prob[mode], color=color, ls="--", lw=1)
    if oracle_native_gap is not None:
        # oracle's own EXACT max_min_distance (see load_oracle_native_gap)
        # -- dashed + triangle markers to visually flag "read directly off
        # this run's own diagnostics", not reconstructed/recomputed the way
        # sampling/bbo's lines on this same axes are. oracle_tol is its own
        # real target for this metric (a max_min_distance/L-inf bound,
        # unlike sampling/bbo's CI-based tolerance_prob) -- matching the
        # reference notebook's own ORACLE, which gets this exact axhline on
        # its max_separation panel too (comparison_figure's
        # cfg["separation_tol"] line).
        group = oracle_native_gap[oracle_native_gap[x_column] > 0] if log_x else oracle_native_gap
        ax_sep.plot(group[x_column], group["max_separation"], marker="^", markersize=5,
                   color=MODE_COLOR["oracle"], linestyle="--", label=MODE_LABEL["oracle"])
        if oracle_tol is not None:
            ax_sep.axhline(oracle_tol, color=MODE_COLOR["oracle"], ls=":", lw=1)
    ax_sep.set_yscale("log")
    ax_sep.set_title("max separation")
    ax_sep.set_ylabel("max $L_\\infty$ separation")
    ax_ci.set_title("directions with gap $\\leq$ 0.1, 95% CI lower bound")
    ax_ci.set_ylabel("fraction of well-explored directions")
    ax_ci.set_ylim(-0.03, 1.03)

    for ax in (ax_sep, ax_ci):
        ax.set_xlabel(x_label)
        if log_x:
            ax.set_xscale("log")
        ax.grid(alpha=0.3)
    ax_sep.legend(fontsize=8, frameon=False)
    fig.suptitle(title, fontsize=12, fontweight="bold")
    savefig(fig, name)


def fig3_query_time_comparison(points: dict[str, list[tuple[str, np.ndarray, float]]],
                               polys: dict[str, Polytope]) -> None:
    native_sep, native_ci, tolerance_prob, oracle_native_gap, oracle_tol = _compute_fig3_scores(points, polys)
    if not native_sep and oracle_native_gap is None:
        print("  skipping fig3_query_time_comparison: no scored modes")
        return
    _comparison_figure(
        "n_queries", "number of model queries", "fig3a_query_comparison",
        "MGA Method Comparison vs. Model Queries",
        native_sep, native_ci, tolerance_prob, log_x=False,
        oracle_native_gap=oracle_native_gap, oracle_tol=oracle_tol,
    )
    _comparison_figure(
        "seconds", "cumulative ZEN-garden solving time [s]", "fig3b_time_comparison",
        "MGA Method Comparison vs. Cumulative Solving Time",
        native_sep, native_ci, tolerance_prob, log_x=True,
        oracle_native_gap=oracle_native_gap, oracle_tol=oracle_tol,
    )


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    print("Loading run polytopes...")
    polys: dict[str, Polytope] = {}
    for mode in ALL_SUPF_MODES:
        run_poly = try_load_run_polytope(RUN_DIR[mode], mode, BASE_MODE[mode])
        if run_poly is not None:
            polys[mode] = run_poly
            batch_note = f", batch_size={run_poly.run.get('batch_size', '?')}" if mode in BATCH_MODES else ""
            print(f"  {mode}: polytope loaded ({run_poly.X.shape[0]} points on disk, "
                  f"converged={run_poly.converged}, {run_poly.run.get('iterations_done', '?')} iterations, "
                  f"tolerance_prob={run_poly.convergence_threshold:g}{batch_note})")
        else:
            print(f"  {mode}: no usable polytope.npz under {RUN_DIR[mode].relative_to(REPO_ROOT)} "
                  f"(skipping this mode entirely)")

    oracle_poly = try_load_run_polytope(ORACLE_DIR, "oracle")
    if oracle_poly is not None:
        polys["oracle"] = oracle_poly
        print(f"  oracle: polytope loaded ({oracle_poly.X.shape[0]} points on disk, "
              f"converged={oracle_poly.converged}, {oracle_poly.run.get('iterations_done', '?')} iterations, "
              f"tolerance_prob={oracle_poly.convergence_threshold:g})")
    else:
        print(f"  oracle: no usable polytope.npz under {ORACLE_DIR.relative_to(REPO_ROOT)} "
              f"(placeholder -- not yet re-run against the CAPEX axis set)")

    if not any(m in polys for m in ALL_SUPF_MODES):
        raise SystemExit(
            "No SUPF_MODES/BATCH_MODES run has a "
            "usable polytope -- nothing to build the shared coordinate frame or fig2 from."
        )

    # Shared coordinate frame (axis names/units/z*/scale/offset, used by
    # fig1) -- whichever SUPF_MODES/BATCH_MODES run loads first, in
    # ALL_SUPF_MODES order (SUPF_MODES then BATCH_MODES; empty as of the
    # batch16 switchover, so batch16 itself supplies the frame). See module
    # docstring.
    frame_mode = next(m for m in ALL_SUPF_MODES if m in polys)
    poly = polys[frame_mode]
    print(f"Shared frame (from {frame_mode}): axes={poly.names}, epsilon={poly.epsilon:g}, c_star={poly.c_star:,.0f}")
    present = [m for m in ALL_SUPF_MODES if m in polys]
    for a, b in zip(present, present[1:]):
        z_diff = float(np.abs(polys[a].z_star_phys - polys[b].z_star_phys).max())
        if z_diff > 1e-6:
            print(f"  WARNING: {a}'s and {b}'s baselines (z*) differ by up to {z_diff:g} -- "
                  f"expected bit-for-bit identical (same model, same cost-optimal baseline solve)")
        else:
            print(f"  sanity check: {a}'s and {b}'s baselines (z*) agree to {z_diff:g} -- same problem, confirmed")

    points: dict[str, list[tuple[str, np.ndarray, float]]] = {}

    for mode in SUPF_MODES:
        if mode not in polys:
            continue
        print(f"Loading {mode} mode...")
        points[mode] = load_supf_points(polys[mode], RUN_DIR[mode])

    for mode in BATCH_MODES:
        if mode not in polys:
            continue
        print(f"Loading {mode} mode...")
        batch_size = int(polys[mode].run.get("batch_size", 4))
        points[mode] = load_batch_points(polys[mode], RUN_DIR[mode], batch_size)

    if "oracle" in polys:
        # Same treatment as sampling/bbo now that oracle has its own usable
        # polytope.npz: real per-point solving times from each point's own
        # Postprocess folder, not the NaN-timed shortcut load_oracle_points
        # used to take when only the summary (no per-point mapping) was
        # trusted. oracle_driver.py names its own iteration folders
        # oracle_iter_N rather than supf_iter_N (different algorithm, same
        # point_origin convention) -- see load_supf_points's docstring.
        print("Loading oracle mode...")
        points["oracle"] = load_supf_points(polys["oracle"], ORACLE_DIR, iter_prefix="oracle_iter")
    else:
        print("Loading oracle mode (best effort, no polytope available)...")
        o = load_oracle_points(poly)
        if o:
            points["oracle"] = o

    print(f"Modes with usable data: {list(points)}")
    print("Generating figures...")

    fig1_pairwise_points(poly, points)

    # Rejection-sampling each mode's inner approximation for fig2 is disabled
    # for now (2026-09-03, per user request) -- fig2 uses ONLY each mode's own
    # actual visited points (the _hull_panel_data "actual points" fallback,
    # normally reserved for runs with <20 accepted inner samples -- see that
    # function's docstring) rather than a synthetic rejection-sampled cloud.
    # samples stays empty so every mode falls through to that fallback.
    samples: dict[str, tuple[np.ndarray, float]] = {}

    fig2_polytope_samples(polys, points, samples)
    fig3_query_time_comparison(points, polys)

    print(f"Done. Figures in {FIGURES_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
