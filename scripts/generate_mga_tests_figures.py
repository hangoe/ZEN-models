"""Regenerate every figure in data/outputs/figures/mga_tests/.

Runs, in order: plot_mga_results (fig1/2/3a/3b), plot_mga_regional_investment
(fig7/8), plot_mga_cum_regional_capex (fig10/11).

Usage:
    python scripts/generate_mga_tests_figures.py
"""

import plot_mga_cum_regional_capex
import plot_mga_regional_investment
import plot_mga_results


def main() -> None:
    plot_mga_results.main()
    plot_mga_regional_investment.main()
    plot_mga_cum_regional_capex.main()


if __name__ == "__main__":
    main()
