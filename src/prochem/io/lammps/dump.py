"""LAMMPS dump parser placeholder."""

from __future__ import annotations

from pathlib import Path

from prochem.core.models import Calculation
from prochem.io.base import AbstractParser


class Parser(AbstractParser):
    """Parser skeleton for future LAMMPS dump support."""

    engine = "lammps"

    @classmethod
    def can_parse(cls, path: str | Path) -> bool:
        source = Path(path)
        return source.is_file() and source.suffix.lower() in {".dump", ".lammpstrj"}

    def parse(self) -> Calculation:
        return self._error_calculation("LAMMPS dump parser is not implemented yet.")

