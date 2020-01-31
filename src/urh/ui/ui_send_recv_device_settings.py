# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'send_recv_device_settings.ui'
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

from urh.ui.KillerDoubleSpinBox import KillerDoubleSpinBox

import urh.ui.urh_rc

class Ui_FormDeviceSettings(object):
    def setupUi(self, FormDeviceSettings):
        if FormDeviceSettings.objectName():
            FormDeviceSettings.setObjectName(u"FormDeviceSettings")
        FormDeviceSettings.resize(860, 711)
        self.verticalLayout = QVBoxLayout(FormDeviceSettings)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBoxDeviceSettings = QGroupBox(FormDeviceSettings)
        self.groupBoxDeviceSettings.setObjectName(u"groupBoxDeviceSettings")
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBoxDeviceSettings.setFont(font)
        self.groupBoxDeviceSettings.setStyleSheet(u"QGroupBox\n"
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
        self.groupBoxDeviceSettings.setFlat(True)
        self.groupBoxDeviceSettings.setCheckable(True)
        self.gridLayout_6 = QGridLayout(self.groupBoxDeviceSettings)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(-1, 15, -1, -1)
        self.frame_2 = QFrame(self.groupBoxDeviceSettings)
        self.frame_2.setObjectName(u"frame_2")
        font1 = QFont()
        font1.setBold(False)
        font1.setWeight(50)
        self.frame_2.setFont(font1)
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.frame_2.setLineWidth(0)
        self.gridLayout = QGridLayout(self.frame_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.spinBoxFreqCorrection = QSpinBox(self.frame_2)
        self.spinBoxFreqCorrection.setObjectName(u"spinBoxFreqCorrection")
        self.spinBoxFreqCorrection.setMinimum(-1000)
        self.spinBoxFreqCorrection.setMaximum(1000)
        self.spinBoxFreqCorrection.setValue(1)

        self.gridLayout.addWidget(self.spinBoxFreqCorrection, 13, 1, 1, 1)

        self.labelBasebandGain = QLabel(self.frame_2)
        self.labelBasebandGain.setObjectName(u"labelBasebandGain")

        self.gridLayout.addWidget(self.labelBasebandGain, 12, 0, 1, 1)

        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.sliderBasebandGain = QSlider(self.frame_2)
        self.sliderBasebandGain.setObjectName(u"sliderBasebandGain")
        self.sliderBasebandGain.setSliderPosition(0)
        self.sliderBasebandGain.setOrientation(Qt.Horizontal)
        self.sliderBasebandGain.setInvertedAppearance(False)
        self.sliderBasebandGain.setInvertedControls(False)
        self.sliderBasebandGain.setTickPosition(QSlider.NoTicks)
        self.sliderBasebandGain.setTickInterval(0)

        self.gridLayout_8.addWidget(self.sliderBasebandGain, 0, 0, 1, 1)

        self.spinBoxBasebandGain = QSpinBox(self.frame_2)
        self.spinBoxBasebandGain.setObjectName(u"spinBoxBasebandGain")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBoxBasebandGain.sizePolicy().hasHeightForWidth())
        self.spinBoxBasebandGain.setSizePolicy(sizePolicy)

        self.gridLayout_8.addWidget(self.spinBoxBasebandGain, 0, 1, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_8, 12, 1, 1, 1)

        self.labelBandwidth = QLabel(self.frame_2)
        self.labelBandwidth.setObjectName(u"labelBandwidth")

        self.gridLayout.addWidget(self.labelBandwidth, 9, 0, 1, 1)

        self.labelFreqCorrection = QLabel(self.frame_2)
        self.labelFreqCorrection.setObjectName(u"labelFreqCorrection")

        self.gridLayout.addWidget(self.labelFreqCorrection, 13, 0, 1, 1)

        self.labelGain = QLabel(self.frame_2)
        self.labelGain.setObjectName(u"labelGain")

        self.gridLayout.addWidget(self.labelGain, 10, 0, 1, 1)

        self.comboBoxDeviceIdentifier = QComboBox(self.frame_2)
        self.comboBoxDeviceIdentifier.setObjectName(u"comboBoxDeviceIdentifier")
        self.comboBoxDeviceIdentifier.setEditable(False)
        self.comboBoxDeviceIdentifier.setInsertPolicy(QComboBox.NoInsert)

        self.gridLayout.addWidget(self.comboBoxDeviceIdentifier, 1, 1, 1, 1)

        self.labelDCCorrection = QLabel(self.frame_2)
        self.labelDCCorrection.setObjectName(u"labelDCCorrection")

        self.gridLayout.addWidget(self.labelDCCorrection, 16, 0, 1, 1)

        self.labelDeviceIdentifier = QLabel(self.frame_2)
        self.labelDeviceIdentifier.setObjectName(u"labelDeviceIdentifier")

        self.gridLayout.addWidget(self.labelDeviceIdentifier, 1, 0, 1, 1)

        self.labelPort = QLabel(self.frame_2)
        self.labelPort.setObjectName(u"labelPort")

        self.gridLayout.addWidget(self.labelPort, 6, 0, 1, 1)

        self.labelIFGain = QLabel(self.frame_2)
        self.labelIFGain.setObjectName(u"labelIFGain")

        self.gridLayout.addWidget(self.labelIFGain, 11, 0, 1, 1)

        self.label_3 = QLabel(self.frame_2)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)

        self.spinBoxFreq = KillerDoubleSpinBox(self.frame_2)
        self.spinBoxFreq.setObjectName(u"spinBoxFreq")
        self.spinBoxFreq.setDecimals(3)
        self.spinBoxFreq.setMinimum(0.001000000000000)
        self.spinBoxFreq.setMaximum(1000000000000.000000000000000)

        self.gridLayout.addWidget(self.spinBoxFreq, 7, 1, 1, 1)

        self.labelAntenna = QLabel(self.frame_2)
        self.labelAntenna.setObjectName(u"labelAntenna")

        self.gridLayout.addWidget(self.labelAntenna, 4, 0, 1, 1)

        self.btnRefreshDeviceIdentifier = QToolButton(self.frame_2)
        self.btnRefreshDeviceIdentifier.setObjectName(u"btnRefreshDeviceIdentifier")
        icon = QIcon()
        iconThemeName = u"view-refresh"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnRefreshDeviceIdentifier.setIcon(icon)

        self.gridLayout.addWidget(self.btnRefreshDeviceIdentifier, 1, 2, 1, 1)

        self.cbDevice = QComboBox(self.frame_2)
        self.cbDevice.addItem("")
        self.cbDevice.addItem("")
        self.cbDevice.setObjectName(u"cbDevice")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cbDevice.sizePolicy().hasHeightForWidth())
        self.cbDevice.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.cbDevice, 0, 1, 1, 1)

        self.lineEditIP = QLineEdit(self.frame_2)
        self.lineEditIP.setObjectName(u"lineEditIP")

        self.gridLayout.addWidget(self.lineEditIP, 5, 1, 1, 1)

        self.labelIP = QLabel(self.frame_2)
        self.labelIP.setObjectName(u"labelIP")

        self.gridLayout.addWidget(self.labelIP, 5, 0, 1, 1)

        self.labelFreq = QLabel(self.frame_2)
        self.labelFreq.setObjectName(u"labelFreq")

        self.gridLayout.addWidget(self.labelFreq, 7, 0, 1, 1)

        self.btnLockBWSR = QToolButton(self.frame_2)
        self.btnLockBWSR.setObjectName(u"btnLockBWSR")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.btnLockBWSR.sizePolicy().hasHeightForWidth())
        self.btnLockBWSR.setSizePolicy(sizePolicy2)
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons/lock.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.btnLockBWSR.setIcon(icon1)
        self.btnLockBWSR.setIconSize(QSize(16, 16))
        self.btnLockBWSR.setCheckable(True)
        self.btnLockBWSR.setChecked(True)

        self.gridLayout.addWidget(self.btnLockBWSR, 8, 2, 2, 1)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.sliderGain = QSlider(self.frame_2)
        self.sliderGain.setObjectName(u"sliderGain")
        self.sliderGain.setMaximum(100)
        self.sliderGain.setSingleStep(1)
        self.sliderGain.setOrientation(Qt.Horizontal)

        self.gridLayout_5.addWidget(self.sliderGain, 0, 0, 1, 1)

        self.spinBoxGain = QSpinBox(self.frame_2)
        self.spinBoxGain.setObjectName(u"spinBoxGain")
        sizePolicy.setHeightForWidth(self.spinBoxGain.sizePolicy().hasHeightForWidth())
        self.spinBoxGain.setSizePolicy(sizePolicy)
        self.spinBoxGain.setMinimum(0)
        self.spinBoxGain.setMaximum(99)
        self.spinBoxGain.setValue(40)

        self.gridLayout_5.addWidget(self.spinBoxGain, 0, 1, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_5, 10, 1, 1, 1)

        self.spinBoxPort = QSpinBox(self.frame_2)
        self.spinBoxPort.setObjectName(u"spinBoxPort")
        self.spinBoxPort.setMinimum(1)
        self.spinBoxPort.setMaximum(65535)
        self.spinBoxPort.setValue(1234)

        self.gridLayout.addWidget(self.spinBoxPort, 6, 1, 1, 1)

        self.comboBoxAntenna = QComboBox(self.frame_2)
        self.comboBoxAntenna.setObjectName(u"comboBoxAntenna")

        self.gridLayout.addWidget(self.comboBoxAntenna, 4, 1, 1, 1)

        self.comboBoxDirectSampling = QComboBox(self.frame_2)
        self.comboBoxDirectSampling.setObjectName(u"comboBoxDirectSampling")

        self.gridLayout.addWidget(self.comboBoxDirectSampling, 14, 1, 1, 1)

        self.labelDirectSampling = QLabel(self.frame_2)
        self.labelDirectSampling.setObjectName(u"labelDirectSampling")

        self.gridLayout.addWidget(self.labelDirectSampling, 14, 0, 1, 1)

        self.labelNRepeat = QLabel(self.frame_2)
        self.labelNRepeat.setObjectName(u"labelNRepeat")

        self.gridLayout.addWidget(self.labelNRepeat, 15, 0, 1, 1)

        self.checkBoxDCCorrection = QCheckBox(self.frame_2)
        self.checkBoxDCCorrection.setObjectName(u"checkBoxDCCorrection")
        self.checkBoxDCCorrection.setChecked(True)

        self.gridLayout.addWidget(self.checkBoxDCCorrection, 16, 1, 1, 1)

        self.comboBoxChannel = QComboBox(self.frame_2)
        self.comboBoxChannel.setObjectName(u"comboBoxChannel")

        self.gridLayout.addWidget(self.comboBoxChannel, 3, 1, 1, 1)

        self.labelChannel = QLabel(self.frame_2)
        self.labelChannel.setObjectName(u"labelChannel")

        self.gridLayout.addWidget(self.labelChannel, 3, 0, 1, 1)

        self.labelSampleRate = QLabel(self.frame_2)
        self.labelSampleRate.setObjectName(u"labelSampleRate")

        self.gridLayout.addWidget(self.labelSampleRate, 8, 0, 1, 1)

        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.sliderIFGain = QSlider(self.frame_2)
        self.sliderIFGain.setObjectName(u"sliderIFGain")
        self.sliderIFGain.setOrientation(Qt.Horizontal)

        self.gridLayout_7.addWidget(self.sliderIFGain, 0, 0, 1, 1)

        self.spinBoxIFGain = QSpinBox(self.frame_2)
        self.spinBoxIFGain.setObjectName(u"spinBoxIFGain")
        sizePolicy.setHeightForWidth(self.spinBoxIFGain.sizePolicy().hasHeightForWidth())
        self.spinBoxIFGain.setSizePolicy(sizePolicy)

        self.gridLayout_7.addWidget(self.spinBoxIFGain, 0, 1, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_7, 11, 1, 1, 1)

        self.spinBoxNRepeat = QSpinBox(self.frame_2)
        self.spinBoxNRepeat.setObjectName(u"spinBoxNRepeat")
        self.spinBoxNRepeat.setMaximum(999999999)

        self.gridLayout.addWidget(self.spinBoxNRepeat, 15, 1, 1, 1)

        self.spinBoxSampleRate = KillerDoubleSpinBox(self.frame_2)
        self.spinBoxSampleRate.setObjectName(u"spinBoxSampleRate")
        self.spinBoxSampleRate.setDecimals(3)
        self.spinBoxSampleRate.setMinimum(0.001000000000000)
        self.spinBoxSampleRate.setMaximum(1000000000000.000000000000000)

        self.gridLayout.addWidget(self.spinBoxSampleRate, 8, 1, 1, 1)

        self.spinBoxBandwidth = KillerDoubleSpinBox(self.frame_2)
        self.spinBoxBandwidth.setObjectName(u"spinBoxBandwidth")
        self.spinBoxBandwidth.setDecimals(3)
        self.spinBoxBandwidth.setMinimum(0.001000000000000)
        self.spinBoxBandwidth.setMaximum(1000000000000.000000000000000)

        self.gridLayout.addWidget(self.spinBoxBandwidth, 9, 1, 1, 1)

        self.labelSubdevice = QLabel(self.frame_2)
        self.labelSubdevice.setObjectName(u"labelSubdevice")

        self.gridLayout.addWidget(self.labelSubdevice, 2, 0, 1, 1)

        self.lineEditSubdevice = QLineEdit(self.frame_2)
        self.lineEditSubdevice.setObjectName(u"lineEditSubdevice")

        self.gridLayout.addWidget(self.lineEditSubdevice, 2, 1, 1, 1)


        self.gridLayout_6.addWidget(self.frame_2, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBoxDeviceSettings)

        QWidget.setTabOrder(self.groupBoxDeviceSettings, self.cbDevice)
        QWidget.setTabOrder(self.cbDevice, self.comboBoxDeviceIdentifier)
        QWidget.setTabOrder(self.comboBoxDeviceIdentifier, self.btnRefreshDeviceIdentifier)
        QWidget.setTabOrder(self.btnRefreshDeviceIdentifier, self.lineEditSubdevice)
        QWidget.setTabOrder(self.lineEditSubdevice, self.comboBoxChannel)
        QWidget.setTabOrder(self.comboBoxChannel, self.comboBoxAntenna)
        QWidget.setTabOrder(self.comboBoxAntenna, self.lineEditIP)
        QWidget.setTabOrder(self.lineEditIP, self.spinBoxPort)
        QWidget.setTabOrder(self.spinBoxPort, self.spinBoxFreq)
        QWidget.setTabOrder(self.spinBoxFreq, self.spinBoxSampleRate)
        QWidget.setTabOrder(self.spinBoxSampleRate, self.btnLockBWSR)
        QWidget.setTabOrder(self.btnLockBWSR, self.spinBoxBandwidth)
        QWidget.setTabOrder(self.spinBoxBandwidth, self.sliderGain)
        QWidget.setTabOrder(self.sliderGain, self.spinBoxGain)
        QWidget.setTabOrder(self.spinBoxGain, self.sliderIFGain)
        QWidget.setTabOrder(self.sliderIFGain, self.spinBoxIFGain)
        QWidget.setTabOrder(self.spinBoxIFGain, self.sliderBasebandGain)
        QWidget.setTabOrder(self.sliderBasebandGain, self.spinBoxBasebandGain)
        QWidget.setTabOrder(self.spinBoxBasebandGain, self.spinBoxFreqCorrection)
        QWidget.setTabOrder(self.spinBoxFreqCorrection, self.comboBoxDirectSampling)
        QWidget.setTabOrder(self.comboBoxDirectSampling, self.spinBoxNRepeat)
        QWidget.setTabOrder(self.spinBoxNRepeat, self.checkBoxDCCorrection)

        self.retranslateUi(FormDeviceSettings)
        self.groupBoxDeviceSettings.toggled.connect(self.frame_2.setVisible)
    # setupUi

    def retranslateUi(self, FormDeviceSettings):
        FormDeviceSettings.setWindowTitle(QCoreApplication.translate("FormDeviceSettings", u"Form", None))
        self.groupBoxDeviceSettings.setTitle(QCoreApplication.translate("FormDeviceSettings", u"Device settings", None))
