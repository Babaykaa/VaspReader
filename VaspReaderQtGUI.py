from QT_GUI.VRVisualGUI import Ui_VRVisual
from QT_GUI.VRPrintGUI import Ui_VRPrint
from QT_GUI.VRPoscarGUI import Ui_VRPoscar
from QT_GUI.VROszicarGUI import Ui_VROszicar
from QT_GUI.VRGraphProcessingGUI import Ui_VRGraphProcessing
from QT_GUI.VRProcessingGUI import Ui_VRProcessing
from QT_GUI.VRChoosePoscarGUI import Ui_ChooseFileWindow
from QT_GUI.VRAuthSupercomputerGUI import Ui_VRAuthSupercomputer
from QT_GUI.VRRewriteFileGUI import Ui_RewriteFile
from QT_GUI.VRTransferredGUI import Ui_VRTransferProgress
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QFile


class VRGUI(QMainWindow):
    def __init__(self, GUI_type):
        super(VRGUI, self).__init__()
        self.ui = GUI_type()
        self.ui.setupUi(self)

    def __repr__(self):
        return f'Window object: {self.ui}.'


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = VRGUI(Ui_VRVisual)
    window.show()

    sys.exit(app.exec())


# core_test = VRGUI(processing_GUI, title='TEST', resizable=True).testloop()
