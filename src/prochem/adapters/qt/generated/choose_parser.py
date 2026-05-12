# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'VRChooseParserzKIMwf.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)
import prochem.adapters.qt.generated.resource_rc

class Ui_VRParserChoose(QMainWindow):
    """
    A class for managing the user interface of the VR parser selection window.
    
    This class sets up the UI elements, links them to corresponding functions, and handles
    the display of the VR parser selection window.
    """

    def __init__(self):
        """
        Initializes the Ui_VRParserChoose object.
        
        This constructor calls the superclass constructor, sets up the user interface,
        links UI elements to their corresponding functions, and displays the window.
        
        Args:
            self: The instance of the Ui_VRParserChoose class.
        
        Initializes the following object properties:
            setupUi: Sets up the user interface elements.
            link_elements_with_functions: Connects UI elements to their respective functions.
        
        Returns:
            None
        """
        super(Ui_VRParserChoose, self).__init__()
        self.setupUi(self)
        self.link_elements_with_functions()
        self.show()


    def setupUi(self, VRParserChoose):
        """
        Sets up the user interface for the VRParserChoose window.
        
        Args:
           VRParserChoose: The main window object.
        
        Class Fields Initialized:
           centralwidget: A QWidget instance that serves as the central widget of the window.
           verticalLayout: A QVBoxLayout that arranges widgets vertically within the central widget.
           ChooseMethodBox: A QComboBox widget that allows the user to select a parsing method.
           horizontalLayout: A QHBoxLayout that arranges widgets horizontally within the central widget.
           horizontalSpacer: A QSpacerItem that provides horizontal spacing within the horizontal layout.
           SubmitButton: A QPushButton widget that submits the selected parsing method.
           CancelButton: A QPushButton widget that cancels the operation.
        
        Returns:
           None
        """
        if not VRParserChoose.objectName():
            VRParserChoose.setObjectName(u"VRParserChoose")
        VRParserChoose.resize(400, 100)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(VRParserChoose.sizePolicy().hasHeightForWidth())
        VRParserChoose.setSizePolicy(sizePolicy)
        VRParserChoose.setMinimumSize(QSize(400, 100))
        VRParserChoose.setMaximumSize(QSize(400, 100))
        VRParserChoose.setFocusPolicy(Qt.NoFocus)
        icon = QIcon()
        icon.addFile(u":/VRlogo/VR-logo.ico", QSize(), QIcon.Normal, QIcon.Off)
        VRParserChoose.setWindowIcon(icon)
        VRParserChoose.setStyleSheet(u"QPushButton {\n"
"  background-color: rgb(255, 240, 202);\n"
"  color: black;\n"
"  font-weight: 600;\n"
"  border-radius: 8px;\n"
"  border: 2px solid rgb(85, 0, 127);\n"
"  border-style: outset;\n"
"  padding: 3px 3px;\n"
"  margin-top: 0px;\n"
"  outline: 0px;\n"
"}\n"
"QPushButton:disabled {\n"
"border-radius: 8px;\n"
"padding: 3px 3px;\n"
"color: black;\n"
"font-weight: 600;\n"
"border-radius: 8px;\n"
"border: 2px solid rgb(75, 75, 75);\n"
"background-color:rgb(150, 150, 150);\n"
"margin-top: 0px;\n"
"outline: 0px;\n"
"border-style: outset;\n"
"}\n"
"QPushButton:hover {\n"
"  background-color: rgb(255, 212, 137);\n"
"  border: 1px solid #000000;\n"
"  border-style: outset;\n"
"}\n"
"QPushButton:pressed {\n"
"background-color: white;\n"
"border: 3px solid #000000\n"
"}\n"
"QComboBox {\n"
"  border-radius: 8px;\n"
"  border: 2px solid #000000;\n"
"  padding: 3px 3px;\n"
"}\n"
"QComboBox:disabled {\n"
"border-radius: 8px;\n"
"padding: 3px 3px;\n"
"border-radius: 8px;\n"
"border: 2px solid rgb(75, 75, 75);\n"
""
                        "background-color:rgb(150, 150, 150);\n"
"}\n"
"QComboBox::drop-down {\n"
"  width: 18px;\n"
"  height:22px;\n"
"  padding: 0px 1px;\n"
"  border: 1px solid #000000;\n"
"  border-radius: 8px;\n"
"}\n"
"QComboBox::down-arrow {\n"
"  image: url(:/down-arrow_ico/down-arrow.ico);\n"
"  width: 18px;\n"
"  height:22px;\n"
"}\n"
"QComboBox::down-arrow:hover {\n"
"    width: 18px;\n"
"    height:22px;\n"
"    padding: 0px 1px;\n"
"    border: 1px solid #000000;\n"
"    border-radius: 8px;\n"
"	background-color: rgb(255, 229, 162);\n"
"}\n"
"QComboBox::down-arrow:pressed {\n"
"    width: 18px;\n"
"    height:22px;\n"
"    padding: 0px 1px;\n"
"    border: 0px solid #000000;\n"
"    border-radius: 8px;\n"
"	background-color: rgb(255, 232, 216);\n"
"}\n"
"QComboBox:pressed {\n"
"	background-color: rgb(255, 250, 237);\n"
"}\n"
"QFrame{\n"
"  border: 2px solid #000000;\n"
"  border-radius: 5px;\n"
"}")
        self.centralwidget = QWidget(VRParserChoose)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 16, -1, -1)
        self.ChooseMethodBox = QComboBox(self.centralwidget)
        self.ChooseMethodBox.setObjectName(u"ChooseMethodBox")

        self.verticalLayout.addWidget(self.ChooseMethodBox)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 12, -1, -1)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.SubmitButton = QPushButton(self.centralwidget)
        self.SubmitButton.setObjectName(u"SubmitButton")

        self.horizontalLayout.addWidget(self.SubmitButton)

        self.CancelButton = QPushButton(self.centralwidget)
        self.CancelButton.setObjectName(u"CancelButton")

        self.horizontalLayout.addWidget(self.CancelButton)

        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 1)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout.setStretch(0, 5)
        self.verticalLayout.setStretch(1, 1)
        VRParserChoose.setCentralWidget(self.centralwidget)

        self.retranslateUi(VRParserChoose)

        QMetaObject.connectSlotsByName(VRParserChoose)
    # setupUi

    def link_elements_with_functions(self):
        """
        Links HTML elements with their corresponding functions.
        
        This method iterates through HTML elements and associates them with functions
        based on predefined criteria. It updates the element's attributes to reflect
        this linkage, enabling dynamic behavior when the element is interacted with.
        
        Args:
            self: The instance of the class.
        
        Returns:
            None
        """
        ...

    def retranslateUi(self, VRParserChoose):
        """
        Sets the text for various UI elements.
        
        This method translates and sets the window title, submit button text,
        and cancel button text for the VRParserChoose window.
        
        Args:
           self:  The instance of the class.
           VRParserChoose: The main window object for the VRParserChoose dialog.
        
        Returns:
           None
        """
        VRParserChoose.setWindowTitle(QCoreApplication.translate("VRParserChoose", u"VaspReader", None))
        self.SubmitButton.setText(QCoreApplication.translate("VRParserChoose", u"Submit", None))
        self.CancelButton.setText(QCoreApplication.translate("VRParserChoose", u"Cancel", None))
    # retranslateUi

