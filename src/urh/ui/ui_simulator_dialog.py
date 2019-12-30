# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'simulator_dialog.ui'
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

import LiveGraphicView
import LoggingGraphicsView

class Ui_DialogSimulator(object):
    def setupUi(self, DialogSimulator):
        if DialogSimulator.objectName():
            DialogSimulator.setObjectName(u"DialogSimulator")
        DialogSimulator.resize(1088, 823)
        self.verticalLayout_4 = QVBoxLayout(DialogSimulator)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.tabWidgetSimulatorSettings = QTabWidget(DialogSimulator)
        self.tabWidgetSimulatorSettings.setObjectName(u"tabWidgetSimulatorSettings")
        self.tabWidgetSimulatorSettings.setStyleSheet(u"QTabWidget::pane { border: 0; }")
        self.tabLog = QWidget()
        self.tabLog.setObjectName(u"tabLog")
        self.verticalLayout_3 = QVBoxLayout(self.tabLog)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gvSimulator = LoggingGraphicsView(self.tabLog)
        self.gvSimulator.setObjectName(u"gvSimulator")
        self.gvSimulator.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_3.addWidget(self.gvSimulator)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btnLogAll = QPushButton(self.tabLog)
        self.btnLogAll.setObjectName(u"btnLogAll")
        self.btnLogAll.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.btnLogAll)

        self.btnLogNone = QPushButton(self.tabLog)
        self.btnLogNone.setObjectName(u"btnLogNone")
        self.btnLogNone.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.btnLogNone)

        self.btnToggleLog = QPushButton(self.tabLog)
        self.btnToggleLog.setObjectName(u"btnToggleLog")
        self.btnToggleLog.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.btnToggleLog)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.tabWidgetSimulatorSettings.addTab(self.tabLog, QString())
        self.tabRX = QWidget()
        self.tabRX.setObjectName(u"tabRX")
        self.verticalLayout_5 = QVBoxLayout(self.tabRX)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.scrollAreaRX = QScrollArea(self.tabRX)
        self.scrollAreaRX.setObjectName(u"scrollAreaRX")
        self.scrollAreaRX.setFrameShape(QFrame.NoFrame)
        self.scrollAreaRX.setWidgetResizable(True)
        self.scrollAreaWidgetContentsRX = QWidget()
        self.scrollAreaWidgetContentsRX.setObjectName(u"scrollAreaWidgetContentsRX")
        self.scrollAreaWidgetContentsRX.setGeometry(QRect(0, 0, 1066, 766))
        self.verticalLayout_6 = QVBoxLayout(self.scrollAreaWidgetContentsRX)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.btnTestSniffSettings = QPushButton(self.scrollAreaWidgetContentsRX)
        self.btnTestSniffSettings.setObjectName(u"btnTestSniffSettings")
        icon = QIcon()
        icon.addFile(u":/icons/icons/sniffer.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.btnTestSniffSettings.setIcon(icon)
        self.btnTestSniffSettings.setAutoDefault(False)

        self.verticalLayout_6.addWidget(self.btnTestSniffSettings)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer)

        self.scrollAreaRX.setWidget(self.scrollAreaWidgetContentsRX)

        self.verticalLayout_5.addWidget(self.scrollAreaRX)

        self.tabWidgetSimulatorSettings.addTab(self.tabRX, QString())
        self.tabTX = QWidget()
        self.tabTX.setObjectName(u"tabTX")
        self.verticalLayout_7 = QVBoxLayout(self.tabTX)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.scrollAreaTX = QScrollArea(self.tabTX)
        self.scrollAreaTX.setObjectName(u"scrollAreaTX")
        self.scrollAreaTX.setFrameShape(QFrame.NoFrame)
        self.scrollAreaTX.setWidgetResizable(True)
        self.scrollAreaWidgetContentsTX = QWidget()
        self.scrollAreaWidgetContentsTX.setObjectName(u"scrollAreaWidgetContentsTX")
        self.scrollAreaWidgetContentsTX.setGeometry(QRect(0, 0, 1066, 766))
        self.verticalLayout_8 = QVBoxLayout(self.scrollAreaWidgetContentsTX)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_2)

        self.scrollAreaTX.setWidget(self.scrollAreaWidgetContentsTX)

        self.verticalLayout_7.addWidget(self.scrollAreaTX)

        self.tabWidgetSimulatorSettings.addTab(self.tabTX, QString())
        self.tabSimulation = QWidget()
        self.tabSimulation.setObjectName(u"tabSimulation")
        self.verticalLayout_9 = QVBoxLayout(self.tabSimulation)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.tabSimulation)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setStyleSheet(u"QTabWidget::pane { border: 0; }")
        self.tabWidget.setTabPosition(QTabWidget.West)
        self.tabWidget.setTabShape(QTabWidget.Triangular)
        self.tab_simulation = QWidget()
        self.tab_simulation.setObjectName(u"tab_simulation")
        self.verticalLayout_15 = QVBoxLayout(self.tab_simulation)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.groupBoxSimulationStatus = QGroupBox(self.tab_simulation)
        self.groupBoxSimulationStatus.setObjectName(u"groupBoxSimulationStatus")
        self.groupBoxSimulationStatus.setStyleSheet(u"QGroupBox\n"
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
        self.groupBoxSimulationStatus.setCheckable(True)
        self.verticalLayout_12 = QVBoxLayout(self.groupBoxSimulationStatus)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(-1, 15, -1, -1)
        self.frame = QFrame(self.groupBoxSimulationStatus)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Plain)
        self.frame.setLineWidth(0)
        self.verticalLayout_11 = QVBoxLayout(self.frame)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.textEditSimulation = QTextEdit(self.frame)
        self.textEditSimulation.setObjectName(u"textEditSimulation")
        self.textEditSimulation.setReadOnly(True)

        self.verticalLayout_11.addWidget(self.textEditSimulation)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.lblCurrentRepeatValue = QLabel(self.frame)
        self.lblCurrentRepeatValue.setObjectName(u"lblCurrentRepeatValue")
        font = QFont()
        font.setBold(True)
        font.setWeight(75);
        self.lblCurrentRepeatValue.setFont(font)
        self.lblCurrentRepeatValue.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.lblCurrentRepeatValue)

        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.lblCurrentItemValue = QLabel(self.frame)
        self.lblCurrentItemValue.setObjectName(u"lblCurrentItemValue")
        self.lblCurrentItemValue.setFont(font)
        self.lblCurrentItemValue.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.lblCurrentItemValue)

        self.btnSaveLog = QToolButton(self.frame)
        self.btnSaveLog.setObjectName(u"btnSaveLog")
        icon1 = QIcon()
        iconThemeName = u"document-save"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnSaveLog.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.btnSaveLog)


        self.verticalLayout_11.addLayout(self.horizontalLayout_2)


        self.verticalLayout_12.addWidget(self.frame)


        self.verticalLayout_15.addWidget(self.groupBoxSimulationStatus)

        self.groupBoxRXStatus = QGroupBox(self.tab_simulation)
        self.groupBoxRXStatus.setObjectName(u"groupBoxRXStatus")
        self.groupBoxRXStatus.setStyleSheet(u"QGroupBox\n"
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
        self.groupBoxRXStatus.setCheckable(True)
        self.verticalLayout_14 = QVBoxLayout(self.groupBoxRXStatus)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(-1, 15, -1, -1)
        self.frame_2 = QFrame(self.groupBoxRXStatus)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Plain)
        self.frame_2.setLineWidth(0)
        self.verticalLayout_13 = QVBoxLayout(self.frame_2)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.checkBoxCaptureFullRX = QCheckBox(self.frame_2)
        self.checkBoxCaptureFullRX.setObjectName(u"checkBoxCaptureFullRX")

        self.horizontalLayout_5.addWidget(self.checkBoxCaptureFullRX)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_2)

        self.btnSaveRX = QToolButton(self.frame_2)
        self.btnSaveRX.setObjectName(u"btnSaveRX")
        self.btnSaveRX.setIcon(icon1)

        self.horizontalLayout_5.addWidget(self.btnSaveRX)


        self.verticalLayout_13.addLayout(self.horizontalLayout_5)

        self.graphicsViewPreview = LiveGraphicView(self.frame_2)
        self.graphicsViewPreview.setObjectName(u"graphicsViewPreview")

        self.verticalLayout_13.addWidget(self.graphicsViewPreview)


        self.verticalLayout_14.addWidget(self.frame_2)


        self.verticalLayout_15.addWidget(self.groupBoxRXStatus)

        self.tabWidget.addTab(self.tab_simulation, QString())
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout = QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.textEditTranscript = QTextEdit(self.tab)
        self.textEditTranscript.setObjectName(u"textEditTranscript")
        self.textEditTranscript.setReadOnly(True)

        self.verticalLayout.addWidget(self.textEditTranscript)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.radioButtonTranscriptBit = QRadioButton(self.tab)
        self.radioButtonTranscriptBit.setObjectName(u"radioButtonTranscriptBit")
        self.radioButtonTranscriptBit.setChecked(True)

        self.horizontalLayout_3.addWidget(self.radioButtonTranscriptBit)

        self.radioButtonTranscriptHex = QRadioButton(self.tab)
        self.radioButtonTranscriptHex.setObjectName(u"radioButtonTranscriptHex")

        self.horizontalLayout_3.addWidget(self.radioButtonTranscriptHex)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.btnOpenInAnalysis = QPushButton(self.tab)
        self.btnOpenInAnalysis.setObjectName(u"btnOpenInAnalysis")

        self.horizontalLayout_3.addWidget(self.btnOpenInAnalysis)

        self.btnSaveTranscript = QToolButton(self.tab)
        self.btnSaveTranscript.setObjectName(u"btnSaveTranscript")
        self.btnSaveTranscript.setIcon(icon1)

        self.horizontalLayout_3.addWidget(self.btnSaveTranscript)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.tabWidget.addTab(self.tab, QString())
        self.tab_device = QWidget()
        self.tab_device.setObjectName(u"tab_device")
        self.verticalLayout_10 = QVBoxLayout(self.tab_device)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.textEditDevices = QTextEdit(self.tab_device)
        self.textEditDevices.setObjectName(u"textEditDevices")
        self.textEditDevices.setReadOnly(True)

        self.verticalLayout_10.addWidget(self.textEditDevices)

        self.tabWidget.addTab(self.tab_device, QString())

        self.verticalLayout_9.addWidget(self.tabWidget)

        self.btnStartStop = QPushButton(self.tabSimulation)
        self.btnStartStop.setObjectName(u"btnStartStop")
        icon2 = QIcon()
        iconThemeName = u"media-playback-start"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnStartStop.setIcon(icon2)

        self.verticalLayout_9.addWidget(self.btnStartStop)

        self.tabWidgetSimulatorSettings.addTab(self.tabSimulation, QString())

        self.verticalLayout_4.addWidget(self.tabWidgetSimulatorSettings)


        self.retranslateUi(DialogSimulator)
        self.groupBoxSimulationStatus.toggled.connect(self.frame.setVisible)
        self.groupBoxRXStatus.toggled.connect(self.frame_2.setVisible)

        self.tabWidgetSimulatorSettings.setCurrentIndex(3)
        self.tabWidget.setCurrentIndex(0)
        self.btnStartStop.setDefault(True)

    # setupUi

    def retranslateUi(self, DialogSimulator):
        DialogSimulator.setWindowTitle(QCoreApplication.translate("DialogSimulator", u"Simulation", None))
        self.btnLogAll.setText(QCoreApplication.translate("DialogSimulator", u"Log all", None))
        self.btnLogNone.setText(QCoreApplication.translate("DialogSimulator", u"Log none", None))
        self.btnToggleLog.setText(QCoreApplication.translate("DialogSimulator", u"Toggle selected", None))
        self.tabWidgetSimulatorSettings.setTabText(self.tabWidgetSimulatorSettings.indexOf(self.tabLog), QCoreApplication.translate("DialogSimulator", u"Log settings", None))
        self.btnTestSniffSettings.setText(QCoreApplication.translate("DialogSimulator", u"Test sniffer settings", None))
        self.tabWidgetSimulatorSettings.setTabText(self.tabWidgetSimulatorSettings.indexOf(self.tabRX), QCoreApplication.translate("DialogSimulator", u"RX settings", None))
        self.tabWidgetSimulatorSettings.setTabText(self.tabWidgetSimulatorSettings.indexOf(self.tabTX), QCoreApplication.translate("DialogSimulator", u"TX settings", None))
        self.groupBoxSimulationStatus.setTitle(QCoreApplication.translate("DialogSimulator", u"Simulation Status", None))
        self.label.setText(QCoreApplication.translate("DialogSimulator", u"Current iteration:", None))
        self.lblCurrentRepeatValue.setText(QCoreApplication.translate("DialogSimulator", u"0", None))
        self.label_2.setText(QCoreApplication.translate("DialogSimulator", u"Current item:", None))
        self.lblCurrentItemValue.setText(QCoreApplication.translate("DialogSimulator", u"0", None))
        self.btnSaveLog.setText(QCoreApplication.translate("DialogSimulator", u"...", None))
        self.groupBoxRXStatus.setTitle(QCoreApplication.translate("DialogSimulator", u"RX Status", None))
        self.checkBoxCaptureFullRX.setText(QCoreApplication.translate("DialogSimulator", u"Capture complete RX", None))
