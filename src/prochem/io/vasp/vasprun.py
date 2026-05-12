"""vasprun.xml parser and restart-sequence merger."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from prochem.core.models import Calculation, Cell, CalculationError, Trajectory
from prochem.core.trajectory import MergeReport, TrajectoryMergePolicy, merge_calculations
from prochem.io.vasp.common import TAG_VALUE_RE, VASPfileType, numbers_from_line


def read_vasprun(source: Path, file_type: VASPfileType = VASPfileType.XML, engine: str = "vasp") -> Calculation:
    """Read a VASP vasprun.xml file."""
    atom_count = 0
    atom_types: list[int] = []
    species: list[str] = []
    pomass_by_type: list[float] = []
    position_frames: list[list[list[float]]] = []
    force_frames: list[list[list[float]]] = []
    cell_frames: list[list[list[float]]] = []
    initial_cell: list[list[float]] | None = None
    timestep_fs: float | None = None
    in_calculation = False

    with source.open("r", encoding="utf-8", errors="replace") as xml:
        while True:
            line = xml.readline()
            if not line:
                break

            if "<calculation>" in line:
                in_calculation = True
            elif "</calculation>" in line:
                in_calculation = False

            if "<atoms>" in line:
                numbers = numbers_from_line(line)
                if numbers:
                    atom_count = int(numbers[0])

            elif 'name="POMASS"' in line:
                pomass_by_type = numbers_from_line(line)

            elif 'name="POTIM"' in line and timestep_fs is None:
                values = numbers_from_line(line)
                if values:
                    timestep_fs = float(values[-1])

            elif '<field type="int">atomtype</field>' in line:
                species, atom_types = read_atominfo_rows(xml, atom_count)

            elif '<varray name="basis"' in line:
                basis = read_vasp_varray(xml, 3)
                if in_calculation:
                    cell_frames.append(basis)
                elif initial_cell is None:
                    initial_cell = basis

            elif '<varray name="positions"' in line and in_calculation:
                position_frames.append(read_vasp_varray(xml, atom_count))

            elif '<varray name="forces"' in line and in_calculation:
                force_frames.append(read_vasp_varray(xml, atom_count))

    if not species:
        return _error_calculation(source, engine, "No atom information was found in vasprun.xml.")
    if not position_frames:
        return _error_calculation(source, engine, "No trajectory positions were found in vasprun.xml.")

    cell_vectors = np.asarray(
        cell_frames[0] if cell_frames else initial_cell,
        dtype=np.float64,
    )
    if cell_vectors.shape != (3, 3):
        return _error_calculation(source, engine, "No valid cell basis was found in vasprun.xml.")

    direct_positions = np.asarray(position_frames, dtype=np.float64)
    cells = (
        np.asarray(cell_frames, dtype=np.float64)
        if len(cell_frames) == len(position_frames)
        else cell_vectors
    )
    positions = (
        np.einsum("sai,sij->saj", direct_positions, cells)
        if isinstance(cells, np.ndarray) and cells.ndim == 3
        else direct_positions @ cell_vectors
    )
    forces = np.asarray(force_frames, dtype=np.float64) if force_frames else None
    masses = masses_from_atom_types(atom_types, pomass_by_type)
    time_fs = (
        np.arange(len(position_frames), dtype=np.float64) * timestep_fs
        if timestep_fs is not None
        else None
    )

    trajectory = Trajectory.from_arrays(
        species=np.asarray(species, dtype=str),
        positions=positions,
        direct_positions=direct_positions,
        cell=cells if isinstance(cells, np.ndarray) else Cell(cells),
        time_fs=time_fs,
        timestep_fs=timestep_fs,
        masses=masses,
        forces=forces,
        properties={
            "format": "vasprun.xml",
            "cell_frames": cells if isinstance(cells, np.ndarray) and cells.ndim == 3 else None,
        },
    )
    return Calculation(
        source=source,
        engine=engine,
        trajectory=trajectory,
        properties={"file_type": file_type.value},
    )


def read_atominfo_rows(xml, atom_count: int) -> tuple[list[str], list[int]]:
    species: list[str] = []
    atom_types: list[int] = []
    while len(species) < atom_count:
        line = xml.readline()
        if not line:
            break
        values = TAG_VALUE_RE.findall(line)
        if not values:
            continue
        species.append(values[0].strip())
        try:
            atom_types.append(int(values[-1]))
        except ValueError:
            atom_types.append(0)
    return species, atom_types


def read_vasp_varray(xml, rows: int) -> list[list[float]]:
    array: list[list[float]] = []
    while len(array) < rows:
        line = xml.readline()
        if not line or "</varray>" in line:
            break
        values = numbers_from_line(line)
        if len(values) >= 3:
            array.append(values[:3])
    return array


def masses_from_atom_types(atom_types: list[int], pomass_by_type: list[float]) -> np.ndarray | None:
    if not atom_types or not pomass_by_type:
        return None
    masses = []
    for atom_type in atom_types:
        index = atom_type - 1
        masses.append(pomass_by_type[index] if 0 <= index < len(pomass_by_type) else np.nan)
    return np.asarray(masses, dtype=np.float64)


def discover_vasprun_files(directory: str | Path, recursive: bool = False) -> list[Path]:
    """Return vasprun XML files sorted for restart merging."""
    root = Path(directory)
    iterator = root.rglob("vasprun*.xml") if recursive else root.glob("vasprun*.xml")
    return sorted((path for path in iterator if path.is_file()), key=vasprun_sort_key)


def parse_vasprun_sequence(
    directory: str | Path,
    *,
    recursive: bool = False,
    policy: TrajectoryMergePolicy | None = None,
) -> tuple[Calculation, MergeReport]:
    """Parse and merge all vasprun XML files in a directory."""
    from prochem.io.vasp.parser import Parser

    files = discover_vasprun_files(directory, recursive=recursive)
    if not files:
        raise ValueError(f"No vasprun XML files found in {directory}.")
    calculations = [Parser(path).parse() for path in files]
    errors = [calculation for calculation in calculations if calculation.errors.exist]
    if errors:
        first = errors[0]
        raise ValueError(f"Could not parse {first.source}: {first.errors.message}")
    return merge_calculations(calculations, policy or TrajectoryMergePolicy())


def vasprun_sort_key(path: Path) -> tuple:
    numbers = [int(value) for value in re.findall(r"\d+", path.name)]
    return (0 if numbers else 1, numbers, path.stat().st_mtime, str(path))


def _error_calculation(source: Path, engine: str, message: str) -> Calculation:
    return Calculation(
        source=source,
        engine=engine,
        errors=CalculationError(exist=True, message=message),
    )

