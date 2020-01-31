# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'modulation_settings_widget.ui'
##
## Created by: Qt User Interface Compiler version 5.14.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *

from urh.ui.ElidedLabel import ElidedLabel

import urh.ui.urh_rc

class Ui_ModulationSettings(object):
    def setupUi(self, ModulationSettings):
        if ModulationSettings.objectName():
            ModulationSettings.setObjectName(u"ModulationSettings")
        ModulationSettings.resize(821, 635)
        self.verticalLayout = QVBoxLayout(ModulationSettings)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBoxSniffSettings = QGroupBox(ModulationSettings)
        self.groupBoxSniffSettings.setObjectName(u"groupBoxSniffSettings")
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBoxSniffSettings.setFont(font)
        self.groupBoxSniffSettings.setStyleSheet(u"QGroupBox\n"
"{\n"
"border: none;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"}\n"
"QGroupBox::indicator:unchecked {\n"
" image: url(:/icons/icons/collapse.svg)\n"
"}\n"
"QGroupBox::indicator:checked {\n"
" image: url(:/icons/icons/uncollapse.svg)\n"
"}")
        self.groupBoxSniffSettings.setFlat(True)
        self.groupBoxSniffSettings.setCheckable(True)
        self.gridLayout_3 = QGridLayout(self.groupBoxSniffSettings)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(-1, 15, -1, -1)
        self.frame = QFrame(self.groupBoxSniffSettings)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Plain)
        self.frame.setLineWidth(0)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.labelModulationProfile = QLabel(self.frame)
        self.labelModulationProfile.setObjectName(u"labelModulationProfile")

        self.verticalLayout_2.addWidget(self.labelModulationProfile)

        self.comboBoxModulationProfiles = QComboBox(self.frame)
        self.comboBoxModulationProfiles.setObjectName(u"comboBoxModulationProfiles")

        self.verticalLayout_2.addWidget(self.comboBoxModulationProfiles)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.labelCarrierFrequencyValue = QLabel(self.frame)
        self.labelCarrierFrequencyValue.setObjectName(u"labelCarrierFrequencyValue")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelCarrierFrequencyValue.sizePolicy().hasHeightForWidth())
        self.labelCarrierFrequencyValue.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.labelCarrierFrequencyValue, 0, 1, 1, 1)

        self.labelSampleRate = QLabel(self.frame)
        self.labelSampleRate.setObjectName(u"labelSampleRate")

        self.gridLayout.addWidget(self.labelSampleRate, 1, 3, 1, 1)

        self.line_2 = QFrame(self.frame)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line_2, 0, 5, 2, 1)

        self.labelCarrierFrequency = QLabel(self.frame)
        self.labelCarrierFrequency.setObjectName(u"labelCarrierFrequency")

        self.gridLayout.addWidget(self.labelCarrierFrequency, 0, 0, 1, 1)

        self.labelSamplesPerSymbol = QLabel(self.frame)
        self.labelSamplesPerSymbol.setObjectName(u"labelSamplesPerSymbol")

        self.gridLayout.addWidget(self.labelSamplesPerSymbol, 0, 3, 1, 1)

        self.labelSampleRateValue = QLabel(self.frame)
        self.labelSampleRateValue.setObjectName(u"labelSampleRateValue")

        self.gridLayout.addWidget(self.labelSampleRateValue, 1, 4, 1, 1)

        self.labelModulationType = QLabel(self.frame)
        self.labelModulationType.setObjectName(u"labelModulationType")

        self.gridLayout.addWidget(self.labelModulationType, 1, 0, 1, 1)

        self.line = QFrame(self.frame)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line, 0, 2, 2, 1)

        self.labelSamplesPerSymbolValue = QLabel(self.frame)
        self.labelSamplesPerSymbolValue.setObjectName(u"labelSamplesPerSymbolValue")

        self.gridLayout.addWidget(self.labelSamplesPerSymbolValue, 0, 4, 1, 1)

        self.labelModulationTypeValue = QLabel(self.frame)
        self.labelModulationTypeValue.setObjectName(u"labelModulationTypeValue")

        self.gridLayout.addWidget(self.labelModulationTypeValue, 1, 1, 1, 1)

        self.labelParameters = QLabel(self.frame)
        self.labelParameters.setObjectName(u"labelParameters")

        self.gridLayout.addWidget(self.labelParameters, 1, 6, 1, 1)

        self.labelParameterValues = ElidedLabel(self.frame)
        self.labelParameterValues.setObjectName(u"labelParameterValues")

        self.gridLayout.addWidget(self.labelParameterValues, 1, 7, 1, 1)

        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 6, 1, 1)

        self.labelBitsPerSymbol = QLabel(self.frame)
        self.labelBitsPerSymbol.setObjectName(u"labelBitsPerSymbol")

        self.gridLayout.addWidget(self.labelBitsPerSymbol, 0, 7, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout)

        self.btnConfigurationDialog = QPushButton(self.frame)
        self.btnConfigurationDialog.setObjectName(u"btnConfigurationDialog")
        icon = QIcon()
        iconThemeName = u"configure"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnConfigurationDialog.setIcon(icon)

        self.verticalLayout_2.addWidget(self.btnConfigurationDialog)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.gridLayout_3.addWidget(self.frame, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBoxSniffSettings)

        QWidget.setTabOrder(self.groupBoxSniffSettings, self.comboBoxModulationProfiles)
        QWidget.setTabOrder(self.comboBoxModulationProfiles, self.btnConfigurationDialog)

        self.retranslateUi(ModulationSettings)
        self.groupBoxSniffSettings.toggled.connect(self.frame.setVisible)
    # setupUi

    def retranslateUi(self, ModulationSettings):
        ModulationSettings.setWindowTitle(QCoreApplication.translate("ModulationSettings", u"Form", None))
        self.groupBoxSniffSettings.setTitle(QCoreApplication.translate("ModulationSettings", u"Modulation settings", None))
        self.labelModulationProfile.setText(QCoreApplication.translate("ModulationSettings", u"Choose profile:", None))
        self.labelCarrierFrequencyValue.setText(QCoreApplication.translate("ModulationSettings", u"TextLabel", None))
        self.labelSampleRate.setText(QCoreApplication.translate("ModulationSettings", u"Sample Rate:", None))
        self.labelCarrierFrequency.setText(QCoreApplication.translate("ModulationSettings", u"Carrier Frequency:", None))
        self.labelSamplesPerSymbol.setText(QCoreApplication.translate("ModulationSettings", u"Samples per Symbol:", None))
        self.labelSampleRateValue.setText(QCoreApplication.translate("ModulationSettings", u"TextLabel", None))
        self.labelModulationType.setText(QCoreApplication.translate("ModulationSettings", u"Modulation type:", None))
        self.labelSamplesPerSymbolValue.setText(QCoreApplication.translate("ModulationSettings", u"TextLabel", None))
        self.labelModulationTypeValue.setText(QCoreApplication.translate("ModulationSettings", u"TextLabel", None))
        self.labelParameters.setText(QCoreApplication.translate("ModulationSettings", u"Amplitudes in %:", None))
        self.labelParameterValues.setText(QCoreApplication.translate("ModulationSettings", u"0/100", None))
        self.label.setText(QCoreApplication.translate("ModulationSettings", u"Bits per Symbol:", None))
        self.labelBitsPerSymbol.setText(QCoreApplication.translate("ModulationSettings", u"1", None))
        self.btnConfigurationDialog.setText(QCoreApplication.translate("ModulationSettings", u"Open modulation configuration dialog...", None))
    # retranslateUi

