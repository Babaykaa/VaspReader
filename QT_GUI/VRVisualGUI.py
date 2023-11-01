# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'VRVisualGUIhYBPSM.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QHBoxLayout, QLineEdit, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSlider,
    QSpacerItem, QTabWidget, QVBoxLayout, QWidget)
import Resource_rc

class Ui_VaspReader(object):
    def setupUi(self, VaspReader):
        if not VaspReader.objectName():
            VaspReader.setObjectName(u"VaspReader")
        VaspReader.resize(480, 212)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(VaspReader.sizePolicy().hasHeightForWidth())
        VaspReader.setSizePolicy(sizePolicy)
        VaspReader.setMinimumSize(QSize(480, 212))
        VaspReader.setMaximumSize(QSize(1440, 636))
        icon = QIcon()
        icon.addFile(u"../VR_icons/VR-logo.ico", QSize(), QIcon.Normal, QIcon.Off)
        VaspReader.setWindowIcon(icon)
        VaspReader.setAutoFillBackground(True)
        VaspReader.setStyleSheet(u"QLineEdit{\n"
"  border-radius: 8px;\n"
"  border: 2px solid #000000;\n"
"  padding: 3px 3px;\n"
"}\n"
"QLineEdit:focus {\n"
"  border: 3px solid rgb(75, 75, 75);\n"
"}\n"
"\n"
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
"QPushButton:hover {\n"
"  background-color: rgb(255, 212, 137);\n"
"  border: 1px solid #000000;\n"
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
"QComboBox::drop-down {\n"
"  width: 18px;\n"
"  height:22px;\n"
"  padding: 0px 1px;\n"
"  border: 1px solid #000000;\n"
"  border-radius: 8px;\n"
"}\n"
"QComboBox::down-arrow {\n"
"  image: url(:/down-arrow_ico/down-arrow.ico);\n"
"  width:"
                        " 18px;\n"
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
        VaspReader.setInputMethodHints(Qt.ImhNone)
        VaspReader.setToolButtonStyle(Qt.ToolButtonIconOnly)
        VaspReader.setTabShape(QTabWidget.Rounded)
        VaspReader.setDockNestingEnabled(False)
        VaspReader.setUnifiedTitleAndToolBarOnMac(False)
        self.actionOpen_calculation = QAction(VaspReader)
        self.actionOpen_calculation.setObjectName(u"actionOpen_calculation")
        font = QFont()
        font.setFamilies([u"Times New Roman"])
        font.setPointSize(10)
        self.actionOpen_calculation.setFont(font)
        self.actionLoad_Calculation_State = QAction(VaspReader)
        self.actionLoad_Calculation_State.setObjectName(u"actionLoad_Calculation_State")
        self.actionLoad_Calculation_State.setFont(font)
        self.actionSave_Calculation_State = QAction(VaspReader)
        self.actionSave_Calculation_State.setObjectName(u"actionSave_Calculation_State")
        self.actionSave_Calculation_State.setFont(font)
        self.actionLoad_Configuration = QAction(VaspReader)
        self.actionLoad_Configuration.setObjectName(u"actionLoad_Configuration")
        self.actionLoad_Configuration.setFont(font)
        self.actionSave_Configuration = QAction(VaspReader)
        self.actionSave_Configuration.setObjectName(u"actionSave_Configuration")
        self.actionSave_Configuration.setFont(font)
        self.actionExit = QAction(VaspReader)
        self.actionExit.setObjectName(u"actionExit")
        self.actionExit.setFont(font)
        self.actionAxes = QAction(VaspReader)
        self.actionAxes.setObjectName(u"actionAxes")
        self.actionAxes.setCheckable(True)
        self.actionAxes.setChecked(True)
        self.actionCell_boarder = QAction(VaspReader)
        self.actionCell_boarder.setObjectName(u"actionCell_boarder")
        self.actionCell_boarder.setCheckable(True)
        self.actionCell_boarder.setChecked(True)
        self.actionBonds = QAction(VaspReader)
        self.actionBonds.setObjectName(u"actionBonds")
        self.actionChange_background = QAction(VaspReader)
        self.actionChange_background.setObjectName(u"actionChange_background")
        self.actionDelete_coordinates_after_leave_cell = QAction(VaspReader)
        self.actionDelete_coordinates_after_leave_cell.setObjectName(u"actionDelete_coordinates_after_leave_cell")
        self.actionDelete_coordinates_after_leave_cell.setCheckable(True)
        self.actionDelete_coordinates_after_leave_cell.setChecked(True)
        self.actionDelete_coordinates_after_leave_cell.setFont(font)
        self.actionLight_1 = QAction(VaspReader)
        self.actionLight_1.setObjectName(u"actionLight_1")
        self.actionLight_1.setFont(font)
        self.actionLight_2 = QAction(VaspReader)
        self.actionLight_2.setObjectName(u"actionLight_2")
        self.actionLight_2.setFont(font)
        self.actionLight_3 = QAction(VaspReader)
        self.actionLight_3.setObjectName(u"actionLight_3")
        self.actionLight_3.setFont(font)
        self.actionLight_4 = QAction(VaspReader)
        self.actionLight_4.setObjectName(u"actionLight_4")
        self.actionLight_4.setFont(font)
        self.actionLight_5 = QAction(VaspReader)
        self.actionLight_5.setObjectName(u"actionLight_5")
        self.actionLight_5.setFont(font)
        self.actionLight_6 = QAction(VaspReader)
        self.actionLight_6.setObjectName(u"actionLight_6")
        self.actionLight_6.setFont(font)
        self.actionLight_7 = QAction(VaspReader)
        self.actionLight_7.setObjectName(u"actionLight_7")
        self.actionLight_7.setFont(font)
        self.actionLight_8 = QAction(VaspReader)
        self.actionLight_8.setObjectName(u"actionLight_8")
        self.actionLight_8.setFont(font)
        self.actionProvessing = QAction(VaspReader)
        self.actionProvessing.setObjectName(u"actionProvessing")
        self.actionOSZICAR = QAction(VaspReader)
        self.actionOSZICAR.setObjectName(u"actionOSZICAR")
        self.actionPOSCAR = QAction(VaspReader)
        self.actionPOSCAR.setObjectName(u"actionPOSCAR")
        self.actionCHGCAR = QAction(VaspReader)
        self.actionCHGCAR.setObjectName(u"actionCHGCAR")
        self.actionIR_and_RAMAN = QAction(VaspReader)
        self.actionIR_and_RAMAN.setObjectName(u"actionIR_and_RAMAN")
        self.actionSupercomputer = QAction(VaspReader)
        self.actionSupercomputer.setObjectName(u"actionSupercomputer")
        self.actionGraphs = QAction(VaspReader)
        self.actionGraphs.setObjectName(u"actionGraphs")
        self.actionKeyboard = QAction(VaspReader)
        self.actionKeyboard.setObjectName(u"actionKeyboard")
        self.actionMouse_keyboard = QAction(VaspReader)
        self.actionMouse_keyboard.setObjectName(u"actionMouse_keyboard")
        self.actionAtom_ID = QAction(VaspReader)
        self.actionAtom_ID.setObjectName(u"actionAtom_ID")
        self.actionBond = QAction(VaspReader)
        self.actionBond.setObjectName(u"actionBond")
        self.actionValence_angle = QAction(VaspReader)
        self.actionValence_angle.setObjectName(u"actionValence_angle")
        self.actionScreenshot = QAction(VaspReader)
        self.actionScreenshot.setObjectName(u"actionScreenshot")
        self.actionForm_POSCAR = QAction(VaspReader)
        self.actionForm_POSCAR.setObjectName(u"actionForm_POSCAR")
        self.actionAbout_the_program = QAction(VaspReader)
        self.actionAbout_the_program.setObjectName(u"actionAbout_the_program")
        self.actionWindow_description = QAction(VaspReader)
        self.actionWindow_description.setObjectName(u"actionWindow_description")
        self.actionLatest_update = QAction(VaspReader)
        self.actionLatest_update.setObjectName(u"actionLatest_update")
        self.actionChanges_history = QAction(VaspReader)
        self.actionChanges_history.setObjectName(u"actionChanges_history")
        self.centralwidget = QWidget(VaspReader)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setSpacing(8)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, 12, -1, -1)
        self.step_widget = QWidget(self.centralwidget)
        self.step_widget.setObjectName(u"step_widget")
        self.horizontalLayout = QHBoxLayout(self.step_widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_2 = QPushButton(self.step_widget)
        self.pushButton_2.setObjectName(u"pushButton_2")
        font1 = QFont()
        font1.setFamilies([u"Times New Roman"])
        font1.setPointSize(12)
        font1.setBold(True)
        self.pushButton_2.setFont(font1)

        self.horizontalLayout.addWidget(self.pushButton_2)

        self.leftmove = QPushButton(self.step_widget)
        self.leftmove.setObjectName(u"leftmove")
        font2 = QFont()
        font2.setFamilies([u"Times New Roman"])
        font2.setPointSize(14)
        font2.setBold(True)
        self.leftmove.setFont(font2)

        self.horizontalLayout.addWidget(self.leftmove)

        self.stepFrame = QFrame(self.step_widget)
        self.stepFrame.setObjectName(u"stepFrame")
        sizePolicy.setHeightForWidth(self.stepFrame.sizePolicy().hasHeightForWidth())
        self.stepFrame.setSizePolicy(sizePolicy)
        self.stepFrame.setFrameShape(QFrame.Box)
        self.stepFrame.setFrameShadow(QFrame.Sunken)
        self.stepFrame.setLineWidth(3)
        self.stepFrame.setMidLineWidth(1)
        self.verticalLayout_2 = QVBoxLayout(self.stepFrame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(1, 1, 5, 1)
        self.stepSlider = QSlider(self.stepFrame)
        self.stepSlider.setObjectName(u"stepSlider")
        font3 = QFont()
        font3.setFamilies([u"Times New Roman"])
        font3.setPointSize(12)
        self.stepSlider.setFont(font3)
        self.stepSlider.setAcceptDrops(False)
        self.stepSlider.setAutoFillBackground(True)
        self.stepSlider.setSingleStep(1)
        self.stepSlider.setOrientation(Qt.Horizontal)
        self.stepSlider.setInvertedAppearance(False)
        self.stepSlider.setInvertedControls(False)
        self.stepSlider.setTickPosition(QSlider.TicksBelow)
        self.stepSlider.setTickInterval(5)

        self.verticalLayout_2.addWidget(self.stepSlider)


        self.horizontalLayout.addWidget(self.stepFrame)

        self.rightmove = QPushButton(self.step_widget)
        self.rightmove.setObjectName(u"rightmove")
        self.rightmove.setFont(font2)

        self.horizontalLayout.addWidget(self.rightmove)

        self.pushButton = QPushButton(self.step_widget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setFont(font1)

        self.horizontalLayout.addWidget(self.pushButton)


        self.gridLayout.addWidget(self.step_widget, 3, 0, 1, 4)

        self.deleteButton = QPushButton(self.centralwidget)
        self.deleteButton.setObjectName(u"deleteButton")
        self.deleteButton.setFont(font1)
        self.deleteButton.setCursor(QCursor(Qt.PointingHandCursor))

        self.gridLayout.addWidget(self.deleteButton, 1, 2, 1, 2)

        self.browseButton = QPushButton(self.centralwidget)
        self.browseButton.setObjectName(u"browseButton")
        self.browseButton.setFont(font1)
        self.browseButton.setCursor(QCursor(Qt.PointingHandCursor))

        self.gridLayout.addWidget(self.browseButton, 0, 2, 1, 1)

        self.addButton = QPushButton(self.centralwidget)
        self.addButton.setObjectName(u"addButton")
        self.addButton.setFont(font1)
        self.addButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.addButton.setFlat(False)

        self.gridLayout.addWidget(self.addButton, 0, 3, 1, 1)

        self.addedCombo = QComboBox(self.centralwidget)
        self.addedCombo.setObjectName(u"addedCombo")
        self.addedCombo.setFont(font)
        self.addedCombo.setCursor(QCursor(Qt.PointingHandCursor))

        self.gridLayout.addWidget(self.addedCombo, 1, 0, 1, 2)

        self.input_directory = QLineEdit(self.centralwidget)
        self.input_directory.setObjectName(u"input_directory")
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Active, QPalette.PlaceholderText, brush)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush)
#endif
        self.input_directory.setPalette(palette)
        self.input_directory.setFont(font)

        self.gridLayout.addWidget(self.input_directory, 0, 0, 1, 2)

        self.speed_widget = QWidget(self.centralwidget)
        self.speed_widget.setObjectName(u"speed_widget")
        self.horizontalLayout_2 = QHBoxLayout(self.speed_widget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.speedFrame = QFrame(self.speed_widget)
        self.speedFrame.setObjectName(u"speedFrame")
        sizePolicy.setHeightForWidth(self.speedFrame.sizePolicy().hasHeightForWidth())
        self.speedFrame.setSizePolicy(sizePolicy)
        self.speedFrame.setFrameShape(QFrame.Box)
        self.speedFrame.setFrameShadow(QFrame.Sunken)
        self.speedFrame.setLineWidth(2)
        self.speedFrame.setMidLineWidth(1)
        self.verticalLayout = QVBoxLayout(self.speedFrame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(1, 1, 5, 1)
        self.speedSlider = QSlider(self.speedFrame)
        self.speedSlider.setObjectName(u"speedSlider")
        self.speedSlider.setFont(font3)
        self.speedSlider.setAcceptDrops(False)
        self.speedSlider.setAutoFillBackground(True)
        self.speedSlider.setSingleStep(1)
        self.speedSlider.setOrientation(Qt.Horizontal)
        self.speedSlider.setInvertedAppearance(False)
        self.speedSlider.setInvertedControls(False)
        self.speedSlider.setTickPosition(QSlider.TicksBelow)
        self.speedSlider.setTickInterval(5)

        self.verticalLayout.addWidget(self.speedSlider)


        self.horizontalLayout_2.addWidget(self.speedFrame)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 3)
        self.horizontalLayout_2.setStretch(2, 1)

        self.gridLayout.addWidget(self.speed_widget, 4, 0, 1, 4)

        self.gridLayout.setColumnStretch(1, 1)
        VaspReader.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(VaspReader)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 480, 21))
        self.menubar.setFont(font)
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuFile.setFont(font)
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuEdit.setFont(font)
        self.menuLight = QMenu(self.menuEdit)
        self.menuLight.setObjectName(u"menuLight")
        self.menuLight.setFont(font)
        self.menuMods = QMenu(self.menubar)
        self.menuMods.setObjectName(u"menuMods")
        self.menuMods.setFont(font)
        self.menuTools = QMenu(self.menubar)
        self.menuTools.setObjectName(u"menuTools")
        self.menuTools.setFont(font)
        self.menuSelect_mode = QMenu(self.menuTools)
        self.menuSelect_mode.setObjectName(u"menuSelect_mode")
        self.menuSelect_mode.setFont(font)
        self.menuSet = QMenu(self.menuTools)
        self.menuSet.setObjectName(u"menuSet")
        self.menuSet.setFont(font)
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuHelp.setFont(font)
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        VaspReader.setMenuBar(self.menubar)
        QWidget.setTabOrder(self.input_directory, self.browseButton)
        QWidget.setTabOrder(self.browseButton, self.addButton)
        QWidget.setTabOrder(self.addButton, self.addedCombo)
        QWidget.setTabOrder(self.addedCombo, self.deleteButton)
        QWidget.setTabOrder(self.deleteButton, self.stepSlider)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuMods.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpen_calculation)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionLoad_Calculation_State)
        self.menuFile.addAction(self.actionSave_Calculation_State)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionLoad_Configuration)
        self.menuFile.addAction(self.actionSave_Configuration)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuEdit.addAction(self.actionDelete_coordinates_after_leave_cell)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.menuLight.menuAction())
        self.menuLight.addAction(self.actionLight_1)
        self.menuLight.addAction(self.actionLight_2)
        self.menuLight.addAction(self.actionLight_3)
        self.menuLight.addAction(self.actionLight_4)
        self.menuLight.addAction(self.actionLight_5)
        self.menuLight.addAction(self.actionLight_6)
        self.menuLight.addAction(self.actionLight_7)
        self.menuLight.addAction(self.actionLight_8)
        self.menuMods.addAction(self.actionProvessing)
        self.menuMods.addAction(self.actionOSZICAR)
        self.menuMods.addAction(self.actionPOSCAR)
        self.menuMods.addAction(self.actionCHGCAR)
        self.menuMods.addAction(self.actionIR_and_RAMAN)
        self.menuMods.addSeparator()
        self.menuMods.addAction(self.actionSupercomputer)
        self.menuMods.addSeparator()
        self.menuMods.addAction(self.actionGraphs)
        self.menuTools.addAction(self.menuSelect_mode.menuAction())
        self.menuTools.addAction(self.menuSet.menuAction())
        self.menuTools.addSeparator()
        self.menuTools.addAction(self.actionForm_POSCAR)
        self.menuTools.addSeparator()
        self.menuTools.addAction(self.actionScreenshot)
        self.menuSelect_mode.addAction(self.actionKeyboard)
        self.menuSelect_mode.addAction(self.actionMouse_keyboard)
        self.menuSet.addAction(self.actionAtom_ID)
        self.menuSet.addAction(self.actionBond)
        self.menuSet.addAction(self.actionValence_angle)
        self.menuHelp.addAction(self.actionAbout_the_program)
        self.menuHelp.addAction(self.actionWindow_description)
        self.menuHelp.addAction(self.actionLatest_update)
        self.menuHelp.addAction(self.actionChanges_history)
        self.menuView.addAction(self.actionAxes)
        self.menuView.addAction(self.actionCell_boarder)
        self.menuView.addSeparator()
        self.menuView.addAction(self.actionBonds)
        self.menuView.addSeparator()
        self.menuView.addAction(self.actionChange_background)

        self.retranslateUi(VaspReader)

        QMetaObject.connectSlotsByName(VaspReader)
    # setupUi

    def retranslateUi(self, VaspReader):
        VaspReader.setWindowTitle(QCoreApplication.translate("VaspReader", u"VaspReader", None))
        self.actionOpen_calculation.setText(QCoreApplication.translate("VaspReader", u"Open calculation", None))
        self.actionLoad_Calculation_State.setText(QCoreApplication.translate("VaspReader", u"Load Calculation State", None))
        self.actionSave_Calculation_State.setText(QCoreApplication.translate("VaspReader", u"Save Calculation State", None))
        self.actionLoad_Configuration.setText(QCoreApplication.translate("VaspReader", u"Load Configuration", None))
        self.actionSave_Configuration.setText(QCoreApplication.translate("VaspReader", u"Save Configuration", None))
        self.actionExit.setText(QCoreApplication.translate("VaspReader", u"Exit", None))
        self.actionAxes.setText(QCoreApplication.translate("VaspReader", u"Axes", None))
        self.actionCell_boarder.setText(QCoreApplication.translate("VaspReader", u"Cell boarder", None))
        self.actionBonds.setText(QCoreApplication.translate("VaspReader", u"Bonds", None))
        self.actionChange_background.setText(QCoreApplication.translate("VaspReader", u"Change background", None))
        self.actionDelete_coordinates_after_leave_cell.setText(QCoreApplication.translate("VaspReader", u"Delete coordinates after leave cell", None))
        self.actionLight_1.setText(QCoreApplication.translate("VaspReader", u"Light 1", None))
        self.actionLight_2.setText(QCoreApplication.translate("VaspReader", u"Light 2", None))
        self.actionLight_3.setText(QCoreApplication.translate("VaspReader", u"Light 3", None))
        self.actionLight_4.setText(QCoreApplication.translate("VaspReader", u"Light 4", None))
        self.actionLight_5.setText(QCoreApplication.translate("VaspReader", u"Light 5", None))
        self.actionLight_6.setText(QCoreApplication.translate("VaspReader", u"Light 6", None))
        self.actionLight_7.setText(QCoreApplication.translate("VaspReader", u"Light 7", None))
        self.actionLight_8.setText(QCoreApplication.translate("VaspReader", u"Light 8", None))
        self.actionProvessing.setText(QCoreApplication.translate("VaspReader", u"Processing", None))
        self.actionOSZICAR.setText(QCoreApplication.translate("VaspReader", u"OSZICAR", None))
        self.actionPOSCAR.setText(QCoreApplication.translate("VaspReader", u"POSCAR", None))
        self.actionCHGCAR.setText(QCoreApplication.translate("VaspReader", u"CHGCAR", None))
        self.actionIR_and_RAMAN.setText(QCoreApplication.translate("VaspReader", u"IR and RAMAN", None))
        self.actionSupercomputer.setText(QCoreApplication.translate("VaspReader", u"Supercomputer", None))
        self.actionGraphs.setText(QCoreApplication.translate("VaspReader", u"Graphs", None))
        self.actionKeyboard.setText(QCoreApplication.translate("VaspReader", u"Keyboard", None))
        self.actionMouse_keyboard.setText(QCoreApplication.translate("VaspReader", u"Mouse+keyboard", None))
        self.actionAtom_ID.setText(QCoreApplication.translate("VaspReader", u"Atom ID", None))
        self.actionBond.setText(QCoreApplication.translate("VaspReader", u"Bond", None))
        self.actionValence_angle.setText(QCoreApplication.translate("VaspReader", u"Valence angle", None))
        self.actionScreenshot.setText(QCoreApplication.translate("VaspReader", u"Screenshot", None))
        self.actionForm_POSCAR.setText(QCoreApplication.translate("VaspReader", u"Form POSCAR", None))
        self.actionAbout_the_program.setText(QCoreApplication.translate("VaspReader", u"About the program", None))
        self.actionWindow_description.setText(QCoreApplication.translate("VaspReader", u"Window description", None))
        self.actionLatest_update.setText(QCoreApplication.translate("VaspReader", u"Latest update", None))
        self.actionChanges_history.setText(QCoreApplication.translate("VaspReader", u"Changes history", None))
        self.pushButton_2.setText(QCoreApplication.translate("VaspReader", u"<<", None))
        self.leftmove.setText(QCoreApplication.translate("VaspReader", u"<", None))
