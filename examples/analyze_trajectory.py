"""Analyze a parsed trajectory using backend-independent analysis functions.

Run from the repository root, for example:

    python examples/analyze_trajectory.py B:\\Science\\Calculations\\VASP\\ALE\\C12F26\\Ar\\C\\30eV
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis import (  # noqa: E402
    add_distance_columns,
    add_kinetic_energy_columns,
    add_velocity_columns,
    coordinate_dataframe,
    export_dataframe,
)
from parsers import parse  # noqa: E402


DEFAULT_SOURCE = r"B:\Science\Calculations\VASP\ALE\C12F26\Ar\C\30eV"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run core trajectory analysis.")
    parser.add_argument("source", nargs="?", default=DEFAULT_SOURCE)
    parser.add_argument("--export", default=None, help="Optional csv/xlsx/html output path.")
    args = parser.parse_args()

    calculation = parse(args.source)
    if calculation.errors.exist:
        raise SystemExit(calculation.errors.message)
    trajectory = calculation.trajectory
    atom_ids = [record.atom_id for record in trajectory.atom_registry[: min(3, trajectory.atom_count)]]

    dataframe = coordinate_dataframe(trajectory, atom_ids=atom_ids)
    dataframe = add_velocity_columns(dataframe, trajectory, atom_ids)

    try:
        dataframe = add_kinetic_energy_columns(dataframe, trajectory, atom_ids)
    except ValueError:
        pass

    if len(atom_ids) >= 2:
        dataframe = add_distance_columns(dataframe, trajectory, [(atom_ids[0], atom_ids[1])])

    print(dataframe.head())
    print(f"rows={len(dataframe)} columns={len(dataframe.columns)}")
    print(f"missing atom slots={int((~trajectory.presence_mask()).sum())}")

    if args.export:
        output = export_dataframe(dataframe, args.export)
        print(f"exported: {output}")


if __name__ == "__main__":
    main()
