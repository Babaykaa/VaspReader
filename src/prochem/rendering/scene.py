"""Scene DTOs and converters shared by Qt, Jupyter and web renderers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Iterable, Sequence

import numpy as np

from prochem.core.geometry import distance
from prochem.core.models import Calculation, Structure, StructureDataset, Trajectory
from prochem.core.periodic_table import covalent_radius, element
from prochem.rendering.primitives import (
    AtomPrimitive,
    AxesPrimitive,
    BondPrimitive,
    CellPrimitive,
    Color,
    PrimitiveSet,
    Vec3,
)


@dataclass(frozen=True, slots=True)
class SceneData:
    frames: tuple[PrimitiveSet, ...]
    name: str = ""
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "frames", tuple(self.frames))

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    def frame(self, index: int) -> PrimitiveSet:
        """Return one renderable frame."""
        return self.frames[index]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly nested representation."""
        return asdict(self)


def scene_from_structure(
    structure: Structure,
    *,
    name: str = "",
    include_bonds: bool = True,
    include_cell: bool = True,
    include_axes: bool = True,
    atom_radius_scale: float = 0.35,
    bond_radius: float = 0.08,
    bond_scale: float = 1.25,
    max_atoms_for_bonds: int = 500,
    metadata: dict[str, object] | None = None,
) -> SceneData:
    """Convert one structure into backend-independent scene data."""
    return SceneData(
        frames=(
            primitive_set_from_structure(
                structure,
                include_bonds=include_bonds,
                include_cell=include_cell,
                include_axes=include_axes,
                atom_radius_scale=atom_radius_scale,
                bond_radius=bond_radius,
                bond_scale=bond_scale,
                max_atoms_for_bonds=max_atoms_for_bonds,
            ),
        ),
        name=name,
        metadata={
            "kind": "structure",
            "atom_count": structure.atom_count,
            **(metadata or {}),
        },
    )


def scene_from_trajectory(
    trajectory: Trajectory,
    *,
    frame_indices: Sequence[int] | None = None,
    name: str = "",
    include_bonds: bool = True,
    include_cell: bool = True,
    include_axes: bool = True,
    atom_radius_scale: float = 0.35,
    bond_radius: float = 0.08,
    bond_scale: float = 1.25,
    max_atoms_for_bonds: int = 500,
    metadata: dict[str, object] | None = None,
) -> SceneData:
    """Convert selected trajectory frames into scene data."""
    indices = tuple(range(trajectory.step_count)) if frame_indices is None else tuple(frame_indices)
    frames = tuple(
        primitive_set_from_structure(
            trajectory.frame(index),
            include_bonds=include_bonds,
            include_cell=include_cell,
            include_axes=include_axes,
            atom_radius_scale=atom_radius_scale,
            bond_radius=bond_radius,
            bond_scale=bond_scale,
            max_atoms_for_bonds=max_atoms_for_bonds,
            metadata={
                "frame_index": index,
                "time_fs": trajectory.frame(index).time_fs,
            },
        )
        for index in indices
    )
    return SceneData(
        frames=frames,
        name=name,
        metadata={
            "kind": "trajectory",
            "frame_indices": indices,
            "step_count": trajectory.step_count,
            "atom_count": trajectory.atom_count,
            **(metadata or {}),
        },
    )


def scene_from_dataset(
    dataset: StructureDataset,
    *,
    structure_indices: Sequence[int] | None = None,
    name: str = "",
    include_bonds: bool = True,
    include_cell: bool = True,
    include_axes: bool = True,
    atom_radius_scale: float = 0.35,
    bond_radius: float = 0.08,
    bond_scale: float = 1.25,
    max_atoms_for_bonds: int = 500,
    metadata: dict[str, object] | None = None,
) -> SceneData:
    """Convert independent dataset structures into scene frames."""
    indices = (
        tuple(range(dataset.structure_count))
        if structure_indices is None
        else tuple(structure_indices)
    )
    frames = tuple(
        primitive_set_from_structure(
            dataset.structure(index),
            include_bonds=include_bonds,
            include_cell=include_cell,
            include_axes=include_axes,
            atom_radius_scale=atom_radius_scale,
            bond_radius=bond_radius,
            bond_scale=bond_scale,
            max_atoms_for_bonds=max_atoms_for_bonds,
            metadata={
                "dataset_index": index,
                "source": None if dataset.source(index) is None else str(dataset.source(index)),
            },
        )
        for index in indices
    )
    return SceneData(
        frames=frames,
        name=name,
        metadata={
            "kind": "dataset",
            "structure_indices": indices,
            "structure_count": dataset.structure_count,
            **(metadata or {}),
        },
    )


