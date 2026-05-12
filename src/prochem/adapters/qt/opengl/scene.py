"""Scene formation and visualization class."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

import numpy as np
from OpenGL.GL import *
from PySide6.QtGui import QImage
from PIL import Image, ImageQt
from prochem.adapters.qt.opengl.camera import Camera
from prochem.adapters.qt.opengl.light import SceneLight
from prochem.adapters.qt.opengl.axes import Axes
from prochem.adapters.qt.opengl.primitives import Primitive
from prochem.adapters.qt.opengl.jit_functions.visual import *
from prochem.adapters.qt.opengl.jit_functions.primitives import *

__all__ = ["Scene"]


class Scene:
    """Scene class."""
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Scene class constructor."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, settings):
        """Scene class initialization function."""
        if not self._initialized:
            self.__settings = settings
            self.__camera = Camera(self.__settings)
            self.__light = SceneLight(self.__settings)
            self.__axes = Axes(self.__settings)
            self.__primitives = {
                'Logo': Primitive(*Quad(5)),
                'Sphere': Primitive(*Sphere(1.0, 32, 32)),
                'Quad': Primitive(*Quad(1)),
                'Cube': Primitive(*Cube(1)),
                'Torus': Primitive(*Torus(1, 1.0, 0.5, 32, 32)),
                'Tube': Primitive(*Tube(1, 0.5, 32)),
                'Cone': Primitive(*Cone(1, 0.5, 32))
            }
            self.__draw_buffer = dict()
            self.__texture = dict()

            self.__rotation_matrix = np.identity(4, dtype=np.float32)
            self.__translation_matrix = np.identity(4, dtype=np.float32)
            self._initialized = True

    def set_draw_buffer(self, draw_buffer):
        """
        Sets the draw buffer.
        
        Args:
         draw_buffer: The draw buffer to set.
        
        Returns:
         None
        """
        self.__draw_buffer = draw_buffer

    def update_camera(self):
        """Updates camera."""
        self.__camera.set_orthographic_matrix()
        self.__camera.set_perspective_matrix()
        self.__camera.set_view_matrix()

    def update_lights(self):
        """Updates lights."""
        pass

    def rotate(self, dx, dy, dz):
        """Rotates scene."""
        self.__rotation_matrix = rotate(self.__rotation_matrix, dx, dy, dz)

    def move_x(self, dx):
        """Moves scene in x direction."""
        self.__translation_matrix[0][-1] += dx

    def move_y(self, dy):
        """Moves scene in y direction."""
        self.__translation_matrix[1][-1] += dy

    def move_z(self, dz):
        """Moves scene in z direction."""
        self.__translation_matrix[2][-1] += dz

    def scale(self, scale):
        """Scales scene."""
        self.__translation_matrix[3][-1] /= scale

    def reset_scene_matrices(self):
        """Resets scene matrices."""
        self.__translation_matrix = np.identity(4, dtype=np.float32)
        self.__rotation_matrix = np.identity(4, dtype=np.float32)

    def load_texture(self, image, is_qtype=True, texture_name="default"):
        """
        Loads a texture from an image file or QImage.
        
        Args:
            image: The image file path or QImage object to load.
            is_qtype:  A boolean indicating whether the image is a QImage. Defaults to True.
            texture_name: The name to assign to the loaded texture. Defaults to "default".
        
        Returns:
            None
        """
        img = None
        if is_qtype:
            img = QImage(image)  # ":/icons/logo/PROCHEM-logo.png"
            img = ImageQt.fromqimage(img)
        else:
            img = Image.open(
                image
            )  # os.path.join(self.__project_directory, "icons", "logo", "PROCHEM-logo.png")
        img = img.convert("RGBA")

        self.__texture[texture_name] = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.__texture[texture_name])

        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, [1.0, 1.0, 1.0, 1.0])

        glTexParameteri(
            GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR
        )  # position 3 possible parameters: GL_NEAREST, GL_LINEAR
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            img.width,
            img.height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            img.tobytes(),
        )
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)

    def draw(self, program=None, mouse_moving=False):
        """Draws scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(*self.__settings.get_scene_params('background', 'color'))
        glUniformMatrix4fv(program.uniform_variables[('Rotation', 'mat4')], 1, GL_TRUE, self.__translation_matrix @ self.__rotation_matrix)
        
        self.__camera.send_info_to_shader(program.uniform_variables)
        self.__light.send_light_info(program.uniform_variables)
        
        if self.__draw_buffer:
            # NOTE: draw_buffer structure: {'Sphere': {(color, scale): [[[x, y, z], [x, y, z], ..., [x, y, z]], [[x, y, z], [x, y, z], ..., [x, y, z]]]}}
            if mouse_moving:
                self.__axes.draw(program.uniform_variables)
            for key in self.__draw_buffer:
                for (color, scale) in self.__draw_buffer[key]:
                    glUniform3f(program.uniform_variables[('ObjColor', 'vec3')], *color)
                    self.__primitives[key].scale(scale)
                    for (x, y, z) in self.__draw_buffer[key][(color, scale)]:
                        self.__primitives[key].translate(x, y, z)
                        self.__primitives[key].draw(program.uniform_variables)
        else:
            glUniform3f(program.uniform_variables[('ObjColor', 'vec3')], *[0.2, 0.2, 0.2])
            self.__primitives['Logo'].set_texture(self.__texture['default'])
            self.__primitives['Logo'].translate(0, 0, 0)
            self.__primitives['Logo'].draw(program.uniform_variables)
