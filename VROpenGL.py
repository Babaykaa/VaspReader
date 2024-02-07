import OpenGL
import traceback
import numpy as np
import math
import os
from os import environ
from PIL import ImageGrab
from VRPrimitives import Primitives
import win32gui
import ctypes
import json
import random
import threading
import freetype as ft
import time
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.WGL import *
from OpenGL.arrays import vbo
import glm
import pygame
from pygame.locals import *
from PIL import Image
from VRMD import VRMD


class VRShaders:
    """VaspReader shaders compile class. Union shader files into programs for next using in VaspReaderCore."""
    VERTEX = GL_VERTEX_SHADER
    FRAGMENT = GL_FRAGMENT_SHADER
    GEOMETRY = GL_GEOMETRY_SHADER
    TESS_CONTROL = GL_TESS_CONTROL_SHADER
    TESS_EVALUATION = GL_TESS_EVALUATION_SHADER
    COMPUTE = GL_COMPUTE_SHADER

    def __init__(self, directory: str, shader_files: list[str], shader_types: list[str]):
        """Initialize function of class. Requires directory of shader files, list of string names of shaders
        for next form pathnames of files and shaders type: VERTEX, FRAGMENT, GEOMETRY, TESS_CONTROL, TESS_EVALUATION
        or COMPUTE. Please always check positions of files and types of shaders in list."""
        self.program = 0
        self.shaders = dict()
        self.uniform_variables_dict = dict()
        self.subroutine_variables = dict()
        self.directory = directory
        self.shader_files = shader_files
        self.shader_types = shader_types
        self.define_shaders_types(self.shader_types)
        for index, file in enumerate(shader_files):
            self.compyle_shader(file, self.shader_types[index])
        self.create_shader_program()
        self.search_for_uniform_variables()

    def define_shaders_types(self, array):
        for index, s_type in enumerate(list(array)):
            if s_type == 'VERTEX':
                array[index] = self.VERTEX
            elif s_type == 'FRAGMENT':
                array[index] = self.FRAGMENT
            elif s_type == 'GEOMETRY':
                array[index] = self.GEOMETRY
            elif s_type == 'TESS_CONTROL':
                array[index] = self.TESS_CONTROL
            elif s_type == 'TESS_EVALUATION':
                array[index] = self.TESS_EVALUATION
            elif s_type == 'COMPUTE':
                array[index] = self.COMPUTE
            else:
                raise VRShaderError('Error in names of shader types.')

    def compyle_shader(self, file, shader_type):
        shader = glCreateShader(shader_type)
        if shader == 0:
            raise VRShaderError('Cannot load shader.')
        glShaderSource(shader, self.load_shader_info(file))
        glCompileShader(shader)
        status = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not status:
            raise VRShaderError(f'Error while compiling {shader_type} shader.')
        self.shaders[shader] = True

    def load_shader_info(self, file):
        path = f'{self.directory}\\{file}'
        try:
            f = open(path, 'r', encoding="utf-8", errors='ignore')
        except:
            raise VRShaderError(f'File {path} does not exist.')
        else:
            f.close()
        shader_source = ""
        with open(path) as f:
            shader_source = f.read()
        return str.encode(shader_source)

    def delete_shader(self, shader):
        if shader in self.shaders:
            glDeleteShader(shader)
            self.shaders[shader] = False

    def create_shader_program(self):
        self.program = glCreateProgram()
        if not self.program:
            raise VRShaderError('Cannot create program.')
        for shader in self.shaders:
            if self.shaders[shader]:
                glAttachShader(self.program, shader)  # Connect shaders into program
        glLinkProgram(self.program)  # Join the flats program
        status = glGetProgramiv(self.program, GL_LINK_STATUS)
        if not status:
            raise VRShaderError('Error with linking program.')

    def delete_program(self):
        if self.program:
            glDeleteProgram(self.program)
            self.program = 0

    def __add__(self, other: list[str, str]):
        try:
            file, shader_type = other
        except:
            raise VRShaderError('Add function requires pair of file, shader type.')
        self.shader_files.append(file)
        shader_type = [shader_type]
        self.define_shaders_types(shader_type)
        self.shader_types.append(*shader_type)

    def delete_shader_file(self, file):
        ind = self.shader_files.index(file)
        self.shader_files.pop(ind)
        self.shader_types.pop(ind)

    def search_for_uniform_variables(self):
        numUniforms = glGetProgramInterfaceiv(self.program, GL_UNIFORM, GL_ACTIVE_RESOURCES)
        types = [GL_NAME_LENGTH, GL_TYPE, GL_LOCATION, GL_BLOCK_INDEX]
        for i in range(numUniforms):
            # results = np.zeros(4)
            results = glGetProgramResourceiv(self.program, GL_UNIFORM, i, 4, types, 4, None)[-1]
            if results[-1] != -1:
                continue
            nameBufSize = results[0] + 1
            name = glGetProgramResourceName(self.program, GL_UNIFORM, i, nameBufSize, None)[-1]
            name = ''.join([chr(int(el)) for el in name][:-2])
            type_name = ''
            for file in self.shader_files:
                with open(f'{self.directory}\\{file}', 'r') as f:
                    while True:
                        line = f.readline()
                        if not line:
                            break
                        if name in line:
                            type_name = line.split()[1]
                            break
                if type_name:
                    break
            self.uniform_variables_dict[(name, type_name)] = results[2]

    def search_subroutine_location(self, variable_name, variable, shader: [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, ...]):
        if self.subroutine_variables.get(variable_name, None) is not None:
            self.subroutine_variables.pop(variable_name)
        self.subroutine_variables[variable_name] = glGetSubroutineIndex(self.program, shader, variable)

    def __call__(self):
        return self.program


