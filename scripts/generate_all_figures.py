"""Regenerate every figure in data/outputs/figures/ in one run.

Calls each folder's own orchestrator in turn; each one remains independently
runnable (python scripts/generate_si_figures.py,
python scripts/generate_mga_investment_figures.py,
python scripts/generate_mga_tests_figures.py) for a single-folder rebuild.

Usage:
    python scripts/generate_all_figures.py
"""

import generate_mga_investment_figures
import generate_mga_tests_figures
import generate_si_figures


def main() -> None:
    generate_si_figures.main()
    generate_mga_investment_figures.main()
    generate_mga_tests_figures.main()


if __name__ == "__main__":
    main()
