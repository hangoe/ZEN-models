"""Generate the thesis figures into figures/report/ (and figures/presentation/).

Every figure runs in its own process, so only its own runs are loaded (peak memory about
0.7 GB). The thesis figure numbers are in thesis_figures/registry.py.

Usage:
    python make_figures.py                         all figures, report and presentation
    python make_figures.py fig05 figA07            figures whose name starts with these
    python make_figures.py --mode report           one mode only
    python make_figures.py --tables                also write figures/tables/*.csv
    python make_figures.py --list                  list the figures

Requires ZEN-garden and ZEN-garden-plugins (see README.md).
"""

import argparse
import os
import subprocess
import sys

MODES = ("report", "presentation")


def build_one(name: str) -> None:
    """Build one figure in this process (mode from FIGURE_MODE)."""
    from thesis_figures.registry import FIGURES
    from thesis_figures.style import apply_style
    apply_style()
    FIGURES[name].build(name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("figures", nargs="*", help="figure names or prefixes (default: all)")
    parser.add_argument("--mode", choices=(*MODES, "both"), default="both")
    parser.add_argument("--tables", action="store_true", help="also write the MGA run-test tables")
    parser.add_argument("--list", action="store_true", help="list the figures and exit")
    parser.add_argument("--build-one", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.build_one:
        build_one(args.build_one)
        return

    from thesis_figures.registry import FIGURES
    if args.list:
        for name, fig in FIGURES.items():
            print(f"{'Fig. ' + fig.thesis if fig.thesis else 'presentation':14s} {name}")
        return

    names = [n for n in FIGURES if not args.figures or any(n.startswith(p) for p in args.figures)]
    if not names:
        sys.exit(f"no figure matches {args.figures}; see --list")
    modes = MODES if args.mode == "both" else (args.mode,)
    failed = []
    for mode in modes:
        for name in names:
            if FIGURES[name].presentation_only and mode != "presentation":
                continue
            print(f"== {mode}: {name}", flush=True)
            env = {**os.environ, "FIGURE_MODE": mode}
            if subprocess.run([sys.executable, __file__, "--build-one", name], env=env).returncode:
                failed.append(f"{mode}: {name}")
    if args.tables:
        from thesis_figures.mga.run_tests import write_tables
        write_tables()
    if failed:
        sys.exit("failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()
