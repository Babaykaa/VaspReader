import OpenGL
from numba import jit
from numba.core.types import int64
import numpy as np
import os
from os import environ
from Visual.VRPrimitives import Primitives
import random
import time
from PIL import Image
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.WGL import *
import pygame
from pygame.locals import *
from Visual.VRVBO import VRVBO
from Visual.Shaders.VRShaders import VRShaders
from Logs.VRLogger import sendDataToLogger


def TransformVec3(vecA, mat44) -> tuple[list[float], int]:
    """Transform 3d vector to 2d projection."""
    vecB = [0, 0, 0, 0]
    for i0 in range(0, 4):
        vecB[i0] = vecA[0] * mat44[0 * 4 + i0] + vecA[1] * mat44[1 * 4 + i0] + vecA[2] * mat44[2 * 4 + i0] + mat44[3 * 4 + i0]
    return [vecB[0] / vecB[3], vecB[1] / vecB[3], vecB[2] / vecB[3]], vecB[3]


def perspective_choose(prjMat, mpos, ll, dis, parameter) -> list[int]:
    """Option of choosing object on the screen with perspective view.
       prjMat - projection matrix, mpos - mouse position at the screen,
       ll - atoms vertices, dis - display size, parameter - radii of sphere."""
    ll_ndc = [[0.0 for i in range(3)] for m in range(len(ll))]
    inRectCounter = 0  # atoms in sphere counter
    depth = list()  # atoms in sphere list
    mult = [0.0 for _ in range(len(ll))]  # коэффициенты масштабирования пространства
    for num in range(len(ll)):
        ll_ndc[num], mult[num] = TransformVec3(ll[num], prjMat)  # координаты в мировом пространстве???
    radii = [parameter[i] / mult[i] * 1.0 for i in range(len(ll))]  # radius of projected sphere
    ndc = [2.0 * mpos[0] / dis[0] - 1.0, 1.0 - 2.0 * mpos[1] / dis[1]]
    inRect = [0 for _ in range(len(ll))]  # список попаданий в атом, 0 - не попал, 1 - попал
    for num in range(len(ll)):
        if ll_ndc[num][0] - radii[num] <= ndc[0] <= ll_ndc[num][0] + radii[num] and ll_ndc[num][1] - radii[num] <= ndc[1] <= ll_ndc[num][1] + radii[num]:
            inRect[num] = 1
        else:
            inRect[num] = 0
    for num in range(len(ll)):
        if inRect[num] == 1:
            inRectCounter += 1  # число попаданий
            depth.append(ll_ndc[num][2])  # координаты по глубине
    if inRectCounter > 1:
        right_vec = min(depth)
        for num in range(len(ll)):
            if ll_ndc[num][2] != right_vec:
                inRect[num] = 0
    return inRect


def orthographic_choose(mpos, ll, dis, parameter) -> list[int]:
    """Option of choosing object on the screen with orthographic view.
    mpos - mouse position at the screen, ll - atoms vertices, dis - display size, parameter - radii of sphere."""
    ortho_size = (12, 9)
    coordinate = [(1.0 - 2.0 * mpos[0] / dis[0]) * ortho_size[0], (1.0 - 2.0 * mpos[1] / dis[1]) * ortho_size[1]]
    inRectCounter = 0  # atoms in sphere counter
    depth = []  # atoms in sphere list
    inRect = [0 for m in range(len(ll))]  # список попаданий в атом, 0 - не попал, 1 - попал
    for num in range(len(ll)):
        if ll[num][0] - parameter[num] <= coordinate[0] <= ll[num][0] + parameter[num] and ll[num][2] - parameter[num] <= coordinate[1] <= ll[num][2] + parameter[num]:
            inRect[num] = 1
        else:
            inRect[num] = 0
    for num in range(len(ll)):
        if inRect[num] == 1:
            inRectCounter += 1  # число попаданий
            depth.append(ll[num][1])  # координаты по глубине
    if inRectCounter > 1:
        right_vec = max(depth)
        for num in range(len(ll)):
            if ll[num][1] != right_vec:
                inRect[num] = 0
    return inRect


