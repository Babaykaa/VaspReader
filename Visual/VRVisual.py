import os
import codecs
from Visual.VROpenGL import VROpenGL
from Processing.VRMD import VRMD, QEMD
from Processing.VRProcessing import VRProcessing
from Gui.VRVisualGUI import Ui_VRVisual, QColorDialog, QFileDialog, QMainWindow
from Logs.VRLogger import sendDataToLogger


class VRVisualWindow(Ui_VRVisual, QMainWindow):
    __project_directory = os.path.abspath('')

    @sendDataToLogger
    def __init__(self, app, settings, open_gl_window, print_window_object):
        super(VRVisualWindow, self).__init__()
        self.__logger = print_window_object
        self.calculation_folder = None
        self.__calculations = dict()
        self.__app = app
        self.__settings = settings
        location = self.__settings.visual_window_location
        self.setupUi(self)
        self.link_elements_with_functions()
        if location is not None:
            self.move(location[0], location[1])
        self.show()

        self.__open_gl_window = None
        self.__processing_window = None
        self._StepSliderSpeed = 1
        self._backgroundColor = (0.6, 0.6, 0.6, 1.0)
        self._window_closed = False

    def link_with_open_gl_window(self, window_object):
        self.__open_gl_window = window_object

    @sendDataToLogger
    def link_elements_with_functions(self):
        self.AOpen_calculation.triggered.connect(self.open_calculation_folder)
        self.ABackground.triggered.connect(self.background_color_change)
        self.BrowseButton.clicked.connect(self.open_calculation_folder)
        self.AAbout_the_program.triggered.connect(self.about_the_program)
        self.AAbout_window.triggered.connect(self.about_the_window)
        self.ALatest_update.triggered.connect(self.lattest_update)
        self.AChanges_history.triggered.connect(self.changes_history)
        self.AExit.triggered.connect(self.closeEvent)
        self.CalculationAddButton.clicked.connect(self.add_calculation)
        self.AddedCalculations.activated.connect(self.change_active_calculation)
        self.DeleteCalculationButton.clicked.connect(self.delete_calculation)
        self.StepSlider.actionTriggered.connect(self.calculation_step_change)
        self.SpeedSlider.actionTriggered.connect(self.speed_change)
        self.APerspective.toggled.connect(self.perspective_chose)
        self.AOrthographic.toggled.connect(self.orthographic_chose)
        self.MoveBack.clicked.connect(self.backward_move)
        self.MoveForward.clicked.connect(self.forward_move)
        self.ToFirstStep.clicked.connect(self.to_first_step)
        self.ToLastStep.clicked.connect(self.to_last_step)
        self.AProcessing.triggered.connect(self.processing_start)

    def get_logger(self):
        return self.__logger

    @sendDataToLogger(operation_type='user')
    def to_first_step(self):
        self.__open_gl_window._step = 0
        self.StepSlider.setSliderPosition(0)

    @sendDataToLogger(operation_type='user')
    def to_last_step(self):
        self.__open_gl_window._step = self.__calculations[self.calculation_folder]['STEPS'] - 1
        self.StepSlider.setSliderPosition(self.__calculations[self.calculation_folder]['STEPS'] - 1)

    @sendDataToLogger(operation_type='user')
    def backward_move(self):
        self.__open_gl_window.Back_Step = True

    @sendDataToLogger(operation_type='user')
    def forward_move(self):
        self.__open_gl_window.Forward_Step = True

    def stop_step_changing(self):
        self.__open_gl_window.Back_Step = False
        self.__open_gl_window.Forward_Step = False

    @sendDataToLogger(operation_type='user')
    def open_calculation_folder(self):
        self.DirectoryPath.setText(QFileDialog.getExistingDirectory(None, caption="Choose directory to parse"))

    @sendDataToLogger
    def closeEvent(self, event):
        self.__settings.visual_window_location = self.pos().toTuple()
        self.__logger.close()
        self.__open_gl_window._parent_window_closed = True
        self.__logger._visual_window_closed = True
        event.accept()

    @sendDataToLogger(operation_type='user')
    def perspective_chose(self, checked, *args):
        if checked:
            self.APerspective.setChecked(True)
            self.AOrthographic.setChecked(False)
            self.__open_gl_window.is_perspective = True
            self.__logger.addMessage('Changed to perspective view', self.__class__.__name__)
        else:
            self.APerspective.setChecked(False)
            self.AOrthographic.setChecked(True)
            self.__open_gl_window.is_perspective = False
            self.__logger.addMessage('Changed to orthographic view', self.__class__.__name__)

    @sendDataToLogger(operation_type='user')
    def orthographic_chose(self, checked, *args):
        if checked:
            self.APerspective.setChecked(False)
            self.AOrthographic.setChecked(True)
            self.__open_gl_window.is_perspective = False
            self.__logger.addMessage('Changed to orthographic view', self.__class__.__name__)
        else:
            self.APerspective.setChecked(True)
            self.AOrthographic.setChecked(False)
            self.__open_gl_window.is_perspective = True
            self.__logger.addMessage('Changed to perspective view', self.__class__.__name__)

    @sendDataToLogger(operation_type='user')
    def background_color_change(self):
        self._backgroundColor = QColorDialog().getColor().toTuple()
        self._backgroundColor = tuple([self._backgroundColor[i] / 255 for i in range(len(self._backgroundColor))])
        self.__open_gl_window._background_color = self._backgroundColor
        self.__open_gl_window._fogColor = self._backgroundColor
        self.__logger.addMessage(f'Background color changed to {self._backgroundColor}', self.__class__.__name__)

    def calculation_step_change(self):
        self.stop_step_changing()
        self.__open_gl_window._step = self.StepSlider.sliderPosition()

    def speed_change(self):
        self._StepSliderSpeed = self.SpeedSlider.sliderPosition()
        self.__open_gl_window._speed = self._StepSliderSpeed

    @sendDataToLogger(operation_type='user')
    def add_calculation(self):
        self.stop_step_changing()
        self.calculation_folder = self.DirectoryPath.text()
        if self.calculation_folder not in self.__calculations:
            parser_obj = VRMD(self.calculation_folder, self.__logger)
            self.__calculations[self.calculation_folder] = parser_obj._parser_parameters
            if parser_obj.breaker:
                self.__calculations.pop(self.calculation_folder)
                parser_obj = QEMD(self.calculation_folder, self.__logger)
                self.__calculations[self.calculation_folder] = parser_obj._parser_parameters

            if not parser_obj.breaker:
                self.__open_gl_window.load_calculation_info(self.__calculations[self.calculation_folder])
                self.__logger.addMessage(f'Chosen {self.calculation_folder} appended.\n', self.__class__.__name__)
                self.AddedCalculations.addItem(self.calculation_folder)
                self.AddedCalculations.setPlaceholderText(self.calculation_folder)
                self.StepSlider.setMaximum(self.__calculations[self.calculation_folder]['STEPS'] - 1)
                self.StepSlider.setValue(0)
                self.__open_gl_window._step = 0
            else:
                self.__calculations.pop(self.calculation_folder)

    @sendDataToLogger(operation_type='user')
    def delete_calculation(self):
        self.stop_step_changing()
        self.__calculations.pop(self.calculation_folder)
        if self.__calculations:
            folder_to_delete = self.calculation_folder
            self.calculation_folder = list(self.__calculations.keys())[-1]
            self.__open_gl_window.load_calculation_info(self.__calculations[self.calculation_folder])
            self.StepSlider.setMaximum(self.__calculations[self.calculation_folder]['STEPS'] - 1)
            self.__logger.addMessage(f'Changed to {self.calculation_folder}.\n', self.__class__.__name__)
            self.AddedCalculations.setPlaceholderText(self.calculation_folder)
            index = [self.AddedCalculations.itemText(i) for i in range(self.AddedCalculations.count())].index(
                folder_to_delete)
            self.AddedCalculations.removeItem(index)
        else:
            self.calculation_folder = None
            self.__open_gl_window.without_calculation()
            self.StepSlider.setMaximum(100)
            self.AddedCalculations.removeItem(0)
            self.AddedCalculations.setPlaceholderText('Choose calculation to delete.')
        self.StepSlider.setValue(0)
        self.__open_gl_window._step = 0

    @sendDataToLogger(operation_type='user')
    def change_active_calculation(self):
        self.stop_step_changing()
        new_calculation_folder = self.AddedCalculations.currentText()
        if new_calculation_folder != self.calculation_folder:
            self.calculation_folder = new_calculation_folder
            self.__open_gl_window.load_calculation_info(self.__calculations[self.calculation_folder])
            self.StepSlider.setMaximum(self.__calculations[self.calculation_folder]['STEPS'] - 1)
            self.StepSlider.setValue(0)
            self.__open_gl_window._step = 0
            self.__logger.addMessage(f'Changed to {self.calculation_folder}.\n', self.__class__.__name__)

    @sendDataToLogger(operation_type='user')
    def processing_start(self):
        if self.__calculations[self.calculation_folder]['STEPS']:
            self.__processing_window = VRProcessing(self.__app, self.__settings, self, self.__logger,
                                                    self.__open_gl_window, self.__calculations[self.calculation_folder], self.calculation_folder,
                                                    self.ADelete_coordinates_after_leave_cell.isChecked())
            self.__processing_window.show()

    @sendDataToLogger(operation_type='user')
    def about_the_program(self):
        message = '''VaspReader is a program firstly for processing and visualizing the results of VASP calculations. \
Have additional modes for simplify your life as more as it possible. \
It was developed at the end of 2021 and has undergone many changes described in other features of the help menu.\n'''
        self.__logger.addMessage(message, self.__class__.__name__, "Wrote about the program", 'user')

    @sendDataToLogger(operation_type='user')
    def about_the_window(self):
        message = '''Main VaspReader windows consists of control panel with the ability to add and delete calculations, \
processing them and use some additional modes such as work with supercomputer, parsing OSZICAR files, reading and work \
with POSCAR files and some others functions and visualizing of calculations window with changeable settings, such as \
lightning, background color, bounds draw and some others functions. Key assignments: +, - on keypad or keyboard or \
mouse scroll to zoom, a - to add an atom to the list, d - to remove an atom from the list, z - to move camera left, \
x - right, u - up, j - down, Backspace - return model to the first position, use arrows to rotate the model.\n'''
        self.__logger.addMessage(message, self.__class__.__name__, "Wrote about the visual window", 'user')

    @sendDataToLogger(operation_type='user')
    def lattest_update(self):
        message = '''\u262D ver. 3.0.0: \u262D\n\u2705 Global update:\n1. VaspReader, consisting of several windows, \
has been redesigned into one main window with a settings menu before processing. It consists of many useful features \
such as: parsing calculation, configuration state loading/saving, loading/saving from/to json parsed calculations and \
others. You can find the entire list of options using the change history option.\n2. The position of the main window \
is now saved when the window is closed and after starting the program it will be in the saved position.\n3. Created \
two window themes: white and black. The theme is also saved when the window is closed.\n4. Added two functions: view \
model cell and axes.\n5. The position of the light can now be set by 8 edges of the cube.\n6. Added a convenient \
option to change the background.\n7. In the latest version, an orthogonal view of the model with the mode of selecting \
atoms has been added.\n8. NEW PERFECT FEATURE: The camera can be moved in all directions. You can find the binding \
keys in the visual description of the window.\n9. The bonds calculation function now activates the bonds editing \
window with 3 modes: all bonds, selected bonds and the drawing trajectory tab. A description of these options can be \
found in the update history.\n10. Reworked windows OSZICAR, POSCAR. The new graphical interface for these windows \
allows, for example, checking curves from an OSZICAR file or drawing POSCAR/CONTCAR files in the visual window.\n'''
        self.__logger.addMessage(message, self.__class__.__name__, "Wrote latest update info", 'user')

    @sendDataToLogger(operation_type='user')
    def changes_history(self):
        with codecs.open('PreviousChanges.txt', 'r', encoding='utf-8') as previous_file:
            message = previous_file.read()
            self.__logger.addMessage(f'{message}\n', self.__class__.__name__, "Wrote previous changes", 'user')
