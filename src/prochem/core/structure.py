"""Structure domain object."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

import numpy as np

from prochem.core.atom import Atom
from prochem.core.cell import Cell

ArrayLike = np.ndarray


def _as_atom_vectors(values: ArrayLike, name: str) -> ArrayLike:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError(f"Structure {name} must have shape (atoms, 3), got {array.shape}.")
    return array


def _as_stress(values: Iterable[float] | None) -> ArrayLike:
    if values is None:
        return np.zeros(3, dtype=np.float64)
    array = np.asarray(values, dtype=np.float64)
    if array.shape == (3, 3):
        return np.diag(array).astype(np.float64)
    if array.shape != (3,):
        raise ValueError(f"Structure stress must have shape (3,), got {array.shape}.")
    return array


def _as_atom_scalars(values: ArrayLike, name: str, count: int) -> ArrayLike:
    array = np.asarray(values, dtype=np.float64)
    if array.shape != (count,):
        raise ValueError(f"Structure {name} must have shape ({count},), got {array.shape}.")
    return array


@dataclass(init=False, slots=True)
class Structure:
    """Single atomic structure or one structure-sequence frame."""

    atoms: list[Atom]
    cell: Cell | None
    stress: ArrayLike
    potential_energy: float | None
    kinetic_energy: float | None
    _total_energy: float | None = field(repr=False)
    properties: dict[str, Any] = field(default_factory=dict)
    time_fs: float | None = None

    def __init__(
        self,
        atoms: Sequence[Atom] | None = None,
        *,
        cell: Cell | ArrayLike | None = None,
        stress: Iterable[float] | None = None,
        potential_energy: float | None = None,
        kinetic_energy: float | None = None,
        total_energy: float | None = None,
        properties: dict[str, Any] | None = None,
        time_fs: float | None = None,
        species: ArrayLike | None = None,
        positions: ArrayLike | None = None,
        atom_ids: ArrayLike | None = None,
        direct_positions: ArrayLike | None = None,
        masses: ArrayLike | None = None,
        atom_potential_energies: ArrayLike | None = None,
        atom_kinetic_energies: ArrayLike | None = None,
        atom_total_energies: ArrayLike | None = None,
        velocities: ArrayLike | None = None,
        forces: ArrayLike | None = None,
    ) -> None:
        if atoms is None:
            if species is None or positions is None:
                raise ValueError("Structure requires atoms or species and positions arrays.")
            atoms = self._atoms_from_arrays(
                species=species,
                positions=positions,
                atom_ids=atom_ids,
                direct_positions=direct_positions,
                masses=masses,
                atom_potential_energies=atom_potential_energies,
                atom_kinetic_energies=atom_kinetic_energies,
                atom_total_energies=atom_total_energies,
                velocities=velocities,
                forces=forces,
            )
        self.atoms = [atom if isinstance(atom, Atom) else Atom(**atom) for atom in atoms]
        self.cell = None if cell is None else (cell if isinstance(cell, Cell) else Cell(cell))
        self.stress = _as_stress(stress)
        self.potential_energy = _optional_float(potential_energy)
        self.kinetic_energy = _optional_float(kinetic_energy)
        self._total_energy = _optional_float(total_energy)
        self.properties = {} if properties is None else dict(properties)
        self.time_fs = None if time_fs is None else float(time_fs)

    @staticmethod
    def _atoms_from_arrays(
        *,
        species: ArrayLike,
        positions: ArrayLike,
        atom_ids: ArrayLike | None,
        direct_positions: ArrayLike | None,
        masses: ArrayLike | None,
        atom_potential_energies: ArrayLike | None,
        atom_kinetic_energies: ArrayLike | None,
        atom_total_energies: ArrayLike | None,
        velocities: ArrayLike | None,
        forces: ArrayLike | None,
    ) -> list[Atom]:
        species_array = np.asarray(species, dtype=str)
        positions_array = _as_atom_vectors(positions, "positions")
        if species_array.shape[0] != positions_array.shape[0]:
            raise ValueError("Number of atom species does not match number of positions.")

        count = positions_array.shape[0]
        ids = (
            np.arange(count, dtype=np.int64)
            if atom_ids is None
            else np.asarray(atom_ids, dtype=np.int64)
        )
        if ids.shape != (count,):
            raise ValueError("Number of atom ids does not match number of atoms.")

        direct = (
            None
            if direct_positions is None
            else _as_atom_vectors(direct_positions, "direct_positions")
        )
        velocity = None if velocities is None else _as_atom_vectors(velocities, "velocities")
        force = None if forces is None else _as_atom_vectors(forces, "forces")
        mass_values = None if masses is None else np.asarray(masses, dtype=np.float64)
        if mass_values is not None and mass_values.shape != (count,):
            raise ValueError("Number of masses does not match number of atoms.")
        potential_energy_values = (
            None
            if atom_potential_energies is None
            else _as_atom_scalars(atom_potential_energies, "atom_potential_energies", count)
        )
        kinetic_energy_values = (
            None
            if atom_kinetic_energies is None
            else _as_atom_scalars(atom_kinetic_energies, "atom_kinetic_energies", count)
        )
        total_energy_values = (
            None
            if atom_total_energies is None
            else _as_atom_scalars(atom_total_energies, "atom_total_energies", count)
        )

        atoms = []
        for local_index, symbol in enumerate(species_array):
            markers = {
                key: True
                for key, available in (
                    ("direct_position", direct is not None),
                    ("velocity", velocity is not None),
                    ("force", force is not None),
                    (
                        "potential_energy",
                        potential_energy_values is not None
                        and np.isfinite(potential_energy_values[local_index]),
                    ),
                    (
                        "kinetic_energy",
                        kinetic_energy_values is not None
                        and np.isfinite(kinetic_energy_values[local_index]),
                    ),
                    (
                        "total_energy",
                        total_energy_values is not None
                        and np.isfinite(total_energy_values[local_index]),
                    ),
                )
                if available
            }
            atoms.append(
                Atom(
                    name=str(symbol),
                    index=int(ids[local_index]),
                    position=positions_array[local_index],
                    direct_position=None if direct is None else direct[local_index],
                    velocity=None if velocity is None else velocity[local_index],
                    force=None if force is None else force[local_index],
                    potential_energy=None
                    if potential_energy_values is None
                    else _optional_float(potential_energy_values[local_index]),
                    kinetic_energy=None
                    if kinetic_energy_values is None
                    else _optional_float(kinetic_energy_values[local_index]),
                    total_energy=None
                    if total_energy_values is None
                    else _optional_float(total_energy_values[local_index]),
                    mass=None if mass_values is None else float(mass_values[local_index]),
                    properties=markers,
                )
            )
        return atoms

    @property
    def atom_count(self) -> int:
        return len(self.atoms)

    @property
    def atom_ids(self) -> ArrayLike:
        return np.asarray([atom.index for atom in self.atoms], dtype=np.int64)

    @property
    def species(self) -> ArrayLike:
        return np.asarray([atom.name for atom in self.atoms], dtype=str)

    @property
    def positions(self) -> ArrayLike:
        return np.asarray([atom.position for atom in self.atoms], dtype=np.float64)

    @positions.setter
    def positions(self, values: ArrayLike) -> None:
        array = _as_atom_vectors(values, "positions")
        if array.shape[0] != self.atom_count:
            raise ValueError("Number of positions does not match number of atoms.")
        for atom, value in zip(self.atoms, array, strict=True):
            atom.position = value.copy()

    @property
    def direct_positions(self) -> ArrayLike | None:
        if not self.atoms:
            return np.empty((0, 3), dtype=np.float64)
        values = np.asarray([atom.direct_position for atom in self.atoms], dtype=np.float64)
        if np.allclose(values, 0.0) and not any(
            "direct_position" in atom.properties for atom in self.atoms
        ):
            return None
        return values

    @property
    def velocities(self) -> ArrayLike | None:
        if not self.atoms:
            return np.empty((0, 3), dtype=np.float64)
        values = np.asarray([atom.velocity for atom in self.atoms], dtype=np.float64)
        if np.allclose(values, 0.0) and not any(
            "velocity" in atom.properties for atom in self.atoms
        ):
            return None
        return values

    @property
    def forces(self) -> ArrayLike | None:
        if not self.atoms:
            return np.empty((0, 3), dtype=np.float64)
        values = np.asarray([atom.force for atom in self.atoms], dtype=np.float64)
        if np.allclose(values, 0.0) and not any(
            "force" in atom.properties for atom in self.atoms
        ):
            return None
        return values

    @property
    def masses(self) -> ArrayLike:
        return np.asarray([atom.mass for atom in self.atoms], dtype=np.float64)

    def positions_array(self) -> ArrayLike:
        return self.positions

    def coordinates_array(self) -> ArrayLike:
        return self.positions_array()

    def direct_positions_array(self) -> ArrayLike | None:
        return self.direct_positions

    def velocities_array(self) -> ArrayLike | None:
        return self.velocities

    def forces_array(self) -> ArrayLike | None:
        return self.forces

    def atom_potential_energies_array(self) -> ArrayLike:
        return _optional_float_array(atom.potential_energy for atom in self.atoms)

    def atom_kinetic_energies_array(self) -> ArrayLike:
        return _optional_float_array(_atom_kinetic_energy(atom) for atom in self.atoms)

    def atom_total_energies_array(self) -> ArrayLike:
        return _optional_float_array(_atom_total_energy(atom) for atom in self.atoms)

    @property
    def total_energy(self) -> float | None:
        if self._total_energy is not None:
            return self._total_energy
        if self.potential_energy is None or self.kinetic_energy is None:
            return None
        return self.potential_energy + self.kinetic_energy

    @total_energy.setter
    def total_energy(self, value: float | None) -> None:
        self._total_energy = _optional_float(value)

    def copy(self, **changes: Any) -> "Structure":
        params = {
            "atoms": [atom.copy() for atom in self.atoms],
            "cell": self.cell,
            "stress": self.stress.copy(),
            "potential_energy": self.potential_energy,
            "kinetic_energy": self.kinetic_energy,
            "total_energy": self._total_energy,
            "properties": dict(self.properties),
            "time_fs": self.time_fs,
        }
        params.update(changes)
        return Structure(**params)

    def __repr__(self) -> str:
        species_counts = _species_counts(self.atoms)
        lines = [
            "Structure(",
            f"  atoms={self.atom_count}, species={species_counts}",
            f"  potential_energy={_format_float(self.potential_energy)}, "
            f"kinetic_energy={_format_float(self.kinetic_energy)}, "
            f"total_energy={_format_float(self.total_energy)}",
            f"  cell={_cell_summary(self.cell)}, stress={_format_vector(self.stress)}, "
            f"time_fs={None if self.time_fs is None else _format_float(self.time_fs)}",
            "  atoms_preview=[",
        ]
        preview_count = min(self.atom_count, 6)
        for atom in self.atoms[:preview_count]:
            lines.append(f"    {atom!r},")
        if self.atom_count > preview_count:
            lines.append(f"    ... {self.atom_count - preview_count} more atoms")
        lines.extend(["  ]", ")"])
        return "\n".join(lines)


def _species_counts(atoms: Sequence[Atom]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for atom in atoms:
        counts[atom.name] = counts.get(atom.name, 0) + 1
    return counts


def _cell_summary(cell: Cell | None) -> str:
    if cell is None:
        return "None"
    lengths = np.linalg.norm(cell.vectors, axis=1)
    return (
        "Cell("
        f"lengths={_format_vector(lengths)}, "
        f"pbc={cell.pbc}, units='{cell.units}'"
        ")"
    )


def _optional_float(value: float | None) -> float | None:
    if value is None:
        return None
    result = float(value)
    return None if np.isnan(result) else result


def _optional_float_array(values: Iterable[float | None]) -> ArrayLike:
    return np.asarray(
        [np.nan if value is None else float(value) for value in values],
        dtype=np.float64,
    )


def _atom_kinetic_energy(atom: Atom) -> float | None:
    if atom.kinetic_energy is not None:
        return atom.kinetic_energy
    if "velocity" not in atom.properties:
        return None
    return atom.kinetic_energy_from_velocity()


def _atom_total_energy(atom: Atom) -> float | None:
    if atom._total_energy is not None:
        return atom._total_energy
    potential = atom.potential_energy
    kinetic = _atom_kinetic_energy(atom)
    if potential is None or kinetic is None:
        return None
    return potential + kinetic


def _sum_optional_arrays(left: ArrayLike, right: ArrayLike) -> ArrayLike:
    values = left + right
    values[~np.isfinite(left) | ~np.isfinite(right)] = np.nan
    return values


def _format_float(value: float | None) -> str:
    if value is None:
        return "None"
    return f"{float(value):.6g}"


def _format_vector(values: Iterable[float]) -> str:
    return "(" + ", ".join(_format_float(value) for value in values) + ")"


__all__ = ["Structure"]
