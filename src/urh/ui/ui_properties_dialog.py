# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/joe/GIT/urh/ui/properties_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogLabels(object):
    def setupUi(self, DialogLabels):
        DialogLabels.setObjectName("DialogLabels")
        DialogLabels.resize(673, 336)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(DialogLabels)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tblViewProtoLabels = ProtocolLabelTableView(DialogLabels)
        self.tblViewProtoLabels.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tblViewProtoLabels.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tblViewProtoLabels.setObjectName("tblViewProtoLabels")
        self.horizontalLayout.addWidget(self.tblViewProtoLabels)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
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
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.btnConfirm = QtWidgets.QPushButton(DialogLabels)
        self.btnConfirm.setObjectName("btnConfirm")
        self.verticalLayout_2.addWidget(self.btnConfirm)

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
