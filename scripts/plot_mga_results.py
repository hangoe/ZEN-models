"""Compare the four MGA exploration modes (weights, sampling, bbo, oracle)
run against Crystal_Ball_ind_heat_v8_0_no_flexibility_nodiffusion on Euler.

All four modes explore the same near-optimal space: 6 axes (nuclear,
photovoltaics, wind_offshore, wind_onshore capacity additions, biomass
carrier import, total cost), epsilon = 0.1, same baseline solve -- so their
results live in one shared coordinate system and can be overlaid directly.

sampling and bbo both run through pyoNearOpt's generic supf_explore harness
(near_optimal_tools' shared support-function polytope bookkeeping) and only
differ in how the next direction to query is picked: sampling scores many
candidate directions and takes the largest observed inner/outer gap; bbo
searches for that direction with a black-box optimiser (SHADE) instead. Both
therefore save their own independent polytope.npz + diagnostics.csv under
..._MGA_<mode>/..._<mode>_summary/ (data/outputs/euler_outputs_mga/) --
unlike the older single "probabilistic" run this script used to compare
against weights/oracle, there is now no one mode whose polytope is *the*
shared frame by construction. This script picks sampling's own polytope.npz
as the canonical shared frame for axis names/units/z*/scale/offset (used by
fig0 and fig1), falling back to bbo's if sampling's is missing, and prints a
sanity check comparing the two runs' baselines (they
solve the same cost-optimal model, so z*/bounds/A0/b0 should agree to full
floating-point precision -- same check this script used to do for weights
vs. the old probabilistic run). For fig2/fig3 specifically -- the ones this
project actually cares about *comparing* bbo against sampling on -- each
mode gets its own inner-hull sample and its own panel; see those functions'
docstrings.

oracle is now downloaded and wired in like sampling/bbo: 31 points (z*, 10
VMM bound solves, 20 KKT/MILP refinement iterations named
..._oracle_iter_<n>, mapped to real per-point solving times by
load_supf_points exactly like sampling/bbo's own ..._supf_iter_<n> --
oracle_driver.py just uses a different folder-naming convention for the
same point_origin schema, see that function's docstring). Every
oracle-touching step still degrades to "skip, log why" rather than erroring
if its data is ever incomplete (e.g. a partial re-download): missing
polytope -> load_oracle_points falls back to a best-effort reconstruction
from the individual oracle_iter_N / vmm_*_<axis> Postprocess folders, and if
even those are unreadable, oracle is dropped from every figure rather than
plotting fabricated data. One real asymmetry remains, not a bug: oracle's
diagnostics.csv logs its own certified max_min_distance per iteration --
directly comparable to max_separation, no recomputation needed, so fig4
DOES include oracle on that one metric (see load_oracle_native_gap) -- but
not the OA_A/OA_b outer-approximation snapshots sampling/bbo's
diagnostics.csv has (this run's oracle_driver.py call didn't set
save_intermediate=True, unlike near_optimal_tools' own reference notebook,
docs/examples/method_comparison.ipynb, which does and so gets a full
ci_lower curve for its ORACLE too). Without those snapshots
fraction_well_explored/ci_lower has nothing to evaluate for oracle, so
fig4's ci_lower panel stays sampling/bbo-only; see load_oracle_native_gap's
docstring for the full reasoning and _comparison_figure's in-figure note.

Convergence metric (fig4): pyoNearOpt.metrics.fraction_well_explored and
max_separation (the same machinery behind sampling/bbo's own
ci_convergence_metric and oracle's own max-min distance), evaluated on each
mode's growing set of known near-optimal points against ITS OWN live,
evolving outer approximation -- sampling/bbo's fully reconstructed from
their own cut history (see load_native_outer_at), oracle's own certified gap
read directly off its own diagnostics for max_separation only (see
load_oracle_native_gap). An earlier version of this figure also scored every
mode against one shared, FROZEN initial outer box (the un-cut VMM box before
any refinement) as a second row, so all modes had one common ruler despite
each building a different real approximation. That row was dropped: scoring
against a box that never shrinks conflates "coverage of a fixed region" with
actual convergence, and made every mode look like it stalled well before it
actually had (each mode's real, evolving approximation kept shrinking
substantially past the point the frozen-box metric stopped moving). weights
never builds an outer approximation at all, so it has no representation in
fig4 any more -- fig0 remains the figure for weights' own behaviour.

Figures (data/outputs/figures/mga_results/):
  fig0_weights_axis_bars        weights-mode capacity ADDITION per axis, per
                                 iteration, vs baseline (4 tech axes; weights
                                 never touches the biomass/cost axes as
                                 exploration directions).
  fig1_pairwise_points           pairwise projections of every mode's actual
                                 visited points, colour-coded by mode.
  fig2_polytope_samples          One panel per mode with its own polytope
                                 (sampling, bbo, and oracle once downloaded):
                                 hexbin density of a uniform sample of THAT
                                 mode's own INNER approximation
                                 (rejection-sampled from its own outer body --
                                 see rejection_sample_inner's docstring and
                                 Steen2026_Thesis Sec 3.3), diagonal = per-axis
                                 marginals, green outline = exact 2D
                                 projection of that mode's inner hull; every
                                 mode's actual points (weights/sampling/bbo/
                                 oracle) overlaid on every panel for context.
                                 Side-by-side panels are the actual bbo-vs-
                                 sampling comparison this project wanted --
                                 weights never builds a polytope, so it never
                                 gets its own panel.
  fig3_axis_correlations         Same per-mode panel layout as fig2, one
                                 Pearson correlation heatmap of the 6 axes per
                                 mode's own inner-hull sample (Steen2026_Thesis
                                 Figure 7 analog): which axes substitute
                                 (negative) or move together (positive) across
                                 that mode's own near-optimal volume. Pearson r
                                 is invariant to per-axis affine rescaling
                                 (verified: physical-unit and normalised draws
                                 give the same matrix to 1e-14), so this is on
                                 physical units purely for readability --
                                 normalising would not change a single value.
  fig4a/b_query/time_comparison  Two figures, columns are max_separation and
                                 fraction_well_explored's ci_lower; fig4a's
                                 x-axis is number of model queries, fig4b's is
                                 cumulative real ZEN-garden solving time (log).
                                 One row: each mode's own live, evolving
                                 approximation -- sampling AND bbo fully
                                 (reference-equivalent to near_optimal_tools'
                                 docs/examples/method_comparison.ipynb, see
                                 load_native_outer_at), oracle on
                                 max_separation only (see
                                 load_oracle_native_gap), weights absent (it
                                 never builds an approximation -- see fig0
                                 instead). An earlier 2-row version also
                                 scored every mode against one shared frozen
                                 initial box; dropped, see the module
                                 docstring's "Convergence metric" section for
                                 why. This file's only per-mode convergence
                                 trace now (an earlier fig1_convergence and
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
import warnings
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Match MT_report_HG's font -- see generate_si_figures.py for the rationale
# (cmr10 ships inside matplotlib, no system LaTeX/font install needed).
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["cmr10"],
    "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True,
    "axes.unicode_minus": False,
})

from scipy.optimize import linprog

from figure_settings import SCENARIO_PALETTE
from zen_garden import Results
from zen_garden_plugins.mga.polytope_io import Polytope, load_polytope
from pyoNearOpt.metrics import fraction_well_explored, max_separation
from pyoNearOpt.polytope_approximation.approximation_class import approximation
from pyoNearOpt.polytope_approximation.polytope_samples import PolytopeSamples

FIGURES_DIR = REPO_ROOT / "data" / "outputs" / "figures" / "mga_results"
MGA_ROOT = REPO_ROOT / "data" / "outputs" / "euler_outputs_mga"

MODEL = "Crystal_Ball_ind_heat_v8_0_no_flexibility_nodiffusion"
RUN_PREFIX = f"{MODEL}_2050_1a_5a_interval_5ts_MGA"
WEIGHTS_DIR = MGA_ROOT / f"{RUN_PREFIX}_weights"
SAMPLING_DIR = MGA_ROOT / f"{RUN_PREFIX}_sampling"
BBO_DIR = MGA_ROOT / f"{RUN_PREFIX}_bbo"
ORACLE_DIR = MGA_ROOT / f"{RUN_PREFIX}_oracle"
RUN_DIR = {"sampling": SAMPLING_DIR, "bbo": BBO_DIR, "oracle": ORACLE_DIR}

# Colours reused from figure_settings.SCENARIO_PALETTE (the full 7-color ETH
# corporate swatch: blue, petrol, green, bronze, red, purple, grey), per this
# project's convention of never inventing a separate palette for print
# figures -- picked for maximum pairwise contrast (not adjacent palette
# slots) per user request: weights=green, sampling=purple/pink, bbo=blue,
# oracle=bronze/brown.
_ETH_BLUE, _ETH_GREEN, _ETH_BRONZE, _ETH_RED, _ETH_PURPLE = (
    SCENARIO_PALETTE[0], SCENARIO_PALETTE[2], SCENARIO_PALETTE[3], SCENARIO_PALETTE[4], SCENARIO_PALETTE[5],
)
MODE_COLOR = {
    "weights": _ETH_GREEN,
    "sampling": _ETH_PURPLE,
    "bbo": _ETH_BLUE,
    "oracle": _ETH_BRONZE,
}
MODE_LABEL = {
    "weights": "Weights",
    # $\tau$ (mathtext, "cm" fontset) rather than a literal unicode tau --
    # the plain text font (cmr10) has no tau glyph.
    "sampling": r"Sampling ($\tau$=0.95)",
    "bbo": r"BBO ($\tau$=0.95)",
    "oracle": "Oracle",
}
MODES = ("weights", "sampling", "bbo", "oracle")

# config_mga_weights.json's "iterations" list: weight sign, combined with
# run_iteration's fixed sense="min", determines whether each solve minimises
# or maximises the axis (weight > 0 -> minimises). Verified against the
# actual reconstructed capacities (see module docstring).
WEIGHTS_ITERATIONS = [
    ("mga_iter_0", "photovoltaics", "min"),
    ("mga_iter_1", "photovoltaics", "max"),
    ("mga_iter_2", "wind", "min"),  # wind_onshore + wind_offshore weighted together
    ("mga_iter_3", "wind", "max"),
    ("mga_iter_4", "nuclear", "min"),
    ("mga_iter_5", "nuclear", "max"),
]
# The 4 tech-capacity axes weights mode actually drives (see fig0); it never
# targets the biomass carrier-import or cost axes.
WEIGHTS_TECH_AXES = ["photovoltaics", "wind_onshore", "wind_offshore", "nuclear"]

UNIT_LABEL = {"gigawatt": "GW", "gigawatt * hour": "GWh", "megaEuro": "MEUR"}
# fig0's per-iteration bars cycle through the palette minus _ETH_RED, which
# is reserved for the baseline bar -- otherwise one iteration's colour would
# be visually indistinguishable from the baseline.
_ITER_PALETTE = [c for c in SCENARIO_PALETTE if c != _ETH_RED]


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
    axis sums annual flow_import over members; the cost axis sums
    net_present_cost over years."""
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
    raise ValueError(f"unknown axis kind {kind!r}")


