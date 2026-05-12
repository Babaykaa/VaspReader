"""Plotly adapter entry points."""

from __future__ import annotations

from prochem.rendering.scene import SceneData


def scene_figure(scene: SceneData):
    raise NotImplementedError("Plotly scene adapter is not implemented yet.")

