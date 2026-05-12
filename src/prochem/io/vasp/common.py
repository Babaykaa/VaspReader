"""Shared utilities for VASP parsers."""

from __future__ import annotations

import re
from enum import Enum
from pathlib import Path

import numpy as np


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

