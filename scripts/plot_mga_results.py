"""Generate figures from MGA runs: the completed weights-mode run and an
ORACLE run's progress (whole or partial/interrupted).

  fig0_weights_comparison - weights-mode run (Crystal_Ball_HG_v6_1_..._MGA,
                          4 completed iterations: max PV / max wind / max
                          coal / max gas): capacity per axis, per iteration,
                          vs baseline. Loaded directly via zen_garden.Results
                          (get_capacity from figures_by_run.py) -- no
                          polytope involved, weights mode never builds one.

The remaining figures cover an ORACLE run's progress via the polytope.npz +
diagnostics.csv written by zen_garden.plugins.mga.plugin._run_oracle_mode
(ZEN-garden-mga fork, Code-CleanUp branch) through polytope_io.load_polytope.
An ORACLE run that was interrupted (e.g. SIGINT) before converging or
reaching max_iterations still produces both files -- refine_approximations()
returns its accumulated result up to the last completed iteration rather
than losing it, so these are "info on the iterations completed so far", not
just a converged-run summary:

  fig1_convergence      - ORACLE's max-min distance per iteration vs tolerance
  fig2_variable_ranges  - per-axis near-optimal range (outer approximation)
                          from whatever's been explored so far, physical
                          units, baseline z* marked
  fig3_pairwise_points  - pairwise projections of the design points ORACLE
                          actually visited (poly.X) so far, physical units
  fig4_polytope_samples - denser uniform samples of the outer approximation
                          as currently constrained (pyoNearOpt.PolytopeSamples,
                          PolyRound + Vaidya walk), same pairwise layout as
                          fig3 for comparison

fig4 is best-effort: PolyRound's rounding step can fail on a degenerate or
very high-aspect-ratio polytope, so it's wrapped and skipped with a message
rather than aborting the other figures.

Reuses this project's own figure conventions (cmr10 font, ETH corporate
palette, savefig-to-SVG pattern) from generate_si_figures.py / figure_settings.py
rather than re-deriving them.

Usage:
    python scripts/plot_mga_results.py [oracle_summary_dir]

    If omitted, auto-discovers the most recently modified *_oracle_summary
    folder under data/outputs/local_outputs/ (searched recursively). Pass
    "" (empty string) or any nonexistent path to skip the oracle figures
    entirely and only generate fig0_weights_comparison.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Match MT_report_HG's font — see generate_si_figures.py for the rationale
# (cmr10 ships inside matplotlib, no system LaTeX/font install needed).
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["cmr10"],
    "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True,
    "axes.unicode_minus": False,
})

from figure_settings import LOCAL_ROOT
from figures_by_run import get_capacity
from zen_garden import Results
from zen_garden.plugins.mga.polytope_io import Polytope, load_polytope
from pyoNearOpt.polytope_approximation.approximation_class import approximation
from pyoNearOpt.polytope_approximation.polytope_samples import PolytopeSamples

FIGURES_DIR = REPO_ROOT / "data" / "outputs" / "figures" / "mga_results"

_ETH_BLUE, _ETH_RED, _ETH_PETROL, _ETH_BRONZE, _ETH_GREEN = (
    "#215CAF", "#B7352D", "#007894", "#8E6713", "#627313")

# The 4 MGA exploration axes, shared by both weights mode and oracle mode
# (see data/config_mga.json): axis name -> member technologies (a lumped
# axis, "wind", sums onshore + offshore).
MGA_AXES = [
    ("photovoltaics", ["photovoltaics"]),
    ("wind", ["wind_onshore", "wind_offshore"]),
    ("hard_coal_plant", ["hard_coal_plant"]),
    ("natural_gas_turbine", ["natural_gas_turbine"]),
]

# Weights-mode run (completed before the switch to oracle mode): baseline +
# one folder per iteration, sibling subfolders under this same run folder.
# Iteration order matches config_mga.json's weights-mode "iterations" list
# at the time that run was made: photovoltaics, wind, hard_coal_plant,
# natural_gas_turbine -- same order as MGA_AXES above.
WEIGHTS_RUN_DIR = LOCAL_ROOT / "Crystal_Ball_HG_v6_1_2025_1a_5a_interval_5ts_MGA"
WEIGHTS_BASELINE_SUBDIR = "Crystal_Ball_HG_v6_1"
WEIGHTS_ITERATIONS = [
    ("mga_iter_0", "Max PV"),
    ("mga_iter_1", "Max wind"),
    ("mga_iter_2", "Max coal"),
    ("mga_iter_3", "Max gas"),
]


def savefig(fig: plt.Figure, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.svg"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {path.relative_to(REPO_ROOT)}")


# ── 0: Weights-mode run (baseline + 4 completed iterations) ─────────────

def _axis_capacity(r: Results, members: list[str]) -> float:
    cap = get_capacity(r, members, "power")
    return float(cap.to_numpy().sum()) if not cap.empty else 0.0


def fig0_weights_comparison() -> None:
    if not WEIGHTS_RUN_DIR.exists():
        print(f"  skipping fig0_weights_comparison: {WEIGHTS_RUN_DIR} not found")
        return
    baseline_path = WEIGHTS_RUN_DIR / WEIGHTS_BASELINE_SUBDIR
    if not baseline_path.exists():
        print(f"  skipping fig0_weights_comparison: baseline folder {baseline_path} not found")
        return

    runs = [("Baseline", Results(path=str(baseline_path)))]
    for subdir, label in WEIGHTS_ITERATIONS:
        path = WEIGHTS_RUN_DIR / f"{WEIGHTS_BASELINE_SUBDIR}_{subdir}"
        if not path.exists():
            print(f"  fig0_weights_comparison: {path} not found, skipping")
            continue
        runs.append((label, Results(path=str(path))))
    if len(runs) < 2:
        print("  skipping fig0_weights_comparison: no completed iterations found")
        return

    df = pd.DataFrame(
        {label: [_axis_capacity(r, members) for _, members in MGA_AXES] for label, r in runs},
        index=[name for name, _ in MGA_AXES],
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    n = len(df.columns)
    width = 0.8 / n
    x = np.arange(len(df))
    colors = [_ETH_RED, _ETH_BLUE, _ETH_PETROL, _ETH_BRONZE, _ETH_GREEN]
    for i, label in enumerate(df.columns):
        offsets = x + (i - (n - 1) / 2) * width
        ax.bar(offsets, df[label].to_numpy(), width, label=label,
               color=colors[i % len(colors)], edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(df.index, rotation=15, ha="right", fontsize=9)
    ax.set_ylabel("capacity [GW]")
    ax.set_title("MGA Weights-Mode: Capacity per Axis, per Maximized Direction\n"
                 "(each iteration maximizes ONE axis; bars show its effect on all 4)",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, frameon=False, ncol=min(n, 3))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig0_weights_comparison")


def find_oracle_summary_dir(explicit: str | None) -> Path:
    if explicit is not None:
        path = Path(explicit)
        if not path.is_absolute():
            path = REPO_ROOT / path
        if not path.exists():
            raise FileNotFoundError(f"{path} does not exist")
        return path
    candidates = sorted(
        LOCAL_ROOT.glob("**/*_oracle_summary"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(
            f"No *_oracle_summary folder found under {LOCAL_ROOT}. "
            f"Run run_model_local_mga.py with plugins.mga.mode='oracle' first, "
            f"and check it completed without raising."
        )
    return candidates[0]


def load_run(summary_dir: Path) -> tuple[Polytope, pd.DataFrame]:
    poly_files = sorted(summary_dir.glob("polytope_*.npz"))
    if not poly_files:
        raise FileNotFoundError(f"No polytope_*.npz found in {summary_dir}")
    poly = load_polytope(poly_files[0])
    diag_path = summary_dir / "diagnostics.csv"
    diagnostics = pd.read_csv(diag_path) if diag_path.exists() else pd.DataFrame()
    return poly, diagnostics


# ── 1: Convergence trace ─────────────────────────────────────────────────

def fig1_convergence(poly: Polytope, diagnostics: pd.DataFrame) -> None:
    if diagnostics.empty or "max_min_distance" not in diagnostics.columns:
        print("  skipping fig1_convergence: no diagnostics.csv / max_min_distance column")
        return
    iteration = (diagnostics["iteration"] if "iteration" in diagnostics.columns
                 else np.arange(len(diagnostics)))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(iteration, diagnostics["max_min_distance"], marker="o", markersize=3,
             color=_ETH_BLUE, linewidth=1.2)
    ax.axhline(poly.tolerance, color=_ETH_RED, linestyle="--", linewidth=1,
               label=f"tolerance = {poly.tolerance:g}")
    ax.set_yscale("log")
    ax.set_xlabel("ORACLE iteration")
    ax.set_ylabel("max-min distance (normalised L-inf)")
    status = "CONVERGED" if poly.converged else "not converged"
    ax.set_title(f"MGA ORACLE Convergence ({status}, final = {poly.final_max_min_distance:.4g})",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, frameon=False)
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    savefig(fig, "fig1_convergence")


# ── 2: Per-axis near-optimal range (outer approximation) ────────────────

def fig2_variable_ranges(poly: Polytope) -> None:
    approx = approximation(A=poly.A, X=poly.X, b=poly.b, name_list=poly.names, print_lv=0)
    ranges = pd.DataFrame(approx.effective_variable_ranges()).set_index("variable").loc[poly.names]
    bounds_norm = ranges[["min", "max"]].to_numpy().T  # (2, n_explore)
    bounds_phys = poly.to_phys(bounds_norm)
    mins_phys, maxs_phys = bounds_phys[0], bounds_phys[1]

    names = poly.design_names
    n = len(names)
    fig, ax = plt.subplots(figsize=(9, 0.9 * n + 1.5))
    for i, name in enumerate(names):
        lo, hi = mins_phys[i], maxs_phys[i]
        ax.plot([lo, hi], [i, i], color=_ETH_BLUE, linewidth=6, solid_capstyle="butt", alpha=0.85)
        ax.plot(poly.z_star[i], i, marker="D", color=_ETH_RED, markersize=7, zorder=5,
                label="baseline (z*)" if i == 0 else None)
        ax.text(hi, i, f"  {hi:,.2f}", va="center", fontsize=8)
        ax.text(lo, i, f"{lo:,.2f}  ", va="center", ha="right", fontsize=8)

    unit_labels = [f"{name}\n[{unit or 'n/a'}]" for name, unit in zip(names, poly.units[:n])]
    ax.set_yticks(range(n))
    ax.set_yticklabels(unit_labels, fontsize=9)
    ax.set_xlabel("capacity addition (near-optimal range)")
    ax.set_title(f"MGA Near-Optimal Range per Axis (epsilon = {poly.epsilon:g})\n"
                 "outer-polytope projection; diamond = baseline",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig2_variable_ranges")


# ── 3 & 4: Pairwise projections (shared layout helper) ──────────────────

def _pairwise_grid(names: list[str], units: list[str], title: str, name: str,
                    plot_fn) -> None:
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
                ax.set_xlabel(f"{names[j]}\n[{units[j] or 'n/a'}]", fontsize=8)
            else:
                ax.set_xticklabels([])
            if j == 0:
                ax.set_ylabel(f"{names[i]}\n[{units[i] or 'n/a'}]", fontsize=8)
            else:
                ax.set_yticklabels([])
            ax.tick_params(labelsize=7)
            ax.grid(alpha=0.25)
    handles, labels = axes[1 - 1, 0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper right", fontsize=9, frameon=False)
    fig.suptitle(title, fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    savefig(fig, name)


def fig3_pairwise_points(poly: Polytope) -> None:
    n = len(poly.design_names)
    X_phys = poly.to_phys(poly.X)[:, :n]  # poly.X[0] is the baseline z* (normalised)

    def plot_fn(ax, j, i):
        ax.scatter(X_phys[1:, j], X_phys[1:, i], s=14, color=_ETH_BLUE, alpha=0.6,
                   edgecolor="white", linewidth=0.3,
                   label="ORACLE iterate" if (i, j) == (1, 0) else None)
        ax.scatter(X_phys[0, j], X_phys[0, i], marker="D", s=60, color=_ETH_RED, zorder=5,
                   label="baseline (z*)" if (i, j) == (1, 0) else None)

    _pairwise_grid(poly.design_names, poly.units[:n],
                   "MGA ORACLE Explored Design Points (pairwise projections)",
                   "fig3_pairwise_points", plot_fn)


def fig4_polytope_samples(poly: Polytope, n_steps: int = 2000) -> None:
    n = len(poly.design_names)
    try:
        approx = approximation(A=poly.A, X=poly.X, b=poly.b, name_list=poly.names, print_lv=0)
        sampler = PolytopeSamples(approx, use="outer", walk_type="vaidya", print_lv=0)
        samples_norm = sampler.sample(n_steps=n_steps)
    except Exception as exc:  # PolyRound rounding can fail on degenerate/thin polytopes
        print(f"  skipping fig4_polytope_samples: sampling failed ({exc!r})")
        return
    samples_phys = poly.to_phys(samples_norm)[:, :n]
    z_star_norm = poly.X[0:1, :]
    z_star_phys = poly.to_phys(z_star_norm)[0, :n]

    def plot_fn(ax, j, i):
        ax.scatter(samples_phys[:, j], samples_phys[:, i], s=6, color=_ETH_PETROL, alpha=0.35,
                   edgecolor="none", label=f"outer samples (n={len(samples_phys)})" if (i, j) == (1, 0) else None)
        ax.scatter(z_star_phys[j], z_star_phys[i], marker="D", s=60, color=_ETH_RED, zorder=5,
                   label="baseline (z*)" if (i, j) == (1, 0) else None)

    _pairwise_grid(poly.design_names, poly.units[:n],
                   "MGA Outer-Approximation Samples (pairwise projections)",
                   "fig4_polytope_samples", plot_fn)


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    print("Weights-mode run...")
    fig0_weights_comparison()

    explicit = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        summary_dir = find_oracle_summary_dir(explicit)
    except FileNotFoundError as exc:
        print(f"Skipping oracle figures: {exc}")
        print(f"Done. Figures in {FIGURES_DIR.relative_to(REPO_ROOT)}/")
        return

    print(f"Loading oracle run from {summary_dir.relative_to(REPO_ROOT) if summary_dir.is_relative_to(REPO_ROOT) else summary_dir}")
    poly, diagnostics = load_run(summary_dir)

    n_iters = len(diagnostics) if not diagnostics.empty else "unknown"
    print(f"  converged = {poly.converged}, final_max_min_distance = {poly.final_max_min_distance:.4g}, "
          f"tolerance = {poly.tolerance:g}, epsilon = {poly.epsilon:g}, iterations completed = {n_iters}")
    for a in poly.axes:
        print(f"  axis '{a['name']}' ({a['kind']}): members={a['members']}, unit={a['unit']!r}")

    print("Generating oracle figures...")
    fig1_convergence(poly, diagnostics)
    fig2_variable_ranges(poly)
    fig3_pairwise_points(poly)
    fig4_polytope_samples(poly)
    print(f"Done. Figures in {FIGURES_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
