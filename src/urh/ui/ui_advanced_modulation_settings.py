# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogAdvancedModSettings(object):
    def setupUi(self, DialogAdvancedModSettings):
        DialogAdvancedModSettings.setObjectName("DialogAdvancedModSettings")
        DialogAdvancedModSettings.resize(527, 501)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(DialogAdvancedModSettings)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox = QtWidgets.QGroupBox(DialogAdvancedModSettings)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.spinBoxPauseThreshold = QtWidgets.QSpinBox(self.groupBox)
        self.spinBoxPauseThreshold.setMinimum(0)
        self.spinBoxPauseThreshold.setMaximum(999999999)
        self.spinBoxPauseThreshold.setProperty("value", 8)
        self.spinBoxPauseThreshold.setObjectName("spinBoxPauseThreshold")
        self.verticalLayout.addWidget(self.spinBoxPauseThreshold)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(DialogAdvancedModSettings)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.spinBoxMessageLengthDivisor = QtWidgets.QSpinBox(self.groupBox_2)
        self.spinBoxMessageLengthDivisor.setMinimum(1)
        self.spinBoxMessageLengthDivisor.setObjectName("spinBoxMessageLengthDivisor")
        self.verticalLayout_2.addWidget(self.spinBoxMessageLengthDivisor)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogAdvancedModSettings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(DialogAdvancedModSettings)
        self.buttonBox.accepted.connect(DialogAdvancedModSettings.accept)
        self.buttonBox.rejected.connect(DialogAdvancedModSettings.reject)

    def retranslateUi(self, DialogAdvancedModSettings):
        _translate = QtCore.QCoreApplication.translate
        DialogAdvancedModSettings.setWindowTitle(_translate("DialogAdvancedModSettings", "Advanced Modulation Settings"))
        self.groupBox.setTitle(_translate("DialogAdvancedModSettings", "Pause Threshold"))
        self.label.setText(_translate("DialogAdvancedModSettings", "<html><head/><body><p>The pause threshold gives you control <span style=\" font-weight:600;\">when to insert a message break.</span></p><p>The pause threshold is the maximum length of consecutive zero bits represented by a pause before a new message begins.</p><p>Special value is 0 to disable message breaking completely.</p></body></html>"))
        self.spinBoxPauseThreshold.setSpecialValueText(_translate("DialogAdvancedModSettings", "Disable"))
        self.groupBox_2.setTitle(_translate("DialogAdvancedModSettings", "Message Length Divisor"))
        self.label_2.setText(_translate("DialogAdvancedModSettings", "<html><head/><body><p>With the message <span style=\" font-weight:600;\">divisor length</span> you can control the minimum message length in a flexible way. URH will try to demodulate signals in such a way, that the resulting message has a number of bits that is divisble by the configured divisor. <br/><br/><span style=\" font-style:italic;\">How does the zero padding work? Remaining zero bits are taken from the pause behind the message if possible.</span></p></body></html>"))