def scene_from_calculation(
    calculation: Calculation,
    *,
    name: str | None = None,
    frame_indices: Sequence[int] | None = None,
    include_bonds: bool = True,
    include_cell: bool = True,
    include_axes: bool = True,
    atom_radius_scale: float = 0.35,
    bond_radius: float = 0.08,
    bond_scale: float = 1.25,
    max_atoms_for_bonds: int = 500,
) -> SceneData:
    """Convert a parsed calculation to scene data using its best structure container."""
    scene_name = calculation.name if name is None else name
    metadata = {
        "source": str(calculation.source),
        "engine": calculation.engine,
    }
    kwargs = {
        "name": scene_name,
        "include_bonds": include_bonds,
        "include_cell": include_cell,
        "include_axes": include_axes,
        "atom_radius_scale": atom_radius_scale,
        "bond_radius": bond_radius,
        "bond_scale": bond_scale,
        "max_atoms_for_bonds": max_atoms_for_bonds,
        "metadata": metadata,
    }
    if calculation.trajectory is not None:
        return scene_from_trajectory(
            calculation.trajectory,
            frame_indices=frame_indices,
            **kwargs,
        )
    if calculation.dataset is not None:
        return scene_from_dataset(
            calculation.dataset,
            structure_indices=frame_indices,
            **kwargs,
        )
    structure = calculation.structure
    if structure is not None:
        return scene_from_structure(structure, **kwargs)
    raise ValueError("Calculation does not contain structures that can be rendered.")


def primitive_set_from_structure(
    structure: Structure,
    *,
    include_bonds: bool = True,
    include_cell: bool = True,
    include_axes: bool = True,
    atom_radius_scale: float = 0.35,
    bond_radius: float = 0.08,
    bond_scale: float = 1.25,
    max_atoms_for_bonds: int = 500,
    metadata: dict[str, object] | None = None,
) -> PrimitiveSet:
    """Convert one Structure frame into atoms, optional bonds, cell and axes primitives."""
    local_indices = _finite_atom_indices(structure)
    atoms = tuple(
        AtomPrimitive(
            atom_id=int(structure.atom_ids[index]),
            symbol=str(structure.species[index]),
            position=_vec3(structure.positions[index]),
            radius=_atom_radius(str(structure.species[index]), atom_radius_scale),
            color=_atom_color(str(structure.species[index])),
        )
        for index in local_indices
    )
    should_infer_bonds = include_bonds and len(local_indices) <= max_atoms_for_bonds
    bonds = (
        _infer_bonds(structure, local_indices, radius=bond_radius, scale=bond_scale)
        if should_infer_bonds
        else tuple()
    )
    return PrimitiveSet(
        atoms=atoms,
        bonds=bonds,
        cell=_cell_primitive(structure) if include_cell else None,
        axes=AxesPrimitive() if include_axes else None,
        metadata={
            "atom_count": len(atoms),
            "bonds_inferred": should_infer_bonds,
            **(metadata or {}),
        },
    )


def to_scene_data(
    value: Calculation | StructureDataset | Trajectory | Structure,
    **kwargs,
) -> SceneData:
    """Dispatch helper for user code that already has a ProChem object."""
    if isinstance(value, Calculation):
        return scene_from_calculation(value, **kwargs)
    if isinstance(value, StructureDataset):
        return scene_from_dataset(value, **kwargs)
    if isinstance(value, Trajectory):
        return scene_from_trajectory(value, **kwargs)
    if isinstance(value, Structure):
        return scene_from_structure(value, **kwargs)
    raise TypeError(f"Cannot convert {type(value).__name__} to SceneData.")


def _finite_atom_indices(structure: Structure) -> tuple[int, ...]:
    finite = np.isfinite(structure.positions).all(axis=1)
    return tuple(int(index) for index in np.flatnonzero(finite))


def _infer_bonds(
    structure: Structure,
    local_indices: Iterable[int],
    *,
    radius: float,
    scale: float,
) -> tuple[BondPrimitive, ...]:
    indices = tuple(local_indices)
    bonds: list[BondPrimitive] = []
    for left_offset, first in enumerate(indices):
        first_symbol = str(structure.species[first])
        first_radius = covalent_radius(first_symbol) or 0.75
        for second in indices[left_offset + 1 :]:
            second_symbol = str(structure.species[second])
            second_radius = covalent_radius(second_symbol) or 0.75
            threshold = (first_radius + second_radius) * scale
            value = distance(structure, first, second, use_pbc=True)
            if 1.0e-8 < value <= threshold:
                bonds.append(
                    BondPrimitive(
                        first_atom_id=int(structure.atom_ids[first]),
                        second_atom_id=int(structure.atom_ids[second]),
                        radius=radius,
                    )
                )
    return tuple(bonds)


def _cell_primitive(structure: Structure) -> CellPrimitive | None:
    if structure.cell is None:
        return None
    return CellPrimitive(vectors=tuple(_vec3(vector) for vector in structure.cell.vectors))


def _atom_radius(symbol: str, scale: float) -> float:
    return (covalent_radius(symbol) or 0.75) * scale


def _atom_color(symbol: str) -> Color:
    item = element(symbol)
    rgb = (0.6, 0.6, 0.6) if item is None else item.color
    return (float(rgb[0]), float(rgb[1]), float(rgb[2]), 1.0)


def _vec3(values) -> Vec3:
    x, y, z = np.asarray(values, dtype=np.float64).tolist()
    return (float(x), float(y), float(z))


__all__ = [
    "SceneData",
    "primitive_set_from_structure",
    "scene_from_calculation",
    "scene_from_dataset",
    "scene_from_structure",
    "scene_from_trajectory",
    "to_scene_data",
]
