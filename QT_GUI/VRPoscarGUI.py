# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'VRPoscarGUITyNEtl.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)
import QT_GUI.Resource_rc

class Ui_VRPoscar(object):
    def setupUi(self, VRPoscar):
        if not VRPoscar.objectName():
            VRPoscar.setObjectName(u"VRPoscar")
        VRPoscar.resize(332, 250)
        VRPoscar.setMinimumSize(QSize(330, 250))
        VRPoscar.setMaximumSize(QSize(500, 350))
        icon = QIcon()
        icon.addFile(u":/VRlogo/VR-logo.ico", QSize(), QIcon.Normal, QIcon.Off)
        VRPoscar.setWindowIcon(icon)
        VRPoscar.setStyleSheet(u"QLineEdit{\n"
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
"  border-style: outset;\n"
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
"border: 0px solid #000000;\n"
"background-color: rgb(255, 255, 255, 255);\n"
"color: black;\n"
"font-weight: 600;\n"
"height:28px;}\n"
"QCheckBox{\n"
"  border-radius: 6px;\n"
"  border: 2px solid #000000;\n"
"  padding: 3px 3px;\n"
"}")
        VRPoscar.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.actionAbout = QAction(VRPoscar)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionBack = QAction(VRPoscar)
        self.actionBack.setObjectName(u"actionBack")
        self.actionExit = QAction(VRPoscar)
        self.actionExit.setObjectName(u"actionExit")
        self.PoscarMainWidget = QWidget(VRPoscar)
        self.PoscarMainWidget.setObjectName(u"PoscarMainWidget")
        self.verticalLayout = QVBoxLayout(self.PoscarMainWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(13, -1, 12, -1)
        self.PoscarTopLayout = QHBoxLayout()
        self.PoscarTopLayout.setObjectName(u"PoscarTopLayout")
        self.PoscarTopLayout.setContentsMargins(0, -1, 0, -1)
        self.label = QLabel(self.PoscarMainWidget)
        self.label.setObjectName(u"label")

        self.PoscarTopLayout.addWidget(self.label)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.PoscarTopLayout.addItem(self.horizontalSpacer_2)

        self.lineEdit = QLineEdit(self.PoscarMainWidget)
        self.lineEdit.setObjectName(u"lineEdit")

        self.PoscarTopLayout.addWidget(self.lineEdit)

        self.PoscarTopLayout.setStretch(0, 1)
        self.PoscarTopLayout.setStretch(1, 1)
        self.PoscarTopLayout.setStretch(2, 3)

        self.verticalLayout.addLayout(self.PoscarTopLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, -1, 0, -1)
        self.label_2 = QLabel(self.PoscarMainWidget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.lineEdit_2 = QLineEdit(self.PoscarMainWidget)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.horizontalLayout_2.addWidget(self.lineEdit_2)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 1)
        self.horizontalLayout_2.setStretch(2, 3)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, -1, 0, -1)
        self.label_3 = QLabel(self.PoscarMainWidget)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)

        self.comboBox = QComboBox(self.PoscarMainWidget)
        self.comboBox.setObjectName(u"comboBox")

        self.horizontalLayout_3.addWidget(self.comboBox)

        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 1)
        self.horizontalLayout_3.setStretch(2, 100)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.checkBox = QCheckBox(self.PoscarMainWidget)
        self.checkBox.setObjectName(u"checkBox")

        self.verticalLayout.addWidget(self.checkBox)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.pushButton = QPushButton(self.PoscarMainWidget)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout_4.addWidget(self.pushButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.pushButton_2 = QPushButton(self.PoscarMainWidget)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout_4.addWidget(self.pushButton_2)

        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(1, 1)
        self.horizontalLayout_4.setStretch(2, 1)

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        VRPoscar.setCentralWidget(self.PoscarMainWidget)
        self.menubar = QMenuBar(VRPoscar)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 332, 22))
        self.menuWindow = QMenu(self.menubar)
        self.menuWindow.setObjectName(u"menuWindow")
        VRPoscar.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuWindow.menuAction())
        self.menuWindow.addAction(self.actionAbout)
        self.menuWindow.addSeparator()
        self.menuWindow.addAction(self.actionBack)
        self.menuWindow.addSeparator()
        self.menuWindow.addAction(self.actionExit)

        self.retranslateUi(VRPoscar)

        QMetaObject.connectSlotsByName(VRPoscar)
    # setupUi

    def retranslateUi(self, VRPoscar):
        VRPoscar.setWindowTitle(QCoreApplication.translate("VRPoscar", u"VaspReader (POSCAR)", None))
        self.actionAbout.setText(QCoreApplication.translate("VRPoscar", u"About", None))
        self.actionBack.setText(QCoreApplication.translate("VRPoscar", u"Back", None))
        self.actionExit.setText(QCoreApplication.translate("VRPoscar", u"Exit", None))
        self.label.setText(QCoreApplication.translate("VRPoscar", u"Step:", None))
        self.label_2.setText(QCoreApplication.translate("VRPoscar", u"Max. Step:", None))
        self.label_3.setText(QCoreApplication.translate("VRPoscar", u"Type Of Coordinates:", None))
        self.checkBox.setText(QCoreApplication.translate("VRPoscar", u"Fix Coordinates Of Atoms", None))
        self.pushButton.setText(QCoreApplication.translate("VRPoscar", u"Create POSCAR", None))
        self.pushButton_2.setText(QCoreApplication.translate("VRPoscar", u"Back", None))
        self.menuWindow.setTitle(QCoreApplication.translate("VRPoscar", u"Window", None))
    # retranslateUi

