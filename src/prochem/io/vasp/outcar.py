"""OUTCAR parser."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from prochem.core.models import Calculation, CalculationError, Trajectory
from prochem.io.vasp.common import VASPfileType, numbers_from_line, species_from_symbols_counts


def read_outcar(source: Path, file_type: VASPfileType = VASPfileType.OUTCAR, engine: str = "vasp") -> Calculation:
    """Read OUTCAR trajectory positions, forces and lattice vectors."""
    counts = []
    symbols = []
    timestep_fs = None
    current_cell = None
    cells = []
    positions = []
    forces = []

    with source.open("r", encoding="utf-8", errors="replace") as outcar:
        lines_iter = iter(outcar)
        for line in lines_iter:
            if "POTIM" in line and timestep_fs is None:
                values = numbers_from_line(line)
                if values:
                    timestep_fs = values[0]
            elif "VRHFIN" in line:
                symbol = line.split("=", 1)[-1].split(":", 1)[0].strip()
                if symbol:
                    symbols.append(symbol)
            elif "ions per type" in line:
                counts = [int(value) for value in numbers_from_line(line)]
            elif "direct lattice vectors" in line:
                basis = []
                for _ in range(3):
                    values = numbers_from_line(next(lines_iter))
                    if len(values) >= 3:
                        basis.append(values[:3])
                if len(basis) == 3:
                    current_cell = np.asarray(basis, dtype=np.float64)
            elif "POSITION" in line and "TOTAL-FORCE" in line:
                next(lines_iter, None)
                frame_positions = []
                frame_forces = []
                for row in lines_iter:
                    values = numbers_from_line(row)
                    if len(values) < 6:
                        break
                    frame_positions.append(values[:3])
                    frame_forces.append(values[3:6])
                if frame_positions:
                    positions.append(frame_positions)
                    forces.append(frame_forces)
                    if current_cell is not None:
                        cells.append(current_cell)

    if not positions:
        return _error_calculation(source, engine, "No POSITION/TOTAL-FORCE blocks were found in OUTCAR.")
    atom_count = len(positions[0])
    if not counts:
        counts = [atom_count]
    if not symbols:
        symbols = [f"X{index + 1}" for index in range(len(counts))]
    species = species_from_symbols_counts(symbols, counts)
    if species.shape[0] != atom_count:
        species = np.asarray([f"X{index + 1}" for index in range(atom_count)], dtype=str)
    if not cells:
        return _error_calculation(source, engine, "No lattice vectors were found in OUTCAR.")

    positions_array = np.asarray(positions, dtype=np.float64)
    forces_array = np.asarray(forces, dtype=np.float64)
    cells_array = np.asarray(cells, dtype=np.float64)
    trajectory = Trajectory.from_arrays(
        species=species,
        positions=positions_array,
        cell=cells_array if len(cells_array) == len(positions_array) else cells_array[0],
        forces=forces_array,
        timestep_fs=timestep_fs,
        time_fs=np.arange(len(positions_array), dtype=np.float64) * timestep_fs
        if timestep_fs is not None
        else None,
        properties={"format": "OUTCAR"},
    )
    return Calculation(
        source=source,
        engine=engine,
        trajectory=trajectory,
        properties={"file_type": file_type.value, "symbols": symbols, "counts": counts},
    )


def _error_calculation(source: Path, engine: str, message: str) -> Calculation:
    return Calculation(
        source=source,
        engine=engine,
        errors=CalculationError(exist=True, message=message),
    )

