# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'VRPrintGUIMJScvM.ui'
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
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QFrame, QMainWindow,
    QSizePolicy, QTextBrowser, QVBoxLayout, QWidget)
import QT_GUI.Resource_rc

class Ui_VRPrint(object):
    def setupUi(self, VRPrint):
        if not VRPrint.objectName():
            VRPrint.setObjectName(u"VRPrint")
        VRPrint.resize(450, 300)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(VRPrint.sizePolicy().hasHeightForWidth())
        VRPrint.setSizePolicy(sizePolicy)
        VRPrint.setMinimumSize(QSize(450, 300))
        palette = QPalette()
        brush = QBrush(QColor(0, 243, 243, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        brush1 = QBrush(QColor(154, 154, 154, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush1)
        brush2 = QBrush(QColor(229, 229, 229, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Light, brush2)
        brush3 = QBrush(QColor(227, 227, 227, 255))
        brush3.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Midlight, brush3)
        brush4 = QBrush(QColor(0, 234, 234, 255))
        brush4.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Text, brush4)
        brush5 = QBrush(QColor(170, 255, 255, 255))
        brush5.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.BrightText, brush5)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush4)
        brush6 = QBrush(QColor(0, 0, 0, 255))
        brush6.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush6)
        palette.setBrush(QPalette.Active, QPalette.Window, brush6)
        brush7 = QBrush(QColor(0, 77, 136, 255))
        brush7.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Highlight, brush7)
        brush8 = QBrush(QColor(0, 136, 136, 255))
        brush8.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.HighlightedText, brush8)
        brush9 = QBrush(QColor(85, 0, 0, 255))
        brush9.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.LinkVisited, brush9)
        brush10 = QBrush(QColor(107, 107, 107, 255))
        brush10.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush10)
        brush11 = QBrush(QColor(100, 100, 86, 255))
        brush11.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.ToolTipBase, brush11)
        brush12 = QBrush(QColor(0, 239, 239, 255))
        brush12.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.ToolTipText, brush12)
        brush13 = QBrush(QColor(0, 234, 234, 128))
        brush13.setStyle(Qt.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Active, QPalette.PlaceholderText, brush13)
#endif
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Light, brush2)
        palette.setBrush(QPalette.Inactive, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.BrightText, brush5)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush6)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush6)
        palette.setBrush(QPalette.Inactive, QPalette.Highlight, brush7)
        palette.setBrush(QPalette.Inactive, QPalette.HighlightedText, brush8)
        palette.setBrush(QPalette.Inactive, QPalette.LinkVisited, brush9)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush10)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush11)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush12)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush13)
#endif
        brush14 = QBrush(QColor(120, 120, 120, 255))
        brush14.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush14)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Light, brush2)
        palette.setBrush(QPalette.Disabled, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush14)
        palette.setBrush(QPalette.Disabled, QPalette.BrightText, brush5)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush14)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush6)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush6)
        brush15 = QBrush(QColor(0, 120, 215, 255))
        brush15.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Highlight, brush15)
        palette.setBrush(QPalette.Disabled, QPalette.HighlightedText, brush8)
        palette.setBrush(QPalette.Disabled, QPalette.LinkVisited, brush9)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush10)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush11)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush12)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush13)
#endif
        VRPrint.setPalette(palette)
        font = QFont()
        font.setFamilies([u"Times New Roman"])
        font.setPointSize(10)
        VRPrint.setFont(font)
        VRPrint.setContextMenuPolicy(Qt.DefaultContextMenu)
        icon = QIcon()
        icon.addFile(u":/VRlogo/VR-logo.ico", QSize(), QIcon.Normal, QIcon.Off)
        VRPrint.setWindowIcon(icon)
        VRPrint.setStyleSheet(u"QMainWindow{\n"
"gridline-color: rgb(53, 0, 80);\n"
"border-color: rgb(78, 0, 117);\n"
"}\n"
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
"QScrollBar"
                        "::add-line:hover:vertical, QScrollBar::sub-line:hover:vertical {\n"
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
"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"    background: none;\n"
"}\n"
"QTextBrowser{border-image: url(:/background/belka.jpg) 0 0 0 0 scratch scratch;}")
        VRPrint.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.MainWidget = QWidget(VRPrint)
        self.MainWidget.setObjectName(u"MainWidget")
        sizePolicy.setHeightForWidth(self.MainWidget.sizePolicy().hasHeightForWidth())
        self.MainWidget.setSizePolicy(sizePolicy)
        self.MainWidget.setContextMenuPolicy(Qt.NoContextMenu)
        self.verticalLayout = QVBoxLayout(self.MainWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.Logger = QTextBrowser(self.MainWidget)
        self.Logger.setObjectName(u"Logger")
        self.Logger.setEnabled(True)
        sizePolicy.setHeightForWidth(self.Logger.sizePolicy().hasHeightForWidth())
        self.Logger.setSizePolicy(sizePolicy)
        self.Logger.setSizeIncrement(QSize(0, 0))
        palette1 = QPalette()
        palette1.setBrush(QPalette.Active, QPalette.WindowText, brush)
        palette1.setBrush(QPalette.Active, QPalette.Button, brush1)
        palette1.setBrush(QPalette.Active, QPalette.Light, brush2)
        palette1.setBrush(QPalette.Active, QPalette.Midlight, brush3)
        palette1.setBrush(QPalette.Active, QPalette.Text, brush4)
        palette1.setBrush(QPalette.Active, QPalette.BrightText, brush5)
        palette1.setBrush(QPalette.Active, QPalette.ButtonText, brush4)
        brush16 = QBrush(QColor(0, 0, 0, 255))
        brush16.setStyle(Qt.NoBrush)
        palette1.setBrush(QPalette.Active, QPalette.Base, brush16)
        palette1.setBrush(QPalette.Active, QPalette.Window, brush6)
        palette1.setBrush(QPalette.Active, QPalette.Highlight, brush7)
        palette1.setBrush(QPalette.Active, QPalette.HighlightedText, brush8)
        palette1.setBrush(QPalette.Active, QPalette.LinkVisited, brush9)
        palette1.setBrush(QPalette.Active, QPalette.AlternateBase, brush10)
        palette1.setBrush(QPalette.Active, QPalette.ToolTipBase, brush11)
        palette1.setBrush(QPalette.Active, QPalette.ToolTipText, brush12)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Active, QPalette.PlaceholderText, brush13)
