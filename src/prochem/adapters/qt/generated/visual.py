from PySide6.QtCore import QCoreApplication, QLocale, QSize, Qt
from PySide6.QtGui import (QOpenGLContext, QSurfaceFormat,
    QCursor, QFont, QIcon, QImage)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from prochem.adapters.qt.generated.opengl_widget import GLWidget
from PySide6.QtWidgets import QMainWindow, QSizePolicy, QVBoxLayout, QWidget
import prochem.adapters.qt.generated.resource_rc


class Ui_Visual(object):
    """
    A class for managing the user interface of a visual application.
    
    Class Methods:
    - setupUi:
    """

    def setupUi(self, Visual, settings, project_directory):
        """
        Sets up the user interface.
        
        Args:
            Visual: The main window object.
            settings: Application settings.
            project_directory: The project directory path.
        
        Initializes and configures the main window and its central widget.
        Specifically, it sets the window's object name, size, size policy, minimum size,
        font, window icon, and locale. It also sets dock options for allowing tabbed and animated docks.
        A central widget (MainWidget) is created and a vertical layout (verticalLayout) is applied to it.
        An instance of GLWidget is created and added to the vertical layout.
        Finally, the central widget is set for the main window and the UI is retranslated.
        
        The `GLWidget` is initialized with the provided `settings` and `project_directory`.
        It sets up the OpenGL context, scene, and mouse tracking.
        
        Fields initialized:
            self.MainWidget: The central widget of the main window.
            self.verticalLayout: The vertical layout manager for the central widget.
            self.openGLWidget: An instance of GLWidget, which handles the OpenGL rendering.
        """
        if not Visual.objectName():
            Visual.setObjectName("Visual")
        Visual.resize(400, 300)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Visual.sizePolicy().hasHeightForWidth())
        Visual.setSizePolicy(sizePolicy)
        Visual.setMinimumSize(QSize(400, 300))
        font = QFont()
        font.setFamilies(["Times New Roman"])
        font.setPointSize(10)
        Visual.setFont(font)
        Visual.setWindowIcon(QIcon(":/icons/logo/PROCHEM-logo.ico"))
        Visual.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        Visual.setDockOptions(
            QMainWindow.DockOption.AllowTabbedDocks
            | QMainWindow.DockOption.AnimatedDocks
        )
        self.MainWidget = QWidget(Visual)
        self.MainWidget.setObjectName("MainWidget")
        sizePolicy.setHeightForWidth(self.MainWidget.sizePolicy().hasHeightForWidth())
        self.MainWidget.setSizePolicy(sizePolicy)
        self.MainWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.verticalLayout = QVBoxLayout(self.MainWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.openGLWidget = GLWidget(self.MainWidget, settings, project_directory)
        self.openGLWidget.setObjectName("openGLWidget")

        self.verticalLayout.addWidget(self.openGLWidget)

        Visual.setCentralWidget(self.MainWidget)

        self.retranslateUi(Visual)

    def retranslateUi(self, Visual):
        """
        Sets the window title of the given Visual object.
        
        Args:
          self:  The instance of the class.
          Visual: The main window object to retranslate.
        
        Returns:
          None
        """
        Visual.setWindowTitle(QCoreApplication.translate("Visual", "PROCHEM", None))
