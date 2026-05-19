"""Pandas-based analysis model for structure sequences."""

from __future__ import annotations

from itertools import combinations, product
from pathlib import Path
from typing import Iterable, Literal, Sequence

import numpy as np
import pandas as pd

from prochem.analysis.export import export_dataframe
from prochem.analysis.selection import Selection
from prochem.core.models import Structures
from prochem.core.units import KINETIC_ENERGY_FACTOR

Axis = Literal["x", "y", "z"]


class AnalysisTable:
    """Stateful pandas analysis table backed by hidden coordinate caches."""

    def __init__(
        self,
        structures: Structures,
        selections: Selection | Sequence[Selection],
        *,
        unwrap_direct: bool = True,
    ) -> None:
        self.structures = structures
        self.selections = _selection_tuple(selections)
        self._selection_by_name = _selection_map(self.selections)
        self._atom_ids = _union_atom_ids(self.selections)
        self._columns = structures.atom_columns(self._atom_ids)
        self._labels = {atom_id: self.atom_label(atom_id) for atom_id in self._atom_ids}
        self._coordinates = self._build_coordinate_frame(structures.positions_array())
        direct = structures.direct_positions_array()
        if direct is not None and unwrap_direct:
            direct = _unwrap_direct_positions(direct)
        self._direct_coordinates = None if direct is None else self._build_coordinate_frame(direct)
        self.data = pd.DataFrame({"Time, fs": self.time_axis})

    @property
    def time_axis(self) -> np.ndarray:
        if self.structures.time_fs is not None:
            return self.structures.time_fs
        return np.arange(self.structures.step_count, dtype=np.float64)

    @property
    def atom_ids(self) -> tuple[int, ...]:
        return self._atom_ids

    @property
    def coordinate_cache(self) -> pd.DataFrame:
        """Hidden Cartesian coordinate representation for selected unique atoms."""
        return self._coordinates.copy()

    @property
    def direct_coordinate_cache(self) -> pd.DataFrame | None:
        """Hidden direct-coordinate representation for selected unique atoms."""
        if self._direct_coordinates is None:
            return None
        return self._direct_coordinates.copy()

    def atom_label(self, atom_id: int) -> str:
        record = self.structures.atom_record(int(atom_id))
        return f"{record.name}_{int(atom_id) + 1}"

    def atom_labels(self, atom_ids: Iterable[int] | None = None) -> list[str]:
        selected = self._atom_ids if atom_ids is None else tuple(int(atom_id) for atom_id in atom_ids)
        return [self.atom_label(atom_id) for atom_id in selected]

    def selection(self, value: str | Selection) -> Selection:
        if isinstance(value, Selection):
            return value
        return self._selection_by_name[str(value)]

    def coordinates(
        self,
        selection: str | Selection | None = None,
        *,
        direct: bool = False,
    ) -> pd.DataFrame:
        """Return coordinates for one selection or all cached atoms."""
        source = self._direct_coordinates if direct else self._coordinates
        if source is None:
            return pd.DataFrame(index=self.data.index)
        atom_ids = self._atom_ids if selection is None else self.selection(selection).atom_ids
        return source.loc[:, _coordinate_columns(atom_ids)]

    def dataframe(
        self,
        *,
        include_coordinates: bool = False,
        include_direct: bool = False,
    ) -> pd.DataFrame:
        """Return visible results, optionally appending hidden coordinate caches."""
        frames = [self.data]
        if include_coordinates:
            frames.append(self._flatten_coordinates(self._coordinates, direct=False))
        if include_direct and self._direct_coordinates is not None:
            frames.append(self._flatten_coordinates(self._direct_coordinates, direct=True))
        return pd.concat(frames, axis=1)

    def add_coordinates(
        self,
        selection: str | Selection | None = None,
        *,
        direct: bool = False,
    ) -> "AnalysisTable":
        frame = self._flatten_coordinates(self.coordinates(selection, direct=direct), direct=direct)
        self._append_columns(frame)
        return self

    def add_atom_velocities(
        self,
        selection: str | Selection | None = None,
        *,
        components: bool = False,
        scale_to_m_per_s: bool = True,
        prefix: str = "V",
    ) -> "AnalysisTable":
        atom_ids = self._atom_ids if selection is None else self.selection(selection).atom_ids
        velocities = self._velocity_vectors(atom_ids)
        scale = 1000.0 if scale_to_m_per_s else 1.0
        data: dict[str, np.ndarray] = {}
        for index, atom_id in enumerate(atom_ids):
            label = self._labels[atom_id]
            vector = velocities[:, index, :] * scale
            if components:
                data[f"{prefix}_{label}_x"] = vector[:, 0]
                data[f"{prefix}_{label}_y"] = vector[:, 1]
                data[f"{prefix}_{label}_z"] = vector[:, 2]
            data[f"{prefix}_{label}"] = np.linalg.norm(vector, axis=1)
        self._append_columns(pd.DataFrame(data))
        return self

    def add_atom_kinetic_energies(
        self,
        selection: str | Selection | None = None,
        *,
        prefix: str = "E",
    ) -> "AnalysisTable":
        atom_ids = self._atom_ids if selection is None else self.selection(selection).atom_ids
        speeds = np.linalg.norm(self._velocity_vectors(atom_ids), axis=2) * 1000.0
        data = {}
        for index, atom_id in enumerate(atom_ids):
            mass = self.structures.atom_record(atom_id).mass
            data[f"{prefix}_{self._labels[atom_id]}"] = speeds[:, index] ** 2 * mass / KINETIC_ENERGY_FACTOR
        self._append_columns(pd.DataFrame(data))
        return self

    def add_center_of_mass(self, selection: str | Selection, *, prefix: str = "cm") -> "AnalysisTable":
        selected = self.selection(selection)
        values = self.center_of_mass(selected)
        name = f"{prefix}_{selected.name}"
        self._append_columns(
            pd.DataFrame(
                {
                    f"{name}_x": values[:, 0],
                    f"{name}_y": values[:, 1],
                    f"{name}_z": values[:, 2],
                }
            )
        )
        return self

    def add_center_of_mass_velocity(
        self,
        selection: str | Selection,
        *,
        prefix: str = "V_cm",
        scale_to_m_per_s: bool = True,
    ) -> "AnalysisTable":
        selected = self.selection(selection)
        velocity = _finite_difference_vectors(self.center_of_mass(selected), self.time_axis)
        if scale_to_m_per_s:
            velocity = velocity * 1000.0
        self._append_columns(pd.DataFrame({f"{prefix}_{selected.name}": np.linalg.norm(velocity, axis=1)}))
        return self

    def add_center_of_mass_kinetic_energy(
        self,
        selection: str | Selection,
        *,
        prefix: str = "E_cm",
    ) -> "AnalysisTable":
        selected = self.selection(selection)
        velocity = _finite_difference_vectors(self.center_of_mass(selected), self.time_axis) * 1000.0
        speed = np.linalg.norm(velocity, axis=1)
        mass = self.selection_mass(selected)
        self._append_columns(pd.DataFrame({f"{prefix}_{selected.name}": speed**2 * mass / KINETIC_ENERGY_FACTOR}))
        return self

    def add_distances(
        self,
        selection: str | Selection,
        *,
        pairs: Sequence[tuple[int, int]] | None = None,
        use_pbc: bool = True,
    ) -> "AnalysisTable":
        selected = self.selection(selection)
        selected_pairs = list(combinations(selected.atom_ids, 2)) if pairs is None else list(pairs)
        data = {}
        for first, second in selected_pairs:
            data[f"{self.atom_label(first)}--{self.atom_label(second)}"] = self.distance_series(
                int(first),
                int(second),
                use_pbc=use_pbc,
            )
        self._append_columns(pd.DataFrame(data))
        return self

    def add_selection_distance(
        self,
        first: str | Selection,
        second: str | Selection,
        *,
        mode: Literal["com", "pairs"] = "com",
        use_pbc: bool = True,
    ) -> "AnalysisTable":
        left = self.selection(first)
        right = self.selection(second)
        if mode == "com":
            delta = self.center_of_mass(right) - self.center_of_mass(left)
            values = np.linalg.norm(delta, axis=1)
            self._append_columns(pd.DataFrame({f"{left.name}--{right.name}": values}))
            return self
        data = {}
        for first_atom, second_atom in product(left.atom_ids, right.atom_ids):
            if first_atom == second_atom:
                continue
            data[f"{self.atom_label(first_atom)}--{self.atom_label(second_atom)}"] = self.distance_series(
                first_atom,
                second_atom,
                use_pbc=use_pbc,
            )
        self._append_columns(pd.DataFrame(data))
        return self

    def add_valence_angles(
        self,
        selection: str | Selection,
        *,
        triples: Sequence[tuple[int, int, int]] | None = None,
        use_pbc: bool = True,
    ) -> "AnalysisTable":
        selected = self.selection(selection)
        selected_triples = _all_angle_triples(selected.atom_ids) if triples is None else list(triples)
        data = {}
        for first, center, third in selected_triples:
            name = f"{self.atom_label(first)}-{self.atom_label(center)}-{self.atom_label(third)}"
            data[name] = self.valence_angle_series(first, center, third, use_pbc=use_pbc)
        self._append_columns(pd.DataFrame(data))
        return self

    def add_angles_to_plane(
        self,
        selection: str | Selection,
        *,
        plane: tuple[int, int, int],
        atom_ids: Sequence[int] | None = None,
        use_pbc: bool = True,
    ) -> "AnalysisTable":
        selected = self.selection(selection)
        measured = tuple(selected.atom_ids if atom_ids is None else atom_ids)
        data = {}
        plane_name = "-".join(self.atom_label(atom_id) for atom_id in plane)
        for atom_id in measured:
            if atom_id in plane:
                continue
            data[f"{self.atom_label(atom_id)}__to_plane__{plane_name}"] = self.angle_to_plane_series(
                atom_id,
                plane,
                use_pbc=use_pbc,
            )
        self._append_columns(pd.DataFrame(data))
        return self

    def center_of_mass(self, selection: str | Selection) -> np.ndarray:
        selected = self.selection(selection)
        columns = [self._atom_ids.index(atom_id) for atom_id in selected.atom_ids]
        positions = self._coordinate_array()[:, columns, :]
        masses = np.asarray([self.structures.atom_record(atom_id).mass for atom_id in selected.atom_ids], dtype=np.float64)
        valid = np.isfinite(positions).all(axis=2)
        weighted = positions * masses[np.newaxis, :, np.newaxis]
        weighted[~valid] = 0.0
        weight_sums = (valid * masses[np.newaxis, :]).sum(axis=1)
        result = weighted.sum(axis=1) / weight_sums[:, np.newaxis]
        result[weight_sums == 0.0] = np.nan
        return result

    def selection_mass(self, selection: str | Selection) -> float:
        selected = self.selection(selection)
        return float(sum(self.structures.atom_record(atom_id).mass for atom_id in selected.atom_ids))

    def distance_series(self, first_atom_id: int, second_atom_id: int, *, use_pbc: bool = True) -> np.ndarray:
        values = [
            _frame_distance(frame, int(first_atom_id), int(second_atom_id), use_pbc=use_pbc)
            for frame in self.structures.frames
        ]
        return np.asarray(values, dtype=np.float64)

    def valence_angle_series(
        self,
        first_atom_id: int,
        center_atom_id: int,
        third_atom_id: int,
        *,
        use_pbc: bool = True,
    ) -> np.ndarray:
        values = []
        for frame in self.structures.frames:
            first = _frame_displacement(frame, center_atom_id, first_atom_id, use_pbc=use_pbc)
            second = _frame_displacement(frame, center_atom_id, third_atom_id, use_pbc=use_pbc)
            values.append(_angle_between(first, second))
        return np.asarray(values, dtype=np.float64)

    def angle_to_plane_series(
        self,
        atom_id: int,
        plane: tuple[int, int, int],
        *,
        use_pbc: bool = True,
    ) -> np.ndarray:
        values = []
        for frame in self.structures.frames:
            origin, plane_first, plane_second = plane
            normal = np.cross(
                _frame_displacement(frame, origin, plane_first, use_pbc=use_pbc),
                _frame_displacement(frame, origin, plane_second, use_pbc=use_pbc),
            )
            vector = _frame_displacement(frame, origin, atom_id, use_pbc=use_pbc)
            normal_norm = np.linalg.norm(normal)
            vector_norm = np.linalg.norm(vector)
            if normal_norm == 0.0 or vector_norm == 0.0 or not np.isfinite(normal_norm + vector_norm):
                values.append(np.nan)
                continue
            sine = np.clip(abs(float(np.dot(vector, normal))) / (vector_norm * normal_norm), 0.0, 1.0)
            values.append(float(np.degrees(np.arcsin(sine))))
        return np.asarray(values, dtype=np.float64)

    def to_csv(
        self,
        path: str | Path,
        *,
        include_coordinates: bool = False,
        include_direct: bool = False,
        **kwargs,
    ) -> Path:
        output = Path(path)
        self.dataframe(
            include_coordinates=include_coordinates,
            include_direct=include_direct,
        ).to_csv(output, index=False, **kwargs)
        return output

    def export(
        self,
        path: str | Path,
        *,
        include_coordinates: bool = False,
        include_direct: bool = False,
    ) -> Path:
        return export_dataframe(
            self.dataframe(
                include_coordinates=include_coordinates,
                include_direct=include_direct,
            ),
            path,
        )

    def _build_coordinate_frame(self, values: np.ndarray) -> pd.DataFrame:
        selected = values[:, self._columns, :]
        columns = pd.MultiIndex.from_tuples(
            [(atom_id, axis) for atom_id in self._atom_ids for axis in ("x", "y", "z")],
            names=("atom_id", "axis"),
        )
        return pd.DataFrame(selected.reshape(self.structures.step_count, len(columns)), columns=columns)

    def _coordinate_array(self) -> np.ndarray:
        return self._coordinates.to_numpy(dtype=np.float64).reshape(
            self.structures.step_count,
            len(self._atom_ids),
            3,
        )

    def _velocity_vectors(self, atom_ids: Sequence[int]) -> np.ndarray:
        columns = [self._atom_ids.index(int(atom_id)) for atom_id in atom_ids]
        return _finite_difference_vectors(self._coordinate_array()[:, columns, :], self.time_axis)

    def _flatten_coordinates(self, frame: pd.DataFrame, *, direct: bool) -> pd.DataFrame:
        suffixes = ("dir_1", "dir_2", "dir_3") if direct else ("x", "y", "z")
        data = {}
        for atom_id in dict.fromkeys(atom_id for atom_id, _axis in frame.columns):
            label = self._labels[int(atom_id)]
            for axis, suffix in zip(("x", "y", "z"), suffixes, strict=True):
                data[f"{label}_{suffix}"] = frame[(atom_id, axis)].to_numpy()
        return pd.DataFrame(data)

    def _append_columns(self, frame: pd.DataFrame) -> None:
        for column in frame.columns:
            self.data[column] = frame[column].to_numpy()


