"""Compare the three MGA exploration modes (weights, probabilistic, oracle)
run against Crystal_Ball_ind_heat_v8_0_nodiffusion on Euler.

All three modes explore the same near-optimal space: 6 axes (nuclear,
photovoltaics, wind_offshore, wind_onshore capacity additions, biomass
carrier import, total cost), epsilon = 0.1, same baseline solve -- so their
results live in one shared coordinate system and can be overlaid directly.
That shared frame (names/scale/offset/z_star/bounds, and the initial outer
box A0/b0) is taken from the probabilistic run's own saved polytope.npz
(data/outputs/euler_outputs_mga/..._MGA_probabilistic/
..._probabilistic_summary/). The "sanity checks" section of this file's dev
history (not reproduced here) confirmed weights' own baseline solve
reproduces that same z* bit-for-bit, and its explored points all fall
inside the VMM-derived box.

The probabilistic run uses pyoNearOpt's support-function sampling method
with `tolerance_prob` (the CI-lower-bound convergence bar in
`pyoNearOpt.metrics.ci_convergence_metric` -- see probabilistic_driver.py)
set to 0.95, n_samples=2000, max_iterations=500 -- a near-complete-coverage
bar (need 95% of sampled directions well-approximated). It ran 129
iterations (of its 500-iteration budget) and had NOT converged
(converged=False) when the run was stopped; final_gap = 0.140, and
diagnostics.csv shows ci_lower climbing steadily to 0.94 by the last
iteration, just short of the 0.95 bar. Note `tolerance_prob` is a
*confidence* target, not an error tolerance: higher means stricter (more of
the space must be certified), not looser -- the opposite sense of `epsilon`
or `tolerance_explore`.

(An earlier, more loosely converged probabilistic run at tolerance_prob=0.05
was dropped from this script and its Euler output folder deleted once the
0.95 run above was available -- it is no longer referenced anywhere below.)

Mode status as of writing:
  weights              every result folder intact. No polytope: each
                       iteration is a single min/max-weighted-capacity
                       solve, not a refinement step.
  probabilistic         fully intact, including its own polytope.npz +
                       diagnostics.csv (native ci_lower/ci_upper/mean_gap/
                       max_gap per iteration, computed against its own
                       refined outer approximation).
  oracle               oracle_summary/ (polytope.npz + diagnostics.csv) is
                       empty -- the run was interrupted before it could
                       write them, per the user's account of stopping it
                       because it seemed stuck revisiting the same vertex.
                       load_oracle_points below reconstructs its trajectory
                       from the individual oracle_iter_N / vmm_*_<axis>
                       Postprocess folders (which exist independently of the
                       lost summary) and degrades gracefully: unreadable
                       folders are skipped with a logged count, and if
                       nothing is readable oracle is dropped from every
                       figure rather than plotting fabricated data (this
                       mattered during development, when every var_dict.h5
                       under the oracle folder was truncated by a
                       mid-download disk-full -- re-running after a clean
                       download picked the run back up with no code
                       changes). That reconstruction confirms the user's
                       account precisely: iterations 13-85 (73 of 85, 86% of
                       the run) returned the exact same design point
                       bit-for-bit -- not just a slow approach to one, a
                       hard stall -- which is visible directly in fig1
                       (oracle's points forming one dense overlapping
                       cluster rather than spreading out) and in fig4's
                       max-separation trace (a flat plateau from ~solve 21
                       onward).

Convergence metric: pyoNearOpt.metrics.fraction_well_explored and
max_separation (the same machinery behind probabilistic's own
ci_convergence_metric and oracle's own max-min distance), evaluated in fig4
on each mode's growing set of known near-optimal points against one shared,
FROZEN initial outer box (probabilistic's A0/b0 -- the initial VMM box
before any cuts). This is deliberately not each method's own native metric:
oracle's and probabilistic's real outer approximations shrink via cuts as
they run (information the lost oracle summary can't provide, and weights
never produces at all), so comparing native metrics would mostly compare cut
quality, not point coverage. Freezing the box isolates "how much of the
near-optimal box do the known points cover" as the common denominator -- the
only question that is fairly askable of weights' 6 directional solves too.

Figures (data/outputs/figures/mga_results/):
  fig0_weights_axis_bars        weights-mode capacity ADDITION per axis, per
                                 iteration, vs baseline (4 tech axes; weights
                                 never touches the biomass/cost axes as
                                 exploration directions).
  fig1_pairwise_points           pairwise projections of every mode's actual
                                 visited points, colour-coded by mode.
  fig2_polytope_samples          hexbin density of a uniform sample of the
                                 INNER approximation (rejection-sampled from
                                 probabilistic's outer body -- see
                                 rejection_sample_inner's docstring and
                                 Steen2026_Thesis Sec 3.3), diagonal = per-axis
                                 marginals, green outline = exact 2D
                                 projection of the inner hull, modes overlaid.
  fig3_axis_correlations         Pearson correlation heatmap of the 6 axes
                                 over the same inner-hull sample (Steen
                                 2026_Thesis Figure 7 analog): which axes
                                 substitute (negative) or move together
                                 (positive) across the near-optimal volume.
                                 Pearson r is invariant to per-axis affine
                                 rescaling (verified: physical-unit and
                                 normalised draws give the same matrix to
                                 1e-14), so this is on physical units purely
                                 for readability -- normalising would not
                                 change a single value.
  fig4a/b_query/time_comparison  Two figures, matching near_optimal_tools' own
                                 docs/examples/method_comparison.ipynb layout
                                 exactly (its method_comparison.png/_time.png):
                                 columns are max_separation and
                                 fraction_well_explored's ci_lower; fig4a's
                                 x-axis is number of model queries, fig4b's is
                                 cumulative real ZEN-garden solving time (log).
                                 Each has 2 rows: frozen initial box (all
                                 available modes, this project's own choice for
                                 a shared comparison) and the probabilistic
                                 run's own evolving, cut-refined outer
                                 approximation (reference-equivalent, the only
                                 mode whose cut history survives -- see
                                 load_native_outer_at). This file's only
                                 per-mode convergence trace now (an earlier
                                 fig1_convergence and
                                 fig2_axis_range_comparison were dropped:
                                 the former didn't add much beyond this
                                 figure's own max-separation/query panel, and
                                 the latter mostly just showed which modes
                                 ran VMM -- probabilistic and oracle both do,
                                 so they trivially span the full axis range,
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

MODEL = "Crystal_Ball_ind_heat_v8_0_nodiffusion"
RUN_PREFIX = f"{MODEL}_2050_1a_5a_interval_5ts_MGA"
WEIGHTS_DIR = MGA_ROOT / f"{RUN_PREFIX}_weights"
PROBABILISTIC_DIR = MGA_ROOT / f"{RUN_PREFIX}_probabilistic"
ORACLE_DIR = MGA_ROOT / f"{RUN_PREFIX}_oracle"

# Positional colours reused from figure_settings.SCENARIO_PALETTE (ETH
# corporate design: blue, petrol, green, olive, red, magenta, grey), per this
# project's convention of never inventing a separate palette for print
# figures. weights was ETH blue, too close to probabilistic's original
# petrol to tell apart at a glance; weights moved to green; oracle keeps red.
_ETH_BLUE, _ETH_GREEN, _ETH_RED = (
    SCENARIO_PALETTE[0], SCENARIO_PALETTE[2], SCENARIO_PALETTE[4],
)
MODE_COLOR = {
    "weights": _ETH_GREEN,
    "probabilistic": _ETH_BLUE,
    "oracle": _ETH_RED,
}
MODE_LABEL = {
    "weights": "Weights",
    # $\tau$ (mathtext, "cm" fontset) rather than a literal unicode tau --
    # the plain text font (cmr10) has no tau glyph.
    "probabilistic": r"Probabilistic ($\tau$=0.95)",
    "oracle": "Oracle",
}
MODES = ("weights", "probabilistic", "oracle")

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


def load_shared_polytope() -> Polytope:
    """The probabilistic run's own polytope.npz: the shared coordinate
    frame (names/scale/offset/z_star/bounds/initial box) every mode is
    expressed in, plus its own true (cut-refined) inner+outer approximation."""
    summary = PROBABILISTIC_DIR / f"{MODEL}_probabilistic_summary"
    poly_files = sorted(summary.glob("polytope*.npz"))
    if not poly_files:
        raise FileNotFoundError(
            f"No polytope*.npz in {summary}; the probabilistic run is "
            f"this script's shared coordinate frame and must be present."
        )
    return load_polytope(poly_files[0])


def load_probabilistic_points(poly: Polytope, run_dir: Path) -> list[tuple[str, np.ndarray, float]]:
    """[(label, phys_point, solving_time)] for the probabilistic run's own
    polytope.npz, in solve order (baseline/VMM points, then refinement
    iterates)."""
    run_poly = poly
    iterate_count = 0
    rows = []
    for lab, pt in zip(run_poly.point_origin, run_poly.X):
        if lab == "z_star":
            folder = run_dir / MODEL
        elif lab == "iterate":
            iterate_count += 1
            folder = run_dir / f"{MODEL}_probabilistic_iter_{iterate_count}"
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


# ── Oracle mode (best-effort reconstruction) ─────────────────────────────

def load_oracle_points(poly: Polytope) -> list[tuple[str, np.ndarray, float]] | None:
    """[("z_star", ...), ("max:<axis>"/"min:<axis>", ...)*, (iter_n, ...)*]
    in solve order, or None if nothing beyond z* is readable.

    Prefers the official oracle_summary/polytope.npz + diagnostics.csv when
    present and loadable; otherwise reconstructs from the individual
    vmm_<sense>_<axis> and oracle_iter_N Postprocess folders that survive
    independently of that summary. See the module docstring for why this is
    necessary and how it degrades when folders are unreadable.
    """
    summary = ORACLE_DIR / f"{MODEL}_oracle_summary"
    poly_files = sorted(summary.glob("polytope*.npz")) if summary.exists() else []
    if poly_files:
        try:
            official = load_polytope(poly_files[0])
            print(f"  oracle: loaded official artifacts from {summary.relative_to(REPO_ROOT)}")
            labels = official.point_origin
            points_norm = official.X
            # No per-point folder mapping from the summary alone (repeated
            # "iterate" origins aren't indexed), so solving_time is unknown here.
            return [(lab, official.to_phys(pt), float("nan")) for lab, pt in zip(labels, points_norm)]
        except Exception as exc:
            print(f"  oracle: official artifacts present but unreadable ({exc!r}); reconstructing from folders")

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
        f"(baseline folder is empty; z* taken from the shared probabilistic frame)"
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
    fig, axes = plt.subplots(n - 1, n - 1, figsize=(3.2 * (n - 1), 3.2 * (n - 1)), squeeze=False)
    for i in range(1, n):
        for j in range(0, n - 1):
            ax = axes[i - 1, j]
            if j >= i:
                ax.axis("off")
                continue
            plot_fn(ax, j, i)
            if i == n - 1:
                ax.set_xlabel(f"{names[j]}\n[{UNIT_LABEL.get(units[j], units[j] or 'n/a')}]", fontsize=8)
            else:
                ax.set_xticklabels([])
            if j == 0:
                ax.set_ylabel(f"{names[i]}\n[{UNIT_LABEL.get(units[i], units[i] or 'n/a')}]", fontsize=8)
            else:
                ax.set_yticklabels([])
            ax.tick_params(labelsize=7)
            ax.grid(alpha=0.25)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper right", fontsize=9, frameon=False)
    fig.suptitle(title, fontsize=12, fontweight="bold")
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
# 10-D, 700-iteration ORACLE certificate got 11.6% over 9.3M proposals; ours,
# a 6-D, 129-iteration probabilistic run (tolerance_prob=0.95), gets 84%
# (see the printed acceptance rate) -- much higher than Steen's, not the same order of
# magnitude, consistent with tolerance_prob=0.95 pushing this run to
# near-complete coverage of its (lower-dimensional, 6-D vs. his 10-D) space
# rather than a coincidence; the useful cross-check is still that the number
# is a sane fraction and not near-0 or near-1-by-construction, i.e. nothing
# about the geometry here is pathological. Steen's own proposal count is well
# beyond this script's purpose; a few tens of thousands is enough for a
# readable density plot at the same statistical validity, just a noisier one.
def _poly_fingerprint(poly: Polytope) -> str:
    """Identifies which polytope a cached sample was drawn from, so a stale
    cache (e.g. after re-downloading a re-run probabilistic mode) is
    detected and regenerated rather than silently reused."""
    import hashlib
    h = hashlib.sha256()
    h.update(poly.X.tobytes())
    h.update(poly.A.tobytes())
    h.update(poly.b.tobytes())
    return h.hexdigest()


SAMPLING_CACHE = MGA_ROOT / "mga_inner_sampling" / "rejection_sample_probabilistic_inner.npz"


def cached_rejection_sample_inner(poly: Polytope, n_propose: int = 30_000,
                                   seed: int = 0) -> tuple[np.ndarray, float]:
    """rejection_sample_inner, cached to SAMPLING_CACHE: the sampling in fig2
    and fig3 depends only on the probabilistic run's polytope (fixed once
    that run is done, unlike the still-arriving oracle data), so redoing it
    on every script invocation is pure waste. Regenerates automatically if
    the polytope, n_propose, or seed have changed since the cache was written."""
    fingerprint = _poly_fingerprint(poly)
    if SAMPLING_CACHE.exists():
        cached = np.load(SAMPLING_CACHE)
        if (str(cached["fingerprint"]) == fingerprint
                and int(cached["n_propose"]) == n_propose
                and int(cached["seed"]) == seed):
            print(f"  using cached inner sample from {SAMPLING_CACHE.relative_to(REPO_ROOT)} "
                  f"({len(cached['samples_norm'])} points, {float(cached['rate']):.2%} acceptance)")
            return cached["samples_norm"], float(cached["rate"])
        print("  cached inner sample is stale (polytope/n_propose/seed changed); regenerating")

    samples_norm, rate = rejection_sample_inner(poly, n_propose, seed)
    SAMPLING_CACHE.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        SAMPLING_CACHE, samples_norm=samples_norm, rate=rate,
        n_propose=n_propose, seed=seed, fingerprint=fingerprint,
    )
    print(f"  cached inner sample to {SAMPLING_CACHE.relative_to(REPO_ROOT)}")
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


# ── fig4: hexbin density of the inner approximation's uniform interior samples ─
# Styled after Steen2026_Thesis Figure 6: hexbin density lower triangle, the
# exact 2D projection of I as a green outline (a linear projection of a convex
# hull is the hull of the projected vertices, so this is just ConvexHull on
# poly.X's projected columns -- no extra approximation), per-axis marginal
# histograms on the diagonal, baseline marked. Modes are overlaid as before.

def fig2_polytope_samples(poly: Polytope, points: dict[str, list[tuple[str, np.ndarray, float]]],
                           samples_norm: np.ndarray, rate: float) -> None:
    if len(samples_norm) < 20:
        print("  skipping fig2_polytope_samples: too few accepted samples for a readable density")
        return
    samples_phys = poly.to_phys(samples_norm)
    modes = [m for m in MODES if m in points]

    from scipy.spatial import ConvexHull

    n_z = poly.n_axes
    if n_z < 2:
        print("  skipping fig2_polytope_samples: fewer than 2 design axes")
        return
    # Full n_z x n_z triangular grid (unlike _pairwise_grid's (n-1) x (n-1)
    # off-diagonal-only layout used by fig3): row/col i==j is axis i's own
    # marginal, so every axis gets one, matching Steen2026_Thesis Figure 6.
    fig, axes = plt.subplots(n_z, n_z, figsize=(3.0 * n_z, 3.0 * n_z), squeeze=False)
    first_legend_done = False
    for i in range(n_z):
        for j in range(n_z):
            ax = axes[i, j]
            if j > i:
                ax.axis("off")
                continue
            if j == i:  # diagonal: per-axis marginal of the inner-body sample
                ax.hist(samples_phys[:, i], bins=25, color="#6b1f5c", alpha=0.8)
                ax.set_yticks([])
                ax.tick_params(labelsize=7)
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
                            label="exact 2D projection of inner hull" if not first_legend_done else None)
                except Exception:
                    pass  # degenerate projection (e.g. collinear points); skip the outline
                for mode in modes:
                    phys = np.vstack([p for _, p, _ in points[mode]])
                    ax.scatter(phys[:, j], phys[:, i], s=14, color=MODE_COLOR[mode], alpha=0.8,
                               edgecolor="white", linewidth=0.3,
                               label=MODE_LABEL[mode] if not first_legend_done else None)
                ax.scatter(poly.z_star_phys[j], poly.z_star_phys[i], marker="D", s=55, color="black",
                           zorder=5, label="baseline (z*)" if not first_legend_done else None)
                first_legend_done = True
            if i == n_z - 1:
                ax.set_xlabel(f"{poly.names[j]}\n[{UNIT_LABEL.get(poly.units[j], poly.units[j] or 'n/a')}]", fontsize=8)
            else:
                ax.set_xticklabels([])
            if j == 0:
                ax.set_ylabel(f"{poly.names[i]}\n[{UNIT_LABEL.get(poly.units[i], poly.units[i] or 'n/a')}]", fontsize=8)
            else:
                ax.set_yticklabels([])
            ax.tick_params(labelsize=7)
    handles, labels = axes[1, 0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper right", fontsize=9, frameon=False)
    fig.suptitle(
        f"MGA Near-Optimal Interior: Uniform Samples of the Inner Approximation (n={len(samples_norm)}, "
        f"acceptance {rate:.1%})\nprobabilistic's certified hull; darker hexes = more of the near-optimal volume",
        fontsize=12, fontweight="bold",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    savefig(fig, "fig2_polytope_samples")


# ── fig3: pairwise Pearson correlation of the axes over the inner samples ──
# Steen2026_Thesis Figure 7 analog: how the near-optimal *volume* trades axes
# off against each other (substitution, negative) or moves them together
# (co-requirement, positive) -- a property of the space itself, not of any
# single design, so it needs the uniform interior sample from fig4, not just
# the handful of certified vertices.

def fig3_axis_correlations(poly: Polytope, samples_norm: np.ndarray) -> None:
    if len(samples_norm) < 20:
        print("  skipping fig3_axis_correlations: too few inner samples")
        return
    df = pd.DataFrame(poly.to_phys(samples_norm), columns=poly.names)
    corr = df.corr(method="pearson")

    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    im = ax.imshow(corr.to_numpy(), cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(poly.names)))
    ax.set_yticks(range(len(poly.names)))
    ax.set_xticklabels(poly.names, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(poly.names, fontsize=9)
    for i in range(len(poly.names)):
        for j in range(len(poly.names)):
            v = corr.to_numpy()[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8,
                    color="white" if abs(v) > 0.6 else "black")
    fig.colorbar(im, ax=ax, label="Pearson r", shrink=0.85)
    ax.set_title(
        f"MGA Pairwise Axis Correlations over the Near-Optimal Interior (n={len(samples_norm)})\n"
        "negative = substitution, positive = co-requirement (probabilistic's inner hull)",
        fontsize=11, fontweight="bold",
    )
    fig.tight_layout()
    savefig(fig, "fig3_axis_correlations")


# ── fig4: model-query and time comparison, matching near_optimal_tools' ────
# docs/examples/method_comparison.ipynb (2 metrics x 2 x-axes). max_separation
# is the oracle-style max-min L-inf distance (needs a MILP per evaluation, so
# it's only evaluated at sparse checkpoints, as the reference notebook itself
# does via its "eval_every" config); fraction_well_explored's ci_lower is the
# same cheap LP-based metric used throughout this script. Both are evaluated
# against poly's frozen initial outer box (poly.A/b up to n_initial_rows --
# i.e. ignoring any cuts later refined into the full poly.A) rather than each
# mode's own native, possibly-cut-refined outer approximation -- see the
# module docstring's "Convergence metric" section for why. "seconds" is the
# real cumulative ZEN-garden solving_time from each solve's benchmarking.json
# -- not wall-clock around the whole loop like the reference notebook's
# TimedCallback, and for oracle specifically it excludes the per-iteration
# max-min MILP time (lost with the oracle_summary that was never written),
# so oracle's true wall time is understated here; see module docstring.

def _gurobi_maxsep_solver(time_limit: float = 30.0):
    import pyomo.environ as pyo
    solver = pyo.SolverFactory("gurobi", solver_io="python", manage_env=True)
    solver.set_options(f"MIPGap=0.05 TimeLimit={time_limit} Threads=4 OutputFlag=0")
    return solver


def query_time_scores(poly: Polytope, X_norm: np.ndarray, solve_seconds: list[float],
                       eval_every: int, outer_at=None) -> pd.DataFrame:
    """outer_at(k) -> (A_k, b_k), the outer approximation to score checkpoint k
    against. Defaults to poly's frozen initial box for every k (see the module
    docstring's "Convergence metric" section); pass native_outer_at's result
    instead to score against each run's own evolving, cut-refined outer
    approximation, as the reference notebook's own score_run does."""
    if outer_at is None:
        A0, b0 = poly.A[: poly.n_initial_rows], poly.b[: poly.n_initial_rows]
        outer_at = lambda k: (A0, b0)
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


