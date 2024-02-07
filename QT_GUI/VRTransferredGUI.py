# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'VRTransferredGUIGbJoPn.ui'
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
    QMainWindow, QProgressBar, QSizePolicy, QVBoxLayout,
    QWidget)
import QT_GUI.Resource_rc

class Ui_VRTransferProgress(object):
    def setupUi(self, VRTransferProgress):
        if not VRTransferProgress.objectName():
            VRTransferProgress.setObjectName(u"VRTransferProgress")
        VRTransferProgress.resize(456, 126)
        VRTransferProgress.setMinimumSize(QSize(456, 126))
        VRTransferProgress.setMaximumSize(QSize(456, 126))
        icon = QIcon()
        icon.addFile(u":/VRlogo/VR-logo.ico", QSize(), QIcon.Normal, QIcon.Off)
        VRTransferProgress.setWindowIcon(icon)
        VRTransferProgress.setStyleSheet(u"QFrame{\n"
"border: 2px solid rgb(0, 0, 0);\n"
"border-radius: 6px;\n"
"background-color: rgb(255, 240, 202);\n"
"}\n"
"QLabel{\n"
"border: 0px solid rgb(0, 0, 0);\n"
"color: black;\n"
"font-weight: 600;\n"
"height:28px;}\n"
"QProgressBar {\n"
"    border: 2px solid rgb(0, 0, 0);\n"
"    border-radius: 6px;\n"
"    text-align: center;\n"
"    font-weight: 600;\n"
"}\n"
"QProgressBar::chunk {\n"
"    background-color: #00CDCD;\n"
"    width: 4px;\n"
"}")
        VRTransferProgress.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.VRTransferProgressWidget = QWidget(VRTransferProgress)
        self.VRTransferProgressWidget.setObjectName(u"VRTransferProgressWidget")
        self.verticalLayout = QVBoxLayout(self.VRTransferProgressWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.TransferTopWidget = QFrame(self.VRTransferProgressWidget)
        self.TransferTopWidget.setObjectName(u"TransferTopWidget")
        self.TransferTopWidget.setFrameShape(QFrame.StyledPanel)
        self.TransferTopWidget.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.TransferTopWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.TransferFileLabel = QLabel(self.TransferTopWidget)
        self.TransferFileLabel.setObjectName(u"TransferFileLabel")

        self.horizontalLayout.addWidget(self.TransferFileLabel)

        self.TransferFileName = QLabel(self.TransferTopWidget)
        self.TransferFileName.setObjectName(u"TransferFileName")
        self.TransferFileName.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout.addWidget(self.TransferFileName)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 50)

        self.verticalLayout.addWidget(self.TransferTopWidget)

        self.TransferProgress = QProgressBar(self.VRTransferProgressWidget)
        self.TransferProgress.setObjectName(u"TransferProgress")
        self.TransferProgress.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.TransferProgress.setValue(0)
        self.TransferProgress.setTextVisible(True)
        self.TransferProgress.setOrientation(Qt.Horizontal)
        self.TransferProgress.setInvertedAppearance(False)
        self.TransferProgress.setTextDirection(QProgressBar.TopToBottom)

        self.verticalLayout.addWidget(self.TransferProgress)

        self.TransferBottomWidget = QFrame(self.VRTransferProgressWidget)
        self.TransferBottomWidget.setObjectName(u"TransferBottomWidget")
        self.TransferBottomWidget.setFrameShape(QFrame.StyledPanel)
        self.TransferBottomWidget.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.TransferBottomWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.TransferredLabel = QLabel(self.TransferBottomWidget)
        self.TransferredLabel.setObjectName(u"TransferredLabel")

        self.horizontalLayout_2.addWidget(self.TransferredLabel)

        self.TransferredInfo = QLabel(self.TransferBottomWidget)
        self.TransferredInfo.setObjectName(u"TransferredInfo")

        self.horizontalLayout_2.addWidget(self.TransferredInfo)

        self.TransferFromLabel = QLabel(self.TransferBottomWidget)
        self.TransferFromLabel.setObjectName(u"TransferFromLabel")

        self.horizontalLayout_2.addWidget(self.TransferFromLabel)

        self.TransferAllInfo = QLabel(self.TransferBottomWidget)
        self.TransferAllInfo.setObjectName(u"TransferAllInfo")

        self.horizontalLayout_2.addWidget(self.TransferAllInfo)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 50)
        self.horizontalLayout_2.setStretch(2, 1)
        self.horizontalLayout_2.setStretch(3, 50)

        self.verticalLayout.addWidget(self.TransferBottomWidget)

        VRTransferProgress.setCentralWidget(self.VRTransferProgressWidget)

        self.retranslateUi(VRTransferProgress)

        QMetaObject.connectSlotsByName(VRTransferProgress)
    # setupUi

    def retranslateUi(self, VRTransferProgress):
        VRTransferProgress.setWindowTitle(QCoreApplication.translate("VRTransferProgress", u"VaspReader", None))
        self.TransferFileLabel.setText(QCoreApplication.translate("VRTransferProgress", u"File To Transfer:", None))
        self.TransferFileName.setText("")
        self.TransferredLabel.setText(QCoreApplication.translate("VRTransferProgress", u"Transferred:", None))
        self.TransferredInfo.setText("")
        self.TransferFromLabel.setText(QCoreApplication.translate("VRTransferProgress", u"From:", None))
        self.TransferAllInfo.setText("")
    # retranslateUi

