"""Check how fast the industry heat pumps may grow (diffusion limit + seed).

Two modes:
  * dataset (no solve): reads a ZEN-europe dataset and computes, per sector and
    temperature band, the largest heat pump share the diffusion limit allows in
    the first year, i.e. Σ_nodes capacity_addition_unbounded + market_share_unbounded
    × existing capacity of the peers (same reference carrier), versus the band
    demand. Upper bound: assumes the heat pumps run flat at full load.
  * results: reads a solved run and prints the heat pump share of the industry
    heat per year, and for the first year each heat pump's capacity addition
    next to the rebuilt diffusion limit and the dual of
    constraint_technology_diffusion_limit_total.

Usage:
    python scripts/check_hp_diffusion.py --dataset zen_europe_ind_heat_v1_no_flexibility
    python scripts/check_hp_diffusion.py --results <run folder name in euler_outputs>
Datasets are looked up in data/outputs/zen-europe, results in data/outputs/euler_outputs
(absolute paths work too).
"""

import argparse
from pathlib import Path

import pandas as pd
import yaml

from plots.figure_settings import EULER_ROOT, OUTPUT_DIR, _search_var_dict

DATASET_ROOT = OUTPUT_DIR / "zen-europe"
TARGET_SHARE = 0.10
HP_PREFIX = "heat_pump_industry_"


def _attributes(tech_dir: Path) -> dict:
    return yaml.safe_load(open(tech_dir / "attributes.yaml"))


def _value(attributes: dict, name: str) -> float:
    return float(attributes[name]["default_value"])


def _capacity_existing(tech_dir: Path, attributes: dict, year: int) -> float:
    """Existing capacity (GW, summed over nodes) still alive in `year`."""
    path = tech_dir / "capacity_existing.csv"
    if not path.exists():
        return 0.0
    df = pd.read_csv(path)
    lifetime = _value(attributes, "lifetime")
    return df.loc[df.year_construction + lifetime > year, "capacity_existing"].sum()


def _band_demand(dataset: Path) -> pd.Series:
    """Heat demand (GW) per heat carrier: product demand × heat per product."""
    conversion = dataset / "set_technologies" / "set_conversion_technologies"
    demand = {}
    for tech_dir in conversion.glob("*_production"):
        attributes = _attributes(tech_dir)
        product = attributes["reference_carrier"]["default_value"][0]
        demand_path = dataset / "set_carriers" / product / "demand.csv"
        if not demand_path.exists():
            continue
        product_demand = pd.read_csv(demand_path).demand.sum()
        for factor in attributes["conversion_factor"]:
            for carrier, entry in factor.items():
                if carrier.startswith("heat_industry_"):
                    demand[carrier] = product_demand * float(entry["default_value"])
    return pd.Series(demand)


def check_dataset(dataset: Path) -> None:
    system = yaml.safe_load(open(dataset / "system.yaml"))
    year = system["reference_year"]
    nodes = len(system["set_nodes"])
    energy_system = yaml.safe_load(open(dataset / "energy_system" / "attributes.yaml"))
    market_share = _value(energy_system, "market_share_unbounded")
    conversion = dataset / "set_technologies" / "set_conversion_technologies"
    techs = {t: _attributes(conversion / t) for t in system["set_conversion_technologies"]}
    reference = {t: a["reference_carrier"]["default_value"][0] for t, a in techs.items()}
    existing = {t: _capacity_existing(conversion / t, a, year) for t, a in techs.items()}
    demand = _band_demand(dataset)

    rows = []
    for tech in sorted(t for t in techs if t.startswith(HP_PREFIX)):
        carrier = reference[tech]
        peers = [t for t in techs if reference[t] == carrier and t != tech]
        seed = _value(techs[tech], "capacity_addition_unbounded") * nodes
        rows.append(
            {
                "carrier": carrier,
                "tech": tech,
                "seed": seed,
                "market_share": market_share * sum(existing[t] for t in peers),
            }
        )
    df = pd.DataFrame(rows)
    df["limit"] = df.seed + df.market_share
    band = df.groupby("carrier")[["seed", "market_share", "limit"]].sum()
    band["demand"] = demand.reindex(band.index)
    band["max_hp_share"] = (band.limit / band.demand).clip(upper=1)
    print(f"\n{dataset.name}: first year {year}, {nodes} nodes, "
          f"market_share_unbounded {market_share}")
    print("GW per heat carrier (all heat pumps of the carrier together):")
    print(band.round(3).to_string())
    hp_max = band[["limit", "demand"]].min(axis=1).sum()
    print(f"\nseed total {df.seed.sum():.2f} GW, market-share total "
          f"{df.market_share.sum():.2f} GW, demand total {band.demand.sum():.2f} GW")
    print(f"max heat pump share {year} (upper bound): {hp_max / band.demand.sum():.1%} "
          f"(target <= {TARGET_SHARE:.0%})")


