"""vasprun.xml parser and restart-sequence merger."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from prochem.core.models import Calculation, Cell, Structures
from prochem.core.structures_merge import MergeReport, StructuresMergePolicy, merge_calculations
from prochem.io.vasp.common import (
    TAG_VALUE_RE,
    VASPfileType,
    derive_potential_kinetic_arrays,
    error_calculation,
    numbers_from_line,
)

_I_TAG_RE = re.compile(r'<i[^>]*name="(?P<name>[^"]+)"[^>]*>\s*(?P<value>[^<]+)\s*</i>')


def read_vasprun(source: Path, file_type: VASPfileType = VASPfileType.XML, engine: str = "vasp") -> Calculation:
    """Read a VASP vasprun.xml file."""
    atom_count = 0
    atom_types: list[int] = []
    species: list[str] = []
    pomass_by_type: list[float] = []
    position_frames: list[list[list[float]]] = []
    force_frames: list[list[list[float]]] = []
    potential_energy_frames: list[float | None] = []
    kinetic_energy_frames: list[float | None] = []
    total_energy_frames: list[float | None] = []
    cell_frames: list[list[list[float]]] = []
    initial_cell: list[list[float]] | None = None
    timestep: float | None = None
    in_calculation = False
    current_potential_energy: float | None = None
    current_kinetic_energy: float | None = None
    current_total_energy: float | None = None
    current_has_positions = False
    in_energy = False
    block_potential_energy: float | None = None
    block_fallback_potential_energy: float | None = None
    block_kinetic_energy: float | None = None
    block_total_energy: float | None = None

    with source.open("r", encoding="utf-8", errors="replace") as xml:
        while True:
            line = xml.readline()
            if not line:
                break

            if "<calculation>" in line:
                in_calculation = True
                current_potential_energy = None
                current_kinetic_energy = None
                current_total_energy = None
                current_has_positions = False
                in_energy = False
            elif "</calculation>" in line:
                if current_has_positions:
                    potential_energy_frames.append(current_potential_energy)
                    kinetic_energy_frames.append(current_kinetic_energy)
                    total_energy_frames.append(current_total_energy)
                in_calculation = False
                in_energy = False

            if in_calculation and "<energy" in line:
                in_energy = True
                block_potential_energy = None
                block_fallback_potential_energy = None
                block_kinetic_energy = None
                block_total_energy = None

            if "<atoms>" in line:
                numbers = numbers_from_line(line)
                if numbers:
                    atom_count = int(numbers[0])

            elif 'name="POMASS"' in line:
                pomass_by_type = numbers_from_line(line)

            elif 'name="POTIM"' in line and timestep is None:
                values = numbers_from_line(line)
                if values:
                    timestep = float(values[-1])

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
                current_has_positions = True

            elif '<varray name="forces"' in line and in_calculation:
                force_frames.append(read_vasp_varray(xml, atom_count))

            elif in_calculation and in_energy:
                kind, value = _energy_value_from_vasprun_line(line)
                if value is not None:
                    if kind == "potential":
                        block_potential_energy = value
                    elif kind == "potential_fallback":
                        block_fallback_potential_energy = value
                    elif kind == "kinetic":
                        block_kinetic_energy = value
                    elif kind == "total":
                        block_total_energy = value

            if in_calculation and in_energy and "</energy>" in line:
                potential = block_potential_energy
                if potential is None:
                    potential = block_fallback_potential_energy
                if potential is not None:
                    current_potential_energy = potential
                if block_kinetic_energy is not None:
                    current_kinetic_energy = block_kinetic_energy
                if block_total_energy is not None:
                    current_total_energy = block_total_energy
                in_energy = False

    if not species:
        return error_calculation(source, engine, "No atom information was found in vasprun.xml.")
    if not position_frames:
        return error_calculation(source, engine, "No structure-sequence positions were found in vasprun.xml.")

    cell_vectors = np.asarray(
        cell_frames[0] if cell_frames else initial_cell,
        dtype=np.float64,
    )
    if cell_vectors.shape != (3, 3):
        return error_calculation(source, engine, "No valid cell basis was found in vasprun.xml.")

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
    (
        structure_potential_energies,
        structure_kinetic_energies,
        structure_total_energies,
    ) = derive_potential_kinetic_arrays(
        potential_energy_frames,
        kinetic_energy_frames,
        total_energy_frames,
    )
    masses = masses_from_atom_types(atom_types, pomass_by_type)
    time_fs = (
        np.arange(len(position_frames), dtype=np.float64) * timestep
        if timestep is not None
        else None
    )

    structures = Structures.from_arrays(
        species=np.asarray(species, dtype=str),
        positions=positions,
        direct_positions=direct_positions,
        cell=cells if isinstance(cells, np.ndarray) else Cell(cells),
        time_fs=time_fs,
        timestep=timestep,
        masses=masses,
        forces=forces,
        structure_potential_energies=structure_potential_energies,
        structure_kinetic_energies=structure_kinetic_energies,
        structure_total_energies=structure_total_energies,
        sources=tuple(source for _ in range(len(position_frames))),
        properties={"format": "vasprun.xml"},
    )
    return Calculation(
        source=source,
        engine=engine,
        structures=structures,
        properties={"file_type": file_type.value},
    )


def _energy_value_from_vasprun_line(line: str) -> tuple[str | None, float | None]:
    match = _I_TAG_RE.search(line)
    if match is None:
        return None, None
    try:
        value = float(match.group("value").replace("D", "E").replace("d", "e"))
    except ValueError:
        return None, None

    name = match.group("name").lower()
    if name == "e_fr_energy":
        return "potential", value
    if name in {"e_0_energy", "e_wo_entrp"}:
        return "potential_fallback", value
    if name in {"kinetic", "kinetic_energy", "ekin"}:
        return "kinetic", value
    if "etotal" in name or name in {"total", "total_energy"}:
        return "total", value
    return None, None


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
    policy: StructuresMergePolicy | None = None,
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
    return merge_calculations(calculations, policy or StructuresMergePolicy())


def vasprun_sort_key(path: Path) -> tuple:
    numbers = [int(value) for value in re.findall(r"\d+", path.name)]
    return (0 if numbers else 1, numbers, path.stat().st_mtime, str(path))
