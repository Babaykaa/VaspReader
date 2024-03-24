from Logs.VRLogger import sendDataToLogger
from Visual.VRVisual import VRVisualWindow
from Visual.VROpenGL import VROpenGL
from Gui.VRPrintGUI import Ui_VRPrint, QMainWindow


class VRPrintWindow(Ui_VRPrint, QMainWindow):

    @sendDataToLogger
    def __init__(self, app, settings, logger):
        super(VRPrintWindow, self).__init__()
        self.__logger = logger
        self.__app = app
        self.__visual_window = None
        self._visual_window_closed = False
        self.__open_gl_window = None
        self.__settings = settings
        location = self.__settings.print_window_location
        self.setupUi(self)
        if location is not None:
            self.move(location[0], location[1])
        self.show()
        self.awake_visual_window()
        self.awake_open_gl_window()
        self.open_gl_mainloop()

    def get_logger(self):
        return self.__logger

    def insert_logs(self, window, operation, operation_type, result='SUCCESS'):
        self.__logger.insert_logs(window, operation, operation_type, result)

    def addMessage(self, message, from_window, operation=None, operation_type='program', result='SUCCESS'):
        toLogger = message if operation is None else operation
        message = message.split('\n')
        for line in message:
            self.Logger.append(f"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Times New Roman'; font-size:10pt; font-weight:696; color:#00e5e5; background-color:#000000\">{line}</span></p>\n")
        self.__logger.insert_logs(from_window, toLogger, operation_type, result)

    def link_elements_with_functions(self):
        pass

    @sendDataToLogger
    def closeEvent(self, event):
        if self._visual_window_closed:
            self.__settings.print_window_location = self.pos().toTuple()
            event.accept()
        else:
            event.ignore()

    @sendDataToLogger
    def awake_visual_window(self):
        self.__visual_window = VRVisualWindow(self.__app, self.__settings, self.__open_gl_window, self)
        self.__visual_window.show()

    @sendDataToLogger
    def awake_open_gl_window(self):
        self.__open_gl_window = VROpenGL(self.__app, self.__settings, self.__visual_window, self)
        self.__visual_window.link_with_open_gl_window(self.__open_gl_window)

    @sendDataToLogger
    def open_gl_mainloop(self):
        self.__open_gl_window.mainloop()
