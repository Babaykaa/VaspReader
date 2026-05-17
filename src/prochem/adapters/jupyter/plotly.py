"""Plotly helpers for rendering ProChem SceneData in notebooks."""

from __future__ import annotations

from typing import Any

from prochem.core.models import Calculation, Structure, StructureDataset, Trajectory
from prochem.rendering import SceneData, to_scene_data
from prochem.rendering.primitives import CellPrimitive, Color, PrimitiveSet, Vec3


def scene_figure(
    scene: SceneData,
    *,
    frame_index: int = 0,
    show_bonds: bool = True,
    show_cell: bool = True,
    show_axes: bool = True,
    atom_size_scale: float = 28.0,
    title: str | None = None,
):
    """Return a Plotly 3D figure for one SceneData frame."""
    go = _graph_objects()
    frame = scene.frame(frame_index)
    traces = [_atoms_trace(go, frame, atom_size_scale=atom_size_scale)]
    if show_bonds and frame.bonds:
        traces.append(_bonds_trace(go, frame))
    if show_cell and frame.cell is not None:
        traces.append(_cell_trace(go, frame.cell))
    if show_axes and frame.axes is not None:
        traces.extend(_axes_trace(go, frame.axes.origin, frame.axes.length, frame.axes.labels))

    figure = go.Figure(data=traces)
    figure.update_layout(
        title=title or scene.name or None,
        scene={
            "xaxis_title": "x, A",
            "yaxis_title": "y, A",
            "zaxis_title": "z, A",
            "aspectmode": "data",
        },
        margin={"l": 0, "r": 0, "t": 40, "b": 0},
        showlegend=True,
    )
    return figure


def structure_figure(structure: Structure, **kwargs):
    """Return a Plotly 3D figure for one Structure."""
    scene = to_scene_data(structure)
    return scene_figure(scene, **kwargs)


def trajectory_figure(
    trajectory: Trajectory,
    *,
    frame_index: int = 0,
    **kwargs,
):
    """Return a Plotly 3D figure for one trajectory frame."""
    scene = to_scene_data(trajectory, frame_indices=[frame_index])
    return scene_figure(scene, frame_index=0, **kwargs)


def calculation_figure(
    calculation: Calculation,
    *,
    frame_index: int = 0,
    **kwargs,
):
    """Return a Plotly 3D figure for a parsed calculation frame."""
    scene = to_scene_data(calculation, frame_indices=[frame_index])
    return scene_figure(scene, frame_index=0, **kwargs)


def scene_animation(
    value: SceneData | Calculation | StructureDataset | Trajectory | Structure,
    *,
    atom_size_scale: float = 28.0,
    show_bonds: bool = True,
    show_cell: bool = True,
    show_axes: bool = True,
    title: str | None = None,
):
    """Return a Plotly figure with a frame slider for SceneData-like inputs."""
    go = _graph_objects()
    scene = value if isinstance(value, SceneData) else to_scene_data(value)
    if scene.frame_count == 0:
        raise ValueError("SceneData must contain at least one frame.")

    base = scene_figure(
        scene,
        frame_index=0,
        atom_size_scale=atom_size_scale,
        show_bonds=show_bonds,
        show_cell=show_cell,
        show_axes=show_axes,
        title=title,
    )
    frames = []
    for index in range(scene.frame_count):
        frame_figure = scene_figure(
            scene,
            frame_index=index,
            atom_size_scale=atom_size_scale,
            show_bonds=show_bonds,
            show_cell=show_cell,
            show_axes=show_axes,
            title=title,
        )
        frames.append(go.Frame(data=frame_figure.data, name=str(index)))

    base.frames = frames
    base.update_layout(
        sliders=[
            {
                "active": 0,
                "steps": [
                    {
                        "label": str(index),
                        "method": "animate",
                        "args": [[str(index)], {"mode": "immediate", "frame": {"duration": 0}}],
                    }
                    for index in range(scene.frame_count)
                ],
            }
        ],
        updatemenus=[
            {
                "type": "buttons",
                "showactive": False,
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [None, {"frame": {"duration": 250}, "fromcurrent": True}],
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [[None], {"mode": "immediate", "frame": {"duration": 0}}],
                    },
                ],
            }
        ],
    )
    return base


def _atoms_trace(go, frame: PrimitiveSet, *, atom_size_scale: float):
    return go.Scatter3d(
        x=[atom.position[0] for atom in frame.atoms],
        y=[atom.position[1] for atom in frame.atoms],
        z=[atom.position[2] for atom in frame.atoms],
        mode="markers+text",
        text=[atom.symbol for atom in frame.atoms],
        textposition="top center",
        marker={
            "size": [max(atom.radius * atom_size_scale, 3.0) for atom in frame.atoms],
            "color": [_rgba(atom.color) for atom in frame.atoms],
            "line": {"width": 1, "color": "rgba(40,40,40,0.55)"},
        },
        name="atoms",
    )


def _bonds_trace(go, frame: PrimitiveSet):
    positions = {atom.atom_id: atom.position for atom in frame.atoms}
    x: list[float | None] = []
    y: list[float | None] = []
    z: list[float | None] = []
    for bond in frame.bonds:
        first = positions.get(bond.first_atom_id)
        second = positions.get(bond.second_atom_id)
        if first is None or second is None:
            continue
        x.extend([first[0], second[0], None])
        y.extend([first[1], second[1], None])
        z.extend([first[2], second[2], None])
    return go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="lines",
        line={"width": 5, "color": "rgba(120,120,120,0.8)"},
        name="bonds",
    )


def _cell_trace(go, cell: CellPrimitive):
    corners = _cell_corners(cell.vectors)
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
    x: list[float | None] = []
    y: list[float | None] = []
    z: list[float | None] = []
    for first, second in edges:
        a = corners[first]
        b = corners[second]
        x.extend([a[0], b[0], None])
        y.extend([a[1], b[1], None])
        z.extend([a[2], b[2], None])
    return go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="lines",
        line={"width": 3, "color": _rgba(cell.color)},
        name="cell",
    )


def _axes_trace(go, origin: Vec3, length: float, labels: tuple[str, str, str]):
    directions = ((length, 0.0, 0.0), (0.0, length, 0.0), (0.0, 0.0, length))
    colors = ("rgba(210,40,40,0.9)", "rgba(40,160,60,0.9)", "rgba(50,80,220,0.9)")
    traces = []
    for label, direction, color in zip(labels, directions, colors, strict=True):
        end = (
            origin[0] + direction[0],
            origin[1] + direction[1],
            origin[2] + direction[2],
        )
        traces.append(
            go.Scatter3d(
                x=[origin[0], end[0]],
                y=[origin[1], end[1]],
                z=[origin[2], end[2]],
                mode="lines+text",
                text=["", label],
                line={"width": 4, "color": color},
                name=f"{label}-axis",
                showlegend=False,
            )
        )
    return traces


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


def _rgba(color: Color) -> str:
    r, g, b, a = color
    return f"rgba({int(r * 255)},{int(g * 255)},{int(b * 255)},{a})"


def _graph_objects() -> Any:
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise RuntimeError("Install prochem[jupyter] to use Plotly notebook rendering.") from exc
    return go


__all__ = [
    "calculation_figure",
    "scene_animation",
    "scene_figure",
    "structure_figure",
    "trajectory_figure",
]
