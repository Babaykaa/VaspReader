# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'VRRewriteFileGUISQhPSU.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QLayout, QMainWindow, QPushButton, QSizePolicy,
    QSpacerItem, QToolButton, QVBoxLayout, QWidget)
import QT_GUI.Resource_rc

class Ui_RewriteFile(object):
    def setupUi(self, RewriteFile):
        if not RewriteFile.objectName():
            RewriteFile.setObjectName(u"RewriteFile")
        RewriteFile.resize(440, 168)
        RewriteFile.setMinimumSize(QSize(440, 168))
        RewriteFile.setMaximumSize(QSize(440, 168))
        icon = QIcon()
        icon.addFile(u":/VRlogo/VR-logo.ico", QSize(), QIcon.Normal, QIcon.Off)
        RewriteFile.setWindowIcon(icon)
        RewriteFile.setStyleSheet(u"QPushButton {\n"
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
"QLabel{\n"
"background-color: rgb(255, 240, 202);\n"
"color: black;\n"
"font-weight: 600;\n"
"height:28px;}\n"
"QToolButton {\n"
"  background-color: rgb(255, 2"
                        "40, 202);\n"
"  color: black;\n"
"  font-weight: 600;\n"
"  border-radius: 6px;\n"
"  border: 2px solid rgb(85, 0, 127);\n"
"  border-style: outset;\n"
"}\n"
"QToolButton:disabled {\n"
"border-radius: 6px;\n"
"color: black;\n"
"font-weight: 600;\n"
"border: 2px solid rgb(75, 75, 75);\n"
"background-color:rgb(150, 150, 150);\n"
"border-style: outset;\n"
"}\n"
"QToolButton:hover {\n"
"  background-color: rgb(255, 212, 137);\n"
"  border: 1px solid #000000;\n"
"  border-style: outset;\n"
"}\n"
"QToolButton:pressed {\n"
"background-color: white;\n"
"border: 3px solid #000000;\n"
"}\n"
"QToolButton[popupMode=\"1\"] { /* only for MenuButtonPopup */\n"
"    padding-right: 10px; /* make way for the popup button */\n"
"}\n"
"QToolButton::menu-button {\n"
"    border: 2px solid rgb(85, 0, 127); /* rgb(255, 212, 137) */\n"
"    /* border-style: inline; */\n"
"    border-top-right-radius: 6px;\n"
"    border-bottom-right-radius: 6px;\n"
"    background-color:  rgb(255, 240, 202);\n"
"    /* 16px width + 4px for border = 2"
                        "0px allocated above */\n"
"    width: 16px;\n"
"}\n"
"QToolButton::menu-arrow {\n"
"    width: 12px;\n"
"    height: 12px;\n"
"}\n"
"QToolButton::menu-arrow:open {\n"
"    background-color: white;\n"
"    border: 3px solid #000000;\n"
"    border-top-right-radius: 6px;\n"
"    border-bottom-right-radius: 6px;\n"
"    width: 16px;\n"
"    height: 16px;\n"
"    top: 0.5px;\n"
"}\n"
"QToolButton#RewriteNoToolButton{\n"
"width: 60px;\n"
"border-style: outset;\n"
"}\n"
"QToolButton#RewriteYesToolButton{\n"
"width: 60px;\n"
"border-style: outset;\n"
"}\n"
"QPushButton#RewriteCancelButton:pressed {\n"
"background-color: white;\n"
"border: 3px solid #000000\n"
"border-style: inset;\n"
"}")
        RewriteFile.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.RewriteFileMainWidget = QWidget(RewriteFile)
        self.RewriteFileMainWidget.setObjectName(u"RewriteFileMainWidget")
        self.verticalLayout = QVBoxLayout(self.RewriteFileMainWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.RewriteAskLabel = QLabel(self.RewriteFileMainWidget)
        self.RewriteAskLabel.setObjectName(u"RewriteAskLabel")
        self.RewriteAskLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.RewriteAskLabel)

        self.OldFileFrame = QFrame(self.RewriteFileMainWidget)
        self.OldFileFrame.setObjectName(u"OldFileFrame")
        self.OldFileFrame.setFrameShape(QFrame.StyledPanel)
        self.OldFileFrame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.OldFileFrame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.OldFileLabel = QLabel(self.OldFileFrame)
        self.OldFileLabel.setObjectName(u"OldFileLabel")

        self.horizontalLayout_2.addWidget(self.OldFileLabel)

        self.OldParametersLabel = QLabel(self.OldFileFrame)
        self.OldParametersLabel.setObjectName(u"OldParametersLabel")
        self.OldParametersLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.OldParametersLabel)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 50)

        self.verticalLayout.addWidget(self.OldFileFrame)

        self.NewFileFrame = QFrame(self.RewriteFileMainWidget)
        self.NewFileFrame.setObjectName(u"NewFileFrame")
        self.NewFileFrame.setFrameShape(QFrame.StyledPanel)
        self.NewFileFrame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.NewFileFrame)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.NewFileLabel = QLabel(self.NewFileFrame)
        self.NewFileLabel.setObjectName(u"NewFileLabel")

        self.horizontalLayout_3.addWidget(self.NewFileLabel)

        self.NewParametersLabel = QLabel(self.NewFileFrame)
        self.NewParametersLabel.setObjectName(u"NewParametersLabel")
        self.NewParametersLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.NewParametersLabel)

        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 50)

        self.verticalLayout.addWidget(self.NewFileFrame)

        self.RewriteBottomLayout = QHBoxLayout()
        self.RewriteBottomLayout.setObjectName(u"RewriteBottomLayout")
        self.RewriteBottomLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.RewriteYesToolButton = QToolButton(self.RewriteFileMainWidget)
        self.RewriteYesToolButton.setObjectName(u"RewriteYesToolButton")
        self.RewriteYesToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.RewriteYesToolButton.setAutoRaise(False)

        self.RewriteBottomLayout.addWidget(self.RewriteYesToolButton)

        self.RewriteNoToolButton = QToolButton(self.RewriteFileMainWidget)
        self.RewriteNoToolButton.setObjectName(u"RewriteNoToolButton")
        self.RewriteNoToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.RewriteNoToolButton.setArrowType(Qt.NoArrow)

        self.RewriteBottomLayout.addWidget(self.RewriteNoToolButton)

        self.RewriteSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.RewriteBottomLayout.addItem(self.RewriteSpacer)

        self.RewriteCancelButton = QPushButton(self.RewriteFileMainWidget)
        self.RewriteCancelButton.setObjectName(u"RewriteCancelButton")

        self.RewriteBottomLayout.addWidget(self.RewriteCancelButton)

        self.RewriteBottomLayout.setStretch(0, 1)
        self.RewriteBottomLayout.setStretch(1, 1)
        self.RewriteBottomLayout.setStretch(2, 3)
        self.RewriteBottomLayout.setStretch(3, 1)

        self.verticalLayout.addLayout(self.RewriteBottomLayout)

        RewriteFile.setCentralWidget(self.RewriteFileMainWidget)

        self.retranslateUi(RewriteFile)

        QMetaObject.connectSlotsByName(RewriteFile)
    # setupUi

    def retranslateUi(self, RewriteFile):
        RewriteFile.setWindowTitle(QCoreApplication.translate("RewriteFile", u"VaspReader", None))
        self.RewriteAskLabel.setText(QCoreApplication.translate("RewriteFile", u"Do you want to rewrite the file?", None))
        self.OldFileLabel.setText(QCoreApplication.translate("RewriteFile", u"Old:", None))
        self.OldParametersLabel.setText("")
        self.NewFileLabel.setText(QCoreApplication.translate("RewriteFile", u"New:", None))
        self.NewParametersLabel.setText("")
        self.RewriteYesToolButton.setText(QCoreApplication.translate("RewriteFile", u"Yes", None))
        self.RewriteNoToolButton.setText(QCoreApplication.translate("RewriteFile", u"No", None))
        self.RewriteCancelButton.setText(QCoreApplication.translate("RewriteFile", u"Cancel", None))
    # retranslateUi

