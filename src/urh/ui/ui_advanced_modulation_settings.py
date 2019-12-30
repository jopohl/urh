# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'advanced_modulation_settings.ui'
##
## Created by: Qt User Interface Compiler version 5.14.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *

class Ui_DialogAdvancedModSettings(object):
    def setupUi(self, DialogAdvancedModSettings):
        if DialogAdvancedModSettings.objectName():
            DialogAdvancedModSettings.setObjectName(u"DialogAdvancedModSettings")
        DialogAdvancedModSettings.resize(527, 501)
        self.verticalLayout_3 = QVBoxLayout(DialogAdvancedModSettings)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox = QGroupBox(DialogAdvancedModSettings)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setWordWrap(True)

        self.verticalLayout.addWidget(self.label)

        self.spinBoxPauseThreshold = QSpinBox(self.groupBox)
        self.spinBoxPauseThreshold.setObjectName(u"spinBoxPauseThreshold")
        self.spinBoxPauseThreshold.setMinimum(0)
        self.spinBoxPauseThreshold.setMaximum(999999999)
        self.spinBoxPauseThreshold.setValue(8)

        self.verticalLayout.addWidget(self.spinBoxPauseThreshold)


        self.verticalLayout_3.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(DialogAdvancedModSettings)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.label_2)

        self.spinBoxMessageLengthDivisor = QSpinBox(self.groupBox_2)
        self.spinBoxMessageLengthDivisor.setObjectName(u"spinBoxMessageLengthDivisor")
        self.spinBoxMessageLengthDivisor.setMinimum(1)
        self.spinBoxMessageLengthDivisor.setMaximum(999999999)

        self.verticalLayout_2.addWidget(self.spinBoxMessageLengthDivisor)


        self.verticalLayout_3.addWidget(self.groupBox_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(DialogAdvancedModSettings)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout_3.addWidget(self.buttonBox)


        self.retranslateUi(DialogAdvancedModSettings)
        self.buttonBox.accepted.connect(DialogAdvancedModSettings.accept)
        self.buttonBox.rejected.connect(DialogAdvancedModSettings.reject)
    # setupUi

    def retranslateUi(self, DialogAdvancedModSettings):
        DialogAdvancedModSettings.setWindowTitle(QCoreApplication.translate("DialogAdvancedModSettings", u"Advanced Modulation Settings", None))
        self.groupBox.setTitle(QCoreApplication.translate("DialogAdvancedModSettings", u"Pause Threshold", None))
        self.label.setText(QCoreApplication.translate("DialogAdvancedModSettings", u"<html><head/><body><p>The pause threshold gives you control <span style=\" font-weight:600;\">when to insert a message break.</span></p><p>The pause threshold is the maximum length of consecutive zero bits represented by a pause before a new message begins.</p><p>Special value is 0 to disable message breaking completely.</p></body></html>", None))
        self.spinBoxPauseThreshold.setSpecialValueText(QCoreApplication.translate("DialogAdvancedModSettings", u"Disable", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("DialogAdvancedModSettings", u"Message Length Divisor", None))
        self.label_2.setText(QCoreApplication.translate("DialogAdvancedModSettings", u"<html><head/><body><p>With the message <span style=\" font-weight:600;\">divisor length</span> you can control the minimum message length in a flexible way. URH will try to demodulate signals in such a way, that the resulting message has a number of bits that is divisble by the configured divisor. <br/><br/><span style=\" font-style:italic;\">How does the zero padding work? Remaining zero bits are taken from the pause behind the message if possible.</span></p></body></html>", None))
    # retranslateUi

