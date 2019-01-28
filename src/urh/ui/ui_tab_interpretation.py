# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Interpretation(object):
    def setupUi(self, Interpretation):
        Interpretation.setObjectName("Interpretation")
        Interpretation.resize(631, 561)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Interpretation)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.scrollArea = ScrollArea(Interpretation)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setAcceptDrops(True)
        self.scrollArea.setStyleSheet("")
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrlAreaSignals = QtWidgets.QWidget()
        self.scrlAreaSignals.setGeometry(QtCore.QRect(0, 0, 631, 561))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrlAreaSignals.sizePolicy().hasHeightForWidth())
        self.scrlAreaSignals.setSizePolicy(sizePolicy)
        self.scrlAreaSignals.setAutoFillBackground(True)
        self.scrlAreaSignals.setStyleSheet("")
        self.scrlAreaSignals.setObjectName("scrlAreaSignals")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrlAreaSignals)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(self.scrlAreaSignals)
        self.splitter.setStyleSheet("QSplitter::handle:vertical {\n"
"margin: 4px 0px;\n"
"    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, \n"
"stop:0 rgba(255, 255, 255, 0), \n"
"stop:0.5 rgba(100, 100, 100, 100), \n"
"stop:1 rgba(255, 255, 255, 0));\n"
"    image: url(:/icons/icons/splitter_handle_horizontal.svg);\n"
"}")
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setHandleWidth(6)
        self.splitter.setObjectName("splitter")
        self.labelGettingStarted = QtWidgets.QLabel(self.splitter)
        font = QtGui.QFont()
        font.setPointSize(32)
        self.labelGettingStarted.setFont(font)
        self.labelGettingStarted.setStyleSheet("")
        self.labelGettingStarted.setAlignment(QtCore.Qt.AlignCenter)
        self.labelGettingStarted.setWordWrap(True)
        self.labelGettingStarted.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.labelGettingStarted.setObjectName("labelGettingStarted")
        self.placeholderLabel = QtWidgets.QLabel(self.splitter)
        self.placeholderLabel.setText("")
        self.placeholderLabel.setObjectName("placeholderLabel")
        self.verticalLayout.addWidget(self.splitter)
        self.scrollArea.setWidget(self.scrlAreaSignals)
        self.horizontalLayout.addWidget(self.scrollArea)

        self.retranslateUi(Interpretation)

    def retranslateUi(self, Interpretation):
        _translate = QtCore.QCoreApplication.translate
        Interpretation.setWindowTitle(_translate("Interpretation", "Form"))
        self.labelGettingStarted.setText(_translate("Interpretation", "<html><head/><body><p>Open a file or record a new signal using the <b>File menu</b> to get started.</p></body></html>"))

from urh.ui.ScrollArea import ScrollArea
from . import urh_rc
