"""Merge restarted VASP vasprun XML files and print the merge report.

Run from the repository root, for example:

    python examples/merge_vasprun_directory.py B:\\Science\\Calculations\\VASP\\ALE\\C12F26\\Ar\\C\\30eV
    python examples/merge_vasprun_directory.py B:\\Science\\Calculations\\VASP\\MoS2\\N2\\Mo\\MoS2_N2_30eV_parallel_Mo
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from prochem.core import TrajectoryMergePolicy  # noqa: E402
from prochem.io.vasp import discover_vasprun_files, parse_vasprun_sequence  # noqa: E402


DEFAULT_DIRECTORY = r"B:\Science\Calculations\VASP\ALE\C12F26\Ar\C\30eV"


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge vasprun XML restart segments.")
    parser.add_argument("directory", nargs="?", default=DEFAULT_DIRECTORY)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--drop-topology-frame", action="store_true")
    args = parser.parse_args()

    policy = TrajectoryMergePolicy(
        strict=args.strict,
        keep_topology_change_frame=not args.drop_topology_frame,
    )
    files = discover_vasprun_files(args.directory, recursive=args.recursive)
    print("files:")
    for path in files:
        print(f"  {path}")

    calculation, report = parse_vasprun_sequence(
        args.directory,
        recursive=args.recursive,
        policy=policy,
    )
    trajectory = calculation.trajectory
    positions = trajectory.positions_array()
    mask = trajectory.presence_mask()

    print("\nmerge events:")
    for event in report.events:
        print(
            f"  {event.status:16s} next={event.next_source.name} "
            f"drop={event.dropped_next_frames} deleted={event.deleted_atom_ids} "
            f"max_delta={event.max_delta}"
        )

    print("\nmerged trajectory:")
    print(f"  frames: {calculation.step_count}")
    print(f"  registry atoms: {calculation.atom_count}")
    print(f"  positions shape: {positions.shape}")
    print(f"  missing atom slots: {int((~mask).sum())}")
    print(f"  NaN coordinates: {int(np.isnan(positions).sum())}")
    print(f"  deleted atom ids: {report.deleted_atom_ids}")


if __name__ == "__main__":
    main()
