"""Geometry-related table helpers for analysis workflows."""

from __future__ import annotations

from typing import Sequence

import pandas as pd

from prochem.analysis.trajectory import time_axis
from prochem.core.geometry import (
    center_of_mass,
    distance,
    distance_series,
    displacement,
    valence_angle,
)
from prochem.core.models import Trajectory


def add_distance_columns(
    dataframe: pd.DataFrame,
    trajectory: Trajectory,
    pairs: Sequence[tuple[int, int]],
    *,
    use_pbc: bool = True,
) -> pd.DataFrame:
    result = dataframe.copy()
    for first, second in pairs:
        result[f"{first}--{second}"] = distance_series(
            trajectory,
            first,
            second,
            use_pbc=use_pbc,
        )
    return result


def add_valence_angle_columns(
    dataframe: pd.DataFrame,
    trajectory: Trajectory,
    triples: Sequence[tuple[int, int, int]],
    *,
    use_pbc: bool = True,
) -> pd.DataFrame:
    result = dataframe.copy()
    for first, center, third in triples:
        result[f"{first}-{center}-{third}"] = valence_angle(
            trajectory,
            first,
            center,
            third,
            use_pbc=use_pbc,
        )
    return result


def center_of_mass_dataframe(
    trajectory: Trajectory,
    atom_ids: Sequence[int],
    *,
    name: str = "cm",
    masses: Sequence[float] | None = None,
) -> pd.DataFrame:
    values = center_of_mass(trajectory, atom_ids, masses=masses)
    return pd.DataFrame(
        {
            "Time, fs": time_axis(trajectory),
            f"{name}_x": values[:, 0],
            f"{name}_y": values[:, 1],
            f"{name}_z": values[:, 2],
        }
    )


__all__ = [
    "add_distance_columns",
    "add_valence_angle_columns",
    "center_of_mass",
    "center_of_mass_dataframe",
    "distance",
    "distance_series",
    "displacement",
    "valence_angle",
]