# ── Native (own evolving) outer approximation, probabilistic modes only ──
#
# The reference notebook's own score_run scores each method against ITS OWN
# stored approximation state at each checkpoint (oracle_states/direction_
# states keep a full A/b/X snapshot per iteration) -- not a shared frozen
# box. query_time_scores above deliberately does NOT do that (see its
# docstring and the module docstring's "Convergence metric" section): oracle's
# own cut history was lost with its oracle_summary/, and weights never builds
# an outer approximation at all, so a fair *shared* comparison across all
# three modes needs everyone evaluated against the same fixed initial box.
#
# But for the probabilistic run specifically, the cut history was NOT lost:
# supf_explore.explore calls poly_approx.add_point(new_point) and
# poly_approx.add_cut(direction, support_value) exactly once per iteration
# (near_optimal_tools/src/pyoNearOpt/exploration_methods/supf_explore.py),
# and diagnostics.csv logs precisely those two raw arguments every iteration.
# Replaying them in order therefore reconstructs each iteration's own live
# A_k/b_k exactly -- verified directly: reconstructing the run's full cut
# history this way and comparing against its own saved final A/b gives an
# identical feasible region (same shape, and every one of 20,000 random test
# points agrees on which polytope contains it). So this project CAN add a
# faithful, reference-notebook-equivalent "own approximation" row for
# probabilistic; it still cannot for oracle (no surviving cut data at all)
# or weights (no such object exists for that mode).
def _parse_diagnostics_vector(s: str) -> np.ndarray:
    """Parses one diagnostics.csv cut_direction cell -- numpy's default
    array repr (e.g. '[ 0.36 -0.62 ... ]', occasionally wrapped over several
    lines for wide vectors), not JSON/literal-eval-able."""
    return np.array([float(x) for x in s.strip().lstrip("[").rstrip("]").split()])


