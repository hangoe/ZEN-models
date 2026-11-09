"""Block capacity additions in the reference year for the technologies behind the
MGA share axes, so the shares start from the dataset's existing capacity.

Without a diffusion limit, ZEN-garden builds freely in the first model year (e.g.
15.8 GW of electrode boilers in 2022, 35% electrified industrial heat from 0.4%
existing). A year-specific capacity_limit of 0 in the reference year fixes that:
where existing capacity >= capacity_limit, ZEN-garden sets capacity_addition to 0
(technology_capacity_limit_constraint.py). Existing capacity can still run, and
later years keep their previous limit.

Technologies are the numerators of the axes config's ratio groups plus its
limit-utilisation groups. Per technology, capacity_limit.csv becomes node x year:
  - year column present (industry heat pumps): reference year set to 0;
  - node column only (carbon_storage, geological limit): broadcast to all years;
  - no file (electrode boilers, BEV): the attributes.yaml default for all years.
The dataset is edited in place (git history is the undo). Running it twice gives
the same result.

Usage:
    python scripts/freeze_first_year_additions.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).parent.parent
DATASET = REPO_ROOT / "data" / "outputs" / "zen-europe-old" / "zen_europe_ind_heat_v1_no_flexibility_nodiffusion_export0"
AXES_CONFIG = REPO_ROOT / "data" / "config_euler" / "config_mga_axes_total_output_1reg_co2storage.yaml"
LAST_YEAR = 2050
NOTE_HEADER = "capacity_limit (first-year freeze)"


def frozen_technologies() -> list[str]:
    axes = yaml.safe_load(AXES_CONFIG.read_text())
    technologies = []
    for group in axes["node_output_ratio"]["ratio_groups"]:
        for spec in group.values():
            technologies += spec["numerator"]
    for group in axes["node_limit_utilisation"]["technology_groups"]:
        for members in group.values():
            technologies += members
    return list(dict.fromkeys(technologies))


def technology_folder(technology: str) -> Path:
    return next(path for path in (DATASET / "set_technologies").rglob(technology) if path.is_dir())


def frozen_limit(folder: Path, nodes: list[str], years: list[int], reference_year: int) -> tuple[pd.DataFrame, float]:
    """(new capacity_limit table, old reference-year limit summed over nodes)."""
    attributes = yaml.safe_load((folder / "attributes.yaml").read_text())
    default = float(attributes["capacity_limit"]["default_value"])
    path = folder / "capacity_limit.csv"
    if not path.exists():
        table = pd.DataFrame([(n, y, default) for n in nodes for y in years],
                             columns=["node", "year", "capacity_limit"])
    else:
        table = pd.read_csv(path)
        if "year" not in table.columns:
            table = table.merge(pd.DataFrame({"year": years}), how="cross")[["node", "year", "capacity_limit"]]
    first = table["year"] == reference_year
    old = float(table.loc[first, "capacity_limit"].sum())
    table.loc[first, "capacity_limit"] = 0.0
    return table, old


def add_note(folder: Path, reference_year: int) -> None:
    sources = folder / "sources.md"
    text = sources.read_text() if sources.exists() else ""
    if NOTE_HEADER in text:
        return
    note = (f"\n{NOTE_HEADER}\n{'-' * len(NOTE_HEADER)}\n\n"
            f"Set to 0 in {reference_year} by ZEN-models scripts/freeze_first_year_additions.py: no capacity "
            "additions in the first model year, so the share starts from existing capacity. Other years keep "
            "the previous limit.\n")
    sources.write_text(text.rstrip("\n") + "\n" + note)


def main() -> None:
    system = yaml.safe_load((DATASET / "system.yaml").read_text())
    reference_year = int(system["reference_year"])
    nodes = [str(node) for node in system["set_nodes"]]
    years = list(range(reference_year, LAST_YEAR + 1))
    for technology in frozen_technologies():
        folder = technology_folder(technology)
        table, old = frozen_limit(folder, nodes, years, reference_year)
        existing = folder / "capacity_existing.csv"
        existing_total = pd.read_csv(existing)["capacity_existing"].sum() if existing.exists() else 0.0
        table.to_csv(folder / "capacity_limit.csv", index=False)
        add_note(folder, reference_year)
        old_text = "inf" if np.isinf(old) else f"{old:.4g}"
        print(f"{technology:50s} existing {existing_total:10.4g}  {reference_year} limit {old_text:>10s} -> 0")


if __name__ == "__main__":
    main()