#if QT_CONFIG(tooltip)
        self.spinBoxFreqCorrection.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"<html><head/><body><p>Set the frequency correction in <span style=\" font-weight:600;\">ppm</span>. If you do not know what to enter here, just leave it to one.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.labelBasebandGain.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"<html><head/><body><p>The baseband gain is applied to the baseband signal in your software defined radio. The baseband signal is at low frequency and gathered from the RF signal by <span style=\" font-weight:600;\">complex downsampling</span>.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.labelBasebandGain.setText(QCoreApplication.translate("FormDeviceSettings", u"Baseband gain:", None))
#if QT_CONFIG(tooltip)
        self.sliderBasebandGain.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"<html><head/><body><p>The baseband gain is applied to the baseband signal in your software defined radio. The baseband signal is at low frequency and gathered from the RF signal by <span style=\" font-weight:600;\">complex downsampling</span>.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.spinBoxBasebandGain.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"<html><head/><body><p>The baseband gain is applied to the baseband signal in your software defined radio. The baseband signal is at low frequency and gathered from the RF signal by <span style=\" font-weight:600;\">complex downsampling</span>.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.labelBandwidth.setText(QCoreApplication.translate("FormDeviceSettings", u"Bandwidth (Hz):", None))
#if QT_CONFIG(tooltip)
        self.labelFreqCorrection.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"<html><head/><body><p>Set the frequency correction in <span style=\" font-weight:600;\">ppm</span>. If you do not know what to enter here, just leave it to one.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.labelFreqCorrection.setText(QCoreApplication.translate("FormDeviceSettings", u"Frequency correction:", None))
