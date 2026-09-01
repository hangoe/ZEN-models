"""Extract European industry emissions by NACE-ish subsector from JRC-IDEES-2023
(input-data logic, not model results).

Feeds fig8_industry_sector_emissions_context in generate_si_figures.py. Must be
run with the `zen-creator-env` conda environment (has openpyxl for the
JRC-IDEES workbooks) rather than `zen-garden-env` (has matplotlib/pandas for
plotting, but not openpyxl) -- same env split as
extract_heat_demand_by_sector.py, bridged by the JSON file this script writes.

Source: input_data/JRC-IDEES-2023/EU27/JRC-IDEES-2023_EmissionBalance_EU27.xlsx
(zen-creator repo), sheet FC_IND_*_E per subsector -- these are ENERGY-RELATED
(fuel combustion) CO2 emissions only, following the energy-balance/IPCC 1.A
methodology JRC-IDEES itself uses. They do NOT include IPCC 2.x process
emissions (e.g. cement calcination, steel ore reduction, glass/ceramic
carbonate decomposition) -- fig8's caption must say so, since e.g. steel and
non-metallic minerals both have a substantial process-emissions component not
counted here (contrast sector_emissions_2022.csv, which folds UNFCCC
process-emission CRF categories on top of combustion for the sectors Crystal
Ball actually models -- see fig9_model_scope_coverage).

The EU27 workbook's 13 top-level FC_IND_* subsector sheets follow JRC-IDEES's
own industry breakdown (its "index" sheet); each sheet's row 1 ("Total") sums
every fuel row for that subsector. Three subsectors are further broken out
into second-level sheets purely to LABEL which slice is already inside Crystal
Ball's existing (Mannhardt) scope vs. genuinely new (industry-heat extension):
  - FC_IND_NMM_E (Non-metallic minerals) -> CM (cement, old), GL (glass, new),
    CR (ceramics, new)
  - FC_IND_PPP_E (Paper, pulp & printing) -> PA (paper, new); PU (pulp) and PR
    (printing) are adjacent NACE activities Crystal Ball does not model at all.
  - FC_IND_CPC_E (Chemical & petrochemical) is entirely "old" (Mannhardt's
    "chemicals"), no further split needed.
FC_IND_IS_E (Iron & steel) is entirely "old" ("steel"). FC_IND_FBT_E (Food,
beverages & tobacco) is entirely "new" ("food"). The remaining 8 subsectors
(non-ferrous metals, textile & leather, machinery, transport equipment, wood,
mining & quarrying, construction, non-specified) are entirely outside Crystal
Ball's scope.

Usage:
    conda run -n zen-creator-env python scripts/extract_industry_sector_emissions.py
"""

import json
from pathlib import Path

import openpyxl

REPO_ROOT = Path(__file__).parent.parent
ZEN_CREATOR_ROOT = REPO_ROOT.parent / "ZEN-creator"
WORKBOOK = (ZEN_CREATOR_ROOT / "input_data" / "JRC-IDEES-2023" / "EU27" /
            "JRC-IDEES-2023_EmissionBalance_EU27.xlsx")
OUT_JSON = REPO_ROOT / "data" / "outputs" / "figures" / "SI_results" / "industry_sector_emissions_input.json"

YEAR = 2022  # matches sector_emissions_2022.csv's reference year (fig9)

# (sheet, display label, crystal_ball_scope: "old" | "new" | None)
SUBSECTORS = [
    ("FC_IND_IS_E", "Iron & steel", "old"),
    ("FC_IND_NFM_E", "Non-ferrous metals", None),
    ("FC_IND_CPC_E", "Chemical & petrochemical", "old"),
    ("FC_IND_NMM_E", "Non-metallic minerals", "mixed"),  # cement (old) + glass/ceramic (new)
    ("FC_IND_PPP_E", "Paper, pulp & printing", "mixed"),  # paper (new) + pulp/printing (not modeled)
    ("FC_IND_FBT_E", "Food, beverages & tobacco", "new"),
    ("FC_IND_TE_E", "Textiles & leather", None),
    ("FC_IND_MAC_E", "Machinery", None),
    ("FC_IND_TL_E", "Transport equipment", None),
    ("FC_IND_WP_E", "Wood & wood products", None),
    ("FC_IND_MQ_E", "Mining & quarrying", None),
    ("FC_IND_CON_E", "Construction", None),
    ("FC_IND_NSP_E", "Non-specified industry", None),
]

# Second-level sheets used only to annotate the "mixed" subsectors above with
# how much of that bar is old-scope vs. new-scope vs. unmodeled, not plotted
# as their own bars.
SUBSPLITS = {
    "FC_IND_NMM_E": [("FC_IND_NMM_CM_E", "Cement", "old"),
                      ("FC_IND_NMM_GL_E", "Glass", "new"),
                      ("FC_IND_NMM_CR_E", "Ceramics", "new")],
    "FC_IND_PPP_E": [("FC_IND_PPP_PA_E", "Paper", "new"),
                      ("FC_IND_PPP_PU_E", "Pulp", None),
                      ("FC_IND_PPP_PR_E", "Printing", None)],
}


def total_for_year(ws, year: int) -> float:
    header = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
    years = header[2:]
    idx = years.index(year)
    row = next(r for i, r in enumerate(ws.iter_rows(values_only=True)) if i == 1)
    return float(row[2 + idx])


def main() -> None:
    wb = openpyxl.load_workbook(WORKBOOK, data_only=True, read_only=True)
    sectors = []
    for sheet, label, scope in SUBSECTORS:
        total = total_for_year(wb[sheet], YEAR)
        entry = {"sheet": sheet, "label": label, "scope": scope, "emissions_kt_co2": total}
        if sheet in SUBSPLITS:
            entry["subsplit"] = [
                {"sheet": sub_sheet, "label": sub_label, "scope": sub_scope,
                 "emissions_kt_co2": total_for_year(wb[sub_sheet], YEAR)}
                for sub_sheet, sub_label, sub_scope in SUBSPLITS[sheet]
            ]
        sectors.append(entry)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({
        "year": YEAR,
        "source": "JRC-IDEES-2023, EU27, EmissionBalance workbook (energy-related/combustion CO2 only)",
        "sectors": sectors,
    }, indent=2))
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
