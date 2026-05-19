"""Helpers for MLIP-style VASP structure datasets."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from prochem.core.models import Calculation, Structure, StructureDataset
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


def parse_structure_calculations(
    directory: str | Path,
    *,
    recursive: bool = True,
    filenames: Sequence[str] = DEFAULT_STRUCTURE_FILENAMES,
) -> list[Calculation]:
    """Parse independent VASP structures as calculations from a directory tree."""
    calculations: list[Calculation] = []
    for path in discover_structure_files(directory, recursive=recursive, filenames=filenames):
        calculation = Parser(path).parse()
        if calculation.errors.exist:
            raise ValueError(f"Could not parse {path}: {calculation.errors.message}")
        calculations.append(calculation)
    return calculations


def parse_structure_dataset(
    directory: str | Path,
    *,
    recursive: bool = True,
    filenames: Sequence[str] = DEFAULT_STRUCTURE_FILENAMES,
) -> StructureDataset:
    """Parse independent VASP structures from a directory tree."""
    return calculations_to_dataset(
        parse_structure_calculations(directory, recursive=recursive, filenames=filenames)
    )


def calculations_to_dataset(
    calculations: Sequence[Calculation],
) -> StructureDataset:
    """Convert parsed single-structure calculations into a StructureDataset."""
    prepared = [calculation for calculation in calculations if calculation.structures is not None]
    if not prepared:
        raise ValueError("At least one parsed structure is required.")

    structures: list[Structure] = []
    sources = []
    for calculation in prepared:
        frame = calculation.structures.frame(-1)
        properties = dict(frame.properties)
        properties["source"] = calculation.source
        properties["source_step"] = calculation.structures.step_count - 1
        structures.append(
            Structure(
                species=frame.species,
                positions=frame.positions,
                atom_ids=frame.atom_ids,
                cell=frame.cell,
                direct_positions=frame.direct_positions,
                masses=frame.masses,
                atom_potential_energies=frame.atom_potential_energies_array(),
                atom_kinetic_energies=frame.atom_kinetic_energies_array(),
                atom_total_energies=frame.atom_total_energies_array(),
                velocities=frame.velocities,
                forces=frame.forces,
                stress=frame.stress,
                potential_energy=frame.potential_energy,
                kinetic_energy=frame.kinetic_energy,
                total_energy=frame.total_energy,
                time_fs=None,
                properties=properties,
            )
        )
        sources.append(calculation.source)

    return StructureDataset(
        structures=structures,
        sources=sources,
        properties={"source_files": tuple(sources), "engine": prepared[0].engine},
    )


def dataset_to_calculation(dataset: StructureDataset, *, source: str | Path, engine: str = "vasp") -> Calculation:
    """Wrap a StructureDataset in a Calculation object."""
    return Calculation(
        source=source,
        engine=engine,
        dataset=dataset,
        properties={
            "dataset": True,
            "source_files": dataset.source_files,
        },
    )


def parse_structure_dataset_as_structures(
    directory: str | Path,
    *,
    recursive: bool = True,
    filenames: Sequence[str] = DEFAULT_STRUCTURE_FILENAMES,
    strict_topology: bool = True,
) -> Calculation:
    """Parse a VASP structure dataset and explicitly pack it into Structures."""
    dataset = parse_structure_dataset(directory, recursive=recursive, filenames=filenames)
    structures = dataset.to_structures(strict_topology=strict_topology)
    return Calculation(
        source=directory,
        engine="vasp",
        structures=structures,
        dataset=dataset,
        properties={
            "dataset": True,
            "source_files": dataset.source_files,
            "strict_topology": strict_topology,
        },
    )