def point_from_results(r: Results, poly: Polytope) -> np.ndarray:
    """Physical-units point (n_axes,) in poly's axis order."""
    return np.array([axis_value(r, a) for a in poly.meta["axes"]], dtype=float)


def solving_time(folder: Path) -> float:
    """This solve's real wall time from ZEN-garden's own benchmarking.json,
    or NaN if the file is missing/unreadable (e.g. no real solve behind a
    point, as for the shared frame's z* borrowed for oracle -- see
    load_oracle_points). Used for fig4's time axis."""
    path = folder / "benchmarking.json"
    if not path.exists():
        return float("nan")
    try:
        return float(json.loads(path.read_text())["solving_time"])
    except Exception:
        return float("nan")


def try_load_run_polytope(run_dir: Path, mode: str) -> Polytope | None:
    """mode's own polytope.npz (sampling/bbo/oracle all save under
    ..._<mode>_summary/, see supf_driver.py/oracle_driver.py), or None
    (logged) if the summary folder or its polytope*.npz is missing/unreadable
    -- e.g. oracle before its download lands, or an interrupted run whose
    summary was never written (see the module docstring)."""
    summary = run_dir / f"{MODEL}_{mode}_summary"
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


# ── Weights mode ─────────────────────────────────────────────────────────

def load_weights_points(poly: Polytope) -> list[tuple[str, np.ndarray, float]]:
    """[(label, phys_point, solving_time)], baseline first, in solve order.
    Folders that fail to load are skipped."""
    base_dir = WEIGHTS_DIR / MODEL
    base = safe_results(base_dir)
    if base is None:
        print(f"  weights: baseline unreadable at {base_dir}; skipping weights mode entirely")
        return []
    rows = [("baseline", point_from_results(base, poly), solving_time(base_dir))]
    for subdir, axis, sense in WEIGHTS_ITERATIONS:
        folder = WEIGHTS_DIR / f"{MODEL}_{subdir}"
        r = safe_results(folder)
        if r is None:
            continue
        label = f"{'Max' if sense == 'max' else 'Min'} {axis.replace('_', ' ')}"
        rows.append((label, point_from_results(r, poly), solving_time(folder)))
    print(f"  weights: {len(rows) - 1}/{len(WEIGHTS_ITERATIONS)} iterations readable")
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


