"""DataFrame representations for trajectories and analysis results."""

from __future__ import annotations

from typing import Iterable, Optional, Sequence

import numpy as np
import pandas as pd

from prochem.analysis.trajectory import kinetic_energy, time_axis, unwrap_direct_positions, velocities
from prochem.core.geometry import center_of_mass, distance_series, valence_angle
from prochem.core.models import Trajectory


def atom_labels(trajectory: Trajectory, atom_ids: Optional[Iterable[int]] = None) -> list[str]:
    """Return stable labels like C_1 for atom ids."""
    selected = list(atom_ids) if atom_ids is not None else list(trajectory.atom_ids)
    labels = []
    for atom_id in selected:
        record = trajectory.atom_record(int(atom_id))
        labels.append(f"{record.species}_{record.atom_id + 1}")
    return labels


def coordinate_dataframe(
    trajectory: Trajectory,
    atom_ids: Optional[Sequence[int]] = None,
    *,
    include_direct: bool = True,
    include_cartesian: bool = True,
    unwrap_direct: bool = True,
) -> pd.DataFrame:
    """Build a coordinate table suitable for GUI, notebooks or export."""
    selected = list(atom_ids) if atom_ids is not None else list(trajectory.atom_ids)
    columns = trajectory.atom_columns(selected)
    labels = atom_labels(trajectory, selected)
    data: dict[str, np.ndarray] = {"Time, fs": time_axis(trajectory)}

    direct = trajectory.direct_positions_array()
    if unwrap_direct and direct is not None:
        direct = unwrap_direct_positions(direct)
    positions = trajectory.positions_array()

    for column, label in zip(columns, labels, strict=True):
        if include_direct and direct is not None:
            data[f"{label}_dir_1"] = direct[:, column, 0]
            data[f"{label}_dir_2"] = direct[:, column, 1]
            data[f"{label}_dir_3"] = direct[:, column, 2]
        if include_cartesian:
            data[f"{label}_x"] = positions[:, column, 0]
            data[f"{label}_y"] = positions[:, column, 1]
            data[f"{label}_z"] = positions[:, column, 2]
    return pd.DataFrame(data)


def add_velocity_columns(
    dataframe: pd.DataFrame,
    trajectory: Trajectory,
    atom_ids: Sequence[int],
    *,
    prefix: str = "V",
) -> pd.DataFrame:
    """Return a copy of dataframe with per-atom speed columns."""
    result = dataframe.copy()
    speed = velocities(trajectory, atom_ids)
    for column, label in enumerate(atom_labels(trajectory, atom_ids)):
        result[f"{prefix}_{label}"] = speed[:, column]
    return result


def add_kinetic_energy_columns(
    dataframe: pd.DataFrame,
    trajectory: Trajectory,
    atom_ids: Sequence[int],
    *,
    prefix: str = "E",
) -> pd.DataFrame:
    """Return a copy of dataframe with per-atom kinetic-energy columns."""
    result = dataframe.copy()
    energy = kinetic_energy(trajectory, atom_ids)
    for column, label in enumerate(atom_labels(trajectory, atom_ids)):
        result[f"{prefix}_{label}"] = energy[:, column]
    return result


def add_distance_columns(
    dataframe: pd.DataFrame,
    trajectory: Trajectory,
    pairs: Sequence[tuple[int, int]],
    *,
    use_pbc: bool = True,
) -> pd.DataFrame:
    """Return a copy of dataframe with distance columns for atom-id pairs."""
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
    """Return a copy of dataframe with valence-angle columns for atom-id triples."""
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
    """Return a time-indexed center-of-mass table."""
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
    "add_kinetic_energy_columns",
    "add_valence_angle_columns",
    "add_velocity_columns",
    "atom_labels",
    "center_of_mass_dataframe",
    "coordinate_dataframe",
]
