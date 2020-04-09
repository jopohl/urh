# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DialogModulationParameters(object):
    def setupUi(self, DialogModulationParameters):
        DialogModulationParameters.setObjectName("DialogModulationParameters")
        DialogModulationParameters.resize(303, 286)
        DialogModulationParameters.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(DialogModulationParameters)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tblSymbolParameters = QtWidgets.QTableWidget(DialogModulationParameters)
        self.tblSymbolParameters.setShowGrid(False)
        self.tblSymbolParameters.setRowCount(2)
        self.tblSymbolParameters.setObjectName("tblSymbolParameters")
        self.tblSymbolParameters.setColumnCount(2)
        item = QtWidgets.QTableWidgetItem()
        self.tblSymbolParameters.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblSymbolParameters.setHorizontalHeaderItem(1, item)
        self.tblSymbolParameters.horizontalHeader().setVisible(True)
        self.tblSymbolParameters.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.tblSymbolParameters)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogModulationParameters)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DialogModulationParameters)

    def retranslateUi(self, DialogModulationParameters):
        _translate = QtCore.QCoreApplication.translate
        DialogModulationParameters.setWindowTitle(_translate("DialogModulationParameters", "Modulation Parameters"))
        item = self.tblSymbolParameters.horizontalHeaderItem(0)
        item.setText(_translate("DialogModulationParameters", "Symbol"))
        item = self.tblSymbolParameters.horizontalHeaderItem(1)
        item.setText(_translate("DialogModulationParameters", "Amplitude"))
