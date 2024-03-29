# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ChecksumOptions(object):
    def setupUi(self, ChecksumOptions):
        ChecksumOptions.setObjectName("ChecksumOptions")
        ChecksumOptions.resize(775, 836)
        self.gridLayout = QtWidgets.QGridLayout(ChecksumOptions)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QtWidgets.QScrollArea(ChecksumOptions)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 738, 827))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_4 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_3.addWidget(self.label_4)
        self.comboBoxCategory = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
        self.comboBoxCategory.setObjectName("comboBoxCategory")
        self.comboBoxCategory.addItem("")
        self.comboBoxCategory.addItem("")
        self.verticalLayout_3.addWidget(self.comboBoxCategory)
        self.stackedWidget = QtWidgets.QStackedWidget(self.scrollAreaWidgetContents)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page_crc = QtWidgets.QWidget()
        self.page_crc.setObjectName("page_crc")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.page_crc)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.lineEditFinalXOR = QtWidgets.QLineEdit(self.page_crc)
        self.lineEditFinalXOR.setObjectName("lineEditFinalXOR")
        self.gridLayout_2.addWidget(self.lineEditFinalXOR, 3, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.page_crc)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 1, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(self.page_crc)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tableViewDataRanges = QtWidgets.QTableView(self.groupBox)
        self.tableViewDataRanges.setObjectName("tableViewDataRanges")
        self.tableViewDataRanges.horizontalHeader().setHighlightSections(False)
        self.tableViewDataRanges.verticalHeader().setCascadingSectionResizes(False)
        self.tableViewDataRanges.verticalHeader().setHighlightSections(False)
        self.horizontalLayout.addWidget(self.tableViewDataRanges)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.btnAddRange = QtWidgets.QToolButton(self.groupBox)
        icon = QtGui.QIcon.fromTheme("list-add")
        self.btnAddRange.setIcon(icon)
        self.btnAddRange.setObjectName("btnAddRange")
        self.verticalLayout.addWidget(self.btnAddRange)
        self.btnRemoveRange = QtWidgets.QToolButton(self.groupBox)
        icon = QtGui.QIcon.fromTheme("list-remove")
        self.btnRemoveRange.setIcon(icon)
        self.btnRemoveRange.setObjectName("btnRemoveRange")
        self.verticalLayout.addWidget(self.btnRemoveRange)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.gridLayout_2.addWidget(self.groupBox, 7, 0, 1, 2)
        self.lineEditStartValue = QtWidgets.QLineEdit(self.page_crc)
        self.lineEditStartValue.setObjectName("lineEditStartValue")
        self.gridLayout_2.addWidget(self.lineEditStartValue, 2, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.page_crc)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.page_crc)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 3, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.page_crc)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 2, 0, 1, 1)
        self.lineEditCRCPolynomial = QtWidgets.QLineEdit(self.page_crc)
        self.lineEditCRCPolynomial.setObjectName("lineEditCRCPolynomial")
        self.gridLayout_2.addWidget(self.lineEditCRCPolynomial, 1, 1, 1, 1)
        self.comboBoxCRCFunction = QtWidgets.QComboBox(self.page_crc)
        self.comboBoxCRCFunction.setObjectName("comboBoxCRCFunction")
        self.gridLayout_2.addWidget(self.comboBoxCRCFunction, 0, 1, 1, 1)
        self.label_crc_info = QtWidgets.QLabel(self.page_crc)
        self.label_crc_info.setWordWrap(True)
        self.label_crc_info.setObjectName("label_crc_info")
        self.gridLayout_2.addWidget(self.label_crc_info, 6, 0, 1, 2)
        self.checkBoxRefIn = QtWidgets.QCheckBox(self.page_crc)
        self.checkBoxRefIn.setObjectName("checkBoxRefIn")
        self.gridLayout_2.addWidget(self.checkBoxRefIn, 4, 0, 1, 2)
        self.checkBoxRefOut = QtWidgets.QCheckBox(self.page_crc)
        self.checkBoxRefOut.setObjectName("checkBoxRefOut")
        self.gridLayout_2.addWidget(self.checkBoxRefOut, 5, 0, 1, 2)
        self.stackedWidget.addWidget(self.page_crc)
        self.page_wsp = QtWidgets.QWidget()
        self.page_wsp.setObjectName("page_wsp")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.page_wsp)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_6 = QtWidgets.QLabel(self.page_wsp)
        self.label_6.setAlignment(QtCore.Qt.AlignJustify | QtCore.Qt.AlignVCenter)
        self.label_6.setWordWrap(True)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_2.addWidget(self.label_6)
        self.radioButtonWSPAuto = QtWidgets.QRadioButton(self.page_wsp)
        self.radioButtonWSPAuto.setObjectName("radioButtonWSPAuto")
        self.verticalLayout_2.addWidget(self.radioButtonWSPAuto)
        self.radioButtonWSPChecksum4 = QtWidgets.QRadioButton(self.page_wsp)
        self.radioButtonWSPChecksum4.setObjectName("radioButtonWSPChecksum4")
        self.verticalLayout_2.addWidget(self.radioButtonWSPChecksum4)
        self.radioButtonWSPChecksum8 = QtWidgets.QRadioButton(self.page_wsp)
        self.radioButtonWSPChecksum8.setObjectName("radioButtonWSPChecksum8")
        self.verticalLayout_2.addWidget(self.radioButtonWSPChecksum8)
        self.radioButtonWSPCRC8 = QtWidgets.QRadioButton(self.page_wsp)
        self.radioButtonWSPCRC8.setObjectName("radioButtonWSPCRC8")
        self.verticalLayout_2.addWidget(self.radioButtonWSPCRC8)
        spacerItem1 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.verticalLayout_2.addItem(spacerItem1)
        self.stackedWidget.addWidget(self.page_wsp)
        self.verticalLayout_3.addWidget(self.stackedWidget)
        spacerItem2 = QtWidgets.QSpacerItem(
            20, 107, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.verticalLayout_3.addItem(spacerItem2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 1, 0, 1, 2)

        self.retranslateUi(ChecksumOptions)
        self.stackedWidget.setCurrentIndex(0)
        ChecksumOptions.setTabOrder(
            self.comboBoxCRCFunction, self.lineEditCRCPolynomial
        )
        ChecksumOptions.setTabOrder(self.lineEditCRCPolynomial, self.lineEditStartValue)
        ChecksumOptions.setTabOrder(self.lineEditStartValue, self.lineEditFinalXOR)
        ChecksumOptions.setTabOrder(self.lineEditFinalXOR, self.tableViewDataRanges)
        ChecksumOptions.setTabOrder(self.tableViewDataRanges, self.btnAddRange)
        ChecksumOptions.setTabOrder(self.btnAddRange, self.radioButtonWSPAuto)
        ChecksumOptions.setTabOrder(self.radioButtonWSPAuto, self.btnRemoveRange)
        ChecksumOptions.setTabOrder(self.btnRemoveRange, self.radioButtonWSPChecksum4)
        ChecksumOptions.setTabOrder(
            self.radioButtonWSPChecksum4, self.radioButtonWSPChecksum8
        )
        ChecksumOptions.setTabOrder(
            self.radioButtonWSPChecksum8, self.radioButtonWSPCRC8
        )

    def retranslateUi(self, ChecksumOptions):
        _translate = QtCore.QCoreApplication.translate
        ChecksumOptions.setWindowTitle(
            _translate("ChecksumOptions", "Configure Checksum")
        )
        self.label_4.setText(_translate("ChecksumOptions", "Checksum category:"))
        self.comboBoxCategory.setItemText(0, _translate("ChecksumOptions", "CRC"))
        self.comboBoxCategory.setItemText(
            1, _translate("ChecksumOptions", "Wireless Short Packet Checksum")
        )
        self.label_5.setText(_translate("ChecksumOptions", "CRC polynomial (hex):"))
        self.groupBox.setTitle(
            _translate("ChecksumOptions", "Configure data ranges for CRC")
        )
        self.btnAddRange.setText(_translate("ChecksumOptions", "..."))
        self.btnRemoveRange.setText(_translate("ChecksumOptions", "..."))
        self.label_3.setText(_translate("ChecksumOptions", "CRC function:"))
        self.label_2.setText(_translate("ChecksumOptions", "Final XOR (hex):"))
        self.label.setText(_translate("ChecksumOptions", "Start value (hex):"))
        self.label_crc_info.setText(
            _translate(
                "ChecksumOptions",
                '<html><head/><body><p>Order=17</p><p>Length of checksum=16</p><p>start value length =16</p><p>final XOR length = 16</p><p>Polynomial = x<span style=" vertical-align:super;">1</span> + 4</p></body></html>',
            )
        )
        self.checkBoxRefIn.setText(
            _translate("ChecksumOptions", "RefIn (Reflect input)")
        )
        self.checkBoxRefOut.setText(
            _translate("ChecksumOptions", "RefOut (Reflect output)")
        )
        self.label_6.setText(
            _translate(
                "ChecksumOptions",
                '<html><head/><body><p>The Wireless Short Packet (WSP) standard uses three different checksums. URH can automatically detect the used checksum algorithm from the message. However, you can enforce the usage of a certain checksum if you need to.</p><p>With <span style=" font-weight:600;">Automatic</span> setting, checksums are chosen by these rules:</p><p>1) 4 Bit Checksum - For Switch Telegram (RORG=5 or 6 and STATUS = 0x20 or 0x30)</p><p>2) 8 Bit Checksum: STATUS bit 2<span style=" vertical-align:super;">7</span> = 0</p><p>3) 8 Bit CRC: STATUS bit 2<span style=" vertical-align:super;">7</span> = 1</p></body></html>',
            )
        )
        self.radioButtonWSPAuto.setText(
            _translate("ChecksumOptions", "Automatic (recommended)")
        )
        self.radioButtonWSPChecksum4.setText(
            _translate("ChecksumOptions", "Force Checksum4")
        )
        self.radioButtonWSPChecksum8.setText(
            _translate("ChecksumOptions", "Force Checksum8")
        )
        self.radioButtonWSPCRC8.setText(_translate("ChecksumOptions", "Force CRC8"))