class VRShaderError(Exception):
    def __init__(self, message):
        super(VRShaderError, self).__init__('Error in VRShaders occurs.\nMessage:' + message)


class VRVBO:
    """Form vertex buffer object from inputted arrays."""
    def __init__(self, array_elements: tuple[np.ndarray, ...], indexes: np.ndarray = None, usage='GL_STATIC_DRAW', target='GL_ARRAY_BUFFER'):  # GL_DYNAMIC_DRAW
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
        self.indexes = None
        if indexes is not None:
            self.elements_number = len(indexes)
            self.indexes = vbo.VBO(indexes, usage, GL_ELEMENT_ARRAY_BUFFER)

    def __del__(self):
        self.array.delete()
        if self.vao is not None:
            glDeleteVertexArrays(1, [self.vao])
        if self.indexes is not None:
            self.indexes.delete()

    def create_vao_buffer(self):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.array.bind()
        for index, size in enumerate(self.array_elements):
            glVertexAttribPointer(index, size, GL_FLOAT, GL_FALSE, self.dimension_size * self.element_size, self.array + (sum(self.array_elements[:index + 1]) - self.array_elements[index]) * self.element_size)  # ctypes.c_void_p(0)
            glEnableVertexAttribArray(index)
        self.array.unbind()
        glBindVertexArray(0)
        return self

    def load_uniform_vec4(self, location, vec4):
        glUniform4f(location, *vec4)

    def load_uniform_vec3(self, location, vec3):
        glUniform3f(location, *vec3)

    def load_uniform_mat4(self, location, mat4):
        glUniformMatrix4fv(location, 1, GL_TRUE, mat4)

    def load_uniform_mat3(self, location, mat3):
        glUniformMatrix3fv(location, 1, GL_TRUE, mat3)

    def load_uniform_float(self, location, u_float):
        glUniform1f(location, u_float)

    def define_uniform_variable_type(self, var_type):
        if var_type == 'vec4':
            return self.load_uniform_vec4
        elif var_type == 'vec3':
            return self.load_uniform_vec3
        elif var_type == 'mat3':
            return self.load_uniform_mat3
        elif var_type == 'mat4':
            return self.load_uniform_mat4
        elif var_type == 'float':
            return self.load_uniform_float
        else:
            raise VRShaderError('Undefined shader variable type.')

    def prepare_to_draw(self, program):
        glUseProgram(program)
        glBindVertexArray(self.vao)

    def end_of_drawing(self):
        glBindVertexArray(0)
        glUseProgram(0)

    def set_light_settings(self, uniform_variables_dict, Ka, Kd, Ks, Shininess, lightPositions, lightIntensities):
        for index, position in enumerate(lightPositions):
            self.load_uniform_vec4(uniform_variables_dict[(f'lights[{index}].Position', '')], position)
            self.load_uniform_vec3(uniform_variables_dict[(f'lights[{index}].Intensity', '')], lightIntensities[index])
        self.load_uniform_vec3(uniform_variables_dict[('Kd', 'vec3')], Kd)
        self.load_uniform_vec3(uniform_variables_dict[('Ka', 'vec3')], Ka)
        self.load_uniform_vec3(uniform_variables_dict[('Ks', 'vec3')], Ks)
        self.load_uniform_float(uniform_variables_dict[('Shininess', 'float')], Shininess)

    def draw_from_vao_buffer(self, primitive_type, uniform_variables_dict, texture='', ModelMatrix='', ViewMatrix='', ProjectionMatrix='', NormalMatrix='', TranslationMatrix=''):
        self.load_uniform_mat4(uniform_variables_dict[('ModelMatrix', 'mat4')], ModelMatrix)
        self.load_uniform_mat4(uniform_variables_dict[('ViewMatrix', 'mat4')], ViewMatrix)
        self.load_uniform_mat4(uniform_variables_dict[('ProjectionMatrix', 'mat4')], ProjectionMatrix)
        self.load_uniform_mat3(uniform_variables_dict[('NormalMatrix', 'mat3')], NormalMatrix)
        self.load_uniform_mat4(uniform_variables_dict[('TranslationMatrix', 'mat4')], TranslationMatrix)
        if self.indexes is not None:
            self.indexes.bind()
        if texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture)
        glDrawElements(primitive_type, self.elements_number, GL_UNSIGNED_INT, None)
        if texture:
            glBindTexture(GL_TEXTURE_2D, 0)
        if self.indexes is not None:
            self.indexes.unbind()


