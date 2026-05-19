"""ipywidgets helpers for interactive ProChem notebook views."""

from __future__ import annotations

from prochem.core.models import Calculation, Structure, StructureDataset, Structures
from prochem.rendering import SceneData, to_scene_data


def structures_slider(
    value: SceneData | Calculation | StructureDataset | Structures | Structure,
    *,
    atom_size_scale: float = 28.0,
):
    """Return a compact frame slider widget for SceneData-like inputs."""
    widgets = _widgets()
    go = _graph_objects()
    from prochem.adapters.jupyter.plotly import scene_figure

    scene = value if isinstance(value, SceneData) else to_scene_data(value)
    figure = go.FigureWidget(scene_figure(scene, frame_index=0, atom_size_scale=atom_size_scale))
    slider = widgets.IntSlider(
        value=0,
        min=0,
        max=max(scene.frame_count - 1, 0),
        step=1,
        description="frame",
        continuous_update=False,
    )

    def update(change) -> None:
        frame_index = change["new"]
        updated = scene_figure(scene, frame_index=frame_index, atom_size_scale=atom_size_scale)
        with figure.batch_update():
            figure.data = updated.data
            figure.layout.scene = updated.layout.scene

    slider.observe(update, names="value")
    return widgets.VBox([slider, figure])


def _widgets():
    try:
        import ipywidgets as widgets
    except ImportError as exc:
        raise RuntimeError("Install prochem[jupyter] to use notebook widgets.") from exc
    return widgets


def _graph_objects():
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise RuntimeError("Install prochem[jupyter] to use Plotly notebook rendering.") from exc
    return go


__all__ = ["structures_slider"]

