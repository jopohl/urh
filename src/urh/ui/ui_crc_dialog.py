# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogCRC(object):
    def setupUi(self, DialogCRC):
        DialogCRC.setObjectName("DialogCRC")
        DialogCRC.resize(464, 294)
        self.gridLayout = QtWidgets.QGridLayout(DialogCRC)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(DialogCRC)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(DialogCRC)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.spinBoxDataEnd = QtWidgets.QSpinBox(DialogCRC)
        self.spinBoxDataEnd.setMinimum(-999)
        self.spinBoxDataEnd.setMaximum(999)
        self.spinBoxDataEnd.setObjectName("spinBoxDataEnd")
        self.gridLayout.addWidget(self.spinBoxDataEnd, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 137, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.spinBoxDataStart = QtWidgets.QSpinBox(DialogCRC)
        self.spinBoxDataStart.setMinimum(-999)
        self.spinBoxDataStart.setMaximum(999)
        self.spinBoxDataStart.setObjectName("spinBoxDataStart")
        self.gridLayout.addWidget(self.spinBoxDataStart, 1, 1, 1, 1)
        self.comboBoxCRCFunction = QtWidgets.QComboBox(DialogCRC)
        self.comboBoxCRCFunction.setObjectName("comboBoxCRCFunction")
        self.comboBoxCRCFunction.addItem("")
        self.comboBoxCRCFunction.addItem("")
        self.gridLayout.addWidget(self.comboBoxCRCFunction, 3, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(DialogCRC)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(DialogCRC)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.comboBoxName = QtWidgets.QComboBox(DialogCRC)
        self.comboBoxName.setEditable(True)
        self.comboBoxName.setObjectName("comboBoxName")
        self.gridLayout.addWidget(self.comboBoxName, 0, 1, 1, 1)

        self.retranslateUi(DialogCRC)
        QtCore.QMetaObject.connectSlotsByName(DialogCRC)

    def retranslateUi(self, DialogCRC):
        _translate = QtCore.QCoreApplication.translate
        DialogCRC.setWindowTitle(_translate("DialogCRC", "Configure CRC"))
        self.label.setToolTip(_translate("DialogCRC", "Negative values are allowed."))
        self.label.setText(_translate("DialogCRC", "Data Start:"))
        self.label_2.setToolTip(_translate("DialogCRC", "Negative values are allowed."))
        self.label_2.setText(_translate("DialogCRC", "Data End:"))
        self.spinBoxDataEnd.setToolTip(_translate("DialogCRC", "Negative values are allowed."))
        self.spinBoxDataStart.setToolTip(_translate("DialogCRC", "Negative values are allowed."))
        self.comboBoxCRCFunction.setItemText(0, _translate("DialogCRC", "WSP CRC 8"))
        self.comboBoxCRCFunction.setItemText(1, _translate("DialogCRC", "WSP CRC 4"))
        self.label_3.setText(_translate("DialogCRC", "CRC Function:"))
        self.label_4.setText(_translate("DialogCRC", "Name:"))

