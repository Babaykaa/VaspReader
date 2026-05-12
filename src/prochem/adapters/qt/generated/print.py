from PySide6.QtCore import (QCoreApplication, QLocale, QRect, QSize, Qt)
from PySide6.QtGui import (QBrush, QColor, QFont, QIcon, QPalette)
from PySide6.QtWidgets import (QMainWindow, QSizePolicy, QTextEdit, QVBoxLayout, QWidget)
import prochem.adapters.qt.generated.resource_rc
import os


class Ui_Print(object):
    """
    A class to manage the user interface for a Print widget.
    
     This class handles the setup and translation of the UI elements for displaying
     print-related information and logs.
    """
    def setupUi(self, Print):
        """
        Sets up the user interface for the Print widget.
        
        Args:
            self: The instance of the class.
            Print: The Print widget to be configured.
        
        Initializes the following object properties:
            MainWidget: A QWidget instance serving as the central widget for layout management.
            Logger: A QTextEdit widget used for displaying log messages.
            verticalLayout: A QVBoxLayout instance used for vertical arrangement of widgets within MainWidget.
        """
        if not Print.objectName():
            Print.setObjectName("PROCHEM Print")
        Print.resize(450, 300)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Print.sizePolicy().hasHeightForWidth())
        Print.setSizePolicy(sizePolicy)
        Print.setMinimumSize(QSize(450, 300))
        palette = QPalette()
        brush = QBrush(QColor(0, 243, 243, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        brush1 = QBrush(QColor(154, 154, 154, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush1)
        brush2 = QBrush(QColor(229, 229, 229, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Light, brush2)
        brush3 = QBrush(QColor(227, 227, 227, 255))
        brush3.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Midlight, brush3)
        brush4 = QBrush(QColor(0, 234, 234, 255))
        brush4.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Text, brush4)
        brush5 = QBrush(QColor(170, 255, 255, 255))
        brush5.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.BrightText, brush5)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush4)
        brush6 = QBrush(QColor(0, 0, 0, 255))
        brush6.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush6)
        palette.setBrush(QPalette.Active, QPalette.Window, brush6)
        brush7 = QBrush(QColor(0, 77, 136, 255))
        brush7.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Highlight, brush7)
        brush8 = QBrush(QColor(0, 136, 136, 255))
        brush8.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.HighlightedText, brush8)
        brush9 = QBrush(QColor(85, 0, 0, 255))
        brush9.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.LinkVisited, brush9)
        brush10 = QBrush(QColor(107, 107, 107, 255))
        brush10.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush10)
        brush11 = QBrush(QColor(100, 100, 86, 255))
        brush11.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.ToolTipBase, brush11)
        brush12 = QBrush(QColor(0, 239, 239, 255))
        brush12.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.ToolTipText, brush12)
        brush13 = QBrush(QColor(0, 234, 234, 128))
        brush13.setStyle(Qt.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Active, QPalette.PlaceholderText, brush13)
#endif
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Light, brush2)
        palette.setBrush(QPalette.Inactive, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.BrightText, brush5)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush6)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush6)
        palette.setBrush(QPalette.Inactive, QPalette.Highlight, brush7)
        palette.setBrush(QPalette.Inactive, QPalette.HighlightedText, brush8)
        palette.setBrush(QPalette.Inactive, QPalette.LinkVisited, brush9)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush10)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush11)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush12)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush13)
#endif
        brush14 = QBrush(QColor(120, 120, 120, 255))
        brush14.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush14)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Light, brush2)
        palette.setBrush(QPalette.Disabled, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush14)
        palette.setBrush(QPalette.Disabled, QPalette.BrightText, brush5)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush14)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush6)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush6)
        brush15 = QBrush(QColor(0, 120, 215, 255))
        brush15.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Highlight, brush15)
        palette.setBrush(QPalette.Disabled, QPalette.HighlightedText, brush8)
        palette.setBrush(QPalette.Disabled, QPalette.LinkVisited, brush9)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush10)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush11)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush12)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush13)
#endif
        Print.setPalette(palette)
        font = QFont()
        font.setFamilies(["Times New Roman"])
        font.setPointSize(10)
        Print.setFont(font)
        Print.setContextMenuPolicy(Qt.DefaultContextMenu) 
        Print.setWindowIcon(QIcon("../icons/logo/PROCHEM-logo.ico"))
        
        style_sheet = ""
        with open(os.path.join(os.path.dirname(__file__), "style_sheets", "print.css")) as file:
            style_sheet = file.read()
        Print.setStyleSheet(style_sheet)
        
        Print.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        Print.setDockOptions(QMainWindow.AllowTabbedDocks|QMainWindow.AnimatedDocks)
        self.MainWidget = QWidget(Print)
        self.MainWidget.setObjectName("MainWidget")
        sizePolicy.setHeightForWidth(self.MainWidget.sizePolicy().hasHeightForWidth())
        self.MainWidget.setSizePolicy(sizePolicy)
        self.MainWidget.setContextMenuPolicy(Qt.NoContextMenu)
        self.verticalLayout = QVBoxLayout(self.MainWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.Logger = QTextEdit(self.MainWidget)
        self.Logger.setObjectName("Logger")
        self.Logger.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.Logger.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.Logger.setTextInteractionFlags(Qt.TextSelectableByKeyboard|Qt.TextSelectableByMouse)

        self.verticalLayout.addWidget(self.Logger)

        Print.setCentralWidget(self.MainWidget)

        self.retranslateUi(Print)

    def retranslateUi(self, Print):
        """
        Translates UI elements for the Print window.
        
        This method sets the window title and HTML content of the Logger widget
        to provide localized text.
        
        Args:
           self: The instance of the class.
           Print: The main Print window object.
        
        Returns:
           None
        """
        Print.setWindowTitle(QCoreApplication.translate("PROCHEM Print", u"PROCHEM (Message Console)", None))
        self.Logger.setHtml(QCoreApplication.translate("PROCHEM Print", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Times New Roman'; font-size:10pt; font-weight:696; color:#00e5e5; background-color:#000000;\">VaspReader for Windows 11 (64-bit), ver. 1.0.3 (created: 20.02.2022, lat.ver. 30.08.2022)</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Times New Roman'; font-size:10pt; font-weight:696; col"
                        "or:#00e5e5; background-color:#000000;\">Email questions, suggestions and bug reports to: solovykh.aa19@physics.msu.ru</span></p></body></html>", None))
