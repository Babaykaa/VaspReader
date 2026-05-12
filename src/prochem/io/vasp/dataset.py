"""Helpers for MLIP-style VASP structure datasets."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np

from prochem.core.models import Calculation, Trajectory
from prochem.io.vasp.parser import Parser

DEFAULT_STRUCTURE_FILENAMES = ("CONTCAR", "POSCAR")


def discover_structure_files(
    directory: str | Path,
    *,
    recursive: bool = True,
    filenames: Sequence[str] = DEFAULT_STRUCTURE_FILENAMES,
) -> list[Path]:
    """Discover VASP structure files, preferring earlier names in each folder.

    With the default filenames, one file per folder is returned: CONTCAR when it
    exists, otherwise POSCAR. This is useful for MLIP datasets where each
    subfolder is an independent configuration rather than a restart segment.
    """
    root = Path(directory)
    wanted = {name.upper(): index for index, name in enumerate(filenames)}
    files_by_folder: dict[Path, list[Path]] = {}
    iterator = root.rglob("*") if recursive else root.iterdir()
    for path in iterator:
        if not path.is_file():
            continue
        name = path.name.upper()
        if name in wanted:
            files_by_folder.setdefault(path.parent, []).append(path)

    selected = []
    for folder, files in files_by_folder.items():
        selected.append(sorted(files, key=lambda path: (wanted[path.name.upper()], path.name))[0])
    return sorted(selected, key=lambda path: str(path.relative_to(root)))


def parse_structure_dataset(
    directory: str | Path,
    *,
    recursive: bool = True,
    filenames: Sequence[str] = DEFAULT_STRUCTURE_FILENAMES,
) -> list[Calculation]:
    """Parse independent VASP structures from a directory tree."""
    calculations = []
    for path in discover_structure_files(directory, recursive=recursive, filenames=filenames):
        calculation = Parser(path).parse()
        if calculation.errors.exist:
            raise ValueError(f"Could not parse {path}: {calculation.errors.message}")
        calculations.append(calculation)
    return calculations


def dataset_to_trajectory(
    calculations: Sequence[Calculation],
    *,
    strict_topology: bool = True,
) -> Calculation:
    """Convert independent single-structure calculations into one trajectory.

    No mismatch fallback is used here. In strict mode every configuration must
    have the same atom count and species order.
    """
    prepared = [calculation for calculation in calculations if calculation.trajectory is not None]
    if not prepared:
        raise ValueError("At least one parsed structure is required.")

    first = prepared[0].trajectory.frame(0)
    frames = []
    for index, calculation in enumerate(prepared):
        frame = calculation.trajectory.frame(-1)
        if strict_topology and (
            frame.atom_count != first.atom_count or not np.array_equal(frame.species, first.species)
        ):
            raise ValueError(
                f"Dataset topology mismatch at {calculation.source}: "
                "atom count or species order differs from the first configuration."
            )
        properties = dict(frame.properties)
        properties["source"] = calculation.source
        properties["source_step"] = calculation.trajectory.step_count - 1
        frame = frame.__class__(
            species=frame.species,
            positions=frame.positions,
            atom_ids=first.atom_ids if strict_topology else frame.atom_ids,
            cell=frame.cell,
            direct_positions=frame.direct_positions,
            masses=frame.masses,
            velocities=frame.velocities,
            forces=frame.forces,
            stress=frame.stress,
            time_fs=float(index),
            properties=properties,
        )
        frames.append(frame)

    trajectory = Trajectory(
        frames=frames,
        atom_registry=prepared[0].trajectory.atom_registry if strict_topology else None,
        properties={
            "dataset": True,
            "source_files": tuple(calculation.source for calculation in prepared),
            "strict_topology": strict_topology,
        },
    )
    return Calculation(
        source=Path(prepared[0].source).parent,
        engine=prepared[0].engine,
        trajectory=trajectory,
        properties={
            "dataset": True,
            "source_files": tuple(calculation.source for calculation in prepared),
        },
    )


def parse_structure_dataset_as_trajectory(
    directory: str | Path,
    *,
    recursive: bool = True,
    filenames: Sequence[str] = DEFAULT_STRUCTURE_FILENAMES,
    strict_topology: bool = True,
) -> Calculation:
    """Parse a VASP structure dataset and pack it into one trajectory."""
    calculations = parse_structure_dataset(directory, recursive=recursive, filenames=filenames)
    return dataset_to_trajectory(calculations, strict_topology=strict_topology)

