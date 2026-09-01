"""Regenerate every figure in data/outputs/figures/mga_investment/.

Runs, in order: plot_carrier_flows, plot_carrier_groups (built on
plot_carrier_flows's data), plot_country_groups_map, plot_mga_investment_map.

Usage:
    python scripts/generate_mga_investment_figures.py
"""

import plot_carrier_flows
import plot_carrier_groups
import plot_country_groups_map
import plot_mga_investment_map


def main() -> None:
    plot_carrier_flows.main()
    plot_carrier_groups.main()
    plot_country_groups_map.main()
    plot_mga_investment_map.main()


if __name__ == "__main__":
    main()