def build_projection_matrix(scree_width, scree_height, eye_point, fov, near, far):
    """Build the projection matrix according to the formula:
    f / aspect     , 0.0             , 0.0                            , 0.0
    0.0            , f               , 0.0                            , 0.0
    0.0            , 0.0             , (far + near) / (near - far)    , -1.0
    0.0            , 0.0             , 2.0 * far * near / (near - far), 0.0
    where f = 1 / tg(fov / 2.0), aspect = scree_width / scree_height."""
    aspect = scree_width / float(scree_height)
    fov = np.radians(fov)
    f = 1 / np.tan(fov / 2.0)
    pMatrix = np.array([[f / aspect, 0.0, 0.0, 0.0],
                        [0.0, f, 0.0, 0.0],
                        [0.0, 0.0, -(far + (abs(eye_point) + near)) / (far - (abs(eye_point) + near)), -1.0],
                        [0.0, 0.0, -2.0 * far * (abs(eye_point) + near) / (far - (abs(eye_point) + near)), 0.0]], np.float32)
    return pMatrix


def build_orthographic_matrix(left, right, top, bottom, near, far):
    """Build the orthographic matrix according to the formula:
    2 / (r - l)      , 0.0               , 0.0                 , 0.0
    0.0              , 2 / (t - b)       , 0.0                 , 0.0
    0.0              , 0.0               , 1 / (near - far)    , 0.0
    (l + r) / (l - r), (t + b) / (b - t) , near / (near - far) , 1.0
    """
    pMatrix = np.array([[2 / (right - left), 0.0, 0.0, 0.0],
                        [0.0, 2 / (top - bottom), 0.0, 0.0],
                        [0.0, 0.0, 1 / (near - far), 0.0],
                        [(left + right) / (left - right), (top + bottom) / (bottom - top), near / (near - far), 1.0]], np.float32)
    return pMatrix


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
    return np.array([mx[0], my[0], mz[0], tx, mx[1], my[1], mz[1], ty, mx[2], my[2], mz[2], tz, 0, 0, 0, 1], dtype=np.float64).reshape((4, 4))


def GL_version():
    renderer = glGetString(GL_RENDERER)
    vendor = glGetString(GL_VENDOR)
    version = glGetString(GL_VERSION)

    return vendor.decode(), renderer.decode(), version.decode()


