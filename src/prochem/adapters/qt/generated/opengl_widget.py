from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QImage, QSurfaceFormat, QOpenGLContext
from PySide6.QtCore import QTimer, Qt
from prochem.adapters.qt.opengl.shaders.shaders import Shaders
from prochem.adapters.qt.opengl.scene import Scene
import logging
import os
import OpenGL
from OpenGL.GL import *

OpenGL.ERROR_CHECKING = False
logger = logging.getLogger(__name__)


class GLWidget(QOpenGLWidget):
    """
    Initializes the OpenGL widget.
    
    Args:
        parent: The parent widget.
        settings: Application settings.
        project_directory: The project directory.
    
    Initializes the following object properties:
        __settings: Stores the application settings.
        __project_directory: Stores the project directory.
        __program: Stores the OpenGL program (shader). Initialized to None.
        __scene: Stores the scene object. Initialized to None.
        __mouse_x_pos: Stores the x-coordinate of the mouse position. Initialized to 0.
        __mouse_y_pos: Stores the y-coordinate of the mouse position. Initialized to 0.
        __trace_mouse: A boolean flag indicating whether to trace mouse movement. Initialized to False.
        __mouse_dx: Stores the change in x-coordinate of the mouse. Initialized to 0.
        __mouse_dy: Stores the change in y-coordinate of the mouse. Initialized to 0.
        __timer: A QTimer object used to trigger updates.
    
    Returns:
        None
    """
    def __init__(self, parent=None, settings=None, project_directory=None):
        """
        Initializes the OpenGL widget.
        
        Args:
            parent: The parent widget.
            settings: Application settings.
            project_directory: The project directory.
        
        Initializes the following object properties:
            __settings: Stores the application settings.
            __project_directory: Stores the project directory.
            __program: Stores the OpenGL program (shader). Initialized to None.
            __scene: Stores the scene object. Initialized to None.
            __mouse_x_pos: Stores the x-coordinate of the mouse position. Initialized to 0.
            __mouse_y_pos: Stores the y-coordinate of the mouse position. Initialized to 0.
            __trace_mouse: A boolean flag indicating whether to trace mouse movement. Initialized to False.
            __mouse_dx: Stores the change in x-coordinate of the mouse. Initialized to 0.
            __mouse_dy: Stores the change in y-coordinate of the mouse. Initialized to 0.
            __timer: A QTimer object used to trigger updates.
        
        Returns:
            None
        """
        super().__init__(parent)
        self.set_minimal_supported_format() # TODO check how to set once minimal supported format and create context
        context = QOpenGLContext()
        context.create()

        self.__settings = settings
        self.__project_directory = project_directory
        self.__program = None
        self.__scene = None

        self.__mouse_x_pos, self.__mouse_y_pos = 0, 0
        self.__trace_mouse = False
        self.__mouse_dx, self.__mouse_dy = 0, 0
        
        # self.__rotation_matrix = np.array([[-1.0, 0.0, 0.0, 0.0],
        #                                    [0.0, 0.0, 1.0, 0],
        #                                    [0.0, -1.0, 0.0, 0.0],
        #                                    [0.0, 0.0, 0.0, 1.0]], dtype=np.float32)

        self.__timer = QTimer()
        self.__timer.timeout.connect(self.update)

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def initializeGL(self):
        """
        Initializes the OpenGL context.
        
        This method sets up essential OpenGL settings, compiles shaders,
        creates a scene, loads a texture, and starts a timer for rendering.
        
        Args:
           self: The instance of the class.
        
        Class Fields Initialized:
           __settings: An instance of a settings class, used to configure the scene and rendering parameters.
           __program: An instance of the Shaders class, responsible for compiling and managing shaders.
           __scene: An instance of the Scene class, representing the 3D scene to be rendered.
           __timer: A timer object used to control the rendering frequency.
        
        Returns:
           None
        """
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glLineWidth(3.0)
        self.__settings.set_scene_params(self.width() / self.height(), 'view', 'perspective', 'aspect')
        self.__program = Shaders(os.path.join(self.__project_directory, 'visual', 'shaders'), [r'vertex.glsl', r'fragment.glsl'], ['VERTEX', 'FRAGMENT'])
        self.__scene = Scene(self.__settings)
        self.__scene.load_texture(":/icons/logo/PROCHEM-logo.png")
        # self.__scene.set_draw_buffer({'Sphere': {((0.2, 0, 0.5), 1.0): [[0, 0, 0], [1, 1, 1], [2, 2, 2]]}})
        self.__timer.start(16)

    def resizeGL(self, w: int, h: int):
        """
        Resizes the OpenGL viewport and updates scene parameters.
        
        Args:
         self: The object instance.
         w: The new width of the viewport.
         h: The new height of the viewport.
        
        Returns:
         None
        
        Fields initialized:
         None
        """
        glViewport(0, 0, w, h)
        self.__settings.set_scene_params(w / h, 'view', 'perspective', 'aspect')
        if self.__scene is not None:
            self.__scene.update_camera()

    def paintGL(self):
        """
        Renders the scene using the current OpenGL program.
        
        Args:
         self: The instance of the class.
        
        Returns:
         None
        
        Class Fields Initialized:
         - __program: The OpenGL program to use for rendering.
         - __scene: The scene to be rendered.
         - __trace_mouse: A boolean indicating whether to trace the mouse.
        """
        if self.__program:
            glUseProgram(self.__program.program)
            self.__scene.draw(self.__program, self.__trace_mouse)
            glUseProgram(0)

    def keyPressEvent(self, event):
        """
        Handles key press events to manipulate the 3D scene.
        
        Args:
         self: The instance of the class.
         event: The key press event object.
        
        This method responds to specific key presses to rotate, scale, and move
        the 3D scene. It also propagates the event to the parent widget.
        """
        key = event.key()
        match key:
            case Qt.Key_Up:
                self.__scene.rotate(-2, 0, 0)
            case Qt.Key_Down:
                self.__scene.rotate(2, 0, 0)
            case Qt.Key_Left:
                self.__scene.rotate(0, -2, 0)
            case Qt.Key_Right:
                self.__scene.rotate(0, 2, 0)
            case Qt.Key_Q:
                self.__scene.rotate(0, 0, 2)
            case Qt.Key_E:
                self.__scene.rotate(0, 0, -2)
            case Qt.Key_Backspace:
                self.__scene.reset_scene_matrices()
            case Qt.Key_Equal:
                self.__scene.scale(1.02)
            case Qt.Key_Minus:
                self.__scene.scale(0.98)
            case Qt.Key_J:
                self.__scene.move_y(-0.1)
            case Qt.Key_K:
                self.__scene.move_y(0.1)
            case Qt.Key_L:
                self.__scene.move_x(0.1)
            case Qt.Key_H:
                self.__scene.move_x(-0.1)
            case Qt.Key_N:
                self.__scene.move_z(0.1)
            case Qt.Key_M:
                self.__scene.move_z(-0.1)
        self.parent().keyPressEvent(event)

    def mouseMoveEvent(self, event):
        """
        Rotates the scene based on mouse movement.
        
         This method handles mouse move events and rotates the 3D scene
         based on the change in mouse position.  It updates internal
         mouse position variables and calls the scene's rotate method.
        
         Parameters:
          self: The instance of the class.
          event: The mouse move event object.
        
         Returns:
          None
         
        
         Class Fields Initialized:
          __mouse_dx: The difference in x-coordinate between the current and previous mouse positions.
          __mouse_dy: The difference in y-coordinate between the current and previous mouse positions.
          __mouse_x_pos: The current x-coordinate of the mouse.
          __mouse_y_pos: The current y-coordinate of the mouse.
          __scene: The 3D scene object being rotated.
        """
        if self.__trace_mouse:
            self.__mouse_dx = event.x() - self.__mouse_x_pos
            self.__mouse_dy = event.y() - self.__mouse_y_pos
           
            self.__scene.rotate(self.__mouse_dy * 0.2, self.__mouse_dx * 0.2, 0)

            self.__mouse_x_pos = event.x()
            self.__mouse_y_pos = event.y()
   
    def mousePressEvent(self, event):
        """
        Captures the mouse click position and enables mouse tracking.
        
        Args:
         self: The instance of the class.
         event: The mouse press event object.
        
        Initializes:
         __mouse_x_pos: The x-coordinate of the mouse click.
         __mouse_y_pos: The y-coordinate of the mouse click.
         __trace_mouse: A boolean flag indicating whether to trace mouse movements.
        
        Returns:
         None
        """
        self.__mouse_x_pos = event.x()
        self.__mouse_y_pos = event.y()
        self.__trace_mouse = True

    def mouseReleaseEvent(self, event):
        """
        Stops tracing the mouse movement.
        
        Args:
         self: The object instance.
         event: The mouse release event.
        
        Initializes:
         __trace_mouse: A boolean flag indicating whether mouse movement tracing is active. Set to False to stop tracing.
        
        Returns:
         None.
        """
        self.__trace_mouse = False

    def set_program(self, program):
        """
        Sets the program to be executed.
        
        Args:
            program: The program to be set.
        
        Attributes:
            __program: The program to be executed.
        
        Returns:
            None.
        """
        self.__program = program

    def set_settings(self, settings):
        """
        Sets the settings for the object.
        
        Args:
         settings: The settings to apply.
        
        Initializes:
         self.__settings: Stores the provided settings.
        
        Returns:
         None.
        """
        self.__settings = settings

    def set_minimal_supported_format(self):
        """
        Sets the minimal supported OpenGL format.
        
         This method configures the default OpenGL surface format to ensure
         compatibility and desired rendering features. It sets the renderable
         type to OpenGL, requests version 4.3, enables the core profile, and
         sets a depth buffer size of 24 bits.
        
         Parameters:
          self - The instance of the class.
        
         Returns:
          None
        """
        format = QSurfaceFormat()
        format.setRenderableType(QSurfaceFormat.RenderableType.OpenGL)
        format.setVersion(4, 3)  # Request OpenGL 4.3
        format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        format.setDepthBufferSize(24)
        QSurfaceFormat.setDefaultFormat(format)
