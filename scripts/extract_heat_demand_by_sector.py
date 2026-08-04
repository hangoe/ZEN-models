"""Extract exogenous industry heat demand by sector and temperature band from
ZEN-creator (input-data logic, not model results).

Feeds fig4_heat_demand_by_sector in generate_si_figures.py. Must be run with
the `zen-creator-env` conda environment (has openpyxl/xlrd for the JRC-IDEES/
Rehfeldt2017/AIDRES2023/FAOSTAT source files ZEN-creator reads) rather than
`zen-garden-env` (has matplotlib/pandas for plotting, but not openpyxl/xlrd) —
the two envs are disjoint, so this step and the plotting step in
generate_si_figures.py run in separate environments, bridged by the JSON file
this script writes.

Two pieces per sector, both from ProcessParametrizationDataset (the exact
class that builds each production tech's real conversion_factor/input_carrier,
i.e. this is not a re-derivation, it calls the same code the model build uses):

  - "heat": low-temperature heat-carrier demand (GW), 3 bands (0-100, 100-150,
    150-200°C), via self._heat_cfs[sector][level] — the same conversion
    factors written into e.g. glass_production's conversion_factor for
    heat_industry_0_100/100_150/150_200.
  - "fuel_by_carrier": high-temperature (>200°C) demand (GW), met by DIRECT
    FUEL COMBUSTION rather than any heat_industry_* carrier at all — a
    different supply pathway, not a 4th heat band — split by the sector's
    actual fuel mix (self._fuel_shares[sector], e.g. natural_gas/hard_coal/
    biomass) via SectorParams.cf_fuel. Included (per user decision) to show
    each sector's full process-energy intensity for scale/context, NOT as
    another heat-demand band.

Both are demand_volume[sector].sum() (tonproduct/hour, SUMMED ACROSS ALL
MODEL_NODES — this is an EU27(-MT,-CY)+CH+NO+UK AGGREGATE, not a per-country
figure) times a GW/(tonproduct/hour) conversion factor.

demand_volume[sector] is NOT industry_demand_df/_ceramic_demand_series (an
earlier, physical-output-based demand definition) — it is whichever function
each sector's actual Carrier Element class calls for `_set_demand`, i.e. the
literal demand.csv the model solves against:
  glass, paper: JrcIdeesIndustryDataset.get_demand_as_capacity_existing
                (JRC-IDEES installed capacity ÷ OPERATING_HOURS=8000; paper
                also gets the JRC-BAT CH/NO/UK override — both baked in by
                calling the real method rather than reimplementing it)
  ceramic:      JrcIdeesIndustryDataset.get_ceramic_demand_as_capacity_existing
                (JRC-IDEES thermal FEC ÷ Rehfeldt specific energy ÷ 8000)
  food:         FaostatFoodDataset.get_food_demand_as_capacity_existing
                (FAOSTAT production-weighted Rehfeldt activity_Mt ÷ 8000)
(zen_creator/elements/carriers/industry_carriers.py, Glass/Ceramic/Paper/Food
._set_demand). An earlier version of this script used industry_demand_df /
_ceramic_demand_series instead (the same functions get_heat_capacity_split()
in process_parametrization.py happens to use for its own, different purpose
of a cross-sector % split) — those gave demand sums ~40% too high for glass
and paper (physical output, not installed-capacity-equivalent demand).
Verified against a materialized dataset (ZEN-creator/outputs/
Crystal_Ball_ind_heat_v7_3/set_carriers/{glass,ceramic,paper,food}/demand.csv)
— this script's demand_volume sums match those on-disk demand.csv column
sums exactly (glass 6369.58, ceramic 7779.23, paper 19835.12, food 26227.5
tonproduct/hour), and glass_production's heat_cfs/fuel-carrier conversion
factors match that dataset's set_technologies/.../glass_production/
attributes.json to 9 significant figures.

heat_cfs/fuel_shares ultimately trace back to Rehfeldt2017.csv's per-sub-
process temperature distributions (temp_lt100/100_200/200_500/500_1000/
gt1000) and fuels_GJ_t, activity_Mt-weighted across each sector's sub-
processes (glass: container/flat/fibre; ceramic: tiles/technical/houseware;
paper: paper/recovered_fibres/chemical_pulp; food: dairy/meat_processing/
brewing/bread_bakery/sugar) via compute_sector_params() — not re-derived here,
called directly.

Usage:
    /path/to/zen-creator-env/bin/python scripts/extract_heat_demand_by_sector.py
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
ZEN_CREATOR_ROOT = REPO_ROOT.parent / "ZEN-creator"
sys.path.insert(0, str(ZEN_CREATOR_ROOT))

from zen_creator.datasets.datasets.faostat_food import FaostatFoodDataset  # noqa: E402
from zen_creator.datasets.datasets.jrc_idees_industry import JrcIdeesIndustryDataset  # noqa: E402
from zen_creator.datasets.datasets.process_parametrization import (  # noqa: E402
    FEC_YEAR,
    HEAT_TEMP_LEVELS,
    ProcessParametrizationDataset,
)

OUTPUT_PATH = REPO_ROOT / "data" / "outputs" / "figures" / "SI_results" / "heat_demand_by_sector_input.json"


def main() -> None:
    ds = ProcessParametrizationDataset()
    jrc = JrcIdeesIndustryDataset()
    demand_volumes = {
        "glass": jrc.get_demand_as_capacity_existing(None, "glass", FEC_YEAR).df.sum(),
        "ceramic": jrc.get_ceramic_demand_as_capacity_existing(None, FEC_YEAR).df.sum(),
        "paper": jrc.get_demand_as_capacity_existing(None, "paper", FEC_YEAR).df.sum(),
        "food": FaostatFoodDataset().get_food_demand_as_capacity_existing(None, FEC_YEAR).df.sum(),
    }

    result = {}
    for sector, dv in demand_volumes.items():
        heat = {level: dv * ds._heat_cfs[sector][level] for level in HEAT_TEMP_LEVELS}
        fuel_total = dv * ds._sector_params[sector].cf_fuel
        fuel_by_carrier = {carrier: fuel_total * share for carrier, share in ds._fuel_shares[sector].items()}
        result[sector] = {
            "demand_ton_hr": dv,
            "heat": heat,
            "fuel_by_carrier": fuel_by_carrier,
        }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2))
    print(f"wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    for sector, d in result.items():
        heat_str = ", ".join(f"{lvl}={gw:.3f} GW" for lvl, gw in d["heat"].items())
        fuel_str = ", ".join(f"{c}={gw:.3f} GW" for c, gw in d["fuel_by_carrier"].items())
        print(f"  {sector}: demand={d['demand_ton_hr']:.1f} ton/hr | heat: {heat_str} | fuel: {fuel_str}")


if __name__ == "__main__":
    main()
