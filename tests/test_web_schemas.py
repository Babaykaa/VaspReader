from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("pydantic", minversion="2.0")

from prochem.adapters.web.schemas import (  # noqa: E402
    CalculationSummary,
    ParseRequestSchema,
    SceneDataSchema,
    SceneOptionsSchema,
)
from prochem.core import Calculation, Cell, Structure, Trajectory  # noqa: E402
from prochem.rendering import to_scene_data  # noqa: E402


def test_scene_data_schema_serializes_scene_json_contract() -> None:
    structure = Structure(
        species=np.array(["H", "H"]),
        positions=np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]]),
        cell=Cell(np.eye(3)),
    )
    scene = to_scene_data(structure, name="h2")

    schema = SceneDataSchema.from_scene_data(scene)
    payload = schema.model_dump(mode="json")

    assert payload["name"] == "h2"
    assert payload["frame_count"] == 1
    assert payload["frames"][0]["atoms"][0]["position"] == [0.0, 0.0, 0.0]
    assert payload["frames"][0]["atoms"][0]["color"] == [1.0, 1.0, 1.0, 1.0]
    assert payload["frames"][0]["cell"]["vectors"][0] == [1.0, 0.0, 0.0]


def test_scene_options_schema_returns_rendering_kwargs() -> None:
    options = SceneOptionsSchema(
        frame_indices=[0, 2],
        include_bonds=False,
        max_atoms_for_bonds=0,
    )

    kwargs = options.to_scene_kwargs()

    assert kwargs["frame_indices"] == (0, 2)
    assert kwargs["include_bonds"] is False
    assert kwargs["max_atoms_for_bonds"] == 0


def test_calculation_summary_schema_from_trajectory_calculation() -> None:
    trajectory = Trajectory.from_arrays(
        species=np.array(["C"]),
        positions=np.array([[[0.0, 0.0, 0.0]], [[1.0, 0.0, 0.0]]]),
    )
    calculation = Calculation(
        source="vasprun.xml",
        engine="vasp",
        trajectory=trajectory,
        warnings=["synthetic"],
    )

    summary = CalculationSummary.from_calculation(calculation)

    assert summary.name == "vasprun.xml"
    assert summary.engine == "vasp"
    assert summary.kind == "trajectory"
    assert summary.step_count == 2
    assert summary.structure_count == 2
    assert summary.atom_count == 1
    assert summary.warnings == ["synthetic"]


def test_parse_request_schema_serializes_path_and_default_scene_options() -> None:
    request = ParseRequestSchema(path="calculation/vasprun.xml")
    payload = request.model_dump(mode="json")

    assert payload["path"] == "calculation/vasprun.xml"
    assert payload["parser"] is None
    assert payload["scene"]["include_bonds"] is True