def load_native_outer_at(run_dir: Path, run_poly: Polytope):
    """outer_at(k) callable (see query_time_scores) that reconstructs
    run_dir's own evolving outer approximation at checkpoint k from its
    diagnostics.csv cut history, falling back to the frozen initial box for
    any k before the first iterate (the initial VMM/baseline points)."""
    summary = run_dir / f"{MODEL}_probabilistic_summary"
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


def _compute_fig4_scores(poly: Polytope, points: dict[str, list[tuple[str, np.ndarray, float]]]):
    """Frozen-box scores for every available mode, plus a native (own evolving
    approximation) score for the probabilistic mode. Shared by both fig4a (vs
    queries) and fig4b (vs time) so the MILP solves only run once."""
    modes = [m for m in MODES if m in points]
    eval_every = {"weights": 1, "probabilistic": 10, "oracle": 10}
    scores = {}
    for mode in modes:
        labels, phys, secs = zip(*points[mode])
        X_norm = poly.to_norm(np.vstack(phys))
        print(f"  fig4: scoring {mode} ({len(X_norm)} points, "
              f"every {eval_every.get(mode, 5)}th checkpoint, frozen box)...")
        scores[mode] = query_time_scores(poly, X_norm, list(secs), eval_every.get(mode, 5))

    # Native row: the probabilistic run scored against its OWN evolving,
    # cut-refined outer approximation instead of the frozen box -- i.e. the
    # reference notebook's own score_run methodology exactly (see
    # load_native_outer_at's docstring). Only possible for probabilistic:
    # oracle's cut history is gone (data-loss note) and weights never builds
    # an outer approximation at all.
    native_scores = {}
    tolerance_prob = {}
    for mode, run_dir in (("probabilistic", PROBABILISTIC_DIR),):
        if mode not in points:
            continue
        run_poly = poly
        tolerance_prob[mode] = float(run_poly.convergence_threshold)
        outer_at = load_native_outer_at(run_dir, run_poly)
        labels, phys, secs = zip(*points[mode])
        X_norm = poly.to_norm(np.vstack(phys))
        print(f"  fig4: scoring {mode} ({len(X_norm)} points, "
              f"every {eval_every.get(mode, 5)}th checkpoint, own evolving approximation)...")
        native_scores[mode] = query_time_scores(poly, X_norm, list(secs), eval_every.get(mode, 5),
                                                 outer_at=outer_at)
    return scores, native_scores, tolerance_prob


