"""Scene DTOs and converters shared by Qt, Jupyter and web renderers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Iterable, Mapping, Sequence

import numpy as np

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

ColorInput = Sequence[float] | str
BondMaxLengths = Mapping[tuple[str, str] | str, float]


@dataclass(frozen=True, slots=True)
class _BondEdge:
    first: int
    second: int
    image_shift: tuple[int, int, int]


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
    atom_radius_scales: Mapping[str, float] | None = None,
    atom_colors: Mapping[str, ColorInput] | None = None,
    bond_radius: float = 0.08,
    bond_scale: float = 1.25,
    bond_max_lengths: BondMaxLengths | None = None,
    max_atoms_for_bonds: int = 500,
    include_periodic_images: bool = True,
    periodic_image_depth: int = 1,
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
                atom_radius_scales=atom_radius_scales,
                atom_colors=atom_colors,
                bond_radius=bond_radius,
                bond_scale=bond_scale,
                bond_max_lengths=bond_max_lengths,
                max_atoms_for_bonds=max_atoms_for_bonds,
                include_periodic_images=include_periodic_images,
                periodic_image_depth=periodic_image_depth,
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
    atom_radius_scales: Mapping[str, float] | None = None,
    atom_colors: Mapping[str, ColorInput] | None = None,
    bond_radius: float = 0.08,
    bond_scale: float = 1.25,
    bond_max_lengths: BondMaxLengths | None = None,
    max_atoms_for_bonds: int = 500,
    include_periodic_images: bool = True,
    periodic_image_depth: int = 1,
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
            atom_radius_scales=atom_radius_scales,
            atom_colors=atom_colors,
            bond_radius=bond_radius,
            bond_scale=bond_scale,
            bond_max_lengths=bond_max_lengths,
            max_atoms_for_bonds=max_atoms_for_bonds,
            include_periodic_images=include_periodic_images,
            periodic_image_depth=periodic_image_depth,
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
    atom_radius_scales: Mapping[str, float] | None = None,
    atom_colors: Mapping[str, ColorInput] | None = None,
    bond_radius: float = 0.08,
    bond_scale: float = 1.25,
    bond_max_lengths: BondMaxLengths | None = None,
    max_atoms_for_bonds: int = 500,
    include_periodic_images: bool = True,
    periodic_image_depth: int = 1,
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
            atom_radius_scales=atom_radius_scales,
            atom_colors=atom_colors,
            bond_radius=bond_radius,
            bond_scale=bond_scale,
            bond_max_lengths=bond_max_lengths,
            max_atoms_for_bonds=max_atoms_for_bonds,
            include_periodic_images=include_periodic_images,
            periodic_image_depth=periodic_image_depth,
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
    atom_radius_scales: Mapping[str, float] | None = None,
    atom_colors: Mapping[str, ColorInput] | None = None,
    bond_radius: float = 0.08,
    bond_scale: float = 1.25,
    bond_max_lengths: BondMaxLengths | None = None,
    max_atoms_for_bonds: int = 500,
    include_periodic_images: bool = True,
    periodic_image_depth: int = 1,
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
        "atom_radius_scales": atom_radius_scales,
        "atom_colors": atom_colors,
        "bond_radius": bond_radius,
        "bond_scale": bond_scale,
        "bond_max_lengths": bond_max_lengths,
        "max_atoms_for_bonds": max_atoms_for_bonds,
        "include_periodic_images": include_periodic_images,
        "periodic_image_depth": periodic_image_depth,
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
    atom_radius_scales: Mapping[str, float] | None = None,
    atom_colors: Mapping[str, ColorInput] | None = None,
    bond_radius: float = 0.08,
    bond_scale: float = 1.25,
    bond_max_lengths: BondMaxLengths | None = None,
    max_atoms_for_bonds: int = 500,
    include_periodic_images: bool = True,
    periodic_image_depth: int = 1,
    metadata: dict[str, object] | None = None,
) -> PrimitiveSet:
    """Convert one Structure frame into atoms, optional bonds, cell and axes primitives."""
    local_indices = _finite_atom_indices(structure)
    atoms = tuple(
        AtomPrimitive(
            atom_id=int(structure.atom_ids[index]),
            symbol=str(structure.species[index]),
            position=_vec3(structure.positions[index]),
            radius=_atom_radius(
                str(structure.species[index]),
                atom_radius_scale,
                atom_radius_scales,
            ),
            color=_atom_color(str(structure.species[index]), atom_colors),
        )
        for index in local_indices
    )
    should_infer_bonds = include_bonds and len(local_indices) <= max_atoms_for_bonds
    image_atoms: tuple[AtomPrimitive, ...] = tuple()
    if should_infer_bonds:
        bonds, image_atoms = _infer_bonds(
            structure,
            local_indices,
            radius=bond_radius,
            scale=bond_scale,
            max_lengths=bond_max_lengths,
            atom_radius_scale=atom_radius_scale,
            atom_radius_scales=atom_radius_scales,
            atom_colors=atom_colors,
            include_periodic_images=include_periodic_images,
            periodic_image_depth=periodic_image_depth,
        )
    else:
        bonds = tuple()
    return PrimitiveSet(
        atoms=atoms + image_atoms,
        bonds=bonds,
        cell=_cell_primitive(structure) if include_cell else None,
        axes=AxesPrimitive() if include_axes else None,
        metadata={
            "atom_count": len(atoms),
            "image_atom_count": len(image_atoms),
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
    max_lengths: BondMaxLengths | None,
    atom_radius_scale: float,
    atom_radius_scales: Mapping[str, float] | None,
    atom_colors: Mapping[str, ColorInput] | None,
    include_periodic_images: bool,
    periodic_image_depth: int,
) -> tuple[tuple[BondPrimitive, ...], tuple[AtomPrimitive, ...]]:
    indices = tuple(local_indices)
    pair_limits = _normalize_bond_max_lengths(max_lengths)
    fractional = _fractional_positions(structure)
    edges = _bond_edges(structure, indices, scale, pair_limits, fractional)
    bonds: list[BondPrimitive] = [
        _bond_primitive(structure, edge, (0, 0, 0), radius=radius)
        for edge in edges
    ]
    image_atoms: dict[tuple[int, tuple[int, int, int]], AtomPrimitive] = {}
    image_bonds: set[tuple[int, int, tuple[int, int, int]]] = set()

    if include_periodic_images and structure.cell is not None and periodic_image_depth > 0:
        image_atoms, image_bonds = _periodic_component_images(
            structure,
            edges,
            depth=periodic_image_depth,
            atom_radius_scale=atom_radius_scale,
            atom_radius_scales=atom_radius_scales,
            atom_colors=atom_colors,
        )
        for first, second, shift in sorted(image_bonds):
            edge = next(
                item
                for item in edges
                if item.first == first
                and item.second == second
            )
            bonds.append(_bond_primitive(structure, edge, shift, radius=radius))

    return tuple(bonds), tuple(image_atoms.values())


def _bond_edges(
    structure: Structure,
    indices: tuple[int, ...],
    scale: float,
    pair_limits: Mapping[tuple[str, str], float],
    fractional: np.ndarray | None,
) -> tuple[_BondEdge, ...]:
    edges: list[_BondEdge] = []
    for left_offset, first in enumerate(indices):
        first_symbol = str(structure.species[first])
        for second in indices[left_offset + 1 :]:
            second_symbol = str(structure.species[second])
            threshold = _bond_threshold(first_symbol, second_symbol, scale, pair_limits)
            displacement, image_shift = _minimum_image_displacement(
                structure,
                fractional,
                first,
                second,
            )
            value = float(np.linalg.norm(displacement))
            if 1.0e-8 < value <= threshold:
                edges.append(
                    _BondEdge(
                        first=first,
                        second=second,
                        image_shift=tuple(int(component) for component in image_shift),
                    )
                )
    return tuple(edges)


def _periodic_component_images(
    structure: Structure,
    edges: tuple[_BondEdge, ...],
    *,
    depth: int,
    atom_radius_scale: float,
    atom_radius_scales: Mapping[str, float] | None,
    atom_colors: Mapping[str, ColorInput] | None,
) -> tuple[
    dict[tuple[int, tuple[int, int, int]], AtomPrimitive],
    set[tuple[int, int, tuple[int, int, int]]],
]:
    adjacency = _bond_adjacency(edges)
    image_atoms: dict[tuple[int, tuple[int, int, int]], AtomPrimitive] = {}
    image_bonds: set[tuple[int, int, tuple[int, int, int]]] = set()
    queue: list[tuple[int, tuple[int, int, int]]] = []

    for edge in edges:
        if edge.image_shift == (0, 0, 0):
            continue
        _queue_image(
            edge.second,
            edge.image_shift,
            depth,
            image_atoms,
            queue,
            structure,
            atom_radius_scale,
            atom_radius_scales,
            atom_colors,
        )
        reverse_shift = _neg_shift(edge.image_shift)
        _queue_image(
            edge.first,
            reverse_shift,
            depth,
            image_atoms,
            queue,
            structure,
            atom_radius_scale,
            atom_radius_scales,
            atom_colors,
        )

    while queue:
        atom_index, atom_shift = queue.pop(0)
        for other_index, other_relative_shift in adjacency[atom_index]:
            other_shift = _add_shift(atom_shift, other_relative_shift)
            if other_shift != (0, 0, 0) and max(abs(component) for component in other_shift) > depth:
                continue
            first, second, first_shift = _canonical_bond_key(
                atom_index,
                other_index,
                atom_shift,
                other_shift,
            )
            if first_shift != (0, 0, 0):
                image_bonds.add((first, second, first_shift))

            if other_shift == (0, 0, 0):
                continue
            _queue_image(
                other_index,
                other_shift,
                depth,
                image_atoms,
                queue,
                structure,
                atom_radius_scale,
                atom_radius_scales,
                atom_colors,
            )

    return image_atoms, image_bonds


def _bond_adjacency(
    edges: tuple[_BondEdge, ...],
) -> dict[int, list[tuple[int, tuple[int, int, int]]]]:
    adjacency: dict[int, list[tuple[int, tuple[int, int, int]]]] = {}
    for edge in edges:
        adjacency.setdefault(edge.first, []).append((edge.second, edge.image_shift))
        adjacency.setdefault(edge.second, []).append((edge.first, _neg_shift(edge.image_shift)))
    return adjacency


def _queue_image(
    atom_index: int,
    shift: tuple[int, int, int],
    depth: int,
    image_atoms: dict[tuple[int, tuple[int, int, int]], AtomPrimitive],
    queue: list[tuple[int, tuple[int, int, int]]],
    structure: Structure,
    atom_radius_scale: float,
    atom_radius_scales: Mapping[str, float] | None,
    atom_colors: Mapping[str, ColorInput] | None,
) -> None:
    if shift == (0, 0, 0) or max(abs(component) for component in shift) > depth:
        return
    atom_id = int(structure.atom_ids[atom_index])
    key = (atom_id, shift)
    if key in image_atoms:
        return
    symbol = str(structure.species[atom_index])
    image_atoms[key] = AtomPrimitive(
        atom_id=atom_id,
        symbol=symbol,
        position=_vec3(_shifted_position(structure, atom_index, shift)),
        radius=_atom_radius(symbol, atom_radius_scale, atom_radius_scales),
        color=_atom_color(symbol, atom_colors),
        image_of_atom_id=atom_id,
        image_shift=shift,
    )
    queue.append((atom_index, shift))


def _canonical_bond_key(
    first: int,
    second: int,
    first_shift: tuple[int, int, int],
    second_shift: tuple[int, int, int],
) -> tuple[int, int, tuple[int, int, int]]:
    if first < second:
        return first, second, first_shift
    return second, first, second_shift


def _bond_primitive(
    structure: Structure,
    edge: _BondEdge,
    first_shift: tuple[int, int, int],
    *,
    radius: float,
) -> BondPrimitive:
    second_shift = _add_shift(first_shift, edge.image_shift)
    start = _shifted_position(structure, edge.first, first_shift)
    end = _shifted_position(structure, edge.second, second_shift)
    image_shift = second_shift if first_shift == (0, 0, 0) else first_shift
    return BondPrimitive(
        first_atom_id=int(structure.atom_ids[edge.first]),
        second_atom_id=int(structure.atom_ids[edge.second]),
        radius=radius,
        start=_vec3(start),
        end=_vec3(end),
        image_shift=image_shift if image_shift != (0, 0, 0) else None,
    )


def _shifted_position(
    structure: Structure,
    atom_index: int,
    shift: tuple[int, int, int],
) -> np.ndarray:
    position = np.asarray(structure.positions[atom_index], dtype=np.float64)
    if structure.cell is None or shift == (0, 0, 0):
        return position
    return position + np.asarray(shift, dtype=np.float64) @ structure.cell.vectors


def _add_shift(
    first: tuple[int, int, int],
    second: tuple[int, int, int],
) -> tuple[int, int, int]:
    return (
        first[0] + second[0],
        first[1] + second[1],
        first[2] + second[2],
    )


def _neg_shift(shift: tuple[int, int, int]) -> tuple[int, int, int]:
    return (-shift[0], -shift[1], -shift[2])


def _cell_primitive(structure: Structure) -> CellPrimitive | None:
    if structure.cell is None:
        return None
    return CellPrimitive(vectors=tuple(_vec3(vector) for vector in structure.cell.vectors))


def _atom_radius(
    symbol: str,
    scale: float,
    type_scales: Mapping[str, float] | None,
) -> float:
    symbol_scale = 1.0 if type_scales is None else float(type_scales.get(symbol, 1.0))
    return (covalent_radius(symbol) or 0.75) * scale * symbol_scale


def _atom_color(symbol: str, colors: Mapping[str, ColorInput] | None = None) -> Color:
    if colors is not None and symbol in colors:
        return _normalize_color(colors[symbol])
    item = element(symbol)
    rgb = (0.6, 0.6, 0.6) if item is None else item.color
    return (float(rgb[0]), float(rgb[1]), float(rgb[2]), 1.0)


def _normalize_color(value: ColorInput) -> Color:
    if isinstance(value, str):
        return _hex_color(value)
    channels = tuple(float(channel) for channel in value)
    if len(channels) == 3:
        channels = (*channels, 1.0)
    if len(channels) != 4:
        raise ValueError("Atom colors must contain 3 or 4 channels.")
    if any(channel > 1.0 for channel in channels[:3]):
        channels = (
            channels[0] / 255.0,
            channels[1] / 255.0,
            channels[2] / 255.0,
            channels[3],
        )
    r, g, b, a = (float(np.clip(channel, 0.0, 1.0)) for channel in channels)
    return (r, g, b, a)


def _hex_color(value: str) -> Color:
    color = value.strip()
    if color.startswith("#"):
        color = color[1:]
    if len(color) not in {6, 8}:
        raise ValueError("Hex colors must use #RRGGBB or #RRGGBBAA format.")
    channels = tuple(
        int(color[index : index + 2], 16) / 255.0
        for index in range(0, len(color), 2)
    )
    if len(channels) == 3:
        r, g, b = channels
        return (r, g, b, 1.0)
    r, g, b, a = channels
    return (r, g, b, a)


def _normalize_bond_max_lengths(
    values: BondMaxLengths | None,
) -> dict[tuple[str, str], float]:
    if not values:
        return {}
    normalized: dict[tuple[str, str], float] = {}
    for pair, length in values.items():
        if isinstance(pair, str):
            symbols = _split_pair_key(pair)
        else:
            symbols = tuple(pair)
        if len(symbols) != 2:
            raise ValueError("Bond pair keys must contain exactly two element symbols.")
        key = tuple(sorted((str(symbols[0]), str(symbols[1]))))
        normalized[key] = float(length)
    return normalized


def _split_pair_key(value: str) -> tuple[str, str]:
    for separator in ("-", ":", ",", "/"):
        if separator in value:
            left, right = value.split(separator, 1)
            return left.strip(), right.strip()
    raise ValueError("String bond pair keys must look like 'Si-O' or 'Si:O'.")


def _bond_threshold(
    first_symbol: str,
    second_symbol: str,
    scale: float,
    pair_limits: Mapping[tuple[str, str], float],
) -> float:
    key = tuple(sorted((first_symbol, second_symbol)))
    if key in pair_limits:
        return float(pair_limits[key])
    first_radius = covalent_radius(first_symbol) or 0.75
    second_radius = covalent_radius(second_symbol) or 0.75
    return (first_radius + second_radius) * scale


def _fractional_positions(structure: Structure) -> np.ndarray | None:
    if structure.cell is None:
        return None
    if structure.direct_positions is not None:
        return np.asarray(structure.direct_positions, dtype=np.float64)
    return np.asarray(structure.positions, dtype=np.float64) @ np.linalg.inv(structure.cell.vectors)


def _minimum_image_displacement(
    structure: Structure,
    fractional: np.ndarray | None,
    first: int,
    second: int,
) -> tuple[np.ndarray, np.ndarray]:
    if structure.cell is None or fractional is None:
        return structure.positions[second] - structure.positions[first], np.zeros(3, dtype=np.int64)
    delta = fractional[second] - fractional[first]
    image_shift = np.zeros(3, dtype=np.int64)
    pbc = structure.cell.pbc
    for axis, periodic in enumerate(pbc):
        if periodic:
            shift = int(np.round(delta[axis]))
            delta[axis] -= shift
            image_shift[axis] = -shift
    return delta @ structure.cell.vectors, image_shift


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