#if QT_CONFIG(tooltip)
        self.labelGain.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"<html><head/><body><p>The gain (more exactly RF gain) is the gain applied to the RF signal. This amplifies the high frequent signal arriving at the antenna of your Software Defined Radio.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.labelGain.setText(QCoreApplication.translate("FormDeviceSettings", u"Gain:", None))
#if QT_CONFIG(tooltip)
        self.labelDCCorrection.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"Apply DC correction during recording, that is, ensure the captured signal has a mean value of zero.", None))
#endif // QT_CONFIG(tooltip)
        self.labelDCCorrection.setText(QCoreApplication.translate("FormDeviceSettings", u"DC correction:", None))
        self.labelDeviceIdentifier.setText(QCoreApplication.translate("FormDeviceSettings", u"Device Identifier:", None))
        self.labelPort.setText(QCoreApplication.translate("FormDeviceSettings", u"Port number:", None))
#if QT_CONFIG(tooltip)
        self.labelIFGain.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"<html><head/><body><p>The IF Gain is applied to the Intermediate Frequency signal in your Software Defined Radio. An IF signal has a lower frequency than the high frequent RF signal, so signal processing can be applied more efficiently.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.labelIFGain.setText(QCoreApplication.translate("FormDeviceSettings", u"IF Gain:", None))
        self.label_3.setText(QCoreApplication.translate("FormDeviceSettings", u"Device:", None))
        self.labelAntenna.setText(QCoreApplication.translate("FormDeviceSettings", u"Antenna:", None))
        self.btnRefreshDeviceIdentifier.setText(QCoreApplication.translate("FormDeviceSettings", u"...", None))
        self.cbDevice.setItemText(0, QCoreApplication.translate("FormDeviceSettings", u"USRP", None))
        self.cbDevice.setItemText(1, QCoreApplication.translate("FormDeviceSettings", u"HackRF", None))

        self.lineEditIP.setText(QCoreApplication.translate("FormDeviceSettings", u"127.0.0.1", None))
        self.labelIP.setText(QCoreApplication.translate("FormDeviceSettings", u"IP address:", None))
        self.labelFreq.setText(QCoreApplication.translate("FormDeviceSettings", u"Frequency (Hz):", None))
        self.btnLockBWSR.setText(QCoreApplication.translate("FormDeviceSettings", u"...", None))
