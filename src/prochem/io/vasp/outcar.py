"""OUTCAR parser."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from prochem.core.models import Calculation, Structures
from prochem.io.vasp.common import (
    VASPfileType,
    derive_potential_kinetic_arrays,
    error_calculation,
    numbers_from_line,
    species_from_symbols_counts,
)

_NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][-+]?\d+)?"
_TOTEN_RE = re.compile(rf"free\s+energy\s+TOTEN\s*=\s*({_NUMBER})", re.IGNORECASE)
_ENERGY_WITHOUT_ENTROPY_RE = re.compile(
    rf"energy\s+without\s+entropy\s*=\s*({_NUMBER})",
    re.IGNORECASE,
)
_KINETIC_RE = re.compile(rf"kinetic\s+energy\s+EKIN\s*=\s*({_NUMBER})", re.IGNORECASE)
_TOTAL_RE = re.compile(rf"total\s+energy\s+ETOTAL\s*=\s*({_NUMBER})", re.IGNORECASE)


def read_outcar(source: Path, file_type: VASPfileType = VASPfileType.OUTCAR, engine: str = "vasp") -> Calculation:
    """Read OUTCAR structure-sequence positions, forces and lattice vectors."""
    counts = []
    symbols = []
    timestep = None
    current_cell = None
    cells = []
    positions = []
    forces = []
    potential_energies: list[float | None] = []
    kinetic_energies: list[float | None] = []
    total_energies: list[float | None] = []
    ionic_potential_energies: list[float | None] = []
    ionic_kinetic_energies: list[float | None] = []
    ionic_total_energies: list[float | None] = []
    current_ionic_potential: float | None = None
    current_ionic_kinetic: float | None = None
    open_frame_index: int | None = None

    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if "POTIM" in line and timestep is None:
            values = numbers_from_line(line)
            if values:
                timestep = values[0]
        elif "VRHFIN" in line:
            symbol = line.split("=", 1)[-1].split(":", 1)[0].strip()
            if symbol:
                symbols.append(symbol)
        elif "ions per type" in line:
            counts = [int(value) for value in numbers_from_line(line)]
        elif "direct lattice vectors" in line:
            basis = []
            for offset in range(1, 4):
                if index + offset >= len(lines):
                    break
                values = numbers_from_line(lines[index + offset])
                if len(values) >= 3:
                    basis.append(values[:3])
            if len(basis) == 3:
                current_cell = np.asarray(basis, dtype=np.float64)
            index += 3
        elif "POSITION" in line and "TOTAL-FORCE" in line:
            frame_positions = []
            frame_forces = []
            index += 2
            while index < len(lines):
                values = numbers_from_line(lines[index])
                if len(values) < 6:
                    break
                frame_positions.append(values[:3])
                frame_forces.append(values[3:6])
                index += 1
            if frame_positions:
                positions.append(frame_positions)
                forces.append(frame_forces)
                if current_cell is not None:
                    cells.append(current_cell)
                potential_energies.append(None)
                kinetic_energies.append(None)
                total_energies.append(None)
                open_frame_index = len(positions) - 1
            continue

        potential, kinetic, total = _energy_values_from_outcar_line(line)
        if potential is not None:
            current_ionic_potential = potential
            if open_frame_index is not None and potential_energies[open_frame_index] is None:
                potential_energies[open_frame_index] = potential
        if kinetic is not None:
            current_ionic_kinetic = kinetic
            if open_frame_index is not None and kinetic_energies[open_frame_index] is None:
                kinetic_energies[open_frame_index] = kinetic
        if total is not None:
            ionic_potential_energies.append(current_ionic_potential)
            ionic_kinetic_energies.append(current_ionic_kinetic)
            ionic_total_energies.append(total)
            if open_frame_index is not None and total_energies[open_frame_index] is None:
                total_energies[open_frame_index] = total
                open_frame_index = None
            current_ionic_potential = None
            current_ionic_kinetic = None
        index += 1

    if not positions:
        return error_calculation(source, engine, "No POSITION/TOTAL-FORCE blocks were found in OUTCAR.")
    atom_count = len(positions[0])
    if not counts:
        counts = [atom_count]
    if not symbols:
        symbols = [f"X{index + 1}" for index in range(len(counts))]
    species = species_from_symbols_counts(symbols, counts)
    if species.shape[0] != atom_count:
        species = np.asarray([f"X{index + 1}" for index in range(atom_count)], dtype=str)
    if not cells:
        return error_calculation(source, engine, "No lattice vectors were found in OUTCAR.")

    positions_array = np.asarray(positions, dtype=np.float64)
    forces_array = np.asarray(forces, dtype=np.float64)
    cells_array = np.asarray(cells, dtype=np.float64)
    (
        structure_potential_energies,
        structure_kinetic_energies,
        structure_total_energies,
    ) = derive_potential_kinetic_arrays(
        potential_energies,
        kinetic_energies,
        total_energies,
    )
    structures = Structures.from_arrays(
        species=species,
        positions=positions_array,
        cell=cells_array if len(cells_array) == len(positions_array) else cells_array[0],
        forces=forces_array,
        structure_potential_energies=structure_potential_energies,
        structure_kinetic_energies=structure_kinetic_energies,
        structure_total_energies=structure_total_energies,
        timestep=timestep,
        time_fs=np.arange(len(positions_array), dtype=np.float64) * timestep
        if timestep is not None
        else None,
        sources=tuple(source for _ in range(len(positions_array))),
        properties={
            "format": "OUTCAR",
            "ionic_potential_energies": _optional_energy_array(ionic_potential_energies),
            "ionic_kinetic_energies": _optional_energy_array(ionic_kinetic_energies),
            "ionic_total_energies": _optional_energy_array(ionic_total_energies),
        },
    )
    return Calculation(
        source=source,
        engine=engine,
        structures=structures,
        properties={
            "file_type": file_type.value,
            "symbols": symbols,
            "counts": counts,
            "ionic_step_count": len(ionic_total_energies),
        },
    )


def _energy_values_from_outcar_line(line: str) -> tuple[float | None, float | None, float | None]:
    potential = _match_float(_TOTEN_RE, line)
    if potential is None:
        potential = _match_float(_ENERGY_WITHOUT_ENTROPY_RE, line)
    kinetic = _match_float(_KINETIC_RE, line)
    total = _match_float(_TOTAL_RE, line)
    return potential, kinetic, total


def _match_float(pattern: re.Pattern[str], line: str) -> float | None:
    match = pattern.search(line)
    if match is None:
        return None
    return float(match.group(1).replace("D", "E").replace("d", "e"))


def _optional_energy_array(values: list[float | None]) -> np.ndarray | None:
    if not values:
        return None
    return np.asarray(
        [np.nan if value is None else value for value in values],
        dtype=np.float64,
    )
