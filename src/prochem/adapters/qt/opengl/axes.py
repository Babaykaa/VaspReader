"""Axes class. Cointains primitives which are used to draw axes."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

from OpenGL.GL import *
from prochem.adapters.qt.opengl.primitives import Primitive
from prochem.adapters.qt.opengl.jit_functions.primitives import *
from prochem.adapters.qt.opengl.jit_functions.visual import *

__all__ = ["Axes"]


class Axes:
    """Axes class."""

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Axes class constructor."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, settings):
        """Axes class initialization function."""
        if not self._initialized:
            self.__settings = settings
            self.__axes_primitives = {
                "center": Primitive(*Sphere(0.25, 64, 64)),
                "x_tube": Primitive(*Tube(0.22, 2.0, 64)),
                "x_cone": Primitive(*Cone(0.35, 0.5, 64)),
                "y_tube": Primitive(*Tube(0.22, 2.0, 64)),
                "y_cone": Primitive(*Cone(0.35, 0.5, 64)),
                "z_tube": Primitive(*Tube(0.22, 2.0, 64)),
                "z_cone": Primitive(*Cone(0.35, 0.5, 64))
            }
            for key, primitive in self.__axes_primitives.items():
                match key:
                    case "x_tube":
                        primitive.set_transformation_matrix(rotate(primitive.get_transformation_matrix(), 0.0, 90.0, 0.0))
                    case "x_cone":
                        primitive.translate(2.0, 0.0, 0.0)
                        primitive.set_transformation_matrix(rotate(primitive.get_transformation_matrix(), 0.0, 90.0, 0.0))
                    case "y_tube":
                        primitive.set_transformation_matrix(rotate(primitive.get_transformation_matrix(), -90.0, 0.0, 0.0))
                    case "y_cone":
                        primitive.translate(0.0, 2.0, 0.0)
                        primitive.set_transformation_matrix(rotate(primitive.get_transformation_matrix(), -90.0, 0.0, 0.0))
                    case "z_cone":
                        primitive.translate(0.0, 0.0, 2.0)
            self._initialized = True

    def move_axes(self, x, y, z):
        """Moves axes."""
        for key, primitive in self.__axes_primitives.items():
            match key:
                case "x_cone":
                    primitive.translate(x + 2.0, y, z)
                case "y_cone":
                    primitive.translate(x, y + 2.0, z)
                case "z_cone":
                    primitive.translate(x, y, z + 2.0)
                case _:
                    primitive.translate(x, y, z)

    def draw(self, uniform_variables) -> None:
        """Draws axes."""
        for key, primitive in self.__axes_primitives.items():
            if "x" in key:
                glUniform3f(uniform_variables[('ObjColor', 'vec3')], 1.0, 0.0, 0.0)
            elif "y" in key:
                glUniform3f(uniform_variables[('ObjColor', 'vec3')], 0.0, 1.0, 0.0)
            elif "z" in key:
                glUniform3f(uniform_variables[('ObjColor', 'vec3')], 0.0, 0.0, 1.0)
            else:
                glUniform3f(uniform_variables[('ObjColor', 'vec3')], 0.0, 0.0, 0.0)
            primitive.draw(uniform_variables)
