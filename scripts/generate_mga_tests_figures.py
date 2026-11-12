"""Regenerate the figures in data/outputs/figures/mga_tests/.

Runs plot_mga_results (fig1a/1b, one per year), plot_mga_ts_resolution (fig3a/3b/4)
and plot_mga_cum_regional_capex (fig10/12; fig11 only for runs with several regions),
all for the run set in plots/mga_capex_periods_common.py (run 47), and
plot_mga_run_comparison (fig70-73, run 46 vs run 47).

plot_mga_regional_investment_whatif.py (fig20/21) and plot_mga_share_whatif.py
(fig30-33, fig40-43) stay standalone scripts because their LPs are heavier.
They plot run 21 and write to mga_tests/archive/run21/.
plot_mga_diffusion_whatif.py (fig51, fig52) and plot_mga_npc_vs_diffusion.py (fig60)
are standalone too; they also plot run 47.
plot_ts_resolution_benchmark.py (fig5) is not run here: it still plots the old
runs.

Usage:
    python scripts/generate_mga_tests_figures.py
"""

import plot_mga_cum_regional_capex
import plot_mga_results
import plot_mga_run_comparison
import plot_mga_ts_resolution


def main() -> None:
    plot_mga_results.main()
    plot_mga_ts_resolution.main()
    plot_mga_cum_regional_capex.main()
    plot_mga_run_comparison.main()


if __name__ == "__main__":
    main()
