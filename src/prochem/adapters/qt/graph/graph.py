import matplotlib

matplotlib.use("Qt5Agg")
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QApplication
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure
import prochem.adapters.qt.generated.resource_rc


class MplCanvas(FigureCanvasQTAgg):
    """
    Initializes the MplCanvas with a Matplotlib figure and axes.
    
    Args:
        parent: The parent widget.
        width: The width of the figure in inches.
        height: The height of the figure in inches.
        dpi: The dots per inch for the figure.
    
    Initializes the following class fields:
        axes: The Matplotlib axes object for plotting.
    
    Returns:
        None
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """
        Initializes the MplCanvas with a Matplotlib figure and axes.
        
        Args:
            parent: The parent widget.
            width: The width of the figure in inches.
            height: The height of the figure in inches.
            dpi: The dots per inch for the figure.
        
        Initializes the following class fields:
            axes: The Matplotlib axes object for plotting.
        
        Returns:
            None
        """
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class VRGraph(QMainWindow):
    """
    VRGraph is a class designed to visualize data using Matplotlib within a PyQt application.
     It sets up a window with a plot canvas and navigation toolbar for interactive data exploration.
    """

    def __init__(self, data):
        """
        Initializes the VRGraph with data and sets up the visualization.
        
        Args:
            data: The data to be plotted.
        
        Initializes the following object properties:
            windowIcon: The window icon, set to the VR logo.
            windowTitle: The title of the window, set to "VaspReader (Processing Window)".
            mplCanvas: An MplCanvas instance for plotting the data.
            navigationToolbar: A NavigationToolbar instance for interacting with the plot.
            centralWidget: The central widget of the main window, containing the toolbar and canvas.
        
        Returns:
            None
        """
        super(VRGraph, self).__init__()
        icon = QIcon()
        icon.addFile(":/VRlogo/VR-logo.ico", QSize(), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowTitle("VaspReader (Processing Window)")
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.figure.gca().spines["right"].set_visible(False)
        sc.figure.gca().spines["top"].set_visible(False)
        data.plot(ax=sc.axes, x=data.columns[0])

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(sc, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(sc)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.show()
