"""Jupyter and notebook adapters."""

from prochem.adapters.jupyter.plotly import (
    calculation_figure,
    scene_animation,
    scene_figure,
    structure_figure,
    trajectory_figure,
)
from prochem.adapters.jupyter.widgets import trajectory_slider

__all__ = [
    "calculation_figure",
    "scene_animation",
    "scene_figure",
    "structure_figure",
    "trajectory_figure",
    "trajectory_slider",
]
