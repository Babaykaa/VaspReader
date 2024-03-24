# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'VRGraphProcessingGUIUDBxXF.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGraphicsView, QHBoxLayout, QLabel, QLineEdit,
    QListView, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QVBoxLayout, QWidget)
import Gui.Resource_rc

class Ui_VRGraphProcessing(object):
    def setupUi(self, VRGraphProcessing):
        if not VRGraphProcessing.objectName():
            VRGraphProcessing.setObjectName(u"VRGraphProcessing")
        VRGraphProcessing.resize(900, 600)
        VRGraphProcessing.setMinimumSize(QSize(900, 600))
        icon = QIcon()
        icon.addFile(u":/VRlogo/VR-logo.ico", QSize(), QIcon.Normal, QIcon.Off)
        VRGraphProcessing.setWindowIcon(icon)
        VRGraphProcessing.setStyleSheet(u"QLineEdit{\n"
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
        VRGraphProcessing.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.AAbout = QAction(VRGraphProcessing)
        self.AAbout.setObjectName(u"AAbout")
        self.ABack = QAction(VRGraphProcessing)
        self.ABack.setObjectName(u"ABack")
        self.AExit = QAction(VRGraphProcessing)
        self.AExit.setObjectName(u"AExit")
        self.MainWidget = QWidget(VRGraphProcessing)
        self.MainWidget.setObjectName(u"MainWidget")
        self.verticalLayout = QVBoxLayout(self.MainWidget)
        self.verticalLayout.setSpacing(14)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, -1, -1, 18)
        self.TopLayout = QHBoxLayout()
        self.TopLayout.setSpacing(10)
        self.TopLayout.setObjectName(u"TopLayout")
        self.TopLayout.setContentsMargins(-1, -1, 9, -1)
        self.TopLeftLayout = QVBoxLayout()
        self.TopLeftLayout.setObjectName(u"TopLeftLayout")
        self.TopLeftLayout.setContentsMargins(9, -1, 9, -1)
        self.ColumnsList = QListView(self.MainWidget)
        self.ColumnsList.setObjectName(u"ColumnsList")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ColumnsList.sizePolicy().hasHeightForWidth())
        self.ColumnsList.setSizePolicy(sizePolicy)
        self.ColumnsList.setMinimumSize(QSize(250, 167))

        self.TopLeftLayout.addWidget(self.ColumnsList)

        self.GraphOptionsTab = QTabWidget(self.MainWidget)
        self.GraphOptionsTab.setObjectName(u"GraphOptionsTab")
        sizePolicy.setHeightForWidth(self.GraphOptionsTab.sizePolicy().hasHeightForWidth())
        self.GraphOptionsTab.setSizePolicy(sizePolicy)
        self.GraphOptionsTab.setMinimumSize(QSize(260, 334))
        self.GraphLimits = QWidget()
        self.GraphLimits.setObjectName(u"GraphLimits")
        self.verticalLayoutWidget = QWidget(self.GraphLimits)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 251, 301))
        self.GraphLimitsLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.GraphLimitsLayout.setObjectName(u"GraphLimitsLayout")
        self.GraphLimitsLayout.setContentsMargins(6, 8, 6, 8)
        self.XAxisLimitsLabel = QLabel(self.verticalLayoutWidget)
        self.XAxisLimitsLabel.setObjectName(u"XAxisLimitsLabel")

        self.GraphLimitsLayout.addWidget(self.XAxisLimitsLabel)

        self.XAxisFromTo = QHBoxLayout()
        self.XAxisFromTo.setObjectName(u"XAxisFromTo")
        self.XAxisFrom = QLineEdit(self.verticalLayoutWidget)
        self.XAxisFrom.setObjectName(u"XAxisFrom")
        self.XAxisFrom.setEnabled(True)

        self.XAxisFromTo.addWidget(self.XAxisFrom)

        self.XAxisTo = QLineEdit(self.verticalLayoutWidget)
        self.XAxisTo.setObjectName(u"XAxisTo")
        self.XAxisTo.setEnabled(True)

        self.XAxisFromTo.addWidget(self.XAxisTo)


        self.GraphLimitsLayout.addLayout(self.XAxisFromTo)

        self.YAxisLimitsLabel = QLabel(self.verticalLayoutWidget)
        self.YAxisLimitsLabel.setObjectName(u"YAxisLimitsLabel")

        self.GraphLimitsLayout.addWidget(self.YAxisLimitsLabel)

        self.YAxisFromTo = QHBoxLayout()
        self.YAxisFromTo.setObjectName(u"YAxisFromTo")
        self.YAxisFrom = QLineEdit(self.verticalLayoutWidget)
        self.YAxisFrom.setObjectName(u"YAxisFrom")
        self.YAxisFrom.setEnabled(True)

        self.YAxisFromTo.addWidget(self.YAxisFrom)

        self.YAxisTo = QLineEdit(self.verticalLayoutWidget)
        self.YAxisTo.setObjectName(u"YAxisTo")

        self.YAxisFromTo.addWidget(self.YAxisTo)


        self.GraphLimitsLayout.addLayout(self.YAxisFromTo)

        self.LimitsSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.GraphLimitsLayout.addItem(self.LimitsSpacer)

        self.SetLimitsButton = QPushButton(self.verticalLayoutWidget)
        self.SetLimitsButton.setObjectName(u"SetLimitsButton")

        self.GraphLimitsLayout.addWidget(self.SetLimitsButton)

        self.ResetLimitsButton = QPushButton(self.verticalLayoutWidget)
        self.ResetLimitsButton.setObjectName(u"ResetLimitsButton")

        self.GraphLimitsLayout.addWidget(self.ResetLimitsButton)

        self.GraphOptionsTab.addTab(self.GraphLimits, "")
        self.GraphLabels = QWidget()
        self.GraphLabels.setObjectName(u"GraphLabels")
        self.verticalLayoutWidget_2 = QWidget(self.GraphLabels)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(0, 0, 251, 301))
        self.GraphLabelsLayout = QVBoxLayout(self.verticalLayoutWidget_2)
        self.GraphLabelsLayout.setObjectName(u"GraphLabelsLayout")
        self.GraphLabelsLayout.setContentsMargins(6, 8, 6, 8)
        self.XAxisLabelLabel = QLabel(self.verticalLayoutWidget_2)
        self.XAxisLabelLabel.setObjectName(u"XAxisLabelLabel")

        self.GraphLabelsLayout.addWidget(self.XAxisLabelLabel)

        self.XAxisLabelEdit = QLineEdit(self.verticalLayoutWidget_2)
        self.XAxisLabelEdit.setObjectName(u"XAxisLabelEdit")

        self.GraphLabelsLayout.addWidget(self.XAxisLabelEdit)

        self.YAxisLabelLabel = QLabel(self.verticalLayoutWidget_2)
        self.YAxisLabelLabel.setObjectName(u"YAxisLabelLabel")

        self.GraphLabelsLayout.addWidget(self.YAxisLabelLabel)

        self.YAxisLabelEdit = QLineEdit(self.verticalLayoutWidget_2)
        self.YAxisLabelEdit.setObjectName(u"YAxisLabelEdit")

        self.GraphLabelsLayout.addWidget(self.YAxisLabelEdit)

        self.LabelsSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.GraphLabelsLayout.addItem(self.LabelsSpacer)

        self.SetLabelsButton = QPushButton(self.verticalLayoutWidget_2)
        self.SetLabelsButton.setObjectName(u"SetLabelsButton")

        self.GraphLabelsLayout.addWidget(self.SetLabelsButton)

        self.ResetLabelsButton = QPushButton(self.verticalLayoutWidget_2)
        self.ResetLabelsButton.setObjectName(u"ResetLabelsButton")

        self.GraphLabelsLayout.addWidget(self.ResetLabelsButton)

        self.GraphOptionsTab.addTab(self.GraphLabels, "")
        self.GraphLegend = QWidget()
        self.GraphLegend.setObjectName(u"GraphLegend")
        self.verticalLayoutWidget_3 = QWidget(self.GraphLegend)
        self.verticalLayoutWidget_3.setObjectName(u"verticalLayoutWidget_3")
        self.verticalLayoutWidget_3.setGeometry(QRect(0, 0, 251, 301))
        self.GraphLegendLayout = QVBoxLayout(self.verticalLayoutWidget_3)
        self.GraphLegendLayout.setObjectName(u"GraphLegendLayout")
        self.GraphLegendLayout.setContentsMargins(6, 8, 6, 8)
        self.AddLegendCheckbox = QCheckBox(self.verticalLayoutWidget_3)
        self.AddLegendCheckbox.setObjectName(u"AddLegendCheckbox")
        self.AddLegendCheckbox.setAutoFillBackground(False)
        self.AddLegendCheckbox.setTristate(False)

        self.GraphLegendLayout.addWidget(self.AddLegendCheckbox)

        self.RenameCurvesLabel = QLabel(self.verticalLayoutWidget_3)
        self.RenameCurvesLabel.setObjectName(u"RenameCurvesLabel")

        self.GraphLegendLayout.addWidget(self.RenameCurvesLabel)

        self.RenameCurves = QComboBox(self.verticalLayoutWidget_3)
        self.RenameCurves.setObjectName(u"RenameCurves")
        self.RenameCurves.setEnabled(False)

        self.GraphLegendLayout.addWidget(self.RenameCurves)

        self.LegendEdit = QLineEdit(self.verticalLayoutWidget_3)
        self.LegendEdit.setObjectName(u"LegendEdit")
        self.LegendEdit.setEnabled(False)

        self.GraphLegendLayout.addWidget(self.LegendEdit)

        self.AutoRenameCurvesLabel = QLabel(self.verticalLayoutWidget_3)
        self.AutoRenameCurvesLabel.setObjectName(u"AutoRenameCurvesLabel")

        self.GraphLegendLayout.addWidget(self.AutoRenameCurvesLabel)

        self.AutoRenameCurves = QComboBox(self.verticalLayoutWidget_3)
        self.AutoRenameCurves.setObjectName(u"AutoRenameCurves")
        self.AutoRenameCurves.setEnabled(False)

        self.GraphLegendLayout.addWidget(self.AutoRenameCurves)

        self.LegendSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.GraphLegendLayout.addItem(self.LegendSpacer)

        self.ChangeLegendButton = QPushButton(self.verticalLayoutWidget_3)
        self.ChangeLegendButton.setObjectName(u"ChangeLegendButton")
        self.ChangeLegendButton.setEnabled(False)

        self.GraphLegendLayout.addWidget(self.ChangeLegendButton)

        self.GraphOptionsTab.addTab(self.GraphLegend, "")
        self.GraphParameters = QWidget()
        self.GraphParameters.setObjectName(u"GraphParameters")
        self.verticalLayoutWidget_4 = QWidget(self.GraphParameters)
        self.verticalLayoutWidget_4.setObjectName(u"verticalLayoutWidget_4")
        self.verticalLayoutWidget_4.setGeometry(QRect(0, 0, 251, 301))
        self.GraphParametersLayout = QVBoxLayout(self.verticalLayoutWidget_4)
        self.GraphParametersLayout.setObjectName(u"GraphParametersLayout")
        self.GraphParametersLayout.setContentsMargins(6, 8, 6, 8)
        self.CurveToChangeParametersLabel = QLabel(self.verticalLayoutWidget_4)
        self.CurveToChangeParametersLabel.setObjectName(u"CurveToChangeParametersLabel")

        self.GraphParametersLayout.addWidget(self.CurveToChangeParametersLabel)

        self.CurveToChangeParameters = QComboBox(self.verticalLayoutWidget_4)
        self.CurveToChangeParameters.setObjectName(u"CurveToChangeParameters")

        self.GraphParametersLayout.addWidget(self.CurveToChangeParameters)

        self.LineWidthLabel = QLabel(self.verticalLayoutWidget_4)
        self.LineWidthLabel.setObjectName(u"LineWidthLabel")

        self.GraphParametersLayout.addWidget(self.LineWidthLabel)

        self.CurveLineWidthEdit = QLineEdit(self.verticalLayoutWidget_4)
        self.CurveLineWidthEdit.setObjectName(u"CurveLineWidthEdit")
        self.CurveLineWidthEdit.setEnabled(False)

        self.GraphParametersLayout.addWidget(self.CurveLineWidthEdit)

        self.CurveColorLabel = QLabel(self.verticalLayoutWidget_4)
        self.CurveColorLabel.setObjectName(u"CurveColorLabel")

        self.GraphParametersLayout.addWidget(self.CurveColorLabel)

        self.ColorChangeLayout = QHBoxLayout()
        self.ColorChangeLayout.setObjectName(u"ColorChangeLayout")
        self.CurveColorCheck = QFrame(self.verticalLayoutWidget_4)
        self.CurveColorCheck.setObjectName(u"CurveColorCheck")
        self.CurveColorCheck.setEnabled(False)
        sizePolicy.setHeightForWidth(self.CurveColorCheck.sizePolicy().hasHeightForWidth())
        self.CurveColorCheck.setSizePolicy(sizePolicy)
        self.CurveColorCheck.setMinimumSize(QSize(150, 23))
        self.CurveColorCheck.setFrameShape(QFrame.StyledPanel)
        self.CurveColorCheck.setFrameShadow(QFrame.Raised)

        self.ColorChangeLayout.addWidget(self.CurveColorCheck)

        self.CurveColorChoose = QPushButton(self.verticalLayoutWidget_4)
        self.CurveColorChoose.setObjectName(u"CurveColorChoose")
        self.CurveColorChoose.setEnabled(False)

        self.ColorChangeLayout.addWidget(self.CurveColorChoose)


        self.GraphParametersLayout.addLayout(self.ColorChangeLayout)

        self.ParametersSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.GraphParametersLayout.addItem(self.ParametersSpacer)

        self.CurveParametersChangeApply = QPushButton(self.verticalLayoutWidget_4)
        self.CurveParametersChangeApply.setObjectName(u"CurveParametersChangeApply")
        self.CurveParametersChangeApply.setEnabled(False)

        self.GraphParametersLayout.addWidget(self.CurveParametersChangeApply)

        self.GraphOptionsTab.addTab(self.GraphParameters, "")

        self.TopLeftLayout.addWidget(self.GraphOptionsTab)

        self.TopLeftLayout.setStretch(0, 1)

        self.TopLayout.addLayout(self.TopLeftLayout)

        self.GraphsView = QGraphicsView(self.MainWidget)
        self.GraphsView.setObjectName(u"GraphsView")

        self.TopLayout.addWidget(self.GraphsView)

        self.TopLayout.setStretch(0, 2)
        self.TopLayout.setStretch(1, 5)

        self.verticalLayout.addLayout(self.TopLayout)

        self.BottomLayout = QHBoxLayout()
        self.BottomLayout.setObjectName(u"BottomLayout")
        self.BottomLayout.setContentsMargins(9, -1, -1, 0)
        self.CreateGraphButton = QPushButton(self.MainWidget)
        self.CreateGraphButton.setObjectName(u"CreateGraphButton")

        self.BottomLayout.addWidget(self.CreateGraphButton)

        self.GraphBackButton = QPushButton(self.MainWidget)
        self.GraphBackButton.setObjectName(u"GraphBackButton")

        self.BottomLayout.addWidget(self.GraphBackButton)

        self.BottomHSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.BottomLayout.addItem(self.BottomHSpacer)

        self.BottomLayout.setStretch(0, 1)
        self.BottomLayout.setStretch(1, 1)
        self.BottomLayout.setStretch(2, 7)

        self.verticalLayout.addLayout(self.BottomLayout)

        self.verticalLayout.setStretch(0, 20)
        self.verticalLayout.setStretch(1, 1)
        VRGraphProcessing.setCentralWidget(self.MainWidget)
        self.GraphProcessingMenubar = QMenuBar(VRGraphProcessing)
        self.GraphProcessingMenubar.setObjectName(u"GraphProcessingMenubar")
        self.GraphProcessingMenubar.setGeometry(QRect(0, 0, 900, 22))
        self.GraphProcessingMenuWindow = QMenu(self.GraphProcessingMenubar)
        self.GraphProcessingMenuWindow.setObjectName(u"GraphProcessingMenuWindow")
        VRGraphProcessing.setMenuBar(self.GraphProcessingMenubar)

        self.GraphProcessingMenubar.addAction(self.GraphProcessingMenuWindow.menuAction())
        self.GraphProcessingMenuWindow.addAction(self.AAbout)
        self.GraphProcessingMenuWindow.addSeparator()
        self.GraphProcessingMenuWindow.addAction(self.ABack)
        self.GraphProcessingMenuWindow.addSeparator()
        self.GraphProcessingMenuWindow.addAction(self.AExit)

        self.retranslateUi(VRGraphProcessing)

        self.GraphOptionsTab.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(VRGraphProcessing)
    # setupUi

    def retranslateUi(self, VRGraphProcessing):
        VRGraphProcessing.setWindowTitle(QCoreApplication.translate("VRGraphProcessing", u"VaspReader (Graphs Processing)", None))
        self.AAbout.setText(QCoreApplication.translate("VRGraphProcessing", u"About", None))
        self.ABack.setText(QCoreApplication.translate("VRGraphProcessing", u"Back", None))
        self.AExit.setText(QCoreApplication.translate("VRGraphProcessing", u"Exit", None))
        self.XAxisLimitsLabel.setText(QCoreApplication.translate("VRGraphProcessing", u"X-Axis:", None))
        self.YAxisLimitsLabel.setText(QCoreApplication.translate("VRGraphProcessing", u"Y-Axis:", None))
        self.SetLimitsButton.setText(QCoreApplication.translate("VRGraphProcessing", u"Set Limits", None))
        self.ResetLimitsButton.setText(QCoreApplication.translate("VRGraphProcessing", u"Reset", None))
        self.GraphOptionsTab.setTabText(self.GraphOptionsTab.indexOf(self.GraphLimits), QCoreApplication.translate("VRGraphProcessing", u"Limits", None))
        self.XAxisLabelLabel.setText(QCoreApplication.translate("VRGraphProcessing", u"X-Label:", None))
        self.YAxisLabelLabel.setText(QCoreApplication.translate("VRGraphProcessing", u"Y-Label:", None))
        self.SetLabelsButton.setText(QCoreApplication.translate("VRGraphProcessing", u"Set Labels", None))
        self.ResetLabelsButton.setText(QCoreApplication.translate("VRGraphProcessing", u"Reset", None))
        self.GraphOptionsTab.setTabText(self.GraphOptionsTab.indexOf(self.GraphLabels), QCoreApplication.translate("VRGraphProcessing", u"Labels", None))
        self.AddLegendCheckbox.setText(QCoreApplication.translate("VRGraphProcessing", u"Add Legend", None))
        self.RenameCurvesLabel.setText(QCoreApplication.translate("VRGraphProcessing", u"Rename curves:", None))
        self.AutoRenameCurvesLabel.setText(QCoreApplication.translate("VRGraphProcessing", u"Auto-Rename:", None))
        self.ChangeLegendButton.setText(QCoreApplication.translate("VRGraphProcessing", u"Submit", None))
        self.GraphOptionsTab.setTabText(self.GraphOptionsTab.indexOf(self.GraphLegend), QCoreApplication.translate("VRGraphProcessing", u"Legend", None))
        self.CurveToChangeParametersLabel.setText(QCoreApplication.translate("VRGraphProcessing", u"Curve to change:", None))
        self.LineWidthLabel.setText(QCoreApplication.translate("VRGraphProcessing", u"Line Width:", None))
        self.CurveColorLabel.setText(QCoreApplication.translate("VRGraphProcessing", u"Curve Color:", None))
        self.CurveColorChoose.setText(QCoreApplication.translate("VRGraphProcessing", u"Color", None))
        self.CurveParametersChangeApply.setText(QCoreApplication.translate("VRGraphProcessing", u"Submit", None))
        self.GraphOptionsTab.setTabText(self.GraphOptionsTab.indexOf(self.GraphParameters), QCoreApplication.translate("VRGraphProcessing", u"Parameters", None))
        self.CreateGraphButton.setText(QCoreApplication.translate("VRGraphProcessing", u"Create Graph", None))
        self.GraphBackButton.setText(QCoreApplication.translate("VRGraphProcessing", u"Back", None))
        self.GraphProcessingMenuWindow.setTitle(QCoreApplication.translate("VRGraphProcessing", u"Window", None))
    # retranslateUi

