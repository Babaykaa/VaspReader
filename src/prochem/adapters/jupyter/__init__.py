"""Jupyter and notebook adapters."""

from prochem.adapters.jupyter.plotly import (
    calculation_figure,
    scene_animation,
    scene_figure,
    structure_figure,
    structures_figure,
)
from prochem.adapters.jupyter.widgets import structures_slider

__all__ = [
    "calculation_figure",
    "scene_animation",
    "scene_figure",
    "structure_figure",
    "structures_figure",
    "structures_slider",
]
