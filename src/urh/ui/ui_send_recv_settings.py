# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SendRecvSettingsDialog(object):
    def setupUi(self, SendRecvSettingsDialog):
        SendRecvSettingsDialog.setObjectName("SendRecvSettingsDialog")
        SendRecvSettingsDialog.resize(708, 690)
        self.gridLayout_2 = QtWidgets.QGridLayout(SendRecvSettingsDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.comboBoxProfiles = QtWidgets.QComboBox(SendRecvSettingsDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBoxProfiles.sizePolicy().hasHeightForWidth())
        self.comboBoxProfiles.setSizePolicy(sizePolicy)
        self.comboBoxProfiles.setEditable(True)
        self.comboBoxProfiles.setInsertPolicy(QtWidgets.QComboBox.InsertAtCurrent)
        self.comboBoxProfiles.setObjectName("comboBoxProfiles")
        self.gridLayout_2.addWidget(self.comboBoxProfiles, 0, 0, 1, 1)
        self.btnRemoveProfile = QtWidgets.QToolButton(SendRecvSettingsDialog)
        icon = QtGui.QIcon.fromTheme("list-remove")
        self.btnRemoveProfile.setIcon(icon)
        self.btnRemoveProfile.setObjectName("btnRemoveProfile")
        self.gridLayout_2.addWidget(self.btnRemoveProfile, 0, 2, 1, 1)
        self.btnAddProfile = QtWidgets.QToolButton(SendRecvSettingsDialog)
        icon = QtGui.QIcon.fromTheme("list-add")
        self.btnAddProfile.setIcon(icon)
        self.btnAddProfile.setObjectName("btnAddProfile")
        self.gridLayout_2.addWidget(self.btnAddProfile, 0, 1, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(SendRecvSettingsDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_receive = QtWidgets.QWidget()
        self.tab_receive.setObjectName("tab_receive")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab_receive)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget.addTab(self.tab_receive, "")
        self.tab_send = QtWidgets.QWidget()
        self.tab_send.setObjectName("tab_send")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab_send)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabWidget.addTab(self.tab_send, "")
        self.gridLayout_2.addWidget(self.tabWidget, 1, 0, 1, 3)

        self.retranslateUi(SendRecvSettingsDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(SendRecvSettingsDialog)

    def retranslateUi(self, SendRecvSettingsDialog):
        _translate = QtCore.QCoreApplication.translate
        SendRecvSettingsDialog.setWindowTitle(_translate("SendRecvSettingsDialog", "Dialog"))
        self.btnRemoveProfile.setText(_translate("SendRecvSettingsDialog", "..."))
        self.btnAddProfile.setText(_translate("SendRecvSettingsDialog", "..."))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_receive), _translate("SendRecvSettingsDialog", "Receive"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_send), _translate("SendRecvSettingsDialog", "Send"))

from . import urh_rc
