"""Regenerate every figure in data/outputs/figures/mga_tests/.

Runs, in order: plot_mga_results (fig1/2), plot_mga_ts_resolution
(fig3a/3b), plot_mga_cum_regional_capex (fig10/11/12),
plot_ts_resolution_benchmark (fig5).

plot_mga_regional_investment_whatif.py (fig20/21) is not wired in here --
it reuses the same batch4 CAPEX-CUM/share run as plot_mga_cum_regional_
capex.py's fig10/11/12 but stays a standalone script (python
scripts/plot_mga_regional_investment_whatif.py), its own set of what-if LP
solves being heavier than the rest of this orchestrator's figures.

Usage:
    python scripts/generate_mga_tests_figures.py
"""

import plot_mga_cum_regional_capex
import plot_mga_results
import plot_mga_ts_resolution
import plot_ts_resolution_benchmark


def main() -> None:
    plot_mga_results.main()
    plot_mga_ts_resolution.main()
    plot_mga_cum_regional_capex.main()
    plot_ts_resolution_benchmark.main()


if __name__ == "__main__":
    main()
