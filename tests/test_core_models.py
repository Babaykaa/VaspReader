from __future__ import annotations

import numpy as np

from prochem.analysis import coordinate_dataframe, velocities
from prochem.core import Atom, Cell, Structure, Trajectory
from prochem.core.geometry import center_of_mass


def test_trajectory_keeps_registry_for_missing_atoms() -> None:
    registry = (
        Atom(atom_id=0, species="H", initial_index=0, mass=1.0),
        Atom(atom_id=1, species="O", initial_index=1, mass=16.0),
    )
    first = Structure(
        species=np.array(["H", "O"]),
        atom_ids=np.array([0, 1]),
        positions=np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]]),
        masses=np.array([1.0, 16.0]),
        time_fs=0.0,
    )
    second = Structure(
        species=np.array(["H"]),
        atom_ids=np.array([0]),
        positions=np.array([[1.0, 0.0, 0.0]]),
        time_fs=1.0,
    )

    trajectory = Trajectory(frames=(first, second), atom_registry=registry)

    assert trajectory.atom_ids == (0, 1)
    assert trajectory.atom_columns([1, 0]) == [1, 0]
    np.testing.assert_array_equal(
        trajectory.presence_mask(),
        np.array([[True, True], [True, False]]),
    )
    assert np.isnan(trajectory.positions_array()[1, 1]).all()


def test_analysis_uses_stable_atom_ids() -> None:
    trajectory = Trajectory.from_arrays(
        species=np.array(["H", "O"]),
        positions=np.array(
            [
                [[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]],
                [[1.0, 0.0, 0.0], [0.0, 0.0, 2.0]],
            ]
        ),
        time_fs=np.array([0.0, 1.0]),
        masses=np.array([1.0, 16.0]),
    )

    dataframe = coordinate_dataframe(trajectory, atom_ids=[1], include_direct=False)
    assert list(dataframe.columns) == ["Time, fs", "O_2_x", "O_2_y", "O_2_z"]
    np.testing.assert_allclose(dataframe["O_2_z"].to_numpy(), [1.0, 2.0])
    np.testing.assert_allclose(velocities(trajectory, atom_ids=[0])[:, 0], [np.nan, 1000.0])
    np.testing.assert_allclose(center_of_mass(trajectory, [0, 1])[0], [0.0, 0.0, 16.0 / 17.0])


def test_structure_dataset_can_be_packed_without_strict_topology() -> None:
    from prochem.core import StructureDataset

    dataset = StructureDataset(
        structures=(
            Structure(species=np.array(["H"]), positions=np.array([[0.0, 0.0, 0.0]])),
            Structure(species=np.array(["O", "H"]), positions=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])),
        )
    )

    trajectory = dataset.to_trajectory(strict_topology=False)

    assert trajectory.step_count == 2
    assert trajectory.atom_count == 3
    assert trajectory.frame(1).properties["dataset_index"] == 1


def test_cell_validates_shape() -> None:
    try:
        Cell(np.eye(2))
    except ValueError as error:
        assert "shape (3, 3)" in str(error)
    else:
        raise AssertionError("Cell accepted invalid vectors.")
