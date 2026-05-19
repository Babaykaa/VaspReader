from __future__ import annotations

import numpy as np

from prochem.analysis import AnalysisTable, Selection
from prochem.core import Atom, Cell, Structure, Structures


def test_atom_uses_periodic_defaults_and_shared_visual_style() -> None:
    first = Atom(name="C")
    second = Atom(name="C")
    by_atomic_number = Atom(name=6)

    assert first.charge == 6
    assert first.valent_charge == 4
    assert first.mass == 12.011
    assert by_atomic_number.name == "C"
    assert by_atomic_number.charge == 6

    first.size = 1.2
    first.color = (0.1, 0.2, 0.3, 1.0)

    assert first.size is second.size
    assert first.size is by_atomic_number.size
    assert first.color is second.color
    assert first.color is by_atomic_number.color
    assert float(second.size) == 1.2
    np.testing.assert_allclose(second.color, [0.1, 0.2, 0.3, 1.0])


def test_atom_and_structure_energy_helpers() -> None:
    default_atom = Atom(name="H")
    default_structure = Structure(atoms=[default_atom.copy(index=0)])

    assert default_atom.potential_energy is None
    assert default_atom.kinetic_energy is None
    assert default_atom.total_energy is None
    assert default_structure.potential_energy is None
    assert default_structure.kinetic_energy is None
    assert default_structure.total_energy is None
    assert np.isnan(default_structure.atom_potential_energies_array()).all()

    atom = Atom(
        name="H",
        velocity=(1.0, 0.0, 0.0),
        mass=2.0,
        potential_energy=0.25,
    )

    np.testing.assert_allclose(atom.approximate_force((2.0, 0.0, 0.0), delta_t=0.5), [4.0, 0.0, 0.0])
    assert atom.kinetic_energy_from_velocity() == 1.0

    structure = Structure(atoms=[atom.copy(index=0)], potential_energy=-3.0, kinetic_energy=1.0)

    assert structure.potential_energy == -3.0
    assert structure.kinetic_energy == 1.0
    assert structure.total_energy == -2.0
    np.testing.assert_allclose(structure.atom_potential_energies_array(), [0.25])
    np.testing.assert_allclose(structure.atom_kinetic_energies_array(), [1.0])
    np.testing.assert_allclose(structure.atom_total_energies_array(), [1.25])

    explicit_total = Structure(
        atoms=[Atom(name="H", index=0)],
        potential_energy=-3.0,
        total_energy=-2.5,
    )
    assert explicit_total.kinetic_energy is None
    assert explicit_total.total_energy == -2.5


def test_structure_and_structures_store_atoms_as_source_of_truth() -> None:
    structure = Structure(
        atoms=[
            Atom(name="H", index=0, position=(0.0, 0.0, 0.0)),
            Atom(name="O", index=1, position=(0.0, 0.0, 1.0)),
        ],
        cell=Cell(np.eye(3)),
    )
    structures = Structures(frames=[structure], timestep=0.5)

    assert structure.atom_count == 2
    np.testing.assert_allclose(structure.positions[1], [0.0, 0.0, 1.0])
    assert structures.step_count == 1
    assert structures.timestep == 0.5
    assert len(structures.sources) == 1
    np.testing.assert_allclose(structures.time_fs, [0.0])


def test_structures_keeps_internal_registry_for_missing_atoms() -> None:
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

    structures = Structures(frames=(first, second))

    assert structures.atom_ids == (0, 1)
    assert structures.atom_columns([1, 0]) == [1, 0]
    np.testing.assert_array_equal(
        structures.presence_mask(),
        np.array([[True, True], [True, False]]),
    )
    assert np.isnan(structures.positions_array()[1, 1]).all()


def test_analysis_uses_stable_atom_ids() -> None:
    structures = Structures.from_arrays(
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

    analysis = AnalysisTable(structures, Selection("oxygen", [1]))
    dataframe = analysis.dataframe(include_coordinates=True)

    assert list(dataframe.columns) == ["Time, fs", "O_2_x", "O_2_y", "O_2_z"]
    np.testing.assert_allclose(dataframe["O_2_z"].to_numpy(), [1.0, 2.0])

    analysis = AnalysisTable(structures, Selection("all", [0, 1]))
    analysis.add_atom_velocities(Selection("hydrogen", [0]))
    analysis.add_center_of_mass("all")

    np.testing.assert_allclose(analysis.data["V_H_1"].to_numpy(), [np.nan, 1000.0])
    np.testing.assert_allclose(
        analysis.data[["cm_all_x", "cm_all_y", "cm_all_z"]].to_numpy()[0],
        [0.0, 0.0, 16.0 / 17.0],
    )


def test_analysis_table_deduplicates_overlapping_selection_coordinates() -> None:
    structures = Structures.from_arrays(
        species=np.array(["H", "O", "H"]),
        positions=np.array(
            [
                [[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]],
                [[0.0, 0.0, 0.1], [0.0, 0.0, 1.1], [1.0, 0.1, 0.0]],
            ]
        ),
        time_fs=np.array([0.0, 1.0]),
        masses=np.array([1.0, 16.0, 1.0]),
    )

    analysis = AnalysisTable(
        structures,
        [
            Selection("left", [0, 1]),
            Selection("right", [1, 2]),
        ],
    )

    assert list(analysis.dataframe().columns) == ["Time, fs"]
    assert analysis.coordinate_cache.shape == (2, 9)
    assert "O_2_x" in analysis.dataframe(include_coordinates=True)

    analysis.add_selection_distance("left", "right")
    analysis.add_valence_angles("right", triples=[(1, 2, 0)])

    assert "left--right" in analysis.data
    assert "O_2-H_3-H_1" in analysis.data


def test_structure_dataset_can_be_packed_without_strict_topology() -> None:
    from prochem.core import StructureDataset

    dataset = StructureDataset(
        structures=(
            Structure(species=np.array(["H"]), positions=np.array([[0.0, 0.0, 0.0]])),
            Structure(
                species=np.array(["O", "H"]),
                positions=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]),
            ),
        )
    )

    structures = dataset.to_structures(strict_topology=False)

    assert structures.step_count == 2
    assert structures.atom_count == 3
    assert structures.atom_potential_energies_array().shape == (2, 3)
    assert dataset.positions_array().shape == (2, 2, 3)
    assert np.isnan(dataset.structure_potential_energies_array()).all()
    assert structures.frame(1).properties["dataset_index"] == 1


def test_cell_validates_shape() -> None:
    try:
        Cell(np.eye(2))
    except ValueError as error:
        assert "shape (3, 3)" in str(error)
    else:
        raise AssertionError("Cell accepted invalid vectors.")
