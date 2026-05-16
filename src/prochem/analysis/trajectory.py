"""Trajectory-level numeric analysis."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2026 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

from prochem.core.models import Trajectory
from prochem.core.units import KINETIC_ENERGY_FACTOR


def time_axis(trajectory: Trajectory) -> np.ndarray:
    """Return trajectory time in fs, falling back to step index when needed."""
    if trajectory.time_fs is not None:
        return trajectory.time_fs
    if trajectory.timestep_fs is not None:
        return np.arange(trajectory.step_count, dtype=np.float64) * trajectory.timestep_fs
    return np.arange(trajectory.step_count, dtype=np.float64)


def unwrap_direct_positions(direct_positions: np.ndarray) -> np.ndarray:
    """Unwrap direct coordinates across periodic boundaries."""
    direct = np.asarray(direct_positions, dtype=np.float64)
    unwrapped = direct.copy()
    for step in range(1, direct.shape[0]):
        delta = direct[step] - direct[step - 1]
        shift = np.round(delta)
        shift[~np.isfinite(delta)] = 0
        unwrapped[step] = unwrapped[step - 1] + delta - shift
    return unwrapped


def velocities(
    trajectory: Trajectory,
    atom_ids: Optional[Sequence[int]] = None,
    *,
    scale_to_m_per_s: bool = True,
) -> np.ndarray:
    """Return finite-difference speeds for selected atoms.

    The result has shape (steps, atoms). The first row is NaN because no previous
    frame exists.
    """
    selected = list(atom_ids) if atom_ids is not None else [record.atom_id for record in trajectory.atom_registry]
    id_to_column = {record.atom_id: index for index, record in enumerate(trajectory.atom_registry)}
    columns = [id_to_column[int(atom_id)] for atom_id in selected]
    positions = trajectory.positions_array()[:, columns, :]
    times = time_axis(trajectory)
    delta = np.diff(positions, axis=0)
    dt = np.diff(times)
    dt[dt == 0] = np.nan
    speeds = np.linalg.norm(delta, axis=2) / dt[:, np.newaxis]
    if scale_to_m_per_s:
        speeds *= 1000.0
    return np.vstack([np.full((1, len(columns)), np.nan), speeds])


def kinetic_energy(
    trajectory: Trajectory,
    atom_ids: Optional[Sequence[int]] = None,
    *,
    masses: Optional[Sequence[float]] = None,
) -> np.ndarray:
    """Return per-atom kinetic energy using the legacy ProChem factor."""
    selected = list(atom_ids) if atom_ids is not None else [record.atom_id for record in trajectory.atom_registry]
    speeds = velocities(trajectory, selected)
    if masses is None:
        mass_values = []
        for atom_id in selected:
            mass_values.append(trajectory.atom_record(int(atom_id)).mass)
        if any(value is None for value in mass_values):
            raise ValueError("Masses are required to compute kinetic energy.")
        masses_array = np.asarray(mass_values, dtype=np.float64)
    else:
        masses_array = np.asarray(masses, dtype=np.float64)
    return speeds**2 * masses_array[np.newaxis, :] / KINETIC_ENERGY_FACTOR
