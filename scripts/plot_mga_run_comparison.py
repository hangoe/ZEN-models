"""Run 56 vs run 57 (COMPARE_RUNS and COMPARE_TAG in plots/mga_capex_periods_common.py).

The two runs explore the same 7 axes from the same baseline and the same VMM (own-axis
min/max) solves, with the same stopping rule (95% CI lower bound of the share of
well-approximated directions >= 0.95, from 4000 directions). They differ in
tolerance_explore, the gap below which a direction counts as well approximated: 0.1 in
run 56, 0.01 in run 57. Per-axis ranges (fig12) are therefore identical, and the figures
look at the interior instead:

  fig70_<tag>_convergence           ci_lower, max gap and mean gap per iteration, as each
                                    run logged them (diagnostics.csv)
  fig71_<tag>_common_gaps           both final polytopes scored on the same directions:
                                    distribution of the support-function gap, the share
                                    within each run's tolerance, and inner/outer volumes
  fig72_<tag>_pairwise_hulls        2D projections of each run's inner hull, all axes
  fig73_<tag>_npc_vs_diffusion      fig60's cheapest cost per diffusion band, both runs

Each run's logged ci_lower counts directions within its own tolerance, on its own random
direction set, so the logged values are not comparable between the runs. fig71 re-scores
both on one fixed set (N_DIRECTIONS scrambled Sobol directions, seed SEED) with
pyoNearOpt's own gap code, at both tolerances. Both runs are drawn in one hue, the older
run as a light tint. Earlier versions: mga_tests/archive/run46_vs_47/ and archive/run45_vs_46/.

Usage (zen-garden-plugins-env, PYTHONPATH=../ZEN-garden-plugins):
    python scripts/plot_mga_run_comparison.py
"""

import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.spatial import ConvexHull, QhullError
from statsmodels.stats.proportion import proportion_confint

from plots.figure_settings import apply_font_mode, eth_tint

apply_font_mode()

from plot_mga_diffusion_whatif import MANDATE_COLOR, SHARE_METRICS, initial_values, mandate_start, style_axes
from plot_mga_npc_vs_diffusion import NAMES, min_cost_curve, plot_curve, style_cost_axis
from plot_mga_results import load_native_ci_history
from plots.mga_capex_periods_common import (
    COMPARE_RUNS, COMPARE_TAG, METRIC_COLOR, METRIC_LABEL, MGA_ROOT, MODEL, NEAR_BLACK,
    display_unit, parse_axis, savefig,
)
from pyoNearOpt.metrics import _DirectionSampler
from pyoNearOpt.polytope_approximation.approximation_class import approximation
from zen_garden_plugins.mga.polytope_io import load_polytope

N_DIRECTIONS = 4000  # common direction set of fig71, as many as the runs used per check
GAP_FLOOR = 1e-4  # fig71 has a log gap axis; smaller gaps (many are 0) are drawn here
VOLUME_CHUNK = 20_000  # Monte Carlo points per A @ z <= b check (A has ~1800 rows in run 47/57)
SEED = 0
ALPHA = 0.05  # 95% CI, as in the runs
N_VOLUME_SAMPLES = 400_000  # Monte Carlo points for the outer volume
GREY = "#6F6F6F"
# fig72 axis order: by metric, then year, cost last.
METRIC_ORDER = {"heating": 0, "ccs": 1, "biomass": 2, "cost": 3}


def tinted(color: str, tint: float) -> str:
    return eth_tint(color, tint) if tint else color


def load_runs() -> dict:
    """{label: {poly, history, tint}} for COMPARE_RUNS."""
    runs = {}
    for label, (suffix, tint) in COMPARE_RUNS.items():
        run_dir = MGA_ROOT / f"{MODEL}_{suffix}"
        summary = run_dir / f"{MODEL}_batch_summary"
        poly = load_polytope(summary / "polytope.npz")
        history = load_native_ci_history(run_dir, poly, "batch")
        diagnostics = pd.read_csv(summary / "diagnostics.csv")
        history["max_gap"] = diagnostics["max_gap"]
        history["mean_gap"] = diagnostics["mean_gap"]
        print(f"  {label}: {poly.X.shape[0]} points, {len(history)} logged iterations, "
              f"target {poly.convergence_threshold:g}, n_samples {poly.run['n_samples']}, "
              f"final_gap {poly.final_gap:.3f}")
        runs[label] = {"poly": poly, "history": history, "tint": tint, "dir": run_dir}
    return runs


