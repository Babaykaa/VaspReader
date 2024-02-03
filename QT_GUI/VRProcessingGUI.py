# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'VRProcessingGUIjPApKL.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QHBoxLayout, QHeaderView, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QMenu, QMenuBar,
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QTabWidget, QTableView, QVBoxLayout, QWidget)
import QT_GUI.Resource_rc

class Ui_VRProcessing(object):
    def setupUi(self, VRProcessing):
        if not VRProcessing.objectName():
            VRProcessing.setObjectName(u"VRProcessing")
        VRProcessing.resize(1080, 657)
        font = QFont()
        font.setFamilies([u"Times New Roman"])
        font.setPointSize(10)
        VRProcessing.setFont(font)
        icon = QIcon()
        icon.addFile(u":/VRlogo/VR-logo.ico", QSize(), QIcon.Normal, QIcon.Off)
        VRProcessing.setWindowIcon(icon)
        VRProcessing.setStyleSheet(u"QLineEdit{\n"
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
"}\n"
"QPushButton:hover {\n"
"  background-color: rgb(255, 212, 137);\n"
"  border: 1px solid #000000;\n"
"}\n"
"QPushButton:pressed {"
                        "\n"
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
"    padding: 0px 1px;\n"
"    border: 0px solid #000000;\n"
"    border-radius: 8px;\n"
"	background"
                        "-color: rgb(255, 232, 216);\n"
"}\n"
"QComboBox:pressed {\n"
"	background-color: rgb(255, 250, 237);\n"
"}\n"
"QFrame{\n"
"  border: 2px solid #000000;\n"
"  border-radius: 5px;\n"
"}\n"
"QScrollArea{border: none;}\n"
"QScrollBar{background: white; border-radius: 5px;}\n"
"QScrollBar:horizontal{height: 8px;}\n"
"QScrollBar:vertical{width: 8px; background:white;}\n"
"QScrollBar::handle{background: rgb(0, 203, 203); border-radius: 4px; width: 4px}\n"
"QScrollBar::handle:horizontal{height: 25px; min-width: 10px;}\n"
"QScrollBar::handle:vertical{width: 25px; min-height: 10px;}\n"
"QScrollBar::add-line{border: none;background: none;}\n"
"QScrollBar::sub-line{border: none; background: none;}\n"
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
"}")
        self.AAbout = QAction(VRProcessing)
        self.AAbout.setObjectName(u"AAbout")
        self.ABack = QAction(VRProcessing)
        self.ABack.setObjectName(u"ABack")
        self.AExit = QAction(VRProcessing)
        self.AExit.setObjectName(u"AExit")
        self.ADel_coords_of_sel_atoms = QAction(VRProcessing)
        self.ADel_coords_of_sel_atoms.setObjectName(u"ADel_coords_of_sel_atoms")
        self.ADel_coords_of_sel_atoms.setCheckable(True)
        self.ADel_coords_of_sel_atoms.setChecked(True)
        self.ADel_energy_of_sel_atoms = QAction(VRProcessing)
        self.ADel_energy_of_sel_atoms.setObjectName(u"ADel_energy_of_sel_atoms")
        self.ADel_energy_of_sel_atoms.setCheckable(True)
        self.AInclude_OSZICAR = QAction(VRProcessing)
        self.AInclude_OSZICAR.setObjectName(u"AInclude_OSZICAR")
        self.AInclude_OSZICAR.setCheckable(True)
        self.APreview_of_table = QAction(VRProcessing)
        self.APreview_of_table.setObjectName(u"APreview_of_table")
        self.APreview_of_table.setCheckable(True)
        self.APreview_of_table.setChecked(True)
        self.ASelected_atoms = QAction(VRProcessing)
        self.ASelected_atoms.setObjectName(u"ASelected_atoms")
        self.ASelected_atoms.setEnabled(False)
        self.AOSZICAR = QAction(VRProcessing)
        self.AOSZICAR.setObjectName(u"AOSZICAR")
        self.AOSZICAR.setEnabled(False)
        self.ATable = QAction(VRProcessing)
        self.ATable.setObjectName(u"ATable")
        self.ATable.setEnabled(False)
        self.MainProcessingWidget = QWidget(VRProcessing)
        self.MainProcessingWidget.setObjectName(u"MainProcessingWidget")
        self.verticalLayout = QVBoxLayout(self.MainProcessingWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, -1, -1, -1)
        self.CentralWidget = QWidget(self.MainProcessingWidget)
        self.CentralWidget.setObjectName(u"CentralWidget")
        self.horizontalLayout = QHBoxLayout(self.CentralWidget)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(9, -1, -1, -1)
        self.LeftCentralWidget = QWidget(self.CentralWidget)
        self.LeftCentralWidget.setObjectName(u"LeftCentralWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LeftCentralWidget.sizePolicy().hasHeightForWidth())
        self.LeftCentralWidget.setSizePolicy(sizePolicy)
        self.LeftCentralWidget.setMinimumSize(QSize(320, 500))
        self.verticalLayout_2 = QVBoxLayout(self.LeftCentralWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, -1, 9, -1)
        self.LeftCentralVSpacer1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.LeftCentralVSpacer1)

        self.ProcessingTab = QTabWidget(self.LeftCentralWidget)
        self.ProcessingTab.setObjectName(u"ProcessingTab")
        self.ProcessingTab.setTabShape(QTabWidget.Rounded)
        self.ProcessingTab.setDocumentMode(True)
        self.DCPM = QWidget()
        self.DCPM.setObjectName(u"DCPM")
        self.verticalLayoutWidget = QWidget(self.DCPM)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 301, 391))
        self.DCPMVLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.DCPMVLayout.setSpacing(14)
        self.DCPMVLayout.setObjectName(u"DCPMVLayout")
        self.DCPMVLayout.setContentsMargins(8, 8, 10, 18)
        self.DCPMList = QListWidget(self.verticalLayoutWidget)
        self.DCPMList.setObjectName(u"DCPMList")

        self.DCPMVLayout.addWidget(self.DCPMList)

        self.DCPMSelected = QLineEdit(self.verticalLayoutWidget)
        self.DCPMSelected.setObjectName(u"DCPMSelected")
        self.DCPMSelected.setEnabled(False)

        self.DCPMVLayout.addWidget(self.DCPMSelected)

        self.DCPMRadioLayout = QHBoxLayout()
        self.DCPMRadioLayout.setObjectName(u"DCPMRadioLayout")
        self.DistanceRadio = QRadioButton(self.verticalLayoutWidget)
        self.DistanceRadio.setObjectName(u"DistanceRadio")
        self.DistanceRadio.setChecked(True)

        self.DCPMRadioLayout.addWidget(self.DistanceRadio)

        self.COMRadio = QRadioButton(self.verticalLayoutWidget)
        self.COMRadio.setObjectName(u"COMRadio")

        self.DCPMRadioLayout.addWidget(self.COMRadio)

        self.PlusRadio = QRadioButton(self.verticalLayoutWidget)
        self.PlusRadio.setObjectName(u"PlusRadio")

        self.DCPMRadioLayout.addWidget(self.PlusRadio)

        self.MinusRadio = QRadioButton(self.verticalLayoutWidget)
        self.MinusRadio.setObjectName(u"MinusRadio")

        self.DCPMRadioLayout.addWidget(self.MinusRadio)

        self.DCPMRadioLayout.setStretch(0, 1)
        self.DCPMRadioLayout.setStretch(1, 1)
        self.DCPMRadioLayout.setStretch(2, 1)
        self.DCPMRadioLayout.setStretch(3, 1)

        self.DCPMVLayout.addLayout(self.DCPMRadioLayout)

        self.DCMPAddCol = QPushButton(self.verticalLayoutWidget)
        self.DCMPAddCol.setObjectName(u"DCMPAddCol")
        self.DCMPAddCol.setEnabled(False)

        self.DCPMVLayout.addWidget(self.DCMPAddCol)

        self.DCPMAdded = QComboBox(self.verticalLayoutWidget)
        self.DCPMAdded.setObjectName(u"DCPMAdded")
        self.DCPMAdded.setEnabled(False)

        self.DCPMVLayout.addWidget(self.DCPMAdded)

        self.DCPMRemoveCol = QPushButton(self.verticalLayoutWidget)
        self.DCPMRemoveCol.setObjectName(u"DCPMRemoveCol")
        self.DCPMRemoveCol.setEnabled(False)

        self.DCPMVLayout.addWidget(self.DCPMRemoveCol)

        self.DCPMVLayout.setStretch(0, 2)
        self.ProcessingTab.addTab(self.DCPM, "")
        self.Angle = QWidget()
        self.Angle.setObjectName(u"Angle")
        self.verticalLayoutWidget_2 = QWidget(self.Angle)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(0, 0, 301, 391))
        self.AngleVLayout = QVBoxLayout(self.verticalLayoutWidget_2)
        self.AngleVLayout.setSpacing(14)
        self.AngleVLayout.setObjectName(u"AngleVLayout")
        self.AngleVLayout.setContentsMargins(8, 8, 10, 18)
        self.AngleList = QListWidget(self.verticalLayoutWidget_2)
        self.AngleList.setObjectName(u"AngleList")

        self.AngleVLayout.addWidget(self.AngleList)

        self.AngleSelected = QLineEdit(self.verticalLayoutWidget_2)
        self.AngleSelected.setObjectName(u"AngleSelected")
        self.AngleSelected.setEnabled(False)

        self.AngleVLayout.addWidget(self.AngleSelected)

        self.AnglePlaneSelectLayout = QHBoxLayout()
        self.AnglePlaneSelectLayout.setObjectName(u"AnglePlaneSelectLayout")
        self.AnglePlaneXY = QCheckBox(self.verticalLayoutWidget_2)
        self.AnglePlaneXY.setObjectName(u"AnglePlaneXY")

        self.AnglePlaneSelectLayout.addWidget(self.AnglePlaneXY)

        self.AnglePlaneYZ = QCheckBox(self.verticalLayoutWidget_2)
        self.AnglePlaneYZ.setObjectName(u"AnglePlaneYZ")

        self.AnglePlaneSelectLayout.addWidget(self.AnglePlaneYZ)

        self.AnglePlaneZX = QCheckBox(self.verticalLayoutWidget_2)
        self.AnglePlaneZX.setObjectName(u"AnglePlaneZX")

        self.AnglePlaneSelectLayout.addWidget(self.AnglePlaneZX)


        self.AngleVLayout.addLayout(self.AnglePlaneSelectLayout)

        self.AngleAddCol = QPushButton(self.verticalLayoutWidget_2)
        self.AngleAddCol.setObjectName(u"AngleAddCol")
        self.AngleAddCol.setEnabled(False)

        self.AngleVLayout.addWidget(self.AngleAddCol)

        self.AngleAdded = QComboBox(self.verticalLayoutWidget_2)
        self.AngleAdded.setObjectName(u"AngleAdded")
        self.AngleAdded.setEnabled(False)

        self.AngleVLayout.addWidget(self.AngleAdded)

        self.AngleRemoveCol = QPushButton(self.verticalLayoutWidget_2)
        self.AngleRemoveCol.setObjectName(u"AngleRemoveCol")
        self.AngleRemoveCol.setEnabled(False)

        self.AngleVLayout.addWidget(self.AngleRemoveCol)

        self.AngleVLayout.setStretch(0, 2)
        self.ProcessingTab.addTab(self.Angle, "")
        self.Divide = QWidget()
        self.Divide.setObjectName(u"Divide")
        self.verticalLayoutWidget_3 = QWidget(self.Divide)
        self.verticalLayoutWidget_3.setObjectName(u"verticalLayoutWidget_3")
        self.verticalLayoutWidget_3.setGeometry(QRect(0, 0, 301, 391))
        self.DivideVLayout = QVBoxLayout(self.verticalLayoutWidget_3)
        self.DivideVLayout.setSpacing(14)
        self.DivideVLayout.setObjectName(u"DivideVLayout")
        self.DivideVLayout.setContentsMargins(8, 8, 10, 18)
        self.DivideList = QListWidget(self.verticalLayoutWidget_3)
        self.DivideList.setObjectName(u"DivideList")

        self.DivideVLayout.addWidget(self.DivideList)

        self.DivideSelected = QLineEdit(self.verticalLayoutWidget_3)
        self.DivideSelected.setObjectName(u"DivideSelected")
        self.DivideSelected.setEnabled(False)

        self.DivideVLayout.addWidget(self.DivideSelected)

        self.DivideAddCol = QPushButton(self.verticalLayoutWidget_3)
        self.DivideAddCol.setObjectName(u"DivideAddCol")
        self.DivideAddCol.setEnabled(False)

        self.DivideVLayout.addWidget(self.DivideAddCol)

        self.DivideAdded = QComboBox(self.verticalLayoutWidget_3)
        self.DivideAdded.setObjectName(u"DivideAdded")
        self.DivideAdded.setEnabled(False)

        self.DivideVLayout.addWidget(self.DivideAdded)

        self.DivideRemoveCol = QPushButton(self.verticalLayoutWidget_3)
        self.DivideRemoveCol.setObjectName(u"DivideRemoveCol")
        self.DivideRemoveCol.setEnabled(False)

        self.DivideVLayout.addWidget(self.DivideRemoveCol)

        self.DivideVLayout.setStretch(0, 2)
        self.ProcessingTab.addTab(self.Divide, "")
        self.Rename = QWidget()
        self.Rename.setObjectName(u"Rename")
        self.verticalLayoutWidget_4 = QWidget(self.Rename)
        self.verticalLayoutWidget_4.setObjectName(u"verticalLayoutWidget_4")
        self.verticalLayoutWidget_4.setGeometry(QRect(0, 0, 301, 391))
        self.RenameVLayout = QVBoxLayout(self.verticalLayoutWidget_4)
        self.RenameVLayout.setSpacing(14)
        self.RenameVLayout.setObjectName(u"RenameVLayout")
        self.RenameVLayout.setContentsMargins(8, 8, 10, 18)
        self.RenameSelect = QComboBox(self.verticalLayoutWidget_4)
        self.RenameSelect.setObjectName(u"RenameSelect")

        self.RenameVLayout.addWidget(self.RenameSelect)

        self.RenameLine = QLineEdit(self.verticalLayoutWidget_4)
        self.RenameLine.setObjectName(u"RenameLine")
        self.RenameLine.setEnabled(False)

        self.RenameVLayout.addWidget(self.RenameLine)

        self.RenameButton = QPushButton(self.verticalLayoutWidget_4)
        self.RenameButton.setObjectName(u"RenameButton")
        self.RenameButton.setEnabled(False)

        self.RenameVLayout.addWidget(self.RenameButton)

        self.RenameVSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.RenameVLayout.addItem(self.RenameVSpacer)

        self.RenameBottomLayout = QHBoxLayout()
        self.RenameBottomLayout.setObjectName(u"RenameBottomLayout")
        self.RenameHSpacer1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.RenameBottomLayout.addItem(self.RenameHSpacer1)

        self.RenameLogoWidget = QWidget(self.verticalLayoutWidget_4)
        self.RenameLogoWidget.setObjectName(u"RenameLogoWidget")
        self.RenameLogoWidget.setMaximumSize(QSize(100, 100))
        self.RenameLogoWidget.setStyleSheet(u"QWidget{image:url(:/VRlogo/VR-logo.ico);}")

        self.RenameBottomLayout.addWidget(self.RenameLogoWidget)

        self.RenameHSpacer2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.RenameBottomLayout.addItem(self.RenameHSpacer2)

        self.RenameBottomLayout.setStretch(0, 1)
        self.RenameBottomLayout.setStretch(1, 2)
        self.RenameBottomLayout.setStretch(2, 1)

        self.RenameVLayout.addLayout(self.RenameBottomLayout)

        self.RenameVLayout.setStretch(0, 1)
        self.RenameVLayout.setStretch(1, 1)
        self.RenameVLayout.setStretch(2, 1)
        self.RenameVLayout.setStretch(4, 20)
        self.ProcessingTab.addTab(self.Rename, "")

        self.verticalLayout_2.addWidget(self.ProcessingTab)

        self.LeftCentralVSpacer2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.LeftCentralVSpacer2)

        self.verticalLayout_2.setStretch(0, 1)
        self.verticalLayout_2.setStretch(1, 30)
        self.verticalLayout_2.setStretch(2, 3)

        self.horizontalLayout.addWidget(self.LeftCentralWidget)

        self.ViewTable = QTableView(self.CentralWidget)
        self.ViewTable.setObjectName(u"ViewTable")
        self.ViewTable.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ViewTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ViewTable.setDragDropMode(QAbstractItemView.NoDragDrop)

        self.horizontalLayout.addWidget(self.ViewTable)

        self.horizontalLayout.setStretch(0, 8)
        self.horizontalLayout.setStretch(1, 18)

        self.verticalLayout.addWidget(self.CentralWidget)

        self.LowerButtonsWidget = QHBoxLayout()
        self.LowerButtonsWidget.setObjectName(u"LowerButtonsWidget")
        self.LowerButtonsWidget.setContentsMargins(16, 8, 8, 8)
        self.CreateExcel = QPushButton(self.MainProcessingWidget)
        self.CreateExcel.setObjectName(u"CreateExcel")

        self.LowerButtonsWidget.addWidget(self.CreateExcel)

        self.BuildGraph = QPushButton(self.MainProcessingWidget)
        self.BuildGraph.setObjectName(u"BuildGraph")

        self.LowerButtonsWidget.addWidget(self.BuildGraph)

        self.Back = QPushButton(self.MainProcessingWidget)
        self.Back.setObjectName(u"Back")

        self.LowerButtonsWidget.addWidget(self.Back)

        self.LowerButtonsWidgetSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.LowerButtonsWidget.addItem(self.LowerButtonsWidgetSpacer)

        self.LowerButtonsWidget.setStretch(0, 1)
        self.LowerButtonsWidget.setStretch(1, 1)
        self.LowerButtonsWidget.setStretch(2, 1)
        self.LowerButtonsWidget.setStretch(3, 7)

        self.verticalLayout.addLayout(self.LowerButtonsWidget)

        VRProcessing.setCentralWidget(self.MainProcessingWidget)
        self.ProcessingMenubar = QMenuBar(VRProcessing)
        self.ProcessingMenubar.setObjectName(u"ProcessingMenubar")
        self.ProcessingMenubar.setGeometry(QRect(0, 0, 1080, 22))
        self.ProcessingMenuWindow = QMenu(self.ProcessingMenubar)
        self.ProcessingMenuWindow.setObjectName(u"ProcessingMenuWindow")
        self.ProcessingMenuOptions = QMenu(self.ProcessingMenubar)
        self.ProcessingMenuOptions.setObjectName(u"ProcessingMenuOptions")
        VRProcessing.setMenuBar(self.ProcessingMenubar)

        self.ProcessingMenubar.addAction(self.ProcessingMenuWindow.menuAction())
        self.ProcessingMenubar.addAction(self.ProcessingMenuOptions.menuAction())
        self.ProcessingMenuWindow.addAction(self.AAbout)
        self.ProcessingMenuWindow.addSeparator()
        self.ProcessingMenuWindow.addAction(self.ABack)
        self.ProcessingMenuWindow.addSeparator()
        self.ProcessingMenuWindow.addAction(self.AExit)
        self.ProcessingMenuOptions.addAction(self.ASelected_atoms)
        self.ProcessingMenuOptions.addSeparator()
        self.ProcessingMenuOptions.addAction(self.ADel_coords_of_sel_atoms)
        self.ProcessingMenuOptions.addAction(self.ADel_energy_of_sel_atoms)
        self.ProcessingMenuOptions.addSeparator()
        self.ProcessingMenuOptions.addAction(self.AOSZICAR)
        self.ProcessingMenuOptions.addSeparator()
        self.ProcessingMenuOptions.addAction(self.AInclude_OSZICAR)
        self.ProcessingMenuOptions.addSeparator()
        self.ProcessingMenuOptions.addAction(self.ATable)
        self.ProcessingMenuOptions.addSeparator()
        self.ProcessingMenuOptions.addAction(self.APreview_of_table)

        self.retranslateUi(VRProcessing)

        self.ProcessingTab.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(VRProcessing)
    # setupUi

    def retranslateUi(self, VRProcessing):
        VRProcessing.setWindowTitle(QCoreApplication.translate("VRProcessing", u"VaspReader (Processing Window)", None))
        self.AAbout.setText(QCoreApplication.translate("VRProcessing", u"About", None))
        self.ABack.setText(QCoreApplication.translate("VRProcessing", u"Back", None))
        self.AExit.setText(QCoreApplication.translate("VRProcessing", u"Exit", None))
        self.ADel_coords_of_sel_atoms.setText(QCoreApplication.translate("VRProcessing", u"Delete coords", None))
        self.ADel_energy_of_sel_atoms.setText(QCoreApplication.translate("VRProcessing", u"Delete energy", None))
        self.AInclude_OSZICAR.setText(QCoreApplication.translate("VRProcessing", u"Add to table", None))
        self.APreview_of_table.setText(QCoreApplication.translate("VRProcessing", u"Show", None))
        self.ASelected_atoms.setText(QCoreApplication.translate("VRProcessing", u"Selected atoms", None))
        self.AOSZICAR.setText(QCoreApplication.translate("VRProcessing", u"OSZICAR", None))
        self.ATable.setText(QCoreApplication.translate("VRProcessing", u"Table", None))
        self.DistanceRadio.setText(QCoreApplication.translate("VRProcessing", u"Distance", None))
        self.COMRadio.setText(QCoreApplication.translate("VRProcessing", u"COM", None))
        self.PlusRadio.setText(QCoreApplication.translate("VRProcessing", u"+", None))
        self.MinusRadio.setText(QCoreApplication.translate("VRProcessing", u"-", None))
        self.DCMPAddCol.setText(QCoreApplication.translate("VRProcessing", u"Add Column", None))
        self.DCPMRemoveCol.setText(QCoreApplication.translate("VRProcessing", u"Remove Column", None))
        self.ProcessingTab.setTabText(self.ProcessingTab.indexOf(self.DCPM), QCoreApplication.translate("VRProcessing", u"Distance|COM|+|-", None))
        self.AnglePlaneXY.setText(QCoreApplication.translate("VRProcessing", u"xy", None))
        self.AnglePlaneYZ.setText(QCoreApplication.translate("VRProcessing", u"yz", None))
        self.AnglePlaneZX.setText(QCoreApplication.translate("VRProcessing", u"zx", None))
        self.AngleAddCol.setText(QCoreApplication.translate("VRProcessing", u"Add Column", None))
        self.AngleRemoveCol.setText(QCoreApplication.translate("VRProcessing", u"Remove Column", None))
        self.ProcessingTab.setTabText(self.ProcessingTab.indexOf(self.Angle), QCoreApplication.translate("VRProcessing", u"Angle", None))
        self.DivideAddCol.setText(QCoreApplication.translate("VRProcessing", u"Add Column", None))
        self.DivideRemoveCol.setText(QCoreApplication.translate("VRProcessing", u"Remove Column", None))
        self.ProcessingTab.setTabText(self.ProcessingTab.indexOf(self.Divide), QCoreApplication.translate("VRProcessing", u"Divide", None))
        self.RenameButton.setText(QCoreApplication.translate("VRProcessing", u"Rename", None))
        self.ProcessingTab.setTabText(self.ProcessingTab.indexOf(self.Rename), QCoreApplication.translate("VRProcessing", u"Rename", None))
        self.CreateExcel.setText(QCoreApplication.translate("VRProcessing", u"Create Excel", None))
        self.BuildGraph.setText(QCoreApplication.translate("VRProcessing", u"Build Graph", None))
        self.Back.setText(QCoreApplication.translate("VRProcessing", u"Back", None))
        self.ProcessingMenuWindow.setTitle(QCoreApplication.translate("VRProcessing", u"Window", None))
        self.ProcessingMenuOptions.setTitle(QCoreApplication.translate("VRProcessing", u"Options", None))
    # retranslateUi

