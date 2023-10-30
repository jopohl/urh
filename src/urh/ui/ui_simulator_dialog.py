# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DialogSimulator(object):
    def setupUi(self, DialogSimulator):
        DialogSimulator.setObjectName("DialogSimulator")
        DialogSimulator.resize(1088, 823)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(DialogSimulator)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.tabWidgetSimulatorSettings = QtWidgets.QTabWidget(DialogSimulator)
        self.tabWidgetSimulatorSettings.setStyleSheet("QTabWidget::pane { border: 0; }")
        self.tabWidgetSimulatorSettings.setObjectName("tabWidgetSimulatorSettings")
        self.tabLog = QtWidgets.QWidget()
        self.tabLog.setObjectName("tabLog")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tabLog)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.gvSimulator = LoggingGraphicsView(self.tabLog)
        self.gvSimulator.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.gvSimulator.setObjectName("gvSimulator")
        self.verticalLayout_3.addWidget(self.gvSimulator)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnLogAll = QtWidgets.QPushButton(self.tabLog)
        self.btnLogAll.setAutoDefault(False)
        self.btnLogAll.setObjectName("btnLogAll")
        self.horizontalLayout.addWidget(self.btnLogAll)
        self.btnLogNone = QtWidgets.QPushButton(self.tabLog)
        self.btnLogNone.setAutoDefault(False)
        self.btnLogNone.setObjectName("btnLogNone")
        self.horizontalLayout.addWidget(self.btnLogNone)
        self.btnToggleLog = QtWidgets.QPushButton(self.tabLog)
        self.btnToggleLog.setAutoDefault(False)
        self.btnToggleLog.setObjectName("btnToggleLog")
        self.horizontalLayout.addWidget(self.btnToggleLog)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.tabWidgetSimulatorSettings.addTab(self.tabLog, "")
        self.tabRX = QtWidgets.QWidget()
        self.tabRX.setObjectName("tabRX")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.tabRX)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.scrollAreaRX = QtWidgets.QScrollArea(self.tabRX)
        self.scrollAreaRX.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollAreaRX.setWidgetResizable(True)
        self.scrollAreaRX.setObjectName("scrollAreaRX")
        self.scrollAreaWidgetContentsRX = QtWidgets.QWidget()
        self.scrollAreaWidgetContentsRX.setGeometry(QtCore.QRect(0, 0, 1066, 766))
        self.scrollAreaWidgetContentsRX.setObjectName("scrollAreaWidgetContentsRX")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContentsRX)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.btnTestSniffSettings = QtWidgets.QPushButton(
            self.scrollAreaWidgetContentsRX
        )
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/icons/sniffer.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btnTestSniffSettings.setIcon(icon)
        self.btnTestSniffSettings.setAutoDefault(False)
        self.btnTestSniffSettings.setObjectName("btnTestSniffSettings")
        self.verticalLayout_6.addWidget(self.btnTestSniffSettings)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.verticalLayout_6.addItem(spacerItem)
        self.scrollAreaRX.setWidget(self.scrollAreaWidgetContentsRX)
        self.verticalLayout_5.addWidget(self.scrollAreaRX)
        self.tabWidgetSimulatorSettings.addTab(self.tabRX, "")
        self.tabTX = QtWidgets.QWidget()
        self.tabTX.setObjectName("tabTX")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.tabTX)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.scrollAreaTX = QtWidgets.QScrollArea(self.tabTX)
        self.scrollAreaTX.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollAreaTX.setWidgetResizable(True)
        self.scrollAreaTX.setObjectName("scrollAreaTX")
        self.scrollAreaWidgetContentsTX = QtWidgets.QWidget()
        self.scrollAreaWidgetContentsTX.setGeometry(QtCore.QRect(0, 0, 1066, 766))
        self.scrollAreaWidgetContentsTX.setObjectName("scrollAreaWidgetContentsTX")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContentsTX)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        spacerItem1 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.verticalLayout_8.addItem(spacerItem1)
        self.scrollAreaTX.setWidget(self.scrollAreaWidgetContentsTX)
        self.verticalLayout_7.addWidget(self.scrollAreaTX)
        self.tabWidgetSimulatorSettings.addTab(self.tabTX, "")
        self.tabSimulation = QtWidgets.QWidget()
        self.tabSimulation.setObjectName("tabSimulation")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.tabSimulation)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.tabWidget = QtWidgets.QTabWidget(self.tabSimulation)
        self.tabWidget.setStyleSheet("QTabWidget::pane { border: 0; }")
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Triangular)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_simulation = QtWidgets.QWidget()
        self.tab_simulation.setObjectName("tab_simulation")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout(self.tab_simulation)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.groupBoxSimulationStatus = QtWidgets.QGroupBox(self.tab_simulation)
        self.groupBoxSimulationStatus.setStyleSheet(
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
        self.groupBoxSimulationStatus.setCheckable(True)
        self.groupBoxSimulationStatus.setObjectName("groupBoxSimulationStatus")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.groupBoxSimulationStatus)
        self.verticalLayout_12.setContentsMargins(-1, 15, -1, -1)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.frame = QtWidgets.QFrame(self.groupBoxSimulationStatus)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame.setLineWidth(0)
        self.frame.setObjectName("frame")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.textEditSimulation = QtWidgets.QTextEdit(self.frame)
        self.textEditSimulation.setReadOnly(True)
        self.textEditSimulation.setObjectName("textEditSimulation")
        self.verticalLayout_11.addWidget(self.textEditSimulation)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.lblCurrentRepeatValue = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblCurrentRepeatValue.setFont(font)
        self.lblCurrentRepeatValue.setAlignment(QtCore.Qt.AlignCenter)
        self.lblCurrentRepeatValue.setObjectName("lblCurrentRepeatValue")
        self.horizontalLayout_2.addWidget(self.lblCurrentRepeatValue)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.lblCurrentItemValue = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblCurrentItemValue.setFont(font)
        self.lblCurrentItemValue.setAlignment(QtCore.Qt.AlignCenter)
        self.lblCurrentItemValue.setObjectName("lblCurrentItemValue")
        self.horizontalLayout_2.addWidget(self.lblCurrentItemValue)
        self.btnSaveLog = QtWidgets.QToolButton(self.frame)
        icon = QtGui.QIcon.fromTheme("document-save")
        self.btnSaveLog.setIcon(icon)
        self.btnSaveLog.setObjectName("btnSaveLog")
        self.horizontalLayout_2.addWidget(self.btnSaveLog)
        self.verticalLayout_11.addLayout(self.horizontalLayout_2)
        self.verticalLayout_12.addWidget(self.frame)
        self.verticalLayout_15.addWidget(self.groupBoxSimulationStatus)
        self.groupBoxRXStatus = QtWidgets.QGroupBox(self.tab_simulation)
        self.groupBoxRXStatus.setStyleSheet(
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
        self.groupBoxRXStatus.setCheckable(True)
        self.groupBoxRXStatus.setObjectName("groupBoxRXStatus")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.groupBoxRXStatus)
        self.verticalLayout_14.setContentsMargins(-1, 15, -1, -1)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.frame_2 = QtWidgets.QFrame(self.groupBoxRXStatus)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_2.setLineWidth(0)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.checkBoxCaptureFullRX = QtWidgets.QCheckBox(self.frame_2)
        self.checkBoxCaptureFullRX.setObjectName("checkBoxCaptureFullRX")
        self.horizontalLayout_5.addWidget(self.checkBoxCaptureFullRX)
        spacerItem2 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_5.addItem(spacerItem2)
        self.btnSaveRX = QtWidgets.QToolButton(self.frame_2)
        icon = QtGui.QIcon.fromTheme("document-save")
        self.btnSaveRX.setIcon(icon)
        self.btnSaveRX.setObjectName("btnSaveRX")
        self.horizontalLayout_5.addWidget(self.btnSaveRX)
        self.verticalLayout_13.addLayout(self.horizontalLayout_5)
        self.graphicsViewPreview = LiveGraphicView(self.frame_2)
        self.graphicsViewPreview.setObjectName("graphicsViewPreview")
        self.verticalLayout_13.addWidget(self.graphicsViewPreview)
        self.verticalLayout_14.addWidget(self.frame_2)
        self.verticalLayout_15.addWidget(self.groupBoxRXStatus)
        self.tabWidget.addTab(self.tab_simulation, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textEditTranscript = QtWidgets.QTextEdit(self.tab)
        self.textEditTranscript.setReadOnly(True)
        self.textEditTranscript.setObjectName("textEditTranscript")
        self.verticalLayout.addWidget(self.textEditTranscript)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.radioButtonTranscriptBit = QtWidgets.QRadioButton(self.tab)
        self.radioButtonTranscriptBit.setChecked(True)
        self.radioButtonTranscriptBit.setObjectName("radioButtonTranscriptBit")
        self.horizontalLayout_3.addWidget(self.radioButtonTranscriptBit)
        self.radioButtonTranscriptHex = QtWidgets.QRadioButton(self.tab)
        self.radioButtonTranscriptHex.setObjectName("radioButtonTranscriptHex")
        self.horizontalLayout_3.addWidget(self.radioButtonTranscriptHex)
        spacerItem3 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_3.addItem(spacerItem3)
        self.btnOpenInAnalysis = QtWidgets.QPushButton(self.tab)
        self.btnOpenInAnalysis.setObjectName("btnOpenInAnalysis")
        self.horizontalLayout_3.addWidget(self.btnOpenInAnalysis)
        self.btnSaveTranscript = QtWidgets.QToolButton(self.tab)
        icon = QtGui.QIcon.fromTheme("document-save")
        self.btnSaveTranscript.setIcon(icon)
        self.btnSaveTranscript.setObjectName("btnSaveTranscript")
        self.horizontalLayout_3.addWidget(self.btnSaveTranscript)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.tabWidget.addTab(self.tab, "")
        self.tab_device = QtWidgets.QWidget()
        self.tab_device.setObjectName("tab_device")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.tab_device)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.textEditDevices = QtWidgets.QTextEdit(self.tab_device)
        self.textEditDevices.setReadOnly(True)
        self.textEditDevices.setObjectName("textEditDevices")
        self.verticalLayout_10.addWidget(self.textEditDevices)
        self.tabWidget.addTab(self.tab_device, "")
        self.verticalLayout_9.addWidget(self.tabWidget)
        self.btnStartStop = QtWidgets.QPushButton(self.tabSimulation)
        icon = QtGui.QIcon.fromTheme("media-playback-start")
        self.btnStartStop.setIcon(icon)
        self.btnStartStop.setDefault(True)
        self.btnStartStop.setObjectName("btnStartStop")
        self.verticalLayout_9.addWidget(self.btnStartStop)
        self.tabWidgetSimulatorSettings.addTab(self.tabSimulation, "")
        self.verticalLayout_4.addWidget(self.tabWidgetSimulatorSettings)

        self.retranslateUi(DialogSimulator)
        self.tabWidgetSimulatorSettings.setCurrentIndex(3)
        self.tabWidget.setCurrentIndex(0)
        self.groupBoxSimulationStatus.toggled["bool"].connect(self.frame.setVisible)
        self.groupBoxRXStatus.toggled["bool"].connect(self.frame_2.setVisible)

    def retranslateUi(self, DialogSimulator):
        _translate = QtCore.QCoreApplication.translate
        DialogSimulator.setWindowTitle(_translate("DialogSimulator", "Simulation"))
        self.btnLogAll.setText(_translate("DialogSimulator", "Log all"))
        self.btnLogNone.setText(_translate("DialogSimulator", "Log none"))
        self.btnToggleLog.setText(_translate("DialogSimulator", "Toggle selected"))
        self.tabWidgetSimulatorSettings.setTabText(
            self.tabWidgetSimulatorSettings.indexOf(self.tabLog),
            _translate("DialogSimulator", "Log settings"),
        )
        self.btnTestSniffSettings.setText(
            _translate("DialogSimulator", "Test sniffer settings")
        )
        self.tabWidgetSimulatorSettings.setTabText(
            self.tabWidgetSimulatorSettings.indexOf(self.tabRX),
            _translate("DialogSimulator", "RX settings"),
        )
        self.tabWidgetSimulatorSettings.setTabText(
            self.tabWidgetSimulatorSettings.indexOf(self.tabTX),
            _translate("DialogSimulator", "TX settings"),
        )
        self.groupBoxSimulationStatus.setTitle(
            _translate("DialogSimulator", "Simulation Status")
        )
        self.label.setText(_translate("DialogSimulator", "Current iteration:"))
        self.lblCurrentRepeatValue.setText(_translate("DialogSimulator", "0"))
        self.label_2.setText(_translate("DialogSimulator", "Current item:"))
        self.lblCurrentItemValue.setText(_translate("DialogSimulator", "0"))
        self.btnSaveLog.setText(_translate("DialogSimulator", "..."))
        self.groupBoxRXStatus.setTitle(_translate("DialogSimulator", "RX Status"))
        self.checkBoxCaptureFullRX.setText(
            _translate("DialogSimulator", "Capture complete RX")
        )
        self.btnSaveRX.setToolTip(_translate("DialogSimulator", "Save current capture"))
        self.btnSaveRX.setText(_translate("DialogSimulator", "Save"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_simulation),
            _translate("DialogSimulator", "Status"),
        )
        self.textEditTranscript.setPlaceholderText(
            _translate(
                "DialogSimulator",
                "Here you will find all messages that were sent and received during simulation.",
            )
        )
        self.radioButtonTranscriptBit.setText(
            _translate("DialogSimulator", "Bit &view")
        )
        self.radioButtonTranscriptHex.setText(_translate("DialogSimulator", "Hex view"))
        self.btnOpenInAnalysis.setText(
            _translate("DialogSimulator", "Open in Analysis")
        )
        self.btnSaveTranscript.setText(_translate("DialogSimulator", "..."))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab), _translate("DialogSimulator", "Messages")
        )
        self.textEditDevices.setPlaceholderText(
            _translate(
                "DialogSimulator",
                "After simulation start you will see the log messages of your configured SDRs here.",
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_device),
            _translate("DialogSimulator", "Devices"),
        )
        self.btnStartStop.setText(_translate("DialogSimulator", "Start"))
        self.tabWidgetSimulatorSettings.setTabText(
            self.tabWidgetSimulatorSettings.indexOf(self.tabSimulation),
            _translate("DialogSimulator", "Simulation"),
        )


from urh.ui.views.LiveGraphicView import LiveGraphicView
from urh.ui.views.LoggingGraphicsView import LoggingGraphicsView
from . import urh_rc
