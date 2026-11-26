"""Near-optimal run tests: what drives convergence and run time (figures-*/mga-run-tests).

Runs (short run_id -> Euler jobs + settings) are in euler/mga_runs.csv; the
effect groups in plots/mga_run_tests_registry.py. V*/Z* are calibration runs,
T* thesis runs (only used where they give the only clean pair). Runs not on
disk yet are skipped, and a pair is only drawn when both of its runs exist.

  fig4_convergence_by_effect  one panel per effect (tolerance, dimensions, cost
      slack, batch size and seed, time series resolution): CI lower bound of
      well-explored directions (solid) and implied tolerance (dashed, right log
      axis) vs. number of evaluations. The implied tolerance is the smallest
      tolerance_explore the sampled directions would already meet, so one run
      also shows what a looser tolerance would cost.
  fig7_effect_overview  one row per effect: evaluations until stop, median solve
      time per batch round, elapsed job time, peak memory, CPU efficiency (sacct;
      hatched time bar = solve-round time only, a lower bound, where no
      slurm_usage.json exists).
  mga_run_tests_results.csv (figures-report only)  results per run_id.
  single_model_runs_resources.csv (figures-report only)  Euler time/memory of the
      single model runs (2020, 16 years 2 apart, 1/3/10/20 ts), from
      slurm_usage_plain_solves/ (restored from git, commit 54fa3d47^).

slurm_usage.json files are written by import_slurm_usage.py from a sacct dump.
"Solve-round" time is diagnostics.csv's wall_time_seconds: only the parallel LP
rounds, not sampling/BBO in between, so it understates job time.

Usage:
    python scripts/plot_mga_run_tests.py
    FIGURE_MODE=presentation python scripts/plot_mga_run_tests.py
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt

from plots.figure_settings import (
    FIGURES_ROOT, REPORT_FIGURES_ROOT, REPORT_RC, REPORT_WIDTH, SCENARIO_PALETTE, apply_font_mode,
)

apply_font_mode()

import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from zen_garden_plugins.mga.polytope_io import load_polytope

from plots.mga_run_tests_registry import EFFECTS, PAIRED_EFFECTS, RUN_COLOR, RUNS

REPO_ROOT = Path(__file__).parent.parent
MGA_ROOT = REPO_ROOT / "data" / "outputs" / "euler_outputs_mga"
FIGURES_DIR = FIGURES_ROOT / "mga-run-tests"
DATA_DIR = REPORT_FIGURES_ROOT / "mga-run-tests"
PLAIN_SOLVES_DIR = DATA_DIR / "slurm_usage_plain_solves"

GREY = SCENARIO_PALETTE[6]
# fig4 legend position per panel (loc, anchor in axes coordinates) where "center right" covers lines.
LEGEND_LOC = {"dimensions": ("lower right", (1, 0)), "time_resolution": ("lower right", (1, 0.27))}


def savefig(fig: plt.Figure, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / f"{name}.svg", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"  saved {(FIGURES_DIR / f'{name}.svg').relative_to(REPO_ROOT)}")


def mem_kb(text: str) -> float:
    return float(text[:-1]) * {"K": 1, "M": 1024, "G": 1024 ** 2, "T": 1024 ** 3}[text[-1].upper()]


def usage_metrics(usage: dict) -> dict:
    return {
        "elapsed_hours": usage["elapsed_seconds"] / 3600,
        "max_rss_gib": usage["max_rss_kb"] / 1024 ** 2,
        "mem_efficiency_pct": 100 * usage["max_rss_kb"] / mem_kb(usage["req_mem"]),
        "cpu_efficiency_pct": 100 * usage["total_cpu_seconds"] / (usage["elapsed_seconds"] * usage["alloc_cpus"]),
    }


# ── Loading ───────────────────────────────────────────────────────────────

def load_run(run_id: str) -> dict | None:
    """Polytope, per-iteration history and sacct usage of one run."""
    run = RUNS[run_id]
    run_dir = MGA_ROOT / run["folder"] if run["folder"] else None
    summaries = sorted(run_dir.glob("*_batch_summary")) if run_dir and run_dir.exists() else []
    poly_files = sorted(summaries[0].glob("polytope*.npz")) if summaries else []
    if not poly_files:
        print(f"  {run_id}: not on disk ({run['status']}), skipping")
        return None
    poly = load_polytope(poly_files[0])
    diagnostics = pd.read_csv(summaries[0] / "diagnostics.csv")
    batch_size = int(poly.run["batch_size"])
    n_initial = sum(1 for origin in poly.point_origin if origin != "iterate")
    implied = diagnostics.get("implied_threshold_for_tolerance", pd.Series(np.nan, index=diagnostics.index))
    history = pd.DataFrame({
        "n_queries": n_initial + diagnostics["iteration"].astype(int) * batch_size,
        "ci_lower": diagnostics["ci_lower"].astype(float),
        "round_seconds": diagnostics["wall_time_seconds"].astype(float),
        "implied": implied.astype(float),
    })
    usage_file = run_dir / "slurm_usage.json"
    return {"poly": poly, "history": history,
            "usage": json.loads(usage_file.read_text()) if usage_file.exists() else None}


def present_members(tag: str, members: list[tuple[str, str]], loaded: dict) -> list[tuple[str, str]]:
    """Members on disk; for paired effects only complete pairs."""
    if tag not in PAIRED_EFFECTS:
        return [(k, t) for k, t in members if k in loaded]
    pairs = [members[i:i + 2] for i in range(0, len(members), 2)]
    return [m for pair in pairs if all(k in loaded for k, _ in pair) for m in pair]


# ── fig4: convergence, one panel per effect ───────────────────────────────

def fig4_convergence(loaded: dict) -> None:
    n = len(EFFECTS)
    n_rows = (n + 2) // 2  # last slot holds the line-style legend
    fig, axes = plt.subplots(n_rows, 2, figsize=(REPORT_WIDTH, 2.25 * n_rows))
    axes = axes.ravel()
    thresholds, tolerances = set(), set()
    for idx, (tag, title, members) in enumerate(EFFECTS):
        ax = axes[idx]
        ax_r = ax.twinx()
        ax_r.spines["right"].set_visible(True)
        present = present_members(tag, members, loaded)
        ax.set_title(f"({chr(97 + idx)}) {title}", loc="left")
        if len(present) < 2:
            missing = [k for k, _ in members if k not in loaded]
            ax.text(0.5, 0.5, f"{', '.join(missing)} not available yet", transform=ax.transAxes,
                    ha="center", va="center", color=GREY)
            ax.set_xticks([])
        for run_id, text in present:
            data = loaded[run_id]
            h = data["history"]
            ax.plot(h["n_queries"], h["ci_lower"], color=RUN_COLOR[run_id], lw=1.2, label=f"{run_id}: {text}")
            if h["implied"].notna().any():
                ax_r.plot(h["n_queries"], h["implied"], color=RUN_COLOR[run_id], lw=1.0, ls="--")
            thresholds.add(float(data["poly"].convergence_threshold))
            tolerances.add(float(data["poly"].run["tolerance_explore"]))
            ax.axhline(float(data["poly"].convergence_threshold), color=GREY, ls="--", lw=0.6)
            ax_r.axhline(float(data["poly"].run["tolerance_explore"]), color=GREY, ls=":", lw=0.6)
        ax.set_ylim(-0.03, 1.03)
        ax_r.set_yscale("log")
        ax_r.set_ylim(0.005, 2)
        ax.grid(alpha=0.3, lw=0.5)
        ax.set_xlabel("number of evaluations", fontsize=8)
        ax.set_ylabel("well-explored directions" if idx % 2 == 0 else "", fontsize=8)
        ax_r.set_ylabel("implied tolerance" if idx % 2 == 1 else "", fontsize=8)
        if present:
            loc, anchor = LEGEND_LOC.get(tag, ("center right", (1, 0.5)))
            ax.legend(loc=loc, bbox_to_anchor=anchor, fontsize=6.5, handlelength=1.2, borderaxespad=0.3)

    legend_ax = axes[n]
    legend_ax.axis("off")
    legend_ax.legend(handles=[
        plt.Line2D([0], [0], color="black", lw=1.2, label="95% CI lower bound of well-\nexplored directions (left axis)"),
        plt.Line2D([0], [0], color="black", lw=1.0, ls="--", label="implied tolerance (right axis)"),
        plt.Line2D([0], [0], color=GREY, lw=0.6, ls="--", label="convergence target"),
        plt.Line2D([0], [0], color=GREY, lw=0.6, ls=":", label="tolerance_explore of the run"),
    ], loc="center", fontsize=7.5)
    for ax in axes[n + 1:]:
        ax.axis("off")
    fig.tight_layout(h_pad=0.8, w_pad=0.6)
    savefig(fig, "fig4_convergence_by_effect")


# ── fig7: effect overview ─────────────────────────────────────────────────

def run_metrics(data: dict) -> dict:
    h, usage = data["history"], data["usage"]
    m = {"evaluations": len(data["poly"].X), "round_seconds": float(h["round_seconds"].median()),
         "hours": h["round_seconds"].sum() / 3600, "hours_from_sacct": False,
         "max_rss_gib": np.nan, "cpu_efficiency_pct": np.nan}
    if usage:
        u = usage_metrics(usage)
        m.update(hours=u["elapsed_hours"], hours_from_sacct=True,
                 max_rss_gib=u["max_rss_gib"], cpu_efficiency_pct=u["cpu_efficiency_pct"])
    return m


def fig7_overview(loaded: dict) -> None:
    groups = [(title, present) for tag, title, members in EFFECTS
              if len(present := present_members(tag, members, loaded)) >= 2]
    heights = [len(present) for _, present in groups]
    fig, axes = plt.subplots(len(groups), 5, figsize=(REPORT_WIDTH, 0.32 * sum(heights) + 1.7),
                             gridspec_kw={"height_ratios": heights}, sharex="col", squeeze=False)
    columns = [("evaluations", "evaluations\nuntil stop", "{:,.0f}", True),
               ("round_seconds", "solve time per\nbatch round [s]", "{:,.0f}", True),
               ("hours", "elapsed job\ntime [h]", "{:,.1f}", True),
               ("max_rss_gib", "peak memory\n[GiB]", "{:,.0f}", False),
               ("cpu_efficiency_pct", "CPU\nefficiency [%]", "{:.0f}", False)]
    any_lower_bound = False
    for row, (title, present) in enumerate(groups):
        for col, (metric, x_label, fmt, log_x) in enumerate(columns):
            ax = axes[row, col]
            for i, (run_id, _) in enumerate(present):
                m = run_metrics(loaded[run_id])
                value = m[metric]
                if np.isnan(value):
                    ax.text(0.02, i, "n/a", va="center", fontsize=6, color=GREY,
                            transform=ax.get_yaxis_transform())
                    continue
                lower_bound = metric == "hours" and not m["hours_from_sacct"]
                any_lower_bound |= lower_bound
                ax.barh(i, value, color=RUN_COLOR[run_id], height=0.7,
                        hatch="////" if lower_bound else None,
                        edgecolor="black" if RUNS[run_id]["thesis"] else "none", linewidth=0.6)
                ax.text(value, i, " " + fmt.format(value), va="center", fontsize=6)
            if log_x:
                ax.set_xscale("log")
            ax.set_yticks(np.arange(len(present)))
            ax.set_yticklabels([f"{r}: {t}" for r, t in present] if col == 0 else [], fontsize=6.5)
            ax.set_ylim(len(present) - 0.5, -0.5)
            ax.tick_params(axis="x", labelsize=6.5)
            ax.grid(alpha=0.3, axis="x", lw=0.5)
            if col == 0:
                ax.set_title(f"({chr(97 + row)}) {title}", loc="left", fontsize=8.5)
            if row == len(groups) - 1:
                ax.set_xlabel(x_label, fontsize=7.5)
    for col, (*_, log_x) in enumerate(columns):
        lo, hi = axes[0, col].get_xlim()
        if log_x:
            axes[0, col].set_xlim(lo, hi * 6)
        else:
            axes[0, col].set_xlim(0, 125 if columns[col][0] == "cpu_efficiency_pct" else hi * 1.35)
    fig.tight_layout(rect=(0, 0.04, 1, 1), h_pad=0.6, w_pad=0.2)
    handles = [Patch(facecolor="white", edgecolor="black", linewidth=0.6, label="thesis run (T)")]
    if any_lower_bound:
        handles.append(Patch(facecolor="white", edgecolor=GREY, hatch="////",
                             label="no sacct: solve-round time only (lower bound)"))
    fig.legend(handles=handles, loc="lower center", ncol=2, fontsize=7)
    savefig(fig, "fig7_effect_overview")


# ── Tables ────────────────────────────────────────────────────────────────

def write_results_table(loaded: dict) -> None:
    """Results per run_id; settings stay in euler/mga_runs.csv."""
    rows = []
    for run_id, data in loaded.items():
        poly, h, usage = data["poly"], data["history"], data["usage"]
        row = {"run_id": run_id, "iterations": poly.run.get("iterations_done"), "evaluations": len(poly.X),
               "final_ci_lower": round(float(h["ci_lower"].iloc[-1]), 3),
               "median_round_seconds": round(float(h["round_seconds"].median()), 1),
               "solve_round_hours": round(h["round_seconds"].sum() / 3600, 2)}
        if usage:
            u = usage_metrics(usage)
            row.update({
                "elapsed_hours": round(u["elapsed_hours"], 2), "cpus": usage["alloc_cpus"],
                "req_mem": usage["req_mem"], "max_rss_gib": round(u["max_rss_gib"], 1),
                "mem_efficiency_pct": round(u["mem_efficiency_pct"], 1),
                "cpu_efficiency_pct": round(u["cpu_efficiency_pct"], 1),
                "failed_attempts": len(usage.get("attempts", [])),
            })
        rows.append(row)
    path = DATA_DIR / "mga_run_tests_results.csv"
    pd.DataFrame(rows).convert_dtypes().to_csv(path, index=False)
    print(f"  saved {path.relative_to(REPO_ROOT)}")


def write_single_model_table() -> None:
    """Euler resources of the single model runs (one cost-optimal solve each)."""
    rows = []
    for usage_file in sorted(PLAIN_SOLVES_DIR.glob("*/slurm_usage*.json")):
        usage = json.loads(usage_file.read_text())
        ts = int(usage_file.parent.name.rsplit("_", 1)[1].removesuffix("ts"))
        u = usage_metrics(usage)
        rows.append({"ts_per_year": ts, "job_id": usage["job_id"], "cpus": usage["alloc_cpus"],
                     "req_mem": usage["req_mem"], "elapsed_minutes": round(usage["elapsed_seconds"] / 60, 1),
                     "max_rss_gib": round(u["max_rss_gib"], 1),
                     "mem_efficiency_pct": round(u["mem_efficiency_pct"], 1),
                     "cpu_efficiency_pct": round(u["cpu_efficiency_pct"], 1)})
    table = pd.DataFrame(rows).sort_values(["ts_per_year", "cpus"], ascending=[True, False])
    path = DATA_DIR / "single_model_runs_resources.csv"
    table.to_csv(path, index=False)
    print(f"  saved {path.relative_to(REPO_ROOT)}")


def main() -> None:
    print("Loading runs...")
    loaded = {run_id: data for run_id in RUNS if (data := load_run(run_id)) is not None}
    with plt.rc_context(REPORT_RC):
        fig4_convergence(loaded)
        fig7_overview(loaded)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    write_results_table(loaded)
    write_single_model_table()


if __name__ == "__main__":
    main()