def fig70_convergence(runs: dict) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(7.5, 8.4), sharex=True, constrained_layout=True)
    for label, run in runs.items():
        color = tinted(NEAR_BLACK, run["tint"])
        h = run["history"]
        for ax, column in zip(axes, ("ci_lower", "max_gap", "mean_gap")):
            ax.plot(h["n_queries"], h[column], color=color, linewidth=1.8, marker="o", markersize=3.5, label=label)
    targets = {float(run["poly"].convergence_threshold) for run in runs.values()}
    for label, run in runs.items():
        color = tinted(NEAR_BLACK, run["tint"]) if len(targets) > 1 else GREY
        target = run["poly"].convergence_threshold
        axes[0].axhline(target, color=color, linestyle="--", linewidth=1)
        if len(targets) > 1 or not run["tint"]:  # a shared target is labelled once
            axes[0].annotate(f"target {target:g}", (0, target), xycoords=("axes fraction", "data"),
                             xytext=(4, -10 if run["tint"] else 3), textcoords="offset points", fontsize=8,
                             color=color)
        color = tinted(NEAR_BLACK, run["tint"])
        tolerance = float(run["poly"].run["tolerance_explore"])
        for ax in axes[1:]:
            ax.axhline(tolerance, color=color, linestyle=":", linewidth=1)
        axes[1].annotate(f"tolerance_explore {tolerance:g}", (1, tolerance), xycoords=("axes fraction", "data"),
                         xytext=(-4, 3), textcoords="offset points", ha="right", fontsize=8, color=color)
    for ax in axes[1:]:
        ax.set_yscale("log")
    axes[0].set_ylim(-0.03, 1.03)
    axes[0].set_ylabel("ci_lower (directions within\nthe run's own tolerance)")
    axes[1].set_ylabel("max gap (worst sampled direction)")
    axes[2].set_ylabel("mean gap")
    axes[2].set_xlabel("number of model queries")
    for ax in axes:
        ax.grid(alpha=0.3)
    axes[0].legend(fontsize=8, frameon=False, loc="lower right")
    axes[0].set_title("Convergence as logged by each run (own tolerance and direction set; final check not logged)",
                      fontsize=9.5)
    savefig(fig, f"fig70_{COMPARE_TAG}_convergence")


def common_gaps(poly, tolerances) -> dict:
    """Gap of each common direction, share within each tolerance with its CI lower bound,
    and the implied tolerances at CI targets 0.90 and 0.95."""
    approx = approximation(poly.A, poly.X, poly.b, name_list=list(poly.names), print_lv=0)
    sampler = _DirectionSampler(n_samples=N_DIRECTIONS, use_randomized_qmc=True, n_jobs=1, seed_rng=SEED,
                                logger=logging.getLogger("fig71"))
    _, gaps = sampler.sample_separation(approx)
    within = {}
    for tolerance in tolerances:
        close = int((gaps <= tolerance).sum())
        ci_lower, _ = proportion_confint(close, N_DIRECTIONS, alpha=ALPHA, method="jeffreys")
        within[tolerance] = (close / N_DIRECTIONS, ci_lower)
    implied = {target: sampler._implied_threshold_for_tolerance(gaps, N_DIRECTIONS, ALPHA, target)
               for target in (0.90, 0.95)}
    return {"gaps": gaps, "within": within, "implied": implied}


