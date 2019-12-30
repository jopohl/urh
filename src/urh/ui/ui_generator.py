# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'generator.ui'
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

import ElidedLabel
import GeneratorTreeView
import GeneratorTableView
import GeneratorListWidget
import GeneratorListView

class Ui_GeneratorTab(object):
    def setupUi(self, GeneratorTab):
        if GeneratorTab.objectName():
            GeneratorTab.setObjectName(u"GeneratorTab")
        GeneratorTab.resize(1287, 774)
        self.verticalLayout_3 = QVBoxLayout(GeneratorTab)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(GeneratorTab)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1287, 774))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.splitter = QSplitter(self.scrollAreaWidgetContents)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setStyleSheet(u"QSplitter::handle:horizontal {\n"
"margin: 4px 0px;\n"
"    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"stop:0 rgba(255, 255, 255, 0), \n"
"stop:0.5 rgba(100, 100, 100, 100), \n"
"stop:1 rgba(255, 255, 255, 0));\n"
"image: url(:/icons/icons/splitter_handle_vertical.svg);\n"
"}")
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setHandleWidth(6)
        self.layoutWidget_2 = QWidget(self.splitter)
        self.layoutWidget_2.setObjectName(u"layoutWidget_2")
        self.verticalLayout = QVBoxLayout(self.layoutWidget_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.tabWidget = QTabWidget(self.layoutWidget_2)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setStyleSheet(u"QTabWidget::pane { border: 0; }")
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.tab_proto = QWidget()
        self.tab_proto.setObjectName(u"tab_proto")
        self.verticalLayout_4 = QVBoxLayout(self.tab_proto)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.treeProtocols = GeneratorTreeView(self.tab_proto)
        self.treeProtocols.setObjectName(u"treeProtocols")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.treeProtocols.sizePolicy().hasHeightForWidth())
        self.treeProtocols.setSizePolicy(sizePolicy1)
        self.treeProtocols.header().setDefaultSectionSize(57)

        self.verticalLayout_4.addWidget(self.treeProtocols)

        self.tabWidget.addTab(self.tab_proto, QString())
        self.tab_pauses = QWidget()
        self.tab_pauses.setObjectName(u"tab_pauses")
        self.gridLayout_5 = QGridLayout(self.tab_pauses)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.lWPauses = GeneratorListWidget(self.tab_pauses)
        self.lWPauses.setObjectName(u"lWPauses")
        sizePolicy.setHeightForWidth(self.lWPauses.sizePolicy().hasHeightForWidth())
        self.lWPauses.setSizePolicy(sizePolicy)
        self.lWPauses.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.lWPauses.setProperty("showDropIndicator", False)
        self.lWPauses.setDragDropMode(QAbstractItemView.NoDragDrop)

        self.gridLayout_5.addWidget(self.lWPauses, 0, 0, 1, 2)

        self.tabWidget.addTab(self.tab_pauses, QString())
        self.tab_fuzzing = QWidget()
        self.tab_fuzzing.setObjectName(u"tab_fuzzing")
        self.verticalLayout_9 = QVBoxLayout(self.tab_fuzzing)
        self.verticalLayout_9.setSpacing(6)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.listViewProtoLabels = GeneratorListView(self.tab_fuzzing)
        self.listViewProtoLabels.setObjectName(u"listViewProtoLabels")
        sizePolicy.setHeightForWidth(self.listViewProtoLabels.sizePolicy().hasHeightForWidth())
        self.listViewProtoLabels.setSizePolicy(sizePolicy)
        self.listViewProtoLabels.setEditTriggers(QAbstractItemView.EditKeyPressed)

        self.verticalLayout_9.addWidget(self.listViewProtoLabels)

        self.groupBox = QGroupBox(self.tab_fuzzing)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout_6 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.stackedWidgetFuzzing = QStackedWidget(self.groupBox)
        self.stackedWidgetFuzzing.setObjectName(u"stackedWidgetFuzzing")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.stackedWidgetFuzzing.sizePolicy().hasHeightForWidth())
        self.stackedWidgetFuzzing.setSizePolicy(sizePolicy2)
        self.pageFuzzingUI = QWidget()
        self.pageFuzzingUI.setObjectName(u"pageFuzzingUI")
        self.horizontalLayout_4 = QHBoxLayout(self.pageFuzzingUI)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.btnFuzz = QPushButton(self.pageFuzzingUI)
        self.btnFuzz.setObjectName(u"btnFuzz")

        self.horizontalLayout_4.addWidget(self.btnFuzz)

        self.rBSuccessive = QRadioButton(self.pageFuzzingUI)
        self.rBSuccessive.setObjectName(u"rBSuccessive")
        self.rBSuccessive.setChecked(True)

        self.horizontalLayout_4.addWidget(self.rBSuccessive)

        self.rbConcurrent = QRadioButton(self.pageFuzzingUI)
        self.rbConcurrent.setObjectName(u"rbConcurrent")

        self.horizontalLayout_4.addWidget(self.rbConcurrent)

        self.rBExhaustive = QRadioButton(self.pageFuzzingUI)
        self.rBExhaustive.setObjectName(u"rBExhaustive")

        self.horizontalLayout_4.addWidget(self.rBExhaustive)

        self.stackedWidgetFuzzing.addWidget(self.pageFuzzingUI)
        self.pageFuzzingProgressBar = QWidget()
        self.pageFuzzingProgressBar.setObjectName(u"pageFuzzingProgressBar")
        self.horizontalLayout_7 = QHBoxLayout(self.pageFuzzingProgressBar)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.progressBarFuzzing = QProgressBar(self.pageFuzzingProgressBar)
        self.progressBarFuzzing.setObjectName(u"progressBarFuzzing")
        self.progressBarFuzzing.setValue(24)

        self.horizontalLayout_7.addWidget(self.progressBarFuzzing)

        self.stackedWidgetFuzzing.addWidget(self.pageFuzzingProgressBar)

        self.horizontalLayout_6.addWidget(self.stackedWidgetFuzzing)


        self.verticalLayout_9.addWidget(self.groupBox)

        self.tabWidget.addTab(self.tab_fuzzing, QString())

        self.verticalLayout.addWidget(self.tabWidget)

        self.line_2 = QFrame(self.layoutWidget_2)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.line_2)

        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(0, -1, 0, -1)
        self.modulationLayout_2 = QGridLayout()
        self.modulationLayout_2.setObjectName(u"modulationLayout_2")
        self.lCarrierFreqValue = QLabel(self.layoutWidget_2)
        self.lCarrierFreqValue.setObjectName(u"lCarrierFreqValue")

        self.modulationLayout_2.addWidget(self.lCarrierFreqValue, 1, 1, 1, 1)

        self.lModType = QLabel(self.layoutWidget_2)
        self.lModType.setObjectName(u"lModType")

        self.modulationLayout_2.addWidget(self.lModType, 1, 2, 1, 1)

        self.lModTypeValue = QLabel(self.layoutWidget_2)
        self.lModTypeValue.setObjectName(u"lModTypeValue")

        self.modulationLayout_2.addWidget(self.lModTypeValue, 1, 3, 1, 1)

        self.label_carrier_phase = QLabel(self.layoutWidget_2)
        self.label_carrier_phase.setObjectName(u"label_carrier_phase")

        self.modulationLayout_2.addWidget(self.label_carrier_phase, 2, 0, 1, 1)

        self.lCarrierPhaseValue = QLabel(self.layoutWidget_2)
        self.lCarrierPhaseValue.setObjectName(u"lCarrierPhaseValue")

        self.modulationLayout_2.addWidget(self.lCarrierPhaseValue, 2, 1, 1, 1)

        self.lBitLength = QLabel(self.layoutWidget_2)
        self.lBitLength.setObjectName(u"lBitLength")

        self.modulationLayout_2.addWidget(self.lBitLength, 3, 0, 1, 1)

        self.lBitLenValue = QLabel(self.layoutWidget_2)
        self.lBitLenValue.setObjectName(u"lBitLenValue")

        self.modulationLayout_2.addWidget(self.lBitLenValue, 3, 1, 1, 1)

        self.lEncoding = QLabel(self.layoutWidget_2)
        self.lEncoding.setObjectName(u"lEncoding")

        self.modulationLayout_2.addWidget(self.lEncoding, 0, 0, 1, 1)

        self.lEncodingValue = QLabel(self.layoutWidget_2)
        self.lEncodingValue.setObjectName(u"lEncodingValue")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lEncodingValue.sizePolicy().hasHeightForWidth())
        self.lEncodingValue.setSizePolicy(sizePolicy3)

        self.modulationLayout_2.addWidget(self.lEncodingValue, 0, 1, 1, 1)

        self.lSampleRate = QLabel(self.layoutWidget_2)
        self.lSampleRate.setObjectName(u"lSampleRate")

        self.modulationLayout_2.addWidget(self.lSampleRate, 0, 2, 1, 1)

        self.lSampleRateValue = QLabel(self.layoutWidget_2)
        self.lSampleRateValue.setObjectName(u"lSampleRateValue")

        self.modulationLayout_2.addWidget(self.lSampleRateValue, 0, 3, 1, 1)

        self.lCarrierFrequency = QLabel(self.layoutWidget_2)
        self.lCarrierFrequency.setObjectName(u"lCarrierFrequency")

        self.modulationLayout_2.addWidget(self.lCarrierFrequency, 1, 0, 1, 1)

        self.labelParameterValues = ElidedLabel(self.layoutWidget_2)
        self.labelParameterValues.setObjectName(u"labelParameterValues")

        self.modulationLayout_2.addWidget(self.labelParameterValues, 3, 3, 1, 1)

        self.lParamCaption = QLabel(self.layoutWidget_2)
        self.lParamCaption.setObjectName(u"lParamCaption")

        self.modulationLayout_2.addWidget(self.lParamCaption, 3, 2, 1, 1)

        self.label = QLabel(self.layoutWidget_2)
        self.label.setObjectName(u"label")

        self.modulationLayout_2.addWidget(self.label, 2, 2, 1, 1)

        self.labelBitsPerSymbol = QLabel(self.layoutWidget_2)
        self.labelBitsPerSymbol.setObjectName(u"labelBitsPerSymbol")

        self.modulationLayout_2.addWidget(self.labelBitsPerSymbol, 2, 3, 1, 1)


        self.gridLayout_6.addLayout(self.modulationLayout_2, 0, 0, 1, 3)

        self.line = QFrame(self.layoutWidget_2)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_6.addWidget(self.line, 1, 0, 1, 3)

        self.cBoxModulations = QComboBox(self.layoutWidget_2)
        self.cBoxModulations.addItem(QString())
        self.cBoxModulations.setObjectName(u"cBoxModulations")

        self.gridLayout_6.addWidget(self.cBoxModulations, 2, 1, 1, 1)

        self.prBarGeneration = QProgressBar(self.layoutWidget_2)
        self.prBarGeneration.setObjectName(u"prBarGeneration")
        sizePolicy4 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.prBarGeneration.sizePolicy().hasHeightForWidth())
        self.prBarGeneration.setSizePolicy(sizePolicy4)
        self.prBarGeneration.setValue(0)

        self.gridLayout_6.addWidget(self.prBarGeneration, 5, 0, 1, 1)

        self.btnSend = QPushButton(self.layoutWidget_2)
        self.btnSend.setObjectName(u"btnSend")
        self.btnSend.setEnabled(False)
        icon = QIcon()
        iconThemeName = u"media-playback-start"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnSend.setIcon(icon)

        self.gridLayout_6.addWidget(self.btnSend, 5, 2, 1, 1)

        self.btnEditModulation = QPushButton(self.layoutWidget_2)
        self.btnEditModulation.setObjectName(u"btnEditModulation")

        self.gridLayout_6.addWidget(self.btnEditModulation, 2, 2, 1, 1)

        self.lModulation = QLabel(self.layoutWidget_2)
        self.lModulation.setObjectName(u"lModulation")

        self.gridLayout_6.addWidget(self.lModulation, 2, 0, 1, 1)

        self.btnGenerate = QPushButton(self.layoutWidget_2)
        self.btnGenerate.setObjectName(u"btnGenerate")
        self.btnGenerate.setEnabled(False)
        icon1 = QIcon()
        iconThemeName = u"document-new"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnGenerate.setIcon(icon1)

        self.gridLayout_6.addWidget(self.btnGenerate, 5, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_6)

        self.splitter.addWidget(self.layoutWidget_2)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.gridLayout_2 = QGridLayout(self.layoutWidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(11, 11, 11, 11)
        self.cbViewType = QComboBox(self.layoutWidget)
        self.cbViewType.addItem(QString())
        self.cbViewType.addItem(QString())
        self.cbViewType.addItem(QString())
        self.cbViewType.setObjectName(u"cbViewType")

        self.gridLayout_2.addWidget(self.cbViewType, 2, 6, 1, 1)

        self.lViewType = QLabel(self.layoutWidget)
        self.lViewType.setObjectName(u"lViewType")
        sizePolicy5 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.lViewType.sizePolicy().hasHeightForWidth())
        self.lViewType.setSizePolicy(sizePolicy5)

        self.gridLayout_2.addWidget(self.lViewType, 2, 5, 1, 1)

        self.tableMessages = GeneratorTableView(self.layoutWidget)
        self.tableMessages.setObjectName(u"tableMessages")
        self.tableMessages.setAcceptDrops(True)
        self.tableMessages.setFrameShape(QFrame.StyledPanel)
        self.tableMessages.setDragEnabled(False)
        self.tableMessages.setDragDropOverwriteMode(False)
        self.tableMessages.setDragDropMode(QAbstractItemView.DropOnly)
        self.tableMessages.setDefaultDropAction(Qt.CopyAction)
        self.tableMessages.setAlternatingRowColors(True)
        self.tableMessages.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.tableMessages.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tableMessages.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tableMessages.setShowGrid(False)
        self.tableMessages.horizontalHeader().setHighlightSections(False)
        self.tableMessages.verticalHeader().setHighlightSections(False)

        self.gridLayout_2.addWidget(self.tableMessages, 1, 0, 1, 7)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.labelGeneratedData = QLabel(self.layoutWidget)
        self.labelGeneratedData.setObjectName(u"labelGeneratedData")
        sizePolicy3.setHeightForWidth(self.labelGeneratedData.sizePolicy().hasHeightForWidth())
        self.labelGeneratedData.setSizePolicy(sizePolicy3)
        font = QFont()
        font.setBold(True)
        font.setWeight(75);
        self.labelGeneratedData.setFont(font)
        self.labelGeneratedData.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.labelGeneratedData)

        self.btnSave = QToolButton(self.layoutWidget)
        self.btnSave.setObjectName(u"btnSave")
        sizePolicy5.setHeightForWidth(self.btnSave.sizePolicy().hasHeightForWidth())
        self.btnSave.setSizePolicy(sizePolicy5)
        icon2 = QIcon()
        iconThemeName = u"document-save"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnSave.setIcon(icon2)

        self.horizontalLayout.addWidget(self.btnSave)

        self.btnOpen = QToolButton(self.layoutWidget)
        self.btnOpen.setObjectName(u"btnOpen")
        sizePolicy5.setHeightForWidth(self.btnOpen.sizePolicy().hasHeightForWidth())
        self.btnOpen.setSizePolicy(sizePolicy5)
        icon3 = QIcon()
        iconThemeName = u"document-open"
        if QIcon.hasThemeIcon(iconThemeName):
            icon3 = QIcon.fromTheme(iconThemeName)
        else:
            icon3.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnOpen.setIcon(icon3)

        self.horizontalLayout.addWidget(self.btnOpen)


        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 7)

        self.btnNetworkSDRSend = QPushButton(self.layoutWidget)
        self.btnNetworkSDRSend.setObjectName(u"btnNetworkSDRSend")
        icon4 = QIcon()
        iconThemeName = u"network-wired"
        if QIcon.hasThemeIcon(iconThemeName):
            icon4 = QIcon.fromTheme(iconThemeName)
        else:
            icon4.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnNetworkSDRSend.setIcon(icon4)
        self.btnNetworkSDRSend.setCheckable(True)

        self.gridLayout_2.addWidget(self.btnNetworkSDRSend, 2, 0, 1, 1)

        self.btnRfCatSend = QPushButton(self.layoutWidget)
        self.btnRfCatSend.setObjectName(u"btnRfCatSend")
        icon5 = QIcon()
        iconThemeName = u"network-wireless"
        if QIcon.hasThemeIcon(iconThemeName):
            icon5 = QIcon.fromTheme(iconThemeName)
        else:
            icon5.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnRfCatSend.setIcon(icon5)

        self.gridLayout_2.addWidget(self.btnRfCatSend, 2, 1, 1, 1)

        self.lEstimatedTime = QLabel(self.layoutWidget)
        self.lEstimatedTime.setObjectName(u"lEstimatedTime")

        self.gridLayout_2.addWidget(self.lEstimatedTime, 2, 2, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(38, 22, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_3, 2, 3, 1, 2)

        self.splitter.addWidget(self.layoutWidget)

        self.verticalLayout_2.addWidget(self.splitter)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_3.addWidget(self.scrollArea)


        self.retranslateUi(GeneratorTab)

        self.tabWidget.setCurrentIndex(0)
        self.stackedWidgetFuzzing.setCurrentIndex(0)

    # setupUi

    def retranslateUi(self, GeneratorTab):
        GeneratorTab.setWindowTitle(QCoreApplication.translate("GeneratorTab", u"Form", None))
#if QT_CONFIG(tooltip)
        self.treeProtocols.setToolTip(QCoreApplication.translate("GeneratorTab", u"<html><head/><body><p>Drag&amp;Drop Protocols to the table on the right to fill the generation table.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_proto), QCoreApplication.translate("GeneratorTab", u"Protocols", None))
#if QT_CONFIG(tooltip)
        self.lWPauses.setToolTip(QCoreApplication.translate("GeneratorTab", u"<html><head/><body><p>The pauses will be added automatically when you drag a protocol from the tree above to the table on the right.<br/></p><p>You can see the <span style=\" font-weight:600;\">position</span> of each pause by <span style=\" font-weight:600;\">selecting it</span>. There will be drawn a line in the table indiciating the position of the pause.<br/></p><p>Use context menu or double click to <span style=\" font-weight:600;\">edit a pauses' length</span>.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_pauses), QCoreApplication.translate("GeneratorTab", u"Pauses", None))
        self.groupBox.setTitle(QCoreApplication.translate("GeneratorTab", u"Add fuzzing values to generated data", None))
        self.btnFuzz.setText(QCoreApplication.translate("GeneratorTab", u"Fuzz", None))
#if QT_CONFIG(tooltip)
        self.rBSuccessive.setToolTip(QCoreApplication.translate("GeneratorTab", u"<html><head/><body><p>For multiple labels per message the fuzzed values are inserted <span style=\" font-weight:600;\">one-by-one</span>.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.rBSuccessive.setText(QCoreApplication.translate("GeneratorTab", u"S&uccessive", None))
#if QT_CONFIG(tooltip)
        self.rbConcurrent.setToolTip(QCoreApplication.translate("GeneratorTab", u"<html><head/><body><p>For multiple labels per message the labels are fuzzed <span style=\" font-weight:600;\">at the same time</span>.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.rbConcurrent.setText(QCoreApplication.translate("GeneratorTab", u"&Concurrent", None))
#if QT_CONFIG(tooltip)
        self.rBExhaustive.setToolTip(QCoreApplication.translate("GeneratorTab", u"<html><head/><body><p>For multiple labels per message the fuzzed values are inserted in <span style=\" font-weight:600;\">all possible combinations</span>.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.rBExhaustive.setText(QCoreApplication.translate("GeneratorTab", u"E&xhaustive", None))
        self.progressBarFuzzing.setFormat(QCoreApplication.translate("GeneratorTab", u"%v/%m", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_fuzzing), QCoreApplication.translate("GeneratorTab", u"Fuzzing", None))
        self.lCarrierFreqValue.setText(QCoreApplication.translate("GeneratorTab", u"TextLabel", None))
        self.lModType.setText(QCoreApplication.translate("GeneratorTab", u"Modulation Type:", None))
        self.lModTypeValue.setText(QCoreApplication.translate("GeneratorTab", u"TextLabel", None))
        self.label_carrier_phase.setText(QCoreApplication.translate("GeneratorTab", u"Carrier Phase:", None))
        self.lCarrierPhaseValue.setText(QCoreApplication.translate("GeneratorTab", u"TextLabel", None))
        self.lBitLength.setText(QCoreApplication.translate("GeneratorTab", u"Symbol Length:", None))
        self.lBitLenValue.setText(QCoreApplication.translate("GeneratorTab", u"TextLabel", None))
        self.lEncoding.setText(QCoreApplication.translate("GeneratorTab", u"Encoding:", None))
        self.lEncodingValue.setText(QCoreApplication.translate("GeneratorTab", u"-", None))
        self.lSampleRate.setText(QCoreApplication.translate("GeneratorTab", u"Sample Rate:", None))
        self.lSampleRateValue.setText(QCoreApplication.translate("GeneratorTab", u"TextLabel", None))
        self.lCarrierFrequency.setText(QCoreApplication.translate("GeneratorTab", u"Carrier Frequency:", None))
        self.labelParameterValues.setText(QCoreApplication.translate("GeneratorTab", u"0/100", None))
        self.lParamCaption.setText(QCoreApplication.translate("GeneratorTab", u"Amplitudes:", None))
        self.label.setText(QCoreApplication.translate("GeneratorTab", u"Bits per Symbol:", None))
        self.labelBitsPerSymbol.setText(QCoreApplication.translate("GeneratorTab", u"TextLabel", None))
        self.cBoxModulations.setItemText(0, QCoreApplication.translate("GeneratorTab", u"MyModulation", None))

        self.prBarGeneration.setFormat(QCoreApplication.translate("GeneratorTab", u"Modulating %p%", None))
        self.btnSend.setText(QCoreApplication.translate("GeneratorTab", u"Send data...", None))
        self.btnEditModulation.setText(QCoreApplication.translate("GeneratorTab", u"Edit ...", None))
        self.lModulation.setText(QCoreApplication.translate("GeneratorTab", u"Modulation:", None))
#if QT_CONFIG(tooltip)
        self.btnGenerate.setToolTip(QCoreApplication.translate("GeneratorTab", u"Generate the complex file of the modulated signal, after tuning all parameters above.", None))
#endif // QT_CONFIG(tooltip)
        self.btnGenerate.setText(QCoreApplication.translate("GeneratorTab", u"Generate file...", None))
        self.cbViewType.setItemText(0, QCoreApplication.translate("GeneratorTab", u"Bit", None))
        self.cbViewType.setItemText(1, QCoreApplication.translate("GeneratorTab", u"Hex", None))
        self.cbViewType.setItemText(2, QCoreApplication.translate("GeneratorTab", u"ASCII", None))

        self.lViewType.setText(QCoreApplication.translate("GeneratorTab", u"Viewtype:", None))
        self.labelGeneratedData.setText(QCoreApplication.translate("GeneratorTab", u"Generated Data", None))
#if QT_CONFIG(tooltip)
        self.btnSave.setToolTip(QCoreApplication.translate("GeneratorTab", u"Save current fuzz profile.", None))
#endif // QT_CONFIG(tooltip)
        self.btnSave.setText(QCoreApplication.translate("GeneratorTab", u"...", None))
#if QT_CONFIG(tooltip)
        self.btnOpen.setToolTip(QCoreApplication.translate("GeneratorTab", u"Load a fuzz profile.", None))
#endif // QT_CONFIG(tooltip)
        self.btnOpen.setText(QCoreApplication.translate("GeneratorTab", u"...", None))
#if QT_CONFIG(tooltip)
        self.btnNetworkSDRSend.setToolTip(QCoreApplication.translate("GeneratorTab", u"<html><head/><body><p><span style=\" font-weight:600;\">Send encoded data to your external application via TCP.</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnNetworkSDRSend.setText(QCoreApplication.translate("GeneratorTab", u"Send via Network", None))
#if QT_CONFIG(tooltip)
        self.btnRfCatSend.setToolTip(QCoreApplication.translate("GeneratorTab", u"<html><head/><body><p><span style=\" font-weight:600;\">Send encoded data via RfCat. </span></p><p><span style=\" font-style:italic;\">Hit again for stopping the sending process. Note that you can set the number of repetitions (from 1 to infinite) in:</span></p><p><span style=\" font-style:italic;\">Edit-&gt;Options-&gt;Device-&gt;'Device sending repetitions'</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnRfCatSend.setText(QCoreApplication.translate("GeneratorTab", u"Send via RfCat", None))
#if QT_CONFIG(tooltip)
        self.lEstimatedTime.setToolTip(QCoreApplication.translate("GeneratorTab", u"<html><head/><body><p>The estimated average time is based on the average number of bits per message and average sample rate, you set for the modulations.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lEstimatedTime.setText(QCoreApplication.translate("GeneratorTab", u"Estimated Time: ", None))
    # retranslateUi