#if QT_CONFIG(tooltip)
        self.btnSaveRX.setToolTip(QCoreApplication.translate("DialogSimulator", u"Save current capture", None))
#endif // QT_CONFIG(tooltip)
        self.btnSaveRX.setText(QCoreApplication.translate("DialogSimulator", u"Save", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_simulation), QCoreApplication.translate("DialogSimulator", u"Status", None))
        self.textEditTranscript.setPlaceholderText(QCoreApplication.translate("DialogSimulator", u"Here you will find all messages that were sent and received during simulation.", None))
        self.radioButtonTranscriptBit.setText(QCoreApplication.translate("DialogSimulator", u"Bit &view", None))
        self.radioButtonTranscriptHex.setText(QCoreApplication.translate("DialogSimulator", u"Hex view", None))
        self.btnOpenInAnalysis.setText(QCoreApplication.translate("DialogSimulator", u"Open in Analysis", None))
        self.btnSaveTranscript.setText(QCoreApplication.translate("DialogSimulator", u"...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("DialogSimulator", u"Messages", None))
        self.textEditDevices.setPlaceholderText(QCoreApplication.translate("DialogSimulator", u"After simulation start you will see the log messages of your configured SDRs here.", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_device), QCoreApplication.translate("DialogSimulator", u"Devices", None))
        self.btnStartStop.setText(QCoreApplication.translate("DialogSimulator", u"Start", None))
        self.tabWidgetSimulatorSettings.setTabText(self.tabWidgetSimulatorSettings.indexOf(self.tabSimulation), QCoreApplication.translate("DialogSimulator", u"Simulation", None))
    # retranslateUi

