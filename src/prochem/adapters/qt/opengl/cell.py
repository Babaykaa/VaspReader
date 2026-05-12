"""Cell class. Cointains custom cube primitive which are used to draw cell."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

from prochem.adapters.qt.opengl.primitives import Primitive
from prochem.adapters.qt.opengl.jit_functions.primitives import Parallelepiped, Cube
import numpy as np

__all__ = ["Cell"]


class Cell:
    """Cell class."""

    def __init__(self, vec_x, vec_y, vec_z, settings):
        """Cell class initialization function."""
        self.__settings = settings
        self.__cell_primitive = Primitive(
            *Parallelepiped(vec_x, vec_y, vec_z, draw_type="LINES"), [1.0, 0.0, 0.0]
        )
        self.__cell_primitive.scale(3)

    def draw(self, uniform_variables) -> None:
        """Draws cell."""
        self.__cell_primitive.draw(uniform_variables)
