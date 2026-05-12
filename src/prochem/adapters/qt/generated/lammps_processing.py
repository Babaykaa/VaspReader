# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'VRLAMMPSProcessingwIbQPJ.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QHeaderView,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QTableView,
    QVBoxLayout, QWidget)
import prochem.adapters.qt.generated.resource_rc

class Ui_VRLAMMPSProcessing(object):
    """
    A class for managing the user interface of the VRLAMMPSProcessing application.
    
    This class handles the setup and translation of the UI elements, 
    providing a visual interface for LAMMPS data processing.
    """
    def setupUi(self, VRLAMMPSProcessing):
        """
        Sets up the user interface for the VRLAMMPSProcessing application.
        
        This method configures the main window, layouts, widgets, and actions
        for the application. It sets up the visual elements and their
        interactions.
        
        Args:
            self: The instance of the class.
            VRLAMMPSProcessing: The main application window.
        
        Fields Initialized:
            AAbout: QAction for the "About" menu item.
            ABack: QAction for the "Back" menu item.
            AExit: QAction for the "Exit" menu item.
            centralwidget: QWidget serving as the central widget of the main window.
            verticalLayout: QVBoxLayout managing the vertical layout of widgets.
            Top1Layout: QHBoxLayout managing the horizontal layout for path editing and buttons.
            PathEdit: QLineEdit for entering the file path.
            BrowseButton: QPushButton for browsing files.
            AddButton: QPushButton for adding files.
            horizontalLayout_3: QHBoxLayout managing the horizontal layout for regular expression selection and submission.
            RegularExprChoose: QComboBox for selecting a regular expression.
            SubmitReButton: QPushButton for submitting the selected regular expression.
            TableView: QTableView for displaying data.
            BottomLayout: QHBoxLayout managing the horizontal layout for buttons at the bottom.
            CreateExcelButton: QPushButton for creating an Excel file.
            BuildGraphsButton: QPushButton for building graphs.
            BackButton: QPushButton for going back.
            horizontalSpacer: QSpacerItem for adding horizontal space.
            menubar: QMenuBar for the main menu.
            Window: QMenu for the "Window" menu.
        """
        if not VRLAMMPSProcessing.objectName():
            VRLAMMPSProcessing.setObjectName(u"VRLAMMPSProcessing")
        VRLAMMPSProcessing.resize(800, 600)
        VRLAMMPSProcessing.setMinimumSize(QSize(400, 400))
        VRLAMMPSProcessing.setStyleSheet(u"QLineEdit{\n"
"  border-radius: 8px;\n"
"  border: 2px solid #000000;\n"
"  padding: 3px 3px;\n"
"}\n"
"QLineEdit:focus {\n"
"  border: 3px solid rgb(75, 75, 75);\n"
"}\n"
"QLineEdit:disabled {\n"
"border-radius: 8px;\n"
"padding: 3px 3px;  \n"
"border: 2px solid rgb(75, 75, 75);\n"
"background-color:rgb(150, 150, 150);\n"
"}\n"
"QLineEdit::placeholder {\n"
"  color: #000000;\n"
"}\n"
"QPushButton {\n"
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
"  bord"
                        "er: 1px solid #000000;\n"
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
"    padding: 0px 1"
                        "px;\n"
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
"}\n"
"QLabel{\n"
"background-color: rgb(255, 240, 202);\n"
"color: black;\n"
"font-weight: 600;\n"
"height:28px;}\n"
"QCheckBox{\n"
"  border-radius: 6px;\n"
"  border: 2px solid #000000;\n"
"  padding: 3px 3px;\n"
"}\n"
"QRadioButton{\n"
"  border-radius: 6px;\n"
"  border: 2px solid #000000;\n"
"  padding: 3px 3px;\n"
"}\n"
"\n"
"QScrollBar:vertical {\n"
"    border-radius: 6px;\n"
"    border: 2px solid rgb(0, 0, 0);\n"
"	color: rgb(0, 0, 0);\n"
"    background: rgb(182, 182, 182);\n"
"    width: 16px;\n"
"    margin: 23px 0 23px 0;\n"
"}\n"
"QScrollBar::handle:vertical {\n"
"    background: rgb(0, 203, 203);\n"
"    min-height: 18px;\n"
"    border-radius: 5px;\n"
"}\n"
"QScrollBar::handle:hover:vertical {\n"
"    background: rgb(255, 255, 255);\n"
""
                        "}\n"
"QScrollBar::add-line:vertical {\n"
"    border: 1.5px solid rgb(0, 0, 0);\n"
"    border-radius: 6px;\n"
"    background: rgb(0, 203, 203);\n"
"    height: 18px;\n"
"    subcontrol-position: bottom;\n"
"    subcontrol-origin: margin;\n"
"}\n"
"QScrollBar::sub-line:vertical {\n"
"    border: 1.5px solid rgb(0, 0, 0);\n"
"    border-radius: 6px;\n"
"    background: rgb(0, 203, 203);\n"
"    height: 18px;\n"
"    subcontrol-position: top;\n"
"    subcontrol-origin: margin;\n"
"}\n"
"QScrollBar::add-line:hover:vertical, QScrollBar::sub-line:hover:vertical {\n"
"    background: rgb(255, 255, 255);\n"
"}\n"
"QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
"    border: 1px solid rgb(0, 0, 0);\n"
"    border-radius: 2px;\n"
"    width: 3.5px;\n"
"    height: 3.5px;\n"
"    background: rgb(255, 255, 255);\n"
"}\n"
"QScrollBar::up-arrow:vertical:hover, QScrollBar::down-arrow:vertical:hover {\n"
"    background: rgb(0, 203, 203);\n"
"}\n"
"\n"
"QScrollBar::add-page:vertical, QScrollBar::sub-page"
                        ":vertical {\n"
"    background: none;\n"
"}\n"
"\n"
"QScrollBar:horizontal {\n"
"    border-radius: 6px;\n"
"    border: 2px solid rgb(0, 0, 0);\n"
"	color: rgb(0, 0, 0);\n"
"    background: rgb(182, 182, 182);\n"
"    height: 16px;\n"
"    margin: 0 23px 0 23px;\n"
"}\n"
"QScrollBar::handle:horizontal {\n"
"    background: rgb(0, 203, 203);\n"
"    min-width: 18px;\n"
"    border-radius: 5px;\n"
"}\n"
"QScrollBar::handle:hover:horizontal {\n"
"    background: rgb(255, 255, 255);\n"
"}\n"
"QScrollBar::add-line:horizontal {\n"
"    border: 1.5px solid rgb(0, 0, 0);\n"
"    border-radius: 6px;\n"
"    background: rgb(0, 203, 203);\n"
"    width: 18px;\n"
"    subcontrol-position: right;\n"
"    subcontrol-origin: margin;\n"
"}\n"
"QScrollBar::sub-line:horizontal {\n"
"    border: 1.5px solid rgb(0, 0, 0);\n"
"    border-radius: 6px;\n"
"    background: rgb(0, 203, 203);\n"
"    width: 18px;\n"
"    subcontrol-position: left;\n"
"    subcontrol-origin: margin;\n"
"}\n"
"QScrollBar::add-line:hover:horizontal, QScr"
                        "ollBar::sub-line:hover:horizontal {\n"
"    background: rgb(255, 255, 255);\n"
"}\n"
"QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {\n"
"    border: 1px solid rgb(0, 0, 0);\n"
"    border-radius: 2px;\n"
"    width: 3.5px;\n"
"    height: 3.5px;\n"
"    background: rgb(255, 255, 255);\n"
"}\n"
"QScrollBar::left-arrow:horizontal:hover, QScrollBar::right-arrow:horizontal:hover {\n"
"    background: rgb(0, 203, 203);\n"
"}\n"
"\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {\n"
"    background: none;\n"
"}")
        VRLAMMPSProcessing.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.AAbout = QAction(VRLAMMPSProcessing)
        self.AAbout.setObjectName(u"AAbout")
        self.ABack = QAction(VRLAMMPSProcessing)
        self.ABack.setObjectName(u"ABack")
        self.AExit = QAction(VRLAMMPSProcessing)
        self.AExit.setObjectName(u"AExit")
        self.centralwidget = QWidget(VRLAMMPSProcessing)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.Top1Layout = QHBoxLayout()
        self.Top1Layout.setObjectName(u"Top1Layout")
        self.PathEdit = QLineEdit(self.centralwidget)
        self.PathEdit.setObjectName(u"PathEdit")

        self.Top1Layout.addWidget(self.PathEdit)

        self.BrowseButton = QPushButton(self.centralwidget)
        self.BrowseButton.setObjectName(u"BrowseButton")

        self.Top1Layout.addWidget(self.BrowseButton)

        self.AddButton = QPushButton(self.centralwidget)
        self.AddButton.setObjectName(u"AddButton")

        self.Top1Layout.addWidget(self.AddButton)

        self.Top1Layout.setStretch(0, 5)
        self.Top1Layout.setStretch(1, 1)
        self.Top1Layout.setStretch(2, 1)

        self.verticalLayout.addLayout(self.Top1Layout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.RegularExprChoose = QComboBox(self.centralwidget)
        self.RegularExprChoose.setObjectName(u"RegularExprChoose")

        self.horizontalLayout_3.addWidget(self.RegularExprChoose)

        self.SubmitReButton = QPushButton(self.centralwidget)
        self.SubmitReButton.setObjectName(u"SubmitReButton")

        self.horizontalLayout_3.addWidget(self.SubmitReButton)

        self.horizontalLayout_3.setStretch(0, 245)
        self.horizontalLayout_3.setStretch(1, 100)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.TableView = QTableView(self.centralwidget)
        self.TableView.setObjectName(u"TableView")

        self.verticalLayout.addWidget(self.TableView)

        self.BottomLayout = QHBoxLayout()
        self.BottomLayout.setObjectName(u"BottomLayout")
        self.CreateExcelButton = QPushButton(self.centralwidget)
        self.CreateExcelButton.setObjectName(u"CreateExcelButton")

        self.BottomLayout.addWidget(self.CreateExcelButton)

        self.BuildGraphsButton = QPushButton(self.centralwidget)
        self.BuildGraphsButton.setObjectName(u"BuildGraphsButton")

        self.BottomLayout.addWidget(self.BuildGraphsButton)

        self.BackButton = QPushButton(self.centralwidget)
        self.BackButton.setObjectName(u"BackButton")

        self.BottomLayout.addWidget(self.BackButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.BottomLayout.addItem(self.horizontalSpacer)

        self.BottomLayout.setStretch(0, 2)
        self.BottomLayout.setStretch(1, 2)
        self.BottomLayout.setStretch(2, 2)
        self.BottomLayout.setStretch(3, 6)

        self.verticalLayout.addLayout(self.BottomLayout)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 20)
        self.verticalLayout.setStretch(3, 1)
        VRLAMMPSProcessing.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(VRLAMMPSProcessing)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        self.Window = QMenu(self.menubar)
        self.Window.setObjectName(u"Window")
        VRLAMMPSProcessing.setMenuBar(self.menubar)

        self.menubar.addAction(self.Window.menuAction())
        self.Window.addAction(self.AAbout)
        self.Window.addSeparator()
        self.Window.addAction(self.ABack)
        self.Window.addSeparator()
        self.Window.addAction(self.AExit)

        self.retranslateUi(VRLAMMPSProcessing)

        QMetaObject.connectSlotsByName(VRLAMMPSProcessing)
    # setupUi

    def retranslateUi(self, VRLAMMPSProcessing):
        """
        Translates UI elements for the VRLAMMPSProcessing window.
        
        This method sets the text labels for various UI elements within the
        VRLAMMPSProcessing window, ensuring the application is localized.
        
        Args:
          self: The instance of the class.
          VRLAMMPSProcessing: The main window object for LAMMPS processing.
        
        Returns:
          None
        """
        VRLAMMPSProcessing.setWindowTitle(QCoreApplication.translate("VRLAMMPSProcessing", u"VaspReader (LAMMPS Processing)", None))
        self.AAbout.setText(QCoreApplication.translate("VRLAMMPSProcessing", u"About", None))
        self.ABack.setText(QCoreApplication.translate("VRLAMMPSProcessing", u"Back", None))
        self.AExit.setText(QCoreApplication.translate("VRLAMMPSProcessing", u"Exit", None))
        self.PathEdit.setText(QCoreApplication.translate("VRLAMMPSProcessing", u"Directory", None))
        self.BrowseButton.setText(QCoreApplication.translate("VRLAMMPSProcessing", u"Browse", None))
        self.AddButton.setText(QCoreApplication.translate("VRLAMMPSProcessing", u"Add", None))
        self.SubmitReButton.setText(QCoreApplication.translate("VRLAMMPSProcessing", u"Submit", None))
        self.CreateExcelButton.setText(QCoreApplication.translate("VRLAMMPSProcessing", u"Create Excel", None))
        self.BuildGraphsButton.setText(QCoreApplication.translate("VRLAMMPSProcessing", u"Build Graphs", None))
        self.BackButton.setText(QCoreApplication.translate("VRLAMMPSProcessing", u"Back", None))
        self.Window.setTitle(QCoreApplication.translate("VRLAMMPSProcessing", u"Window", None))
    # retranslateUi