def _comparison_figure(x_column: str, x_label: str, name: str, title: str,
                       scores: dict, native_scores: dict, tolerance_prob: dict, log_x: bool) -> None:
    """One query-time comparison figure, columns/rows matching the reference
    notebook's own comparison_figure exactly (near_optimal_tools/docs/examples/
    method_comparison.ipynb): columns are the two metrics (max_separation |
    fraction_well_explored's ci_lower), not the two x-axis choices -- an
    earlier version of this project's fig4 put the x-axis choice in the
    columns instead (metric in rows), which showed the same four combinations
    but did not read side by side against the reference's own figures the way
    this layout does. The reference itself makes one row per test-problem
    dimensionality (its "case"); this project has only one real problem (the
    6-D MGA space), so the row grouping is repurposed for "which outer
    approximation was scored against" instead: frozen initial box (row 1, all
    available modes, comparable but not each mode's own criterion -- see the
    module docstring's "Convergence metric" section) vs. each probabilistic
    run's own live, cut-refined approximation (row 2, reference-equivalent,
    restricted to the two modes whose cut history survives)."""
    has_native = bool(native_scores)
    n_rows = 2 if has_native else 1
    fig, axes = plt.subplots(n_rows, 2, figsize=(11, 4.2 * n_rows), squeeze=False, constrained_layout=True)
    ax_sep, ax_ci = axes[0]

    for mode, df in scores.items():
        color = MODE_COLOR[mode]
        group = df[df[x_column] > 0] if log_x else df  # "the initial state sits at zero"
        ax_sep.plot(group[x_column], group["max_separation"], marker="o", markersize=4,
                   color=color, label=MODE_LABEL[mode])
        ax_ci.plot(group[x_column], group["ci_lower"], marker="o", markersize=4, color=color)
    ax_sep.set_yscale("log")
    ax_sep.set_title("max separation (frozen initial box)")
    ax_sep.set_ylabel("max $L_\\infty$ separation")
    ax_ci.set_title("directions with gap $\\leq$ 0.1, 95% CI lower bound (frozen initial box)")
    ax_ci.set_ylabel("fraction of well-explored directions")
    ax_ci.set_ylim(-0.03, 1.03)

    if has_native:
        ax_sep_n, ax_ci_n = axes[1]
        for mode, df in native_scores.items():
            color = MODE_COLOR[mode]
            group = df[df[x_column] > 0] if log_x else df
            ax_sep_n.plot(group[x_column], group["max_separation"], marker="o", markersize=4, color=color)
            ax_ci_n.plot(group[x_column], group["ci_lower"], marker="o", markersize=4, color=color)
            # Each run's own real convergence target for THIS metric: its own
            # tolerance_prob (0.05 short / 0.95 long -- see README), colour-
            # matched, exactly like the reference's cfg["tolerance_prob"]
            # axhline. No target line on the max_separation panel: unlike
            # ORACLE's own "tol" in the reference notebook, probabilistic mode
            # never targets an exact worst-case max_separation bound at all.
            ax_ci_n.axhline(tolerance_prob[mode], color=color, ls="--", lw=1)
        ax_sep_n.set_yscale("log")
        ax_sep_n.set_title("max separation (own evolving approximation)")
        ax_sep_n.set_ylabel("max $L_\\infty$ separation")
        ax_ci_n.set_title("directions with gap $\\leq$ 0.1, 95% CI lower bound (own evolving approximation)")
        ax_ci_n.set_ylabel("fraction of well-explored directions")
        ax_ci_n.set_ylim(-0.03, 1.03)
        ax_sep_n.text(
            0.02, 0.03, "oracle/weights not shown here: oracle's cut history\nwas lost; weights never builds one.",
            transform=ax_sep_n.transAxes, fontsize=7.5, color="#555555", va="bottom",
        )

    for ax in axes.flat:
        ax.set_xlabel(x_label)
        if log_x:
            ax.set_xscale("log")
        ax.grid(alpha=0.3)
    ax_sep.legend(fontsize=8, frameon=False)
    fig.suptitle(title, fontsize=12, fontweight="bold")
    savefig(fig, name)