def _selection_tuple(selections: Selection | Sequence[Selection]) -> tuple[Selection, ...]:
    if isinstance(selections, Selection):
        return (selections,)
    result = tuple(selections)
    if not result:
        raise ValueError("At least one selection is required.")
    return result


def _selection_map(selections: Sequence[Selection]) -> dict[str, Selection]:
    result: dict[str, Selection] = {}
    for selection in selections:
        if selection.name in result:
            raise ValueError(f"Duplicate selection name: {selection.name!r}.")
        result[selection.name] = selection
    return result


def _union_atom_ids(selections: Sequence[Selection]) -> tuple[int, ...]:
    atom_ids: list[int] = []
    for selection in selections:
        for atom_id in selection.atom_ids:
            if atom_id not in atom_ids:
                atom_ids.append(atom_id)
    return tuple(atom_ids)


def _coordinate_columns(atom_ids: Iterable[int]) -> list[tuple[int, Axis]]:
    return [(int(atom_id), axis) for atom_id in atom_ids for axis in ("x", "y", "z")]


def _unwrap_direct_positions(direct_positions: np.ndarray) -> np.ndarray:
    direct = np.asarray(direct_positions, dtype=np.float64)
    unwrapped = direct.copy()
    for step in range(1, direct.shape[0]):
        delta = direct[step] - direct[step - 1]
        shift = np.round(delta)
        shift[~np.isfinite(delta)] = 0.0
        unwrapped[step] = unwrapped[step - 1] + delta - shift
    return unwrapped


