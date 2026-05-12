"""Backend-independent data models used by parsers, analysis and frontends."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2026 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

import numpy as np

ArrayLike = np.ndarray


@dataclass(slots=True)
class CalculationError:
    """Error state for parser results."""

    exist: bool = False
    message: str = ""


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


@dataclass(frozen=True, slots=True)
class AtomRecord:
    """Stable atom identity across a trajectory, including deletion/restart cases."""

    atom_id: int
    species: str
    initial_index: int
    mass: Optional[float] = None
    properties: dict[str, Any] = field(default_factory=dict)


Atom = AtomRecord


@dataclass(slots=True)
class Structure:
    """Single atomic structure or one trajectory frame."""

    species: ArrayLike
    positions: ArrayLike
    atom_ids: Optional[ArrayLike] = None
    cell: Optional[Cell] = None
    direct_positions: Optional[ArrayLike] = None
    masses: Optional[ArrayLike] = None
    velocities: Optional[ArrayLike] = None
    forces: Optional[ArrayLike] = None
    stress: Optional[ArrayLike] = None
    time_fs: Optional[float] = None
    properties: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.species = np.asarray(self.species, dtype=str)
        self.positions = _as_atom_vectors(self.positions, "positions")
        if self.positions.shape[0] != self.species.shape[0]:
            raise ValueError("Number of atom species does not match number of positions.")
        if self.atom_ids is None:
            self.atom_ids = np.arange(self.atom_count, dtype=np.int64)
        else:
            self.atom_ids = np.asarray(self.atom_ids, dtype=np.int64)
            if self.atom_ids.shape[0] != self.atom_count:
                raise ValueError("Number of atom ids does not match number of atoms.")
        if self.direct_positions is not None:
            self.direct_positions = _as_atom_vectors(self.direct_positions, "direct_positions")
        if self.masses is not None:
            self.masses = np.asarray(self.masses, dtype=np.float64)
            if self.masses.shape[0] != self.atom_count:
                raise ValueError("Number of masses does not match number of atoms.")
        if self.velocities is not None:
            self.velocities = _as_atom_vectors(self.velocities, "velocities")
        if self.forces is not None:
            self.forces = _as_atom_vectors(self.forces, "forces")
        if self.stress is not None:
            self.stress = np.asarray(self.stress, dtype=np.float64)

    @property
    def atom_count(self) -> int:
        """Number of atoms in the structure."""
        return int(self.species.shape[0])


@dataclass(slots=True)
class Trajectory:
    """Atomic trajectory represented as an ordered collection of structures."""

    frames: tuple[Structure, ...] | list[Structure]
    atom_registry: Optional[tuple[AtomRecord, ...] | list[AtomRecord]] = None
    timestep_fs: Optional[float] = None
    properties: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.frames = tuple(self.frames)
        if not self.frames:
            raise ValueError("Trajectory must contain at least one structure frame.")

        if self.atom_registry is None:
            self.atom_registry = _build_atom_registry(self.frames)
        else:
            self.atom_registry = tuple(self.atom_registry)

        known_ids = {record.atom_id for record in self.atom_registry}
        for index, frame in enumerate(self.frames):
            unknown_ids = set(frame.atom_ids.tolist()) - known_ids
            if unknown_ids:
                raise ValueError(f"Frame {index} references unknown atom ids: {sorted(unknown_ids)}.")
            for species, atom_id in zip(frame.species, frame.atom_ids, strict=True):
                record = self.atom_record(int(atom_id))
                if record.species != str(species):
                    raise ValueError(
                        f"Frame {index} species for atom id {atom_id} is {species}, "
                        f"expected {record.species}."
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
        forces: Optional[ArrayLike] = None,
        velocities: Optional[ArrayLike] = None,
        time_fs: Optional[ArrayLike] = None,
        timestep_fs: Optional[float] = None,
        properties: Optional[dict[str, Any]] = None,
    ) -> "Trajectory":
        """Build a trajectory from step-major arrays."""
        species = np.asarray(species, dtype=str)
        positions = _as_step_atom_vectors(positions, "positions")
        direct_positions = (
            None
            if direct_positions is None
            else _as_step_atom_vectors(direct_positions, "direct_positions")
        )
        forces = None if forces is None else _as_step_atom_vectors(forces, "forces")
        velocities = None if velocities is None else _as_step_atom_vectors(velocities, "velocities")
        masses = None if masses is None else np.asarray(masses, dtype=np.float64)
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
                    velocities=None if velocities is None else velocities[step],
                    forces=None if forces is None else forces[step],
                    time_fs=None if time_fs is None else float(time_fs[step]),
                )
            )
        return cls(frames=frames, timestep_fs=timestep_fs, properties=properties or {})

    @property
    def step_count(self) -> int:
        """Number of trajectory frames."""
        return len(self.frames)

    @property
    def atom_count(self) -> int:
        """Number of stable atoms in the trajectory registry."""
        return len(self.atom_registry)

    @property
    def species(self) -> ArrayLike:
        """Atom species in stable registry order."""
        return np.asarray([record.species for record in self.atom_registry], dtype=str)

    @property
    def masses(self) -> Optional[ArrayLike]:
        """Atomic masses when present."""
        masses = [record.mass for record in self.atom_registry]
        if any(mass is None for mass in masses):
            return None
        return np.asarray(masses, dtype=np.float64)

    @property
    def positions(self) -> ArrayLike:
        """Dense Cartesian positions with missing atoms filled by NaN."""
        return self.positions_array()

    @property
    def direct_positions(self) -> Optional[ArrayLike]:
        """Dense direct positions with missing atoms filled by NaN, when present."""
        if any(frame.direct_positions is None for frame in self.frames):
            return None
        return self.direct_positions_array()

    @property
    def forces(self) -> Optional[ArrayLike]:
        """Dense forces with missing atoms filled by NaN, when present."""
        if any(frame.forces is None for frame in self.frames):
            return None
        return self.forces_array()

    @property
    def time_fs(self) -> Optional[ArrayLike]:
        """Frame times in femtoseconds, when present."""
        if any(frame.time_fs is None for frame in self.frames):
            return None
        return np.asarray([frame.time_fs for frame in self.frames], dtype=np.float64)

    def frame(self, index: int) -> Structure:
        """Return one trajectory frame."""
        return self.frames[index]

    def atom_record(self, atom_id: int) -> AtomRecord:
        """Return atom metadata by stable atom id."""
        for record in self.atom_registry:
            if record.atom_id == atom_id:
                return record
        raise KeyError(atom_id)

    def presence_mask(self) -> ArrayLike:
        """Boolean array with shape (steps, registry_atoms)."""
        mask = np.zeros((self.step_count, self.atom_count), dtype=bool)
        id_to_column = self._id_to_column()
        for step, frame in enumerate(self.frames):
            for atom_id in frame.atom_ids:
                mask[step, id_to_column[int(atom_id)]] = True
        return mask

    def positions_array(self, fill: float = np.nan) -> ArrayLike:
        """Cartesian positions with shape (steps, registry_atoms, 3)."""
        return self._dense_vector_array("positions", fill)

    def direct_positions_array(self, fill: float = np.nan) -> ArrayLike:
        """Direct positions with shape (steps, registry_atoms, 3)."""
        return self._dense_vector_array("direct_positions", fill)

    def forces_array(self, fill: float = np.nan) -> ArrayLike:
        """Forces with shape (steps, registry_atoms, 3)."""
        return self._dense_vector_array("forces", fill)

    def with_frames(self, frames: Sequence[Structure], **changes: Any) -> "Trajectory":
        """Return a new trajectory with the same registry and selected fields changed."""
        params = {
            "frames": tuple(frames),
            "atom_registry": self.atom_registry,
            "timestep_fs": self.timestep_fs,
            "properties": dict(self.properties),
        }
        params.update(changes)
        return Trajectory(**params)

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
        return {record.atom_id: index for index, record in enumerate(self.atom_registry)}


@dataclass(slots=True)
class Calculation:
    """Unified calculation object returned by parser backends."""

    source: Path | str
    engine: str
    trajectory: Optional[Trajectory] = None
    properties: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: CalculationError = field(default_factory=CalculationError)

    def __post_init__(self) -> None:
        self.source = Path(self.source)
        self.engine = self.engine.lower()

    @property
    def name(self) -> str:
        """Source file or folder name."""
        return self.source.name

    @property
    def directory(self) -> Path:
        """Source parent directory."""
        return self.source.parent

    @property
    def structure(self) -> Optional[Structure]:
        """First structure frame, when available."""
        if self.trajectory is None:
            return None
        return self.trajectory.frame(0)

    @property
    def step_count(self) -> int:
        """Number of parsed frames."""
        return 0 if self.trajectory is None else self.trajectory.step_count

    @property
    def atom_count(self) -> int:
        """Number of atoms."""
        return 0 if self.trajectory is None else self.trajectory.atom_count


def _as_atom_vectors(values: ArrayLike, name: str) -> ArrayLike:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError(f"Structure {name} must have shape (atoms, 3), got {array.shape}.")
    return array


def _as_step_atom_vectors(values: ArrayLike, name: str) -> ArrayLike:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim == 2:
        array = array[np.newaxis, :, :]
    if array.ndim != 3 or array.shape[2] != 3:
        raise ValueError(
            f"Trajectory {name} must have shape (steps, atoms, 3), got {array.shape}."
        )
    return array


def _build_atom_registry(frames: Sequence[Structure]) -> tuple[AtomRecord, ...]:
    records: dict[int, AtomRecord] = {}
    for frame in frames:
        for local_index, atom_id in enumerate(frame.atom_ids):
            atom_id = int(atom_id)
            if atom_id in records:
                continue
            mass = None
            if frame.masses is not None:
                mass = float(frame.masses[local_index])
            records[atom_id] = AtomRecord(
                atom_id=atom_id,
                species=str(frame.species[local_index]),
                initial_index=local_index,
                mass=mass,
            )
    return tuple(records[atom_id] for atom_id in sorted(records))


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
        raise ValueError("Number of cells does not match number of trajectory frames.")
    return cells
