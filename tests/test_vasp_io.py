from __future__ import annotations

import numpy as np

from prochem.core import BandStructure, DensityOfStates, ElectronicSteps, IonicSteps
from prochem.io import parse
from prochem.io.vasp.doscar import read_doscar
from prochem.io.vasp.eigenval import read_eigenval
from prochem.io.vasp.oszicar import read_oszicar
from prochem.io.vasp.poscar import read_poscar
from prochem.io.vasp.common import VASPfileType


def test_poscar_parser_builds_single_frame_trajectory(tmp_path) -> None:
    source = tmp_path / "POSCAR"
    source.write_text(
        "\n".join(
            [
                "water fragment",
                "1.0",
                "10.0 0.0 0.0",
                "0.0 10.0 0.0",
                "0.0 0.0 10.0",
                "O H",
                "1 2",
                "Direct",
                "0.0 0.0 0.0",
                "0.1 0.0 0.0",
                "0.0 0.1 0.0",
            ]
        ),
        encoding="utf-8",
    )

    calculation = read_poscar(source, VASPfileType.POSCAR)

    assert not calculation.errors.exist
    assert calculation.atom_count == 3
    assert calculation.trajectory is not None
    np.testing.assert_allclose(calculation.trajectory.frame(0).positions[1], [1.0, 0.0, 0.0])


def test_oszicar_parser_returns_typed_step_models(tmp_path) -> None:
    source = tmp_path / "OSZICAR"
    source.write_text(
        "\n".join(
            [
                "DAV:   1   -0.100000D+01    0.100D-02    0.200D-03    3   0.4D-02",
                "DAV:   2   -0.100100D+01   -0.100D-02    0.100D-03    4   0.2D-02",
                " 1 F= -.200000D+01 E0= -.199000D+01  d E =-.100D-01  mag= 0.0",
            ]
        ),
        encoding="utf-8",
    )

    calculation = read_oszicar(source)

    assert isinstance(calculation.electronic_steps, ElectronicSteps)
    assert isinstance(calculation.ionic_steps, IonicSteps)
    assert len(calculation.electronic_steps) == 2
    assert len(calculation.ionic_steps) == 1
    assert calculation.electronic_steps[-1].ncg == 4
    assert calculation.ionic_steps[0].free_energy == -2.0
    assert "F" in calculation.ionic_steps.to_dataframe().columns


def test_doscar_parser_returns_density_of_states(tmp_path) -> None:
    source = tmp_path / "DOSCAR"
    source.write_text(
        "\n".join(
            [
                "1 0 0 0 0",
                "header 1",
                "header 2",
                "header 3",
                "header 4",
                "1.0 -1.0 2 0.25",
                "-1.0 2.0 3.0",
                "1.0 4.0 5.0",
                "0 0 0 0 0",
                "-1.0 0.2 0.3",
                "1.0 0.4 0.5",
            ]
        ),
        encoding="utf-8",
    )

    calculation = read_doscar(source)
    dos = calculation.density_of_states

    assert isinstance(dos, DensityOfStates)
    assert dos.nedos == 2
    assert dos.fermi_energy == 0.25
    assert dos.projected[0].atom_index == 1
    assert "energy_minus_fermi" in dos.to_dataframe(shifted=True).columns


def test_eigenval_parser_returns_band_structure(tmp_path) -> None:
    source = tmp_path / "EIGENVAL"
    source.write_text(
        "\n".join(
            [
                "header 0",
                "header 1",
                "header 2",
                "header 3",
                "header 4",
                "2 1 2",
                "0.0 0.0 0.0 1.0",
                "1 -1.0 1.0",
                "2 2.0 0.0",
            ]
        ),
        encoding="utf-8",
    )

    calculation = read_eigenval(source)
    bands = calculation.band_structure

    assert isinstance(bands, BandStructure)
    assert bands.kpoint_count == 1
    assert bands.band_count == 2
    assert list(bands.to_dataframe()["energy"]) == [-1.0, 2.0]


def test_registry_detects_vasp_file(tmp_path) -> None:
    source = tmp_path / "POSCAR"
    source.write_text(
        "\n".join(
            [
                "single H",
                "1",
                "1 0 0",
                "0 1 0",
                "0 0 1",
                "H",
                "1",
                "Direct",
                "0 0 0",
            ]
        ),
        encoding="utf-8",
    )

    calculation = parse(source)

    assert calculation.engine == "vasp"
    assert calculation.atom_count == 1

