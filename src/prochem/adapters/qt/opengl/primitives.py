"""Primitives class."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

import numpy as np
from prochem.adapters.qt.opengl.vao import VAO
from OpenGL.GL import *

__all__ = ["Primitive"]


class Primitive:
    """Primitive class."""
    __draw_types = {
        'TRIANGLES': GL_TRIANGLES,
        'TRIANGLE_STRIP': GL_TRIANGLE_STRIP,
        'LINES': GL_LINES,
        'QUADS': GL_QUADS
    }

    def __init__(
        self,
        vertices,
        normal,
        texture_indexes,
        indexes,
        draw_type='TRIANGLES',
        texture=None,
        usage='GL_STATIC_DRAW',
        target='GL_ARRAY_BUFFER'
    ):
        """Primitive class initialization function."""
        self.__vertex = vertices
        self.__normal = normal
        self.__texture_indexes = texture_indexes
        self.__indexes = indexes

        self.__draw_type = self.__draw_types[draw_type]
        self.__texture = texture
        self.__transformation_matrix = np.identity(4, dtype=np.float32)
        self.__vao_buffer = VAO((self.__vertex, self.__normal, self.__texture_indexes), self.__indexes, usage, target).create()

    def set_transformation_matrix(self, transformation_matrix) -> None:
        """Sets transformation matrix."""
        self.__transformation_matrix = transformation_matrix

    def get_transformation_matrix(self) -> np.ndarray:
        """Gets transformation matrix."""
        return self.__transformation_matrix

    def translate(self, dx, dy, dz) -> None:
        """Translates primitive."""
        self.__transformation_matrix[0][-1] = dx
        self.__transformation_matrix[1][-1] = dy
        self.__transformation_matrix[2][-1] = dz

    def scale(self, scale) -> None:
        """Scales primitive."""
        self.__transformation_matrix[3][-1] = 1 / scale

    def scale_x(self, scale) -> None:
        """Changes length of primitive in x direction."""
        self.__transformation_matrix[0][0] = scale

    def scale_y(self, scale) -> None:
        """Changes length of primitive in y direction."""
        self.__transformation_matrix[1][1] = scale

    def scale_z(self, scale) -> None:
        """Changes length of primitive in z direction."""
        self.__transformation_matrix[2][2] = scale

    def set_texture(self, texture):
        """Sets texture for primitive."""
        self.__texture = texture

    def draw(self, uniform_variables) -> None:
        """Draws primitive."""
        glUniformMatrix4fv(uniform_variables[('Translation', 'mat4')], 1, GL_TRUE, self.__transformation_matrix)
        
        glBindVertexArray(self.__vao_buffer.vao)
        self.__vao_buffer.get_indexes().bind()
        if self.__texture is not None:
            glActiveTexture(GL_TEXTURE0)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.__texture)
            glUniform1i(uniform_variables[('isTextureExist', 'int')], 1)
            glUniform1i(uniform_variables[('textureMap', 'sampler2D')], 0)
        glDrawElements(self.__draw_type, self.__indexes.shape[0], GL_UNSIGNED_INT, None)
        if self.__texture is not None:
            glBindTexture(GL_TEXTURE_2D, 0)
        self.__vao_buffer.get_indexes().unbind()
        glBindVertexArray(0)

