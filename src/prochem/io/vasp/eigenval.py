"""EIGENVAL parser."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from prochem.core.models import Calculation
from prochem.core.results import BandStructure
from prochem.io.vasp.common import VASPfileType, error_calculation, numbers_from_line, read_nonempty_lines


def read_eigenval(source: Path, file_type: VASPfileType = VASPfileType.EIGENVAL, engine: str = "vasp") -> Calculation:
    """Read EIGENVAL k-point band energies and occupations."""
    lines = read_nonempty_lines(source)
    if len(lines) < 7:
        return error_calculation(source, engine, "EIGENVAL file is too short.")
    metadata = list(map(int, lines[5].split()[:3]))
    electron_count, kpoint_count, band_count = metadata
    cursor = 6
    kpoints = []
    weights = []
    bands = []
    for _ in range(kpoint_count):
        while cursor < len(lines) and len(lines[cursor].split()) < 4:
            cursor += 1
        if cursor >= len(lines):
            break
        kpoint_line = list(map(float, lines[cursor].split()[:4]))
        kpoints.append(kpoint_line[:3])
        weights.append(kpoint_line[3])
        cursor += 1
        kpoint_bands = []
        for _ in range(band_count):
            values = numbers_from_line(lines[cursor])
            if len(values) >= 3:
                kpoint_bands.append(values[1:])
            cursor += 1
        bands.append(kpoint_bands)
    band_structure = BandStructure(
        electron_count=electron_count,
        kpoints=np.asarray(kpoints, dtype=np.float64),
        weights=np.asarray(weights, dtype=np.float64),
        bands=np.asarray(bands, dtype=np.float64),
    )
    return Calculation(
        source=source,
        engine=engine,
        properties={
            "file_type": file_type.value,
            "band_structure": band_structure,
        },
    )
