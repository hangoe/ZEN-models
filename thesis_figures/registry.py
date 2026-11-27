"""All generated figures: output name (thesis figure number + content) -> how to build it.

Main-text figures are numbered continuously (fig02 = Figure 2), appendix figures A1, A2,
... (figA01 = Figure A1). Figure 1 (sector diagram) is drawn by hand (figures/drawio/).
If the thesis is reordered, only the names here change.
"""

from collections.abc import Callable
from dataclasses import dataclass

from .mga import limit_radar, pairwise, run_tests
from .single import (
    capacity_storage,
    cost_breakdown,
    dsm_discharge,
    emissions,
    energy_input,
    flexibility_matrix,
    flexibility_scenarios,
    heat_supply,
    node_map,
)
from .single.scenarios import (
    FULL,
    FULL_20TS,
    LEGACY,
    NO_DSM,
    NO_FLEX,
    NO_FLEX_20TS,
    NO_FLEX_SINGLE_TEMP,
    NO_TES,
    NO_TES_DSM_PESS,
    SINGLE_TEMP,
    load_runs,
)


@dataclass(frozen=True)
class Figure:
    thesis: str                      # figure number in the thesis ("" = presentation only)
    build: Callable[[str], None]     # build(name) draws and saves the figure
    presentation_only: bool = False


def _single(fn, labels: list[str], **kw) -> Callable[[str], None]:
    """Build function of a single-run figure: load `labels`, call fn(*runs, name, **kw)."""
    return lambda name: fn(*load_runs(labels), name, **kw)


TEMPERATURE_MATRIX_RUNS = [NO_FLEX, NO_FLEX_SINGLE_TEMP, FULL, SINGLE_TEMP]

FIGURES: dict[str, Figure] = {
    "fig02_industry_energy_input_by_carrier": Figure(
        "2", _single(energy_input.industry_energy_input, [NO_FLEX])),
    "fig03_cost_breakdown_sector_industry_heating": Figure(
        "3", _single(cost_breakdown.cost_breakdown, [LEGACY, NO_FLEX])),
    "fig04_capacity_and_storage_legacy_vs_no_flex": Figure(
        "4", _single(capacity_storage.capacity_and_storage, [LEGACY, NO_FLEX])),
    "fig05_heat_supply_no_flex": Figure(
        "5", _single(heat_supply.heat_supply, [NO_FLEX])),
    "fig06_flexibility_matrix": Figure(
        "6", _single(flexibility_matrix.temperature_matrix, TEMPERATURE_MATRIX_RUNS)),
    "fig07_mga_limit_radar": Figure(
        "7", limit_radar.main_run_radar),
    "figA01_emissions_by_source_and_carbon_budget": Figure(
        "A1", _single(emissions.emissions_and_budget, [LEGACY, NO_FLEX])),
    "figA02_heat_supply_zen_europe": Figure(
        "A2", _single(heat_supply.heat_supply, [FULL])),
    "figA03_flexibility_scenarios_table": Figure(
        "A3", lambda name: flexibility_scenarios.flexibility_scenarios_table(
            load_runs([NO_FLEX, FULL, NO_TES_DSM_PESS, NO_TES, NO_DSM]), name)),
    "figA04_dsm_discharge_by_product": Figure(
        "A4", _single(dsm_discharge.dsm_discharge_by_product, [FULL, NO_TES_DSM_PESS])),
    "figA05_flexibility_matrix_time_steps": Figure(
        "A5", _single(flexibility_matrix.time_step_matrix, [NO_FLEX, NO_FLEX_20TS, FULL, FULL_20TS])),
    "figA06_mga_limit_radar_ccs_biomass": Figure(
        "A6", lambda name: limit_radar.main_run_radar(name, appendix=True)),
    "figA09_mga_limit_radar_test_runs": Figure(
        "A9", limit_radar.test_runs_radar),
    "figA07_mga_run_tests_convergence": Figure(
        "A7", run_tests.convergence),
    "figA08_mga_run_tests_effort": Figure(
        "A8", run_tests.effort),
    "figA10_mga_limit_radar_cost_slack": Figure(
        "A10", limit_radar.cost_slack_radar),
    "figA11_mga_pairwise_hulls_cost_slack_vs_test_run": Figure(
        "A11", pairwise.pairwise_hulls),
    "presi_flexibility_matrix_one_row": Figure(
        "", _single(flexibility_matrix.temperature_matrix, TEMPERATURE_MATRIX_RUNS, one_row=True),
        presentation_only=True),
    "presi_heat_supply_aggregated": Figure(
        "", _single(heat_supply.heat_supply_aggregated, [NO_FLEX, FULL]), presentation_only=True),
    "presi_zen_europe_node_map": Figure("", node_map.node_map, presentation_only=True),
}
