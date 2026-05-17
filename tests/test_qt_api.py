from __future__ import annotations

import numpy as np

from prochem.adapters.qt.api import (
    QtSceneOptions,
    calculation_entry,
    calculation_kind,
    calculation_step_count,
    scene_to_draw_buffer,
    value_to_draw_buffer,
)
from prochem.core import Calculation, Cell, Structure, Trajectory
from prochem.rendering import to_scene_data


def test_qt_api_converts_scene_data_to_legacy_draw_buffer() -> None:
    structure = Structure(
        species=np.array(["H", "O"]),
        positions=np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.96]]),
        cell=Cell(np.eye(3) * 8.0),
    )
    scene = to_scene_data(
        structure,
        include_bonds=False,
        atom_colors={"O": "#ff0000"},
        atom_radius_scales={"H": 0.5},
    )

    draw_buffer = scene_to_draw_buffer(scene)

    assert set(draw_buffer) == {"Sphere", "Line"}
    assert sum(len(positions) for positions in draw_buffer["Sphere"].values()) == 2
    assert any(color == (1.0, 0.0, 0.0) for color, _scale in draw_buffer["Sphere"])
    assert sum(len(segments) for segments in draw_buffer["Line"].values()) == 12


def test_qt_api_converts_bonds_to_line_segments() -> None:
    structure = Structure(
        species=np.array(["H", "O"]),
        positions=np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.96]]),
        cell=Cell(np.eye(3) * 8.0),
    )
    scene = to_scene_data(structure, include_cell=False)

    draw_buffer = scene_to_draw_buffer(scene)
    line_segments = [segment for segments in draw_buffer["Line"].values() for segment in segments]

    assert len(line_segments) == 1
    assert line_segments[0] == ((0.0, 0.0, 0.0), (0.0, 0.0, 0.96))


def test_qt_api_builds_calculation_entry_from_current_core_model() -> None:
    trajectory = Trajectory.from_arrays(
        species=np.array(["C"]),
        positions=np.array([[[0.0, 0.0, 0.0]], [[1.0, 0.0, 0.0]]]),
    )
    calculation = Calculation(source="vasprun.xml", engine="vasp", trajectory=trajectory)

    entry = calculation_entry(calculation)

    assert calculation_kind(calculation) == "trajectory"
    assert calculation_step_count(calculation) == 2
    assert entry.as_legacy_dict()["calculations"] == [calculation]
    assert entry.scene is not None
    assert entry.scene.frame_count == 2


def test_qt_api_can_select_single_frame_for_draw_buffer() -> None:
    trajectory = Trajectory.from_arrays(
        species=np.array(["C"]),
        positions=np.array([[[0.0, 0.0, 0.0]], [[1.0, 0.0, 0.0]]]),
    )
    options = QtSceneOptions(frame_indices=(1,))

    draw_buffer = value_to_draw_buffer(trajectory, options=options, frame_index=1)
    positions = next(iter(draw_buffer["Sphere"].values()))

    assert positions == [(1.0, 0.0, 0.0)]


def test_qt_api_keeps_non_renderable_calculation_entry_valid() -> None:
    calculation = Calculation(source="OSZICAR", engine="vasp")

    entry = calculation_entry(calculation)

    assert calculation_kind(calculation) == "empty"
    assert calculation_step_count(calculation) == 0
    assert entry.scene is None