#if QT_CONFIG(tooltip)
        self.stepSlider.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.rightmove.setText(QCoreApplication.translate("VaspReader", u">", None))
        self.pushButton.setText(QCoreApplication.translate("VaspReader", u">>", None))
        self.deleteButton.setText(QCoreApplication.translate("VaspReader", u"Delete", None))
        self.browseButton.setText(QCoreApplication.translate("VaspReader", u"Browse", None))
        self.addButton.setText(QCoreApplication.translate("VaspReader", u"Add", None))
        self.addedCombo.setCurrentText("")
        self.addedCombo.setPlaceholderText(QCoreApplication.translate("VaspReader", u"Choose calculation to delete", None))
        self.input_directory.setText("")
        self.input_directory.setPlaceholderText(QCoreApplication.translate("VaspReader", u"Input calculation folder", None))
#if QT_CONFIG(tooltip)
        self.speedSlider.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.menuFile.setTitle(QCoreApplication.translate("VaspReader", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("VaspReader", u"Edit", None))
        self.menuLight.setTitle(QCoreApplication.translate("VaspReader", u"Light", None))
        self.menuMods.setTitle(QCoreApplication.translate("VaspReader", u"Mods", None))
        self.menuTools.setTitle(QCoreApplication.translate("VaspReader", u"Tools", None))
        self.menuSelect_mode.setTitle(QCoreApplication.translate("VaspReader", u"Select mode", None))
        self.menuSet.setTitle(QCoreApplication.translate("VaspReader", u"Set", None))
        self.menuHelp.setTitle(QCoreApplication.translate("VaspReader", u"Help", None))
        self.menuView.setTitle(QCoreApplication.translate("VaspReader", u"View", None))
    # retranslateUi

