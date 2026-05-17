"""Core-to-Qt adapter helpers.

This module intentionally avoids importing PySide6. It contains the stable
translation layer between current ProChem core models / SceneData and the
legacy OpenGL draw-buffer format used by the Qt widgets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence

from prochem.core.models import Calculation, Structure, StructureDataset, Trajectory
from prochem.io import parse
from prochem.rendering import SceneData, to_scene_data

ColorInput = Sequence[float] | str
BondMaxLengths = Mapping[tuple[str, str] | str, float]
Vec3 = tuple[float, float, float]
Rgb = tuple[float, float, float]
SphereBuffer = dict[tuple[Rgb, float], list[Vec3]]
LineBuffer = dict[tuple[Rgb, float], list[tuple[Vec3, Vec3]]]
DrawBuffer = dict[str, SphereBuffer | LineBuffer]


@dataclass(frozen=True, slots=True)
class QtSceneOptions:
    """Rendering options accepted by Qt SceneData conversion."""

    frame_indices: tuple[int, ...] | None = None
    include_bonds: bool = True
    include_cell: bool = True
    include_axes: bool = True
    atom_radius_scale: float = 0.35
    atom_radius_scales: Mapping[str, float] | None = None
    atom_colors: Mapping[str, ColorInput] | None = None
    bond_radius: float = 0.08
    bond_scale: float = 1.25
    bond_max_lengths: BondMaxLengths | None = None
    max_atoms_for_bonds: int = 500
    include_periodic_images: bool = True
    periodic_image_depth: int = 1

    def to_scene_kwargs(self) -> dict[str, object]:
        return {
            "frame_indices": self.frame_indices,
            "include_bonds": self.include_bonds,
            "include_cell": self.include_cell,
            "include_axes": self.include_axes,
            "atom_radius_scale": self.atom_radius_scale,
            "atom_radius_scales": self.atom_radius_scales,
            "atom_colors": self.atom_colors,
            "bond_radius": self.bond_radius,
            "bond_scale": self.bond_scale,
            "bond_max_lengths": self.bond_max_lengths,
            "max_atoms_for_bonds": self.max_atoms_for_bonds,
            "include_periodic_images": self.include_periodic_images,
            "periodic_image_depth": self.periodic_image_depth,
        }


@dataclass(slots=True)
class QtCalculationEntry:
    """Calculation record stored by the Qt control window."""

    calculation: Calculation
    visible: bool = True
    scene_options: QtSceneOptions = field(default_factory=QtSceneOptions)
    scene: SceneData | None = None

    @property
    def calculations(self) -> list[Calculation]:
        """Compatibility with the previous dict-shaped control entry."""
        return [self.calculation]

    def as_legacy_dict(self) -> dict[str, object]:
        return {
            "visible": self.visible,
            "calculations": [self.calculation],
            "scene": self.scene,
            "scene_options": self.scene_options,
        }


def parse_calculation(path: str | Path) -> Calculation:
    """Parse a calculation through the current parser registry."""
    return parse(path)


def calculation_kind(calculation: Calculation) -> str:
    if calculation.trajectory is not None:
        return "trajectory"
    if calculation.dataset is not None:
        return "dataset"
    if calculation.structure is not None:
        return "structure"
    return "empty"


def calculation_step_count(calculation: Calculation) -> int:
    """Return the number of renderable frames for a calculation."""
    if calculation.trajectory is not None:
        return calculation.trajectory.step_count
    if calculation.dataset is not None:
        return calculation.dataset.structure_count
    if calculation.structure is not None:
        return 1
    return 0


def calculation_summary(calculation: Calculation) -> dict[str, object]:
    """Return compact GUI metadata for a parsed calculation."""
    return {
        "name": calculation.name,
        "source": str(calculation.source),
        "directory": str(calculation.directory),
        "engine": calculation.engine,
        "kind": calculation_kind(calculation),
        "step_count": calculation_step_count(calculation),
        "atom_count": calculation.atom_count,
        "warnings": list(calculation.warnings),
        "has_errors": calculation.errors.exist,
        "error_message": calculation.errors.message,
    }


def calculation_entry(
    calculation: Calculation,
    *,
    visible: bool = True,
    scene_options: QtSceneOptions | None = None,
) -> QtCalculationEntry:
    options = QtSceneOptions() if scene_options is None else scene_options
    try:
        frame_index = None if options.frame_indices is not None else 0
        scene = scene_from_calculation(calculation, options=options, frame_index=frame_index)
    except ValueError:
        scene = None
    return QtCalculationEntry(
        calculation=calculation,
        visible=visible,
        scene_options=options,
        scene=scene,
    )


def scene_from_calculation(
    calculation: Calculation,
    *,
    options: QtSceneOptions | None = None,
    frame_index: int | None = None,
) -> SceneData:
    """Convert a core Calculation to SceneData suitable for Qt."""
    options = QtSceneOptions() if options is None else options
    kwargs = options.to_scene_kwargs()
    if frame_index is not None:
        kwargs["frame_indices"] = (int(frame_index),)
    return to_scene_data(calculation, **kwargs)


def scene_from_value(
    value: Calculation | StructureDataset | Trajectory | Structure | SceneData,
    *,
    options: QtSceneOptions | None = None,
    frame_index: int | None = None,
) -> SceneData:
    if isinstance(value, SceneData):
        return value
    if isinstance(value, Calculation):
        return scene_from_calculation(value, options=options, frame_index=frame_index)
    options = QtSceneOptions() if options is None else options
    kwargs = options.to_scene_kwargs()
    if frame_index is not None and isinstance(value, (Trajectory, StructureDataset)):
        kwargs["frame_indices"] = (int(frame_index),)
    return to_scene_data(value, **kwargs)


def scene_to_draw_buffer(scene: SceneData, *, frame_index: int = 0) -> DrawBuffer:
    """Convert one SceneData frame to the legacy Qt OpenGL draw buffer.

    Spheres are grouped by color and radius. Bonds and cell edges are grouped
    as OpenGL line segments by color and line width.
    """
    frame = scene.frame(frame_index)
    spheres: SphereBuffer = {}
    for atom in frame.atoms:
        color = tuple(float(channel) for channel in atom.color[:3])
        scale = float(atom.radius)
        position = tuple(float(value) for value in atom.position)
        spheres.setdefault((color, scale), []).append(position)

    lines: LineBuffer = {}
    atom_positions = {
        atom.atom_id: tuple(float(value) for value in atom.position)
        for atom in frame.atoms
        if atom.image_of_atom_id is None
    }
    for bond in frame.bonds:
        start = _vec3(bond.start) if bond.start is not None else atom_positions.get(bond.first_atom_id)
        end = _vec3(bond.end) if bond.end is not None else atom_positions.get(bond.second_atom_id)
        if start is None or end is None:
            continue
        color = tuple(float(channel) for channel in bond.color[:3])
        width = max(1.0, float(bond.radius) * 24.0)
        lines.setdefault((color, width), []).append((start, end))

    if frame.cell is not None:
        color = tuple(float(channel) for channel in frame.cell.color[:3])
        lines.setdefault((color, 2.0), []).extend(_cell_segments(frame.cell.vectors))

    draw_buffer: DrawBuffer = {"Sphere": spheres}
    if lines:
        draw_buffer["Line"] = lines
    return draw_buffer


def _vec3(values: Sequence[float]) -> Vec3:
    return (float(values[0]), float(values[1]), float(values[2]))


def _cell_segments(vectors: tuple[Vec3, Vec3, Vec3]) -> list[tuple[Vec3, Vec3]]:
    corners = _cell_corners(vectors)
    edges = (
        (0, 1),
        (0, 2),
        (0, 4),
        (1, 3),
        (1, 5),
        (2, 3),
        (2, 6),
        (3, 7),
        (4, 5),
        (4, 6),
        (5, 7),
        (6, 7),
    )
    return [(corners[first], corners[second]) for first, second in edges]


def _cell_corners(vectors: tuple[Vec3, Vec3, Vec3]) -> tuple[Vec3, ...]:
    a, b, c = vectors
    return (
        (0.0, 0.0, 0.0),
        a,
        b,
        (a[0] + b[0], a[1] + b[1], a[2] + b[2]),
        c,
        (a[0] + c[0], a[1] + c[1], a[2] + c[2]),
        (b[0] + c[0], b[1] + c[1], b[2] + c[2]),
        (a[0] + b[0] + c[0], a[1] + b[1] + c[1], a[2] + b[2] + c[2]),
    )


def value_to_draw_buffer(
    value: Calculation | StructureDataset | Trajectory | Structure | SceneData,
    *,
    options: QtSceneOptions | None = None,
    frame_index: int = 0,
) -> DrawBuffer:
    scene = scene_from_value(value, options=options, frame_index=frame_index)
    local_frame = 0 if not isinstance(value, SceneData) and frame_index is not None else frame_index
    return scene_to_draw_buffer(scene, frame_index=local_frame)


__all__ = [
    "DrawBuffer",
    "QtCalculationEntry",
    "QtSceneOptions",
    "calculation_entry",
    "calculation_kind",
    "calculation_step_count",
    "calculation_summary",
    "parse_calculation",
    "scene_from_calculation",
    "scene_from_value",
    "scene_to_draw_buffer",
    "value_to_draw_buffer",
]
