"""Simulation cell domain object."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

ArrayLike = np.ndarray


@dataclass(slots=True)
class Cell:
    """Simulation cell vectors."""

    vectors: ArrayLike
    pbc: tuple[bool, bool, bool] = (True, True, True)
    units: str = "angstrom"

    def __post_init__(self) -> None:
        self.vectors = np.asarray(self.vectors, dtype=np.float64)
        if self.vectors.shape != (3, 3):
            raise ValueError(f"Cell vectors must have shape (3, 3), got {self.vectors.shape}.")

    def __repr__(self) -> str:
        lengths = np.linalg.norm(self.vectors, axis=1)
        formatted = ", ".join(f"{float(value):.6g}" for value in lengths)
        return f"Cell(lengths=({formatted}), pbc={self.pbc}, units='{self.units}')"


__all__ = ["Cell"]
