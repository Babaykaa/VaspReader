from __future__ import annotations

import numpy as np

from prochem.core import Calculation, Cell, Structure, Trajectory
from prochem.rendering import (
    SceneData,
    scene_from_calculation,
    scene_from_structure,
    scene_from_trajectory,
    to_scene_data,
)


def test_scene_from_structure_contains_atoms_bond_cell_and_axes() -> None:
    structure = Structure(
        species=np.array(["H", "H"]),
        positions=np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]]),
        cell=Cell(np.eye(3) * 5.0),
    )

    scene = scene_from_structure(structure, name="h2")
    frame = scene.frame(0)

    assert isinstance(scene, SceneData)
    assert scene.name == "h2"
    assert scene.frame_count == 1
    assert len(frame.atoms) == 2
    assert len(frame.bonds) == 1
    assert frame.cell is not None
    assert frame.axes is not None
    assert frame.atoms[0].symbol == "H"
    assert frame.atoms[0].color == (1.0, 1.0, 1.0, 1.0)


def test_scene_from_trajectory_selects_frames_and_metadata() -> None:
    trajectory = Trajectory.from_arrays(
        species=np.array(["O"]),
        positions=np.array([[[0.0, 0.0, 0.0]], [[1.0, 0.0, 0.0]]]),
        time_fs=np.array([0.0, 2.0]),
    )

    scene = scene_from_trajectory(trajectory, frame_indices=[1])

    assert scene.metadata["kind"] == "trajectory"
    assert scene.metadata["frame_indices"] == (1,)
    assert scene.frame_count == 1
    assert scene.frame(0).metadata["frame_index"] == 1
    assert scene.frame(0).metadata["time_fs"] == 2.0
    assert scene.frame(0).atoms[0].position == (1.0, 0.0, 0.0)


def test_scene_from_calculation_and_dispatcher() -> None:
    trajectory = Trajectory.from_arrays(
        species=np.array(["C"]),
        positions=np.array([[[0.0, 0.0, 0.0]]]),
    )
    calculation = Calculation(source="vasprun.xml", engine="vasp", trajectory=trajectory)

    scene = scene_from_calculation(calculation)
    dispatched = to_scene_data(calculation)

    assert scene.metadata["engine"] == "vasp"
    assert dispatched.name == "vasprun.xml"
    assert dispatched.frame(0).atoms[0].symbol == "C"


def test_scene_to_dict_is_json_friendly() -> None:
    structure = Structure(species=np.array(["Xx"]), positions=np.array([[1.0, 2.0, 3.0]]))

    data = to_scene_data(structure, include_bonds=False).to_dict()

    assert data["frames"][0]["atoms"][0]["position"] == (1.0, 2.0, 3.0)
    assert data["frames"][0]["atoms"][0]["color"] == (0.6, 0.6, 0.6, 1.0)

