'''The main module of VaspReader.

Contains the code for the visualization window and provides processing of the graphical interface.

There are VaspReaderVisual and VaspReaderText classes in file and a lot of functions for visualization and connection with another modes of programm
'''
import sys
import time
#from psgtray import SystemTray
from functools import partial
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.WGL import *
from VaspReaderGUI import VRGUI
from VaspReaderGUI import core_GUI
from VaspReaderGUI import exiting_window
from VaspReaderGUI import traceback_window
from VaspReaderGUI import bonds_window
from VaspReaderPrint import VRPrint
from VaspReaderMD import VRMD
from VaspReaderProcessing import VRProcessing
from VaspReaderOszicar import VROszicarMode
from VaspReaderPoscar import VRPoscarForm
from VaspReaderPoscar import VRPoscarView
from VaspReaderSupercomputer import VRConsole
from VaspReaderSupercomputer import VRFileHosting
from VaspReaderChgcar import VRChgcar
import PySimpleGUI as sg
import traceback
import numpy as np
import math
import os
from os import environ
from PIL import ImageGrab
import win32gui
import ctypes
import json
import random
import threading
import freetype as ft
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from pygame.locals import *
from PIL import Image


def valid(text, limit):
    if text:
        try:
            return True if 0 <= float(text) <= limit else False
        except ValueError:
            return False
    return True


def check_input_text_numerical_value(class_number, window, value, element, limit=None):
    try:
        num = class_number(value[element].replace(',', '.'))
        if limit is not None and num > limit:
            while num > limit:
                num = class_number(value[element][:-1])
                window[element].update(num)
    except ValueError:
        window[element].update(value[element][:-1])


def TransformVec3(vecA, mat44):
    """Transform 3d vector to 2d projection."""
    vecB = [0, 0, 0, 0]  # при увеличении экрана возможно меняется проекционная матрица? и она домножается на коэффициент масштабирования
    for i0 in range(0, 4):
        vecB[i0] = vecA[0] * mat44[0 * 4 + i0] + vecA[1] * mat44[1 * 4 + i0] + vecA[2] * mat44[2 * 4 + i0] + mat44[3 * 4 + i0]
    return [vecB[0] / vecB[3], vecB[1] / vecB[3], vecB[2] / vecB[3]], vecB[3]


def perspective_choose(prjMat, mpos, ll, dis, parameter):
    """Option of choosing object in the screen.
       prjMat - projection matrix, mpos - mouse position at the screen,
       ll - atoms vertices, dis - display size, parametr - radii of sphere."""
    ll_ndc = [[0.0 for i in range(3)] for m in range(len(ll))]
    inRectCounter = 0  # atoms in sphere counter
    depth = list()  # atoms in sphere list
    mult = [0.0 for m in range(len(ll))]  # коэффициенты масштабирования пространства
    for num in range(len(ll)):
        ll_ndc[num], mult[num] = TransformVec3(ll[num], prjMat)  # координаты в мировом пространстве???
    radii = [parameter[i] / mult[i] * 2.0 for i in range(len(ll))]  # radius of projected sphere
    ndc = [2.0 * mpos[0] / dis[0] - 1.0, 1.0 - 2.0 * mpos[1] / dis[1]]
    inRect = [0 for m in range(len(ll))]  # список попаданий в атом, 0 - не попал, 1 - попал
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


def orthographic_choose(mpos, ll, dis, parameter):
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


def axis_cylinder_draw(axis_name_draw_function, rotate_angle):
    cyl_size, con_size = 0.75, 0.35
    gluCylinder(gluNewQuadric(), 0.1, 0.1, cyl_size, 16, 16)
    glTranslatef(0, 0, cyl_size)
    gluCylinder(gluNewQuadric(), 0.25, 0, con_size, 16, 16)
    axis_name_draw_function(rotate_angle)
    glTranslatef(0, 0, -cyl_size)


def x_axis_name_draw(rotate):
    glTranslatef(0.0, 0.6, 0.0)
    glRotatef(90 + rotate[2], 0, 1, 0)
    edges = ((0, 1), (2, 3))
    x_coordinates = np.array([[0.25, 0.25, 0.0], [-0.25, -0.25, 0.0], [-0.25, 0.25, 0.0], [0.25, -0.25, 0.0]])
    glLineWidth(3)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glColor4f(0.0, 1.0, 0.0, 1.0)
            glVertex3fv(x_coordinates[vertex])
    glEnd()
    glRotatef(-90 - rotate[2], 0, 1, 0)
    glTranslatef(0.0, -0.6, 0.0)


def y_axis_name_draw(rotate):
    glTranslatef(0.0, 0.0, 0.6)
    glRotatef(90, 1, 0, 0)
    glRotatef(-rotate[2], 0, 1, 0)
    edges = ((0, 1), (0, 2), (0, 3))
    y_coordinates = np.array([[0.0, 0.0, 0.0], [0.25, 0.25, 0.0], [-0.25, 0.25, 0.0], [0.25, -0.25, 0.0]])
    glLineWidth(3)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glColor4f(0.0, 0.0, 1.0, 1.0)
            glVertex3fv(y_coordinates[vertex])
    glEnd()
    glRotatef(rotate[2], 0, 1, 0)
    glRotatef(-90, 1, 0, 0)
    glTranslatef(0.0, 0.0, -0.6)


def z_axis_name_draw(rotate):
    glTranslatef(-0.6, 0.0, 0.0)
    glRotatef(-90, 0, 0, 1)
    glRotatef(-rotate[2], 0, 1, 0)
    edges = ((0, 1), (1, 2), (2, 3))
    z_coordinates = [[0.25, 0.25, 0.0], [-0.25, 0.25, 0.0], [0.25, -0.25, 0.0], [-0.25, -0.25, 0.0]]
    glLineWidth(3)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glColor4f(1.0, 0.0, 0.0, 1.0)
            glVertex3fv(z_coordinates[vertex])
    glEnd()
    glRotatef(rotate[2], 0, 1, 0)
    glRotatef(90, 0, 0, 1)
    glTranslatef(0.6, 0.0, 0.0)


def VR_logo_draw(x, y, z, first, second, rotate, display_scaling):
    x, y = (x - 4.5) / display_scaling, (y - 6) / display_scaling
    logo_coordinates = np.array([[1.5, 0, 1.1], [2, 0, 2.2], [2.5, 0, 3.3], [3, 0, 4.4], [1, 0, 0], [0.5, 0, 1.1], [0, 0, 2.2], [-0.5, 0, 3.3], [-1, 0, 4.4], [-1, 0, 3.3], [-1, 0, 2.2], [-1, 0, 1.1], [-1, 0, 0], [-2, 0, 4.4], [-2, 0, 2.2], [-2, 0, 4.4], [-2, 0, 2.2], [-2, 0, 1.1], [-3, 0, 3.3], [-3, 0, 0]])
    # logo_coordinates = tuple(list(map(lambda x: tuple(list(map(lambda i: i * display_scaling, x))), logo_coordinates)))
    glTranslatef(x, z, y)
    rotate += 1
    if rotate == 360:
        rotate = 0
    for num, vert in enumerate(logo_coordinates):
        glPushMatrix()
        glRotate(rotate, 0, 0, 1)
        glTranslatef(*vert)
        if num <= 7:
            glColor4f(*first, 1)
        else:
            glColor4f(*second, 1)
        gluSphere(gluNewQuadric(), 0.3, 24, 24)
        glPopMatrix()
    glTranslatef(-x, -z, -y)

    return rotate


def thread_save_calculations(object, opened_files):
    opened_files[0], opened_files[1] = object.save_calculation_state(True)


def remove_temp_files():
    try:
        os.remove('TEMP_CALC')
        os.remove('TEMP_CONFIG')
    except:
        pass


def main():
    global stay_in_tray
    menu = ['', ['Open program', 'Exit']]
    tooltip = 'VaspReader'
    first_start = True
    tray = ''
    program_window, settings, calculations, opened_files = '', '', '', [None, None]
    try:
        icon_image = r'VR_icons/VR-logo.ico'
    except:
        icon_image = sg.DEFAULT_BASE64_ICON

    #layout = [[sg.T('Empty Window', key='-T-')]]

    #window = sg.Window('Window in tray', layout, finalize=True, enable_close_attempted_event=True, alpha_channel=0)
    #window.hide()
    #while True:
    #    if first_start:
    #        first_start = False
    #        program_window = VRVisual()
    #        program_window.mainloop()
    #        if not stay_in_tray:
    #            break
    #        else:
    #            threading.Thread(target=thread_save_calculations, args=(program_window, opened_files)).start()
    #        tray = SystemTray(menu, single_click_events=False, window=window, tooltip=tooltip, icon=icon_image, key='-TRAY-')
    #        tray.show_message('VaspReader', 'VaspReader will stay in tray! You can run it from tray without start it again!')
    #    event, values = window.read()
    #    if event == tray.key:
    #        event = values[event]
    #    if event in (sg.WIN_CLOSED, 'Exit'):
    #        break
    #    if (event == 'Open program' or event == '__Double_Clicked__') and opened_files[0] is not None:
    #        settings, calculations = opened_files
    #        tray.hide_icon()
    #        settings.close()
    #        calculations.close()
    #        program_window = VRVisual()
    #        program_window.load_calculation_state('TEMP_CALC')
    #        remove_temp_files()
    #        program_window.mainloop()
    #        if not stay_in_tray:
    #            break
    #        else:
    #            threading.Thread(target=thread_save_calculations, args=(program_window, opened_files)).start()
    #        tray.show_icon()
    #if tray:
    #    tray.close()
    #window.close()
    VRVisual().mainloop()


class VRText(VRPrint):
    __font_dirname = ''
    __default_dirname = r'TextRender\timesnewromanpsmt.ttf'

    def __init__(self, font_dirname=''):
        VRPrint.__init__(self)
        self.__text, self.__image = [], Image.Image()
        self.__font_dirname = font_dirname if font_dirname else self.__default_dirname
        try:
            self.__face = ft.Face(self.__font_dirname)
        except:
            self.__font_dirname = self.__default_dirname
            self.__face = ft.Face(self.__font_dirname)
        self.__face.set_char_size(48 * 64)
        self.__stroker = ft.Stroker()
        self.__stroker.set(1, ft.FT_STROKER_LINECAPS['FT_STROKER_LINECAP_ROUND'], ft.FT_STROKER_LINEJOINS['FT_STROKER_LINEJOIN_ROUND'], 0)

    def load_char(self, char):
        self.__face.load_char(char, ft.FT_LOAD_FLAGS['FT_LOAD_DEFAULT'])
        glyph = ft.FT_Glyph()
        ft.FT_Get_Glyph(self.__face. glyph. _FT_GlyphSlot, ft.byref(glyph))
        glyph = ft.Glyph(glyph)
        error = ft.FT_Glyph_StrokeBorder(ft.byref(glyph. _FT_Glyph), self.__stroker. _FT_Stroker, False, False)
        if not error:
            bitmapGlyph = glyph.to_bitmap(ft.FT_RENDER_MODES['FT_RENDER_MODE_NORMAL'], 0)
            bitmap = ft.Bitmap(bitmapGlyph.bitmap)
            self.__text.append(np.array(bitmap.buffer).reshape((bitmap.rows, bitmap.width)))

    def load_string(self, string):
        for char in string:
            self.load_char(char)

    def del_char(self, position):
        try:
            self.__text.pop(position)
        except:
            self.print('No such element in text.')

    def clear_text(self):
        self.__text.clear()
        self.__image = Image.Image()

    def compile_image(self):
        max_array_height = []
        for image in self.__text:
            max_array_height.append(image.shape[0])
        max_array_height = max(max_array_height) if max_array_height else 0
        for num, image in enumerate(self.__text):
            if image.shape[0] < max_array_height:
                self.__text[num] = np.concatenate((np.zeros((max_array_height - image.shape[0], image.shape[1])), image), axis=0)
        output = self.__text[0] if self.__text else np.array([[0]])
        for image in self.__text[1:]:
            output = np.concatenate((output, image), axis=1)
        output = np.array(output, dtype='object')
        converted = np.zeros((output.shape[0], output.shape[1], 4))
        for axis1 in range(output.shape[0]):
            for axis2 in range(output.shape[1]):
                converted[axis1][axis2][0] = 255 if output[axis1][axis2] == 0 else 0
                converted[axis1][axis2][1] = 255 if output[axis1][axis2] == 0 else 100
                converted[axis1][axis2][2] = 255 if output[axis1][axis2] == 0 else 0
                converted[axis1][axis2][3] = 0 if output[axis1][axis2] == 0 else 255
        # output = output.astype('uint8')
        self.__image = Image.fromarray(converted.astype('uint8'), 'RGBA')

    def get_image(self):
        return self.__image

    def show(self):
        if not self.__image.size[0]:
            self.compile_image()
        self.__image.show()


