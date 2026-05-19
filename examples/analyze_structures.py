"""Analyze parsed structures using the pandas-based analysis model.

Run from the repository root, for example:

    python examples/analyze_structures.py B:\\Science\\Calculations\\VASP\\ALE\\C12F26\\Ar\\C\\30eV
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from prochem.analysis import (  # noqa: E402
    AnalysisTable,
    Selection,
    export_dataframe,
)
from prochem.io import parse  # noqa: E402


DEFAULT_SOURCE = r"B:\Science\Calculations\VASP\ALE\C12F26\Ar\C\30eV"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run core structures analysis.")
    parser.add_argument("source", nargs="?", default=DEFAULT_SOURCE)
    parser.add_argument("--export", default=None, help="Optional csv/xlsx/html output path.")
    args = parser.parse_args()

    calculation = parse(args.source)
    if calculation.errors.exist:
        raise SystemExit(calculation.errors.message)
    structures = calculation.structures
    if structures is None:
        raise SystemExit("Calculation does not contain structures.")
    atom_ids = list(structures.atom_ids[: min(3, structures.atom_count)])

    selection = Selection("selected", atom_ids)
    analysis = AnalysisTable(structures, selection)
    analysis.add_coordinates("selected")
    analysis.add_atom_velocities("selected")
    analysis.add_atom_kinetic_energies("selected")

    if len(atom_ids) >= 2:
        analysis.add_distances("selected", pairs=[(atom_ids[0], atom_ids[1])])

    dataframe = analysis.dataframe()
    print(dataframe.head())
    print(f"rows={len(dataframe)} columns={len(dataframe.columns)}")
    print(f"missing atom slots={int((~structures.presence_mask()).sum())}")

    if args.export:
        output = export_dataframe(dataframe, args.export)
        print(f"exported: {output}")


if __name__ == "__main__":
    main()
