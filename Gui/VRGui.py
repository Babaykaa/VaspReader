import sys
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QApplication
from Gui.VRProcessingGUI import Ui_VRProcessing


class VRGui(QMainWindow, Ui_VRProcessing):

    def __init__(self):
        super(VRGui, self).__init__()
        self.setupUi(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VRGui()
    window.show()
    sys.exit(app.exec())
