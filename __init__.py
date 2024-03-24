import sys
from Logs.VRLogger import VRLogger
from Settings.Settings import VRSettings
from PySide6.QtWidgets import QApplication
from Logs.VRPrint import VRPrintWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    logger = VRLogger()
    settings_object = VRSettings(logger).load_settings()
    print_window = VRPrintWindow(app, settings_object, logger)
    print_window.show()
    settings_object.save_settings(logger)
    sys.exit(0)