# ── fig0: weights-mode capacity addition per axis, per iteration ────────

def fig0_weights_axis_bars(poly: Polytope, weights_points: list[tuple[str, np.ndarray, float]]) -> None:
    if len(weights_points) < 2:
        print("  skipping fig0_weights_axis_bars: no completed iterations")
        return
    axis_idx = {a["name"]: i for i, a in enumerate(poly.meta["axes"])}
    df = pd.DataFrame(
        {label: [phys[axis_idx[axname]] for axname in WEIGHTS_TECH_AXES] for label, phys, _ in weights_points},
        index=WEIGHTS_TECH_AXES,
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    n = len(df.columns)
    width = 0.8 / n
    x = np.arange(len(df))
    for i, label in enumerate(df.columns):
        offsets = x + (i - (n - 1) / 2) * width
        color = _ETH_RED if label == "baseline" else _ITER_PALETTE[(i - 1) % len(_ITER_PALETTE)]
        ax.bar(offsets, df[label].to_numpy(), width, label=label, color=color, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(df.index, rotation=15, ha="right", fontsize=9)
    ax.set_ylabel("capacity addition [GW]")
    ax.set_title(
        "MGA Weights-Mode: Capacity Addition per Axis, per Directional Solve\n"
        "(each iteration minimises or maximises ONE weighted direction; bars show its effect on all 4 axes)",
        fontsize=12, fontweight="bold",
    )
    ax.legend(fontsize=9, frameon=False, ncol=min(n, 4))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig0_weights_axis_bars")


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
# convex combination of real model solves). A first version of fig4 walked O
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
    sampling in fig2/fig3 depends only on that mode's own polytope (fixed
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


# ── fig2/fig3: hexbin density / correlations of each mode's OWN inner hull ──
# Styled after Steen2026_Thesis Figure 6/7: hexbin density lower triangle, the
# exact 2D projection of I as a green outline (a linear projection of a convex
# hull is the hull of the projected vertices, so this is just ConvexHull on
# poly.X's projected columns -- no extra approximation), per-axis marginal
# histograms on the diagonal, baseline marked, every mode's actual points
# overlaid for context. Unlike the old 3-mode script (one shared hull, from
# "probabilistic"), sampling and bbo each get their OWN hull now -- neither is
# more "correct" than the other, they're independent runs of different
# direction-selection strategies over the same space -- so this is genuinely
# a bbo-vs-sampling comparison, not one hull with the other mode's points
# dropped on top. oracle gets a third panel automatically once its own
# oracle_summary/polytope.npz exists (see try_load_run_polytope); weights
# never builds a polytope and so never gets a panel here (see fig0 instead).
_HULL_MODE_ORDER = ("sampling", "bbo", "oracle")


def _hull_modes_to_plot(polys: dict[str, Polytope], samples: dict[str, tuple[np.ndarray, float]]) -> list[str]:
    return [m for m in _HULL_MODE_ORDER if m in polys and m in samples and len(samples[m][0]) >= 20]


def fig2_polytope_samples(polys: dict[str, Polytope], points: dict[str, list[tuple[str, np.ndarray, float]]],
                           samples: dict[str, tuple[np.ndarray, float]]) -> None:
    modes_to_plot = _hull_modes_to_plot(polys, samples)
    if not modes_to_plot:
        print("  skipping fig2_polytope_samples: no mode has >=20 accepted inner samples")
        return

    from scipy.spatial import ConvexHull

    n_z = polys[modes_to_plot[0]].n_axes
    if n_z < 2:
        print("  skipping fig2_polytope_samples: fewer than 2 design axes")
        return
    overlay_modes = [m for m in MODES if m in points]

    fig = plt.figure(figsize=(3.3 * n_z * len(modes_to_plot) + 1.0, 3.3 * n_z + 0.9))
    subfigs = fig.subfigures(1, len(modes_to_plot))
    subfigs = np.atleast_1d(subfigs)
    n_panels = len(modes_to_plot)
    for panel_idx, (subfig, mode) in enumerate(zip(subfigs, modes_to_plot)):
        poly = polys[mode]
        samples_norm, rate = samples[mode]
        samples_phys = poly.to_phys(samples_norm)
        # Full n_z x n_z triangular grid (unlike _pairwise_grid's (n-1) x
        # (n-1) off-diagonal-only layout used by fig1): row/col i==j is axis
        # i's own marginal, so every axis gets one, matching Steen2026_Thesis
        # Figure 6.
        axes = subfig.subplots(n_z, n_z, squeeze=False)
        first_legend_done = False
        # Only the rightmost (last) panel keeps its legend -- with one panel
        # per mode, every panel's legend is otherwise identical (same overlay
        # modes/baseline/hull-outline label), so repeating it on every panel
        # only added clutter and, combined with each panel's own suptitle
        # sitting right above it, is what caused the title/legend overlap.
        show_legend = panel_idx == n_panels - 1
        for i in range(n_z):
            for j in range(n_z):
                ax = axes[i, j]
                if j > i:
                    ax.axis("off")
                    continue
                if j == i:  # diagonal: per-axis marginal of the inner-body sample
                    ax.hist(samples_phys[:, i], bins=25, color="#6b1f5c", alpha=0.8)
                    ax.set_yticks([])
                    ax.tick_params(labelsize=9)
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
                    for m in overlay_modes:
                        phys = np.vstack([p for _, p, _ in points[m]])
                        ax.scatter(phys[:, j], phys[:, i], s=14, color=MODE_COLOR[m], alpha=0.8,
                                   edgecolor="white", linewidth=0.3,
                                   label=MODE_LABEL[m] if not first_legend_done else None)
                    ax.scatter(poly.z_star_phys[j], poly.z_star_phys[i], marker="D", s=55, color="black",
                               zorder=5, label="baseline (z*)" if not first_legend_done else None)
                    first_legend_done = True
                if i == n_z - 1:
                    ax.set_xlabel(f"{poly.names[j]}\n[{UNIT_LABEL.get(poly.units[j], poly.units[j] or 'n/a')}]", fontsize=11)
                else:
                    ax.set_xticklabels([])
                if j == 0:
                    ax.set_ylabel(f"{poly.names[i]}\n[{UNIT_LABEL.get(poly.units[i], poly.units[i] or 'n/a')}]", fontsize=11)
                else:
                    ax.set_yticklabels([])
                ax.tick_params(labelsize=9)
        if show_legend:
            handles, labels = axes[1, 0].get_legend_handles_labels()
            if handles:
                subfig.legend(handles, labels, loc="upper right", fontsize=11, frameon=False)
        subfig.suptitle(
            f"{MODE_LABEL[mode]} (n={len(samples_norm)}, acceptance {rate:.1%})",
            fontsize=14, fontweight="bold",
        )
    fig.suptitle(
        "MGA Near-Optimal Interior: Uniform Samples of Each Mode's Own Inner Approximation\n"
        "darker hexes = more of that mode's near-optimal volume",
        fontsize=17, fontweight="bold", y=0.99,
    )
    savefig(fig, "fig2_polytope_samples")


# ── fig3: pairwise Pearson correlation of the axes over each mode's OWN
# inner samples. Steen2026_Thesis Figure 7 analog: how the near-optimal
# *volume* trades axes off against each other (substitution, negative) or
# moves them together (co-requirement, positive) -- a property of the shape
# of the space, not of any one design, so it needs the uniform interior
# sample from fig2, not just the handful of certified vertices. One heatmap
# per mode, side by side, for the same bbo-vs-sampling comparison as fig2.

def fig3_axis_correlations(polys: dict[str, Polytope], samples: dict[str, tuple[np.ndarray, float]]) -> None:
    modes_to_plot = _hull_modes_to_plot(polys, samples)
    if not modes_to_plot:
        print("  skipping fig3_axis_correlations: no mode has >=20 inner samples")
        return

    fig, axes = plt.subplots(1, len(modes_to_plot), figsize=(6.5 * len(modes_to_plot) + 1.0, 6.0), squeeze=False)
    axes = axes[0]
    im = None
    for ax, mode in zip(axes, modes_to_plot):
        poly = polys[mode]
        samples_norm, rate = samples[mode]
        df = pd.DataFrame(poly.to_phys(samples_norm), columns=poly.names)
        corr = df.corr(method="pearson")
        im = ax.imshow(corr.to_numpy(), cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(len(poly.names)))
        ax.set_yticks(range(len(poly.names)))
        ax.set_xticklabels(poly.names, rotation=45, ha="right", fontsize=8)
        ax.set_yticklabels(poly.names, fontsize=8)
        for i in range(len(poly.names)):
            for j in range(len(poly.names)):
                v = corr.to_numpy()[i, j]
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7,
                        color="white" if abs(v) > 0.6 else "black")
        ax.set_title(f"{MODE_LABEL[mode]} (n={len(samples_norm)})", fontsize=10, fontweight="bold")
    fig.colorbar(im, ax=axes.tolist(), label="Pearson r", shrink=0.85)
    fig.suptitle(
        "MGA Pairwise Axis Correlations over Each Mode's Own Near-Optimal Interior\n"
        "negative = substitution, positive = co-requirement",
        fontsize=12, fontweight="bold",
    )
    savefig(fig, "fig3_axis_correlations")


# ── fig4: model-query and time comparison, matching near_optimal_tools' ────
# docs/examples/method_comparison.ipynb (2 metrics x 2 x-axes). max_separation
# is the oracle-style max-min L-inf distance (needs a MILP per evaluation, so
# it's only evaluated at sparse checkpoints, as the reference notebook itself
# does via its "eval_every" config); fraction_well_explored's ci_lower is the
# same cheap LP-based metric used throughout this script. Both are evaluated
# against each mode's own live, evolving outer approximation (outer_at(k),
# see load_native_outer_at) -- see the module docstring's "Convergence
# metric" section for why an earlier, shared frozen-box version was dropped.
# "seconds" is the real cumulative ZEN-garden solving_time from each solve's
# benchmarking.json -- not wall-clock around the whole loop like the
# reference notebook's TimedCallback.

def _gurobi_maxsep_solver(time_limit: float = 30.0):
    import pyomo.environ as pyo
    solver = pyo.SolverFactory("gurobi", solver_io="python", manage_env=True)
    solver.set_options(f"MIPGap=0.05 TimeLimit={time_limit} Threads=4 OutputFlag=0")
    return solver


def query_time_scores(poly: Polytope, X_norm: np.ndarray, solve_seconds: list[float],
                       eval_every: int, outer_at) -> pd.DataFrame:
    """outer_at(k) -> (A_k, b_k), the outer approximation to score checkpoint k
    against -- pass load_native_outer_at's result to score against a run's
    own evolving, cut-refined outer approximation, as the reference
    notebook's own score_run does."""
    # NaN entries are points with no logged solve (e.g. the shared frame's z*
    # borrowed for oracle, or a missing benchmarking.json): treated as 0s so
    # one NaN doesn't poison every later cumulative value, at the cost of a
    # slight undercount for that mode's total time.
    cum_seconds = np.cumsum(np.nan_to_num(solve_seconds, nan=0.0))
    n = len(X_norm)
    checkpoints = sorted({0, n - 1} | set(range(0, n, eval_every)))
    rows = []
    solver = _gurobi_maxsep_solver()
    for k in checkpoints:
        X_k = X_norm[: k + 1]
        A_k, b_k = outer_at(k)
        approx = approximation(A=A_k, b=b_k, X=X_k, name_list=poly.names, print_lv=0)
        cov = fraction_well_explored(approx, threshold=0.1, n_samples=500, alpha=0.05,
                                     method="jeffreys", seed_rng=0, print_lv=0)
        try:
            sep = max_separation(approx, pyomo_solver=solver, print_lv=0)
            distance = sep.distance
        except Exception as exc:
            print(f"    max_separation failed at k={k + 1}: {exc!r}")
            distance = np.nan
        rows.append({
            "n_queries": k + 1, "seconds": cum_seconds[k],
            "max_separation": distance, "ci_lower": cov.ci_lower, "ci_upper": cov.ci_upper,
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


def load_native_outer_at(run_dir: Path, run_poly: Polytope, mode: str):
    """outer_at(k) callable (see query_time_scores) that reconstructs
    run_dir's own evolving outer approximation at checkpoint k from its
    diagnostics.csv cut history, falling back to this run's own un-cut
    initial VMM box for any k before its first iterate. Works for any
    supf-mode run (sampling or bbo -- both save the same diagnostics.csv
    schema via supf_driver.py's shared _run_supf_mode)."""
    summary = run_dir / f"{MODEL}_{mode}_summary"
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
# metric is conceptually inapplicable to oracle -- fraction_well_explored/
# ci_lower is a post-hoc diagnostic (draw n_samples random test directions,
# check each one's gap against a STORED (A, b, X) snapshot) that doesn't
# care how that snapshot was produced. The reference notebook proves this
# directly: near_optimal_tools' own docs/examples/method_comparison.ipynb
# calls its ORACLE with save_intermediate=True precisely so it can rebuild
# an `approximation` object per iteration (its own oracle_states helper) and
# run BOTH max_separation and fraction_well_explored on it, exactly like
# every direction-based method there. This project's oracle run simply
# didn't set that flag (oracle_driver.py calls near_optimal_tools' ORACLE
# without it), so no per-iteration OA_A/OA_b snapshot survives for THIS run
# to rebuild that object from -- a data-availability gap in this particular
# download, fixable with a future oracle re-run, not a limitation of the
# method or the metric.
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


def _compute_fig4_scores(points: dict[str, list[tuple[str, np.ndarray, float]]],
                         polys: dict[str, Polytope]):
    """A native (own evolving approximation) score for every supf mode
    (sampling and bbo -- both now have surviving diagnostics.csv, unlike the
    old 3-mode script where only "probabilistic" did), and oracle's own
    certified max_separation-only gap (see load_oracle_native_gap). weights
    has no representation here at all -- see the module docstring's
    "Convergence metric" section. Shared by both fig4a (vs queries) and
    fig4b (vs time) so the MILP solves only run once."""
    eval_every = {"sampling": 10, "bbo": 10}

    # Each supf mode scored against its OWN evolving, cut-refined outer
    # approximation -- i.e. the reference notebook's own score_run
    # methodology exactly (see load_native_outer_at's docstring). Only
    # possible for sampling/bbo:
    # their diagnostics.csv logs the incremental cut_direction/cut_support_value
    # each iteration adds, letting outer_at(k) be replayed exactly; oracle's
    # diagnostics.csv logs its own certified max_min_distance instead (no
    # recomputation needed for that quantity, but no OA_A/OA_b snapshots
    # either, so its OWN evolving box can't be reconstructed here), and
    # weights never builds an outer approximation at all. Each mode is scored
    # against ITS OWN polytope (polys[mode]), not the shared frame -- their
    # own X/A/b differ even though the axes/units they're expressed in are
    # the same.
    native_scores = {}
    tolerance_prob = {}
    for mode, run_dir in (("sampling", SAMPLING_DIR), ("bbo", BBO_DIR)):
        if mode not in points or mode not in polys:
            continue
        run_poly = polys[mode]
        tolerance_prob[mode] = float(run_poly.convergence_threshold)
        outer_at = load_native_outer_at(run_dir, run_poly, mode)
        labels, phys, secs = zip(*points[mode])
        X_norm = run_poly.to_norm(np.vstack(phys))
        print(f"  fig4: scoring {mode} ({len(X_norm)} points, "
              f"every {eval_every.get(mode, 5)}th checkpoint, own evolving approximation)...")
        native_scores[mode] = query_time_scores(run_poly, X_norm, list(secs), eval_every.get(mode, 5),
                                                 outer_at=outer_at)

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

    return native_scores, tolerance_prob, oracle_native_gap, oracle_tol


def _comparison_figure(x_column: str, x_label: str, name: str, title: str,
                       native_scores: dict, tolerance_prob: dict, log_x: bool,
                       oracle_native_gap: pd.DataFrame | None = None, oracle_tol: float | None = None) -> None:
    """One query-time comparison figure, columns matching the reference
    notebook's own comparison_figure (near_optimal_tools/docs/examples/
    method_comparison.ipynb): max_separation | fraction_well_explored's
    ci_lower. Every mode shown is scored against ITS OWN live approximation
    -- sampling/bbo fully reconstructed and scored (see load_native_outer_at,
    reference-equivalent to the notebook's own score_run), oracle's own
    certified max_separation read directly off its diagnostics (see
    load_oracle_native_gap) with no ci_lower equivalent (see that function's
    docstring for why). weights never appears here: it never builds an
    outer approximation at all -- see fig0 for weights' own behaviour. An
    earlier version also scored every mode against one shared frozen initial
    box; dropped, see the module docstring's "Convergence metric" section."""
    fig, (ax_sep, ax_ci) = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)

    for mode, df in native_scores.items():
        color = MODE_COLOR[mode]
        group = df[df[x_column] > 0] if log_x else df  # "the initial state sits at zero"
        ax_sep.plot(group[x_column], group["max_separation"], marker="o", markersize=4,
                   color=color, label=MODE_LABEL[mode])
        ax_ci.plot(group[x_column], group["ci_lower"], marker="o", markersize=4, color=color)
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
    weights_note = "weights not shown here: it never builds an approximation at all."
    # NOT "oracle never samples directions so ci_lower is undefined for it"
    # -- fraction_well_explored is a post-hoc diagnostic that only needs a
    # stored (A, b, X) snapshot, and the reference notebook DOES compute it
    # for its own ORACLE (oracle_states relies on save_intermediate=True).
    # The real reason is narrower: THIS run's oracle_driver.py didn't
    # request that flag, so no per-iteration OA_A/OA_b snapshot survives to
    # build that object from -- a data gap specific to this download,
    # fixable in a future oracle re-run, not a property of the method itself.
    oracle_note = (
        "oracle has no line here (own max separation is shown on the left\n"
        "instead): fraction_well_explored needs a stored (A, b, X)\n"
        "snapshot per iteration, and this run's diagnostics don't save\n"
        "one (save_intermediate wasn't set) -- see load_oracle_native_gap."
        if oracle_native_gap is not None else
        "oracle not shown here at all: its diagnostics save neither a\n"
        "direction sample (no ci_lower) nor OA snapshots (no max\n"
        "separation reconstruction either) -- see load_oracle_native_gap."
    )
    ax_ci.text(
        0.02, 0.03, f"{oracle_note}\n{weights_note}",
        transform=ax_ci.transAxes, fontsize=6.8, color="#555555", va="bottom",
    )

    for ax in (ax_sep, ax_ci):
        ax.set_xlabel(x_label)
        if log_x:
            ax.set_xscale("log")
        ax.grid(alpha=0.3)
    ax_sep.legend(fontsize=8, frameon=False)
    fig.suptitle(title, fontsize=12, fontweight="bold")
    savefig(fig, name)


def fig4_query_time_comparison(points: dict[str, list[tuple[str, np.ndarray, float]]],
                               polys: dict[str, Polytope]) -> None:
    native_scores, tolerance_prob, oracle_native_gap, oracle_tol = _compute_fig4_scores(points, polys)
    if not native_scores and oracle_native_gap is None:
        print("  skipping fig4_query_time_comparison: no scored modes")
        return
    _comparison_figure(
        "n_queries", "number of model queries", "fig4a_query_comparison",
        "MGA Method Comparison vs. Model Queries\n"
        "(cf. near_optimal_tools docs/examples/method_comparison.ipynb, method_comparison.png)",
        native_scores, tolerance_prob, log_x=False,
        oracle_native_gap=oracle_native_gap, oracle_tol=oracle_tol,
    )
    _comparison_figure(
        "seconds", "cumulative ZEN-garden solving time [s]", "fig4b_time_comparison",
        "MGA Method Comparison vs. Cumulative Solving Time\n"
        "(cf. near_optimal_tools docs/examples/method_comparison.ipynb, method_comparison_time.png)",
        native_scores, tolerance_prob, log_x=True,
        oracle_native_gap=oracle_native_gap, oracle_tol=oracle_tol,
    )


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    print("Loading run polytopes...")
    polys: dict[str, Polytope] = {}
    for mode, run_dir in (("sampling", SAMPLING_DIR), ("bbo", BBO_DIR), ("oracle", ORACLE_DIR)):
        run_poly = try_load_run_polytope(run_dir, mode)
        if run_poly is not None:
            polys[mode] = run_poly
            print(f"  {mode}: polytope loaded ({run_poly.X.shape[0]} points on disk, "
                  f"converged={run_poly.converged}, {run_poly.run.get('iterations_done', '?')} iterations, "
                  f"tolerance_prob={run_poly.convergence_threshold:g})")
        else:
            note = "placeholder -- not yet downloaded" if mode == "oracle" else "skipping this mode entirely"
            print(f"  {mode}: no usable polytope.npz under {run_dir.relative_to(REPO_ROOT)} ({note})")

    if "sampling" not in polys and "bbo" not in polys:
        raise SystemExit(
            "Neither sampling nor bbo has a usable polytope -- nothing to build "
            "the shared coordinate frame or fig2/fig3 from."
        )

    # Shared coordinate frame (axis names/units/z*/scale/offset, used by fig0
    # and fig1) -- sampling's own polytope, falling back to bbo's if
    # sampling isn't available. See module docstring.
    frame_mode = "sampling" if "sampling" in polys else "bbo"
    poly = polys[frame_mode]
    print(f"Shared frame (from {frame_mode}): axes={poly.names}, epsilon={poly.epsilon:g}, c_star={poly.c_star:,.0f}")
    if "sampling" in polys and "bbo" in polys:
        z_diff = float(np.abs(polys["sampling"].z_star_phys - polys["bbo"].z_star_phys).max())
        if z_diff > 1e-6:
            print(f"  WARNING: sampling's and bbo's baselines (z*) differ by up to {z_diff:g} -- "
                  f"expected bit-for-bit identical (same model, same cost-optimal baseline solve)")
        else:
            print(f"  sanity check: sampling's and bbo's baselines (z*) agree to {z_diff:g} -- same problem, confirmed")

    points: dict[str, list[tuple[str, np.ndarray, float]]] = {}

    print("Loading weights mode...")
    w = load_weights_points(poly)
    if w:
        points["weights"] = w

    for mode, run_dir in (("sampling", SAMPLING_DIR), ("bbo", BBO_DIR)):
        if mode not in polys:
            continue
        print(f"Loading {mode} mode...")
        points[mode] = load_supf_points(polys[mode], run_dir)

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

    if "weights" in points:
        fig0_weights_axis_bars(poly, points["weights"])
    else:
        print("  skipping fig0_weights_axis_bars: weights mode unavailable")

    fig1_pairwise_points(poly, points)

    print("Sampling each mode's own inner approximation for fig2/fig3 (cf. Steen2026_Thesis "
          "Eq. 13 for what each acceptance rate means; this runs locally -- SciPy/LP only, "
          "no HPC resources needed)...")
    samples: dict[str, tuple[np.ndarray, float]] = {}
    for mode in ("sampling", "bbo", "oracle"):
        if mode not in polys:
            continue
        try:
            samples[mode] = cached_rejection_sample_inner(polys[mode], mode, n_propose=30_000)
        except Exception as exc:
            print(f"  {mode}: rejection sampling failed ({exc!r}); skipping its fig2/fig3 panel")

    fig2_polytope_samples(polys, points, samples)
    fig3_axis_correlations(polys, samples)
    fig4_query_time_comparison(points, polys)

    print(f"Done. Figures in {FIGURES_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
