"""Web API schemas.

Pydantic models will live here when the FastAPI adapter is implemented.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CalculationSummary:
    name: str
    engine: str
    step_count: int
    atom_count: int