#endif
        palette1.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette1.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette1.setBrush(QPalette.Inactive, QPalette.Light, brush2)
        palette1.setBrush(QPalette.Inactive, QPalette.Midlight, brush3)
        palette1.setBrush(QPalette.Inactive, QPalette.Text, brush4)
        palette1.setBrush(QPalette.Inactive, QPalette.BrightText, brush5)
        palette1.setBrush(QPalette.Inactive, QPalette.ButtonText, brush4)
        brush17 = QBrush(QColor(0, 0, 0, 255))
        brush17.setStyle(Qt.NoBrush)
        palette1.setBrush(QPalette.Inactive, QPalette.Base, brush17)
        palette1.setBrush(QPalette.Inactive, QPalette.Window, brush6)
        palette1.setBrush(QPalette.Inactive, QPalette.Highlight, brush7)
        palette1.setBrush(QPalette.Inactive, QPalette.HighlightedText, brush8)
        palette1.setBrush(QPalette.Inactive, QPalette.LinkVisited, brush9)
        palette1.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush10)
        palette1.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush11)
        palette1.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush12)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush13)
#endif
        palette1.setBrush(QPalette.Disabled, QPalette.WindowText, brush14)
        palette1.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette1.setBrush(QPalette.Disabled, QPalette.Light, brush2)
        palette1.setBrush(QPalette.Disabled, QPalette.Midlight, brush3)
        palette1.setBrush(QPalette.Disabled, QPalette.Text, brush14)
        palette1.setBrush(QPalette.Disabled, QPalette.BrightText, brush5)
        palette1.setBrush(QPalette.Disabled, QPalette.ButtonText, brush14)
        brush18 = QBrush(QColor(0, 0, 0, 255))
        brush18.setStyle(Qt.NoBrush)
        palette1.setBrush(QPalette.Disabled, QPalette.Base, brush18)
        palette1.setBrush(QPalette.Disabled, QPalette.Window, brush6)
        palette1.setBrush(QPalette.Disabled, QPalette.Highlight, brush15)
        palette1.setBrush(QPalette.Disabled, QPalette.HighlightedText, brush8)
        palette1.setBrush(QPalette.Disabled, QPalette.LinkVisited, brush9)
        palette1.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush10)
        palette1.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush11)
        palette1.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush12)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush13)
#endif
        self.Logger.setPalette(palette1)
        self.Logger.setFont(font)
        self.Logger.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.Logger.setAutoFillBackground(False)
        self.Logger.setStyleSheet(u"")
        self.Logger.setFrameShape(QFrame.Box)
        self.Logger.setFrameShadow(QFrame.Sunken)
        self.Logger.setLineWidth(3)
        self.Logger.setMidLineWidth(0)
        self.Logger.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.Logger.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.Logger.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.Logger.setOpenLinks(True)

        self.verticalLayout.addWidget(self.Logger)

        VRPrint.setCentralWidget(self.MainWidget)

        self.retranslateUi(VRPrint)

        QMetaObject.connectSlotsByName(VRPrint)
    # setupUi

    def retranslateUi(self, VRPrint):
        VRPrint.setWindowTitle(QCoreApplication.translate("VRPrint", u"VaspReader (Message Console)", None))
        self.Logger.setHtml(QCoreApplication.translate("VRPrint", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Times New Roman'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:696;\">VaspReader for Windows 11 (64-bit), ver. 1.0.3 (created: 20.02.2022, lat.ver. 30.08.2022)</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:696;\">Email questions, suggestions and bug reports to: solovykh.aa19@physics.msu.ru</span></p></body></html>", None))
        self.Logger.setPlaceholderText("")
    # retranslateUi

