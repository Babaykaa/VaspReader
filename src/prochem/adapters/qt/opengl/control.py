"""Control window class"""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

import os
import codecs
import logging
from multiprocessing import Process, Lock as MLock, cpu_count, Manager
from threading import Thread, Lock as TLock
from prochem.adapters.qt.api import (
    calculation_entry,
    calculation_step_count,
    parse_calculation,
)
from prochem.adapters.qt.windowing import move_to_saved_or_default
from prochem.adapters.qt.windows.vasp_processing import VRProcessing
from prochem.adapters.qt.windows.oszicar import VROszicar
from prochem.adapters.qt.generated.control import Ui_Control, QMainWindow
from PySide6.QtCore import QTimer
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QColorDialog, QFileDialog

logger = logging.getLogger(__name__)

__all__ = ["ControlWindow"]


class ControlWindow(Ui_Control, QMainWindow):
    """
    A window providing control and visualization for VASP calculations.
    
    This class manages the application's main window, handling user interactions,
    loading calculations, controlling visualization, and managing processing tasks.
    
    Class Attributes:
    - __cpu_count
    
    Class Methods:
    - __init__:
    """
    __cpu_count = cpu_count()
    
    def __init__(self, settings, print_window_object):
        """
        Initializes the ControlWindow.
        
        Args:
            settings: Configuration settings for the window.
            print_window_object: An object providing access to the print window and project directory.
        
        Initializes the following object properties:
            self.__settings: Stores the configuration settings.
            self.__print_window: Stores the print window object.
            self.closed: A boolean flag indicating whether the window is closed. Initialized to False.
            self.__project_directory: The project directory obtained from the print window.
            self.__location: The saved location of the window, if available.
            self.__calculation_id: An integer used to uniquely identify calculations. Initialized to 1.
            self.__calculations: A dictionary to store calculations, keyed by their ID.
            self.__parser_threads: A list to store parser threads.
            self.__parser_processes: A list to store parser processes.
            self.__parser_objs: A list to store parser objects.
            self.__threads_locker: A TLock object for synchronizing access to parser threads.
            self.__processes_locker: An MLock object for synchronizing access to parser processes.
            self.__is_threading_mode: A boolean flag indicating whether threading mode is enabled. Initialized to True.
            self.__visual_window: A reference to the visual window. Initialized to None.
            self.__processing_window: A reference to the processing window. Initialized to None.
            self.__oszicar_window: A reference to the OSZICAR window. Initialized to None.
            self._window_closed: A boolean flag indicating whether the window is closed. Initialized to False.
            self.__parser_timer: A GUI-thread timer that checks completed parser jobs.
        
        Returns:
            None
        """
        super(ControlWindow, self).__init__()
        self.__settings = settings
        self.__print_window = print_window_object
        self.closed = False
        self.__project_directory = self.__print_window.get_project_dir()
        self.setupUi(self)
        logger.info(f"ControlUI setuped")
        self.link_elements_with_functions()
        logger.info(f"ControlUI elements linked with functions")
        
        move_to_saved_or_default(self, self.__settings, 'control', default_offset=(520, 40))
        logger.info(f"Control window positioned")

        self.__calculation_id = 1
        self.__calculations = dict()
        self.calculation_folder = None
        
        self.__parser_threads, self.__parser_processes, self.__parser_objs = [], [], []
        self.__threads_locker, self.__processes_locker = TLock(), MLock()
        self.__is_threading_mode = True
        if self.__cpu_count > 4:
            self.AThreading.setEnabled(True)
            self.AMultiprocessing.setEnabled(True)
            logger.info(f"Device has {self.__cpu_count} cores. Multiprocessing mode enabled")

        self.__visual_window = None
        self.__processing_window = None
        self.__oszicar_window = None
        
        self._window_closed = False
        self.__parser_timer = QTimer(self)
        self.__parser_timer.timeout.connect(self.check_parsers)
        self.__parser_timer.start(200)
        self.show()
        logger.info(f"Control window initialized")

    def link_with_visual_window(self, window_object):
        """
        Links the control window with a visual window.
        
        This method establishes a connection between the control window and a visual
        window, allowing them to share calculation information.
        
        Args:
            self: The ControlWindow instance.
            window_object: The VisualWindow object to link with.
        
        Initializes:
            __visual_window: The VisualWindow object linked to this control window.
            
        
        Returns:
            None
        """
        self.__visual_window = window_object
        self.__visual_window.load_calculation_info(self.__calculations)
        logger.info(f"Control window linked with Visual window")

    def link_elements_with_functions(self):
        """
        Connects GUI elements to their corresponding functions.
        
        This method establishes connections between various GUI elements (e.g., buttons, sliders, menu items)
        and the functions that should be executed when those elements are interacted with.  It effectively
        wires up the user interface to the application's logic.
        
        Args:
            self: The instance of the class.
        
        Returns:
            None
        """
        self.ALoad_Calculation.triggered.connect(self.load_calculation_files)
        self.ABackground.triggered.connect(self.background_color_change)
        self.TreeViewAddCalculation.triggered.connect(self.load_calculation_files)
        self.TreeViewDeleteCalculation.triggered.connect(self.delete_calculation)
        self.AAbout_the_program.triggered.connect(self.about_the_program)
        self.AAbout_window.triggered.connect(self.about_the_window)
        self.ALatest_update.triggered.connect(self.lattest_update)
        self.AChanges_history.triggered.connect(self.changes_history)
        self.AExit.triggered.connect(self.closeEvent)
        self.StepSlider.actionTriggered.connect(self.calculation_step_change)
        self.SpeedSlider.actionTriggered.connect(self.speed_change)
        self.APerspective.toggled.connect(self.perspective_chosen)
        self.AOrthographic.toggled.connect(self.orthographic_chosen)
        self.AKeyboard.toggled.connect(self.keyboard_select)
        self.AMouse_keyboard.toggled.connect(self.mouse_and_keyboard_select)
        self.MoveBack.clicked.connect(self.backward_move)
        self.MoveForward.clicked.connect(self.forward_move)
        self.ToFirstStep.clicked.connect(self.to_first_step)
        self.ToLastStep.clicked.connect(self.to_last_step)
        self.VASP_Processing.triggered.connect(self.processing_start)
        self.VASP_OSZICAR.triggered.connect(self.oszicar_window)
        self.AThreading.toggled.connect(self.set_threading)
        self.AMultiprocessing.toggled.connect(self.set_multiprocessing)
        logger.info(f"Control window elements linked with functions")

    def get_print_window(self):
        """
        Returns the print window.
        
        Args:
          self: The instance of the class.
        
        Returns:
          The print window object.
        """
        return self.__print_window

    def get_visual_window(self):
        """
        Returns the visual window associated with the object.
        
        Args:
            self: The instance of the class.
        
        Returns:
            The visual window object.
        """
        return self.__visual_window

    def get_processing_window(self):
        """
        Returns the processing window.
        
        Args:
            self: The instance of the class.
        
        Returns:
            The processing window.
        """
        return self.__processing_window

    def get_oszicar_window(self):
        """
        Returns the Oszicar window.
        
        Args:
            self: The instance of the class.
        
        Returns:
            The Oszicar window.
        """
        return self.__oszicar_window

    def get_settings(self):
        """
        Retrieves the application settings.
        
        Args:
            self: The instance of the class.
        
        Returns:
            The application settings.
        """
        return self.__settings

    def set_multiprocessing(self, checked):
        """
        Sets the multiprocessing mode.
        
        This method updates the UI elements and internal state to reflect the
        desired multiprocessing mode. It toggles the threading and multiprocessing
        checkboxes and updates a flag indicating the current mode.
        
        Args:
         self: The object instance.
         checked: A boolean value indicating whether multiprocessing mode should be enabled.
        
        Returns:
         None
        
        Class Fields Initialized:
         - `self.AThreading`: A checkbox widget representing threading mode.  Its checked state is set to the opposite of the `checked` argument.
         - `self.AMultiprocessing`: A checkbox widget representing multiprocessing mode. Its checked state is set to the value of the `checked` argument.
         - `self.__is_threading_mode`: A private boolean flag indicating whether threading mode is active. It is set to the opposite of the `checked` argument.
        """
        self.AThreading.setChecked(not checked)
        self.AMultiprocessing.setChecked(checked)
        self.__is_threading_mode = not checked
        logger.info(f"Multiprocessing mode set to {not self.__is_threading_mode}")

    def set_threading(self, checked):
        """
        Sets the threading mode and updates the UI accordingly.
        
        This method enables or disables threading mode based on the provided value.
        When threading mode is enabled, multiprocessing mode is automatically disabled, and vice versa.
        It also updates the UI elements (checkboxes) to reflect the current mode and logs the change.
        
        Args:
         self: The instance of the class.
         checked: A boolean indicating whether threading mode should be enabled.
        
        Returns:
         None
        """
        self.AThreading.setChecked(checked)
        self.AMultiprocessing.setChecked(not checked)
        self.__is_threading_mode = checked
        logger.info(f"Threading mode set to {self.__is_threading_mode}")

    def block_parser_mode_changing(self):
        """
        Blocks the changing of parser modes (threading and multiprocessing).
        
         This method disables both threading and multiprocessing modes for the parser,
         preventing mode switching. It also logs an informational message.
        
         Parameters:
          self: The instance of the class.
        
         Returns:
          None
         
         Class Fields Initialized:
          - AThreading: A boolean flag indicating whether threading mode is enabled. Set to False.
          - AMultiprocessing: A boolean flag indicating whether multiprocessing mode is enabled. Set to False.
        """
        self.AThreading.setEnabled(False)
        self.AMultiprocessing.setEnabled(False)
        logger.info(f"Parser mode changing blocked")

    def enable_parser_mode_changing(self):
        """
        Enables the changing of parser modes by enabling both threading and multiprocessing.
        
        Args:
            self: The instance of the class.
        
        Initializes:
            AThreading: A boolean flag indicating whether threading is enabled for parsing.
            AMultiprocessing: A boolean flag indicating whether multiprocessing is enabled for parsing.
        
        Returns:
            None
        """
        self.AThreading.setEnabled(True)
        self.AMultiprocessing.setEnabled(True)
        logger.info(f"Parser mode changing enabled")

    def to_first_step(self):
        """
        Resets the simulation to the first step.
        
        This method resets the internal step counter and the step slider position
        to the beginning of the simulation. It also updates the step label
        to reflect the new step.
        
        Args:
         self: The instance of the class.
        
        Returns:
         None
        """
        self.__visual_window.set_frame_index(0)
        self.StepSlider.setSliderPosition(0)
        self.StepLabel.setText(f'Step:\t{self.__visual_window._step}\tfrom\t{self.StepSlider.maximum()}')
        logger.info(f"Step changed to 0")

    def to_last_step(self):
        """
        Moves the calculation step to the last step.
        
        Updates the visual window, step slider, and step label to reflect the last step
        of the calculation. Logs an informational message.
        
        Args:
            self: The instance of the class.
        
        Returns:
            None
        """
        last_step = self._calculation_step_count(self.calculation_folder) - 1
        self.__visual_window.set_frame_index(last_step)
        self.StepSlider.setSliderPosition(last_step)
        self.StepLabel.setText(f'Step:\t{self.__visual_window._step}\tfrom\t{self.StepSlider.maximum()}')
        logger.info(f"Step changed to last step")

    def backward_move(self):
        """
        Moves the visualization back one step.
        
        Sets the `back_step` attribute of the visual window to True, indicating a backward move.
        Updates the StepLabel text to reflect the current step and the maximum step value.
        
        Args:
            self: The instance of the class.
        
        Returns:
            None
        """
        self.__visual_window.back_step = True
        self.StepLabel.setText(f'Step:\t{self.__visual_window._step}\tfrom\t{self.StepSlider.maximum()}')

    def forward_move(self):
        """
        Moves the visualization forward one step.
        
        Updates the visual window to reflect the next step in the simulation
        and updates the StepLabel to display the current step and maximum step.
        
        Args:
            self: The instance of the class.
        
        Returns:
            None
        """
        self.__visual_window.forward_step = True
        self.StepLabel.setText(f'Step:\t{self.__visual_window._step}\tfrom\t{self.StepSlider.maximum()}')

    def stop_step_changing(self):
        """
        Stops the visual window from changing steps (back or forward).
        
        This method sets both the `back_step` and `forward_step` attributes of the
        `__visual_window` object to False, effectively halting any automatic step
        changes in the visualization.
        
        Args:
         self: The instance of the class.
        
        Returns:
         None
        """
        self.__visual_window.back_step = False
        self.__visual_window.forward_step = False

    def load_calculation_files(self):
        """
        Loads calculation files selected by the user.
        
        Args:
         self: The instance of the class.
        
        Initializes:
         browse_folder_path: The path to the directory containing the selected calculation files. This is stored in the settings for future use.
        
        Returns:
         None
        """
        file_names, filter = QFileDialog.getOpenFileNames(
            self,
            "Choose files for parsing",
            self.__settings.get_control_params('browse_folder_path'),
            "All Files (*);;VASP XML (*.xml)" # File filters
        )
        if file_names:
            self.__settings.set_control_params(os.path.dirname(file_names[0]), 'browse_folder_path')
            for file_name in file_names:
                self.add_calculation(file_name)

        #logger.info(f"Calculation directory chosen")

    def closeEvent(self, event=QCloseEvent):
        """
        Saves the control window's position and closes associated windows.
        
         This method is called when the control window is closed. It saves the
         current position of the control window, closes the visual and print
         windows, and accepts the close event.
        
         Parameters:
          self: The instance of the class.
        
         Initializes:
          closed: A boolean flag indicating whether the control window has been closed.
        
         Returns:
          None
        """
        self.__settings.set_new_window_location(self.pos().toTuple(), 'control')
        self.closed = True
        if not self.__visual_window.closed:
            self.__visual_window.close()
        self.__print_window.close()
        event.accept()

    def keyboard_select(self, checked, *args):
        """
        Sets the keyboard selection mode and updates related settings.
        
        This method enables or disables keyboard selection, updates the UI to reflect
        the change, and saves the setting to persistent storage.
        
        Args:
          self: The instance of the class.
          checked: A boolean indicating whether keyboard selection is enabled.
        
        Returns:
          None
        
        Class Fields Initialized:
          - AKeyboard: A reference to the keyboard selection UI element.
          - AMouse_keyboard: A reference to the mouse/keyboard selection UI element.
          - __settings: An instance of a settings manager for persistent storage.
        """
        self.AKeyboard.setChecked(checked)
        self.AMouse_keyboard.setChecked(not checked)
        self.__settings.set_control_params(checked, 'only_keyboard_selection')
        logger.info(f"Keyboard selection set to {checked}")

    def mouse_and_keyboard_select(self, checked, *args):
        """
        Toggles between mouse+keyboard and keyboard-only selection modes.
        
        Args:
         checked: A boolean indicating whether to enable mouse+keyboard selection. 
                  If True, enables mouse+keyboard selection; otherwise, enables keyboard-only selection.
        
        Class Fields Initialized:
         - AKeyboard: Checkable widget representing keyboard selection mode.
         - AMouse_keyboard: Checkable widget representing mouse+keyboard selection mode.
         - __settings: An object holding application settings, used to store the visual parameter.
         - get_print_window(): Method to access the print window for displaying messages.
        
        Returns:
         None
        """
        self.AKeyboard.setChecked(not checked)
        self.AMouse_keyboard.setChecked(checked)
        self.__settings.set_control_params(not checked, 'only_keyboard_selection')
        self.get_print_window().add_message('Changed to mouse+keyboard mode.' if checked else 'Changed to keyboard mode.')
        logger.info(f"Mouse+keyboard mode set to {checked}")

    def perspective_chosen(self, checked, *args):
        """
        Sets the perspective mode and updates the UI and settings.
        
        Args:
         checked:  A boolean indicating whether perspective mode is selected.
        
        Initializes:
         self.APerspective: The checkbox representing perspective mode.
         self.AOrthographic: The checkbox representing orthographic mode.
         self.__settings: An object to store and manage settings.
        
        Returns:
         None
        """
        self.APerspective.setChecked(checked)
        self.AOrthographic.setChecked(not checked)
        self.__settings.set_scene_params(checked, 'view', 'is_perspective')
        logger.info(f"Perspective mode set to {checked}")

    def orthographic_chosen(self, checked, *args):
        """
        Toggles between orthographic and perspective views.
        
        Args:
          checked:  A boolean indicating whether to switch to orthographic view.
          *args: Variable length argument list.
        
        Initializes:
          APerspective: A reference to the perspective view checkbox.
          AOrthographic: A reference to the orthographic view checkbox.
          __settings: An instance of a settings class used to store visual parameters.
        
        Returns:
          None
        """
        self.APerspective.setChecked(not checked)
        self.AOrthographic.setChecked(checked)
        self.__settings.set_scene_params(not checked, 'view', 'is_perspective')
        self.get_print_window().add_message('Changed to orthographic view' if checked else 'Changed to perspective view')
        logger.info(f"Orthographic mode set to {checked}")

    def background_color_change(self):
        """
        Changes the background and fog color of the scene.
        
         This method opens a color dialog, applies the selected color to both the
         background and fog, and logs the change.
        
         Parameters:
          self - The instance of the class.
        
         Returns:
          None
        """
        color = tuple([el[i] / 255 for col in QColorDialog().getColor().toTuple()])
        self.__settings.set_scene_params(color, 'background', 'color')
        self.__settings.set_scene_params(color, 'fog', 'color')
        self.get_print_window().add_message(f'Background color changed to {color}')
        logger.info(f"Background color changed to {color}")

    def calculation_step_change(self):
        """
        Updates the displayed step value based on the slider position.
        
        This method stops any ongoing step changing process, updates the internal step
        value with the current slider position, and then updates the label displaying
        the current step and maximum step values.
        
        Args:
            self: The instance of the class.
        
        Returns:
            None
        """
        self.stop_step_changing()
        self.__visual_window.set_frame_index(self.StepSlider.sliderPosition())
        self.StepLabel.setText(f'Step:\t{self.__visual_window._step}\tfrom\t{self.StepSlider.maximum()}')

    def speed_change(self):
        """
        Changes the simulation speed based on the slider position.
        
         This method updates the simulation speed by retrieving the current
         position of the speed slider and setting the 'slider_speed' visual
         parameter in the settings object.
        
         Parameters:
          self - The instance of the class.
        
         Returns:
          None
        """
        self.__settings.set_control_params(self.SpeedSlider.sliderPosition(), 'slider_speed')

    def add_calculation(self, file_path: str):
        """
        Adds a calculation to be parsed.
        
        This method checks if the calculation has already been added, then parses the calculation file
        using either threading or multiprocessing, depending on the configured mode.
        
        Args:
            self: The instance of the class.
            file_path (str): The path to the VASP calculation file.
        
        Returns:
            None
        """
        self.stop_step_changing()
        for calc_id in self.__calculations:
            for calc in self.__calculations[calc_id].get('calculations', []):
                if str(calc.source) == file_path:
                    logger.info(f"Calculation {file_path} already added")
                    return

        job = {"source": file_path, "calculation": None, "error": None}
        self.__parser_objs.append(job)
        self.__parser_threads.append(Thread(target=self._parse_in_thread, args=(job,), daemon=True))
        self.__parser_threads[-1].start()
        self.block_parser_mode_changing()
        logger.info(f"Calculation {file_path} parsing in threading mode")

    @staticmethod
    def _parse_in_thread(job):
        try:
            job["calculation"] = parse_calculation(job["source"])
        except Exception as exc:
            job["error"] = exc

    @staticmethod
    def _normalize_calculation_key(key):
        if isinstance(key, str) and key.isdigit():
            return int(key)
        return key

    def _calculation_step_count(self, key):
        entry = self.__calculations[self._normalize_calculation_key(key)]
        if isinstance(entry, dict) and entry.get('calculations'):
            return max(calculation_step_count(entry['calculations'][0]), 1)
        return entry['STEPS']

    def check_parsers(self):
        """
        Checks for completed parser threads or processes and processes their results.
        
        This method continuously monitors parser threads or processes to determine if they have finished.
        When a thread or process completes, its associated parsing result is processed and added to the action queue.
        The method handles both threading and multiprocessing modes. It also enables parser mode changing when all parsers are finished.
        
        Args:
            self: The instance of the class.
        
        Initializes:
            __is_threading_mode: A boolean indicating whether threading mode is enabled.
            __parser_threads: A list of parser threads.
            __parser_processes: A list of parser processes.
            __parser_objs: A list of parser objects (results).
            __threads_locker: A lock for synchronizing access to parser threads.
            __processes_locker: A lock for synchronizing access to parser processes.
        
        Returns:
            None
        """
        if self.__parser_threads:
            completed = [
                num
                for num, thread in enumerate(self.__parser_threads)
                if not thread.is_alive()
            ]
            for num in reversed(completed):
                with self.__threads_locker:
                    parser = self.__parser_objs.pop(num)
                    self.__parser_threads.pop(num)
                self.process_add_action(parser)
            if not self.__parser_threads:
                self.enable_parser_mode_changing()
        elif not self.__is_threading_mode and self.__parser_processes:
            completed = [
                num
                for num, process in enumerate(self.__parser_processes)
                if not process.is_alive()
            ]
            for num in reversed(completed):
                with self.__processes_locker:
                    parser = dict(self.__parser_objs.pop(num))
                    self.__parser_processes.pop(num)
                self.process_add_action(parser)
            if not self.__parser_processes:
                self.enable_parser_mode_changing()

    def process_add_action(self, parser):
        """
        Processes an add action by parsing a calculation and adding it to the calculations list.
        
        Args:
            self: The instance of the class.
            parser: The parser object containing the calculation to be added.
        
        Initializes the following object properties:
            __calculations: A dictionary storing calculations, where keys are IDs and values are dictionaries containing 'visible' (boolean) and 'calculations' (list of calculation objects).
            __calculation_id: An integer representing the next available ID for a calculation.
        
        Returns:
            None
        """
        if isinstance(parser, dict) and parser.get("error") is not None:
            error = parser["error"]
            message = f"Error while parsing {parser.get('source')}: {error}"
            self.get_print_window().add_message(message)
            logger.error(message, exc_info=(type(error), error, error.__traceback__))
            return
        if isinstance(parser, dict):
            calculation = parser.get("calculation")
            if calculation is None and parser.get("source") is not None:
                try:
                    calculation = parse_calculation(parser["source"])
                except Exception as exc:
                    message = f"Error while parsing {parser.get('source')}: {exc}"
                    self.get_print_window().add_message(message)
                    logger.error(message, exc_info=(type(exc), exc, exc.__traceback__))
                    return
        else:
            calculation = getattr(parser, "calculation", None)
            if calculation is None:
                try:
                    calculation = parser.parse()
                except Exception as exc:
                    message = f"Error while parsing calculation: {exc}"
                    self.get_print_window().add_message(message)
                    logger.error(message, exc_info=(type(exc), exc, exc.__traceback__))
                    return
        if calculation is None:
            message = "Parser finished without a calculation result."
            self.get_print_window().add_message(message)
            logger.error(message)
            return
        if calculation.errors.exist:
            self.get_print_window().add_message(calculation.errors.message)
            logger.error(f"Error in parsing {calculation.directory}: {calculation.errors.message}")
        else:
            id = -1
            for calc_id in range(self.__calculation_id):
                if calc_id not in self.__calculations:
                    id = calc_id
                    self.__calculations[id] = calculation_entry(calculation).as_legacy_dict()
                    break
            else:
                self.__calculation_id += 1
                id = self.__calculation_id
                self.__calculations[id] = calculation_entry(calculation).as_legacy_dict()
            
            calculation_type = calculation.properties.get("file_type", calculation.engine)
            self.TreeModel.append_data([([id, 'V', calculation.directory, calculation_type], 
                                         [(['', '', calculation.name, ''], None)])], self.TreeModel.root_item)
            self.TreeView.expandAll()
            selector = getattr(self, "AddedCalculations", None)
            if selector is not None and str(id) not in [selector.itemText(i) for i in range(selector.count())]:
                selector.addItem(str(id))
            self.calculation_folder = id
            self.get_print_window().add_message(f'File {self.__calculations[id]["calculations"][-1].name} appended.\n')
            self.__visual_window.load_calculation_info(self.__calculations[id])
            self.StepSlider.setMaximum(max(calculation_step_count(calculation) - 1, 0))
            self.StepSlider.setValue(0)
            self.__visual_window.set_frame_index(0)
            self.StepLabel.setText(f'Step:\t{self.__visual_window._step}\tfrom\t{self.StepSlider.maximum()}')
            logger.info(f"Calculation {calculation.name} parsed")

    def stop_all_threads_or_processes(self):
        """
        Stops all parser threads and processes.
        
        This method iterates through the lists of parser processes and threads,
        terminating each process and removing both processes and threads from
        their respective lists. It also calls `enable_parser_mode_changing()`
        after each process or thread is stopped.
        
        Args:
            self: The instance of the class.
        
        Initializes:
            __parser_processes: A list of parser processes. Processes are removed from this list when stopped.
            __parser_threads: A list of parser threads. Threads are removed from this list when stopped.
            __parser_objs: A list of parser objects associated with each process/thread. Objects are removed when the corresponding process/thread is stopped.
        
        Returns:
            None
        """
        for num, process in enumerate(self.__parser_processes.copy()):
            with self.__processes_locker:
                self.__parser_processes.pop(num)
                self.__parser_objs.pop(num)
                process.terminate()
            self.enable_parser_mode_changing()
        for num, thread in enumerate(self.__parser_threads.copy()):
            with self.__threads_locker:
                self.__parser_objs.pop(num)
                self.__parser_threads.pop(num)
            self.enable_parser_mode_changing()

    def delete_calculation(self):
        """
        Deletes the current calculation and updates the UI.
        
        This method removes the calculation associated with the current folder,
        updates the UI elements to reflect the deletion, and loads the next
        available calculation if any exist. If no calculations remain, it
        resets the UI to its initial state.
        
        Args:
         self: The instance of the class.
        
        Returns:
         None
        
        Class Fields Initialized:
         - `self.calculation_folder`: The name of the currently selected calculation folder.
         - `self.__visual_window`: An instance of a visual window class, used for displaying calculation information.
         - `self.StepSlider`: A slider control for selecting a step in the calculation.
         - `self.AddedCalculations`: A combo box listing the available calculations.
         - `self.__calculations`: A dictionary storing the available calculations, keyed by folder name.
         - `self.StepLabel`: A label displaying the current step.
        """
        self.stop_step_changing()
        self.__calculations.pop(self.calculation_folder, None)
        logger.info(f"Calculation {self.calculation_folder} deleted")
        if self.__calculations:
            folder_to_delete = self.calculation_folder
            self.calculation_folder = list(self.__calculations.keys())[-1]
            self.__visual_window.load_calculation_info(self.__calculations[self.calculation_folder])
            self.StepSlider.setMaximum(self._calculation_step_count(self.calculation_folder) - 1)
            self.get_print_window().add_message(f'Changed to {self.calculation_folder}.\n')
            self.AddedCalculations.setCurrentText(str(self.calculation_folder))
            index = [self.AddedCalculations.itemText(i) for i in range(self.AddedCalculations.count())].index(str(folder_to_delete))
            self.AddedCalculations.removeItem(index)
        else:
            self.calculation_folder = None
            self.__visual_window.without_calculation()
            self.StepSlider.setMaximum(100)
            self.AddedCalculations.removeItem(0)
            self.AddedCalculations.setCurrentText('Choose calculation to delete.')
        self.StepSlider.setValue(0)
        self.__visual_window.set_frame_index(0)
        self.StepLabel.setText(f'Step:\t{self.__visual_window._step}\tfrom\t{self.StepSlider.maximum()}')

    def change_active_calculation(self, *args):
        """
        Changes the active calculation folder and updates the visualization.
        
        This method stops the current step changing process, updates the active
        calculation folder based on the selected option in the AddedCalculations
        widget, loads the calculation information for the new folder into the
        visual window, updates the step slider, and adds a message to the print
        window indicating the change.
        
        Args:
         self: The instance of the class.
        
        Returns:
         None
        
        Class Fields Initialized:
         - `calculation_folder`: Stores the path to the currently active calculation folder.
         - `__visual_window`:  An instance of a visual window class, used for displaying calculation information.
         - `StepSlider`: A slider widget used to control the current step of the calculation.
         - `StepLabel`: A label widget displaying the current step.
         - `__calculations`: A dictionary storing calculation information for different folders.
         - `__visual_window._step`: The current step of the calculation displayed in the visual window.
        """
        self.stop_step_changing()
        new_calculation_folder = self.AddedCalculations.currentText()
        if new_calculation_folder != self.calculation_folder:
            self.calculation_folder = new_calculation_folder
            calculation_key = self._normalize_calculation_key(self.calculation_folder)
            self.__visual_window.load_calculation_info(self.__calculations[calculation_key])
            self.StepSlider.setMaximum(self._calculation_step_count(calculation_key) - 1)
            self.StepSlider.setValue(0)
            self.__visual_window.set_frame_index(0)
            self.StepLabel.setText(f'Step:\t{self.__visual_window._step}\tfrom\t{self.StepSlider.maximum()}')
            self.get_print_window().add_message(f'Changed to {self.calculation_folder}.\n')
            logger.info(f"Changed to {self.calculation_folder}")

    def processing_start(self):
        """
        Starts the processing based on the selected calculation folder.
        
         This method initializes the processing window with the appropriate settings and
         calculations, and displays it. It also stops any existing processing
         before starting a new one.
        
         Parameters:
          self - The instance of the class.
        
         Fields initialized:
          calculation_folder - The folder containing the calculations to be processed.
          __processing_window - An instance of the Processing class, responsible for
           performing the calculations and displaying the results.
        
         Returns:
          None
        """
        self.calculation_folder = self.AddedCalculations.currentText() if self.AddedCalculations.count() else self.calculation_folder
        calculation_key = self._normalize_calculation_key(self.calculation_folder)
        if self.__calculations.get(calculation_key, None) is not None:
            self.stop_all_threads_or_processes()
            calculation = self.__calculations[calculation_key]['calculations'][0]
            self.__processing_window = VRProcessing(None, self.__settings, self, self.__print_window,
                                                   self.__visual_window, calculation, str(calculation_key),
                                                   self.ADelete_coordinates_after_leave_cell.isChecked())
            self.__processing_window.show()

    def destroy_processing_window(self):
        """
        Destroys the processing window by setting it to None.
        
        This method is used to release resources associated with the processing window
        and signal that it is no longer active.
        
        Args:
            self: The instance of the class.
        
        Attributes Initialized:
            __processing_window:  Set to None, indicating the processing window is destroyed.
        
        Returns:
            None
        """
        self.__processing_window = None

    def oszicar_window(self):
        """
        Creates and displays the Oszicar window.
        
        This method stops all running threads or processes, initializes an Oszicar
        instance with the current directory path and settings, and then displays
        the Oszicar window.
        
        Args:
         self: The instance of the class.
        
        Returns:
         None
        
        Class Fields Initialized:
         - self.__oszicar_window: An instance of the Oszicar class, representing the
           main window for the application. It is initialized with the directory path,
           settings, and references to the main application instance, visual window,
           and print window.
        """
        self.stop_all_threads_or_processes()
        directory = self.__settings.get_control_params('browse_folder_path')
        calculation_key = self._normalize_calculation_key(self.calculation_folder)
        if calculation_key in self.__calculations:
            calculation = self.__calculations[calculation_key]['calculations'][0]
            directory = calculation.directory
        if directory is None:
            self.get_print_window().add_message("Load a calculation or choose a browse folder first.")
            return
        self.__oszicar_window = VROszicar(
            str(directory),
            None,
            self.__settings,
            self,
            self.__visual_window,
            self.__print_window,
        )
        self.__oszicar_window.show()

    def about_the_program(self):
        """
        Displays information about the PROCHEM program.
        
        This method presents a descriptive message about PROCHEM, its purpose,
        development timeline, and features. The message is added to the print
        window and logged for informational purposes.
        
        Args:
         self:  The instance of the class.
        
        Returns:
         None
        """
        message = '''PROCHEM is a program for processing and visualization the results of quantum chemistry packages' calculations. \
Have additional modes for simplify your life as more as it possible. \
It was developed at the end of 2021 and has undergone many changes and rebrending described in other features of the help menu.\n'''
        self.get_print_window().add_message(message)
        logger.info(f"About the program function called")

    def about_the_window(self):
        """
        Displays an about message describing the main window's features and key assignments.
        
        Args:
            self: The instance of the class.
        
        Returns:
            None
        """
        message = '''Main PROCHEM windows consists of control panel with the ability to add and delete calculations, \
processing them and use some additional modes such as work with supercomputer, parsing OSZICAR files, reading and work \
with POSCAR files and some others functions and visualizing of calculations window with changeable settings, such as \
lightning, background color, bounds draw and some others functions. Key assignments: +, - on keypad or keyboard or \
mouse scroll to zoom, a - to add an atom to the list, d - to remove an atom from the list, z - to move camera left, \
x - right, u - up, j - down, Backspace - return model to the first position, use arrows to rotate the model.\n'''
        self.get_print_window().add_message(message)
        logger.info(f"About the window function called")

    def lattest_update(self):
        """
        Displays the latest update message in the print window.
        
        Args:
            self: The instance of the class.
        
        Returns:
            None
        """
        message = '''\u262D ver. 1.0: \u262D\n\u2705 Global update:\n1. PROCHEM, consisting of several windows, \
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
        self.get_print_window.add_message(message)
        logger.info(f"Latest update function called")

    def changes_history(self):
        """
        Retrieves the changes history from a file and displays it.
        
        Reads the content of 'PreviousChanges.txt' and adds it as a message to the print window.
        
        Args:
         self:  The instance of the class.
        
        Returns:
         None
        """
        with codecs.open('PreviousChanges.txt', 'r', encoding='utf-8') as previous_changes_file:
            message = previous_changes_file.read()
            self.get_print_window().add_message(f'{message}\n')
        logger.info(f"Changes history function called")
