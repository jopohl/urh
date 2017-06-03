# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogCRC(object):
    def setupUi(self, DialogCRC):
        DialogCRC.setObjectName("DialogCRC")
        DialogCRC.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(DialogCRC)
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtWidgets.QLabel(DialogCRC)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.spinBoxDataStart = QtWidgets.QSpinBox(DialogCRC)
        self.spinBoxDataStart.setObjectName("spinBoxDataStart")
        self.gridLayout.addWidget(self.spinBoxDataStart, 1, 1, 1, 1)
        self.spinBoxDataEnd = QtWidgets.QSpinBox(DialogCRC)
        self.spinBoxDataEnd.setObjectName("spinBoxDataEnd")
        self.gridLayout.addWidget(self.spinBoxDataEnd, 2, 1, 1, 1)
        self.label = QtWidgets.QLabel(DialogCRC)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.comboBoxCRCFunction = QtWidgets.QComboBox(DialogCRC)
        self.comboBoxCRCFunction.setObjectName("comboBoxCRCFunction")
        self.comboBoxCRCFunction.addItem("")
        self.comboBoxCRCFunction.addItem("")
        self.gridLayout.addWidget(self.comboBoxCRCFunction, 3, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 107, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 1, 1, 1)
        self.comboBoxCRCName = QtWidgets.QComboBox(DialogCRC)
        self.comboBoxCRCName.setEditable(True)
        self.comboBoxCRCName.setObjectName("comboBoxCRCName")
        self.gridLayout.addWidget(self.comboBoxCRCName, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(DialogCRC)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(DialogCRC)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(DialogCRC)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.lineEditCRCPolynomial = QtWidgets.QLineEdit(DialogCRC)
        self.lineEditCRCPolynomial.setObjectName("lineEditCRCPolynomial")
        self.gridLayout.addWidget(self.lineEditCRCPolynomial, 4, 1, 1, 1)

        self.retranslateUi(DialogCRC)
        QtCore.QMetaObject.connectSlotsByName(DialogCRC)

    def retranslateUi(self, DialogCRC):
        _translate = QtCore.QCoreApplication.translate
        DialogCRC.setWindowTitle(_translate("DialogCRC", "Configure CRC"))
        self.label_4.setText(_translate("DialogCRC", "Name:"))
        self.spinBoxDataStart.setToolTip(_translate("DialogCRC", "Negative values are allowed."))
        self.spinBoxDataEnd.setToolTip(_translate("DialogCRC", "Negative values are allowed."))
        self.label.setToolTip(_translate("DialogCRC", "Negative values are allowed."))
        self.label.setText(_translate("DialogCRC", "Data Start:"))
        self.comboBoxCRCFunction.setItemText(0, _translate("DialogCRC", "WSP CRC 8"))
        self.comboBoxCRCFunction.setItemText(1, _translate("DialogCRC", "WSP CRC 4"))
        self.label_2.setToolTip(_translate("DialogCRC", "Negative values are allowed."))
        self.label_2.setText(_translate("DialogCRC", "Data End:"))
        self.label_3.setText(_translate("DialogCRC", "CRC Function:"))
        self.label_5.setText(_translate("DialogCRC", "Custom CRC Polynomial:"))