class VRVisual(VRGUI, VRPrint):
    default_display = (800, 600)
    light_variables = (GL_LIGHT0, GL_LIGHT1, GL_LIGHT2, GL_LIGHT3, GL_LIGHT4, GL_LIGHT5, GL_LIGHT6, GL_LIGHT7)
    light_states = {i: False for i in range(8)}
    light_positions = [[10, 10, 10], [10, 10, -10], [10, -10, 10], [10, -10, -10], [-10, 10, 10], [-10, 10, -10],
                       [-10, -10, 10], [-10, -10, -10]]
    background_color = (0.5, 0.5, 0.5)
    view_axes = True
    select_symbol = '✅'
    numpy_array_names = ['POSITIONS', 'DIRECT', 'BASIS_VERT', 'BASIS']
    menu_parameters = ['View axes', 'View cell boarder', 'Light1', 'Light2', 'Light3', 'Light4', 'Light5',
                       'Light6', 'Light7', 'Light8', 'Perspective', 'Orthographic', 'Keyboard',
                       'Mouse+Keyboard']
    menu_def = [['&File', ['&Open Calculation     Ctrl-O', '---', '&Save Calc State       Ctrl-S', '&Load Calc State       Ctrl-L', '---', 'Save Program Configuration', 'Load Program Configuration', '---', 'Send to tray', 'E&xit']],
                ['&Edit', ['View axes', 'View cell boarder', 'Del coords after leave a cell', 'Light', ['Light1', 'Light2', 'Light3', 'Light4', 'Light5', 'Light6', 'Light7', 'Light8'], 'Visualization Type', ['Perspective', 'Orthographic'], 'Background Color']],
                ['&Mods', ['Processing', 'Spectrum', 'Supercomputer', ['Console', 'File hosting'], 'OSZICAR', 'POSCAR', 'CHGCAR', 'Graphs']],
                ['&Tools', ['Select mode', ['Keyboard', 'Mouse+Keyboard', 'Select from listbox'], '---', 'Calculate bonds', 'Set', ['ID', 'Bond length', 'Valence angle'], '---', 'Form POSCAR', '---', 'Screenshot']],
                ['&Help', ['&About the program', 'Window description', 'Latest update', 'Changes history']]]
    change_menu_positions = ((1, 1, 0), (1, 1, 1), (1, 1, 4, 0), (1, 1, 4, 1), (1, 1, 4, 2),
                             (1, 1, 4, 3), (1, 1, 4, 4), (1, 1, 4, 5), (1, 1, 4, 6), (1, 1, 4, 7),
                             (1, 1, 6, 0), (1, 1, 6, 1), (3, 1, 1, 0), (3, 1, 1, 1), (3, 1, 1, 2), (1, 1, 2),
                             (3, 1, 5, 0), (3, 1, 5, 1), (3, 1, 5, 2))

    def __init__(self, GUI_type=core_GUI, title='VaspReader', **kwargs):
        super(VRVisual, self).__init__(GUI_type, title, resizable=True, keep_on_top=False, enable_close_attempted_event=True, location=sg.user_settings_get_entry('-location-', (None, None)), theme=sg.user_settings_get_entry('-theme-', 'VRGUI'), **kwargs)
        VRPrint.__init__(self)
        self.text = VRText()
        global stay_in_tray
        stay_in_tray = False
        self.start_program()
        self.__parameters_to_change_menu = [False for i in range(19)]
        self.__core_event, self.__core_value = None, None
        self.text_textures, self.numbers_textures, self.textures_3d = dict(), dict(), dict()
        self.bond_window_active, self.bond_event, self.bond_value, self.bond_window, self.prev_draw_bond_step, self.recalculate_bonds = False, None, None, None, -1, False
        self.bonds_window_refresh, self.trajectory_draw_mode, self.trajectory_steps, self.trajectory_bonds, self.trajectory_first_bonds_calculate = False, False, [], dict(), False
        self.trajectory_range_info, self.first_event_of_bond_window = (), True
        self.now_calc, self.step, self.prev_step, self.color, self.vertices, self.now_step_vertices, self.speed, self.radii = '', 0, 0, None, np.array([]), np.array([]), None, []
        self.prev_calc = ''
        self.POSCAR_form_object, self.POSCAR_form_object_to_none = None, False
        self.__calculations = dict()
        self.directory = None
        self.axes_rotate, self.cell, self.rotate, self.only_keyboard_select, self.draw_cell, self.perspective, self.add_listbox_selection, self.del_cord_leave_cell = None, np.array([]), None, True, True, True, False, True
        self.Back_Step, self.Forward_Step = False, False
        self.display, self.window_size = list(self.default_display), list(self.default_display)
        self.selected_atoms = dict()
        self.scale_parameter = 1
        self.new_coordinate_start = [0, 0]
        self.display_scaling = 1
        self.now_menu = self.menu_parameters.copy()
        self.generate_event = ''
        self.processing_obj = None
        self.theme = sg.user_settings_get_entry('-theme-', 'VRGUI')
        self.mouse_pressed = False
        self.change_model_view, self.change_select_mode, self.calculation_changed = False, False, True
        self.calculation_parsed, self.CLOSE_POSCAR_IF_OPEN = False, False
        self.start_texture = ''
        self.set_ID_mode, self.set_bond_mode, self.set_valence_mode = False, False, False
        self.bond_and_valence_counter, self.bond_and_valence_atoms, self.bonds_or_valence_dict = 0, [], {'bonds': [], 'valence_angles': []}
        self.x_displ, self.y_displ, self.z_displ = 0, 0, 0
        self.fog_exist, self.fog_color = False, self.background_color
        self.chgcar = VRChgcar(hide=True)
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        pygame.init()
        try:
            self.win_icon = r'VR_icons/VR-logo.png'
            pygame.display.set_icon(pygame.image.load(self.win_icon))
        except FileNotFoundError:
            pass
        pygame.display.set_caption('VR')
        self.scree = pygame.display.set_mode(self.default_display, DOUBLEBUF | OPENGL | pygame.RESIZABLE)
        glMatrixMode(GL_PROJECTION)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1, 1, 1, 1])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 128.0)

        gluPerspective(45, (self.default_display[0] / self.default_display[1]), 0.1, 60.0)
        gluLookAt(0, 20, 0, 0, 0, 0, 0, 0, 1)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        self.DisplayCenter = [self.scree.get_size()[i] // 2 for i in range(2)]
        pygame.mouse.set_pos(self.DisplayCenter)
        if not self.light_states[0]:
            self.window_light(0, self.light_positions[0])
        else:
            glEnable(self.light_variables[0])
            glLight(self.light_variables[0], GL_POSITION, (*self.light_positions[0], 1))
            glLightfv(self.light_variables[0], GL_AMBIENT, [0.1, 0.1, 0.1, 1])
            glLightfv(self.light_variables[0], GL_DIFFUSE, [1, 1, 1, 1])
            glLightfv(self.light_variables[0], GL_SPECULAR, [1, 1, 1, 1])
        self.menu_change()

    def menu_change(self):
        now_parameters = [self.view_axes, self.draw_cell, *self.light_states_to_list(), self.perspective, not self.perspective, self.only_keyboard_select, not self.only_keyboard_select, self.add_listbox_selection, self.del_cord_leave_cell, self.set_ID_mode, self.set_bond_mode, self.set_valence_mode]
        if now_parameters != self.__parameters_to_change_menu:
            self.__parameters_to_change_menu = now_parameters.copy()
            self.now_menu = self.menu_def
            for num, parameter in enumerate(self.__parameters_to_change_menu):
                temp = self.now_menu
                for element_num, element in enumerate(self.change_menu_positions[num]):
                    if element_num != len(self.change_menu_positions[num]) - 1:
                        temp = temp[element]
                    else:
                        if parameter:
                            if temp[element][0] != self.select_symbol:
                                temp[element] = self.select_symbol + temp[element]
                        else:
                            if temp[element][0] == self.select_symbol:
                                temp[element] = temp[element][1:]
            self.window['-MENUBAR-'].update(menu_definition=self.now_menu)
            self.window.refresh()

    def window_light(self, light_variable_number, light_position):
        self.light_states[light_variable_number] = not self.light_states[light_variable_number]
        if self.light_states[light_variable_number]:
            glEnable(self.light_variables[light_variable_number])
            glLight(self.light_variables[light_variable_number], GL_POSITION, (*light_position, 1))
            glLightfv(self.light_variables[light_variable_number], GL_AMBIENT, [0.1, 0.1, 0.1, 1])
            glLightfv(self.light_variables[light_variable_number], GL_DIFFUSE, [1, 1, 1, 1])
            glLightfv(self.light_variables[light_variable_number], GL_SPECULAR, [1, 1, 1, 1])
        else:
            glDisable(self.light_variables[light_variable_number])

    def light_states_to_list(self):
        return [light[-1] for light in self.light_states.items()]

    def load_3d_texture(self, key, width, height, depth, array):
        self.textures_3d[key] = glGenTextures(1)
        glBindTexture(GL_TEXTURE_3D, self.textures_3d[key])
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)  # GL_NEAREST
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_BORDER)  # GL_RGBA16    GL_RGBA
        glTexImage3D(GL_TEXTURE_3D, 0, GL_RGBA16, width, height, depth, 0, GL_RGBA, GL_FLOAT, array)
        glBindTexture(GL_TEXTURE_3D, 0)

    def load_texture(self, string='', tex_type='text', texture_name=''):  # , texture
        key = tex_type if not texture_name else texture_name
        if tex_type == 'text':
            self.text_textures[key] = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.text_textures[key])
        elif tex_type == 'background':
            self.start_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.start_texture)
        elif tex_type == 'numbers':
            self.numbers_textures[key] = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.numbers_textures[key])

        # load image
        if tex_type == 'text' or tex_type == 'numbers':
            self.text.clear_text()
            self.text.load_string(string)
            self.text.compile_image()
            image = self.text.get_image()
        else:
            image = Image.open(r'Debug_Wallpaper\Start_text.png')
            image = image.convert("RGBA")
        img_data = image.tobytes()
        # Set the texture wrapping parameters
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        color = [1.0, 1.0, 1.0, 0.0]
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, color)
        # Set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glBindTexture(GL_TEXTURE_2D, 0)

    def draw_texture(self, position, textures_container=None, key='text'):
        if textures_container is None:
            textures_container = self.text_textures
        glColor4f(1.0, 1.0, 1.0, 1.0)
        vertices = np.array([[-0.5, 0.0, 0.4], [-1.1, 0.0, 0.4], [-1.1, 0.0, 0.0], [-0.5, 0.0, 0.0]])
        vertices = np.dot(vertices, self.rotate[0:3, 0:3].transpose())
        vertices = np.array([[position[i] + vertices[j][i] for i in range(3)] for j in range(4)])
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, textures_container[key])
        glPushMatrix()
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(*vertices[0])
        glTexCoord2f(1.0, 0.0)
        glVertex3f(*vertices[1])
        glTexCoord2f(1.0, 1.0)
        glVertex3f(*vertices[2])
        glTexCoord2f(0.0, 1.0)
        glVertex3f(*vertices[3])
        glEnd()
        glPopMatrix()
        glBindTexture(GL_TEXTURE_2D, 0)

    def draw_3d_texture(self, key, vertices):
        basis = vertices / 2
        # glEnable(GL_ALPHA_TEST)
        # glAlphaFunc(GL_GREATER, 0.03)
        glMatrixMode(GL_TEXTURE)
        # glLoadIdentity()
        # glMultMatrixf(self.rotate)
        glEnable(GL_TEXTURE_3D)
        glBindTexture(GL_TEXTURE_3D, self.textures_3d[key])
        glColor4f(*self.chgcar.color)
        glPushMatrix()
        glBegin(GL_QUADS)
        for z_c in np.linspace(1, 0, self.chgcar.array_shape[0]):
            # texcoords = np.dot(np.array([[0.0, 0.0, z_c], [0.0, 1.0, z_c], [1.0, 0.0, z_c], [1.0, 1.0, z_c]]), self.rotate[0:3, 0:3].transpose())
            # arr = np.dot(np.dot(np.array([[-1.0, -1.0, 2 * z_c - 1], [-1.0, 1.0, 2 * z_c - 1], [1.0, -1.0, 2 * z_c - 1], [1.0, 1.0, 2 * z_c - 1]]), basis.transpose()), self.rotate[0:3, 0:3].transpose()).transpose()

            arr = np.dot(np.array([[-1.0, -1.0, 2 * z_c - 1], [-1.0, 1.0, 2 * z_c - 1], [1.0, -1.0, 2 * z_c - 1], [1.0, 1.0, 2 * z_c - 1]]), basis.transpose()).transpose()
            texcoords = np.array([[0.0, 0.0, z_c], [0.0, 1.0, z_c], [1.0, 0.0, z_c], [1.0, 1.0, z_c]])
            # texcoords = np.dot(np.array([[0.0, -z_c, 0.0], [0.0, -z_c, 1.0], [-1.0, -z_c, 0.0], [-1.0, -z_c, 1.0]]), self.rotate[0:3, 0:3].transpose())
            # arr = np.dot(np.dot(np.array([[1.0, -(2 * z_c - 1), -1.0], [1.0, -(2 * z_c - 1), 1.0], [-1.0, -(2 * z_c - 1), -1.0], [-1.0, -(2 * z_c - 1), 1.0]]), self.rotate[0:3, 0:3].transpose()), basis.transpose()).transpose()
            glTexCoord3d(texcoords[0][0], texcoords[0][1], texcoords[0][2])
            glVertex3d(arr[0][0], arr[1][0], arr[2][0])
            glTexCoord3d(texcoords[1][0], texcoords[1][1], texcoords[1][2])
            glVertex3d(arr[0][1], arr[1][1], arr[2][1])
            glTexCoord3d(texcoords[2][0], texcoords[2][1], texcoords[2][2])
            glVertex3d(arr[0][2], arr[1][2], arr[2][2])
            glTexCoord3d(texcoords[3][0], texcoords[3][1], texcoords[3][2])
            glVertex3d(arr[0][3], arr[1][3], arr[2][3])
        glEnd()
        glPopMatrix()
        glBindTexture(GL_TEXTURE_3D, 0)
        glMatrixMode(GL_MODELVIEW)

    def find_window_dimensions(self, far):
        far = 20 + far
        x_limit = math.sin(math.pi / 16 * 3) * far
        y_limit = x_limit / 4 * 3
        if self.window_size[0] / 4 < self.window_size[1] / 3:
            x_limit = x_limit * (self.window_size[0] / self.display[0])
        else:
            y_limit = y_limit * (self.window_size[1] / self.display[1])
        return x_limit, y_limit, -(far - 20)

    def draw_start_texture(self, tex_type='background'):
        x, y, z = self.find_window_dimensions(1.6)
        start_texture_coords = np.array([[-x, z, -y], [x, z, -y], [x, z, y], [-x, z, y]])
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.start_texture)
        glBegin(GL_QUADS)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(*start_texture_coords[0])
        glTexCoord2f(0.0, 1.0)
        glVertex3f(*start_texture_coords[1])
        glTexCoord2f(0.0, 0.0)
        glVertex3f(*start_texture_coords[2])
        glTexCoord2f(1.0, 0.0)
        glVertex3f(*start_texture_coords[3])
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)

    def draw_bond_or_valence_angle(self):
        for atoms in self.bonds_or_valence_dict['bonds']:
            num1, num2 = [self.__calculations[self.now_calc]['ID-TO-NUM'][atom] for atom in atoms]
            distance = round(sum([(self.now_step_vertices[num1][i] - self.now_step_vertices[num2][i]) ** 2 for i in range(3)]) ** 0.5, 2)
            self.draw_numeric_texture(distance, (self.now_step_vertices[num1] + self.now_step_vertices[num2]) / 2)
            glPushAttrib(GL_ENABLE_BIT)
            glLineStipple(1, 0x0F0F)
            glEnable(GL_LINE_STIPPLE)
            glLineWidth(2 / self.scale_parameter)
            glBegin(GL_LINES)
            glColor4f(1.0, 1.0, 0.0, 1.0)
            glVertex3fv(self.now_step_vertices[num1])
            glVertex3fv(self.now_step_vertices[num2])
            glEnd()
            glPopAttrib()

        for atoms in self.bonds_or_valence_dict['valence_angles']:
            num1, num2, num3 = [self.__calculations[self.now_calc]['ID-TO-NUM'][atom] for atom in atoms]
            distances = [sum([(self.now_step_vertices[num1][i] - self.now_step_vertices[num2][i]) ** 2 for i in range(3)]), sum([(self.now_step_vertices[num1][i] - self.now_step_vertices[num3][i]) ** 2 for i in range(3)]), sum([(self.now_step_vertices[num2][i] - self.now_step_vertices[num3][i]) ** 2 for i in range(3)])]
            angle = round(math.degrees(math.acos((distances[0] + distances[2] - distances[1]) / (2 * distances[0] ** 0.5 * distances[2] ** 0.5))), 2)
            vec1 = self.now_step_vertices[num1] - self.now_step_vertices[num2]
            vec2 = self.now_step_vertices[num3] - self.now_step_vertices[num2]
            position = self.now_step_vertices[num2] + 0.75 * (vec1 / np.sqrt(np.sum(np.power(vec1, 2))) + vec2 / np.sqrt(np.sum(np.power(vec2, 2))))
            self.draw_numeric_texture(angle, position)
            glLineWidth(2 / self.scale_parameter)
            glBegin(GL_LINES)
            glColor4f(1.0, 1.0, 0.0, 1.0)
            glVertex3fv(self.now_step_vertices[num1])
            glVertex3fv(self.now_step_vertices[num2])
            glVertex3fv(self.now_step_vertices[num2])
            glVertex3fv(self.now_step_vertices[num3])
            glEnd()

    def draw_numeric_texture(self, value, position):
        if not isinstance(value, str):
            value = str(value)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        vertices = []
        texture_width_center = 0.15 * len(value) / 2
        for index in range(0, len(value)):
            vertices.append([-0.15 * index + texture_width_center, 0.0, 0.4])  # -0.5
            vertices.append([-0.15 * index + texture_width_center, 0.0, 0.0])
            vertices.append([-0.15 * (index + 1) + texture_width_center, 0.0, 0.4])
            vertices.append([-0.15 * (index + 1) + texture_width_center, 0.0, 0.0])
        vertices = np.array(vertices)
        vertices = np.dot(vertices, self.rotate[0:3, 0:3].transpose())
        vertices = np.array([position + vertices[j] for j in range(vertices.shape[0])])
        for num, char in enumerate(value):
            glEnable(GL_TEXTURE_2D)
            if char == '.':
                glBindTexture(GL_TEXTURE_2D, self.numbers_textures[char])
                glPushMatrix()
                glBegin(GL_QUADS)
                glTexCoord2f(6.0, 0.0)
                glVertex3f(*vertices[4 * num])
                glTexCoord2f(0.0, 0.0)
                glVertex3f(*vertices[4 * num + 1])
                glTexCoord2f(0.0, 4.0)
                glVertex3f(*vertices[4 * num + 3])
                glTexCoord2f(6.0, 4.0)
                glVertex3f(*vertices[4 * num + 2])
                glEnd()
                glPopMatrix()
                glBindTexture(GL_TEXTURE_2D, 0)
            else:
                glBindTexture(GL_TEXTURE_2D, self.numbers_textures[char])
                glPushMatrix()
                glBegin(GL_QUADS)
                glTexCoord2f(0.0, 0.0)
                glVertex3f(*vertices[4 * num])
                glTexCoord2f(0.0, 1.0)
                glVertex3f(*vertices[4 * num + 1])
                glTexCoord2f(1.0, 1.0)
                glVertex3f(*vertices[4 * num + 3])
                glTexCoord2f(1.0, 0.0)
                glVertex3f(*vertices[4 * num + 2])
                glEnd()
                glPopMatrix()
                glBindTexture(GL_TEXTURE_2D, 0)

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

    def json_save(self, save_file):
        with open(save_file, 'w') as json_save:
            json.dump(self.__calculations, json_save)

    def save_program_configuration(self):
        save_settings = sg.popup_get_file(message='Save configuration', title='Save configuration', save_as=True, no_window=True, no_titlebar=True, file_types=(('Txt', '*.txt'),))
        if save_settings:
            to_file = {'-CELL-': self.draw_cell, '-AXES-': self.view_axes, '-BACGROUND-COLOR-': self.background_color, '-LIGHT-': self.light_states, '-MODEL-VIEW-': self.perspective, '-ATOM-CHOOSE-TYPE-': self.only_keyboard_select, '-ADD-LISTBOX-SELECTION-': self.add_listbox_selection, '-DEL-COORD-AFTER-LEAVE-': self.del_cord_leave_cell}
            with open(save_settings, 'w') as settings:
                json.dump(to_file, settings)

    def load_program_configuration(self, load_settings=''):
        if not load_settings:
            load_settings = sg.popup_get_file(message='Load configuration', title='Load configuration', save_as=False, no_window=True, no_titlebar=True, file_types=(('Txt', '*.txt'),))
        if load_settings:
            light_state = self.light_states
            with open(load_settings, 'r') as settings:
                try:
                    from_file = json.load(settings)
                    self.draw_cell, self.view_axes, self.background_color, light_state, self.perspective, self.only_keyboard_select, self.add_listbox_selection, self.del_cord_leave_cell = from_file['-CELL-'], from_file['-AXES-'], from_file['-BACGROUND-COLOR-'], from_file['-LIGHT-'], from_file['-MODEL-VIEW-'], from_file['-ATOM-CHOOSE-TYPE-'], from_file['-ADD-LISTBOX-SELECTION-'], from_file['-DEL-COORD-AFTER-LEAVE-']
                    light_state = {int(key): value for key, value in light_state.items()}
                    self.change_model_view, self.change_select_mode = True, True
                    self.window['selected_atoms'].update(visible=self.add_listbox_selection)
                    self.window.set_min_size(self.window.size)
                except:
                    self.print('Error of configuration load. Try to create setting file again.', background_color='red')
            self.change_light_to_input(light_state)

    def change_light_to_input(self, light_state):
        for light in light_state:
            if self.light_states[light] != light_state[light]:
                self.window_light(light, self.light_positions[light])

    def calculation_change(self):
        self.calculation_changed = False
        if self.__calculations[self.now_calc].get('BONDS_INFO', None) is None:
            self.__calculations[self.now_calc]['BONDS_INFO'] = dict()
            self.__calculations[self.now_calc]['ALLOWED_BONDS'] = dict()
        if self.__calculations[self.now_calc].get('IS_DRAW_BONDS', None) is None:
            self.__calculations[self.now_calc]['IS_DRAW_BONDS'] = False
        if self.prev_calc:
            self.__calculations[self.prev_calc]['TEXT_TEXTURES'] = self.text_textures
            self.__calculations[self.prev_calc]['BONDS_AND_VALENCE_TEXTURES'] = self.bonds_or_valence_dict
        self.text_textures = self.__calculations[self.now_calc].get('TEXT_TEXTURES', dict())
        self.bonds_or_valence_dict = self.__calculations[self.now_calc].get('BONDS_AND_VALENCE_TEXTURES', {'bonds': [], 'valence_angles': []})
        self.prev_draw_bond_step = -1
        self.vertices = self.__calculations[self.now_calc]['POSITIONS']
        self.cell = self.__calculations[self.now_calc]['BASIS_VERT']
        self.radii = self.__calculations[self.now_calc]['RADII'].copy()
        self.color = self.__calculations[self.now_calc]['COLORVALUE'].copy()
        self.window['slider'].update(value=0, range=(0, self.__calculations[self.now_calc]['STEPS'] - 1))
        self.Back_Step, self.Forward_Step = False, False
        self.step, self.prev_step = 0, 0
        self.scale_parameter = 1
        self.selected_atoms = {num: False for num in range(self.__calculations[self.now_calc]['ATOMNUMBER'])}
        self.speed = math.ceil((self.vertices.shape[0] - 1) / 100 / 10 * int(self.__core_value['slider_speed'] if self.__core_value is not None else 1) / 100)
        self.window['selected_atoms'].update(values=self.__calculations[self.now_calc]['ID'])
        self.bonds_window_refresh, self.trajectory_draw_mode, self.trajectory_steps, self.trajectory_bonds, self.trajectory_first_bonds_calculate = True, False, [], dict(), False
        self.trajectory_range_info, self.CLOSE_POSCAR_IF_OPEN = (), True

    def save_calculation_state(self, to_tray=False):
        save_file = ''
        if not to_tray:
            save_file = sg.popup_get_file(message='Save state', title='Save state', save_as=True, no_window=True, no_titlebar=True, file_types=(('JSON', '*.json'),))
        else:
            to_file = {'-CELL-': self.draw_cell, '-AXES-': self.view_axes, '-BACGROUND-COLOR-': self.background_color, '-LIGHT-': self.light_states, '-MODEL-VIEW-': self.perspective, '-ATOM-CHOOSE-TYPE-': self.only_keyboard_select}
            settings = open('TEMP_CONFIG', 'w')
            json.dump(to_file, settings)
            for key in self.__calculations:
                for name in self.numpy_array_names:
                    self.__calculations[key][name] = self.__calculations[key][name].tolist()
            calculations = open('TEMP_CALC', 'w')
            json.dump(self.__calculations, calculations)
            return settings, calculations
        if save_file:
            for key in self.__calculations:
                for name in self.numpy_array_names:
                    self.__calculations[key][name] = self.__calculations[key][name].tolist()
            self.window.perform_long_operation(lambda: self.json_save(save_file), end_key='-STATESAVED-')

    def load_calculation_state(self, load_file=''):
        if not load_file:
            load_file = sg.popup_get_file(message='Load state', title='Load state', save_as=False, no_window=True, no_titlebar=True, file_types=(('JSON', '*.json'),))
        else:
            self.load_program_configuration(load_settings='TEMP_CONFIG')
        if load_file:
            with open(load_file, 'r') as json_load:
                self.__calculations = json.load(json_load)
            if self.__calculations:
                for key in self.__calculations:
                    for name in self.numpy_array_names:
                        self.__calculations[key][name] = np.array(self.__calculations[key][name])
                calculations_names = list(self.__calculations.keys())
                self.prev_calc = ''
                for key in self.__calculations:
                    try:
                        self.__calculations[key]['TEXT_TEXTURES'].clear()
                        self.__calculations[key]['BONDS_AND_VALENCE_TEXTURES'].clear()
                    except:
                        pass
                self.now_calc = calculations_names[-1]
                self.window['-MDCALC-'].update(value=self.now_calc, values=calculations_names)
                self.calculation_change()
                self.print(f'Loaded calculations: {list(self.__calculations.keys())}')
                self.calculation_parsed = True

    def select_atom(self, select):
        self.Back_Step, self.Forward_Step = False, False
        parameter = (0.8, 1.25)
        mouseClick = pygame.mouse.get_pos()
        mouseClick = [mouseClick[i] - self.new_coordinate_start[i] for i in range(2)]
        if self.perspective:
            prjMat = (GLfloat * 16)()
            glGetFloatv(GL_PROJECTION_MATRIX, prjMat)
            prjMat = np.dot(self.rotate, np.array(prjMat).reshape((4, 4))).reshape((16, 1))
            onRect = perspective_choose(prjMat, mouseClick, self.now_step_vertices, self.display, self.radii)
        else:
            coordinates = (np.dot(self.now_step_vertices, self.rotate[0:3, 0:3]) + np.array([[*self.rotate[3, :3]] for _ in range(self.now_step_vertices.shape[0])])) / self.rotate[-1, -1]
            onRect = orthographic_choose(mouseClick, coordinates, self.display, self.radii)
        already_selected = False
        if select:
            for num, selected in enumerate(onRect):
                if selected and not self.selected_atoms[num] and not (self.set_ID_mode or self.set_bond_mode or self.set_valence_mode):
                    self.selected_atoms[num] = True
                    self.radii[num] = self.radii[num] * parameter[1]
                    self.color[num] = [self.color[num][k] / 2 for k in range(3)]
                    self.print(f'You chose: {self.__calculations[self.now_calc]["ID"][num]}.')
                elif self.set_ID_mode and selected and not self.text_textures.get(self.__calculations[self.now_calc]["ID"][num], False):
                    text = self.__calculations[self.now_calc]["ID"][num]
                    self.load_texture(string=text, tex_type='text', texture_name=text)
                elif self.set_bond_mode and selected:
                    self.bond_and_valence_counter += 1
                    self.bond_and_valence_atoms.append(self.__calculations[self.now_calc]["ID"][num])
                    self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][self.bond_and_valence_atoms[-1]]] = self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][self.bond_and_valence_atoms[-1]]] * 1.25
                    if self.bond_and_valence_counter == 2:
                        self.bond_and_valence_counter = 0
                        checker = 0
                        for atoms in self.bonds_or_valence_dict['bonds']:
                            if self.bond_and_valence_atoms[0] in atoms and self.bond_and_valence_atoms[1] in atoms:
                                checker += 1
                        if checker == 0:
                            self.bonds_or_valence_dict['bonds'].append(tuple(self.bond_and_valence_atoms))
                        for atom in self.bond_and_valence_atoms:
                            self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][atom]] = self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][atom]] / 1.25
                        self.bond_and_valence_atoms.clear()
                elif self.set_valence_mode and selected:
                    self.bond_and_valence_counter += 1
                    self.bond_and_valence_atoms.append(self.__calculations[self.now_calc]["ID"][num])
                    self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][self.bond_and_valence_atoms[-1]]] = self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][self.bond_and_valence_atoms[-1]]] * 1.25
                    if self.bond_and_valence_counter == 3:
                        self.bond_and_valence_counter = 0
                        checker = 0
                        for atoms in self.bonds_or_valence_dict['valence_angles']:
                            if self.bond_and_valence_atoms[0] in atoms and self.bond_and_valence_atoms[1] in atoms and self.bond_and_valence_atoms[2] in atoms:
                                checker += 1
                        if checker == 0:
                            self.bonds_or_valence_dict['valence_angles'].append(tuple(self.bond_and_valence_atoms))
                        for atom in self.bond_and_valence_atoms:
                            self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][atom]] = self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][atom]] / 1.25
                        self.bond_and_valence_atoms.clear()
                elif selected and self.selected_atoms[num]:
                    already_selected = True
        else:
            for num, selected in enumerate(onRect):
                if selected and self.selected_atoms[num] and not (self.set_ID_mode or self.set_bond_mode or self.set_valence_mode):
                    self.selected_atoms[num] = False
                    self.radii[num] = self.radii[num] * parameter[0]
                    self.color[num] = [self.color[num][k] * 2 for k in range(3)]
                    self.print(f'{self.__calculations[self.now_calc]["ID"][num]} deselected.')
                elif self.set_ID_mode and selected and self.text_textures.get(self.__calculations[self.now_calc]["ID"][num], False):
                    self.text_textures.pop(self.__calculations[self.now_calc]["ID"][num])
                elif self.set_bond_mode and selected:
                    self.bond_and_valence_counter += 1
                    self.bond_and_valence_atoms.append(self.__calculations[self.now_calc]["ID"][num])
                    self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][self.bond_and_valence_atoms[-1]]] = self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][self.bond_and_valence_atoms[-1]]] * 1.25
                    if self.bond_and_valence_counter == 2:
                        self.bond_and_valence_counter = 0
                        checker = 0
                        for atoms in list(self.bonds_or_valence_dict['bonds']):
                            if self.bond_and_valence_atoms[0] in atoms and self.bond_and_valence_atoms[1] in atoms:
                                self.bonds_or_valence_dict['bonds'].remove(atoms)
                        for atom in self.bond_and_valence_atoms:
                            self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][atom]] = self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][atom]] / 1.25
                        self.bond_and_valence_atoms.clear()
                elif self.set_valence_mode and selected:
                    self.bond_and_valence_counter += 1
                    self.bond_and_valence_atoms.append(self.__calculations[self.now_calc]["ID"][num])
                    self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][self.bond_and_valence_atoms[-1]]] = self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][self.bond_and_valence_atoms[-1]]] * 1.25
                    if self.bond_and_valence_counter == 3:
                        self.bond_and_valence_counter = 0
                        checker = 0
                        for atoms in list(self.bonds_or_valence_dict['valence_angles']):
                            if self.bond_and_valence_atoms[0] in atoms and self.bond_and_valence_atoms[1] in atoms and self.bond_and_valence_atoms[2] in atoms:
                                self.bonds_or_valence_dict['valence_angles'].remove(atoms)
                        for atom in self.bond_and_valence_atoms:
                            self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][atom]] = self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][atom]] / 1.25
                        self.bond_and_valence_atoms.clear()
                elif selected and not self.selected_atoms[num]:
                    already_selected = True
        if already_selected:
            self.print('This atom was already chose.' if select else 'This atom was already deleted.')
        index_list = [index for index in self.selected_atoms if self.selected_atoms[index]]
        self.window['selected_atoms'].update(set_to_index=index_list)
        pygame.time.wait(200)

    def axes_draw(self):
        """Drawing axes."""
        x, y, z = self.find_window_dimensions(-4)
        translate = [x - 1.8 / self.display_scaling, z, -y + 1.8 / self.display_scaling]
        back_translate = list(map(lambda i: -i, translate))
        glPushMatrix()
        glTranslatef(*translate)
        ################################################################################################################
        glColor4f(0, 0, 0, 1.0)
        gluSphere(gluNewQuadric(), 0.15, 24, 24)
        glRotate(-self.axes_rotate[0], 1, 0, 0)
        glRotate(self.axes_rotate[2], 0, 0, 1)
        ################################################################################################################
        glColor4f(0, 0, 1, 1.0)
        axis_cylinder_draw(y_axis_name_draw, self.axes_rotate)
        ################################################################################################################
        glRotate(90, 0, 0, 1)
        glRotate(-90, 1, 0, 0)
        glColor4f(0, 1, 0, 1.0)
        axis_cylinder_draw(x_axis_name_draw, self.axes_rotate)
        glRotate(90, 1, 0, 0)
        ################################################################################################################
        glRotate(-90, 0, 1, 0)
        glColor4f(1, 0, 0, 1.0)
        axis_cylinder_draw(z_axis_name_draw, self.axes_rotate)
        glRotate(90, 0, 1, 0)
        glRotate(-90, 0, 0, 1)
        ################################################################################################################
        glRotate(-self.axes_rotate[2], 0, 0, 1)
        glRotate(self.axes_rotate[0], 1, 0, 0)
        glTranslatef(*back_translate)
        glPopMatrix()

    def draw_density(self):
        coordinates = self.chgcar.coordinates_array
        glColor4f(*self.chgcar.color)
        if self.chgcar.draw_mode == 'Points':
            glEnable(GL_POINT_SMOOTH)
            glPointSize(2 / self.scale_parameter)
            for coord in coordinates:
                glBegin(GL_POINTS)
                glVertex3d(*coord)
                glEnd()
            glDisable(GL_POINT_SMOOTH)
            #glDisable(GL_MULTISAMPLE)
        elif self.chgcar.draw_mode == 'Isosurface':
            basis = self.__calculations[self.now_calc]['BASIS']
            self.draw_3d_texture('CHGCAR', basis)

    def display_resize(self, event):
        self.display = [int(event.w), int(event.h)]
        self.window_size = [int(event.w), int(event.h)]
        difference = [int(self.display[i] - self.default_display[i]) for i in range(2)]
        if difference[0] > difference[1]:
            self.display[1] = self.default_display[1] + int(difference[0] * 3 / 4)
        elif difference[0] < difference[1]:
            self.display[0] = self.default_display[0] + int(difference[1] * 4 / 3)
        self.display_scaling = self.display[0] / self.default_display[0]

        nlw = (event.w - self.display[0]) // 2
        nlh = (event.h - self.display[1]) // 2

        self.DisplayCenter = [event.w // 2, event.h // 2]
        self.new_coordinate_start = [nlw, nlh]
        glViewport(nlw, nlh, self.display[0], self.display[1])

    def processing_start(self):
        if self.__calculations[self.now_calc]['STEPS']:
            self.core_windows_hide()
            VRProcessing(self.selected_atoms, self.__calculations[self.now_calc], self.now_calc, self.del_cord_leave_cell, theme=self.theme).mainloop()
            self.core_windows_show()

    def oszicar_mode_start(self):
        self.window.hide()
        VROszicarMode(self.__core_value['-DIRECTORY-'], theme=self.theme).mainloop()
        self.window.un_hide()

    def poscar_form_mode_start(self):
        if self.now_calc:
            self.POSCAR_form_object = VRPoscarForm(self.__calculations[self.now_calc], theme=self.theme)

    def poscar_view_mode_start(self):
        calculation = VRPoscarView(self.__core_value['-DIRECTORY-'], theme=self.theme).return_calculation()
        if calculation:
            if len(calculation['COLORVALUE']) == len(calculation['POSITIONS'][0]):
                self.prev_calc = self.now_calc
                self.calculation_parsed, self.now_calc = True, '/'.join(calculation['DIRECTORY'].split('/')[-2:])
                self.__calculations[self.now_calc] = calculation
                self.window['-MDCALC-'].update(value=self.now_calc, values=list(self.__calculations.keys()))
                self.print(f'POSCAR type file: {self.now_calc} appended.')
                self.calculation_change()

    def console_start(self):
        self.core_windows_hide()
        VRConsole(theme=self.theme).mainloop()
        self.core_windows_show()

    def file_hosting_start(self):
        self.core_windows_hide()
        VRFileHosting(theme=self.theme).mainloop()
        self.core_windows_show()

    def core_windows_hide(self):
        self.window.hide()
        self.scree = pygame.display.set_mode(self.default_display, DOUBLEBUF | OPENGL | pygame.RESIZABLE | pygame.HIDDEN)

    def core_windows_show(self):
        self.scree = pygame.display.set_mode(self.default_display, DOUBLEBUF | OPENGL | pygame.RESIZABLE | pygame.SHOWN)
        self.window.un_hide()

    def theme_change(self):
        directory = self.__core_value['-DIRECTORY-']
        sg.user_settings_set_entry('-location-', self.window.current_location())
        self.window.close()
        if self.theme == 'VRGUI':
            self.theme = 'DARKGUI'
            self.window = VRGUI(GUI_type=core_GUI, title='VaspReader', resizable=True, keep_on_top=False, theme=self.theme, location=sg.user_settings_get_entry('-location-', (None, None)), enable_close_attempted_event=True).window_return()
        else:
            self.theme = 'VRGUI'
            self.window = VRGUI(GUI_type=core_GUI, title='VaspReader', resizable=True, keep_on_top=False, theme=self.theme, location=sg.user_settings_get_entry('-location-', (None, None)), enable_close_attempted_event=True).window_return()
        self.window['-DIRECTORY-'].update(directory)
        self.window['-MDCALC-'].update(value=self.now_calc, values=list(self.__calculations.keys()))
        self.window['selected_atoms'].update(visible=self.add_listbox_selection)
        self.window.set_min_size(self.window.size)
        self.window['-MENUBAR-'].update(menu_definition=self.now_menu)
        self.print('Theme has been changed to dark.' if self.theme != 'VRGUI' else 'Theme has been changed to white.')
        if self.now_calc:
            self.calculation_change()
        self.window.refresh()

    def listbox_selection_function(self):
        sg.user_settings_set_entry('-location-', self.window.current_location())
        self.window.close()
        self.window = VRGUI(GUI_type=core_GUI, title='VaspReader', resizable=True, keep_on_top=False, theme=self.theme, location=sg.user_settings_get_entry('-location-', (None, None)), enable_close_attempted_event=True).window_return()
        self.window['-DIRECTORY-'].update(self.__core_value['-DIRECTORY-'])
        self.window['-MDCALC-'].update(value=self.now_calc, values=list(self.__calculations.keys()))
        if self.now_calc:
            self.calculation_change()
        self.add_listbox_selection = not self.add_listbox_selection
        if self.add_listbox_selection:
            self.window['selected_atoms'].update(visible=self.add_listbox_selection)
            self.window.set_min_size(self.window.size)
        self.window['-MENUBAR-'].update(menu_definition=self.now_menu)
        self.window.refresh()

    def bond_window_open(self):
        self.bond_window_active = True
        self.bond_window = VRGUI(GUI_type=bonds_window, title='VaspReader', resizable=True, keep_on_top=False, theme=self.theme, enable_close_attempted_event=True).window_return()
        [self.bond_window[element].Widget.configure(validate='all', validatecommand=(self.bond_window.TKroot.register(partial(valid, limit=5)), '%P')) for element in ['-ALL-BONDS-LENGTH-', '-BONDS-LENGTH-']]
        [self.bond_window[element].Widget.configure(validate='all', validatecommand=(self.bond_window.TKroot.register(partial(valid, limit=0.5)), '%P')) for element in ['-ALL-BONDS-RADIUS-', '-BONDS-RADIUS-']]

        self.first_event_of_bond_window = True

    def possible_bonds(self):
        bonds_types = []
        [bonds_types.append(f'{i}-{j}') if f'{j}-{i}' not in bonds_types else None for i in sorted(set(self.__calculations[self.now_calc]['ATOMNAMES'])) for j in sorted(set(self.__calculations[self.now_calc]['ATOMNAMES']))]
        return bonds_types

    @ staticmethod
    def cross(a, b):
        return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]

    def bonds_drawing_function(self, bonds_array, vercities_array):
        for atom1, atom2 in bonds_array: # написать отрисовку связей для разных шагов
            unnormed_vec = [vercities_array[atom2][i] - vercities_array[atom1][i] for i in range(3)]
            axis = (1, 0, 0) if math.hypot(unnormed_vec[0], unnormed_vec[1]) < 0.001 else self.cross(unnormed_vec, (0, 0, 1))
            angle = -math.atan2(math.hypot(unnormed_vec[0], unnormed_vec[1]), unnormed_vec[2]) * 180 / math.pi

            glPushMatrix()
            glTranslatef(*vercities_array[atom1])
            glRotate(angle, *axis)
            glColor4f(*self.color[atom1], 1.0)
            gluCylinder(gluNewQuadric(), bonds_array[(atom1, atom2)][1], bonds_array[(atom1, atom2)][1], bonds_array[(atom1, atom2)][0] / 2, 16, 16)
            glTranslatef(0, 0, bonds_array[(atom1, atom2)][0] / 2)
            glColor4f(*self.color[atom2], 1.0)
            gluCylinder(gluNewQuadric(), bonds_array[(atom1, atom2)][1], bonds_array[(atom1, atom2)][1], bonds_array[(atom1, atom2)][0] / 2, 16, 16)
            glPopMatrix()

    @ staticmethod
    def add_bond_to_dictionary(array, allowed_bonds_dict, bonds_info_dict, index1, index2):
        if (index2, index1) not in allowed_bonds_dict:
            vec = [array[index2][i] - array[index1][i] for i in range(3)]
            distance = math.sqrt(sum(map(lambda x: math.pow(x, 2), vec)))
            if bonds_info_dict[0] >= distance > 0:
                allowed_bonds_dict[(index1, index2)] = (distance, bonds_info_dict[1])

    def bond_allowed_atoms_number(self, custom_vertices=None, custom_step=-1):
        if custom_vertices is None:
            custom_vertices = []
        else:
            self.trajectory_bonds[custom_step] = dict()
        self.__calculations[self.now_calc]['ALLOWED_BONDS'].clear()
        is_all_bonds = self.__calculations[self.now_calc]['BONDS_INFO'].get('ALL', None)
        if is_all_bonds is not None:
            for atom1 in self.__calculations[self.now_calc]['ATOM-NUMBERS']:
                for atom2 in self.__calculations[self.now_calc]['ATOM-NUMBERS']:
                    for index1 in self.__calculations[self.now_calc]['ATOM-NUMBERS'][atom1]:
                        for index2 in self.__calculations[self.now_calc]['ATOM-NUMBERS'][atom2]:
                            if not len(custom_vertices):
                                self.add_bond_to_dictionary(self.now_step_vertices, self.__calculations[self.now_calc]['ALLOWED_BONDS'], is_all_bonds, index1, index2)
                            else:
                                self.add_bond_to_dictionary(custom_vertices, self.trajectory_bonds[custom_step], is_all_bonds, index1, index2)
        else:
            for bond in self.__calculations[self.now_calc]['BONDS_INFO']:
                atoms_in_bond = bond.split('-')
                for atom1_index in self.__calculations[self.now_calc]['ATOM-NUMBERS'][atoms_in_bond[0]]:
                    for atom2_index in self.__calculations[self.now_calc]['ATOM-NUMBERS'][atoms_in_bond[1]]:
                        if not len(custom_vertices):
                            self.add_bond_to_dictionary(self.now_step_vertices, self.__calculations[self.now_calc]['ALLOWED_BONDS'], self.__calculations[self.now_calc]['BONDS_INFO'][bond], atom1_index, atom2_index)
                        else:
                            self.add_bond_to_dictionary(custom_vertices, self.trajectory_bonds[custom_step], self.__calculations[self.now_calc]['BONDS_INFO'][bond], atom1_index, atom2_index)

    def enable_draw_bonds_while_dict_is_not_empty(self):
        bonds = self.possible_bonds()
        self.bond_window['-BOND-NAME-CHOOSE-'].update(values=bonds) if self.now_calc else None
        if self.__calculations[self.now_calc]['BONDS_INFO'].get('ALL', None) is None:
            keys = list(self.__calculations[self.now_calc]['BONDS_INFO'])
            indexes = [num for num, bond in enumerate(bonds) if bond in keys]
            self.bond_window['-BOND-NAME-CHOOSE-'].update(set_to_index=indexes)
            self.bond_window['-BOND-NAME-'].update(values=list(self.__calculations[self.now_calc]['BONDS_INFO']) if self.__calculations[self.now_calc]['BONDS_INFO'].get('ALL', None) is None else [])
        self.__calculations[self.now_calc]['IS_DRAW_BONDS'] = True

    def bond_window_events(self):
        self.bond_event, self.bond_value = self.bond_window.read(timeout=1)
        if self.first_event_of_bond_window:
            if self.now_calc and self.__calculations[self.now_calc]['IS_DRAW_BONDS']:
                self.bond_window['-BONDS-DRAW-'].update(value=True)
                [self.bond_window[element].update(disabled=False) for element in ['-ALL-BONDS-RADIUS-', '-ALL-BONDS-LENGTH-', '-BONDS-RADIUS-', '-BONDS-LENGTH-']]
                all_bonds = self.__calculations[self.now_calc]['BONDS_INFO'].get('ALL', None)
                bond_types = self.possible_bonds()
                self.bond_window['-BOND-NAME-CHOOSE-'].update(values=bond_types)
                if all_bonds is not None:
                    self.bond_window['-ALL-BONDS-LENGTH-'].update(all_bonds[0])
                    self.bond_window['-ALL-BONDS-RADIUS-'].update(all_bonds[1])
                elif len(self.__calculations[self.now_calc]['BONDS_INFO']):
                    indexes = [num for num, bond in enumerate(bond_types) if bond in self.__calculations[self.now_calc]['BONDS_INFO']]
                    self.bond_window['-BOND-NAME-CHOOSE-'].update(set_to_index=indexes)
                    self.bond_window['-BOND-NAME-'].update(values=list(self.__calculations[self.now_calc]['BONDS_INFO']))
                if self.trajectory_draw_mode:
                    self.bond_window['-START-TRAJECTORY-'].update(self.trajectory_range_info[0])
                    self.bond_window['-STEP-TRAJECTORY-'].update(self.trajectory_range_info[2])
                    self.bond_window['-END-TRAJECTORY-'].update(self.trajectory_range_info[1])
            self.first_event_of_bond_window = False
        if self.bond_event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            self.bond_window.close()
            self.bond_window = None
            self.bond_window_active = False
        if self.bonds_window_refresh:
            self.bond_event = '-BONDS-DRAW-'
            self.bonds_window_refresh = False
        if self.bond_event == '-BONDS-DRAW-':
            [self.bond_window[element].update(disabled=False if self.bond_value['-BONDS-DRAW-'] else True) for element in ['-ALL-BONDS-RADIUS-', '-ALL-BONDS-LENGTH-', '-BONDS-RADIUS-', '-BONDS-LENGTH-']]
            if self.bond_value['-BONDS-DRAW-']:
                if self.__calculations[self.now_calc]['BONDS_INFO']:
                    self.enable_draw_bonds_while_dict_is_not_empty()
                else:
                    bonds = self.possible_bonds()
                    self.bond_window['-BOND-NAME-CHOOSE-'].update(values=bonds) if self.now_calc else None
            else:
                self.__calculations[self.now_calc]['IS_DRAW_BONDS'] = False
                self.bond_window['-BOND-NAME-CHOOSE-'].update(values=[])
                self.bond_window['-BOND-NAME-'].update(values=[])
        if self.now_calc:
            if self.bond_event == '-BOND-NAME-CHOOSE-':
                self.bond_window['-BOND-NAME-'].update(values=self.bond_value['-BOND-NAME-CHOOSE-'])
                for key in list(self.__calculations[self.now_calc]['BONDS_INFO']):
                    if key not in self.bond_value['-BOND-NAME-CHOOSE-']:
                        self.__calculations[self.now_calc]['BONDS_INFO'].pop(key)
                for bond in self.bond_value['-BOND-NAME-CHOOSE-']:
                    if bond not in self.__calculations[self.now_calc]['BONDS_INFO']:
                        self.__calculations[self.now_calc]['BONDS_INFO'][bond] = (float(self.bond_value['-BONDS-LENGTH-']), float(self.bond_value['-BONDS-RADIUS-']))
            if self.bond_value['-BOND-NAME-CHOOSE-'] and self.bond_value['-BOND-NAME-'] and (self.bond_event == '-BONDS-LENGTH-' or self.bond_event == '-BONDS-RADIUS-'):
                self.__calculations[self.now_calc]['BONDS_INFO'][self.bond_value['-BOND-NAME-']] = (float(self.bond_value['-BONDS-LENGTH-']), float(self.bond_value['-BONDS-RADIUS-']))
            if self.bond_event == '-BOND-NAME-':
                self.bond_window['-BONDS-LENGTH-'].update(self.__calculations[self.now_calc]['BONDS_INFO'][self.bond_value['-BOND-NAME-']][0])
                self.bond_window['-BONDS-RADIUS-'].update(self.__calculations[self.now_calc]['BONDS_INFO'][self.bond_value['-BOND-NAME-']][1])
            if self.bond_event == '-SUBMIT-ALL-':
                self.__calculations[self.now_calc]['BONDS_INFO'] = {'ALL': (float(self.bond_value['-ALL-BONDS-LENGTH-']), float(self.bond_value['-ALL-BONDS-RADIUS-']))}
                self.__calculations[self.now_calc]['IS_DRAW_BONDS'] = True
                if self.bond_value['-BOND-NAME-CHOOSE-']:
                    self.bond_window['-BOND-NAME-CHOOSE-'].update(set_to_index=[])
                    self.bond_window['-BOND-NAME-'].update(values=[])
                self.recalculate_bonds = True
            if self.bond_event == '-SUBMIT-BONDS-' and self.bond_value['-BOND-NAME-CHOOSE-']:
                self.__calculations[self.now_calc]['IS_DRAW_BONDS'] = True
                self.recalculate_bonds = True
            if self.bond_event in ['-START-TRAJECTORY-', '-STEP-TRAJECTORY-', '-END-TRAJECTORY-']:
                check_input_text_numerical_value(int, self.bond_window, self.bond_value, self.bond_event, self.__calculations[self.now_calc]['STEPS'])
            if self.bond_event == '-SUBMIT-TRAJECTORY-' and self.bond_value['-START-TRAJECTORY-'] and self.bond_value['-END-TRAJECTORY-'] and self.bond_value['-STEP-TRAJECTORY-']:
                self.trajectory_range_info = (int(self.bond_value['-START-TRAJECTORY-']), int(self.bond_value['-END-TRAJECTORY-']), int(self.bond_value['-STEP-TRAJECTORY-']))
                self.trajectory_steps = [i for i in range(int(self.bond_value['-START-TRAJECTORY-']), int(self.bond_value['-END-TRAJECTORY-']), int(self.bond_value['-STEP-TRAJECTORY-']))]
                self.trajectory_draw_mode = True
                self.trajectory_first_bonds_calculate = True
            if self.bond_event == '-CLEAR-TRAJECTORY-':
                self.trajectory_draw_mode, self.trajectory_steps, self.trajectory_bonds, self.trajectory_first_bonds_calculate = False, [], dict(), False
                self.trajectory_range_info = ()
                if self.__calculations[self.now_calc]['IS_DRAW_BONDS']:
                    self.recalculate_bonds = True

    def orthographic_view(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-12, 12, -9, 9, 0.1, 50.0)
        gluLookAt(0, 20, 0, 0, 0, 0, 0, 0, 1)
        glMatrixMode(GL_MODELVIEW)
        self.perspective = False

    def perspective_view(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)
        gluLookAt(0, 20, 0, 0, 0, 0, 0, 0, 1)
        glMatrixMode(GL_MODELVIEW)
        self.perspective = True

    def do_screenshot(self):
        try:
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
        except:
            pass
        hwnd = win32gui.FindWindow(None, 'VR')
        win32gui.SetForegroundWindow(hwnd)
        bbox = win32gui.GetWindowRect(hwnd)
        screenshot = ImageGrab.grab(bbox, include_layered_windows=True)
        screenshot_dir = sg.PopupGetFile('Save screenshot', save_as=True, no_window=True, file_types=(("Png", "*.png"), ("Bmp", "*.bmp"), ("Jpg", "*.jpg"), ("Tiff", "*.tiff"), ("Tif", "*.tif")))
        if screenshot_dir:
            screenshot.save(screenshot_dir, dpi=self.display)

    def draw_trajectory_mode(self):
        for step in self.trajectory_steps:
            array = self.vertices[step]
            if self.__calculations[self.now_calc]['IS_DRAW_BONDS'] and self.trajectory_first_bonds_calculate:
                self.bond_allowed_atoms_number(array, step)
            if self.__calculations[self.now_calc]['IS_DRAW_BONDS']:
                self.bonds_drawing_function(self.trajectory_bonds[step], array)
            for k in range(len(array)):
                glPushMatrix()
                glTranslatef(*array[k])
                glColor4f(*self.color[k], 1.0)
                gluSphere(gluNewQuadric(), self.radii[k], 24, 24)
                glPopMatrix()
        self.trajectory_first_bonds_calculate = False

    def interactive_mods_event(self, mode, other_mode1, other_mode2):
        mode = not mode
        self.bond_and_valence_counter = 0
        for atom in self.bond_and_valence_atoms:
            self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][atom]] = self.radii[self.__calculations[self.now_calc]['ID-TO-NUM'][atom]] / 1.25
        self.bond_and_valence_atoms.clear()
        if mode:
            other_mode1 = False
            other_mode2 = False
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND) if mode else pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.only_keyboard_select = False if mode else True
        return mode, other_mode1, other_mode2

    def mainloop(self):
        target_fps = 60
        prev_time = time.time()
        self.load_texture(tex_type='background')
        [self.load_texture(string=str(i), tex_type='numbers', texture_name=str(i)) for i in range(10)]
        self.load_texture(string='.', tex_type='numbers', texture_name='.')
        try:
            rotation_prev, run = [0, 0], True
            first_color = tuple(random.randrange(20, 50, 1) / 100 for i in range(3))
            second_color = tuple(random.randrange(50, 80, 1) / 100 for i in range(3))
            logo_rotate = 0
            while run:
                self.__core_event, self.__core_value = self.window.read(timeout=1)
                if self.bond_window_active:
                    self.bond_window_events()
                if self.chgcar:
                    self.chgcar.mainloop()
                    if self.chgcar.load_model:
                        self.load_3d_texture('CHGCAR', *self.chgcar.array_shape, self.chgcar.points_to_draw)
                        self.chgcar.load_model = False
                # FPS_CONTROL_TIMEDELAY = pygame.time.get_ticks()
                if self.__core_event:
                    self.window.refresh()
                self.menu_change()
                if self.__core_event == '-THEMECHANGE-':
                    self.theme_change()
                    continue
                self.rotate = np.array([[-math.cos(math.radians(rotation_prev[0])), math.cos(math.radians(rotation_prev[1])) * math.sin(math.radians(rotation_prev[0])), -math.sin(math.radians(rotation_prev[1])) * math.sin(math.radians(rotation_prev[0])), 0],
                                        [0.0, math.sin(math.radians(rotation_prev[1])), math.cos(math.radians(rotation_prev[1])), 0],
                                        [-math.sin(math.radians(rotation_prev[0])), -math.cos(math.radians(rotation_prev[1])) * math.cos(math.radians(rotation_prev[0])), math.cos(math.radians(rotation_prev[0])) * math.sin(math.radians(rotation_prev[1])), 0],
                                        [self.x_displ, self.y_displ, self.z_displ, self.scale_parameter]], dtype='f')

                self.axes_rotate = [rotation_prev[1], 0, -rotation_prev[0]]
                glLoadIdentity()
                glMultMatrixf(self.rotate)

                if self.Back_Step:
                    if self.step != 0 and self.step >= self.speed:
                        self.step -= self.speed
                        self.window['slider'].update(value=self.step)
                if self.Forward_Step:
                    if self.step != self.vertices.shape[0] - 1 and self.step <= self.vertices.shape[0] - 1 - self.speed:
                        self.step += self.speed
                        self.window['slider'].update(value=self.step)

                if self.calculation_parsed or self.step != self.prev_step or not self.calculation_changed:
                    self.now_step_vertices = self.vertices[self.step]

                if self.generate_event:
                    self.__core_event = self.generate_event
                    self.generate_event = ''

                if self.__core_event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or self.__core_event == '-EXIT-' or self.__core_event == 'Exit':
                    if self.bond_window is not None:
                        self.bond_window.close()
                    sg.user_settings_set_entry('-location-', self.window.current_location())
                    sg.user_settings_set_entry('-theme-', self.theme)
                    self.print_window.close()
                    break
                if self.__core_event == 'Send to tray':
                    if self.bond_window is not None:
                        self.bond_window.close()
                    sg.user_settings_set_entry('-location-', self.window.current_location())
                    sg.user_settings_set_entry('-theme-', self.theme)
                    global stay_in_tray
                    stay_in_tray = True
                    self.print_window.close()
                    break
                if self.__core_event == '-CALCSTART-':
                    self.step = 0
                    self.window['slider'].update(value=self.step)
                    self.Back_Step, self.Forward_Step = False, False
                if self.__core_event == '-CALCTOSTART-':
                    self.Back_Step, self.Forward_Step = True, False
                if self.__core_event == '-CALCEND-' and self.speed:
                    self.step = self.vertices.shape[0] - 1
                    self.window['slider'].update(value=self.step)
                    self.Back_Step, self.Forward_Step = False, False
                if self.__core_event == '-CALCTOEND-' and self.speed:
                    self.Back_Step, self.Forward_Step = False, True
                if self.__core_event == 'slider':
                    self.step = int(self.__core_value['slider'])
                    self.Back_Step, self.Forward_Step = False, False
                if self.__core_event == 'slider_speed' and self.speed:
                    self.speed = math.ceil((self.vertices.shape[0] - 1) / 100 / 10 * int(self.__core_value['slider_speed']) / 100)

                if self.__core_event == 'Open Calculation     Ctrl-O':
                    directory = sg.PopupGetFolder(message='Choose folder', no_window=True, no_titlebar=True, icon=self.icon_image)
                    self.window['-DIRECTORY-'].update(directory)
                    self.generate_event = '-MD-'
                    continue
                if self.__core_event == 'About the program':
                    self.about_the_program()
                if self.__core_event == 'Changes history':
                    self.updates_history()
                if self.__core_event == 'Save Calc State       Ctrl-S': # folder_name = tk.filedialog.askdirectory(initialdir=initial_folder)
                    self.save_calculation_state()
                if self.__core_event == 'Load Calc State       Ctrl-L':
                    self.load_calculation_state()
                    self.calculation_parsed = True
                if self.__core_event == '-STATESAVED-':
                    self.print(f'Calculations: {list(self.__calculations.keys())} saved.')
                if self.__core_event == 'Latest update':
                    self.latest_update()
                if self.__core_event == 'Window description':
                    self.visual_window_description()
                if self.__core_event == 'Screenshot':
                    self.do_screenshot()
                if self.__core_event == 'Perspective' or self.__core_event == '✅Orthographic':
                    self.perspective_view()
                if self.__core_event == 'Orthographic' or self.__core_event == '✅Perspective':
                    self.orthographic_view()
                if self.__core_event == 'Select from listbox' or self.__core_event == '✅Select from listbox':
                    self.listbox_selection_function()
                if self.change_model_view:
                    self.perspective_view() if self.perspective else self.orthographic_view()
                    self.change_model_view = False
                if self.__core_event in [f'Light{str(i)}' for i in range(1, 9)] or self.__core_event in [f'✅Light{str(i)}' for i in range(1, 9)]:
                    light_num = int(self.__core_event[-1]) - 1
                    self.window_light(light_num, self.light_positions[light_num])
                if self.__core_event == 'Background Color':
                    self.window['-BUTCOL-'].click()
                if self.__core_event == '-BACCOL-':
                    color_chose = self.__core_value['-BACCOL-']
                    if color_chose != 'None':
                        color_chose = color_chose.lstrip('#')
                        self.background_color = tuple(int(color_chose[i:i + 2], 16) / 256 for i in (0, 2, 4))
                        self.fog_color = self.background_color
                if self.__core_event == 'View axes' or self.__core_event == '✅View axes':
                    self.view_axes = not self.view_axes
                if self.__core_event == 'View cell boarder' or self.__core_event == '✅View cell boarder':
                    self.draw_cell = not self.draw_cell
                if self.__core_event == 'Del coords after leave a cell' or self.__core_event == '✅Del coords after leave a cell':
                    self.del_cord_leave_cell = not self.del_cord_leave_cell
                if self.__core_event == 'Calculate bonds':
                    self.bond_window_open()

                if self.__core_event == 'selected_atoms' and self.now_calc:
                    for atom in self.__core_value['selected_atoms']:
                        index = int(atom.split('_')[-1]) - 1
                        if not self.selected_atoms[index]:
                            self.selected_atoms[index] = True
                            self.radii[index] = self.radii[index] * 1.25
                            self.color[index] = [self.color[index][k] / 2 for k in range(3)]
                            self.print(f'You chose: {self.__calculations[self.now_calc]["ID"][index]}.')
                    for atom in self.__calculations[self.now_calc]['ID']:
                        index = int(atom.split('_')[-1]) - 1
                        if self.selected_atoms[index]:
                            if atom not in self.__core_value['selected_atoms']:
                                self.selected_atoms[index] = False
                                self.radii[index] = self.radii[index] * 0.8
                                self.color[index] = [self.color[index][k] * 2 for k in range(3)]
                                self.print(f'{self.__calculations[self.now_calc]["ID"][index]} deselected.')

                if self.__core_event == '-MD-':
                    self.directory = self.__core_value['-DIRECTORY-']
                    if not self.file_not_found_message('MD', self.directory):
                        self.window.perform_long_operation(lambda: VRMD(self.directory), end_key='-PARSED-')
                        self.window['-DIRECTORY-'].update(disabled=True)
                        self.window['Browse'].update(disabled=True)
                        self.window['-MD-'].update(disabled=True)
                if self.__core_event == '-PARSED-':
                    MD_object = self.__core_value['-PARSED-']
                    self.window['-DIRECTORY-'].update(disabled=False)
                    self.window['Browse'].update(disabled=False)
                    self.window['-MD-'].update(disabled=False)
                    if MD_object.breaker:
                        if MD_object.different_calculations:
                            self.print('Files presents different calculations. Check files and try again.',
                                       text_color='Black', background_color='red')
                        if MD_object.no_vaspruns:
                            self.print('No vasprun files in directory.', text_color='Black', background_color='red')
                    else:
                        self.prev_calc = self.now_calc
                        self.calculation_parsed, self.now_calc = True, self.directory.split('/')[-1]
                        self.__calculations[self.now_calc] = MD_object.parser_parameters
                        self.window['-MDCALC-'].update(value=self.now_calc, values=list(self.__calculations.keys()))
                        self.print(f'{self.now_calc} consists of {self.__calculations[self.now_calc]["STEPS"]} steps.')
                        self.calculation_change()
                if self.__core_event == '-MDCALC-':
                    self.prev_calc = self.now_calc
                    self.now_calc = self.__core_value['-MDCALC-']
                    if self.now_calc:
                        self.calculation_change()
                if self.__core_event == '-MDDEL-':
                    if self.now_calc:
                        self.__calculations.pop(self.now_calc)
                        self.print(f'Calculation - {self.now_calc} removed.')
                        if self.__calculations:
                            keys = list(self.__calculations.keys())
                            self.now_calc = keys[-1]
                            self.window['-MDCALC-'].update(value=self.now_calc, values=keys)
                            self.calculation_change()
                        else:
                            self.now_calc, self.calculation_parsed, self.draw, self.step, self.speed = '', False, False, 0, None
                            self.scale_parameter = 1
                            self.prev_draw_bond_step = -1
                            rotation_prev = [0, 0]
                            self.window['-MDCALC-'].update(values=[])
                            self.window['slider'].update(range=(0, 0))
                            self.window['selected_atoms'].update(values=[])
                            self.Back_Step, self.Forward_Step = False, False

                if self.__core_event == 'Keyboard' or self.__core_event == '✅Mouse+Keyboard':
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    self.only_keyboard_select = True
                if self.__core_event == 'Mouse+Keyboard' or self.__core_event == '✅Keyboard':
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                    self.only_keyboard_select = False
                if self.change_select_mode:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW) if self.only_keyboard_select else pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                    self.change_select_mode = False

                if self.__core_event == 'Save Program Configuration':
                    self.save_program_configuration()
                if self.__core_event == 'Load Program Configuration':
                    self.load_program_configuration()

                if self.__core_event == 'Processing' and self.now_calc:
                    self.processing_start()
                if self.__core_event == 'OSZICAR':
                    self.oszicar_mode_start()
                if self.__core_event == 'POSCAR':
                    self.poscar_view_mode_start()
                if self.__core_event == 'CHGCAR':
                    if self.now_calc:
                        self.chgcar = VRChgcar(directory=self.__calculations[self.now_calc]['DIRECTORY'], folder=self.now_calc, atoms_number=self.__calculations[self.now_calc]['ATOMNUMBER'], basis=self.__calculations[self.now_calc]['BASIS'], hide=True)
                if self.__core_event == 'Form POSCAR':
                    self.poscar_form_mode_start()
                if self.POSCAR_form_object is not None and not self.CLOSE_POSCAR_IF_OPEN and not self.POSCAR_form_object.is_closed():
                    self.POSCAR_form_object.mainloop()
                    self.POSCAR_form_object_to_none = True
                elif self.POSCAR_form_object_to_none or self.CLOSE_POSCAR_IF_OPEN:
                    self.POSCAR_form_object.close() if self.POSCAR_form_object is not None else None
                    self.POSCAR_form_object_to_none = False
                    self.POSCAR_form_object, self.CLOSE_POSCAR_IF_OPEN = None, False
                if self.__core_event == 'Console':
                    self.console_start()
                if self.__core_event == 'File hosting':
                    self.file_hosting_start()
                if self.__core_event == 'ID' or self.__core_event == '✅ID':
                    self.set_ID_mode, self.set_bond_mode, self.set_valence_mode = self.interactive_mods_event(self.set_ID_mode, self.set_bond_mode, self.set_valence_mode)
                if self.__core_event == 'Bond length' or self.__core_event == '✅Bond length':
                    self.set_bond_mode, self.set_ID_mode, self.set_valence_mode = self.interactive_mods_event(self.set_bond_mode, self.set_ID_mode, self.set_valence_mode)
                if self.__core_event == 'Valence angle' or self.__core_event == '✅Valence angle':
                    self.set_valence_mode, self.set_ID_mode, self.set_bond_mode = self.interactive_mods_event(self.set_valence_mode, self.set_ID_mode, self.set_bond_mode)

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
                        if self.mouse_pressed and self.calculation_parsed:
                            self.Back_Step, self.Forward_Step = False, False
                            if self.only_keyboard_select:
                                pygame.mouse.set_visible(False)
                            rotation_prev[0] -= (event.rel[0]) * 0.4
                            rotation_prev[1] += (event.rel[1]) * 0.4
                    if event.type == pygame.MOUSEBUTTONUP:
                        if self.only_keyboard_select:
                            pygame.mouse.set_visible(True)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4 and self.calculation_parsed:
                        self.Back_Step, self.Forward_Step = False, False
                        self.scale_parameter = self.scale_parameter * 0.92
                        pygame.time.wait(10)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5 and self.calculation_parsed:
                        self.Back_Step, self.Forward_Step = False, False
                        self.scale_parameter = self.scale_parameter * 1.08
                        pygame.time.wait(10)
                    if event.type == pygame.MOUSEBUTTONDOWN and not self.trajectory_draw_mode and self.calculation_parsed:
                        if event.button == 1:
                            if not self.only_keyboard_select:
                                self.select_atom(True)
                        if event.button == 3:
                            if not self.only_keyboard_select:
                                self.select_atom(False)

                    if event.type == pygame.VIDEORESIZE:
                        self.display_resize(event)
                keypress = pygame.key.get_pressed()
                if self.calculation_parsed:
                    # Отдаление модели при нажатии клавиши - на кейпаде
                    if keypress[pygame.K_KP_MINUS] or keypress[pygame.K_MINUS]:
                        self.Back_Step, self.Forward_Step = False, False
                        self.scale_parameter = self.scale_parameter * 1.03
                        pygame.time.wait(10)
                    # Приближение модели при нажатии кнопки + на кейпаде
                    if keypress[pygame.K_KP_PLUS] or keypress[pygame.K_EQUALS]:
                        self.Back_Step, self.Forward_Step = False, False
                        self.scale_parameter = self.scale_parameter * 0.97
                        pygame.time.wait(10)
                    ##################################
                    if keypress[pygame.K_BACKSPACE]:
                        self.Back_Step, self.Forward_Step = False, False
                        rotation_prev = [0, 0]
                        self.x_displ, self.y_displ, self.z_displ = 0, 0, 0

                    if keypress[pygame.K_LEFT]:
                        self.Back_Step, self.Forward_Step = False, False
                        rotation_prev[0] -= 1.5
                    if keypress[pygame.K_RIGHT]:
                        self.Back_Step, self.Forward_Step = False, False
                        rotation_prev[0] += 1.5
                    if keypress[pygame.K_UP]:
                        self.Back_Step, self.Forward_Step = False, False
                        rotation_prev[1] += 1.5
                    if keypress[pygame.K_DOWN]:
                        self.Back_Step, self.Forward_Step = False, False
                        rotation_prev[1] -= 1.5
                    if keypress[pygame.K_z]:
                        self.x_displ = self.x_displ - 0.1
                    if keypress[pygame.K_x]:
                        self.x_displ = self.x_displ + 0.1
                    if keypress[pygame.K_j]:
                        self.z_displ = self.z_displ + 0.1
                    if keypress[pygame.K_u]:
                        self.z_displ = self.z_displ - 0.1

                    if keypress[pygame.K_a] and not self.trajectory_draw_mode:
                        self.select_atom(True)
                    if keypress[pygame.K_d] and not self.trajectory_draw_mode:
                        self.select_atom(False)
                    if keypress[pygame.K_p] and not self.trajectory_draw_mode:
                        self.processing_start()
                    if keypress[pygame.K_f] and self.calculation_parsed:
                        self.fog_exist = not self.fog_exist
                        if self.fog_exist:
                            glEnable(GL_FOG)
                            glFogi(GL_FOG_MODE, GL_EXP)
                            glFogfv(GL_FOG_COLOR, self.fog_color)
                            glFogf(GL_FOG_DENSITY, 0.35)
                            glFogf(GL_FOG_START, -20.0)
                            glFogf(GL_FOG_END, 20.0)
                        else:
                            glDisable(GL_FOG)
                        pygame.time.wait(200)
                # Движение модели мышкой
                for _ in pygame.mouse.get_pressed():
                    if pygame.mouse.get_pressed()[0] == 1:
                        self.mouse_pressed = True
                    elif pygame.mouse.get_pressed()[0] == 0:
                        self.mouse_pressed = False

                if not self.calculation_changed:
                    self.calculation_changed = True
                    continue
                elif self.calculation_changed:
                    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                    glClearColor(*self.background_color, 0.0)
                    # Отрисовка границ ячейки
                    if self.draw_cell and self.calculation_parsed:
                        self.cell_draw(self.cell, self.draw_cell, self.view_axes)
                    if not self.trajectory_draw_mode and self.calculation_parsed:
                        if (self.__calculations[self.now_calc]['IS_DRAW_BONDS'] and self.prev_draw_bond_step != self.step) or self.recalculate_bonds:
                            self.bond_allowed_atoms_number()
                            self.prev_draw_bond_step = self.step
                            self.recalculate_bonds = False
                        if self.__calculations[self.now_calc]['IS_DRAW_BONDS']:
                            self.bonds_drawing_function(self.__calculations[self.now_calc]['ALLOWED_BONDS'], self.now_step_vertices)
                        for k in range(len(self.now_step_vertices)):
                            glPushMatrix()
                            glTranslatef(*self.now_step_vertices[k])
                            glColor4f(*self.color[k], 1.0)
                            gluSphere(gluNewQuadric(), self.radii[k], 24, 24)
                            glPopMatrix()
                        if self.text_textures:
                            for key in self.text_textures:
                                self.draw_texture(position=self.now_step_vertices[self.__calculations[self.now_calc]['ID-TO-NUM'][key]], key=key)
                        if self.bonds_or_valence_dict:
                            self.draw_bond_or_valence_angle()
                        if self.chgcar.draw_model:
                            self.draw_density()
                    elif self.trajectory_draw_mode and self.calculation_parsed:
                        self.draw_trajectory_mode()
                    if self.view_axes and self.calculation_parsed:
                        glMultMatrixf(np.linalg.inv(self.rotate))
                        self.axes_draw()
                    if not self.calculation_parsed:
                        glMultMatrixf(np.transpose(self.rotate))
                        # self.axes_draw()
                        self.draw_start_texture()
                        x, y, z = self.find_window_dimensions(-5)
                        logo_rotate = VR_logo_draw(x, y, z, first_color, second_color, logo_rotate, self.display_scaling)
                pygame.display.flip()
                # pygame.time.wait(40 - (pygame.time.get_ticks() - FPS_CONTROL_TIMEDELAY))  # настройка FPS и скорости графики
                curr_time = time.time()  # so now we have time after processing
                diff = curr_time - prev_time  # frame took this much time to process and render
                delay = max(1.0 / target_fps - diff, 0)  # if we finished early, wait the remaining time to desired fps, else wait 0 ms!
                time.sleep(delay)
                fps = 1.0 / (delay + diff)  # fps is based on total time ("processing" diff time + "wasted" delay time)
                prev_time = curr_time
            self.window.close()
            pygame.quit()
        except Exception as e:
            traceback_win = VRGUI(GUI_type=traceback_window, title='VaspReader').window_return()
            traceback_win['ERROR'].update(f'Error:\nMistake: {traceback.format_exc()}\nPlease report about the mistake by email: solovykh.aa19@physics.msu.ru.')
            while True:
                traceback_event, traceback_value = traceback_win.read()
                if traceback_event == sg.WINDOW_CLOSED or traceback_event == 'SUBMIT':
                    traceback_win.close()
                    break
            sys.exit('Program closed because of mistakes in work.')


if __name__ == '__main__':
    stay_in_tray = False
    main()
    exiting_image = r'VR_icons/Exiting_ico.png'
    try:
        exiting_window(image=exiting_image)
    except:
        sg.popup_quick_message('VaspReader is closing! Bye-Bye!', font='_ 18', keep_on_top=True, text_color='white', background_color='Black', non_blocking=False)
