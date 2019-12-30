# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'checksum_options_widget.ui'
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

class Ui_ChecksumOptions(object):
    def setupUi(self, ChecksumOptions):
        if ChecksumOptions.objectName():
            ChecksumOptions.setObjectName(u"ChecksumOptions")
        ChecksumOptions.resize(775, 836)
        self.gridLayout = QGridLayout(ChecksumOptions)
        self.gridLayout.setObjectName(u"gridLayout")
        self.scrollArea = QScrollArea(ChecksumOptions)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 738, 827))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(11, 11, 11, 11)
        self.label_4 = QLabel(self.scrollAreaWidgetContents)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_3.addWidget(self.label_4)

        self.comboBoxCategory = QComboBox(self.scrollAreaWidgetContents)
        self.comboBoxCategory.addItem(QString())
        self.comboBoxCategory.addItem(QString())
        self.comboBoxCategory.setObjectName(u"comboBoxCategory")

        self.verticalLayout_3.addWidget(self.comboBoxCategory)

        self.stackedWidget = QStackedWidget(self.scrollAreaWidgetContents)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page_crc = QWidget()
        self.page_crc.setObjectName(u"page_crc")
        self.gridLayout_2 = QGridLayout(self.page_crc)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.lineEditFinalXOR = QLineEdit(self.page_crc)
        self.lineEditFinalXOR.setObjectName(u"lineEditFinalXOR")

        self.gridLayout_2.addWidget(self.lineEditFinalXOR, 3, 1, 1, 1)

        self.label_5 = QLabel(self.page_crc)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 1, 0, 1, 1)

        self.groupBox = QGroupBox(self.page_crc)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tableViewDataRanges = QTableView(self.groupBox)
        self.tableViewDataRanges.setObjectName(u"tableViewDataRanges")
        self.tableViewDataRanges.horizontalHeader().setHighlightSections(False)
        self.tableViewDataRanges.verticalHeader().setCascadingSectionResizes(False)
        self.tableViewDataRanges.verticalHeader().setHighlightSections(False)

        self.horizontalLayout.addWidget(self.tableViewDataRanges)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.btnAddRange = QToolButton(self.groupBox)
        self.btnAddRange.setObjectName(u"btnAddRange")
        icon = QIcon()
        iconThemeName = u"list-add"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u"../../../", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnAddRange.setIcon(icon)

        self.verticalLayout.addWidget(self.btnAddRange)

        self.btnRemoveRange = QToolButton(self.groupBox)
        self.btnRemoveRange.setObjectName(u"btnRemoveRange")
        icon1 = QIcon()
        iconThemeName = u"list-remove"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u"../../../", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnRemoveRange.setIcon(icon1)

        self.verticalLayout.addWidget(self.btnRemoveRange)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)


        self.horizontalLayout.addLayout(self.verticalLayout)


        self.gridLayout_2.addWidget(self.groupBox, 7, 0, 1, 2)

        self.lineEditStartValue = QLineEdit(self.page_crc)
        self.lineEditStartValue.setObjectName(u"lineEditStartValue")

        self.gridLayout_2.addWidget(self.lineEditStartValue, 2, 1, 1, 1)

        self.label_3 = QLabel(self.page_crc)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)

        self.label_2 = QLabel(self.page_crc)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 3, 0, 1, 1)

        self.label = QLabel(self.page_crc)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 2, 0, 1, 1)

        self.lineEditCRCPolynomial = QLineEdit(self.page_crc)
        self.lineEditCRCPolynomial.setObjectName(u"lineEditCRCPolynomial")

        self.gridLayout_2.addWidget(self.lineEditCRCPolynomial, 1, 1, 1, 1)

        self.comboBoxCRCFunction = QComboBox(self.page_crc)
        self.comboBoxCRCFunction.setObjectName(u"comboBoxCRCFunction")

        self.gridLayout_2.addWidget(self.comboBoxCRCFunction, 0, 1, 1, 1)

        self.label_crc_info = QLabel(self.page_crc)
        self.label_crc_info.setObjectName(u"label_crc_info")
        self.label_crc_info.setWordWrap(True)

        self.gridLayout_2.addWidget(self.label_crc_info, 6, 0, 1, 2)

        self.checkBoxRefIn = QCheckBox(self.page_crc)
        self.checkBoxRefIn.setObjectName(u"checkBoxRefIn")

        self.gridLayout_2.addWidget(self.checkBoxRefIn, 4, 0, 1, 2)

        self.checkBoxRefOut = QCheckBox(self.page_crc)
        self.checkBoxRefOut.setObjectName(u"checkBoxRefOut")

        self.gridLayout_2.addWidget(self.checkBoxRefOut, 5, 0, 1, 2)

        self.stackedWidget.addWidget(self.page_crc)
        self.page_wsp = QWidget()
        self.page_wsp.setObjectName(u"page_wsp")
        self.verticalLayout_2 = QVBoxLayout(self.page_wsp)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_6 = QLabel(self.page_wsp)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setAlignment(Qt.AlignJustify|Qt.AlignVCenter)
        self.label_6.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.label_6)

        self.radioButtonWSPAuto = QRadioButton(self.page_wsp)
        self.radioButtonWSPAuto.setObjectName(u"radioButtonWSPAuto")

        self.verticalLayout_2.addWidget(self.radioButtonWSPAuto)

        self.radioButtonWSPChecksum4 = QRadioButton(self.page_wsp)
        self.radioButtonWSPChecksum4.setObjectName(u"radioButtonWSPChecksum4")

        self.verticalLayout_2.addWidget(self.radioButtonWSPChecksum4)

        self.radioButtonWSPChecksum8 = QRadioButton(self.page_wsp)
        self.radioButtonWSPChecksum8.setObjectName(u"radioButtonWSPChecksum8")

        self.verticalLayout_2.addWidget(self.radioButtonWSPChecksum8)

        self.radioButtonWSPCRC8 = QRadioButton(self.page_wsp)
        self.radioButtonWSPCRC8.setObjectName(u"radioButtonWSPCRC8")

        self.verticalLayout_2.addWidget(self.radioButtonWSPCRC8)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_3)

        self.stackedWidget.addWidget(self.page_wsp)

        self.verticalLayout_3.addWidget(self.stackedWidget)

        self.verticalSpacer = QSpacerItem(20, 107, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 1, 0, 1, 2)

        QWidget.setTabOrder(self.comboBoxCRCFunction, self.lineEditCRCPolynomial)
        QWidget.setTabOrder(self.lineEditCRCPolynomial, self.lineEditStartValue)
        QWidget.setTabOrder(self.lineEditStartValue, self.lineEditFinalXOR)
        QWidget.setTabOrder(self.lineEditFinalXOR, self.tableViewDataRanges)
        QWidget.setTabOrder(self.tableViewDataRanges, self.btnAddRange)
        QWidget.setTabOrder(self.btnAddRange, self.radioButtonWSPAuto)
        QWidget.setTabOrder(self.radioButtonWSPAuto, self.btnRemoveRange)
        QWidget.setTabOrder(self.btnRemoveRange, self.radioButtonWSPChecksum4)
        QWidget.setTabOrder(self.radioButtonWSPChecksum4, self.radioButtonWSPChecksum8)
        QWidget.setTabOrder(self.radioButtonWSPChecksum8, self.radioButtonWSPCRC8)

        self.retranslateUi(ChecksumOptions)

        self.stackedWidget.setCurrentIndex(0)

    # setupUi

    def retranslateUi(self, ChecksumOptions):
        ChecksumOptions.setWindowTitle(QCoreApplication.translate("ChecksumOptions", u"Configure Checksum", None))
        self.label_4.setText(QCoreApplication.translate("ChecksumOptions", u"Checksum category:", None))
        self.comboBoxCategory.setItemText(0, QCoreApplication.translate("ChecksumOptions", u"CRC", None))
        self.comboBoxCategory.setItemText(1, QCoreApplication.translate("ChecksumOptions", u"Wireless Short Packet Checksum", None))

        self.label_5.setText(QCoreApplication.translate("ChecksumOptions", u"CRC polynomial (hex):", None))
        self.groupBox.setTitle(QCoreApplication.translate("ChecksumOptions", u"Configure data ranges for CRC", None))
        self.btnAddRange.setText(QCoreApplication.translate("ChecksumOptions", u"...", None))
        self.btnRemoveRange.setText(QCoreApplication.translate("ChecksumOptions", u"...", None))
        self.label_3.setText(QCoreApplication.translate("ChecksumOptions", u"CRC function:", None))
        self.label_2.setText(QCoreApplication.translate("ChecksumOptions", u"Final XOR (hex):", None))
        self.label.setText(QCoreApplication.translate("ChecksumOptions", u"Start value (hex):", None))
        self.label_crc_info.setText(QCoreApplication.translate("ChecksumOptions", u"<html><head/><body><p>Order=17</p><p>Length of checksum=16</p><p>start value length =16</p><p>final XOR length = 16</p><p>Polynomial = x<span style=\" vertical-align:super;\">1</span> + 4</p></body></html>", None))
        self.checkBoxRefIn.setText(QCoreApplication.translate("ChecksumOptions", u"RefIn (Reflect input)", None))
        self.checkBoxRefOut.setText(QCoreApplication.translate("ChecksumOptions", u"RefOut (Reflect output)", None))
        self.label_6.setText(QCoreApplication.translate("ChecksumOptions", u"<html><head/><body><p>The Wireless Short Packet (WSP) standard uses three different checksums. URH can automatically detect the used checksum algorithm from the message. However, you can enforce the usage of a certain checksum if you need to.</p><p>With <span style=\" font-weight:600;\">Automatic</span> setting, checksums are chosen by these rules:</p><p>1) 4 Bit Checksum - For Switch Telegram (RORG=5 or 6 and STATUS = 0x20 or 0x30)</p><p>2) 8 Bit Checksum: STATUS bit 2<span style=\" vertical-align:super;\">7</span> = 0</p><p>3) 8 Bit CRC: STATUS bit 2<span style=\" vertical-align:super;\">7</span> = 1</p></body></html>", None))
        self.radioButtonWSPAuto.setText(QCoreApplication.translate("ChecksumOptions", u"Automatic (recommended)", None))
        self.radioButtonWSPChecksum4.setText(QCoreApplication.translate("ChecksumOptions", u"Force Checksum4", None))
        self.radioButtonWSPChecksum8.setText(QCoreApplication.translate("ChecksumOptions", u"Force Checksum8", None))
        self.radioButtonWSPCRC8.setText(QCoreApplication.translate("ChecksumOptions", u"Force CRC8", None))
    # retranslateUi

