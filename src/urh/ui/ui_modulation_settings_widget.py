# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ModulationSettings(object):
    def setupUi(self, ModulationSettings):
        ModulationSettings.setObjectName("ModulationSettings")
        ModulationSettings.resize(821, 635)
        self.verticalLayout = QtWidgets.QVBoxLayout(ModulationSettings)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBoxSniffSettings = QtWidgets.QGroupBox(ModulationSettings)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBoxSniffSettings.setFont(font)
        self.groupBoxSniffSettings.setStyleSheet(
            "QGroupBox\n"
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
            "}"
        )
        self.groupBoxSniffSettings.setFlat(True)
        self.groupBoxSniffSettings.setCheckable(True)
        self.groupBoxSniffSettings.setObjectName("groupBoxSniffSettings")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBoxSniffSettings)
        self.gridLayout_3.setContentsMargins(-1, 15, -1, -1)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.frame = QtWidgets.QFrame(self.groupBoxSniffSettings)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame.setLineWidth(0)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.labelModulationProfile = QtWidgets.QLabel(self.frame)
        self.labelModulationProfile.setObjectName("labelModulationProfile")
        self.verticalLayout_2.addWidget(self.labelModulationProfile)
        self.comboBoxModulationProfiles = QtWidgets.QComboBox(self.frame)
        self.comboBoxModulationProfiles.setObjectName("comboBoxModulationProfiles")
        self.verticalLayout_2.addWidget(self.comboBoxModulationProfiles)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.labelCarrierFrequencyValue = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.labelCarrierFrequencyValue.sizePolicy().hasHeightForWidth()
        )
        self.labelCarrierFrequencyValue.setSizePolicy(sizePolicy)
        self.labelCarrierFrequencyValue.setObjectName("labelCarrierFrequencyValue")
        self.gridLayout.addWidget(self.labelCarrierFrequencyValue, 0, 1, 1, 1)
        self.labelSampleRate = QtWidgets.QLabel(self.frame)
        self.labelSampleRate.setObjectName("labelSampleRate")
        self.gridLayout.addWidget(self.labelSampleRate, 1, 3, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.frame)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 0, 5, 2, 1)
        self.labelCarrierFrequency = QtWidgets.QLabel(self.frame)
        self.labelCarrierFrequency.setObjectName("labelCarrierFrequency")
        self.gridLayout.addWidget(self.labelCarrierFrequency, 0, 0, 1, 1)
        self.labelSamplesPerSymbol = QtWidgets.QLabel(self.frame)
        self.labelSamplesPerSymbol.setObjectName("labelSamplesPerSymbol")
        self.gridLayout.addWidget(self.labelSamplesPerSymbol, 0, 3, 1, 1)
        self.labelSampleRateValue = QtWidgets.QLabel(self.frame)
        self.labelSampleRateValue.setObjectName("labelSampleRateValue")
        self.gridLayout.addWidget(self.labelSampleRateValue, 1, 4, 1, 1)
        self.labelModulationType = QtWidgets.QLabel(self.frame)
        self.labelModulationType.setObjectName("labelModulationType")
        self.gridLayout.addWidget(self.labelModulationType, 1, 0, 1, 1)
        self.line = QtWidgets.QFrame(self.frame)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 0, 2, 2, 1)
        self.labelSamplesPerSymbolValue = QtWidgets.QLabel(self.frame)
        self.labelSamplesPerSymbolValue.setObjectName("labelSamplesPerSymbolValue")
        self.gridLayout.addWidget(self.labelSamplesPerSymbolValue, 0, 4, 1, 1)
        self.labelModulationTypeValue = QtWidgets.QLabel(self.frame)
        self.labelModulationTypeValue.setObjectName("labelModulationTypeValue")
        self.gridLayout.addWidget(self.labelModulationTypeValue, 1, 1, 1, 1)
        self.labelParameters = QtWidgets.QLabel(self.frame)
        self.labelParameters.setObjectName("labelParameters")
        self.gridLayout.addWidget(self.labelParameters, 1, 6, 1, 1)
        self.labelParameterValues = ElidedLabel(self.frame)
        self.labelParameterValues.setObjectName("labelParameterValues")
        self.gridLayout.addWidget(self.labelParameterValues, 1, 7, 1, 1)
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 6, 1, 1)
        self.labelBitsPerSymbol = QtWidgets.QLabel(self.frame)
        self.labelBitsPerSymbol.setObjectName("labelBitsPerSymbol")
        self.gridLayout.addWidget(self.labelBitsPerSymbol, 0, 7, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.btnConfigurationDialog = QtWidgets.QPushButton(self.frame)
        icon = QtGui.QIcon.fromTheme("configure")
        self.btnConfigurationDialog.setIcon(icon)
        self.btnConfigurationDialog.setObjectName("btnConfigurationDialog")
        self.verticalLayout_2.addWidget(self.btnConfigurationDialog)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.verticalLayout_2.addItem(spacerItem)
        self.gridLayout_3.addWidget(self.frame, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBoxSniffSettings)

        self.retranslateUi(ModulationSettings)
        self.groupBoxSniffSettings.toggled["bool"].connect(self.frame.setVisible)
        ModulationSettings.setTabOrder(
            self.groupBoxSniffSettings, self.comboBoxModulationProfiles
        )
        ModulationSettings.setTabOrder(
            self.comboBoxModulationProfiles, self.btnConfigurationDialog
        )

    def retranslateUi(self, ModulationSettings):
        _translate = QtCore.QCoreApplication.translate
        ModulationSettings.setWindowTitle(_translate("ModulationSettings", "Form"))
        self.groupBoxSniffSettings.setTitle(
            _translate("ModulationSettings", "Modulation settings")
        )
        self.labelModulationProfile.setText(
            _translate("ModulationSettings", "Choose profile:")
        )
        self.labelCarrierFrequencyValue.setText(
            _translate("ModulationSettings", "TextLabel")
        )
        self.labelSampleRate.setText(_translate("ModulationSettings", "Sample Rate:"))
        self.labelCarrierFrequency.setText(
            _translate("ModulationSettings", "Carrier Frequency:")
        )
        self.labelSamplesPerSymbol.setText(
            _translate("ModulationSettings", "Samples per Symbol:")
        )
        self.labelSampleRateValue.setText(_translate("ModulationSettings", "TextLabel"))
        self.labelModulationType.setText(
            _translate("ModulationSettings", "Modulation type:")
        )
        self.labelSamplesPerSymbolValue.setText(
            _translate("ModulationSettings", "TextLabel")
        )
        self.labelModulationTypeValue.setText(
            _translate("ModulationSettings", "TextLabel")
        )
        self.labelParameters.setText(
            _translate("ModulationSettings", "Amplitudes in %:")
        )
        self.labelParameterValues.setText(_translate("ModulationSettings", "0/100"))
        self.label.setText(_translate("ModulationSettings", "Bits per Symbol:"))
        self.labelBitsPerSymbol.setText(_translate("ModulationSettings", "1"))
        self.btnConfigurationDialog.setText(
            _translate("ModulationSettings", "Open modulation configuration dialog...")
        )


from urh.ui.ElidedLabel import ElidedLabel
from . import urh_rc
