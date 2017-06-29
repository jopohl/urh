# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Interpretation(object):
    def setupUi(self, Interpretation):
        Interpretation.setObjectName("Interpretation")
        Interpretation.resize(631, 561)
        self.verticalLayout = QtWidgets.QVBoxLayout(Interpretation)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
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
        self.scrollArea.setWidget(self.scrlAreaSignals)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(Interpretation)
        QtCore.QMetaObject.connectSlotsByName(Interpretation)

    def retranslateUi(self, Interpretation):
        _translate = QtCore.QCoreApplication.translate
        Interpretation.setWindowTitle(_translate("Interpretation", "Form"))

from urh.ui.ScrollArea import ScrollArea
