"""Core domain model re-exports."""

from __future__ import annotations

import numpy as np

from prochem.core.atom import Atom, AtomStyle, SharedFloat
from prochem.core.calculation import Calculation
from prochem.core.calculation_error import CalculationError
from prochem.core.cell import Cell
from prochem.core.structure import Structure
from prochem.core.structure_dataset import StructureDataset
from prochem.core.structures import Structures

ArrayLike = np.ndarray

__all__ = [
    "ArrayLike",
    "Atom",
    "AtomStyle",
    "Calculation",
    "CalculationError",
    "Cell",
    "SharedFloat",
    "Structure",
    "StructureDataset",
    "Structures",
]
