# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'VROszicarGUIBSYmze.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QSpacerItem, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)
import Gui.Resource_rc

class Ui_VROszicar(object):
    def setupUi(self, VROszicar):
        if not VROszicar.objectName():
            VROszicar.setObjectName(u"VROszicar")
        VROszicar.resize(650, 500)
        VROszicar.setMinimumSize(QSize(350, 400))
        icon = QIcon()
        icon.addFile(u":/VRlogo/VR-logo.ico", QSize(), QIcon.Normal, QIcon.Off)
        VROszicar.setWindowIcon(icon)
        VROszicar.setStyleSheet(u"QPushButton {\n"
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
"QFrame{\n"
"  border: 2px solid #000000;\n"
"  border-radius: 5px;\n"
"}\n"
"QScrollBar:vertical {\n"
"    border-radius: 6px;\n"
"    border: 2px solid rgb(0, 0, 0);\n"
"	color: rgb(0, 0, 0);\n"
"    background: rgb(182, 182, 182);\n"
""
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
"  "
                        "  width: 3.5px;\n"
"    height: 3.5px;\n"
"    background: rgb(255, 255, 255);\n"
"}\n"
"QScrollBar::up-arrow:vertical:hover, QScrollBar::down-arrow:vertical:hover {\n"
"    background: rgb(0, 203, 203);\n"
"}\n"
"\n"
"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
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
"QScrollBar::sub-"
                        "line:horizontal {\n"
"    border: 1.5px solid rgb(0, 0, 0);\n"
"    border-radius: 6px;\n"
"    background: rgb(0, 203, 203);\n"
"    width: 18px;\n"
"    subcontrol-position: left;\n"
"    subcontrol-origin: margin;\n"
"}\n"
"QScrollBar::add-line:hover:horizontal, QScrollBar::sub-line:hover:horizontal {\n"
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
        VROszicar.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.AAbout = QAction(VROszicar)
        self.AAbout.setObjectName(u"AAbout")
        self.ABack = QAction(VROszicar)
        self.ABack.setObjectName(u"ABack")
        self.AExit = QAction(VROszicar)
        self.AExit.setObjectName(u"AExit")
        self.OszicarMainWidget = QWidget(VROszicar)
        self.OszicarMainWidget.setObjectName(u"OszicarMainWidget")
        self.verticalLayout = QVBoxLayout(self.OszicarMainWidget)
        self.verticalLayout.setSpacing(14)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(18, 9, 18, 18)
        self.OszicarTableView = QTableWidget(self.OszicarMainWidget)
        self.OszicarTableView.setObjectName(u"OszicarTableView")
        self.OszicarTableView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.OszicarTableView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.OszicarTableView.setAutoScroll(True)
        self.OszicarTableView.setAlternatingRowColors(False)

        self.verticalLayout.addWidget(self.OszicarTableView)

        self.BottomLayout = QHBoxLayout()
        self.BottomLayout.setObjectName(u"BottomLayout")
        self.OszicarCreateExcelButton = QPushButton(self.OszicarMainWidget)
        self.OszicarCreateExcelButton.setObjectName(u"OszicarCreateExcelButton")

        self.BottomLayout.addWidget(self.OszicarCreateExcelButton)

        self.OszicarBuildGraphButton = QPushButton(self.OszicarMainWidget)
        self.OszicarBuildGraphButton.setObjectName(u"OszicarBuildGraphButton")

        self.BottomLayout.addWidget(self.OszicarBuildGraphButton)

        self.OszicarBack = QPushButton(self.OszicarMainWidget)
        self.OszicarBack.setObjectName(u"OszicarBack")

        self.BottomLayout.addWidget(self.OszicarBack)

        self.BottomHSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.BottomLayout.addItem(self.BottomHSpacer)

        self.BottomLayout.setStretch(0, 1)
        self.BottomLayout.setStretch(1, 1)
        self.BottomLayout.setStretch(2, 1)
        self.BottomLayout.setStretch(3, 6)

        self.verticalLayout.addLayout(self.BottomLayout)

        self.verticalLayout.setStretch(0, 1)
        VROszicar.setCentralWidget(self.OszicarMainWidget)
        self.OszicarMenubar = QMenuBar(VROszicar)
        self.OszicarMenubar.setObjectName(u"OszicarMenubar")
        self.OszicarMenubar.setGeometry(QRect(0, 0, 650, 22))
        self.OszicarMenuWindow = QMenu(self.OszicarMenubar)
        self.OszicarMenuWindow.setObjectName(u"OszicarMenuWindow")
        VROszicar.setMenuBar(self.OszicarMenubar)

        self.OszicarMenubar.addAction(self.OszicarMenuWindow.menuAction())
        self.OszicarMenuWindow.addAction(self.AAbout)
        self.OszicarMenuWindow.addSeparator()
        self.OszicarMenuWindow.addAction(self.ABack)
        self.OszicarMenuWindow.addSeparator()
        self.OszicarMenuWindow.addAction(self.AExit)

        self.retranslateUi(VROszicar)

        QMetaObject.connectSlotsByName(VROszicar)
    # setupUi

    def retranslateUi(self, VROszicar):
        VROszicar.setWindowTitle(QCoreApplication.translate("VROszicar", u"VaspReader (OSZICAR)", None))
        self.AAbout.setText(QCoreApplication.translate("VROszicar", u"About", None))
        self.ABack.setText(QCoreApplication.translate("VROszicar", u"Back", None))
        self.AExit.setText(QCoreApplication.translate("VROszicar", u"Exit", None))
        self.OszicarCreateExcelButton.setText(QCoreApplication.translate("VROszicar", u"Create Excel", None))
        self.OszicarBuildGraphButton.setText(QCoreApplication.translate("VROszicar", u"Build Graphs", None))
        self.OszicarBack.setText(QCoreApplication.translate("VROszicar", u"Back", None))
        self.OszicarMenuWindow.setTitle(QCoreApplication.translate("VROszicar", u"Window", None))
    # retranslateUi