#if QT_CONFIG(tooltip)
        self.sliderGain.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"<html><head/><body><p>The gain (more exactly RF gain) is the gain applied to the RF signal. This amplifies the high frequent signal arriving at the antenna of your Software Defined Radio.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.spinBoxGain.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"<html><head/><body><p>The gain (more exactly RF gain) is the gain applied to the RF signal. This amplifies the high frequent signal arriving at the antenna of your Software Defined Radio.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.comboBoxDirectSampling.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"<html><head/><body><p>Set the direct sampling mode. If you do not know what to choose here, just set it to disabled. The<span style=\" font-weight:600;\"> native backend</span> is recommended, when using this setting.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.labelDirectSampling.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"<html><head/><body><p>Set the direct sampling mode. If you do not know what to choose here, just set it to disabled. The<span style=\" font-weight:600;\"> native backend</span> is recommended, when using this setting.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.labelDirectSampling.setText(QCoreApplication.translate("FormDeviceSettings", u"Direct sampling:", None))
        self.labelNRepeat.setText(QCoreApplication.translate("FormDeviceSettings", u"Repeat:", None))
#if QT_CONFIG(tooltip)
        self.checkBoxDCCorrection.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"Apply DC correction during recording, that is, ensure the captured signal has a mean value of zero.", None))
