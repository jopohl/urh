# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SimulateDialog(object):
    def setupUi(self, SimulateDialog):
        SimulateDialog.setObjectName("SimulateDialog")
        SimulateDialog.resize(925, 616)
        SimulateDialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(SimulateDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_2 = QtWidgets.QPushButton(SimulateDialog)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 17, 1, 1, 1)
        self.gvSimulator = QtWidgets.QGraphicsView(SimulateDialog)
        self.gvSimulator.setObjectName("gvSimulator")
        self.gridLayout.addWidget(self.gvSimulator, 2, 1, 15, 2)
        self.label_4 = QtWidgets.QLabel(SimulateDialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 16, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(SimulateDialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 14, 0, 1, 1)
        self.spinBox = QtWidgets.QSpinBox(SimulateDialog)
        self.spinBox.setObjectName("spinBox")
        self.gridLayout.addWidget(self.spinBox, 13, 0, 1, 1)
        self.label = QtWidgets.QLabel(SimulateDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(SimulateDialog)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 17, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(SimulateDialog)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(SimulateDialog)
        icon = QtGui.QIcon.fromTheme("media-playback-start")
        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 18, 0, 1, 3)
        self.comboBox = QtWidgets.QComboBox(SimulateDialog)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.gridLayout.addWidget(self.comboBox, 17, 0, 1, 1)
        self.spinBox_2 = QtWidgets.QSpinBox(SimulateDialog)
        self.spinBox_2.setObjectName("spinBox_2")
        self.gridLayout.addWidget(self.spinBox_2, 15, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(SimulateDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 12, 0, 1, 1)
        self.listViewSimulate = QtWidgets.QListView(SimulateDialog)
        self.listViewSimulate.setObjectName("listViewSimulate")
        self.gridLayout.addWidget(self.listViewSimulate, 2, 0, 10, 1)

        self.retranslateUi(SimulateDialog)
        QtCore.QMetaObject.connectSlotsByName(SimulateDialog)

    def retranslateUi(self, SimulateDialog):
        _translate = QtCore.QCoreApplication.translate
        SimulateDialog.setWindowTitle(_translate("SimulateDialog", "Simulation settings"))
        self.pushButton_2.setText(_translate("SimulateDialog", "Log all"))
        self.label_4.setText(_translate("SimulateDialog", "In case of an unexpected/overdue response:"))
        self.label_3.setText(_translate("SimulateDialog", "Timeout (in seconds):"))
        self.spinBox.setSpecialValueText(_translate("SimulateDialog", "Infinite"))
        self.label.setText(_translate("SimulateDialog", "Simulate:"))
        self.pushButton_3.setText(_translate("SimulateDialog", "Log none"))
        self.label_5.setText(_translate("SimulateDialog", "Log settings:"))
        self.pushButton.setText(_translate("SimulateDialog", "Simulate"))
        self.comboBox.setItemText(0, _translate("SimulateDialog", "Resend last message"))
        self.comboBox.setItemText(1, _translate("SimulateDialog", "Stop simulation"))
        self.comboBox.setItemText(2, _translate("SimulateDialog", "Restart simulation"))
        self.label_2.setText(_translate("SimulateDialog", "Repeat:"))

