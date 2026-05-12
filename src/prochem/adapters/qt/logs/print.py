import os
import logging
from prochem.adapters.qt.opengl.control import ControlWindow
from prochem.adapters.qt.opengl.visual import VisualWindow
from prochem.adapters.qt.generated.print import Ui_Print, QMainWindow
logger = logging.getLogger(__name__)


class PrintWindow(Ui_Print, QMainWindow):
    """
    A window that manages application settings, project directory, and visual/control windows.
    
     Class Methods:
     - __init__:
    """
    def __init__(self, settings, project_directory):
        """
        Initializes the PrintWindow.
        
        Args:
            settings: Configuration settings for the application.
            project_directory: The directory of the current project.
        
        Initializes the following object properties:
            __settings: Stores the application settings.
            __project_directory: Stores the project directory path.
            __control_window:  A reference to the control window (initialized later).
            __visual_window: A reference to the visual window (initialized later).
        
        Returns:
            None
        """
        super(PrintWindow, self).__init__()
        self.__settings = settings
        self.__project_directory = project_directory
        self.__control_window = None
        self.__visual_window = None
        self.setupUi(self)
        logger.info(f"PrintUI setuped")
        
        self.__location = self.__settings.get_new_window_location('print')
        if self.__location is not None:
            self.move(self.__location[0], self.__location[1])
            logger.info(f"Print window positioned")
        self.awake_control_window()
        self.awake_visual_window()
        self.show()

    def get_settings(self):
        """
        Retrieves the application settings.
        
        Args:
            self: The instance of the class.
        
        Returns:
            The application settings.
        """
        return self.__settings
    
    def get_visual_window(self):
        """
        Returns the visual window.
        
        Args:
         self: The instance of the class.
        
        Returns:
         The visual window.
        """
        return self.__visual_window

    def get_control_window(self):
        """
        Returns the control window associated with this object.
        
        Args:
         self: The instance of the class.
        
        Returns:
         The control window.
        """
        return self.__control_window

    def get_project_dir(self):
        """
        Returns the project directory.
        
        Args:
         self: The instance of the class.
        
        Returns:
         str: The project directory path.
        """
        return self.__project_directory

    def link_elements_with_functions(self):
        """
        Links elements with their corresponding functions.
        
        This method establishes connections between elements and the functions
        that operate on them. It prepares the object for processing by
        associating elements with their intended functionalities.
        
        Args:
          self: The instance of the class.
        
        Returns:
          None
        """
        pass
    
    def add_message(self, message): 
        """
        Adds a message to the logger and prints it to the console.
        
        Args:
            self: The instance of the class.
            message: The message to be added to the logger.
        
        Returns:
            None
        """
        self.Logger.append(message)
        logger.info(f'{message} added to print window')

    def closeEvent(self, event):
        """
        Saves the window's position and settings before closing.
        
        Args:
         self: The instance of the class.
         event: The close event.
        
        Initializes:
         __settings: An instance used to manage application settings.
         __control_window: The control window instance.
         __visual_window: The visual window instance.
        
        Returns:
         None
        """
        self.__settings.set_new_window_location(self.pos().toTuple(), 'print')
        if self.__control_window.closed and self.__visual_window.closed:
            event.accept()
            logger.info(f"Print window closed")
            self.__settings.save_settings()
            logger.info(f"Settings saved")
        else:
            event.ignore()

    def awake_control_window(self):
        """
        Awakens and displays the control window.
        
        Args:
            self: The instance of the class.
        
        Returns:
            None
        
        Initializes the following class fields:
            __control_window: An instance of the ControlWindow class, responsible for the control window's UI and functionality.
        """
        self.__control_window = ControlWindow(self.get_settings(), self)
        self.__control_window.show()
        logger.info(f"Control window awaked")

    def awake_visual_window(self):
        """
        Awakens the visual window.
        
        This method creates and displays the visual window, linking it with the control window.
        
        Args:
            self: The instance of the class.
        
        Initializes:
            self.__visual_window: An instance of the VisualWindow class, responsible for displaying visual information. It's initialized with settings, the existing control window, and a reference to the current object.
            self.__control_window: The control window linked with the visual window.
        
        Returns:
            None
        """
        self.__visual_window = VisualWindow(self.get_settings(), self.get_visual_window(), self)
        self.__control_window.link_with_visual_window(self.get_visual_window())
        self.__visual_window.show()
        logger.info(f"Visual window awaked")
