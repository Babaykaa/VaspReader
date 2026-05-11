"""Base classes for calculation parsers."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2026 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from core.models import Calculation, CalculationError

__all__ = ["AbstractParser", "Calculation", "CalculationError"]


class AbstractParser(ABC):
    """Base parser contract for all calculation formats."""

    engine = "unknown"

    def __init__(self, source: str | Path) -> None:
        self.source = Path(source)

    @classmethod
    def can_parse(cls, source: str | Path) -> bool:
        """Return True when this parser can read source."""
        return False

    @abstractmethod
    def parse(self) -> Calculation:
        """Parse source and return a calculation object."""
        raise NotImplementedError

    def _error_calculation(self, message: str) -> Calculation:
        return Calculation(
            source=self.source,
            engine=self.engine,
            errors=CalculationError(exist=True, message=message),
        )