#endif // QT_CONFIG(tooltip)
        self.checkBoxDCCorrection.setText(QCoreApplication.translate("FormDeviceSettings", u"Apply DC correction", None))
        self.labelChannel.setText(QCoreApplication.translate("FormDeviceSettings", u"Channel:", None))
        self.labelSampleRate.setText(QCoreApplication.translate("FormDeviceSettings", u"Sample rate (Sps):", None))
#if QT_CONFIG(tooltip)
        self.sliderIFGain.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"<html><head/><body><p>The IF Gain is applied to the Intermediate Frequency signal in your Software Defined Radio. An IF signal has a lower frequency than the high frequent RF signal, so signal processing can be applied more efficiently.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.spinBoxIFGain.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"<html><head/><body><p>The IF Gain is applied to the Intermediate Frequency signal in your Software Defined Radio. An IF signal has a lower frequency than the high frequent RF signal, so signal processing can be applied more efficiently.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.spinBoxNRepeat.setSpecialValueText(QCoreApplication.translate("FormDeviceSettings", u"Infinite", None))
#if QT_CONFIG(tooltip)
        self.labelSubdevice.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"<html><head/><body><p>Configure the subdevice of your USRP. For example, <span style=\" font-weight:600;\">B:0 </span>to select a WBX on slot B. You can learn more at <a href=\"http://files.ettus.com/manual/page_configuration.html#config_subdev\"><span style=\" text-decoration: underline; color:#2980b9;\">http://files.ettus.com/manual/page_configuration.html#config_subdev.</span></a></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.labelSubdevice.setText(QCoreApplication.translate("FormDeviceSettings", u"<html><head/><body><p>Subdevice:</p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.lineEditSubdevice.setToolTip(QCoreApplication.translate("FormDeviceSettings", u"<html><head/><body><p>Configure the subdevice of your USRP. For example, <span style=\" font-weight:600;\">B:0 </span>to select a WBX on slot B. You can learn more at <a href=\"http://files.ettus.com/manual/page_configuration.html#config_subdev\"><span style=\" text-decoration: underline; color:#2980b9;\">http://files.ettus.com/manual/page_configuration.html#config_subdev.</span></a></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

