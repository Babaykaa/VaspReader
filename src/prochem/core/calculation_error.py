"""Parser error state."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CalculationError:
    """Error state for parser results."""

    exist: bool = False
    message: str = ""


__all__ = ["CalculationError"]
