"""Camera class."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

from OpenGL.GL import *
from prochem.adapters.qt.opengl.jit_functions.visual import *
import numpy as np

__all__ = ["Camera"]


class Camera:
    """Camera class."""
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Camera class constructor."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, settings):
        """Camera class initialization function."""
        if not self._initialized: 
            self.__settings = settings
            
            self.set_view_matrix()
            self.set_perspective_matrix()
            self.set_orthographic_matrix()
            self.set_projection_matrix()
            self._initialized = True

    def get_projection_matrix(self) -> np.ndarray:
        """Returns projection matrix."""
        return self.__projection_matrix

    def get_view_matrix(self) -> np.ndarray:
        """Returns view matrix."""
        return self.__view_matrix

    def set_perspective_matrix(self) -> None:
        """Sets perspective matrix and projection matrix if camera object is initialized."""
        self.__perspective_matrix = perspective(self.__settings.get_scene_params('view', 'perspective', 'fov'),
                                                self.__settings.get_scene_params('view', 'perspective', 'aspect'),
                                                self.__settings.get_scene_params('view', 'projection', 'near'),
                                                self.__settings.get_scene_params('view', 'projection', 'far'))
        if self.__settings.get_scene_params('view', 'is_perspective'):
            self.set_projection_matrix()

    def set_orthographic_matrix(self) -> None:
        """Sets orthographic matrix and projection matrix if camera object is initialized."""
        self.__orthographic_matrix = ortho(self.__settings.get_scene_params('view', 'ortho', 'left'),
                                           self.__settings.get_scene_params('view', 'ortho', 'right'),
                                           self.__settings.get_scene_params('view', 'ortho', 'top'),
                                           self.__settings.get_scene_params('view', 'ortho', 'bottom'),
                                           self.__settings.get_scene_params('view', 'projection', 'near'),
                                           self.__settings.get_scene_params('view', 'projection', 'far'))
        if not self.__settings.get_scene_params('view', 'is_perspective'):
            self.set_projection_matrix()

    def set_projection_matrix(self) -> None:
        """Sets projection matrix."""
        self.__projection_matrix = self.__perspective_matrix if self.__settings.get_scene_params('view', 'perspective') else self.__orthographic_matrix

    def set_view_matrix(self) -> None:
        """Sets view matrix."""
        self.__view_matrix = look_at(self.__settings.get_scene_params('view', 'eye_position'),
                                     self.__settings.get_scene_params('view', 'center'),
                                     self.__settings.get_scene_params('view', 'up'))

    def send_info_to_shader(self, uniform_variables):
        """Sends camera information to shader."""
        glUniformMatrix4fv(uniform_variables[('View', 'mat4')], 1, GL_TRUE, self.__view_matrix)
        glUniformMatrix4fv(uniform_variables[('Projection', 'mat4')], 1, GL_TRUE, self.__projection_matrix)
