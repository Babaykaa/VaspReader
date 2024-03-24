# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'VRAuthSupercomputerGUIvhuVLZ.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QLabel, QLineEdit,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QTabWidget, QVBoxLayout, QWidget)
import Gui.Resource_rc

class Ui_VRAuthSupercomputer(object):
    def setupUi(self, VRAuthSupercomputer):
        if not VRAuthSupercomputer.objectName():
            VRAuthSupercomputer.setObjectName(u"VRAuthSupercomputer")
        VRAuthSupercomputer.resize(400, 230)
        VRAuthSupercomputer.setMinimumSize(QSize(400, 230))
        VRAuthSupercomputer.setMaximumSize(QSize(400, 230))
        icon = QIcon()
        icon.addFile(u":/VRlogo/VR-logo.ico", QSize(), QIcon.Normal, QIcon.Off)
        VRAuthSupercomputer.setWindowIcon(icon)
        VRAuthSupercomputer.setStyleSheet(u"QLineEdit{\n"
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
"height:28px;}")
        VRAuthSupercomputer.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        VRAuthSupercomputer.setTabShape(QTabWidget.Rounded)
        self.AuthMainWidget = QWidget(VRAuthSupercomputer)
        self.AuthMainWidget.setObjectName(u"AuthMainWidget")
        self.verticalLayout = QVBoxLayout(self.AuthMainWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.AuthSelUserLabel = QLabel(self.AuthMainWidget)
        self.AuthSelUserLabel.setObjectName(u"AuthSelUserLabel")

        self.verticalLayout.addWidget(self.AuthSelUserLabel)

        self.AuthChooseAdded = QComboBox(self.AuthMainWidget)
        self.AuthChooseAdded.setObjectName(u"AuthChooseAdded")

        self.verticalLayout.addWidget(self.AuthChooseAdded)

        self.AuthAddUserLabel = QLabel(self.AuthMainWidget)
        self.AuthAddUserLabel.setObjectName(u"AuthAddUserLabel")

        self.verticalLayout.addWidget(self.AuthAddUserLabel)

        self.AuthAddNewUser = QLineEdit(self.AuthMainWidget)
        self.AuthAddNewUser.setObjectName(u"AuthAddNewUser")

        self.verticalLayout.addWidget(self.AuthAddNewUser)

        self.AuthSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.AuthSpacer)

        self.AuthSubmitButton = QPushButton(self.AuthMainWidget)
        self.AuthSubmitButton.setObjectName(u"AuthSubmitButton")

        self.verticalLayout.addWidget(self.AuthSubmitButton)

        self.AuthNoteLabel = QLabel(self.AuthMainWidget)
        self.AuthNoteLabel.setObjectName(u"AuthNoteLabel")
        self.AuthNoteLabel.setEnabled(False)
        self.AuthNoteLabel.setTextFormat(Qt.AutoText)
        self.AuthNoteLabel.setScaledContents(False)
        self.AuthNoteLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.AuthNoteLabel)

        VRAuthSupercomputer.setCentralWidget(self.AuthMainWidget)

        self.retranslateUi(VRAuthSupercomputer)

        QMetaObject.connectSlotsByName(VRAuthSupercomputer)
    # setupUi

    def retranslateUi(self, VRAuthSupercomputer):
        VRAuthSupercomputer.setWindowTitle(QCoreApplication.translate("VRAuthSupercomputer", u"VaspReader (Auth Window)", None))
        self.AuthSelUserLabel.setText(QCoreApplication.translate("VRAuthSupercomputer", u"Select User:", None))
        self.AuthAddUserLabel.setText(QCoreApplication.translate("VRAuthSupercomputer", u"Add New User:", None))
        self.AuthSubmitButton.setText(QCoreApplication.translate("VRAuthSupercomputer", u"Submit", None))
        self.AuthNoteLabel.setText(QCoreApplication.translate("VRAuthSupercomputer", u"Note: Before Auth Use Peageant To Add A Key", None))
    # retranslateUi

