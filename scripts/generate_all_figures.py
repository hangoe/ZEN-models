"""Regenerate the figures used in MT_report_HG (or, with --all, every current figure).

  report  serif font (Computer Modern), data/outputs/figures-report/
  presi   Arial, data/outputs/figures-presi/

Every script runs in its own process, with FIGURE_MODE setting font and output
folder (see plots/figure_settings.py); each one can also be run alone, e.g.
    FIGURE_MODE=presentation python scripts/generate_si_figures.py
The drawio diagrams are not generated here.

One figure per process, so only its own runs are loaded (peak about 0.5 GB).
--all runs the full scripts, which load every run at once: not on a laptop.

Usage:
    python scripts/generate_all_figures.py [report] [presi] [--all]     (default: both)
"""

import os
import subprocess
import sys
from pathlib import Path

FIGURE_MODES = {"report": "report", "presi": "presentation"}
REPORT_JOBS = [["generate_si_figures.py", name] for name in (
    "fig2_industry_energy_input_by_carrier", "fig15a_heat_supply_no_flex", "fig15b_heat_supply_zen_europe",
    "fig2_emissions_by_source_and_carbon_budget", "fig12_capacity_and_storage_legacy_vs_no_flex",
    "fig20_cost_breakdown_sector_industry_heating", "fig5b_dsm_discharge_by_product",
    "fig30a_matrix",  # = fig30_matrix in the report
    "fig31_matrix_tsa", "fig43_flexibility_scenarios_table")] + [
    ["plot_mga_limit_radar.py", "63"], ["plot_mga_limit_radar.py", "64"]]
PRESI_JOBS = [  # presentation only
    ["generate_si_figures.py", "fig101_matrix_one_row"], ["generate_si_figures.py", "fig102_heat_supply_aggregated"],
    ["plot_mga_limit_radar.py", "103"]]
ALL_SCRIPTS = [
    "generate_si_figures.py",
    "plot_country_groups_map.py",
    "generate_mga_tests_figures.py",
    "plot_mga_diffusion_whatif.py",
    "plot_mga_npc_vs_diffusion.py",
    "plot_mga_heat_mandate.py",
    "plot_mga_cost_limit.py",
    "plot_mga_limit_radar.py",
]


def main(targets: list[str], jobs: list[list[str]]) -> None:
    failed = []
    for target in targets:
        env = {**os.environ, "FIGURE_MODE": FIGURE_MODES[target]}
        extra = PRESI_JOBS if target == "presi" and jobs is REPORT_JOBS else []
        for script, *args in jobs + extra:
            print(f"== {target}: {script} {' '.join(args)}", flush=True)
            result = subprocess.run([sys.executable, str(Path(__file__).parent / script), *args], env=env)
            if result.returncode:
                failed.append(f"{target}: {script} {' '.join(args)}")
    if failed:
        sys.exit("failed: " + ", ".join(failed))


if __name__ == "__main__":
    unknown = set(sys.argv[1:]) - {*FIGURE_MODES, "--all"}
    if unknown:
        sys.exit("usage: generate_all_figures.py [report] [presi] [--all]")
    main([a for a in sys.argv[1:] if a != "--all"] or list(FIGURE_MODES),
         [[s] for s in ALL_SCRIPTS] if "--all" in sys.argv else REPORT_JOBS)
