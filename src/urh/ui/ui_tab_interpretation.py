# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tab_interpretation.ui'
##
## Created by: Qt User Interface Compiler version 5.14.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *

from urh.ui.ScrollArea import ScrollArea

import urh.ui.urh_rc

class Ui_Interpretation(object):
    def setupUi(self, Interpretation):
        if Interpretation.objectName():
            Interpretation.setObjectName(u"Interpretation")
        Interpretation.resize(631, 561)
        self.horizontalLayout = QHBoxLayout(Interpretation)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = ScrollArea(Interpretation)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setAcceptDrops(True)
        self.scrollArea.setStyleSheet(u"")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(True)
        self.scrlAreaSignals = QWidget()
        self.scrlAreaSignals.setObjectName(u"scrlAreaSignals")
        self.scrlAreaSignals.setGeometry(QRect(0, 0, 631, 561))
        sizePolicy.setHeightForWidth(self.scrlAreaSignals.sizePolicy().hasHeightForWidth())
        self.scrlAreaSignals.setSizePolicy(sizePolicy)
        self.scrlAreaSignals.setAutoFillBackground(True)
        self.scrlAreaSignals.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(self.scrlAreaSignals)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(self.scrlAreaSignals)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setStyleSheet(u"QSplitter::handle:vertical {\n"
"margin: 4px 0px;\n"
"    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, \n"
"stop:0 rgba(255, 255, 255, 0), \n"
"stop:0.5 rgba(100, 100, 100, 100), \n"
"stop:1 rgba(255, 255, 255, 0));\n"
"	image: url(:/icons/icons/splitter_handle_horizontal.svg);\n"
"}")
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setHandleWidth(6)
        self.labelGettingStarted = QLabel(self.splitter)
        self.labelGettingStarted.setObjectName(u"labelGettingStarted")
        font = QFont()
        font.setPointSize(32)
        self.labelGettingStarted.setFont(font)
        self.labelGettingStarted.setStyleSheet(u"")
        self.labelGettingStarted.setAlignment(Qt.AlignCenter)
        self.labelGettingStarted.setWordWrap(True)
        self.labelGettingStarted.setTextInteractionFlags(Qt.NoTextInteraction)
        self.splitter.addWidget(self.labelGettingStarted)
        self.placeholderLabel = QLabel(self.splitter)
        self.placeholderLabel.setObjectName(u"placeholderLabel")
        self.splitter.addWidget(self.placeholderLabel)

        self.verticalLayout.addWidget(self.splitter)

        self.scrollArea.setWidget(self.scrlAreaSignals)

        self.horizontalLayout.addWidget(self.scrollArea)


        self.retranslateUi(Interpretation)
    # setupUi

    def retranslateUi(self, Interpretation):
        Interpretation.setWindowTitle(QCoreApplication.translate("Interpretation", u"Form", None))
        self.labelGettingStarted.setText(QCoreApplication.translate("Interpretation", u"<html><head/><body><p>Open a file or record a new signal using the <b>File menu</b> to get started.</p></body></html>", None))
        self.placeholderLabel.setText("")
    # retranslateUi