def fig4_query_time_comparison(poly: Polytope, points: dict[str, list[tuple[str, np.ndarray, float]]]) -> None:
    scores, native_scores, tolerance_prob = _compute_fig4_scores(poly, points)
    if not scores:
        print("  skipping fig4_query_time_comparison: no scored modes")
        return
    _comparison_figure(
        "n_queries", "number of model queries", "fig4a_query_comparison",
        "MGA Method Comparison vs. Model Queries\n"
        "(cf. near_optimal_tools docs/examples/method_comparison.ipynb, method_comparison.png)",
        scores, native_scores, tolerance_prob, log_x=False,
    )
    _comparison_figure(
        "seconds", "cumulative ZEN-garden solving time [s]", "fig4b_time_comparison",
        "MGA Method Comparison vs. Cumulative Solving Time\n"
        "(cf. near_optimal_tools docs/examples/method_comparison.ipynb, method_comparison_time.png)",
        scores, native_scores, tolerance_prob, log_x=True,
    )


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    poly = load_shared_polytope()
    print(f"Shared frame: axes={poly.names}, epsilon={poly.epsilon:g}, c_star={poly.c_star:,.0f}")

    points: dict[str, list[tuple[str, np.ndarray, float]]] = {}

    print("Loading weights mode...")
    w = load_weights_points(poly)
    if w:
        points["weights"] = w

    print("Loading probabilistic mode...")
    points["probabilistic"] = load_probabilistic_points(poly, PROBABILISTIC_DIR)
    print(f"  probabilistic: {poly.X.shape[0]} points on disk "
          f"(converged={poly.converged}, {poly.run.get('iterations_done', '?')} iterations, "
          f"tolerance_prob={poly.convergence_threshold:g})")

    print("Loading oracle mode (best effort)...")
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

    print("Sampling the inner approximation for fig2/fig3 (cf. Steen2026_Thesis Eq. 13 "
          "for what the acceptance rate below means)...")
    try:
        samples_norm, rate = cached_rejection_sample_inner(poly, n_propose=30_000)
    except Exception as exc:
        print(f"  rejection sampling failed ({exc!r}); skipping fig2/fig3")
        samples_norm, rate = np.empty((0, poly.n_axes)), float("nan")

    fig2_polytope_samples(poly, points, samples_norm, rate)
    fig3_axis_correlations(poly, samples_norm)
    fig4_query_time_comparison(poly, points)

    print(f"Done. Figures in {FIGURES_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