class VROpenGL:
    __default_display = (800, 600)
    __light_variables = (GL_LIGHT0, GL_LIGHT1, GL_LIGHT2, GL_LIGHT3, GL_LIGHT4, GL_LIGHT5, GL_LIGHT6, GL_LIGHT7)
    __light_states = {i: False for i in range(8)}
    __light_positions = [[10, 10, 10], [10, 10, -10], [10, -10, 10], [10, -10, -10], [-10, 10, 10], [-10, 10, -10],
                         [-10, -10, 10], [-10, -10, -10]]
    __view_axes = True
    __view_cell_border = True
    __draw_type = GL_TRIANGLES
    __calculation = dict()
    __primitives = {'Primitive': Primitives(1, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]).Cube(__draw_type)}
    __background_color = (0.6, 0.6, 0.6)

    def __init__(self):
        self.__display, self.window_size = list(self.__default_display), list(self.__default_display)
        self.__view_matrix = self.m3dLookAt(np.array([0.0, 20.0, 0.0]), np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0]))
        self.__projection_matrix = self.build_projection_matrix(self.__display[0], self.__display[1], 0, 45, 0.1, 60)
        self._x_d, self._y_d, self._z_d, self._scale_parameter = 0.0, 0.0, 0.0, 1.0
        self.euler_rotation_matrix = np.array([[-1.0, 0.0, 0.0, 0.0],
                                               [0.0, 0.0, 1.0, 0],
                                               [0.0, -1.0, 0.0, 0.0],
                                               [self._x_d, self._y_d, self._z_d, self._scale_parameter]],
                                              dtype='f')
        self.__translation_matrix = np.array([[1.0, 0.0, 0.0, 0.0],
                                            [0.0, 1.0, 0.0, 0.0],
                                            [0.0, 0.0, 1.0, 0.0],
                                            [0.0, 0.0, 0.0, 1.0]], dtype='f')
        self.model_view_matrix, self.MVP, self.normal_matrix = None, None, None
        self.mouse_pressed, self.Back_Step, self.Forward_Step, self.only_keyboard_select, self.calculation_parsed, self.draw_cell, self.draw_axes = False, False, True, False, False, True, True
        self.display_scaling, self._step = 1.0, 0
        self.new_coordinate_start = None
        self.rotation_info, self.default_cube_position = [0, 0], [[0, 0, 0]]
        self._Buffers_Labels = []
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        pygame.init()
        try:
            self.__win_icon = r'VR_icons/VR-logo.png'
            pygame.display.set_icon(pygame.image.load(self.__win_icon))
        except FileNotFoundError:
            pass
        pygame.display.set_caption('VaspReader')
        self.__scree = pygame.display.set_mode(self.__default_display, DOUBLEBUF | OPENGL | pygame.RESIZABLE)

        glMatrixMode(GL_PROJECTION)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1, 1, 1, 1])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 128.0)

        gluPerspective(45, (self.__default_display[0] / self.__default_display[1]), 0.1, 60.0)
        gluLookAt(0, 20, 0, 0, 0, 0, 0, 0, 1)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        self.__DisplayCenter = [self.__scree.get_size()[i] // 2 for i in range(2)]
        pygame.mouse.set_pos(self.__DisplayCenter)
        self.__program = VRShaders(r'Shaders', [r'vertex_shader.glsl', r'fragment_shader.glsl'], ['VERTEX', 'FRAGMENT'])
        self._VBO_Buffers = [VRVBO(self.__primitives['Primitive'][:-1], self.__primitives['Primitive'][-1]).create_vao_buffer()]

        if not self.__light_states[0]:
            self.change_light(0, self.__light_positions[0])
        else:
            glEnable(self.__light_variables[0])
            glLight(self.__light_variables[0], GL_POSITION, (*self.__light_positions[0], 1))
            glLightfv(self.__light_variables[0], GL_AMBIENT, [0.1, 0.1, 0.1, 1])
            glLightfv(self.__light_variables[0], GL_DIFFUSE, [1, 1, 1, 1])
            glLightfv(self.__light_variables[0], GL_SPECULAR, [1, 1, 1, 1])

    def change_light(self, light_variable_number, light_position):
        self.__light_states[light_variable_number] = not self.__light_states[light_variable_number]
        if self.__light_states[light_variable_number]:
            glEnable(self.__light_variables[light_variable_number])
            glLight(self.__light_variables[light_variable_number], GL_POSITION, (*light_position, 1))
            glLightfv(self.__light_variables[light_variable_number], GL_AMBIENT, [0.1, 0.1, 0.1, 1])
            glLightfv(self.__light_variables[light_variable_number], GL_DIFFUSE, [1, 1, 1, 1])
            glLightfv(self.__light_variables[light_variable_number], GL_SPECULAR, [1, 1, 1, 1])
        else:
            glDisable(self.__light_variables[light_variable_number])

    def find_window_dimensions(self, far):
        far = 20 + far
        x_limit = math.sin(math.pi / 16 * 3) * far
        y_limit = x_limit / 4 * 3
        if self.window_size[0] / 4 < self.window_size[1] / 3:
            x_limit = x_limit * (self.window_size[0] / self.__display[0])
        else:
            y_limit = y_limit * (self.window_size[1] / self.__display[1])
        return x_limit, y_limit, -(far - 20)

    def change_light_position(self, new_position, light_index):
        self.__light_positions[light_index] = new_position

    @staticmethod
    def build_projection_matrix(scree_width, scree_height, eye_point, fov, near, far):
        """Build the projection matrix according to the formula:
        f / aspect     , 0.0             , 0.0                            , 0.0
        0.0            , f               , 0.0                            , 0.0
        0.0            , 0.0             , (far + near) / (near - far)    , -1.0
        0.0            , 0.0             , 2.0 * far * near / (near - far), 0.0
        where f = 1 / tg(fov / 2.0), aspect = scree_width / scree_height."""
        aspect = scree_width / float(scree_height)
        fov = math.radians(fov)
        f = 1 / math.tan(fov / 2.0)
        pMatrix = np.array([[f / aspect, 0.0, 0.0, 0.0],
                            [0.0, f, 0.0, 0.0],
                            [0.0, 0.0, -(far + (abs(eye_point) + near)) / (far - (abs(eye_point) + near)), -1.0],
                            [0.0, 0.0, -2.0 * far * (abs(eye_point) + near) / (far - (abs(eye_point) + near)), 0.0]], np.float32)
        return pMatrix

    @staticmethod
    def GL_version():
        renderer = glGetString(GL_RENDERER)
        vendor = glGetString(GL_VENDOR)
        version = glGetString(GL_VERSION)

        return vendor.decode(), renderer.decode(), version.decode()
        # print(f"GL Vendor : {vendor.decode()}")
        # print(f"GL Renderer : {renderer.decode()}")
        # print(f"GL Version : {version.decode()}")

    @staticmethod
    def m3dLookAt(eye, target, up):
        """Define view matrix: eye - eye position (x, y, z), target - position where eye is looking, up - normal vector definition."""
        res_vec = eye - target
        res_vec = res_vec / np.linalg.norm(res_vec)
        mz = [*res_vec]  # inverse line of sight
        mx = np.cross(up, mz)
        my = np.cross(mz, mx)
        tx = np.dot(mx, eye)
        ty = np.dot(my, eye)
        tz = -np.dot(mz, eye)
        return np.array(
            [mx[0], my[0], mz[0], tx, mx[1], my[1], mz[1], ty, mx[2], my[2], mz[2], tz, 0, 0, 0, 1]).reshape((4, 4))

    def display_resize(self, event):
        self.__display = [int(event.w), int(event.h)]
        self.window_size = [int(event.w), int(event.h)]
        difference = [int(self.__display[i] - self.__default_display[i]) for i in range(2)]
        if difference[0] > difference[1]:
            self.__display[1] = self.__default_display[1] + int(difference[0] * 3 / 4)
        elif difference[0] < difference[1]:
            self.__display[0] = self.__default_display[0] + int(difference[1] * 4 / 3)
        self.display_scaling = self.__display[0] / self.__default_display[0]

        nlw = (event.w - self.__display[0]) // 2
        nlh = (event.h - self.__display[1]) // 2

        self._displayCenter = [event.w // 2, event.h // 2]
        self.new_coordinate_start = [nlw, nlh]
        glViewport(nlw, nlh, self.__display[0], self.__display[1])

    def load_calculation_info(self, calculation):
        self.__calculation = calculation
        self.__primitives.clear()
        self._VBO_Buffers.clear()
        self._Buffers_Labels.clear()
        for _, atom in enumerate(calculation['ATOMSINFO']):
            self.__primitives[atom] = Primitives(1, calculation['ATOMSINFO'][atom]['COLORVALUE']).Sphere(calculation['ATOMSINFO'][atom]['RADII'], 64, 64)
        for _, key in enumerate(self.__primitives):
            self._VBO_Buffers.append(VRVBO(self.__primitives[key][:-1], self.__primitives[key][-1]).create_vao_buffer())
            self._Buffers_Labels.append(key)

    def without_calculation(self):
        self.__calculation = None
        self.__primitives.clear()
        self._VBO_Buffers.clear()
        self._Buffers_Labels.clear()
        self.__primitives = {'Primitive': Primitives(1, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]).Cube(self.__draw_type)}
        self._VBO_Buffers.append(VRVBO(self.__primitives['Primitive'][:-1], self.__primitives['Primitive'][-1]).create_vao_buffer())

    def cell_draw(self, cell, draw_cell=False, draw_axes=False, line_width=3):
        """Draw cell of model."""
        edges = ((0, 1), (0, 3), (0, 4), (2, 1), (2, 3), (2, 7), (6, 3), (6, 4), (6, 7), (5, 1), (5, 4), (5, 7)) if not draw_axes else ((0, 1), (0, 4), (2, 1), (2, 7), (6, 4), (6, 7), (5, 1), (5, 4), (5, 7))
        glLineWidth(line_width)
        glBegin(GL_LINES)
        if draw_cell:
            for edge in edges:
                for vertex in edge:
                    glColor4f(1.0, 1.0, 0.0, 1.0)
                    glVertex3fv(cell[vertex])
        if draw_axes:
            for color, edge in [((1.0, 0.0, 0.0), (3, 6)), ((0.0, 1.0, 0.0), (3, 0)), ((0.0, 0.0, 1.0), (3, 2))]:
                glColor4f(*color, 1.0)
                glVertex3fv(cell[edge[0]])
                glVertex3fv(cell[edge[1]])
        glEnd()

    def select_atom(self):
        ...

    def mainloop(self):
        target_fps = 60
        prev_time = time.time()
        run = True

        # Light BLOCK

        lights0 = [[1, 1, 1, 0.0], [1, -10, 2, 1.0]]
        intensities = [[0.4, 0.4, 0.4], [0.4, 0.4, 0.4]]
        Kd = np.array([0.3, 0.3, 0.3], np.float32)
        Ld = np.array([1.0, 1.0, 1.0], np.float32)
        Ka, Ks, Shininess = np.array([0.5, 0.5, 0.5], dtype=np.float32), np.array([0.8, 0.8, 0.8], dtype=np.float32), 10.0

        test = [[0, 0, 0], [2, 2, 2]]

        st_time = time.time()
        while run:
            diff = time.time() - st_time
            LightPosition = np.array([20 * math.sin(math.degrees(0.02 * diff)), 20 * math.cos(math.degrees(0.02 * diff)), -3.8, 1.0], np.float32)
            self.euler_rotation_matrix = np.array([[-math.cos(math.radians(self.rotation_info[0])), math.cos(math.radians(self.rotation_info[1])) * math.sin(math.radians(self.rotation_info[0])), -math.sin(math.radians(self.rotation_info[1])) * math.sin(math.radians(self.rotation_info[0])), 0],
                                                   [0.0, math.sin(math.radians(self.rotation_info[1])), math.cos(math.radians(self.rotation_info[1])), 0],
                                                   [-math.sin(math.radians(self.rotation_info[0])), -math.cos(math.radians(self.rotation_info[1])) * math.cos(math.radians(self.rotation_info[0])), math.cos(math.radians(self.rotation_info[0])) * math.sin(math.radians(self.rotation_info[1])), 0],
                                                   [self._x_d, self._y_d, self._z_d, self._scale_parameter]], dtype='f')

            self.model_view_matrix = np.dot(self.__view_matrix, self.euler_rotation_matrix.transpose())
            self.MVP = np.dot(self.__projection_matrix.transpose(), self.model_view_matrix)
            self.normal_matrix = np.linalg.inv(self.model_view_matrix[:3, :3]).transpose()

            glLoadIdentity()
            glMultMatrixf(self.euler_rotation_matrix)

            lights = np.dot(np.asarray(lights0), self.euler_rotation_matrix)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.Back_Step, self.Forward_Step = False, False
                    run = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        self.Back_Step, self.Forward_Step = False, False
                        run = False
                        break
                    if event.key == pygame.K_F4:
                        raise KeyError("Pushed exit key. Don't push F4 if you don't want to exit program.")
                if event.type == pygame.MOUSEMOTION and event.type != pygame.WINDOWLEAVE:
                    coord_x, coord_y = pygame.mouse.get_pos()
                    coord_x_mouse, coord_y_mouse = pygame.mouse.get_rel()
                    if self.mouse_pressed:
                        self.Back_Step, self.Forward_Step = False, False
                        if self.only_keyboard_select:
                            pygame.mouse.set_visible(False)
                        self.rotation_info[0] -= (event.rel[0]) * 0.4
                        self.rotation_info[1] += (event.rel[1]) * 0.4
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.only_keyboard_select:
                        pygame.mouse.set_visible(True)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4 and self.calculation_parsed:
                    self.Back_Step, self.Forward_Step = False, False
                    self._scale_parameter = self._scale_parameter * 0.92
                    pygame.time.wait(10)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5 and self.calculation_parsed:
                    self.Back_Step, self.Forward_Step = False, False
                    self._scale_parameter = self._scale_parameter * 1.08
                    pygame.time.wait(10)
                if event.type == pygame.MOUSEBUTTONDOWN and self.calculation_parsed:
                    if event.button == 1:
                        if not self.only_keyboard_select:
                            self.select_atom(True)
                    if event.button == 3:
                        if not self.only_keyboard_select:
                            self.select_atom(False)

                if event.type == pygame.VIDEORESIZE:
                    self.display_resize(event)

            keypress = pygame.key.get_pressed()

            # Отдаление модели при нажатии клавиши - на кейпаде
            if keypress[pygame.K_KP_MINUS] or keypress[pygame.K_MINUS]:
                self.Back_Step, self.Forward_Step = False, False
                self._scale_parameter = self._scale_parameter * 1.03
                pygame.time.wait(10)
            # Приближение модели при нажатии кнопки + на кейпаде
            if keypress[pygame.K_KP_PLUS] or keypress[pygame.K_EQUALS]:
                self.Back_Step, self.Forward_Step = False, False
                self._scale_parameter = self._scale_parameter * 0.97
                pygame.time.wait(10)
            ##################################
            if keypress[pygame.K_BACKSPACE]:
                self.Back_Step, self.Forward_Step = False, False
                self.rotation_info = [0, 0]
                self._x_d, self._y_d, self._z_d = 0, 0, 0
                self._scale_parameter = 1.0

            if keypress[pygame.K_LEFT]:
                self.Back_Step, self.Forward_Step = False, False
                self.rotation_info[0] -= 1.5
            if keypress[pygame.K_RIGHT]:
                self.Back_Step, self.Forward_Step = False, False
                self.rotation_info[0] += 1.5
            if keypress[pygame.K_UP]:
                self.Back_Step, self.Forward_Step = False, False
                self.rotation_info[1] += 1.5
            if keypress[pygame.K_DOWN]:
                self.Back_Step, self.Forward_Step = False, False
                self.rotation_info[1] -= 1.5
            if keypress[pygame.K_z]:
                self._x_d = self._x_d - 0.1
            if keypress[pygame.K_x]:
                self._x_d = self._x_d + 0.1
            if keypress[pygame.K_j]:
                self._z_d = self._z_d + 0.1
            if keypress[pygame.K_u]:
                self._z_d = self._z_d - 0.1
            if keypress[pygame.K_COMMA] and self._Buffers_Labels:
                self._step -= 1
                if self._step < 0:
                    self._step = self.__calculation['STEPS'] - 1
            if keypress[pygame.K_PERIOD] and self._Buffers_Labels:
                self._step += 1
                if self._step == self.__calculation['STEPS']:
                    self._step = 0


            # if keypress[pygame.K_a]:
            #     self.select_atom(True)
            # if keypress[pygame.K_d]:
            #     self.select_atom(False)
            # Движение модели мышкой
            for _ in pygame.mouse.get_pressed():
                if pygame.mouse.get_pressed()[0] == 1:
                    self.mouse_pressed = True
                elif pygame.mouse.get_pressed()[0] == 0:
                    self.mouse_pressed = False

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glClearColor(*self.__background_color, 1.0)
            # # Отрисовка границ ячейки
            if self.draw_cell and self._Buffers_Labels:
                self.cell_draw(self.__calculation['BASIS_VERT'], self.draw_cell, self.draw_axes, 3)

            # x, y, z = self.find_window_dimensions(-5)
            for index, Buffer in enumerate(self._VBO_Buffers):
                Buffer.prepare_to_draw(self.__program.program)
                Buffer.set_light_settings(self.__program.uniform_variables_dict, Ka, Kd, Ks, Shininess, lights, intensities)
                if not self._Buffers_Labels:
                    for x_d, y_d, z_d in self.default_cube_position:
                        self.__translation_matrix[0][-1] = x_d
                        self.__translation_matrix[1][-1] = y_d
                        self.__translation_matrix[2][-1] = z_d
                        Buffer.draw_from_vao_buffer(self.__draw_type, self.__program.uniform_variables_dict, ModelMatrix=self.euler_rotation_matrix.transpose(), ViewMatrix=self.__view_matrix, ProjectionMatrix=self.__projection_matrix.transpose(), NormalMatrix=self.normal_matrix, TranslationMatrix=self.__translation_matrix)
                else:
                    for atom_index, (x_d, y_d, z_d) in enumerate(self.__calculation['POSITIONS'][self._step]):
                        if self._Buffers_Labels[index] == self.__calculation['ATOMNAMES'][atom_index]:
                            self.__translation_matrix[0][-1] = x_d
                            self.__translation_matrix[1][-1] = y_d
                            self.__translation_matrix[2][-1] = z_d
                            Buffer.draw_from_vao_buffer(self.__draw_type, self.__program.uniform_variables_dict, ModelMatrix=self.euler_rotation_matrix.transpose(), ViewMatrix=self.__view_matrix, ProjectionMatrix=self.__projection_matrix.transpose(), NormalMatrix=self.normal_matrix, TranslationMatrix=self.__translation_matrix)
                Buffer.end_of_drawing()
            pygame.display.flip()

            curr_time = time.time()  # so now we have time after processing
            diff = curr_time - prev_time  # frame took this much time to process and render
            delay = max(1.0 / target_fps - diff, 0)  # if we finished early, wait the remaining time to desired fps, else wait 0 ms!
            time.sleep(delay)
            fps = 1.0 / (delay + diff)  # fps is based on total time ("processing" diff time + "wasted" delay time)
            prev_time = curr_time
        pygame.quit()


calc = VRMD(r'C:\Users\AlexS\Documents\Научка\MoS2\Mo\MoS2_N2_25eV_perp_Mo').parser_parameters
main = VROpenGL()
main.load_calculation_info(calc)
main.mainloop()
