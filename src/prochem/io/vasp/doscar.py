"""DOSCAR parser."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from prochem.core.models import Calculation, CalculationError
from prochem.io.vasp.common import VASPfileType, numbers_from_line, read_nonempty_lines, read_numeric_block


def read_doscar(source: Path, file_type: VASPfileType = VASPfileType.DOSCAR, engine: str = "vasp") -> Calculation:
    """Read DOSCAR total and projected density-of-states blocks."""
    lines = read_nonempty_lines(source)
    if len(lines) < 6:
        return _error_calculation(source, engine, "DOSCAR file is too short.")
    first = lines[0].split()
    atom_count = int(first[0]) if first else 0
    header_values = numbers_from_line(lines[5])
    if len(header_values) < 4:
        return _error_calculation(source, engine, "DOSCAR header does not contain NEDOS/EFERMI metadata.")
    emax, emin, nedos, efermi = header_values[:4]
    nedos = int(nedos)
    cursor = 6
    total_dos = read_numeric_block(lines, cursor, nedos)
    cursor += nedos
    projected_dos = []
    for _ in range(atom_count):
        if cursor >= len(lines):
            break
        atom_header = numbers_from_line(lines[cursor])
        cursor += 1
        if cursor + nedos > len(lines):
            break
        projected_dos.append(
            {
                "header": np.asarray(atom_header, dtype=np.float64),
                "data": read_numeric_block(lines, cursor, nedos),
            }
        )
        cursor += nedos
    return Calculation(
        source=source,
        engine=engine,
        properties={
            "file_type": file_type.value,
            "atom_count": atom_count,
            "emax": emax,
            "emin": emin,
            "nedos": nedos,
            "efermi": efermi,
            "total_dos": total_dos,
            "projected_dos": projected_dos,
        },
    )


def _error_calculation(source: Path, engine: str, message: str) -> Calculation:
    return Calculation(
        source=source,
        engine=engine,
        errors=CalculationError(exist=True, message=message),
    )

