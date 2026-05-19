"""Calculation result domain object."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np

from prochem.core.calculation_error import CalculationError
from prochem.core.results import BandStructure, DensityOfStates, ElectronicSteps, IonicSteps
from prochem.core.structure import Structure
from prochem.core.structure_dataset import StructureDataset
from prochem.core.structures import Structures


@dataclass(slots=True)
class Calculation:
    """Unified calculation object returned by parser backends."""

    source: Path | str
    engine: str
    structures: Optional[Structures] = None
    dataset: Optional[StructureDataset] = None
    properties: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: CalculationError = field(default_factory=CalculationError)

    def __post_init__(self) -> None:
        self.source = Path(self.source)
        self.engine = self.engine.lower()

    @property
    def name(self) -> str:
        return self.source.name

    @property
    def directory(self) -> Path:
        return self.source.parent

    @property
    def structure(self) -> Optional[Structure]:
        if self.structures is not None:
            return self.structures.frame(0)
        if self.dataset is not None:
            return self.dataset.structure(0)
        return None

    @property
    def step_count(self) -> int:
        return 0 if self.structures is None else self.structures.step_count

    @property
    def structure_count(self) -> int:
        if self.dataset is not None:
            return self.dataset.structure_count
        return self.step_count

    @property
    def atom_count(self) -> int:
        if self.structures is not None:
            return self.structures.atom_count
        if self.dataset is not None:
            counts = self.dataset.atom_counts
            return int(counts[0]) if np.all(counts == counts[0]) else int(counts.max())
        return 0

    @property
    def electronic_steps(self) -> ElectronicSteps | None:
        value = self.properties.get("electronic_steps")
        return value if isinstance(value, ElectronicSteps) else None

    @property
    def ionic_steps(self) -> IonicSteps | None:
        value = self.properties.get("ionic_steps")
        return value if isinstance(value, IonicSteps) else None

    @property
    def density_of_states(self) -> DensityOfStates | None:
        value = self.properties.get("density_of_states", self.properties.get("dos"))
        return value if isinstance(value, DensityOfStates) else None

    @property
    def band_structure(self) -> BandStructure | None:
        value = self.properties.get("band_structure")
        return value if isinstance(value, BandStructure) else None

    def __repr__(self) -> str:
        payload = "empty"
        if self.structures is not None:
            payload = f"structures={self.structures.step_count} frames, atoms={self.structures.atom_count}"
        elif self.dataset is not None:
            payload = (
                f"dataset={self.dataset.structure_count} structures, "
                f"max_atoms={self.atom_count}"
            )
        status = "error" if self.errors.exist else "ok"
        return (
            "Calculation("
            f"engine='{self.engine}', source={str(self.source)!r}, "
            f"{payload}, status='{status}', warnings={len(self.warnings)}"
            ")"
        )


__all__ = ["Calculation"]