def check_results(path: Path) -> None:
    from zen_garden import Results

    run = _search_var_dict(path, max_depth=3)
    if run is None:
        raise FileNotFoundError(f"No variables.nc found under {path}")
    r = Results(path=str(run))
    years = r.get_years()

    flow = r.get_total("flow_conversion_output")
    flow = flow[flow.index.get_level_values("carrier").str.startswith("heat_industry_")]
    flow = flow.groupby(level=["technology", "carrier"]).sum()
    techs = flow.index.get_level_values("technology")
    # the temperature cascade only passes heat on; final heat = heat pumps + boilers
    final = flow[~techs.str.contains("temp_conversion")]
    is_hp = final.index.get_level_values("technology").str.startswith(HP_PREFIX)
    share = final[is_hp].sum() / final.sum()
    print(f"\n{path.name}")
    print("heat pump share of industry heat:")
    print(share.map("{:.1%}".format).to_string())
    band = final.groupby(level="carrier").sum()
    band_hp = final[is_hp].groupby(level="carrier").sum()
    print("\nheat pump share per heat carrier:")
    print((band_hp / band).reindex(band.index).fillna(0).round(2).to_string())

    # first year: addition vs. rebuilt diffusion limit
    params = {}
    for name in ["capacity_addition", "capacity_previous"]:
        params[name] = (
            r.get_total(name).xs("power", level="capacity_type")
            .groupby(level="technology").sum()
        )
    # the seed is per node and summed over the nodes of the technology
    seed = r.get_total("capacity_addition_unbounded")
    nodes = (r.get_total("capacity_addition").xs("power", level="capacity_type")
             .groupby(level="technology").size())
    dual = r.get_dual("constraint_technology_diffusion_limit_total")
    if dual is not None and "capacity_type" in dual.index.names:
        dual = dual.xs("power", level="capacity_type")
    year0 = params["capacity_addition"].columns[0]
    hps = [t for t in params["capacity_addition"].index if t.startswith(HP_PREFIX)]
    reference = {t: c for t, c in flow.index if t in hps}
    rows = []
    for tech in hps:
        carrier = reference.get(tech)
        # peers: the other producers of the carrier (their reference carrier)
        peers = [t for t, c in flow.index if c == carrier and t != tech]
        market_share = 0.02 * params["capacity_previous"].reindex(peers)[year0].sum()
        rows.append(
            {
                "tech": tech.removeprefix(HP_PREFIX),
                "addition": params["capacity_addition"].loc[tech, year0],
                "seed": seed.get(tech, 0.0) * nodes[tech],
                "market_share": market_share,
                "dual": dual.loc[tech].iloc[0] if dual is not None and tech in dual.index
                else float("nan"),
            }
        )
    df = pd.DataFrame(rows).set_index("tech")
    df["limit"] = df.seed + df.market_share
    print(f"\n{years[0]}: capacity addition vs. diffusion limit (GW, summed over nodes); "
          "dual != 0 means binding.")
    print(df[["addition", "limit", "seed", "market_share", "dual"]].round(3).to_string())


def _resolve(name: str, root: Path) -> Path:
    path = Path(name)
    return path if path.is_absolute() or path.exists() else root / name


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dataset", nargs="*", default=[])
    parser.add_argument("--results", nargs="*", default=[])
    args = parser.parse_args()
    for name in args.dataset:
        check_dataset(_resolve(name, DATASET_ROOT))
    for name in args.results:
        check_results(_resolve(name, EULER_ROOT))


if __name__ == "__main__":
    main()
