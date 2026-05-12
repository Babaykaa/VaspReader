"""Jupyter widget adapter entry points."""

from __future__ import annotations

from prochem.core.models import Calculation


def trajectory_widget(calculation: Calculation):
    """Return a widget for a calculation trajectory.

    The concrete ipywidgets UI will be implemented after the core rendering DTOs
    are stabilized.
    """
    raise NotImplementedError("Jupyter widgets adapter is not implemented yet.")

