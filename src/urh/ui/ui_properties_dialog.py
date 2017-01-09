# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogLabels(object):
    def setupUi(self, DialogLabels):
        DialogLabels.setObjectName("DialogLabels")
        DialogLabels.resize(714, 463)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(DialogLabels)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tblViewProtoLabels = ProtocolLabelTableView(DialogLabels)
        self.tblViewProtoLabels.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tblViewProtoLabels.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tblViewProtoLabels.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tblViewProtoLabels.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tblViewProtoLabels.setObjectName("tblViewProtoLabels")
        self.horizontalLayout.addWidget(self.tblViewProtoLabels)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(DialogLabels)
        font = QtGui.QFont()
        font.setUnderline(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.cbProtoView = QtWidgets.QComboBox(DialogLabels)
        self.cbProtoView.setObjectName("cbProtoView")
        self.cbProtoView.addItem("")
        self.cbProtoView.addItem("")
        self.cbProtoView.addItem("")
        self.horizontalLayout_2.addWidget(self.cbProtoView)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.btnConfirm = QtWidgets.QPushButton(DialogLabels)
        self.btnConfirm.setObjectName("btnConfirm")
        self.verticalLayout_3.addWidget(self.btnConfirm)

        self.retranslateUi(DialogLabels)
        QtCore.QMetaObject.connectSlotsByName(DialogLabels)

    def retranslateUi(self, DialogLabels):
        _translate = QtCore.QCoreApplication.translate
        DialogLabels.setWindowTitle(_translate("DialogLabels", "Manage Protocol Labels"))
        self.label.setText(_translate("DialogLabels", "View Type:"))
        self.cbProtoView.setItemText(0, _translate("DialogLabels", "Bits"))
        self.cbProtoView.setItemText(1, _translate("DialogLabels", "Hex"))
        self.cbProtoView.setItemText(2, _translate("DialogLabels", "ASCII"))
        self.btnConfirm.setText(_translate("DialogLabels", "Confirm"))

from urh.ui.views.ProtocolLabelTableView import ProtocolLabelTableView