def _finite_difference_vectors(values: np.ndarray, time_axis: np.ndarray) -> np.ndarray:
    vector = np.asarray(values, dtype=np.float64)
    result = np.full_like(vector, np.nan, dtype=np.float64)
    dt = np.diff(time_axis.astype(np.float64))
    dt[dt == 0.0] = np.nan
    if vector.ndim == 2:
        result[1:] = np.diff(vector, axis=0) / dt[:, np.newaxis]
    else:
        result[1:] = np.diff(vector, axis=0) / dt[:, np.newaxis, np.newaxis]
    return result


def _frame_distance(frame, first_atom_id: int, second_atom_id: int, *, use_pbc: bool) -> float:
    displacement = _frame_displacement(frame, first_atom_id, second_atom_id, use_pbc=use_pbc)
    return float(np.linalg.norm(displacement)) if np.isfinite(displacement).all() else np.nan


def _frame_displacement(frame, first_atom_id: int, second_atom_id: int, *, use_pbc: bool) -> np.ndarray:
    id_to_local = {int(atom_id): index for index, atom_id in enumerate(frame.atom_ids)}
    if first_atom_id not in id_to_local or second_atom_id not in id_to_local:
        return np.full(3, np.nan, dtype=np.float64)
    first = id_to_local[first_atom_id]
    second = id_to_local[second_atom_id]
    if use_pbc and frame.cell is not None and frame.direct_positions is not None:
        delta = frame.direct_positions[second] - frame.direct_positions[first]
        delta = delta - np.round(delta)
        return delta @ frame.cell.vectors
    return frame.positions[second] - frame.positions[first]


def _angle_between(first: np.ndarray, second: np.ndarray) -> float:
    denominator = np.linalg.norm(first) * np.linalg.norm(second)
    if denominator == 0.0 or not np.isfinite(denominator):
        return np.nan
    cosine = np.clip(float(np.dot(first, second)) / denominator, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosine)))


def _all_angle_triples(atom_ids: Sequence[int]) -> list[tuple[int, int, int]]:
    triples: list[tuple[int, int, int]] = []
    for center in atom_ids:
        for first, third in combinations((atom_id for atom_id in atom_ids if atom_id != center), 2):
            triples.append((first, center, third))
    return triples


__all__ = ["AnalysisTable"]
