"""Parse one VASP file or directory and print a compact summary.

Run from the repository root, for example:

    python examples/parse_vasp_file.py B:\\Science\\Calculations\\VASP\\Low-k\\Poss_with_Ar\\POSS_Ar_30_grad_20eV\\vasprun.xml
    python examples/parse_vasp_file.py B:\\Science\\Calculations\\VASP\\ALE\\C12F26\\Ar\\C\\30eV
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from prochem.io import parse  # noqa: E402


DEFAULT_SOURCE = (
    r"B:\Science\Calculations\VASP\Low-k\Poss_with_Ar\POSS_Ar_30_grad_20eV\vasprun.xml"
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse a VASP file or directory.")
    parser.add_argument("source", nargs="?", default=DEFAULT_SOURCE)
    args = parser.parse_args()

    calculation = parse(args.source)
    print(f"source: {calculation.source}")
    print(f"engine: {calculation.engine}")
    print(f"error: {calculation.errors.exist}")
    if calculation.errors.exist:
        print(calculation.errors.message)
        return

    print(f"steps: {calculation.step_count}")
    print(f"registry atoms: {calculation.atom_count}")
    print(f"property keys: {sorted(calculation.properties.keys())}")
    if calculation.trajectory is not None:
        trajectory = calculation.trajectory
        print(f"dense positions: {trajectory.positions_array().shape}")
        print(f"presence mask: {trajectory.presence_mask().shape}")
        print(f"first frame atoms: {trajectory.frame(0).atom_count}")
        print(f"last frame atoms: {trajectory.frame(-1).atom_count}")
        print(f"first species: {', '.join(trajectory.species[:8])}")


if __name__ == "__main__":
    main()
