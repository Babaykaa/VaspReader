"""DOSCAR parser."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from prochem.core.models import Calculation
from prochem.core.results import DensityOfStates, ProjectedDensityOfStates
from prochem.io.vasp.common import (
    VASPfileType,
    error_calculation,
    numbers_from_line,
    read_nonempty_lines,
    read_numeric_block,
)


def read_doscar(source: Path, file_type: VASPfileType = VASPfileType.DOSCAR, engine: str = "vasp") -> Calculation:
    """Read DOSCAR total and projected density-of-states blocks."""
    lines = read_nonempty_lines(source)
    if len(lines) < 6:
        return error_calculation(source, engine, "DOSCAR file is too short.")
    first = lines[0].split()
    atom_count = int(first[0]) if first else 0
    header_values = numbers_from_line(lines[5])
    if len(header_values) < 4:
        return error_calculation(source, engine, "DOSCAR header does not contain NEDOS/EFERMI metadata.")
    emax, emin, nedos, efermi = header_values[:4]
    nedos = int(nedos)
    cursor = 6
    total_dos = read_numeric_block(lines, cursor, nedos)
    cursor += nedos
    projected_dos = []
    for atom_index in range(atom_count):
        if cursor >= len(lines):
            break
        atom_header = numbers_from_line(lines[cursor])
        cursor += 1
        if cursor + nedos > len(lines):
            break
        projected_dos.append(
            ProjectedDensityOfStates(
                atom_index=atom_index + 1,
                header=np.asarray(atom_header, dtype=np.float64),
                data=read_numeric_block(lines, cursor, nedos),
            )
        )
        cursor += nedos
    density_of_states = DensityOfStates(
        atom_count=atom_count,
        energy_min=emin,
        energy_max=emax,
        fermi_energy=efermi,
        total=total_dos,
        projected=projected_dos,
    )
    return Calculation(
        source=source,
        engine=engine,
        properties={
            "file_type": file_type.value,
            "density_of_states": density_of_states,
        },
    )
