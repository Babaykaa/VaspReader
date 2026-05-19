import numpy as np
import os
import random
import time
import logging
from PIL import Image, ImageQt
import OpenGL
from OpenGL.GL import *
from PySide6.QtCore import QThread, QTimer, Qt
from PySide6.QtGui import QOpenGLContext, QSurfaceFormat, QImage, QKeyEvent
from prochem.adapters.qt.generated.visual import Ui_Visual, QMainWindow
from prochem.adapters.qt.api import (
    QtCalculationEntry,
    calculation_entry,
    scene_from_calculation,
)
from prochem.adapters.qt.windowing import move_to_saved_or_default
OpenGL.ERROR_CHECKING = False
logger = logging.getLogger(__name__)


class VisualWindow(Ui_Visual, QMainWindow):
    """Class for visualisation VASP and not only VASP calculation results. Have many features connected with bonds,
    cell and axes drawing and others options.""" 
    __calculation = dict()

    def __init__(self, settings=None, control_window=None, print_window=None):
        """Initialization function of Visual"""
        super(VisualWindow, self).__init__()
        self.__settings = settings
        
        self.__control_window = control_window
        self.__print_window = print_window
        self.closed = False
        self.__project_directory = self.__print_window.get_project_dir()
        self.__calculations = None
        self.__active_entry = None

        self.setupUi(self, self.__settings, self.__project_directory)
        logger.info(f"VisualUI setuped")

        move_to_saved_or_default(self, self.__settings, 'visual', default_offset=(40, 380))
        logger.info(f"Visual window positioned")
        #self.rotation_matrix = np.array([[-1.0, 0.0, 0.0, 0.0],
        #                                 [0.0, 0.0, 1.0, 0],
        #                                 [0.0, -1.0, 0.0, 0.0],
        #                                 [0.0, 0.0, 0.0, 1.0]])
        
        self.back_step, self.forward_step = False, False
        self._step = 0

    def closeEvent(self, event):
        """
        Saves the window's position and closes the application.
        
         This method is called when the window is closed. It saves the current
         window position to settings, marks the window as closed, closes the
         print window if it's open, and accepts the close event.
        
         Parameters:
          self: The instance of the class.
          event: The close event.
        
         Returns:
          None
         
        
         Class Fields Initialized:
          self.closed: A boolean indicating whether the window is closed.
        """
        self.__settings.set_new_window_location(self.pos().toTuple(), 'visual')
        self.closed = True
        if not self.__print_window.get_control_window().closed:
            self.__print_window.get_control_window().close()
        event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        """
        Handles key press events.
        
        This method intercepts key presses and performs actions based on the pressed key.
        Currently, it only handles the 'P' key, printing "Processing..." to the console.
        
        Args:
         self: The instance of the class.
         event: The key event object.
        
        Returns:
         None
        """
        key = event.key()
        match key:
            case Qt.Key_P:
                print('Processing...')

    def load_calculation_info(self, calculation):
        """
        Loads calculation information.
        
        Args:
         calculation: The calculation information to load.
        
        Initializes:
         self.__calculation: Stores the provided calculation information.
        
        Returns:
         None.
        """
        self.__calculation = calculation
        entry = self._resolve_entry(calculation)
        self.__active_entry = entry
        if entry is None:
            return
        self._render_entry_frame(0)

    def set_frame_index(self, frame_index):
        """Updates the rendered structures/dataset frame."""
        self._step = int(frame_index)
        self._render_entry_frame(self._step)

    def without_calculation(self):
        """Clears loaded calculation data from the visual widget."""
        self.__calculation = None
        self.__active_entry = None
        if hasattr(self, "openGLWidget"):
            self.openGLWidget.clear_scene_data()

    def _render_entry_frame(self, frame_index):
        if self.__active_entry is None or not hasattr(self, "openGLWidget"):
            return
        try:
            scene = scene_from_calculation(
                self.__active_entry.calculation,
                options=self.__active_entry.scene_options,
                frame_index=int(frame_index),
            )
        except ValueError:
            self.without_calculation()
            return
        self.__active_entry.scene = scene
        self.openGLWidget.set_scene_data(scene, frame_index=0)

    @staticmethod
    def _resolve_entry(value):
        if value is None:
            return None
        if isinstance(value, QtCalculationEntry):
            return value
        if isinstance(value, dict):
            if "calculation" in value:
                return calculation_entry(value["calculation"], visible=value.get("visible", True))
            calculations = value.get("calculations")
            if calculations:
                scene_options = value.get("scene_options")
                entry = calculation_entry(
                    calculations[0],
                    visible=value.get("visible", True),
                    scene_options=scene_options,
                )
                if value.get("scene") is not None:
                    entry.scene = value["scene"]
                return entry
            return None
        return calculation_entry(value)

    # def change_light(self, light_indx):
    #     self.__settings.set_scene_params(not self.__settings.get_scene_params('light', 'states', light_indx), 'states', light_indx)
    #     if self.__settings.get_scene_params('light', 'states', light_indx):
    #         glEnable(self.__settings.get_scene_params('light', 'variables', light_indx))
    #         glLight(self.__settings.get_scene_params('light', 'variables', light_indx), GL_POSITION, 
    #                 (*self.__settings.get_scene_params('light', 'default', light_indx), 1))
    #         glLightfv(self.__settings.get_scene_params('light', 'variables', light_indx), GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
    #         glLightfv(self.__settings.get_scene_params('light', 'variables', light_indx), GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    #         glLightfv(self.__settings.get_scene_params('light', 'variables', light_indx), GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    #     else:
    #         glDisable(self.__settings.get_scene_params('light', 'variables', light_indx))

    # def change_light_position(self, light_indx, new_position):
    #     self.__settings.set_scene_params(new_position, 'light', 'positions', light_indx)

    # def load_calculation_info(self, calculation):
    #     self.__calculation = calculation
    #     self.__is_calculation_loaded = True

    # def complete_load_of_calculation(self):
    #     self.__primitives.clear()
    #     self._VBOBuffers.clear()
    #     self._buffers_labels.clear()
    #     self.__cell_position[1] = self.__calculation['BASIS_VERT'].max()
    #     radii = [1.0 , 1.15]
    #     for _, atom in enumerate(self.__calculation['ATOMSINFO']):
    #         for indx, selection_type in enumerate(['', '_Sel']):
    #             self.__primitives[atom + selection_type] = Primitives(1, self.__calculation['ATOMSINFO'][atom]['COLORVALUE']).Sphere(self.__calculation['ATOMSINFO'][atom]['RADII'] * radii[indx], 32, 32)
    #             self._VBOBuffers.append(VRVBO(self.__primitives[atom + selection_type][:-1], self.__primitives[atom + selection_type][-1]).createVaoBuffer())
    #             self._buffers_labels.append(key)
    #     self.__is_calculation_loaded = False

    # def set_default_rotation_matrix(self):
    #     self.rotation_matrix = np.array([[-1.0, 0.0, 0.0, 0.0],
    #                                      [0.0, 0.0, 1.0, 0],
    #                                      [0.0, -1.0, 0.0, 0.0],
    #                                      [self._x_d, self._y_d, self._z_d, self._scale_parameter]], dtype=np.float64)

    # def select_atom(self, select):
    #     self.back_step, self.forward_step = False, False
    #     mouseClick = pygame.mouse.get_pos()
    #     mouseClick = [mouseClick[i] - self.newCoordinateStart[i] for i in range(2)]
    #     if self.isPerspective:
    #         prjMat = (GLfloat * 16)()
    #         glGetFloatv(GL_PROJECTION_MATRIX, prjMat)
    #         prjMat = np.dot(self.rotationMatrix, np.array(prjMat).reshape((4, 4))).reshape((16, 1))
    #         onRect = perspectiveChoose(prjMat, mouseClick, self.__calculation['POSITIONS'][self._step], self.__display, self.__calculation['RADII'])
    #     else:
    #         coordinates = (np.dot(self.__calculation['POSITIONS'][self._step], self.rotationMatrix[:3, :3]) + np.array([[*self.rotationMatrix[3, :3]] for _ in range(self.__calculation['POSITIONS'][self._step].shape[0])])) / self.rotationMatrix[-1, -1]
    #         onRect = orthographicChoose(mouseClick, coordinates, self.__display, self.__calculation['RADII'])
    #     alreadySelected = False
    #     if select:
    #         for num, selected in enumerate(onRect):
    #             if selected and self.__calculation['ATOMNAMES'][num].split('_')[-1] != 'Sel' and not (self._setIDMode or self._setBondMode or self._setValenceMode):
    #                 self.__calculation['ATOMNAMES'][num] += '_Sel'
    #             elif selected and self.__calculation['ATOMNAMES'][num].split('_')[-1] == 'Sel':
    #                 alreadySelected = True
    #     else:
    #         for num, selected in enumerate(onRect):
    #             if selected and self.__calculation['ATOMNAMES'][num].split('_')[-1] == 'Sel' and not (self._setIDMode or self._setBondMode or self._setValenceMode):
    #                 self.__calculation['ATOMNAMES'][num] = self.__calculation['ATOMNAMES'][num][:-4]
    #             elif selected and self.__calculation['ATOMNAMES'][num].split('_')[-1] != 'Sel':
    #                 alreadySelected = True
    #     if alreadySelected:
    #         self.addMessage('This atom was already chose.' if select else 'This atom was already deleted.', self.__class__.__name__)
    #     pygame.time.wait(200)
 
    # def calculate_bonds(self):  # необходимо отсортировать массив по x, y, z и смотреть начиная с какого то элемента массива расстояние. Если оно больше заданного, то не включаем в рассмотрение, если меньше, то включаем и при этом соответствующим образом сдвигаем далее индекс поиска
    #     one_step_positions = self.__calculation['POSITIONS'][self._step]
    #     biggest_dim = self.nonoptimal_dimension_search(self.__calculation['POSITIONS'], 9)
    #     if self._all_bonds_calculate:
    #         one_step_positions_tr = one_step_positions.transpose()
    #         indexes_big = one_step_positions_tr[biggest_dim].argsort()
    #         neighbours = self.neighbours_search(self.neighbours_search_body, one_step_positions, indexes_big, biggest_dim, self._bond_length)
    #     else:
    #         type1, type2 = 'Mo', 'S'
    #         indexes1, indexes2 = self.__calculation['ATOM-NUMBERS'][type1], self.__calculation['ATOM-NUMBERS'][type2]
    #         one_step_positions_type2 = one_step_positions[indexes2]
    #         one_step_positions_tr = one_step_positions_type2.transpose()
    #         indexes_big = one_step_positions_tr[biggest_dim].argsort() + min(indexes2)
    #         neighbours = self.neighbours_search_between_types(self.neighbours_search_between_types_body, one_step_positions, indexes1, indexes_big, biggest_dim, self._bond_length)

    # def prepare_bond_buffers(self):
    #     atoms = self.__calculation['ATOMNAMES']
    #     if self._bond_radius is None and self._bond_length is None:
    #         for atom in set(atoms):
    #             self.__primitives[f'{atom}_Bond'] = Primitives(1.0, self.__calculation['ATOMSINFO'][atom]['COLORVALUE']).Tube(self._default_bond_radius, self._default_bond_length / 2, 32)
    #     else:
    #         for atom in set(atoms):
    #             self.__primitives[f'{atom}_Bond'] = Primitives(1.0, self.__calculation['ATOMSINFO'][atom]['COLORVALUE']).Tube(self._bond_radius[f'{atom}_Bond'], self._bond_length[f'{atom}_Bond'] / 2, 32)
    #     for key in set(atoms):
    #         self._VBOBuffers.append(VRVBO(self.__primitives[key + '_Bond'][:-1], self.__primitives[key + '_Bond'][-1]).createVaoBuffer())
    #         self._buffers_labels.append(key + '_Bond')

    # def run(self):
    #     targetFps = 60
    #     prevTime = time.time()
    #     print(self._VBOBuffers)
    #     run = True
    #     while run:
    #         if self.__isCalculationLoaded:
    #             self.completeLoadOfCalculation()
    #         # glLoadIdentity()
    #         # glMultMatrixf(self.rotationMatrix)
    #         if self.isPerspective:
    #             self.__projectionMatrix = self.__perspectiveMatrix
    #         else:
    #             self.__projectionMatrix = self.__orthographicMatrix
    #         if self._parentWindowClosed:
    #             break
    #         for event in pygame.event.get():
    #             if event.type == pygame.QUIT:
    #                 self.BackStep, self.ForwardStep = False, False
    #                 run = False
    #                 self.__app.closeAllWindows()
    #                 break
    #             if event.type == pygame.KEYDOWN:
    #                 if event.key == pygame.K_ESCAPE:
    #                     self.BackStep, self.ForwardStep = False, False
    #                     run = False
    #                     self.__app.closeAllWindows()
    #                     break
    #                 if event.key == pygame.K_F4:
    #                     raise KeyError("Pushed exit key. Don't push F4 if you don't want to exit program.")
    #             if event.type == pygame.MOUSEMOTION and event.type != pygame.WINDOWLEAVE:
    #                 coord_x, coord_y = pygame.mouse.get_pos()
    #                 coord_x_mouse, coord_y_mouse = pygame.mouse.get_rel()
    #                 if self.mousePressed:
    #                     self.BackStep, self.ForwardStep = False, False
    #                     if self.onlyKeyboardSelect:
    #                         pygame.mouse.set_visible(False)
    #                     self.rotationInfo[0] -= (event.rel[0]) * 0.4
    #                     self.rotationInfo[1] += (event.rel[1]) * 0.4
    #             if event.type == pygame.MOUSEBUTTONUP:
    #                 if self.onlyKeyboardSelect:
    #                     pygame.mouse.set_visible(True)
    #             if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
    #                 self._scaleParameter = self._scaleParameter * 0.92
    #                 pygame.time.wait(10)
    #             if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
    #                 self._scaleParameter = self._scaleParameter * 1.08
    #                 pygame.time.wait(10)
    #             if event.type == pygame.MOUSEBUTTONDOWN and self._BuffersLabels:
    #                 if event.button == 1:
    #                     if not self.onlyKeyboardSelect:
    #                         self.selectAtom(True)
    #                 if event.button == 3:
    #                     if not self.onlyKeyboardSelect:
    #                         self.selectAtom(False)

    #             if event.type == pygame.VIDEORESIZE:
    #                 self.displayResize(event)

    #         keypress = pygame.key.get_pressed()

    #         # Отдаление модели при нажатии клавиши - на кейпаде
    #         if keypress[pygame.K_KP_MINUS] or keypress[pygame.K_MINUS]:
    #             self.BackStep, self.ForwardStep = False, False
    #             self._scaleParameter = self._scaleParameter * 1.03
    #             pygame.time.wait(10)
    #         # Приближение модели при нажатии кнопки + на кейпаде
    #         if keypress[pygame.K_KP_PLUS] or keypress[pygame.K_EQUALS]:
    #             self.BackStep, self.ForwardStep = False, False
    #             self._scaleParameter = self._scaleParameter * 0.97
    #             pygame.time.wait(10)
    #         ##################################
    #         if keypress[pygame.K_BACKSPACE]:
    #             self.BackStep, self.ForwardStep = False, False
    #             self.rotationInfo[0], self.rotationInfo[1] = 0.0, 0.0
    #             self._xD, self._yD, self._zD = 0, 0, 0
    #             self._scaleParameter = 1.0
    #             self.setDefaultRotationMatrix()
    #             self.__lights = np.dot(np.asarray(self.__lightsDefault), self.rotationMatrix)

    #         if keypress[pygame.K_LEFT]:
    #             self.BackStep, self.ForwardStep = False, False
    #             self.rotationInfo[0] -= 1.5
    #         if keypress[pygame.K_RIGHT]:
    #             self.BackStep, self.ForwardStep = False, False
    #             self.rotationInfo[0] += 1.5
    #         if keypress[pygame.K_UP]:
    #             self.BackStep, self.ForwardStep = False, False
    #             self.rotationInfo[1] += 1.5
    #         if keypress[pygame.K_DOWN]:
    #             self.BackStep, self.ForwardStep = False, False
    #             self.rotationInfo[1] -= 1.5
    #         if keypress[pygame.K_z]:
    #             self._xD = self._xD - 0.1
    #         if keypress[pygame.K_x]:
    #             self._xD = self._xD + 0.1
    #         if keypress[pygame.K_j]:
    #             self._zD = self._zD + 0.1
    #         if keypress[pygame.K_u]:
    #             self._zD = self._zD - 0.1
    #         if keypress[pygame.K_i]:
    #             self._fogPower += 1
    #             time.sleep(0.08)
    #         if keypress[pygame.K_k]:
    #             if self._fogPower > 1:
    #                 self._fogPower -= 1
    #                 time.sleep(0.08)
    #         if keypress[pygame.K_o]:
    #             self._fogDensity = self._fogDensity * 1.05
    #             time.sleep(0.08)
    #         if keypress[pygame.K_l]:
    #             self._fogDensity = self._fogDensity / 1.05
    #             time.sleep(0.08)
    #         if keypress[pygame.K_s]:
    #             for ind, name in enumerate(self.__calculation['ATOMNAMES']):
    #                 if name.split('_')[-1] != 'Sel':
    #                     self.__calculation['ATOMNAMES'][ind] += '_Sel'

    #         if (keypress[pygame.K_COMMA] or self.BackStep) and self._BuffersLabels:
    #             self._step -= 1 * self._speed
    #             if self._step < 0:
    #                 self._step = self.__calculation['STEPS'] - 1 + self._step
    #             self.__visualWindow.StepSlider.setSliderPosition(self._step)
    #             self.BackStep = True
    #         if (keypress[pygame.K_PERIOD] or self.ForwardStep) and self._BuffersLabels:
    #             self._step += 1 * self._speed
    #             if self._step >= self.__calculation['STEPS']:
    #                 self._step = self._step - self.__calculation['STEPS']
    #             self.__visualWindow.StepSlider.setSliderPosition(self._step)
    #             self.ForwardStep = True

    #         if keypress[pygame.K_a]:
    #             self.selectAtom(True)
    #         if keypress[pygame.K_d]:
    #             self.selectAtom(False)

    #         if keypress[pygame.K_p]:
    #             self.__visualWindow.processingStart()

    #         # Движение модели мышкой
    #         for _ in pygame.mouse.get_pressed():
    #             if pygame.mouse.get_pressed()[0] == 1:
    #                 self.mousePressed = True
    #             elif pygame.mouse.get_pressed()[0] == 0:
    #                 self.mousePressed = False

    #         glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    #         glClearColor(*self._backgroundColor)
    #         self.rotationMatrix = self.defineRotation(self.defineRotationAroundAxes, self.rotationMatrix, self.rotationInfo, self._xD, self._yD, self._zD, self._scaleParameter)
    #         self.normalMatrix = self.defineNormalMatrix(self.__viewMatrix, self.rotationMatrix)
    #         # # Отрисовка границ ячейки
    #         # if self.drawCell and self._BuffersLabels:
    #         #     self.cellDraw(self.__calculation['BASIS_VERT'], self.drawCell, self.drawAxes, 3)

    #         # x, y, z = self.findWindowDimensions(-5)
    #         for index, Buffer in enumerate(self._VBOBuffers):
    #             Buffer.prepareToDraw(self.__program.program)
    #             Buffer.setLightSettings(self.__program.uniformVariablesDict, self.__Ka, self.__Kd, self.__Ks, self.__Shininess, self.__lights, self.__intensities)
    #             Buffer.setFogParameters(self.__program.uniformVariablesDict, self.__cellPosition, self._fogColor, self._fogMinDist, self._fogMaxDist, self._fogPower, self._fogDensity)
    #             if not self._BuffersLabels:
    #                 glActiveTexture(GL_TEXTURE0)
    #                 glBindTexture(GL_TEXTURE_2D, self._cubeCoveredTexture)
    #                 Buffer.isTextureExist(self.__program.uniformVariablesDict, 1)
    #                 Buffer.setTextureInfo(self.__program.uniformVariablesDict, 0)
    #                 for xD, yD, zD in self.defaultCubePosition:
    #                     self.__translationMatrix[0][-1] = xD
    #                     self.__translationMatrix[1][-1] = yD
    #                     self.__translationMatrix[2][-1] = zD
    #                     Buffer.drawFromVaoBuffer(self.__drawType, self.__program.uniformVariablesDict, self.rotationMatrix.transpose(), self.__viewMatrix, self.__projectionMatrix.transpose(), self.normalMatrix, self.__translationMatrix)
    #                 glBindTexture(GL_TEXTURE_2D, 0)
    #             else:
    #                 Buffer.isTextureExist(self.__program.uniformVariablesDict, 0)
    #                 for atomIndex, (xD, yD, zD) in enumerate(self.__calculation['POSITIONS'][self._step]):
    #                     if self._BuffersLabels[index] == self.__calculation['ATOMNAMES'][atomIndex]:
    #                         self.__translationMatrix[0][-1] = xD
    #                         self.__translationMatrix[1][-1] = yD
    #                         self.__translationMatrix[2][-1] = zD
    #                         Buffer.drawFromVaoBuffer(self.__drawType, self.__program.uniformVariablesDict, self.rotationMatrix.transpose(), self.__viewMatrix, self.__projectionMatrix.transpose(), self.normalMatrix, self.__translationMatrix)
    #                     if self._BuffersLabels[index] == self.__calculation['ATOMNAMES'][atomIndex] + '_Bond':
    #                         self.__translationMatrix[0][-1] = xD
    #                         self.__translationMatrix[1][-1] = yD
    #                         self.__translationMatrix[2][-1] = zD
    #                         Buffer.drawFromVaoBuffer(self.__drawType, self.__program.uniformVariablesDict, self.rotationMatrix.transpose(), self.__viewMatrix, self.__projectionMatrix.transpose(), self.normalMatrix, self.__translationMatrix)
    #             Buffer.endOfDrawing()
    #         pygame.display.flip()
    #         self.rotationInfo[0], self.rotationInfo[1] = 0.0, 0.0
    #         self._scaleParameter = 1.0
    #         self._xD, self._yD, self._zD = 0.0, 0.0, 0.0
    #         currTime = time.time()
    #         diff = currTime - prevTime
    #         delay = max(1.0 / targetFps - diff, 0)
    #         time.sleep(delay)
    #         fps = 1.0 / (delay + diff)
    #         prevTime = currTime
    #     for _ in range(len(self._VBOBuffers)):
    #         self._VBOBuffers.pop(0).__del__()
    #     self.__visualWindow.close()
    #     pygame.quit()
