# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'VRChoosePoscarGUIoSzkyC.ui'
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
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QPushButton,
    QSizePolicy, QWidget)
import QT_GUI.Resource_rc

class Ui_ChooseFileWindow(object):
    def setupUi(self, ChooseFileWindow):
        if not ChooseFileWindow.objectName():
            ChooseFileWindow.setObjectName(u"ChooseFileWindow")
        ChooseFileWindow.resize(400, 300)
        ChooseFileWindow.setMinimumSize(QSize(400, 300))
        ChooseFileWindow.setMaximumSize(QSize(400, 300))
        icon = QIcon()
        icon.addFile(u":/VRlogo/VR-logo.ico", QSize(), QIcon.Normal, QIcon.Off)
        ChooseFileWindow.setWindowIcon(icon)
        ChooseFileWindow.setStyleSheet(u"QPushButton {\n"
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
        ChooseFileWindow.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.PoscarFileChoose = QComboBox(ChooseFileWindow)
        self.PoscarFileChoose.setObjectName(u"PoscarFileChoose")
        self.PoscarFileChoose.setGeometry(QRect(10, 20, 381, 31))
        self.PoscarChooseSubmitButton = QPushButton(ChooseFileWindow)
        self.PoscarChooseSubmitButton.setObjectName(u"PoscarChooseSubmitButton")
        self.PoscarChooseSubmitButton.setGeometry(QRect(10, 270, 381, 24))
        self.PoscarOpenGLFrame = QFrame(ChooseFileWindow)
        self.PoscarOpenGLFrame.setObjectName(u"PoscarOpenGLFrame")
        self.PoscarOpenGLFrame.setGeometry(QRect(10, 70, 381, 181))
        self.PoscarOpenGLFrame.setFrameShape(QFrame.StyledPanel)
        self.PoscarOpenGLFrame.setFrameShadow(QFrame.Raised)
        self.PoscarOpenGL = QOpenGLWidget(self.PoscarOpenGLFrame)
        self.PoscarOpenGL.setObjectName(u"PoscarOpenGL")
        self.PoscarOpenGL.setGeometry(QRect(10, 10, 361, 161))

        self.retranslateUi(ChooseFileWindow)

        QMetaObject.connectSlotsByName(ChooseFileWindow)
    # setupUi

    def retranslateUi(self, ChooseFileWindow):
        ChooseFileWindow.setWindowTitle(QCoreApplication.translate("ChooseFileWindow", u"Choose POSCAR file", None))
        self.PoscarChooseSubmitButton.setText(QCoreApplication.translate("ChooseFileWindow", u"Submit", None))
    # retranslateUi

