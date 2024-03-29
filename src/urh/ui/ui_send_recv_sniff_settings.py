# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SniffSettings(object):
    def setupUi(self, SniffSettings):
        SniffSettings.setObjectName("SniffSettings")
        SniffSettings.resize(482, 510)
        self.verticalLayout = QtWidgets.QVBoxLayout(SniffSettings)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBoxSniffSettings = QtWidgets.QGroupBox(SniffSettings)
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
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.label_sniff_Center = QtWidgets.QLabel(self.frame)
        self.label_sniff_Center.setObjectName("label_sniff_Center")
        self.gridLayout.addWidget(self.label_sniff_Center, 2, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.spinbox_sniff_Noise = QtWidgets.QDoubleSpinBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.spinbox_sniff_Noise.sizePolicy().hasHeightForWidth()
        )
        self.spinbox_sniff_Noise.setSizePolicy(sizePolicy)
        self.spinbox_sniff_Noise.setDecimals(4)
        self.spinbox_sniff_Noise.setMaximum(1.0)
        self.spinbox_sniff_Noise.setObjectName("spinbox_sniff_Noise")
        self.horizontalLayout_3.addWidget(self.spinbox_sniff_Noise)
        self.checkBoxAdaptiveNoise = QtWidgets.QCheckBox(self.frame)
        self.checkBoxAdaptiveNoise.setObjectName("checkBoxAdaptiveNoise")
        self.horizontalLayout_3.addWidget(self.checkBoxAdaptiveNoise)
        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 1, 1, 1)
        self.label_sniff_Modulation = QtWidgets.QLabel(self.frame)
        self.label_sniff_Modulation.setObjectName("label_sniff_Modulation")
        self.gridLayout.addWidget(self.label_sniff_Modulation, 6, 0, 1, 1)
        self.label_sniff_Signal = QtWidgets.QLabel(self.frame)
        self.label_sniff_Signal.setObjectName("label_sniff_Signal")
        self.gridLayout.addWidget(self.label_sniff_Signal, 0, 0, 1, 1)
        self.spinbox_sniff_ErrorTolerance = QtWidgets.QSpinBox(self.frame)
        self.spinbox_sniff_ErrorTolerance.setMaximum(999999)
        self.spinbox_sniff_ErrorTolerance.setProperty("value", 5)
        self.spinbox_sniff_ErrorTolerance.setObjectName("spinbox_sniff_ErrorTolerance")
        self.gridLayout.addWidget(self.spinbox_sniff_ErrorTolerance, 5, 1, 1, 1)
        self.combox_sniff_Modulation = QtWidgets.QComboBox(self.frame)
        self.combox_sniff_Modulation.setObjectName("combox_sniff_Modulation")
        self.combox_sniff_Modulation.addItem("")
        self.combox_sniff_Modulation.addItem("")
        self.combox_sniff_Modulation.addItem("")
        self.gridLayout.addWidget(self.combox_sniff_Modulation, 6, 1, 1, 1)
        self.label_sniff_Tolerance = QtWidgets.QLabel(self.frame)
        self.label_sniff_Tolerance.setObjectName("label_sniff_Tolerance")
        self.gridLayout.addWidget(self.label_sniff_Tolerance, 5, 0, 1, 1)
        self.spinbox_sniff_SamplesPerSymbol = QtWidgets.QSpinBox(self.frame)
        self.spinbox_sniff_SamplesPerSymbol.setMinimum(1)
        self.spinbox_sniff_SamplesPerSymbol.setMaximum(999999999)
        self.spinbox_sniff_SamplesPerSymbol.setObjectName(
            "spinbox_sniff_SamplesPerSymbol"
        )
        self.gridLayout.addWidget(self.spinbox_sniff_SamplesPerSymbol, 4, 1, 1, 1)
        self.label_sniff_viewtype = QtWidgets.QLabel(self.frame)
        self.label_sniff_viewtype.setObjectName("label_sniff_viewtype")
        self.gridLayout.addWidget(self.label_sniff_viewtype, 9, 0, 1, 1)
        self.lineEdit_sniff_OutputFile = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.lineEdit_sniff_OutputFile.sizePolicy().hasHeightForWidth()
        )
        self.lineEdit_sniff_OutputFile.setSizePolicy(sizePolicy)
        self.lineEdit_sniff_OutputFile.setReadOnly(False)
        self.lineEdit_sniff_OutputFile.setClearButtonEnabled(True)
        self.lineEdit_sniff_OutputFile.setObjectName("lineEdit_sniff_OutputFile")
        self.gridLayout.addWidget(self.lineEdit_sniff_OutputFile, 10, 1, 1, 1)
        self.label_sniff_BitLength = QtWidgets.QLabel(self.frame)
        self.label_sniff_BitLength.setObjectName("label_sniff_BitLength")
        self.gridLayout.addWidget(self.label_sniff_BitLength, 4, 0, 1, 1)
        self.spinBoxCenterSpacing = QtWidgets.QDoubleSpinBox(self.frame)
        self.spinBoxCenterSpacing.setDecimals(4)
        self.spinBoxCenterSpacing.setMaximum(1.0)
        self.spinBoxCenterSpacing.setObjectName("spinBoxCenterSpacing")
        self.gridLayout.addWidget(self.spinBoxCenterSpacing, 3, 1, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.comboBox_sniff_signal = QtWidgets.QComboBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.comboBox_sniff_signal.sizePolicy().hasHeightForWidth()
        )
        self.comboBox_sniff_signal.setSizePolicy(sizePolicy)
        self.comboBox_sniff_signal.setObjectName("comboBox_sniff_signal")
        self.horizontalLayout_2.addWidget(self.comboBox_sniff_signal)
        self.btn_sniff_use_signal = QtWidgets.QPushButton(self.frame)
        self.btn_sniff_use_signal.setObjectName("btn_sniff_use_signal")
        self.horizontalLayout_2.addWidget(self.btn_sniff_use_signal)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 1, 1, 1)
        self.label_sniff_OutputFile = QtWidgets.QLabel(self.frame)
        self.label_sniff_OutputFile.setObjectName("label_sniff_OutputFile")
        self.gridLayout.addWidget(self.label_sniff_OutputFile, 10, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.spinbox_sniff_Center = QtWidgets.QDoubleSpinBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.spinbox_sniff_Center.sizePolicy().hasHeightForWidth()
        )
        self.spinbox_sniff_Center.setSizePolicy(sizePolicy)
        self.spinbox_sniff_Center.setDecimals(4)
        self.spinbox_sniff_Center.setMinimum(-3.14)
        self.spinbox_sniff_Center.setMaximum(3.14)
        self.spinbox_sniff_Center.setObjectName("spinbox_sniff_Center")
        self.horizontalLayout_4.addWidget(self.spinbox_sniff_Center)
        self.checkBoxAutoCenter = QtWidgets.QCheckBox(self.frame)
        self.checkBoxAutoCenter.setObjectName("checkBoxAutoCenter")
        self.horizontalLayout_4.addWidget(self.checkBoxAutoCenter)
        self.gridLayout.addLayout(self.horizontalLayout_4, 2, 1, 1, 1)
        self.label_sniff_encoding = QtWidgets.QLabel(self.frame)
        self.label_sniff_encoding.setObjectName("label_sniff_encoding")
        self.gridLayout.addWidget(self.label_sniff_encoding, 8, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comboBox_sniff_viewtype = QtWidgets.QComboBox(self.frame)
        self.comboBox_sniff_viewtype.setObjectName("comboBox_sniff_viewtype")
        self.comboBox_sniff_viewtype.addItem("")
        self.comboBox_sniff_viewtype.addItem("")
        self.comboBox_sniff_viewtype.addItem("")
        self.horizontalLayout.addWidget(self.comboBox_sniff_viewtype)
        self.checkBox_sniff_Timestamp = QtWidgets.QCheckBox(self.frame)
        self.checkBox_sniff_Timestamp.setObjectName("checkBox_sniff_Timestamp")
        self.horizontalLayout.addWidget(self.checkBox_sniff_Timestamp)
        self.gridLayout.addLayout(self.horizontalLayout, 9, 1, 1, 1)
        self.label_sniff_Noise = QtWidgets.QLabel(self.frame)
        self.label_sniff_Noise.setObjectName("label_sniff_Noise")
        self.gridLayout.addWidget(self.label_sniff_Noise, 1, 0, 1, 1)
        self.comboBox_sniff_encoding = QtWidgets.QComboBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.comboBox_sniff_encoding.sizePolicy().hasHeightForWidth()
        )
        self.comboBox_sniff_encoding.setSizePolicy(sizePolicy)
        self.comboBox_sniff_encoding.setObjectName("comboBox_sniff_encoding")
        self.gridLayout.addWidget(self.comboBox_sniff_encoding, 8, 1, 1, 1)
        self.labelCenterSpacing = QtWidgets.QLabel(self.frame)
        self.labelCenterSpacing.setObjectName("labelCenterSpacing")
        self.gridLayout.addWidget(self.labelCenterSpacing, 3, 0, 1, 1)
        self.labelBitsPerSymbol = QtWidgets.QLabel(self.frame)
        self.labelBitsPerSymbol.setObjectName("labelBitsPerSymbol")
        self.gridLayout.addWidget(self.labelBitsPerSymbol, 7, 0, 1, 1)
        self.spinBoxBitsPerSymbol = QtWidgets.QSpinBox(self.frame)
        self.spinBoxBitsPerSymbol.setMinimum(1)
        self.spinBoxBitsPerSymbol.setMaximum(10)
        self.spinBoxBitsPerSymbol.setObjectName("spinBoxBitsPerSymbol")
        self.gridLayout.addWidget(self.spinBoxBitsPerSymbol, 7, 1, 1, 1)
        self.gridLayout_3.addWidget(self.frame, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBoxSniffSettings)

        self.retranslateUi(SniffSettings)
        self.groupBoxSniffSettings.toggled["bool"].connect(self.frame.setVisible)
        SniffSettings.setTabOrder(self.groupBoxSniffSettings, self.spinbox_sniff_Noise)
        SniffSettings.setTabOrder(
            self.spinbox_sniff_Noise, self.spinbox_sniff_SamplesPerSymbol
        )
        SniffSettings.setTabOrder(
            self.spinbox_sniff_SamplesPerSymbol, self.spinbox_sniff_ErrorTolerance
        )
        SniffSettings.setTabOrder(
            self.spinbox_sniff_ErrorTolerance, self.combox_sniff_Modulation
        )
        SniffSettings.setTabOrder(
            self.combox_sniff_Modulation, self.comboBox_sniff_encoding
        )
        SniffSettings.setTabOrder(
            self.comboBox_sniff_encoding, self.comboBox_sniff_viewtype
        )
        SniffSettings.setTabOrder(
            self.comboBox_sniff_viewtype, self.checkBox_sniff_Timestamp
        )
        SniffSettings.setTabOrder(
            self.checkBox_sniff_Timestamp, self.lineEdit_sniff_OutputFile
        )

    def retranslateUi(self, SniffSettings):
        _translate = QtCore.QCoreApplication.translate
        SniffSettings.setWindowTitle(_translate("SniffSettings", "Form"))
        self.groupBoxSniffSettings.setTitle(
            _translate("SniffSettings", "Sniff settings")
        )
        self.label_sniff_Center.setText(_translate("SniffSettings", "Center:"))
        self.checkBoxAdaptiveNoise.setToolTip(
            _translate(
                "SniffSettings",
                "<html><head/><body><p>With adaptive noise URH will update the noise level automatically during RX. This is helpful in a dynamic environment where noise differs in time.</p></body></html>",
            )
        )
        self.checkBoxAdaptiveNoise.setText(_translate("SniffSettings", "Adaptive"))
        self.label_sniff_Modulation.setText(_translate("SniffSettings", "Modulation:"))
        self.label_sniff_Signal.setText(_translate("SniffSettings", "Use values from:"))
        self.combox_sniff_Modulation.setItemText(0, _translate("SniffSettings", "ASK"))
        self.combox_sniff_Modulation.setItemText(1, _translate("SniffSettings", "FSK"))
        self.combox_sniff_Modulation.setItemText(2, _translate("SniffSettings", "PSK"))
        self.label_sniff_Tolerance.setText(
            _translate("SniffSettings", "Error Tolerance:")
        )
        self.label_sniff_viewtype.setText(_translate("SniffSettings", "View:"))
        self.lineEdit_sniff_OutputFile.setPlaceholderText(
            _translate("SniffSettings", "None")
        )
        self.label_sniff_BitLength.setText(
            _translate("SniffSettings", "Samples per Symbol:")
        )
        self.btn_sniff_use_signal.setText(_translate("SniffSettings", "Use"))
        self.label_sniff_OutputFile.setText(
            _translate("SniffSettings", "Write bitstream to file:")
        )
        self.checkBoxAutoCenter.setText(_translate("SniffSettings", "Automatic"))
        self.label_sniff_encoding.setText(_translate("SniffSettings", "Encoding:"))
        self.comboBox_sniff_viewtype.setItemText(0, _translate("SniffSettings", "Bit"))
        self.comboBox_sniff_viewtype.setItemText(1, _translate("SniffSettings", "Hex"))
        self.comboBox_sniff_viewtype.setItemText(
            2, _translate("SniffSettings", "ASCII")
        )
        self.checkBox_sniff_Timestamp.setText(
            _translate("SniffSettings", "Show Timestamp")
        )
        self.label_sniff_Noise.setText(_translate("SniffSettings", "Noise:"))
        self.labelCenterSpacing.setText(_translate("SniffSettings", "Center Spacing:"))
        self.labelBitsPerSymbol.setText(_translate("SniffSettings", "Bits per Symbol:"))


from . import urh_rc
