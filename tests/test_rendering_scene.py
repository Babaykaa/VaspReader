from __future__ import annotations

import numpy as np
import pytest

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


def test_scene_from_structure_applies_atom_style_overrides() -> None:
    structure = Structure(
        species=np.array(["Si", "O"]),
        positions=np.array([[0.0, 0.0, 0.0], [2.0, 0.0, 0.0]]),
    )

    scene = scene_from_structure(
        structure,
        include_bonds=False,
        atom_colors={"Si": "#ff0000", "O": (0.0, 128.0, 255.0)},
        atom_radius_scales={"Si": 2.0},
    )
    atoms = scene.frame(0).atoms

    assert atoms[0].color == (1.0, 0.0, 0.0, 1.0)
    assert atoms[1].color == pytest.approx((0.0, 128.0 / 255.0, 1.0, 1.0))
    assert atoms[0].radius > atoms[1].radius


def test_scene_from_structure_uses_pair_specific_bond_lengths() -> None:
    structure = Structure(
        species=np.array(["H", "H"]),
        positions=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]),
    )

    without_override = scene_from_structure(structure)
    with_override = scene_from_structure(structure, bond_max_lengths={("H", "H"): 1.1})

    assert len(without_override.frame(0).bonds) == 0
    assert len(with_override.frame(0).bonds) == 1


def test_scene_from_structure_draws_periodic_bonds_to_image_atom() -> None:
    structure = Structure(
        species=np.array(["H", "H"]),
        positions=np.array([[0.1, 5.0, 5.0], [9.9, 5.0, 5.0]]),
        cell=Cell(np.eye(3) * 10.0),
    )

    scene = scene_from_structure(structure)
    frame = scene.frame(0)
    bond = frame.bonds[0]
    image_atoms = [atom for atom in frame.atoms if atom.image_of_atom_id is not None]

    assert bond.start == (0.1, 5.0, 5.0)
    assert bond.end == pytest.approx((-0.1, 5.0, 5.0))
    assert bond.image_shift == (-1, 0, 0)
    assert len(image_atoms) == 2
    assert {atom.image_shift for atom in image_atoms} == {(-1, 0, 0), (1, 0, 0)}
    assert any(atom.position == pytest.approx((-0.1, 5.0, 5.0)) for atom in image_atoms)
    assert any(atom.position == pytest.approx((10.1, 5.0, 5.0)) for atom in image_atoms)


def test_scene_from_structure_extends_periodic_connected_component() -> None:
    structure = Structure(
        species=np.array(["H", "H", "H"]),
        positions=np.array(
            [
                [0.1, 5.0, 5.0],
                [9.9, 5.0, 5.0],
                [9.2, 5.0, 5.0],
            ]
        ),
        cell=Cell(np.eye(3) * 10.0),
    )

    scene = scene_from_structure(structure, bond_max_lengths={("H", "H"): 0.8})
    frame = scene.frame(0)
    image_atoms = [atom for atom in frame.atoms if atom.image_of_atom_id is not None]
    image_positions = {
        atom.atom_id: atom.position
        for atom in image_atoms
        if atom.image_shift == (-1, 0, 0)
    }
    shifted_bond = [
        bond
        for bond in frame.bonds
        if bond.start == pytest.approx((-0.1, 5.0, 5.0))
        and bond.end == pytest.approx((-0.8, 5.0, 5.0))
    ]

    assert frame.metadata["image_atom_count"] == 3
    assert image_positions[1] == pytest.approx((-0.1, 5.0, 5.0))
    assert image_positions[2] == pytest.approx((-0.8, 5.0, 5.0))
    assert shifted_bond
