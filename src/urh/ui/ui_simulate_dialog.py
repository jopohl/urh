# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SimulateDialog(object):
    def setupUi(self, SimulateDialog):
        SimulateDialog.setObjectName("SimulateDialog")
        SimulateDialog.resize(826, 374)
        SimulateDialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(SimulateDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.listViewSimulate = QtWidgets.QListView(SimulateDialog)
        self.listViewSimulate.setObjectName("listViewSimulate")
        self.gridLayout.addWidget(self.listViewSimulate, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(SimulateDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.spinBox = QtWidgets.QSpinBox(SimulateDialog)
        self.spinBox.setObjectName("spinBox")
        self.gridLayout.addWidget(self.spinBox, 3, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(SimulateDialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(SimulateDialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 6, 0, 1, 1)
        self.comboBox = QtWidgets.QComboBox(SimulateDialog)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.gridLayout.addWidget(self.comboBox, 7, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(SimulateDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.spinBox_2 = QtWidgets.QSpinBox(SimulateDialog)
        self.spinBox_2.setObjectName("spinBox_2")
        self.gridLayout.addWidget(self.spinBox_2, 5, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(SimulateDialog)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(SimulateDialog)
        icon = QtGui.QIcon.fromTheme("media-playback-start")
        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 8, 0, 1, 2)
        self.gvSimulator = QtWidgets.QGraphicsView(SimulateDialog)
        self.gvSimulator.setObjectName("gvSimulator")
        self.gridLayout.addWidget(self.gvSimulator, 1, 1, 7, 1)

        self.retranslateUi(SimulateDialog)
        QtCore.QMetaObject.connectSlotsByName(SimulateDialog)

    def retranslateUi(self, SimulateDialog):
        _translate = QtCore.QCoreApplication.translate
        SimulateDialog.setWindowTitle(_translate("SimulateDialog", "Simulation settings"))
        self.label.setText(_translate("SimulateDialog", "Simulate:"))
        self.spinBox.setSpecialValueText(_translate("SimulateDialog", "Infinite"))
        self.label_3.setText(_translate("SimulateDialog", "Timeout (in seconds):"))
        self.label_4.setText(_translate("SimulateDialog", "In case of an unexpected/overdue response:"))
        self.comboBox.setItemText(0, _translate("SimulateDialog", "Resend last message"))
        self.comboBox.setItemText(1, _translate("SimulateDialog", "Stop simulation"))
        self.comboBox.setItemText(2, _translate("SimulateDialog", "Restart simulation"))
        self.label_2.setText(_translate("SimulateDialog", "Repeat:"))
        self.label_5.setText(_translate("SimulateDialog", "Log settings:"))
        self.pushButton.setText(_translate("SimulateDialog", "Simulate"))

