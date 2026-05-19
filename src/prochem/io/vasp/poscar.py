"""POSCAR, CONTCAR, XDATCAR, CHG and CHGCAR parsers."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from prochem.core.models import Calculation, Cell, Structures
from prochem.io.vasp.common import (
    VASPfileType,
    error_calculation,
    numbers_from_line,
    read_nonempty_lines,
    species_from_symbols_counts,
    tokens_are_ints,
)


def read_poscar(source: Path, file_type: VASPfileType, engine: str = "vasp") -> Calculation:
    """Read POSCAR/CONTCAR structure files."""
    lines = read_nonempty_lines(source)
    try:
        parsed = parse_poscar_lines(lines)
    except ValueError as error:
        return error_calculation(source, engine, str(error))
    structures = Structures.from_arrays(
        species=parsed["species"],
        positions=parsed["positions"],
        direct_positions=parsed["direct_positions"],
        cell=Cell(parsed["cell"]),
        sources=(source,),
    )
    return Calculation(
        source=source,
        engine=engine,
        structures=structures,
        properties={
            "file_type": file_type.value,
            "comment": parsed["comment"],
            "symbols": parsed["symbols"],
            "counts": parsed["counts"],
            "selective_dynamics": parsed["selective_dynamics"],
        },
    )


def read_xdatcar(source: Path, file_type: VASPfileType, engine: str = "vasp") -> Calculation:
    """Read VASP XDATCAR structure-sequence files."""
    lines = read_nonempty_lines(source)
    try:
        header = parse_xdatcar_header(lines)
    except ValueError as error:
        return error_calculation(source, engine, str(error))

    frames = []
    configuration_indices = []
    cursor = header["positions_start"]
    atom_count = int(sum(header["counts"]))
    while cursor < len(lines):
        line = lines[cursor]
        if "configuration" in line.lower():
            numbers = numbers_from_line(line)
            configuration_indices.append(int(numbers[-1]) if numbers else len(frames) + 1)
            cursor += 1
        if cursor + atom_count > len(lines):
            break
        try:
            frame = np.asarray(
                [list(map(float, lines[cursor + index].split()[:3])) for index in range(atom_count)],
                dtype=np.float64,
            )
        except ValueError:
            cursor += 1
            continue
        frames.append(frame)
        cursor += atom_count

    if not frames:
        return error_calculation(source, engine, "No XDATCAR structure frames were found.")

    direct_positions = np.asarray(frames, dtype=np.float64)
    positions = direct_positions @ header["cell"]
    structures = Structures.from_arrays(
        species=header["species"],
        positions=positions,
        direct_positions=direct_positions,
        cell=Cell(header["cell"]),
        sources=tuple(source for _ in range(len(frames))),
        properties={"format": "XDATCAR"},
    )
    return Calculation(
        source=source,
        engine=engine,
        structures=structures,
        properties={
            "file_type": file_type.value,
            "comment": header["comment"],
            "symbols": header["symbols"],
            "counts": header["counts"],
            "configuration_indices": np.asarray(configuration_indices, dtype=np.int64),
        },
    )


def read_chgcar(source: Path, file_type: VASPfileType, engine: str = "vasp") -> Calculation:
    """Read CHG/CHGCAR structure and the first volumetric data block."""
    lines = read_nonempty_lines(source)
    try:
        parsed = parse_poscar_lines(lines)
    except ValueError as error:
        return error_calculation(source, engine, str(error))

    cursor = parsed["positions_end"]
    if cursor >= len(lines):
        return error_calculation(source, engine, "No charge-density grid was found.")
    grid = np.asarray(list(map(int, lines[cursor].split()[:3])), dtype=np.int64)
    cursor += 1
    value_count = int(np.prod(grid))
    values = []
    while cursor < len(lines) and len(values) < value_count:
        values.extend(numbers_from_line(lines[cursor]))
        cursor += 1
    if len(values) < value_count:
        return error_calculation(source, engine, "Charge-density block ended before the grid was complete.")

    density = np.asarray(values[:value_count], dtype=np.float64).reshape(tuple(grid), order="F")
    structures = Structures.from_arrays(
        species=parsed["species"],
        positions=parsed["positions"],
        direct_positions=parsed["direct_positions"],
        cell=Cell(parsed["cell"]),
        sources=(source,),
    )
    return Calculation(
        source=source,
        engine=engine,
        structures=structures,
        properties={
            "file_type": file_type.value,
            "comment": parsed["comment"],
            "symbols": parsed["symbols"],
            "counts": parsed["counts"],
            "volumetric_data": {
                "grid": grid,
                "values": density,
                "units": "VASP raw charge density",
            },
        },
    )


def parse_poscar_header(lines: list[str]) -> dict:
    if len(lines) < 8:
        raise ValueError("POSCAR-like file is too short.")

    comment = lines[0]
    scale = float(lines[1].split()[0])
    raw_cell = np.asarray(
        [list(map(float, lines[index].split()[:3])) for index in range(2, 5)],
        dtype=np.float64,
    )
    if scale < 0:
        volume = abs(np.linalg.det(raw_cell))
        scale_factor = (-scale / volume) ** (1.0 / 3.0)
        cell_vectors = raw_cell * scale_factor
        position_scale = 1.0
    else:
        cell_vectors = raw_cell * scale
        position_scale = scale

    symbols_line = lines[5].split()
    if tokens_are_ints(symbols_line):
        counts = list(map(int, symbols_line))
        symbols = [f"X{index + 1}" for index in range(len(counts))]
        cursor = 6
    else:
        symbols = symbols_line
        counts = list(map(int, lines[6].split()))
        cursor = 7

    selective_dynamics = False
    if lines[cursor].lower().startswith("s"):
        selective_dynamics = True
        cursor += 1

    coordinate_mode = lines[cursor].lower()
    cursor += 1

    return {
        "comment": comment,
        "scale": scale,
        "position_scale": position_scale,
        "cell": cell_vectors,
        "symbols": symbols,
        "counts": counts,
        "species": species_from_symbols_counts(symbols, counts),
        "selective_dynamics": selective_dynamics,
        "coordinate_mode": coordinate_mode,
        "positions_start": cursor,
    }


def parse_poscar_lines(lines: list[str]) -> dict:
    header = parse_poscar_header(lines)
    atom_count = int(sum(header["counts"]))
    cursor = header["positions_start"]
    if cursor + atom_count > len(lines):
        raise ValueError("POSCAR-like file does not contain all atom positions.")

    raw_positions = np.asarray(
        [list(map(float, lines[cursor + index].split()[:3])) for index in range(atom_count)],
        dtype=np.float64,
    )
    coordinate_mode = header["coordinate_mode"]
    if coordinate_mode.startswith(("d", "f")):
        direct_positions = raw_positions
        positions = direct_positions @ header["cell"]
    else:
        positions = raw_positions * header["position_scale"]
        direct_positions = positions @ np.linalg.inv(header["cell"])

    header.update(
        {
            "positions": positions,
            "direct_positions": direct_positions,
            "positions_end": cursor + atom_count,
        }
    )
    return header


def parse_xdatcar_header(lines: list[str]) -> dict:
    if len(lines) < 7:
        raise ValueError("XDATCAR file is too short.")

    comment = lines[0]
    scale = float(lines[1].split()[0])
    raw_cell = np.asarray(
        [list(map(float, lines[index].split()[:3])) for index in range(2, 5)],
        dtype=np.float64,
    )
    cell_vectors = raw_cell * scale
    symbols_line = lines[5].split()
    if tokens_are_ints(symbols_line):
        counts = list(map(int, symbols_line))
        symbols = [f"X{index + 1}" for index in range(len(counts))]
        cursor = 6
    else:
        symbols = symbols_line
        counts = list(map(int, lines[6].split()))
        cursor = 7

    return {
        "comment": comment,
        "scale": scale,
        "cell": cell_vectors,
        "symbols": symbols,
        "counts": counts,
        "species": species_from_symbols_counts(symbols, counts),
        "positions_start": cursor,
    }
