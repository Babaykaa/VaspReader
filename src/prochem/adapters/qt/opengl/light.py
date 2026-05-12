"""Scene light control class."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

import numpy as np
from OpenGL.GL import *

__all__ = ["SceneLight", "Light"]


class SceneLight:
    """Scene light control class."""

    __gl_lights = {
        0: GL_LIGHT0,
        1: GL_LIGHT1,
        2: GL_LIGHT2,
        3: GL_LIGHT3,
        4: GL_LIGHT4,
        5: GL_LIGHT5,
        6: GL_LIGHT6,
        7: GL_LIGHT7,
    }

    def __init__(self, settings):
        """Scene light control class initialization function."""
        self.__settings = settings

        self.__lights = {
            idx: Light(
                idx,
                self.__gl_lights[idx],
                self.__settings.get_scene_params("light", "positions")[idx],
                self.__settings.get_scene_params("light", "intensities")[idx],
                self.__settings.get_scene_params("light", "states")[idx],
            )
            for idx in range(8)
        }

    def send_light_info(self, uniform_variables):
        """Sends light information to shader."""
        for light in self.__lights:
            self.__lights[light].send_light_info(uniform_variables)
        glUniform3f(uniform_variables[('Kd', 'vec3')], *self.__settings.get_scene_params('light', 'kd'))
        glUniform3f(uniform_variables[('Ka', 'vec3')], *self.__settings.get_scene_params('light', 'ka'))
        glUniform3f(uniform_variables[('Ks', 'vec3')], *self.__settings.get_scene_params('light', 'ks'))
        glUniform1f(uniform_variables[('Shininess', 'float')], self.__settings.get_scene_params('light', 'shininess'))


class Light:
    """Light class."""

    def __init__(self, light_index, gl_light, position, intensity, enabled=False):
        """Light class initialization function."""
        self.__light_index = light_index
        self.__gl_light = gl_light
        self.__position = position
        self.__intensity = intensity
        self.__enabled = enabled

    def send_light_info(self, uniform_variables):
        """Sends light information to shader."""
        glUniform4f(uniform_variables[(f'lights[{self.__light_index}].Position', '')], *self.__position)
        glUniform3f(uniform_variables[(f'lights[{self.__light_index}].Intensity', '')], *self.__intensity)
        glUniform1i(uniform_variables[(f'lights[{self.__light_index}].Enabled', '')], int(self.__enabled))
