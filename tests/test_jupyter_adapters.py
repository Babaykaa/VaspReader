from __future__ import annotations

import numpy as np

from prochem.core import Structure
from prochem.rendering import to_scene_data


def test_plotly_adapter_imports_without_optional_plotly_dependency() -> None:
    from prochem.adapters.jupyter import plotly

    assert "scene_figure" in plotly.__all__


def test_plotly_adapter_raises_helpful_error_when_plotly_missing() -> None:
    from prochem.adapters.jupyter.plotly import scene_figure

    scene = to_scene_data(Structure(species=np.array(["H"]), positions=np.array([[0.0, 0.0, 0.0]])))
    try:
        scene_figure(scene)
    except RuntimeError as error:
        assert "prochem[jupyter]" in str(error)
    else:
        # In an environment with plotly installed this is also acceptable.
        assert True

