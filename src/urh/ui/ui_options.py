# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'options.ui'
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

import KillerDoubleSpinBox

class Ui_DialogOptions(object):
    def setupUi(self, DialogOptions):
        if DialogOptions.objectName():
            DialogOptions.setObjectName(u"DialogOptions")
        DialogOptions.resize(814, 822)
        icon = QIcon()
        iconThemeName = u"configure"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        DialogOptions.setWindowIcon(icon)
        self.verticalLayout_6 = QVBoxLayout(DialogOptions)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.tabWidget = QTabWidget(DialogOptions)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabGeneration = QWidget()
        self.tabGeneration.setObjectName(u"tabGeneration")
        self.verticalLayout_9 = QVBoxLayout(self.tabGeneration)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.labelFuzzingSamples = QLabel(self.tabGeneration)
        self.labelFuzzingSamples.setObjectName(u"labelFuzzingSamples")

        self.gridLayout_4.addWidget(self.labelFuzzingSamples, 1, 1, 1, 1)

        self.checkBoxDefaultFuzzingPause = QCheckBox(self.tabGeneration)
        self.checkBoxDefaultFuzzingPause.setObjectName(u"checkBoxDefaultFuzzingPause")

        self.gridLayout_4.addWidget(self.checkBoxDefaultFuzzingPause, 0, 0, 1, 2)

        self.doubleSpinBoxFuzzingPause = KillerDoubleSpinBox(self.tabGeneration)
        self.doubleSpinBoxFuzzingPause.setObjectName(u"doubleSpinBoxFuzzingPause")
        self.doubleSpinBoxFuzzingPause.setDecimals(3)
        self.doubleSpinBoxFuzzingPause.setMaximum(999999999.000000000000000)

        self.gridLayout_4.addWidget(self.doubleSpinBoxFuzzingPause, 1, 0, 1, 1)

        self.checkBoxMultipleModulations = QCheckBox(self.tabGeneration)
        self.checkBoxMultipleModulations.setObjectName(u"checkBoxMultipleModulations")

        self.gridLayout_4.addWidget(self.checkBoxMultipleModulations, 2, 0, 1, 2)


        self.verticalLayout_9.addLayout(self.gridLayout_4)

        self.groupBoxModulationAccuracy = QGroupBox(self.tabGeneration)
        self.groupBoxModulationAccuracy.setObjectName(u"groupBoxModulationAccuracy")
        self.verticalLayout_7 = QVBoxLayout(self.groupBoxModulationAccuracy)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.radioButtonLowModulationAccuracy = QRadioButton(self.groupBoxModulationAccuracy)
        self.radioButtonLowModulationAccuracy.setObjectName(u"radioButtonLowModulationAccuracy")

        self.verticalLayout_7.addWidget(self.radioButtonLowModulationAccuracy)

        self.radioButtonMediumModulationAccuracy = QRadioButton(self.groupBoxModulationAccuracy)
        self.radioButtonMediumModulationAccuracy.setObjectName(u"radioButtonMediumModulationAccuracy")

        self.verticalLayout_7.addWidget(self.radioButtonMediumModulationAccuracy)

        self.radioButtonHighModulationAccuracy = QRadioButton(self.groupBoxModulationAccuracy)
        self.radioButtonHighModulationAccuracy.setObjectName(u"radioButtonHighModulationAccuracy")

        self.verticalLayout_7.addWidget(self.radioButtonHighModulationAccuracy)


        self.verticalLayout_9.addWidget(self.groupBoxModulationAccuracy)

        self.verticalSpacer = QSpacerItem(20, 500, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_9.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.tabGeneration, QString())
        self.tabView = QWidget()
        self.tabView.setObjectName(u"tabView")
        self.verticalLayout = QVBoxLayout(self.tabView)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_7 = QLabel(self.tabView)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_2.addWidget(self.label_7)

        self.comboBoxDefaultView = QComboBox(self.tabView)
        self.comboBoxDefaultView.addItem(QString())
        self.comboBoxDefaultView.addItem(QString())
        self.comboBoxDefaultView.addItem(QString())
        self.comboBoxDefaultView.setObjectName(u"comboBoxDefaultView")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBoxDefaultView.sizePolicy().hasHeightForWidth())
        self.comboBoxDefaultView.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.comboBoxDefaultView)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.checkBoxShowConfirmCloseDialog = QCheckBox(self.tabView)
        self.checkBoxShowConfirmCloseDialog.setObjectName(u"checkBoxShowConfirmCloseDialog")

        self.verticalLayout.addWidget(self.checkBoxShowConfirmCloseDialog)

        self.checkBoxHoldShiftToDrag = QCheckBox(self.tabView)
        self.checkBoxHoldShiftToDrag.setObjectName(u"checkBoxHoldShiftToDrag")

        self.verticalLayout.addWidget(self.checkBoxHoldShiftToDrag)

        self.checkBoxPauseTime = QCheckBox(self.tabView)
        self.checkBoxPauseTime.setObjectName(u"checkBoxPauseTime")

        self.verticalLayout.addWidget(self.checkBoxPauseTime)

        self.checkBoxAlignLabels = QCheckBox(self.tabView)
        self.checkBoxAlignLabels.setObjectName(u"checkBoxAlignLabels")

        self.verticalLayout.addWidget(self.checkBoxAlignLabels)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.labelFontSize = QLabel(self.tabView)
        self.labelFontSize.setObjectName(u"labelFontSize")

        self.horizontalLayout.addWidget(self.labelFontSize)

        self.spinBoxFontSize = QSpinBox(self.tabView)
        self.spinBoxFontSize.setObjectName(u"spinBoxFontSize")
        self.spinBoxFontSize.setMinimum(1)
        self.spinBoxFontSize.setMaximum(120)
        self.spinBoxFontSize.setValue(10)

        self.horizontalLayout.addWidget(self.spinBoxFontSize)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_9 = QLabel(self.tabView)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout_4.addWidget(self.label_9)

        self.comboBoxTheme = QComboBox(self.tabView)
        self.comboBoxTheme.addItem(QString())
        self.comboBoxTheme.addItem(QString())
        self.comboBoxTheme.addItem(QString())
        self.comboBoxTheme.setObjectName(u"comboBoxTheme")

        self.horizontalLayout_4.addWidget(self.comboBoxTheme)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.labelIconTheme = QLabel(self.tabView)
        self.labelIconTheme.setObjectName(u"labelIconTheme")

        self.horizontalLayout_5.addWidget(self.labelIconTheme)

        self.comboBoxIconTheme = QComboBox(self.tabView)
        self.comboBoxIconTheme.addItem(QString())
        self.comboBoxIconTheme.addItem(QString())
        self.comboBoxIconTheme.setObjectName(u"comboBoxIconTheme")

        self.horizontalLayout_5.addWidget(self.comboBoxIconTheme)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.groupBoxSpectrogramColormap = QGroupBox(self.tabView)
        self.groupBoxSpectrogramColormap.setObjectName(u"groupBoxSpectrogramColormap")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxSpectrogramColormap)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.scrollAreaSpectrogramColormap = QScrollArea(self.groupBoxSpectrogramColormap)
        self.scrollAreaSpectrogramColormap.setObjectName(u"scrollAreaSpectrogramColormap")
        self.scrollAreaSpectrogramColormap.setWidgetResizable(True)
        self.scrollAreaWidgetSpectrogramColormapContents = QWidget()
        self.scrollAreaWidgetSpectrogramColormapContents.setObjectName(u"scrollAreaWidgetSpectrogramColormapContents")
        self.scrollAreaWidgetSpectrogramColormapContents.setGeometry(QRect(0, 0, 762, 397))
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetSpectrogramColormapContents)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.scrollAreaSpectrogramColormap.setWidget(self.scrollAreaWidgetSpectrogramColormapContents)

        self.verticalLayout_2.addWidget(self.scrollAreaSpectrogramColormap)


        self.verticalLayout.addWidget(self.groupBoxSpectrogramColormap)

        self.tabWidget.addTab(self.tabView, QString())
        self.tabFieldtypes = QWidget()
        self.tabFieldtypes.setObjectName(u"tabFieldtypes")
        self.verticalLayout_5 = QVBoxLayout(self.tabFieldtypes)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.tblLabeltypes = QTableView(self.tabFieldtypes)
        self.tblLabeltypes.setObjectName(u"tblLabeltypes")
        self.tblLabeltypes.setAlternatingRowColors(True)

        self.horizontalLayout_3.addWidget(self.tblLabeltypes)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.btnAddLabelType = QToolButton(self.tabFieldtypes)
        self.btnAddLabelType.setObjectName(u"btnAddLabelType")
        icon1 = QIcon()
        iconThemeName = u"list-add"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnAddLabelType.setIcon(icon1)

        self.verticalLayout_3.addWidget(self.btnAddLabelType)

        self.btnRemoveLabeltype = QToolButton(self.tabFieldtypes)
        self.btnRemoveLabeltype.setObjectName(u"btnRemoveLabeltype")
        icon2 = QIcon()
        iconThemeName = u"list-remove"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnRemoveLabeltype.setIcon(icon2)

        self.verticalLayout_3.addWidget(self.btnRemoveLabeltype)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_5)


        self.horizontalLayout_3.addLayout(self.verticalLayout_3)


        self.verticalLayout_5.addLayout(self.horizontalLayout_3)

        self.verticalSpacer_4 = QSpacerItem(20, 203, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_4)

        self.tabWidget.addTab(self.tabFieldtypes, QString())
        self.tab_plugins = QWidget()
        self.tab_plugins.setObjectName(u"tab_plugins")
        self.tabWidget.addTab(self.tab_plugins, QString())
        self.tabDevices = QWidget()
        self.tabDevices.setObjectName(u"tabDevices")
        self.verticalLayout_8 = QVBoxLayout(self.tabDevices)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.labelInfoDeviceTable = QLabel(self.tabDevices)
        self.labelInfoDeviceTable.setObjectName(u"labelInfoDeviceTable")
        font = QFont()
        font.setItalic(True)
        self.labelInfoDeviceTable.setFont(font)
        self.labelInfoDeviceTable.setWordWrap(True)

        self.verticalLayout_8.addWidget(self.labelInfoDeviceTable)

        self.tblDevices = QTableView(self.tabDevices)
        self.tblDevices.setObjectName(u"tblDevices")
        self.tblDevices.setAlternatingRowColors(True)
        self.tblDevices.setShowGrid(False)
        self.tblDevices.horizontalHeader().setDefaultSectionSize(200)
        self.tblDevices.verticalHeader().setVisible(False)

        self.verticalLayout_8.addWidget(self.tblDevices)

        self.labelDeviceMissingInfo = QLabel(self.tabDevices)
        self.labelDeviceMissingInfo.setObjectName(u"labelDeviceMissingInfo")
        font1 = QFont()
        font1.setItalic(False)
        self.labelDeviceMissingInfo.setFont(font1)
        self.labelDeviceMissingInfo.setWordWrap(True)

        self.verticalLayout_8.addWidget(self.labelDeviceMissingInfo)

        self.line = QFrame(self.tabDevices)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_8.addWidget(self.line)

        self.groupBoxNativeOptions = QGroupBox(self.tabDevices)
        self.groupBoxNativeOptions.setObjectName(u"groupBoxNativeOptions")
        self.gridLayout_5 = QGridLayout(self.groupBoxNativeOptions)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.labelRebuildNativeStatus = QLabel(self.groupBoxNativeOptions)
        self.labelRebuildNativeStatus.setObjectName(u"labelRebuildNativeStatus")
        self.labelRebuildNativeStatus.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_5.addWidget(self.labelRebuildNativeStatus, 3, 2, 1, 1)

        self.labelLibDirs = QLabel(self.groupBoxNativeOptions)
        self.labelLibDirs.setObjectName(u"labelLibDirs")

        self.gridLayout_5.addWidget(self.labelLibDirs, 2, 0, 1, 1)

        self.btnRebuildNative = QPushButton(self.groupBoxNativeOptions)
        self.btnRebuildNative.setObjectName(u"btnRebuildNative")
        self.btnRebuildNative.setEnabled(True)
        icon3 = QIcon()
        iconThemeName = u"view-refresh"
        if QIcon.hasThemeIcon(iconThemeName):
            icon3 = QIcon.fromTheme(iconThemeName)
        else:
            icon3.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnRebuildNative.setIcon(icon3)

        self.gridLayout_5.addWidget(self.btnRebuildNative, 3, 0, 1, 1)

        self.labelNativeRebuildInfo = QLabel(self.groupBoxNativeOptions)
        self.labelNativeRebuildInfo.setObjectName(u"labelNativeRebuildInfo")
        self.labelNativeRebuildInfo.setWordWrap(True)

        self.gridLayout_5.addWidget(self.labelNativeRebuildInfo, 1, 0, 1, 3)

        self.lineEditLibDirs = QLineEdit(self.groupBoxNativeOptions)
        self.lineEditLibDirs.setObjectName(u"lineEditLibDirs")

        self.gridLayout_5.addWidget(self.lineEditLibDirs, 2, 2, 1, 1)

        self.btnViewBuildLog = QPushButton(self.groupBoxNativeOptions)
        self.btnViewBuildLog.setObjectName(u"btnViewBuildLog")
        icon4 = QIcon()
        iconThemeName = u"utilities-log-viewer"
        if QIcon.hasThemeIcon(iconThemeName):
            icon4 = QIcon.fromTheme(iconThemeName)
        else:
            icon4.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnViewBuildLog.setIcon(icon4)

        self.gridLayout_5.addWidget(self.btnViewBuildLog, 3, 1, 1, 1)


        self.verticalLayout_8.addWidget(self.groupBoxNativeOptions)

        self.line_2 = QFrame(self.tabDevices)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_8.addWidget(self.line_2)

        self.groupBox_3 = QGroupBox(self.tabDevices)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_2 = QGridLayout(self.groupBox_3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_11 = QLabel(self.groupBox_3)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setFont(font)

        self.gridLayout_2.addWidget(self.label_11, 0, 0, 1, 2)

        self.lineEditPython2Interpreter = QLineEdit(self.groupBox_3)
        self.lineEditPython2Interpreter.setObjectName(u"lineEditPython2Interpreter")

        self.gridLayout_2.addWidget(self.lineEditPython2Interpreter, 1, 1, 1, 1)

        self.lGnuradioInstalled = QLabel(self.groupBox_3)
        self.lGnuradioInstalled.setObjectName(u"lGnuradioInstalled")
        self.lGnuradioInstalled.setStyleSheet(u"")

        self.gridLayout_2.addWidget(self.lGnuradioInstalled, 3, 0, 1, 2)

        self.lineEditGnuradioDirectory = QLineEdit(self.groupBox_3)
        self.lineEditGnuradioDirectory.setObjectName(u"lineEditGnuradioDirectory")
        self.lineEditGnuradioDirectory.setEnabled(True)

        self.gridLayout_2.addWidget(self.lineEditGnuradioDirectory, 2, 1, 1, 1)

        self.radioButtonPython2Interpreter = QRadioButton(self.groupBox_3)
        self.radioButtonPython2Interpreter.setObjectName(u"radioButtonPython2Interpreter")

        self.gridLayout_2.addWidget(self.radioButtonPython2Interpreter, 1, 0, 1, 1)

        self.radioButtonGnuradioDirectory = QRadioButton(self.groupBox_3)
        self.radioButtonGnuradioDirectory.setObjectName(u"radioButtonGnuradioDirectory")

        self.gridLayout_2.addWidget(self.radioButtonGnuradioDirectory, 2, 0, 1, 1)

        self.btnChoosePython2Interpreter = QToolButton(self.groupBox_3)
        self.btnChoosePython2Interpreter.setObjectName(u"btnChoosePython2Interpreter")

        self.gridLayout_2.addWidget(self.btnChoosePython2Interpreter, 1, 2, 1, 1)

        self.btnChooseGnuRadioDirectory = QToolButton(self.groupBox_3)
        self.btnChooseGnuRadioDirectory.setObjectName(u"btnChooseGnuRadioDirectory")

        self.gridLayout_2.addWidget(self.btnChooseGnuRadioDirectory, 2, 2, 1, 1)


        self.verticalLayout_8.addWidget(self.groupBox_3)

        self.line_3 = QFrame(self.tabDevices)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_8.addWidget(self.line_3)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_8 = QLabel(self.tabDevices)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_3.addWidget(self.label_8, 0, 0, 1, 1)

        self.spinBoxNumSendingRepeats = QSpinBox(self.tabDevices)
        self.spinBoxNumSendingRepeats.setObjectName(u"spinBoxNumSendingRepeats")
        self.spinBoxNumSendingRepeats.setProperty("showGroupSeparator", False)
        self.spinBoxNumSendingRepeats.setMaximum(999999999)
        self.spinBoxNumSendingRepeats.setDisplayIntegerBase(10)

        self.gridLayout_3.addWidget(self.spinBoxNumSendingRepeats, 0, 1, 1, 1)

        self.label_5 = QLabel(self.tabDevices)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_3.addWidget(self.label_5, 1, 0, 1, 1)

        self.doubleSpinBoxRAMThreshold = QDoubleSpinBox(self.tabDevices)
        self.doubleSpinBoxRAMThreshold.setObjectName(u"doubleSpinBoxRAMThreshold")
        self.doubleSpinBoxRAMThreshold.setMinimum(1.000000000000000)
        self.doubleSpinBoxRAMThreshold.setMaximum(100.000000000000000)

        self.gridLayout_3.addWidget(self.doubleSpinBoxRAMThreshold, 1, 1, 1, 1)


        self.verticalLayout_8.addLayout(self.gridLayout_3)

        self.tabWidget.addTab(self.tabDevices, QString())

        self.verticalLayout_6.addWidget(self.tabWidget)


        self.retranslateUi(DialogOptions)

        self.tabWidget.setCurrentIndex(0)

    # setupUi

    def retranslateUi(self, DialogOptions):
        DialogOptions.setWindowTitle(QCoreApplication.translate("DialogOptions", u"Options", None))
        self.labelFuzzingSamples.setText(QCoreApplication.translate("DialogOptions", u"Samples", None))
#if QT_CONFIG(tooltip)
        self.checkBoxDefaultFuzzingPause.setToolTip(QCoreApplication.translate("DialogOptions", u"<html><head/><body><p>If you disable the default pause, the pause of the fuzzed message will be used.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBoxDefaultFuzzingPause.setText(QCoreApplication.translate("DialogOptions", u"Use a default pause for fuzzed messages", None))
        self.checkBoxMultipleModulations.setText(QCoreApplication.translate("DialogOptions", u"Enable modulation profiles", None))
        self.groupBoxModulationAccuracy.setTitle(QCoreApplication.translate("DialogOptions", u"Modulation Accuracy", None))
        self.radioButtonLowModulationAccuracy.setText(QCoreApplication.translate("DialogOptions", u"Low (2x8 bit) - Recommended for HackRF and RTL-SDR", None))
        self.radioButtonMediumModulationAccuracy.setText(QCoreApplication.translate("DialogOptions", u"Medium (2x16 bit) - Recommended for BladeRF, PlutoSDR and SDRPlay", None))
        self.radioButtonHighModulationAccuracy.setText(QCoreApplication.translate("DialogOptions", u"High (2x32 bit) - Recommended if you are not sure what to choose", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabGeneration), QCoreApplication.translate("DialogOptions", u"Generation", None))
        self.label_7.setText(QCoreApplication.translate("DialogOptions", u"Default View:", None))
        self.comboBoxDefaultView.setItemText(0, QCoreApplication.translate("DialogOptions", u"Bit", None))
        self.comboBoxDefaultView.setItemText(1, QCoreApplication.translate("DialogOptions", u"Hex", None))
        self.comboBoxDefaultView.setItemText(2, QCoreApplication.translate("DialogOptions", u"ASCII", None))

        self.checkBoxShowConfirmCloseDialog.setText(QCoreApplication.translate("DialogOptions", u"Show \"confirm close\" dialog", None))
#if QT_CONFIG(tooltip)
        self.checkBoxHoldShiftToDrag.setToolTip(QCoreApplication.translate("DialogOptions", u"<html><head/><body><p>If checked, you need to <span style=\" font-weight:600;\">hold the Shift key to drag</span> with the mouse inside graphic views like the drawn signal in Interpreation tab, while making a selection with the mouse does not require holding any buttons.</p><p>If unchecked, this is inverted: Hold shift to make a selection, and drag by default.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBoxHoldShiftToDrag.setText(QCoreApplication.translate("DialogOptions", u"Hold shift to drag", None))
        self.checkBoxPauseTime.setText(QCoreApplication.translate("DialogOptions", u"Show pauses as time", None))
        self.checkBoxAlignLabels.setText(QCoreApplication.translate("DialogOptions", u"Align on labels", None))
        self.labelFontSize.setText(QCoreApplication.translate("DialogOptions", u"<html><head/><body><p>Application font size (<span style=\" font-weight:600;\">restart</span> for full effect):</p></body></html>", None))
        self.spinBoxFontSize.setSuffix(QCoreApplication.translate("DialogOptions", u"pt", None))
        self.label_9.setText(QCoreApplication.translate("DialogOptions", u"Choose application theme (requires restart):", None))
        self.comboBoxTheme.setItemText(0, QCoreApplication.translate("DialogOptions", u"native look (default)", None))
        self.comboBoxTheme.setItemText(1, QCoreApplication.translate("DialogOptions", u"fallback theme", None))
        self.comboBoxTheme.setItemText(2, QCoreApplication.translate("DialogOptions", u"fallback theme (dark)", None))

        self.labelIconTheme.setText(QCoreApplication.translate("DialogOptions", u"Choose icon theme (requires restart):", None))
        self.comboBoxIconTheme.setItemText(0, QCoreApplication.translate("DialogOptions", u"bundled icons (default)", None))
        self.comboBoxIconTheme.setItemText(1, QCoreApplication.translate("DialogOptions", u"native icon theme", None))

        self.groupBoxSpectrogramColormap.setTitle(QCoreApplication.translate("DialogOptions", u"Spectrogram Colormap", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabView), QCoreApplication.translate("DialogOptions", u"View", None))
        self.btnAddLabelType.setText(QCoreApplication.translate("DialogOptions", u"...", None))
        self.btnRemoveLabeltype.setText(QCoreApplication.translate("DialogOptions", u"...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabFieldtypes), QCoreApplication.translate("DialogOptions", u"Fieldtypes", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_plugins), QCoreApplication.translate("DialogOptions", u"Plugins", None))
#if QT_CONFIG(tooltip)
        self.labelInfoDeviceTable.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.labelInfoDeviceTable.setText(QCoreApplication.translate("DialogOptions", u"<html><head/><body><p>Use the checkboxes in the table below to choose device backends and enable or disable devices. Disabled devices will not show up in device related dialogs such as send or receive.</p></body></html>", None))
        self.labelDeviceMissingInfo.setText(QCoreApplication.translate("DialogOptions", u"<html><head/><body><p>Missing a native backend? Perform a <a href=\"health_check\"><span style=\" text-decoration: underline; color:#0000ff;\">health check</span></a>! If GNU Radio backend is not available double check the GNU Radio settings below.</p></body></html>", None))
        self.groupBoxNativeOptions.setTitle(QCoreApplication.translate("DialogOptions", u"Native options", None))
        self.labelRebuildNativeStatus.setText(QCoreApplication.translate("DialogOptions", u"Rebuild <x> new device extensions. Please restart URH to use them.", None))
        self.labelLibDirs.setText(QCoreApplication.translate("DialogOptions", u"Library directories:", None))
#if QT_CONFIG(tooltip)
        self.btnRebuildNative.setToolTip(QCoreApplication.translate("DialogOptions", u"<html><head/><body><p>Rebuild the native device extensions. You need to restart URH after this, to use new extensions.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnRebuildNative.setText(QCoreApplication.translate("DialogOptions", u"Rebuild", None))
        self.labelNativeRebuildInfo.setText(QCoreApplication.translate("DialogOptions", u"You can rebuild the native device extensions here. This is useful, when you installed a device driver afterwards or your drivers are stored in an unusual location.", None))
        self.lineEditLibDirs.setPlaceholderText(QCoreApplication.translate("DialogOptions", u"Comma separated list of additional library directories", None))
        self.btnViewBuildLog.setText(QCoreApplication.translate("DialogOptions", u"View log", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("DialogOptions", u"Gnuradio options", None))
        self.label_11.setText(QCoreApplication.translate("DialogOptions", u"Needed for Gnuradio backend only", None))
#if QT_CONFIG(tooltip)
        self.lineEditPython2Interpreter.setToolTip(QCoreApplication.translate("DialogOptions", u"<html><head/><body><p>Use this option if you installed Gnuradio with your package manager e.g. on Linux and Mac OS X.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEditPython2Interpreter.setPlaceholderText(QCoreApplication.translate("DialogOptions", u"/usr/bin/python2", None))
        self.lGnuradioInstalled.setText(QCoreApplication.translate("DialogOptions", u"Gnuradio installation found", None))
#if QT_CONFIG(tooltip)
        self.lineEditGnuradioDirectory.setToolTip(QCoreApplication.translate("DialogOptions", u"<html><head/><body><p>If you installed Gnuradio with a bundled python interpreter, you need to enter the site-packages path of the installation here. The path should be something like <span style=\" font-style:italic;\">C:\\Program Files\\GNURadio-3.7</span>.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEditGnuradioDirectory.setPlaceholderText(QCoreApplication.translate("DialogOptions", u"C:\\...\\Gnuradio", None))
#if QT_CONFIG(tooltip)
        self.radioButtonPython2Interpreter.setToolTip(QCoreApplication.translate("DialogOptions", u"<html><head/><body><p>Use this option if you installed Gnuradio with your package manager e.g. on Linux and Mac OS X.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.radioButtonPython2Interpreter.setText(QCoreApplication.translate("DialogOptions", u"&Python2 interpreter", None))
#if QT_CONFIG(tooltip)
        self.radioButtonGnuradioDirectory.setToolTip(QCoreApplication.translate("DialogOptions", u"<html><head/><body><p>If you installed Gnuradio with a bundled python interpreter, you need to enter the site-packages path of the installation here. The path should be something like <span style=\" font-style:italic;\">C:\\Program Files\\GNURadio-3.7</span>.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.radioButtonGnuradioDirectory.setText(QCoreApplication.translate("DialogOptions", u"Gn&uradio Directory", None))
        self.btnChoosePython2Interpreter.setText(QCoreApplication.translate("DialogOptions", u"...", None))
        self.btnChooseGnuRadioDirectory.setText(QCoreApplication.translate("DialogOptions", u"...", None))
        self.label_8.setText(QCoreApplication.translate("DialogOptions", u"Default sending repititions:", None))
        self.spinBoxNumSendingRepeats.setSpecialValueText(QCoreApplication.translate("DialogOptions", u"Infinite", None))
        self.label_5.setText(QCoreApplication.translate("DialogOptions", u"Use this percentage of available RAM for buffer allocation:", None))
        self.doubleSpinBoxRAMThreshold.setSuffix(QCoreApplication.translate("DialogOptions", u"%", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabDevices), QCoreApplication.translate("DialogOptions", u"Device", None))
    # retranslateUi