class VROpenGL:
    """Class for visualisation VASP and not only VASP calculation results. Have many features connected with bonds,
    cell and axes drawing and others options."""
    __default_display = (800, 600)
    __light_variables = (GL_LIGHT0, GL_LIGHT1, GL_LIGHT2, GL_LIGHT3, GL_LIGHT4, GL_LIGHT5, GL_LIGHT6, GL_LIGHT7)
    __light_states = {i: False for i in range(8)}
    __light_positions = [[10, 10, 10], [10, 10, -10], [10, -10, 10], [10, -10, -10], [-10, 10, 10], [-10, 10, -10],
                         [-10, -10, 10], [-10, -10, -10]]
    __view_axes = True
    __view_cell_border = True
    __draw_type = GL_TRIANGLES
    __calculation = dict()
    # __primitives = {'Primitive': Primitives(3, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]).Cube(__draw_type)}
    # __primitives = {'Primitive': Primitives(3, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]).Sphere(1, 32, 32)}
    __primitives = {'Primitive': Primitives(3, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]).Quad(1.0)}
    __project_directory = os.path.abspath('')
    _background_color = (0.6, 0.6, 0.6, 1.0)
    __lights_default = [[10, 10, 10, 0.0], [-10, -10, 10, 1.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]]
    __intensities = [[0.4, 0.4, 0.4], [0.4, 0.4, 0.4], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    __Kd = np.array([0.3, 0.3, 0.3], np.float32)
    __Ld = np.array([0.7, 0.7, 0.7], np.float32)
    __Ka, __Ks, __Shininess = np.array([0.5, 0.5, 0.5], dtype=np.float32), np.array([0.8, 0.8, 0.8], dtype=np.float32), 32.0
    __eye_position = np.array([0.0, 20.0, 0.0])
    _fogColor = (0.6, 0.6, 0.6, 1.0)
    _defaultBondLength = 1.8
    _defaultBondRadius = 0.2

    @sendDataToLogger
    def __init__(self, app=None, settings=None, visual_window=None, print_window=None):
        """Initialization function of VROpenGL"""
        self.__settings_object = settings
        self.__visual_window = visual_window
        self.__logger = print_window
        self._parent_window_closed = False
        self.__app = app

        self.__display, self.window_size = list(self.__default_display), list(self.__default_display)
        self.__view_matrix = m3dLookAt(self.__eye_position, np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0]))
        self.__perspective_matrix = build_projection_matrix(self.__display[0], self.__display[1], 0, 45, 0.1, 60)
        self.__orthographic_matrix = build_orthographic_matrix(-12, 12, 9, -9, 0.1, 60)
        self.__projection_matrix = self.__perspective_matrix
        self._x_d, self._y_d, self._z_d, self._scale_parameter = 0.0, 0.0, 0.0, 1.0
        self.rotation_matrix = np.array([[-1.0, 0.0, 0.0, 0.0],
                                         [0.0, 0.0, 1.0, 0],
                                         [0.0, -1.0, 0.0, 0.0],
                                         [self._x_d, self._y_d, self._z_d, self._scale_parameter]],
                                        dtype=np.float64)
        self.__translation_matrix = np.array([[1.0, 0.0, 0.0, 0.0],
                                              [0.0, 1.0, 0.0, 0.0],
                                              [0.0, 0.0, 1.0, 0.0],
                                              [0.0, 0.0, 0.0, 1.0]], dtype=np.float64)
        self.__lights = np.dot(np.asarray(self.__lights_default), self.rotation_matrix)
        self.model_view_matrix, self.normal_matrix = None, None
        self.mouse_pressed, self.Back_Step, self.Forward_Step, self.only_keyboard_select, self.draw_cell, self.draw_axes, self.is_perspective = False, False, True, True, True, True, True
        self.display_scaling, self._step, self._speed, self._fogMinDist, self._fogMaxDist, self._fogPower, self._fogDensity = 1.0, 0, 1, 0.1, 60, 1, 0.05
        self._set_ID_mode, self._set_bond_mode, self._set_valence_mode = False, False, False
        self.new_coordinate_start = [0, 0]
        self.rotation_info, self.default_cube_position = np.array([0.0, 0.0]), [[0, 0, 0]]
        self._Buffers_Labels = []
        self.__cell_position = self.__eye_position.copy()
        self._BondRadius, self._BondLength, self._allBondsCalculate, self._BondsInfo = None, None, True, dict()
        self._cube_covered_texture, self._cube_covered_texture_sampler = None, None
        environ['SDL_VIDEODRIVER'] = 'windib'
        pygame.init()
        try:
            self.__win_icon = self.__project_directory + r'\VR_icons\VR-logo.png'
            pygame.display.set_icon(pygame.image.load(self.__win_icon))
        except FileNotFoundError:
            pass
        pygame.display.set_caption('VaspReader')
        self.__scree = pygame.display.set_mode(self.__default_display, DOUBLEBUF | OPENGL | pygame.RESIZABLE)

        glMatrixMode(GL_PROJECTION)
        glEnable(GL_TEXTURE_2D)
        glShadeModel(GL_SMOOTH)

        vendor, renderer, version = GL_version()
        self.__logger.addMessage(f"GL Vendor version: {vendor}", self.__class__.__name__)
        self.__logger.addMessage(f"GL Renderer version: {renderer}", self.__class__.__name__)
        self.__logger.addMessage(f"GL Version: {version}", self.__class__.__name__)
        self.__logger.addMessage(f"Pygame Version: {pygame.__version__}\n", self.__class__.__name__)

        gluPerspective(45, (self.__default_display[0] / self.__default_display[1]), 0.1, 60.0)
        gluLookAt(0, 20, 0, 0, 0, 0, 0, 0, 1)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        self.__DisplayCenter = [self.__scree.get_size()[i] // 2 for i in range(2)]
        pygame.mouse.set_pos(self.__DisplayCenter)
        self.__program = VRShaders(self.__project_directory + '\\Visual\\Shaders', [r'vertex_shader.glsl', r'fragment_shader.glsl'], ['VERTEX', 'FRAGMENT'])
        self._VBO_Buffers = [VRVBO(self.__primitives['Primitive'][:-1], self.__primitives['Primitive'][-1]).create_vao_buffer()]
        self.load_texture()

    def get_logger(self):
        return self.__logger

    @sendDataToLogger
    def hide(self):
        self.__scree = pygame.display.set_mode(self.__display, DOUBLEBUF | OPENGL | pygame.RESIZABLE | pygame.HIDDEN)

    @sendDataToLogger
    def show(self):
        self.__scree = pygame.display.set_mode(self.__display, DOUBLEBUF | OPENGL | pygame.RESIZABLE)

    @sendDataToLogger
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

    @sendDataToLogger
    def find_window_dimensions(self, far):
        far = 20 + far
        x_limit = np.sin(np.pi / 16 * 3) * far
        y_limit = x_limit / 4 * 3
        if self.window_size[0] / 4 < self.window_size[1] / 3:
            x_limit = x_limit * (self.window_size[0] / self.__display[0])
        else:
            y_limit = y_limit * (self.window_size[1] / self.__display[1])
        return x_limit, y_limit, -(far - 20)

    @sendDataToLogger
    def change_light_position(self, new_position, light_index):
        self.__light_positions[light_index] = new_position

    @sendDataToLogger(operation_type='user')
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

    @sendDataToLogger
    def load_calculation_info(self, calculation):
        self.__calculation = calculation
        self.__primitives.clear()
        self._VBO_Buffers.clear()
        self._Buffers_Labels.clear()
        self.__cell_position[1] = self.__calculation['BASIS_VERT'].max()
        for _, atom in enumerate(calculation['ATOMSINFO']):
            self.__primitives[atom] = Primitives(1, calculation['ATOMSINFO'][atom]['COLORVALUE']).Sphere(calculation['ATOMSINFO'][atom]['RADII'], 32, 32)
            self.__primitives[f'{atom}_Sel'] = Primitives(1, calculation['ATOMSINFO'][atom]['COLORVALUE'] * 0.6).Sphere(calculation['ATOMSINFO'][atom]['RADII'] * 1.15, 32, 32)
        for _, key in enumerate(self.__primitives):
            self._VBO_Buffers.append(VRVBO(self.__primitives[key][:-1], self.__primitives[key][-1]).create_vao_buffer())
            self._Buffers_Labels.append(key)

    @sendDataToLogger
    def without_calculation(self):
        self.__calculation = None
        self.__primitives.clear()
        self._VBO_Buffers.clear()
        self._Buffers_Labels.clear()
        self.__cell_position[1] = self._fogMaxDist = 20
        self.__primitives = {'Primitive': Primitives(3, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]).Quad(1.0)}
        # self.__primitives = {'Primitive': Primitives(3, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]).Cube(self.__draw_type)}
        self._VBO_Buffers.append(VRVBO(self.__primitives['Primitive'][:-1], self.__primitives['Primitive'][-1]).create_vao_buffer())

    @sendDataToLogger
    def set_default_rotation_matrix(self):
        self.rotation_matrix = self.rotation_matrix = np.array([[-1.0, 0.0, 0.0, 0.0],
                                                                [0.0, 0.0, 1.0, 0],
                                                                [0.0, -1.0, 0.0, 0.0],
                                                                [self._x_d, self._y_d, self._z_d, self._scale_parameter]], dtype=np.float64)

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

    @sendDataToLogger
    def load_texture(self):  # , texture
        image = Image.open(r'VR_icons\VR-logo.png')
        image = image.convert("RGBA")

        img_data = image.tobytes()

        self._cube_covered_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._cube_covered_texture)
        # self._cube_covered_texture_sampler = glGenSamplers(1)
        # glBindSampler(self._cube_covered_texture, self._cube_covered_texture_sampler)


        # Set the texture wrapping parameters

        # glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        color = [1.0, 1.0, 1.0, 1.0]
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, color)

        # Set texture filtering parameters

        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        # print(glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_BYTE))
        glBindTexture(GL_TEXTURE_2D, 0)


    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def define_rotation_around_axes(x_d, y_d, z_d, scale_parameter, x_r, y_r, z_r, limit_rotations=True):
        if limit_rotations:
            x_r, y_r, z_r = x_r % 360 - 180, y_r % 360 - 180, z_r % 360 - 180
        x_rotation = np.array([[1.0, 0.0, 0.0, 0.0],
                               [0.0, np.cos(np.radians(x_r)), -np.sin(np.radians(x_r)), 0.0],
                               [0.0, np.sin(np.radians(x_r)), np.cos(np.radians(x_r)), 0.0],
                               [0.0, 0.0, 0.0, 1.0]], dtype=np.float64)
        y_rotation = np.array([[np.cos(np.radians(y_r)), 0.0, np.sin(np.radians(y_r)), 0.0],
                               [0.0, 1.0, 0.0, 0.0],
                               [-np.sin(np.radians(y_r)), 0.0, np.cos(np.radians(y_r)), 0.0],
                               [0.0, 0.0, 0.0, 1.0]], dtype=np.float64)
        z_rotation = np.array([[np.cos(np.radians(z_r)), -np.sin(np.radians(z_r)), 0.0, 0.0],
                               [np.sin(np.radians(z_r)), np.cos(np.radians(z_r)), 0.0, 0.0],
                               [0.0, 0.0, 1.0, 0.0],
                               [0.0, 0.0, 0.0, 1.0]], dtype=np.float64)
        matrix = np.dot(z_rotation, np.dot(y_rotation, x_rotation))
        matrix[3][0], matrix[3][1], matrix[3][2] = x_d, y_d, z_d
        matrix[3][3] = scale_parameter
        return matrix

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def define_rotation(define_rotation_function, rotation_matrix, rotation_info, x_d, y_d, z_d, scale_parameter):
        if rotation_info[0] or rotation_info[1] or x_d or y_d or z_d or scale_parameter - 1.0:
            rotation_matrix = np.dot(rotation_matrix, define_rotation_function(x_d, y_d, z_d, scale_parameter, rotation_info[1], 0, rotation_info[0]))
            # self.__lights = np.dot(np.asarray(self.__lights_default), self.rotation_matrix)
        return rotation_matrix

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def define_normal_matrix(view_matrix, rotation_matrix):
        model_view_matrix = np.dot(view_matrix, rotation_matrix.transpose())
        return np.linalg.inv(model_view_matrix[:3, :3]).transpose()

    @sendDataToLogger(operation_type='user')
    def select_atom(self, select):
        self.Back_Step, self.Forward_Step = False, False
        mouseClick = pygame.mouse.get_pos()
        mouseClick = [mouseClick[i] - self.new_coordinate_start[i] for i in range(2)]
        if self.is_perspective:
            prjMat = (GLfloat * 16)()
            glGetFloatv(GL_PROJECTION_MATRIX, prjMat)
            prjMat = np.dot(self.rotation_matrix, np.array(prjMat).reshape((4, 4))).reshape((16, 1))
            onRect = perspective_choose(prjMat, mouseClick, self.__calculation['POSITIONS'][self._step], self.__display, self.__calculation['RADII'])
        else:
            coordinates = (np.dot(self.__calculation['POSITIONS'][self._step], self.rotation_matrix[:3, :3]) + np.array([[*self.rotation_matrix[3, :3]] for _ in range(self.__calculation['POSITIONS'][self._step].shape[0])])) / self.rotation_matrix[-1, -1]
            onRect = orthographic_choose(mouseClick, coordinates, self.__display, self.__calculation['RADII'])
        already_selected = False
        if select:
            for num, selected in enumerate(onRect):
                if selected and self.__calculation['ATOMNAMES'][num].split('_')[-1] != 'Sel' and not (self._set_ID_mode or self._set_bond_mode or self._set_valence_mode):
                    self.__calculation['ATOMNAMES'][num] += '_Sel'
                elif selected and self.__calculation['ATOMNAMES'][num].split('_')[-1] == 'Sel':
                    already_selected = True
        else:
            for num, selected in enumerate(onRect):
                if selected and self.__calculation['ATOMNAMES'][num].split('_')[-1] == 'Sel' and not (self._set_ID_mode or self._set_bond_mode or self._set_valence_mode):
                    self.__calculation['ATOMNAMES'][num] = self.__calculation['ATOMNAMES'][num][:-4]
                elif selected and self.__calculation['ATOMNAMES'][num].split('_')[-1] != 'Sel':
                    already_selected = True
        if already_selected:
            self.__logger.addMessage('This atom was already chose.' if select else 'This atom was already deleted.', self.__class__.__name__)
        pygame.time.wait(200)

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def nonoptimal_dimension_search(positions, number_of_dividings):
        length = len(positions) - 1
        size_array = np.zeros((3, number_of_dividings + 1))
        delta_dim = np.zeros(3)
        for iteration in range(number_of_dividings + 1):
            step = iteration * length // number_of_dividings
            pos = positions[step].transpose()
            size_array[0] = pos[0].max() - pos[0].min()
            size_array[1] = pos[1].max() - pos[1].min()
            size_array[2] = pos[2].max() - pos[2].min()
        size_array = np.asarray(size_array)
        for index in range(3):
            delta_dim[index] = size_array[index].max() - size_array[index].min()
        return delta_dim.argsort()[-2]

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def neighbours_search_body(num, index, positions, indexes, dimension, bond_length):
        highest_index = max_index = len(indexes) - num
        min_index = 0
        now_index = max_index // 2 if not max_index % 2 else max_index // 2 + 1
        pos = positions[index][dimension]
        while True:
            index_comp = indexes[now_index - 1 + num]
            index_comp_next = indexes[now_index + num]
            statement1 = abs(pos - positions[index_comp][dimension]) <= bond_length
            statement2 = abs(pos - positions[index_comp_next][dimension]) <= bond_length
            if statement1 and not statement2:
                break
            elif now_index == highest_index - 1 and statement1 and statement2:
                now_index = highest_index
                break
            elif now_index == 0 and not statement1:
                break
            elif statement1 and statement2:
                min_index = now_index
                summary = now_index + max_index
                now_index = summary // 2 if not summary % 2 else summary // 2 + 1
            else:
                max_index = now_index
                summary = now_index + min_index
                now_index = summary // 2 if not summary % 2 else summary // 2 + 1
        tracking_pos = positions[index]
        returning_indexes = []
        for another_index in indexes[num + 1:now_index + num]:
            target_pos = positions[another_index]
            length = np.linalg.norm(tracking_pos - target_pos)
            if length <= bond_length:
                returning_indexes.append(another_index)
        return np.array(returning_indexes)

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def neighbours_search(search_algoritm, positions, indexes, dimension, bond_length):
        neighbours = dict()
        indexes_cp = indexes[:-1]
        for num, index in enumerate(indexes_cp):
            neighbours[int(index)] = search_algoritm(num, index, positions, indexes, dimension, bond_length)
        return neighbours

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def neighbours_search_between_types_body(index, positions, indexes, dimension, bond_length):
        highest_index = max_index = len(indexes)
        min_index = 0
        now_index = max_index // 2 if not max_index % 2 else max_index // 2 + 1
        pos = positions[index][dimension]
        while True:
            index_comp = indexes[now_index - 1]
            index_comp_next = indexes[now_index]
            statement1 = abs(pos - positions[index_comp][dimension]) <= bond_length
            statement2 = abs(pos - positions[index_comp_next][dimension]) <= bond_length
            if statement1 and not statement2:
                break
            elif now_index == highest_index - 1 and statement1 and statement2:
                now_index = highest_index
                break
            elif now_index == 0 and not statement1:
                break
            elif statement1 and statement2:
                min_index = now_index
                summary = now_index + max_index
                now_index = summary // 2 if not summary % 2 else summary // 2 + 1
            else:
                max_index = now_index
                summary = now_index + min_index
                now_index = summary // 2
        tracking_pos = positions[index]
        returning_indexes = []
        for another_index in indexes[:now_index]:
            target_pos = positions[another_index]
            length = np.linalg.norm(tracking_pos - target_pos)
            if length <= bond_length:
                returning_indexes.append(another_index)
        return np.array(returning_indexes)

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def neighbours_search_between_types(search_algoritm, positions, indexes_type1, indexes_type2, dimension, bond_length):
        neighbours = dict()
        for _, index in enumerate(indexes_type1):
            neighbours[int64(index)] = search_algoritm(index, positions, indexes_type2, dimension, bond_length)
        return neighbours

    def calculateBonds(self):  # необходимо отсортировать массив по x, y, z и смотреть начиная с какого то элемента массива расстояние. Если оно больше заданного, то не включаем в рассмотрение, если меньше, то включаем и при этом соответствующим образом сдвигаем далее индекс поиска
        one_step_positions = self.__calculation['POSITIONS'][self._step]
        biggest_dim = self.nonoptimal_dimension_search(self.__calculation['POSITIONS'], 9)
        if self._allBondsCalculate:
            one_step_positions_tr = one_step_positions.transpose()
            indexes_big = one_step_positions_tr[biggest_dim].argsort()
            neighbours = self.neighbours_search(self.neighbours_search_body, one_step_positions, indexes_big, biggest_dim, self._BondLength)
        else:
            type1, type2 = 'Mo', 'S'
            indexes1, indexes2 = self.__calculation['ATOM-NUMBERS'][type1], self.__calculation['ATOM-NUMBERS'][type2]
            one_step_positions_type2 = one_step_positions[indexes2]
            one_step_positions_tr = one_step_positions_type2.transpose()
            indexes_big = one_step_positions_tr[biggest_dim].argsort() + min(indexes2)
            neighbours = self.neighbours_search_between_types(self.neighbours_search_between_types_body, one_step_positions, indexes1, indexes_big, biggest_dim, self._BondLength)

    def prepareBondBuffers(self):
        atoms = self.__calculation['ATOMNAMES']
        if self._BondRadius is None and self._BondLength is None:
            for atom in set(atoms):
                self.__primitives[f'{atom}_Bond'] = Primitives(1.0, self.__calculation['ATOMSINFO'][atom]['COLORVALUE']).Tube(self._defaultBondRadius, self._defaultBondLength / 2, 32)
        else:
            for atom in set(atoms):
                self.__primitives[f'{atom}_Bond'] = Primitives(1.0, self.__calculation['ATOMSINFO'][atom]['COLORVALUE']).Tube(self._BondRadius[f'{atom}_Bond'], self._BondLength[f'{atom}_Bond'] / 2, 32)
        for key in set(atoms):
            self._VBO_Buffers.append(VRVBO(self.__primitives[key + '_Bond'][:-1], self.__primitives[key + '_Bond'][-1]).create_vao_buffer())
            self._Buffers_Labels.append(key + '_Bond')

    @sendDataToLogger
    def mainloop(self):
        target_fps = 60
        prev_time = time.time()
        run = True

        while run:
            # glLoadIdentity()
            # glMultMatrixf(self.rotation_matrix)
            if self.is_perspective:
                self.__projection_matrix = self.__perspective_matrix
            else:
                self.__projection_matrix = self.__orthographic_matrix
            if self._parent_window_closed:
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.Back_Step, self.Forward_Step = False, False
                    run = False
                    self.__app.closeAllWindows()
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.Back_Step, self.Forward_Step = False, False
                        run = False
                        self.__app.closeAllWindows()
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
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
                    self._scale_parameter = self._scale_parameter * 0.92
                    pygame.time.wait(10)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
                    self._scale_parameter = self._scale_parameter * 1.08
                    pygame.time.wait(10)
                if event.type == pygame.MOUSEBUTTONDOWN and self._Buffers_Labels:
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
                self.rotation_info[0], self.rotation_info[1] = 0.0, 0.0
                self._x_d, self._y_d, self._z_d = 0, 0, 0
                self._scale_parameter = 1.0
                self.set_default_rotation_matrix()
                self.__lights = np.dot(np.asarray(self.__lights_default), self.rotation_matrix)

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
            if keypress[pygame.K_i]:
                self._fogPower += 1
                time.sleep(0.08)
            if keypress[pygame.K_k]:
                if self._fogPower > 1:
                    self._fogPower -= 1
                    time.sleep(0.08)
            if keypress[pygame.K_o]:
                self._fogDensity = self._fogDensity * 1.05
                time.sleep(0.08)
            if keypress[pygame.K_l]:
                self._fogDensity = self._fogDensity / 1.05
                time.sleep(0.08)

            if (keypress[pygame.K_COMMA] or self.Back_Step) and self._Buffers_Labels:
                self._step -= 1 * self._speed
                if self._step < 0:
                    self._step = self.__calculation['STEPS'] - 1 + self._step
                self.__visual_window.StepSlider.setSliderPosition(self._step)
                self.Back_Step = True
            if (keypress[pygame.K_PERIOD] or self.Forward_Step) and self._Buffers_Labels:
                self._step += 1 * self._speed
                if self._step >= self.__calculation['STEPS']:
                    self._step = self._step - self.__calculation['STEPS']
                self.__visual_window.StepSlider.setSliderPosition(self._step)
                self.Forward_Step = True

            if keypress[pygame.K_a]:
                self.select_atom(True)
            if keypress[pygame.K_d]:
                self.select_atom(False)

            if keypress[pygame.K_p]:
                self.__visual_window.processing_start()

            # Движение модели мышкой
            for _ in pygame.mouse.get_pressed():
                if pygame.mouse.get_pressed()[0] == 1:
                    self.mouse_pressed = True
                elif pygame.mouse.get_pressed()[0] == 0:
                    self.mouse_pressed = False

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glClearColor(*self._background_color)
            self.rotation_matrix = self.define_rotation(self.define_rotation_around_axes, self.rotation_matrix, self.rotation_info, self._x_d, self._y_d, self._z_d, self._scale_parameter)
            self.normal_matrix = self.define_normal_matrix(self.__view_matrix, self.rotation_matrix)
            # # Отрисовка границ ячейки
            # if self.draw_cell and self._Buffers_Labels:
            #     self.cell_draw(self.__calculation['BASIS_VERT'], self.draw_cell, self.draw_axes, 3)

            # x, y, z = self.find_window_dimensions(-5)
            for index, Buffer in enumerate(self._VBO_Buffers):
                Buffer.prepare_to_draw(self.__program.program)
                Buffer.set_light_settings(self.__program.uniform_variables_dict, self.__Ka, self.__Kd, self.__Ks, self.__Shininess, self.__lights, self.__intensities)
                Buffer.set_fog_parameters(self.__program.uniform_variables_dict, self.__cell_position, self._fogColor, self._fogMinDist, self._fogMaxDist, self._fogPower, self._fogDensity)
                if not self._Buffers_Labels:
                    glActiveTexture(GL_TEXTURE0)
                    glBindTexture(GL_TEXTURE_2D, self._cube_covered_texture)
                    Buffer.is_texture_exist(self.__program.uniform_variables_dict, 1)
                    Buffer.set_texture_info(self.__program.uniform_variables_dict, 0)
                    for x_d, y_d, z_d in self.default_cube_position:
                        self.__translation_matrix[0][-1] = x_d
                        self.__translation_matrix[1][-1] = y_d
                        self.__translation_matrix[2][-1] = z_d
                        Buffer.draw_from_vao_buffer(self.__draw_type, self.__program.uniform_variables_dict, self.rotation_matrix.transpose(), self.__view_matrix, self.__projection_matrix.transpose(), self.normal_matrix, self.__translation_matrix)
                    glBindTexture(GL_TEXTURE_2D, 0)
                else:
                    Buffer.is_texture_exist(self.__program.uniform_variables_dict, 0)
                    for atom_index, (x_d, y_d, z_d) in enumerate(self.__calculation['POSITIONS'][self._step]):
                        if self._Buffers_Labels[index] == self.__calculation['ATOMNAMES'][atom_index]:
                            self.__translation_matrix[0][-1] = x_d
                            self.__translation_matrix[1][-1] = y_d
                            self.__translation_matrix[2][-1] = z_d
                            Buffer.draw_from_vao_buffer(self.__draw_type, self.__program.uniform_variables_dict, self.rotation_matrix.transpose(), self.__view_matrix, self.__projection_matrix.transpose(), self.normal_matrix, self.__translation_matrix)
                        if self._Buffers_Labels[index] == self.__calculation['ATOMNAMES'][atom_index] + '_Bond':
                            self.__translation_matrix[0][-1] = x_d
                            self.__translation_matrix[1][-1] = y_d
                            self.__translation_matrix[2][-1] = z_d
                            Buffer.draw_from_vao_buffer(self.__draw_type, self.__program.uniform_variables_dict, self.rotation_matrix.transpose(), self.__view_matrix, self.__projection_matrix.transpose(), self.normal_matrix, self.__translation_matrix)
                Buffer.end_of_drawing()
            pygame.display.flip()
            self.rotation_info[0], self.rotation_info[1] = 0.0, 0.0
            self._scale_parameter = 1.0
            self._x_d, self._y_d, self._z_d = 0.0, 0.0, 0.0
            curr_time = time.time()
            diff = curr_time - prev_time
            delay = max(1.0 / target_fps - diff, 0)
            time.sleep(delay)
            fps = 1.0 / (delay + diff)
            prev_time = curr_time
        for _ in range(len(self._VBO_Buffers)):
            self._VBO_Buffers.pop(0).__del__()
        self.__visual_window.close()
        pygame.quit()
