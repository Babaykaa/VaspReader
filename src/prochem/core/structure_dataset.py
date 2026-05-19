"""Independent structure dataset domain object."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from prochem.core.structure import Structure
from prochem.core.structures import Structures

ArrayLike = np.ndarray


@dataclass(slots=True)
class StructureDataset:
    """Independent structures for MLIP datasets and configuration collections."""

    structures: tuple[Structure, ...] | list[Structure]
    sources: tuple[Path | None, ...] | list[Path | str | None] = field(default_factory=tuple)
    properties: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.structures = tuple(self.structures)
        if not self.structures:
            raise ValueError("StructureDataset must contain at least one structure.")

        if self.sources:
            self.sources = tuple(None if source is None else Path(source) for source in self.sources)
            if len(self.sources) != self.structure_count:
                raise ValueError("Number of dataset sources does not match number of structures.")
        else:
            self.sources = tuple(None for _ in self.structures)

    @property
    def structure_count(self) -> int:
        return len(self.structures)

    @property
    def atom_counts(self) -> ArrayLike:
        return np.asarray([structure.atom_count for structure in self.structures], dtype=np.int64)

    @property
    def source_files(self) -> tuple[Path, ...]:
        return tuple(source for source in self.sources if source is not None)

    @property
    def has_uniform_topology(self) -> bool:
        first = self.structures[0]
        return all(
            structure.atom_count == first.atom_count
            and np.array_equal(structure.species, first.species)
            for structure in self.structures[1:]
        )

    def structure(self, index: int) -> Structure:
        return self.structures[index]

    def source(self, index: int) -> Path | None:
        return self.sources[index]

    def positions_array(self, fill: float = np.nan) -> ArrayLike:
        return self._dense_vector_array("positions", fill)

    def coordinates_array(self, fill: float = np.nan) -> ArrayLike:
        return self.positions_array(fill)

    def direct_positions_array(self, fill: float = np.nan) -> ArrayLike | None:
        if all(structure.direct_positions is None for structure in self.structures):
            return None
        return self._dense_vector_array("direct_positions", fill)

    def velocities_array(self, fill: float = np.nan) -> ArrayLike | None:
        if all(structure.velocities is None for structure in self.structures):
            return None
        return self._dense_vector_array("velocities", fill)

    def forces_array(self, fill: float = np.nan) -> ArrayLike | None:
        if all(structure.forces is None for structure in self.structures):
            return None
        return self._dense_vector_array("forces", fill)

    def atom_potential_energies_array(self, fill: float = np.nan) -> ArrayLike:
        values = np.full((self.structure_count, self._max_atom_count()), fill, dtype=np.float64)
        for structure_index, structure in enumerate(self.structures):
            atom_energies = structure.atom_potential_energies_array()
            values[structure_index, : structure.atom_count] = atom_energies
        return values

    def atom_kinetic_energies_array(self, fill: float = np.nan) -> ArrayLike:
        values = np.full((self.structure_count, self._max_atom_count()), fill, dtype=np.float64)
        for structure_index, structure in enumerate(self.structures):
            atom_energies = structure.atom_kinetic_energies_array()
            values[structure_index, : structure.atom_count] = atom_energies
        return values

    def atom_total_energies_array(self, fill: float = np.nan) -> ArrayLike:
        values = np.full((self.structure_count, self._max_atom_count()), fill, dtype=np.float64)
        for structure_index, structure in enumerate(self.structures):
            atom_energies = structure.atom_total_energies_array()
            values[structure_index, : structure.atom_count] = atom_energies
        return values

    def structure_potential_energies_array(self) -> ArrayLike:
        return _optional_float_array(structure.potential_energy for structure in self.structures)

    def structure_kinetic_energies_array(self) -> ArrayLike:
        return _optional_float_array(structure.kinetic_energy for structure in self.structures)

    def structure_total_energies_array(self) -> ArrayLike:
        return _optional_float_array(structure.total_energy for structure in self.structures)

    def _dense_vector_array(self, attribute: str, fill: float) -> ArrayLike:
        values = np.full((self.structure_count, self._max_atom_count(), 3), fill, dtype=np.float64)
        for structure_index, structure in enumerate(self.structures):
            structure_values = getattr(structure, attribute)
            if structure_values is None:
                continue
            values[structure_index, : structure.atom_count] = structure_values
        return values

    def _max_atom_count(self) -> int:
        return int(np.max(self.atom_counts))

    def to_structures(self, *, strict_topology: bool = True) -> Structures:
        if strict_topology and not self.has_uniform_topology:
            raise ValueError("Dataset cannot be converted to strict structures: topology differs.")

        frames = []
        next_atom_id = 0
        for index, structure in enumerate(self.structures):
            properties = dict(structure.properties)
            if self.sources[index] is not None:
                properties["source"] = self.sources[index]
            properties["dataset_index"] = index

            if strict_topology:
                atoms = [atom.copy() for atom in structure.atoms]
            else:
                atoms = []
                for atom in structure.atoms:
                    atoms.append(atom.copy(index=next_atom_id))
                    next_atom_id += 1

            frames.append(
                Structure(
                    atoms=atoms,
                    cell=structure.cell,
                    stress=structure.stress,
                    potential_energy=structure.potential_energy,
                    kinetic_energy=structure.kinetic_energy,
                    total_energy=structure.total_energy,
                    time_fs=float(index),
                    properties=properties,
                )
            )
        return Structures(
            frames=frames,
            sources=self.sources,
            properties={
                "dataset": True,
                "source_files": self.source_files,
                "strict_topology": strict_topology,
            },
        )

    def __repr__(self) -> str:
        return (
            "StructureDataset("
            f"structures={self.structure_count}, "
            f"atom_counts={self.atom_counts.tolist()}, "
            f"uniform_topology={self.has_uniform_topology}, "
            f"sources={len(self.source_files)}"
            ")"
        )


def _optional_float_array(values) -> ArrayLike:
    return np.asarray(
        [np.nan if value is None else float(value) for value in values],
        dtype=np.float64,
    )


def _sum_optional_arrays(left: ArrayLike, right: ArrayLike) -> ArrayLike:
    values = left + right
    values[~np.isfinite(left) | ~np.isfinite(right)] = np.nan
    return values


__all__ = ["StructureDataset"]