def volumes(poly, rng) -> tuple[float, float]:
    """(inner hull volume, outer volume) in normalised coordinates. The outer one is a
    Monte Carlo estimate over the box spanned by the outer approximation's bounds."""
    inner = ConvexHull(poly.X, qhull_options="QJ").volume  # joggled: the points are nearly degenerate
    lo, hi = poly.X.min(axis=0), poly.X.max(axis=0)
    # The outer polytope can reach beyond the points; widen the box until no sample on its
    # faces is inside (a box with one sample face inside would cut the outer volume).
    pad = 0.0
    while True:
        box_lo, box_hi = lo - pad, hi + pad
        samples = rng.uniform(box_lo, box_hi, size=(N_VOLUME_SAMPLES, poly.X.shape[1]))
        inside = np.concatenate([np.all(chunk @ poly.A.T <= poly.b + 1e-9, axis=1)
                                 for chunk in np.array_split(samples, max(1, N_VOLUME_SAMPLES // VOLUME_CHUNK))])
        near_face = np.any((samples - box_lo < 0.01 * (box_hi - box_lo)) | (box_hi - samples < 0.01 * (box_hi - box_lo)),
                           axis=1)
        if not (inside & near_face).any() or pad > 1.0:
            break
        pad += 0.1
    outer = inside.mean() * np.prod(box_hi - box_lo)
    return inner, outer


def fig71_common_gaps(runs: dict) -> None:
    rng = np.random.default_rng(SEED)
    tolerances = sorted({float(run["poly"].run["tolerance_explore"]) for run in runs.values()}, reverse=True)
    fig, ax = plt.subplots(figsize=(8.2, 5.0), constrained_layout=True)
    lines = []
    for label, run in runs.items():
        color = tinted(NEAR_BLACK, run["tint"])
        result = common_gaps(run["poly"], tolerances)
        inner, outer = volumes(run["poly"], rng)
        gaps = np.sort(result["gaps"])
        ax.step(np.maximum(gaps, GAP_FLOOR), np.arange(1, len(gaps) + 1) / len(gaps), where="post", color=color,
                linewidth=1.8, label=label)
        within = "; ".join(f"{100 * share:.1f}% within {t:g} (CI lower {ci:.3f})"
                           for t, (share, ci) in result["within"].items())
        implied = ", ".join(f"{v:.3f} at {k:.2f}" if v is not None else f"n/a at {k:.2f}"
                            for k, v in result["implied"].items())
        lines.append((color, f"{label}: {within}; max gap {gaps[-1]:.3f}\n"
                             f"      implied tolerance {implied}; inner/outer volume {inner / outer:.2f}"))
        print(f"  {lines[-1][1]}  (inner {inner:.3g}, outer {outer:.3g})")
    for tolerance in tolerances:
        ax.axvline(tolerance, color=GREY, linestyle=":", linewidth=1)
        ax.annotate(f"tolerance {tolerance:g}", (tolerance, 0.02), xytext=(4, 0), textcoords="offset points",
                    fontsize=8, color=GREY)
    for target in (0.90, 0.95):
        ax.axhline(target, color=GREY, linestyle="--", linewidth=0.7, alpha=0.6)
    ax.set_xscale("log")
    ax.set_xlim(GAP_FLOOR * 0.8, None)
    ax.set_ylim(0, 1.01)
    ax.set_xlabel(f"support-function gap $h_{{outer}}(d) - h_{{inner}}(d)$ (normalised units; "
                  f"gaps below {GAP_FLOOR:g} drawn at {GAP_FLOOR:g})")
    ax.set_ylabel("share of directions with gap $\\leq$ x")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, frameon=False, loc="center right")
    for k, (color, text) in enumerate(lines):
        ax.text(0.0, -0.2 - 0.12 * k, text, transform=ax.transAxes, fontsize=7.5, color=color, va="top")
    ax.set_title(f"Both final polytopes scored on the same {N_DIRECTIONS} directions", fontsize=11)
    savefig(fig, f"fig71_{COMPARE_TAG}_common_gaps")


def _axis_order(poly) -> list[int]:
    def key(i):
        info = parse_axis(poly.names[i])
        return METRIC_ORDER[info.metric], info.year or ""
    return sorted(range(poly.n_axes), key=key)


def _label(poly, i: int) -> str:
    info = parse_axis(poly.names[i])
    _, unit = display_unit(poly.units[i])
    name = METRIC_LABEL[info.metric] + (f" {info.year}" if info.year else "")
    return f"{name}\n[{unit}]"


def _hull_outline(points: np.ndarray):
    """Closed outline of the 2D convex hull and its area; a segment if degenerate."""
    try:
        hull = ConvexHull(points)
    except QhullError:
        order = np.lexsort(points.T[::-1])
        return points[[order[0], order[-1]]], 0.0
    vertices = points[np.append(hull.vertices, hull.vertices[0])]
    return vertices, hull.volume


def fig72_pairwise_hulls(runs: dict) -> None:
    first = next(iter(runs.values()))["poly"]
    order = _axis_order(first)
    factors = np.array([display_unit(first.units[i])[0] for i in range(first.n_axes)])
    data = {label: np.array([run["poly"].to_phys(x) for x in run["poly"].X]) * factors for label, run in runs.items()}
    n = len(order)
    fig, axes = plt.subplots(n - 1, n - 1, figsize=(1.9 * (n - 1), 1.9 * (n - 1)), squeeze=False)
    labels = list(runs)
    for row in range(1, n):
        for col in range(n - 1):
            ax = axes[row - 1, col]
            if col >= row:
                ax.axis("off")
                continue
            i, j = order[col], order[row]
            areas = {}
            for label in labels:
                color = tinted(NEAR_BLACK, runs[label]["tint"])
                points = data[label][:, [i, j]]
                outline, areas[label] = _hull_outline(points)
                light = runs[label]["tint"] > 0
                if light:
                    ax.fill(outline[:, 0], outline[:, 1], color=color, alpha=0.35, linewidth=0, zorder=1)
                ax.plot(outline[:, 0], outline[:, 1], color=color, linewidth=1.6 if light else 0.9, zorder=3)
                ax.scatter(points[:, 0], points[:, 1], s=2, color=color, linewidths=0, zorder=2, rasterized=True)
            if areas[labels[0]] > 0:
                ax.text(0.97, 0.04, f"$\\times${areas[labels[1]] / areas[labels[0]]:.2f}", transform=ax.transAxes,
                        ha="right", va="bottom", fontsize=7, color=NEAR_BLACK,
                        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 0.5})
            ax.grid(alpha=0.25, linewidth=0.5)
            ax.tick_params(labelsize=6.5)
            if row == n - 1:
                ax.set_xlabel(_label(first, i), fontsize=7.5, color=METRIC_COLOR[parse_axis(first.names[i]).metric])
            else:
                ax.set_xticklabels([])
            if col == 0:
                ax.set_ylabel(_label(first, j), fontsize=7.5, color=METRIC_COLOR[parse_axis(first.names[j]).metric])
            else:
                ax.set_yticklabels([])
    handles = [Patch(facecolor=tinted(NEAR_BLACK, runs[labels[0]]["tint"]), alpha=0.5,
                     edgecolor=tinted(NEAR_BLACK, runs[labels[0]]["tint"]), label=f"{labels[0]}, inner hull"),
               Line2D([0], [0], color=tinted(NEAR_BLACK, runs[labels[1]]["tint"]), linewidth=0.9,
                      label=f"{labels[1]}, inner hull"),
               Line2D([0], [0], color="none", label=f"$\\times$ = 2D hull area, {labels[1].split(' (')[0]} / {labels[0].split(' (')[0]}")]
    fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.97, 0.93), fontsize=10, frameon=False)
    fig.suptitle(f"{labels[0].split(' (')[0].capitalize()} vs {labels[1].split(' (')[0]}: "
                 "solved near-optimal designs, projected on every axis pair",
                 fontsize=13, fontweight="bold", color=NEAR_BLACK)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    savefig(fig, f"fig72_{COMPARE_TAG}_pairwise_hulls")


