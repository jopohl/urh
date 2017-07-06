# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(707, 370)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_simulation = QtWidgets.QWidget()
        self.tab_simulation.setObjectName("tab_simulation")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.tab_simulation)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.textEditSimulation = QtWidgets.QTextEdit(self.tab_simulation)
        self.textEditSimulation.setObjectName("textEditSimulation")
        self.horizontalLayout.addWidget(self.textEditSimulation)
        self.tabWidget.addTab(self.tab_simulation, "")
        self.tab_device = QtWidgets.QWidget()
        self.tab_device.setObjectName("tab_device")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tab_device)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.textEditDevices = QtWidgets.QTextEdit(self.tab_device)
        self.textEditDevices.setObjectName("textEditDevices")
        self.horizontalLayout_2.addWidget(self.textEditDevices)
        self.tabWidget.addTab(self.tab_device, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        icon = QtGui.QIcon.fromTheme("media-playback-start")
        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_simulation), _translate("Dialog", "Simulation"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_device), _translate("Dialog", "Devices"))
        self.pushButton.setText(_translate("Dialog", "Start simulation ..."))

