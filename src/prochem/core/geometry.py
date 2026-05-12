"""Geometry calculations independent of GUI, notebooks and web adapters."""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

from prochem.core.models import Structure, Trajectory


def distance(
    structure: Structure,
    first_index: int,
    second_index: int,
    *,
    use_pbc: bool = True,
) -> float:
    vector = displacement(structure, first_index, second_index, use_pbc=use_pbc)
    return float(np.linalg.norm(vector))


def displacement(
    structure: Structure,
    first_index: int,
    second_index: int,
    *,
    use_pbc: bool = True,
) -> np.ndarray:
    if (
        use_pbc
        and structure.cell is not None
        and structure.direct_positions is not None
    ):
        delta = structure.direct_positions[second_index] - structure.direct_positions[first_index]
        delta = delta - np.round(delta)
        return delta @ structure.cell.vectors
    return structure.positions[second_index] - structure.positions[first_index]


def distance_series(
    trajectory: Trajectory,
    first_atom_id: int,
    second_atom_id: int,
    *,
    use_pbc: bool = True,
) -> np.ndarray:
    values = []
    for frame in trajectory.frames:
        local = _local_indices(frame, [first_atom_id, second_atom_id])
        if local is None:
            values.append(np.nan)
        else:
            values.append(distance(frame, local[0], local[1], use_pbc=use_pbc))
    return np.asarray(values, dtype=np.float64)


def valence_angle(
    trajectory: Trajectory,
    first_atom_id: int,
    center_atom_id: int,
    third_atom_id: int,
    *,
    use_pbc: bool = True,
) -> np.ndarray:
    values = []
    for frame in trajectory.frames:
        local = _local_indices(frame, [first_atom_id, center_atom_id, third_atom_id])
        if local is None:
            values.append(np.nan)
            continue
        v1 = displacement(frame, local[1], local[0], use_pbc=use_pbc)
        v2 = displacement(frame, local[1], local[2], use_pbc=use_pbc)
        denom = np.linalg.norm(v1) * np.linalg.norm(v2)
        if denom == 0 or not np.isfinite(denom):
            values.append(np.nan)
            continue
        cosine = np.clip(np.dot(v1, v2) / denom, -1.0, 1.0)
        values.append(float(np.degrees(np.arccos(cosine))))
    return np.asarray(values, dtype=np.float64)


def center_of_mass(
    trajectory: Trajectory,
    atom_ids: Sequence[int],
    *,
    masses: Optional[Sequence[float]] = None,
) -> np.ndarray:
    selected = [int(atom_id) for atom_id in atom_ids]
    if masses is None:
        mass_values = [trajectory.atom_record(atom_id).mass for atom_id in selected]
        if any(value is None for value in mass_values):
            raise ValueError("Masses are required to compute center of mass.")
        masses_array = np.asarray(mass_values, dtype=np.float64)
    else:
        masses_array = np.asarray(masses, dtype=np.float64)

    positions = trajectory.positions_array()
    id_to_column = {record.atom_id: index for index, record in enumerate(trajectory.atom_registry)}
    columns = [id_to_column[atom_id] for atom_id in selected]
    selected_positions = positions[:, columns, :]
    valid = np.isfinite(selected_positions).all(axis=2)
    weighted = selected_positions * masses_array[np.newaxis, :, np.newaxis]
    weighted[~valid] = 0.0
    weight_sums = (valid * masses_array[np.newaxis, :]).sum(axis=1)
    result = weighted.sum(axis=1) / weight_sums[:, np.newaxis]
    result[weight_sums == 0] = np.nan
    return result


def _local_indices(frame: Structure, atom_ids: Sequence[int]) -> list[int] | None:
    id_to_local = {int(atom_id): index for index, atom_id in enumerate(frame.atom_ids)}
    indices = []
    for atom_id in atom_ids:
        if int(atom_id) not in id_to_local:
            return None
        indices.append(id_to_local[int(atom_id)])
    return indices