def fig73_npc_vs_diffusion(runs: dict) -> None:
    labels = list(runs)
    last = runs[labels[-1]]
    # Mandate starts come from the dataset and the baseline, identical for both runs.
    starts = mandate_start(last["poly"], initial_values(last["poly"]))
    fig, axes = plt.subplots(1, len(SHARE_METRICS), figsize=(6.2 * len(SHARE_METRICS), 4.8), constrained_layout=True)
    for ax, metric in zip(axes, SHARE_METRICS):
        for label, run in runs.items():
            poly = run["poly"]
            axis_idx = {name: i for i, name in enumerate(poly.names)}
            print(f"  {label}")
            inner, _ = min_cost_curve(poly, axis_idx, metric, starts[metric])
            plot_curve(ax, poly, inner, tinted(MANDATE_COLOR[metric], run["tint"]), label)
        style_cost_axis(ax, last["poly"])
        style_axes(ax, NAMES[metric], "Net present cost (min. possible)")
        ax.legend(frameon=False, fontsize=8, loc="upper left", bbox_to_anchor=(0.0, 0.9))
    fig.suptitle(f"Minimum possible net present cost per diffusion rate band: {labels[0].split(' (')[0]} vs "
                 f"{labels[1].split(' (')[0]}",
                 fontsize=12, fontweight="bold", color=NEAR_BLACK)
    savefig(fig, f"fig73_{COMPARE_TAG}_npc_vs_diffusion")


def main() -> None:
    print("Loading runs...")
    runs = load_runs()
    fig70_convergence(runs)
    fig71_common_gaps(runs)
    fig72_pairwise_hulls(runs)
    fig73_npc_vs_diffusion(runs)


if __name__ == "__main__":
    main()
