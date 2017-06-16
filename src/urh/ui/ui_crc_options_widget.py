# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CRCOptions(object):
    def setupUi(self, CRCOptions):
        CRCOptions.setObjectName("CRCOptions")
        CRCOptions.resize(478, 397)
        self.gridLayout = QtWidgets.QGridLayout(CRCOptions)
        self.gridLayout.setObjectName("gridLayout")
        self.comboBoxCRCFunction = QtWidgets.QComboBox(CRCOptions)
        self.comboBoxCRCFunction.setObjectName("comboBoxCRCFunction")
        self.comboBoxCRCFunction.addItem("")
        self.comboBoxCRCFunction.addItem("")
        self.gridLayout.addWidget(self.comboBoxCRCFunction, 1, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(CRCOptions)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 107, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.lineEditCRCPolynomial = QtWidgets.QLineEdit(CRCOptions)
        self.lineEditCRCPolynomial.setObjectName("lineEditCRCPolynomial")
        self.gridLayout.addWidget(self.lineEditCRCPolynomial, 2, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(CRCOptions)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(CRCOptions)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tableViewDataRanges = QtWidgets.QTableView(self.groupBox)
        self.tableViewDataRanges.setObjectName("tableViewDataRanges")
        self.tableViewDataRanges.horizontalHeader().setHighlightSections(False)
        self.tableViewDataRanges.verticalHeader().setCascadingSectionResizes(False)
        self.tableViewDataRanges.verticalHeader().setHighlightSections(False)
        self.horizontalLayout.addWidget(self.tableViewDataRanges)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.btnAddRange = QtWidgets.QToolButton(self.groupBox)
        icon = QtGui.QIcon.fromTheme("list-add")
        self.btnAddRange.setIcon(icon)
        self.btnAddRange.setObjectName("btnAddRange")
        self.verticalLayout.addWidget(self.btnAddRange)
        self.btnRemoveRange = QtWidgets.QToolButton(self.groupBox)
        icon = QtGui.QIcon.fromTheme("list-remove")
        self.btnRemoveRange.setIcon(icon)
        self.btnRemoveRange.setObjectName("btnRemoveRange")
        self.verticalLayout.addWidget(self.btnRemoveRange)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.gridLayout.addWidget(self.groupBox, 3, 0, 1, 2)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 3, 2, 1, 1)

        self.retranslateUi(CRCOptions)
        QtCore.QMetaObject.connectSlotsByName(CRCOptions)

    def retranslateUi(self, CRCOptions):
        _translate = QtCore.QCoreApplication.translate
        CRCOptions.setWindowTitle(_translate("CRCOptions", "Configure CRC"))
        self.comboBoxCRCFunction.setItemText(0, _translate("CRCOptions", "WSP CRC 8"))
        self.comboBoxCRCFunction.setItemText(1, _translate("CRCOptions", "WSP CRC 4"))
        self.label_5.setText(_translate("CRCOptions", "Custom CRC polynomial:"))
        self.label_3.setText(_translate("CRCOptions", "Predefined CRC function:"))
        self.groupBox.setTitle(_translate("CRCOptions", "Configure data ranges for CRC"))
        self.btnAddRange.setText(_translate("CRCOptions", "..."))
        self.btnRemoveRange.setText(_translate("CRCOptions", "..."))

