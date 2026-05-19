"""Shared utilities for VASP parsers."""

from __future__ import annotations

import re
from enum import Enum
from pathlib import Path

import numpy as np

from prochem.core.models import Calculation, CalculationError


class VASPfileType(Enum):
    XML = "vasprun.xml"
    OUTCAR = "OUTCAR"
    XDATCAR = "XDATCAR"
    POSCAR = "POSCAR"
    CONTCAR = "CONTCAR"
    CHGCAR = "CHGCAR"
    CHG = "CHG"
    OSZICAR = "OSZICAR"
    DOSCAR = "DOSCAR"
    EIGENVAL = "EIGENVAL"
    UNKNOWN = "UNKNOWN"


TAG_VALUE_RE = re.compile(r"<c[^>]*>\s*([^<]+?)\s*</c>")
FLOAT_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][-+]?\d+)?")


def numbers_from_line(line: str) -> list[float]:
    return [float(value.replace("D", "E").replace("d", "e")) for value in FLOAT_RE.findall(line)]


def read_nonempty_lines(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip()
    ]


def species_from_symbols_counts(symbols: list[str], counts: list[int]) -> np.ndarray:
    return np.asarray(
        [symbol for symbol, count in zip(symbols, counts, strict=False) for _ in range(count)],
        dtype=str,
    )


def read_numeric_block(lines: list[str], start: int, count: int) -> np.ndarray:
    rows = [numbers_from_line(lines[index]) for index in range(start, start + count)]
    return np.asarray(rows, dtype=np.float64)


def tokens_are_ints(tokens: list[str]) -> bool:
    try:
        [int(token) for token in tokens]
    except ValueError:
        return False
    return True


def float_from_fortran(value: str) -> float:
    return float(value.replace("D", "E").replace("d", "e").rstrip(","))


def error_calculation(source: Path, engine: str, message: str) -> Calculation:
    """Return a parser result carrying a VASP parsing error."""
    return Calculation(
        source=source,
        engine=engine,
        errors=CalculationError(exist=True, message=message),
    )


def derive_potential_kinetic_arrays(
    potentials: list[float | None],
    kinetics: list[float | None],
    totals: list[float | None],
) -> tuple[np.ndarray | None, np.ndarray | None, np.ndarray | None]:
    """Return structure energy arrays, deriving only values forced by totals."""
    potential_values = []
    kinetic_values = []
    total_values = []
    for potential, kinetic, total in zip(potentials, kinetics, totals, strict=True):
        if potential is None and total is not None and kinetic is not None:
            potential = total - kinetic
        if kinetic is None and total is not None and potential is not None:
            kinetic = total - potential
        if total is None and potential is not None and kinetic is not None:
            total = potential + kinetic
        potential_values.append(np.nan if potential is None else potential)
        kinetic_values.append(np.nan if kinetic is None else kinetic)
        total_values.append(np.nan if total is None else total)

    potential_array = (
        np.asarray(potential_values, dtype=np.float64)
        if any(value is not None for value in potentials)
        or any(total is not None and kinetic is not None for total, kinetic in zip(totals, kinetics, strict=True))
        else None
    )
    kinetic_array = (
        np.asarray(kinetic_values, dtype=np.float64)
        if any(value is not None for value in kinetics)
        or any(total is not None and potential is not None for total, potential in zip(totals, potentials, strict=True))
        else None
    )
    total_array = (
        np.asarray(total_values, dtype=np.float64)
        if any(value is not None for value in totals)
        or any(
            potential is not None and kinetic is not None
            for potential, kinetic in zip(potentials, kinetics, strict=True)
        )
        else None
    )
    return potential_array, kinetic_array, total_array
