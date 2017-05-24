# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FilterDialog(object):
    def setupUi(self, FilterDialog):
        FilterDialog.setObjectName("FilterDialog")
        FilterDialog.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(FilterDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(FilterDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.spinBoxNumTaps = QtWidgets.QSpinBox(FilterDialog)
        self.spinBoxNumTaps.setMinimum(1)
        self.spinBoxNumTaps.setMaximum(999999999)
        self.spinBoxNumTaps.setProperty("value", 10)
        self.spinBoxNumTaps.setObjectName("spinBoxNumTaps")
        self.gridLayout.addWidget(self.spinBoxNumTaps, 0, 1, 1, 1)
        self.radioButtonCustomTaps = QtWidgets.QRadioButton(FilterDialog)
        self.radioButtonCustomTaps.setObjectName("radioButtonCustomTaps")
        self.gridLayout.addWidget(self.radioButtonCustomTaps, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)
        self.radioButtonMovingAverage = QtWidgets.QRadioButton(FilterDialog)
        self.radioButtonMovingAverage.setObjectName("radioButtonMovingAverage")
        self.gridLayout.addWidget(self.radioButtonMovingAverage, 1, 0, 1, 2)
        self.tableWidget = QtWidgets.QTableWidget(FilterDialog)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(5)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.tableWidget, 3, 0, 1, 2)

        self.retranslateUi(FilterDialog)
        QtCore.QMetaObject.connectSlotsByName(FilterDialog)

    def retranslateUi(self, FilterDialog):
        _translate = QtCore.QCoreApplication.translate
        FilterDialog.setWindowTitle(_translate("FilterDialog", "Configure filter"))
        self.label.setText(_translate("FilterDialog", "Number of taps:"))
        self.radioButtonCustomTaps.setText(_translate("FilterDialog", "Custom taps:"))
        self.radioButtonMovingAverage.setText(_translate("FilterDialog", "Moving average filter"))
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("FilterDialog", "0"))
        item = self.tableWidget.verticalHeaderItem(1)
        item.setText(_translate("FilterDialog", "1"))
        item = self.tableWidget.verticalHeaderItem(2)
        item.setText(_translate("FilterDialog", "2"))
        item = self.tableWidget.verticalHeaderItem(3)
        item.setText(_translate("FilterDialog", "3"))
        item = self.tableWidget.verticalHeaderItem(4)
        item.setText(_translate("FilterDialog", "4"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("FilterDialog", "Index"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("FilterDialog", "Value"))

