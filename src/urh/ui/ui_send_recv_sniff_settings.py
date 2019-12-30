# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'send_recv_sniff_settings.ui'
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

class Ui_SniffSettings(object):
    def setupUi(self, SniffSettings):
        if SniffSettings.objectName():
            SniffSettings.setObjectName(u"SniffSettings")
        SniffSettings.resize(482, 510)
        self.verticalLayout = QVBoxLayout(SniffSettings)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBoxSniffSettings = QGroupBox(SniffSettings)
        self.groupBoxSniffSettings.setObjectName(u"groupBoxSniffSettings")
        font = QFont()
        font.setBold(True)
        font.setWeight(75);
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
        self.gridLayout = QGridLayout(self.frame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_sniff_Center = QLabel(self.frame)
        self.label_sniff_Center.setObjectName(u"label_sniff_Center")

        self.gridLayout.addWidget(self.label_sniff_Center, 2, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.spinbox_sniff_Noise = QDoubleSpinBox(self.frame)
        self.spinbox_sniff_Noise.setObjectName(u"spinbox_sniff_Noise")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinbox_sniff_Noise.sizePolicy().hasHeightForWidth())
        self.spinbox_sniff_Noise.setSizePolicy(sizePolicy)
        self.spinbox_sniff_Noise.setDecimals(4)
        self.spinbox_sniff_Noise.setMaximum(1.000000000000000)

        self.horizontalLayout_3.addWidget(self.spinbox_sniff_Noise)

        self.checkBoxAdaptiveNoise = QCheckBox(self.frame)
        self.checkBoxAdaptiveNoise.setObjectName(u"checkBoxAdaptiveNoise")

        self.horizontalLayout_3.addWidget(self.checkBoxAdaptiveNoise)


        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 1, 1, 1)

        self.label_sniff_Modulation = QLabel(self.frame)
        self.label_sniff_Modulation.setObjectName(u"label_sniff_Modulation")

        self.gridLayout.addWidget(self.label_sniff_Modulation, 6, 0, 1, 1)

        self.label_sniff_Signal = QLabel(self.frame)
        self.label_sniff_Signal.setObjectName(u"label_sniff_Signal")

        self.gridLayout.addWidget(self.label_sniff_Signal, 0, 0, 1, 1)

        self.spinbox_sniff_ErrorTolerance = QSpinBox(self.frame)
        self.spinbox_sniff_ErrorTolerance.setObjectName(u"spinbox_sniff_ErrorTolerance")
        self.spinbox_sniff_ErrorTolerance.setMaximum(999999)
        self.spinbox_sniff_ErrorTolerance.setValue(5)

        self.gridLayout.addWidget(self.spinbox_sniff_ErrorTolerance, 5, 1, 1, 1)

        self.combox_sniff_Modulation = QComboBox(self.frame)
        self.combox_sniff_Modulation.addItem(QString())
        self.combox_sniff_Modulation.addItem(QString())
        self.combox_sniff_Modulation.addItem(QString())
        self.combox_sniff_Modulation.setObjectName(u"combox_sniff_Modulation")

        self.gridLayout.addWidget(self.combox_sniff_Modulation, 6, 1, 1, 1)

        self.label_sniff_Tolerance = QLabel(self.frame)
        self.label_sniff_Tolerance.setObjectName(u"label_sniff_Tolerance")

        self.gridLayout.addWidget(self.label_sniff_Tolerance, 5, 0, 1, 1)

        self.spinbox_sniff_SamplesPerSymbol = QSpinBox(self.frame)
        self.spinbox_sniff_SamplesPerSymbol.setObjectName(u"spinbox_sniff_SamplesPerSymbol")
        self.spinbox_sniff_SamplesPerSymbol.setMinimum(1)
        self.spinbox_sniff_SamplesPerSymbol.setMaximum(999999999)

        self.gridLayout.addWidget(self.spinbox_sniff_SamplesPerSymbol, 4, 1, 1, 1)

        self.label_sniff_viewtype = QLabel(self.frame)
        self.label_sniff_viewtype.setObjectName(u"label_sniff_viewtype")

        self.gridLayout.addWidget(self.label_sniff_viewtype, 9, 0, 1, 1)

        self.lineEdit_sniff_OutputFile = QLineEdit(self.frame)
        self.lineEdit_sniff_OutputFile.setObjectName(u"lineEdit_sniff_OutputFile")
        sizePolicy.setHeightForWidth(self.lineEdit_sniff_OutputFile.sizePolicy().hasHeightForWidth())
        self.lineEdit_sniff_OutputFile.setSizePolicy(sizePolicy)
        self.lineEdit_sniff_OutputFile.setReadOnly(False)
        self.lineEdit_sniff_OutputFile.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.lineEdit_sniff_OutputFile, 10, 1, 1, 1)

        self.label_sniff_BitLength = QLabel(self.frame)
        self.label_sniff_BitLength.setObjectName(u"label_sniff_BitLength")

        self.gridLayout.addWidget(self.label_sniff_BitLength, 4, 0, 1, 1)

        self.spinBoxCenterSpacing = QDoubleSpinBox(self.frame)
        self.spinBoxCenterSpacing.setObjectName(u"spinBoxCenterSpacing")
        self.spinBoxCenterSpacing.setDecimals(4)
        self.spinBoxCenterSpacing.setMaximum(1.000000000000000)

        self.gridLayout.addWidget(self.spinBoxCenterSpacing, 3, 1, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.comboBox_sniff_signal = QComboBox(self.frame)
        self.comboBox_sniff_signal.setObjectName(u"comboBox_sniff_signal")
        sizePolicy.setHeightForWidth(self.comboBox_sniff_signal.sizePolicy().hasHeightForWidth())
        self.comboBox_sniff_signal.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.comboBox_sniff_signal)

        self.btn_sniff_use_signal = QPushButton(self.frame)
        self.btn_sniff_use_signal.setObjectName(u"btn_sniff_use_signal")

        self.horizontalLayout_2.addWidget(self.btn_sniff_use_signal)


        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 1, 1, 1)

        self.label_sniff_OutputFile = QLabel(self.frame)
        self.label_sniff_OutputFile.setObjectName(u"label_sniff_OutputFile")

        self.gridLayout.addWidget(self.label_sniff_OutputFile, 10, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.spinbox_sniff_Center = QDoubleSpinBox(self.frame)
        self.spinbox_sniff_Center.setObjectName(u"spinbox_sniff_Center")
        sizePolicy.setHeightForWidth(self.spinbox_sniff_Center.sizePolicy().hasHeightForWidth())
        self.spinbox_sniff_Center.setSizePolicy(sizePolicy)
        self.spinbox_sniff_Center.setDecimals(4)
        self.spinbox_sniff_Center.setMinimum(-3.140000000000000)
        self.spinbox_sniff_Center.setMaximum(3.140000000000000)

        self.horizontalLayout_4.addWidget(self.spinbox_sniff_Center)

        self.checkBoxAutoCenter = QCheckBox(self.frame)
        self.checkBoxAutoCenter.setObjectName(u"checkBoxAutoCenter")

        self.horizontalLayout_4.addWidget(self.checkBoxAutoCenter)


        self.gridLayout.addLayout(self.horizontalLayout_4, 2, 1, 1, 1)

        self.label_sniff_encoding = QLabel(self.frame)
        self.label_sniff_encoding.setObjectName(u"label_sniff_encoding")

        self.gridLayout.addWidget(self.label_sniff_encoding, 8, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.comboBox_sniff_viewtype = QComboBox(self.frame)
        self.comboBox_sniff_viewtype.addItem(QString())
        self.comboBox_sniff_viewtype.addItem(QString())
        self.comboBox_sniff_viewtype.addItem(QString())
        self.comboBox_sniff_viewtype.setObjectName(u"comboBox_sniff_viewtype")

        self.horizontalLayout.addWidget(self.comboBox_sniff_viewtype)

        self.checkBox_sniff_Timestamp = QCheckBox(self.frame)
        self.checkBox_sniff_Timestamp.setObjectName(u"checkBox_sniff_Timestamp")

        self.horizontalLayout.addWidget(self.checkBox_sniff_Timestamp)


        self.gridLayout.addLayout(self.horizontalLayout, 9, 1, 1, 1)

        self.label_sniff_Noise = QLabel(self.frame)
        self.label_sniff_Noise.setObjectName(u"label_sniff_Noise")

        self.gridLayout.addWidget(self.label_sniff_Noise, 1, 0, 1, 1)

        self.comboBox_sniff_encoding = QComboBox(self.frame)
        self.comboBox_sniff_encoding.setObjectName(u"comboBox_sniff_encoding")
        sizePolicy.setHeightForWidth(self.comboBox_sniff_encoding.sizePolicy().hasHeightForWidth())
        self.comboBox_sniff_encoding.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.comboBox_sniff_encoding, 8, 1, 1, 1)

        self.labelCenterSpacing = QLabel(self.frame)
        self.labelCenterSpacing.setObjectName(u"labelCenterSpacing")

        self.gridLayout.addWidget(self.labelCenterSpacing, 3, 0, 1, 1)

        self.labelBitsPerSymbol = QLabel(self.frame)
        self.labelBitsPerSymbol.setObjectName(u"labelBitsPerSymbol")

        self.gridLayout.addWidget(self.labelBitsPerSymbol, 7, 0, 1, 1)

        self.spinBoxBitsPerSymbol = QSpinBox(self.frame)
        self.spinBoxBitsPerSymbol.setObjectName(u"spinBoxBitsPerSymbol")
        self.spinBoxBitsPerSymbol.setMinimum(1)
        self.spinBoxBitsPerSymbol.setMaximum(10)

        self.gridLayout.addWidget(self.spinBoxBitsPerSymbol, 7, 1, 1, 1)


        self.gridLayout_3.addWidget(self.frame, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBoxSniffSettings)

        QWidget.setTabOrder(self.groupBoxSniffSettings, self.spinbox_sniff_Noise)
        QWidget.setTabOrder(self.spinbox_sniff_Noise, self.spinbox_sniff_SamplesPerSymbol)
        QWidget.setTabOrder(self.spinbox_sniff_SamplesPerSymbol, self.spinbox_sniff_ErrorTolerance)
        QWidget.setTabOrder(self.spinbox_sniff_ErrorTolerance, self.combox_sniff_Modulation)
        QWidget.setTabOrder(self.combox_sniff_Modulation, self.comboBox_sniff_encoding)
        QWidget.setTabOrder(self.comboBox_sniff_encoding, self.comboBox_sniff_viewtype)
        QWidget.setTabOrder(self.comboBox_sniff_viewtype, self.checkBox_sniff_Timestamp)
        QWidget.setTabOrder(self.checkBox_sniff_Timestamp, self.lineEdit_sniff_OutputFile)

        self.retranslateUi(SniffSettings)
        self.groupBoxSniffSettings.toggled.connect(self.frame.setVisible)
    # setupUi

    def retranslateUi(self, SniffSettings):
        SniffSettings.setWindowTitle(QCoreApplication.translate("SniffSettings", u"Form", None))
        self.groupBoxSniffSettings.setTitle(QCoreApplication.translate("SniffSettings", u"Sniff settings", None))
        self.label_sniff_Center.setText(QCoreApplication.translate("SniffSettings", u"Center:", None))
#if QT_CONFIG(tooltip)
        self.checkBoxAdaptiveNoise.setToolTip(QCoreApplication.translate("SniffSettings", u"<html><head/><body><p>With adaptive noise URH will update the noise level automatically during RX. This is helpful in a dynamic environment where noise differs in time.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBoxAdaptiveNoise.setText(QCoreApplication.translate("SniffSettings", u"Adaptive", None))
        self.label_sniff_Modulation.setText(QCoreApplication.translate("SniffSettings", u"Modulation:", None))
        self.label_sniff_Signal.setText(QCoreApplication.translate("SniffSettings", u"Use values from:", None))
        self.combox_sniff_Modulation.setItemText(0, QCoreApplication.translate("SniffSettings", u"ASK", None))
        self.combox_sniff_Modulation.setItemText(1, QCoreApplication.translate("SniffSettings", u"FSK", None))
        self.combox_sniff_Modulation.setItemText(2, QCoreApplication.translate("SniffSettings", u"PSK", None))

        self.label_sniff_Tolerance.setText(QCoreApplication.translate("SniffSettings", u"Error Tolerance:", None))
        self.label_sniff_viewtype.setText(QCoreApplication.translate("SniffSettings", u"View:", None))
        self.lineEdit_sniff_OutputFile.setPlaceholderText(QCoreApplication.translate("SniffSettings", u"None", None))
        self.label_sniff_BitLength.setText(QCoreApplication.translate("SniffSettings", u"Samples per Symbol:", None))
        self.btn_sniff_use_signal.setText(QCoreApplication.translate("SniffSettings", u"Use", None))
        self.label_sniff_OutputFile.setText(QCoreApplication.translate("SniffSettings", u"Write bitstream to file:", None))
        self.checkBoxAutoCenter.setText(QCoreApplication.translate("SniffSettings", u"Automatic", None))
        self.label_sniff_encoding.setText(QCoreApplication.translate("SniffSettings", u"Encoding:", None))
        self.comboBox_sniff_viewtype.setItemText(0, QCoreApplication.translate("SniffSettings", u"Bit", None))
        self.comboBox_sniff_viewtype.setItemText(1, QCoreApplication.translate("SniffSettings", u"Hex", None))
        self.comboBox_sniff_viewtype.setItemText(2, QCoreApplication.translate("SniffSettings", u"ASCII", None))

        self.checkBox_sniff_Timestamp.setText(QCoreApplication.translate("SniffSettings", u"Show Timestamp", None))
        self.label_sniff_Noise.setText(QCoreApplication.translate("SniffSettings", u"Noise:", None))
        self.labelCenterSpacing.setText(QCoreApplication.translate("SniffSettings", u"Center Spacing:", None))
        self.labelBitsPerSymbol.setText(QCoreApplication.translate("SniffSettings", u"Bits per Symbol:", None))
    # retranslateUi

