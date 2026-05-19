"""Ordered collection of structure frames."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

import numpy as np

from prochem.core.atom import Atom
from prochem.core.cell import Cell
from prochem.core.structure import Structure

ArrayLike = np.ndarray
Timestep = float | dict[int, float] | None


def _as_step_atom_vectors(values: ArrayLike, name: str) -> ArrayLike:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim == 2:
        array = array[np.newaxis, :, :]
    if array.ndim != 3 or array.shape[2] != 3:
        raise ValueError(f"Structures {name} must have shape (steps, atoms, 3), got {array.shape}.")
    return array


@dataclass(slots=True)
class Structures:
    """Ordered sequence of structure frames."""

    frames: tuple[Structure, ...] | list[Structure]
    timestep: Timestep = None
    sources: tuple[Path | None, ...] | list[Path | str | None] = field(default_factory=tuple)
    properties: dict[str, Any] = field(default_factory=dict)
    _atom_registry: tuple[Atom, ...] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.frames = tuple(self.frames)
        if not self.frames:
            raise ValueError("Structures must contain at least one structure frame.")
        if self.sources:
            self.sources = tuple(None if source is None else Path(source) for source in self.sources)
            if len(self.sources) != self.step_count:
                raise ValueError("Number of structure sources does not match number of frames.")
        else:
            self.sources = tuple(
                _source_from_properties(frame.properties) for frame in self.frames
            )
        self._atom_registry = tuple(_build_atom_registry(self.frames))
        known_ids = {atom.index for atom in self._atom_registry}
        for index, frame in enumerate(self.frames):
            unknown_ids = set(frame.atom_ids.tolist()) - known_ids
            if unknown_ids:
                raise ValueError(
                    f"Frame {index} references unknown atom ids: {sorted(unknown_ids)}."
                )
            for atom in frame.atoms:
                record = self.atom_record(atom.index)
                if record.name != atom.name:
                    raise ValueError(
                        f"Frame {index} species for atom id {atom.index} is {atom.name}, "
                        f"expected {record.name}."
                    )

    @classmethod
    def from_arrays(
        cls,
        *,
        species: ArrayLike,
        positions: ArrayLike,
        cell: Cell | ArrayLike | Iterable[Cell | ArrayLike] | None = None,
        direct_positions: Optional[ArrayLike] = None,
        masses: Optional[ArrayLike] = None,
        atom_potential_energies: Optional[ArrayLike] = None,
        atom_kinetic_energies: Optional[ArrayLike] = None,
        atom_total_energies: Optional[ArrayLike] = None,
        structure_potential_energies: Optional[ArrayLike] = None,
        structure_kinetic_energies: Optional[ArrayLike] = None,
        structure_total_energies: Optional[ArrayLike] = None,
        forces: Optional[ArrayLike] = None,
        velocities: Optional[ArrayLike] = None,
        time_fs: Optional[ArrayLike] = None,
        timestep: Timestep = None,
        sources: tuple[Path | None, ...] | list[Path | str | None] = (),
        properties: Optional[dict[str, Any]] = None,
    ) -> "Structures":
        species = np.asarray(species, dtype=str)
        positions = _as_step_atom_vectors(positions, "positions")
        direct_positions = (
            None
            if direct_positions is None
            else _as_step_atom_vectors(direct_positions, "direct_positions")
        )
        forces = None if forces is None else _as_step_atom_vectors(forces, "forces")
        velocities = (
            None
            if velocities is None
            else _as_step_atom_vectors(velocities, "velocities")
        )
        masses = None if masses is None else np.asarray(masses, dtype=np.float64)
        atom_potential_energies = (
            None
            if atom_potential_energies is None
            else _as_step_atom_scalars(
                atom_potential_energies,
                "atom_potential_energies",
                positions.shape[0],
                positions.shape[1],
            )
        )
        atom_kinetic_energies = (
            None
            if atom_kinetic_energies is None
            else _as_step_atom_scalars(
                atom_kinetic_energies,
                "atom_kinetic_energies",
                positions.shape[0],
                positions.shape[1],
            )
        )
        atom_total_energies = (
            None
            if atom_total_energies is None
            else _as_step_atom_scalars(
                atom_total_energies,
                "atom_total_energies",
                positions.shape[0],
                positions.shape[1],
            )
        )
        structure_potential_energies = _as_step_scalars(
            structure_potential_energies,
            "structure_potential_energies",
            positions.shape[0],
        )
        structure_kinetic_energies = _as_step_scalars(
            structure_kinetic_energies,
            "structure_kinetic_energies",
            positions.shape[0],
        )
        structure_total_energies = _as_step_scalars(
            structure_total_energies,
            "structure_total_energies",
            positions.shape[0],
        )
        time_fs = None if time_fs is None else np.asarray(time_fs, dtype=np.float64)
        cells = _expand_cells(cell, positions.shape[0])
        atom_ids = np.arange(species.shape[0], dtype=np.int64)

        frames = []
        for step in range(positions.shape[0]):
            frames.append(
                Structure(
                    species=species,
                    positions=positions[step],
                    atom_ids=atom_ids,
                    cell=cells[step],
                    direct_positions=None if direct_positions is None else direct_positions[step],
                    masses=masses,
                    atom_potential_energies=None
                    if atom_potential_energies is None
                    else atom_potential_energies[step],
                    atom_kinetic_energies=None
                    if atom_kinetic_energies is None
                    else atom_kinetic_energies[step],
                    atom_total_energies=None
                    if atom_total_energies is None
                    else atom_total_energies[step],
                    velocities=None if velocities is None else velocities[step],
                    forces=None if forces is None else forces[step],
                    potential_energy=None
                    if structure_potential_energies is None
                    else _optional_scalar(structure_potential_energies[step]),
                    kinetic_energy=None
                    if structure_kinetic_energies is None
                    else _optional_scalar(structure_kinetic_energies[step]),
                    total_energy=None
                    if structure_total_energies is None
                    else _optional_scalar(structure_total_energies[step]),
                    time_fs=None if time_fs is None else float(time_fs[step]),
                )
            )
        return cls(
            frames=frames,
            timestep=timestep,
            sources=sources,
            properties=properties or {},
        )

    @property
    def step_count(self) -> int:
        return len(self.frames)

    @property
    def atom_count(self) -> int:
        return len(self._atom_registry)

    @property
    def species(self) -> ArrayLike:
        return np.asarray([atom.name for atom in self._atom_registry], dtype=str)

    @property
    def atom_ids(self) -> tuple[int, ...]:
        return tuple(atom.index for atom in self._atom_registry)

    @property
    def masses(self) -> ArrayLike:
        return np.asarray([atom.mass for atom in self._atom_registry], dtype=np.float64)

    @property
    def source_files(self) -> tuple[Path, ...]:
        return tuple(source for source in self.sources if source is not None)

    @property
    def positions(self) -> ArrayLike:
        return self.positions_array()

    @property
    def direct_positions(self) -> ArrayLike | None:
        if any(frame.direct_positions is None for frame in self.frames):
            return None
        return self.direct_positions_array()

    @property
    def forces(self) -> ArrayLike | None:
        if any(frame.forces is None for frame in self.frames):
            return None
        return self.forces_array()

    @property
    def velocities(self) -> ArrayLike | None:
        if any(frame.velocities is None for frame in self.frames):
            return None
        return self.velocities_array()

    @property
    def time_fs(self) -> ArrayLike | None:
        if any(frame.time_fs is None for frame in self.frames):
            if self.timestep is None:
                return None
            return _time_from_timestep(self.step_count, self.timestep)
        return np.asarray([frame.time_fs for frame in self.frames], dtype=np.float64)

    def frame(self, index: int) -> Structure:
        return self.frames[index]

    def source(self, index: int) -> Path | None:
        return self.sources[index]

    def atom_record(self, atom_id: int) -> Atom:
        for atom in self._atom_registry:
            if atom.index == atom_id:
                return atom
        raise KeyError(atom_id)

    def atom_columns(self, atom_ids: Optional[Sequence[int]] = None) -> list[int]:
        selected = (
            self.atom_ids
            if atom_ids is None
            else tuple(int(atom_id) for atom_id in atom_ids)
        )
        id_to_column = self._id_to_column()
        return [id_to_column[atom_id] for atom_id in selected]

    def presence_mask(self) -> ArrayLike:
        mask = np.zeros((self.step_count, self.atom_count), dtype=bool)
        id_to_column = self._id_to_column()
        for step, frame in enumerate(self.frames):
            for atom_id in frame.atom_ids:
                mask[step, id_to_column[int(atom_id)]] = True
        return mask

    def positions_array(self, fill: float = np.nan) -> ArrayLike:
        return self._dense_vector_array("positions", fill)

    def coordinates_array(self, fill: float = np.nan) -> ArrayLike:
        return self.positions_array(fill)

    def direct_positions_array(self, fill: float = np.nan) -> ArrayLike | None:
        if any(frame.direct_positions is None for frame in self.frames):
            return None
        return self._dense_vector_array("direct_positions", fill)

    def velocities_array(self, fill: float = np.nan) -> ArrayLike | None:
        if any(frame.velocities is None for frame in self.frames):
            return None
        return self._dense_vector_array("velocities", fill)

    def forces_array(self, fill: float = np.nan) -> ArrayLike | None:
        if any(frame.forces is None for frame in self.frames):
            return None
        return self._dense_vector_array("forces", fill)

    def atom_potential_energies_array(self, fill: float = np.nan) -> ArrayLike:
        values = np.full((self.step_count, self.atom_count), fill, dtype=np.float64)
        id_to_column = self._id_to_column()
        for step, frame in enumerate(self.frames):
            frame_values = frame.atom_potential_energies_array()
            for local_index, atom_id in enumerate(frame.atom_ids):
                values[step, id_to_column[int(atom_id)]] = frame_values[local_index]
        return values

    def atom_kinetic_energies_array(self, fill: float = np.nan) -> ArrayLike:
        values = np.full((self.step_count, self.atom_count), fill, dtype=np.float64)
        id_to_column = self._id_to_column()
        for step, frame in enumerate(self.frames):
            frame_values = frame.atom_kinetic_energies_array()
            for local_index, atom_id in enumerate(frame.atom_ids):
                values[step, id_to_column[int(atom_id)]] = frame_values[local_index]
        return values

    def atom_total_energies_array(self, fill: float = np.nan) -> ArrayLike:
        values = np.full((self.step_count, self.atom_count), fill, dtype=np.float64)
        id_to_column = self._id_to_column()
        for step, frame in enumerate(self.frames):
            frame_values = frame.atom_total_energies_array()
            for local_index, atom_id in enumerate(frame.atom_ids):
                values[step, id_to_column[int(atom_id)]] = frame_values[local_index]
        return values

    def structure_potential_energies_array(self) -> ArrayLike:
        return _optional_float_array(frame.potential_energy for frame in self.frames)

    def structure_kinetic_energies_array(self) -> ArrayLike:
        return _optional_float_array(frame.kinetic_energy for frame in self.frames)

    def structure_total_energies_array(self) -> ArrayLike:
        return _optional_float_array(frame.total_energy for frame in self.frames)

    def with_frames(self, frames: Sequence[Structure], **changes: Any) -> "Structures":
        frame_tuple = tuple(frames)
        params = {
            "frames": frame_tuple,
            "timestep": self.timestep,
            "sources": self.sources if len(frame_tuple) == len(self.sources) else (),
            "properties": dict(self.properties),
        }
        params.update(changes)
        return Structures(**params)

    def _dense_vector_array(self, attribute: str, fill: float) -> ArrayLike:
        values = np.full((self.step_count, self.atom_count, 3), fill, dtype=np.float64)
        id_to_column = self._id_to_column()
        for step, frame in enumerate(self.frames):
            frame_values = getattr(frame, attribute)
            if frame_values is None:
                continue
            for local_index, atom_id in enumerate(frame.atom_ids):
                values[step, id_to_column[int(atom_id)]] = frame_values[local_index]
        return values

    def _id_to_column(self) -> dict[int, int]:
        return {atom.index: index for index, atom in enumerate(self._atom_registry)}

    def __repr__(self) -> str:
        time = self.time_fs
        time_summary = (
            "None"
            if time is None
            else f"({_format_float(float(time[0]))} .. {_format_float(float(time[-1]))})"
        )
        return (
            "Structures("
            f"frames={self.step_count}, atoms={self.atom_count}, "
            f"species={_species_counts(self._atom_registry)}, "
            f"timestep={self.timestep!r}, time_fs={time_summary}, "
            f"sources={len(self.source_files)}"
            ")"
        )


def _build_atom_registry(frames: Sequence[Structure]) -> tuple[Atom, ...]:
    records: dict[int, Atom] = {}
    for frame in frames:
        for local_index, atom in enumerate(frame.atoms):
            if atom.index in records:
                continue
            records[atom.index] = atom.copy(position=np.zeros(3), direct_position=np.zeros(3))
            records[atom.index].properties["initial_index"] = local_index
    return tuple(records[atom_id] for atom_id in sorted(records))


def _source_from_properties(properties: dict[str, Any]) -> Path | None:
    source = properties.get("source")
    return None if source is None else Path(source)


def _as_step_atom_scalars(
    values: ArrayLike,
    name: str,
    step_count: int,
    atom_count: int,
) -> ArrayLike:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim == 1:
        array = np.broadcast_to(array, (step_count, atom_count)).copy()
    if array.shape != (step_count, atom_count):
        raise ValueError(
            f"Structures {name} must have shape "
            f"({step_count}, {atom_count}), got {array.shape}."
        )
    return array


def _as_step_scalars(
    values: ArrayLike | None,
    name: str,
    step_count: int,
) -> ArrayLike | None:
    if values is None:
        return None
    array = np.asarray(values, dtype=np.float64)
    if array.shape != (step_count,):
        raise ValueError(
            f"Structures {name} must have shape ({step_count},), got {array.shape}."
        )
    return array


def _optional_scalar(value: float | None) -> float | None:
    if value is None:
        return None
    result = float(value)
    return None if np.isnan(result) else result


def _optional_float_array(values: Iterable[float | None]) -> ArrayLike:
    return np.asarray(
        [np.nan if value is None else float(value) for value in values],
        dtype=np.float64,
    )


def _sum_optional_arrays(left: ArrayLike, right: ArrayLike) -> ArrayLike:
    values = left + right
    values[~np.isfinite(left) | ~np.isfinite(right)] = np.nan
    return values


def _species_counts(atoms: Sequence[Atom]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for atom in atoms:
        counts[atom.name] = counts.get(atom.name, 0) + 1
    return counts


def _format_float(value: float) -> str:
    return f"{float(value):.6g}"


def _expand_cells(
    cell: Cell | ArrayLike | Iterable[Cell | ArrayLike] | None,
    step_count: int,
) -> tuple[Cell | None, ...]:
    if cell is None:
        return tuple(None for _ in range(step_count))
    if isinstance(cell, Cell):
        return tuple(cell for _ in range(step_count))
    if isinstance(cell, np.ndarray):
        if cell.shape == (3, 3):
            parsed = Cell(cell)
            return tuple(parsed for _ in range(step_count))
        if cell.shape == (step_count, 3, 3):
            return tuple(Cell(cell[step]) for step in range(step_count))
    array = np.asarray(cell, dtype=object)
    if array.shape == (3, 3):
        parsed = Cell(np.asarray(cell, dtype=np.float64))
        return tuple(parsed for _ in range(step_count))
    if array.shape == (step_count, 3, 3):
        numeric_cells = np.asarray(cell, dtype=np.float64)
        return tuple(Cell(numeric_cells[step]) for step in range(step_count))
    cells = tuple(item if isinstance(item, Cell) else Cell(item) for item in cell)
    if len(cells) != step_count:
        raise ValueError("Number of cells does not match number of structure frames.")
    return cells


def _time_from_timestep(step_count: int, timestep: Timestep) -> ArrayLike | None:
    if timestep is None:
        return None
    if isinstance(timestep, int | float):
        return np.arange(step_count, dtype=np.float64) * float(timestep)

    values = np.zeros(step_count, dtype=np.float64)
    starts = sorted((int(step), float(value)) for step, value in timestep.items())
    if not starts or starts[0][0] != 0:
        starts.insert(0, (0, starts[0][1] if starts else 1.0))
    for segment_index, (start, step_size) in enumerate(starts):
        end = starts[segment_index + 1][0] if segment_index + 1 < len(starts) else step_count
        if start >= step_count:
            continue
        if start > 0:
            values[start] = values[start - 1] + step_size
        for step in range(start + 1, min(end, step_count)):
            values[step] = values[step - 1] + step_size
    return values


__all__ = ["Structures", "Timestep"]
