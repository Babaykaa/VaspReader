"""Vertex array object class."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

import numpy as np
import logging
import OpenGL
from OpenGL.GL import *
from OpenGL.arrays import vbo
from typing import Optional

OpenGL.ERROR_CHECKING = False
logger = logging.getLogger(__name__)

__all__ = ["VAO"]


class VAO:
    """Forms vertex buffer object from inputted arrays and creates vertex array object."""
    def __init__(self, array_elements: tuple[np.ndarray, ...], indexes: np.ndarray, usage='GL_STATIC_DRAW', target='GL_ARRAY_BUFFER'):  # GL_DYNAMIC_DRAW
        """Initializes VBO arrays of indexes and vertices, colors, normals, texCords."""
        self.vao = None
        self.array = np.array([])
        self.array_elements = tuple()
        self.element_size = 0
        self.elements_number = 0
        for index, element in enumerate(array_elements):
            if index == 0:
                element = element.astype(np.float32)
                self.elements_number = element.shape[0]
                self.array_elements = (element.shape[1], )
                self.element_size = element.itemsize
                self.array = element
            else:
                element = element.astype(np.float32)
                self.array_elements = self.array_elements + (element.shape[1], )
                self.array = np.concatenate((self.array, element), axis=1)
        self.dimension_size = sum(self.array_elements)
        self.array = vbo.VBO(self.array, usage, target)
        
        indexes = indexes.astype(np.uint32)
        self.indexes = vbo.VBO(indexes, usage, GL_ELEMENT_ARRAY_BUFFER)

    def __del__(self) -> None:
        """A rule for deleting a VAO object."""
        if glDeleteBuffers:
            self.array.delete()
            # if self.vao is not None and glDeleteVertexArrays:
            #     glDeleteVertexArrays(1, [self.vao])
            if self.indexes is not None:
                self.indexes.delete()

    def create(self) -> None:
        """Creates VAO buffer from VBO buffers and return the class object."""
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.array.bind()
        for index, size in enumerate(self.array_elements):
            glVertexAttribPointer(index, size, GL_FLOAT, GL_FALSE, self.dimension_size * self.element_size, self.array + (sum(self.array_elements[:index + 1]) - self.array_elements[index]) * self.element_size)  # ctypes.c_void_p(0)
            glEnableVertexAttribArray(index)
        self.array.unbind()
        glBindVertexArray(0)
        return self

    def get_indexes(self) -> Optional[vbo.VBO]:
        """Returns VBO indexes."""
        return self.indexes

    # def setFogParameters(self, uniform_variables, eyePosition, fogColor, fogMinDist, fogMaxDist, fogPower, fogDensity) -> None:
    #     """Loads fog settings into program."""
    #     self.load_uniform_vec3(uniform_variables[('EyePosition', 'vec3')], eyePosition)
    #     self.load_uniform_vec4(uniform_variables[('fog.FogColor', '=')], fogColor)
    #     # self.load_uniform_float(uniform_variables[('fog.FogMaxDist', '1')], fogMaxDist)
    #     # self.load_uniform_float(uniform_variables[('fog.FogMinDist', '1')], fogMinDist)
    #     self.load_uniform_int(uniform_variables[('fog.FogPower', '1')], fogPower)
    #     self.load_uniform_float(uniform_variables[('fog.FogDensity', '1')], fogDensity)


class VAOError(Exception):
    """Class for processing of errors in VAO class."""
    def __init__(self, message):
        """Initializing function."""
        super(VAOError, self).__init__(f'VAO error: {message}')
