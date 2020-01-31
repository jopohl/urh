# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'modulation.ui'
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

from urh.ui.views.ZoomableGraphicView import ZoomableGraphicView
from urh.ui.KillerDoubleSpinBox import KillerDoubleSpinBox
from urh.ui.views.ZoomAndDropableGraphicView import ZoomAndDropableGraphicView
from urh.ui.views.ModulatorTreeView import ModulatorTreeView

import urh.ui.urh_rc

class Ui_DialogModulation(object):
    def setupUi(self, DialogModulation):
        if DialogModulation.objectName():
            DialogModulation.setObjectName(u"DialogModulation")
        DialogModulation.resize(977, 1041)
        icon = QIcon()
        icon.addFile(u":/icons/icons/modulation.svg", QSize(), QIcon.Normal, QIcon.Off)
        DialogModulation.setWindowIcon(icon)
        self.verticalLayout = QVBoxLayout(DialogModulation)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.comboBoxCustomModulations = QComboBox(DialogModulation)
        self.comboBoxCustomModulations.addItem("")
        self.comboBoxCustomModulations.setObjectName(u"comboBoxCustomModulations")
        self.comboBoxCustomModulations.setEditable(True)
        self.comboBoxCustomModulations.setInsertPolicy(QComboBox.InsertAtCurrent)
        self.comboBoxCustomModulations.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.gridLayout_5.addWidget(self.comboBoxCustomModulations, 0, 0, 1, 1)

        self.btnAddModulation = QToolButton(DialogModulation)
        self.btnAddModulation.setObjectName(u"btnAddModulation")
        icon1 = QIcon()
        iconThemeName = u"list-add"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnAddModulation.setIcon(icon1)

        self.gridLayout_5.addWidget(self.btnAddModulation, 0, 1, 1, 1)

        self.btnRemoveModulation = QToolButton(DialogModulation)
        self.btnRemoveModulation.setObjectName(u"btnRemoveModulation")
        icon2 = QIcon()
        iconThemeName = u"list-remove"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnRemoveModulation.setIcon(icon2)

        self.gridLayout_5.addWidget(self.btnRemoveModulation, 0, 2, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_5)

        self.scrollArea = QScrollArea(DialogModulation)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 965, 984))
        self.gridLayout_7 = QGridLayout(self.scrollAreaWidgetContents_2)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.label_5 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_5.setObjectName(u"label_5")
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setMargin(4)

        self.gridLayout_7.addWidget(self.label_5, 2, 0, 1, 1)

        self.lEqual = QLabel(self.scrollAreaWidgetContents_2)
        self.lEqual.setObjectName(u"lEqual")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lEqual.sizePolicy().hasHeightForWidth())
        self.lEqual.setSizePolicy(sizePolicy)
        self.lEqual.setMaximumSize(QSize(32, 32))
        self.lEqual.setPixmap(QPixmap(u":/icons/icons/equals.svg"))
        self.lEqual.setScaledContents(True)
        self.lEqual.setAlignment(Qt.AlignCenter)

        self.gridLayout_7.addWidget(self.lEqual, 4, 2, 1, 1)

        self.label_6 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font)
        self.label_6.setMargin(4)

        self.gridLayout_7.addWidget(self.label_6, 4, 0, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_5, 8, 1, 1, 1)

        self.label_7 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font)
        self.label_7.setMargin(4)

        self.gridLayout_7.addWidget(self.label_7, 8, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_2, 2, 3, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_3, 4, 1, 1, 1)

        self.label_4 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font)
        self.label_4.setMargin(4)

        self.gridLayout_7.addWidget(self.label_4, 0, 0, 1, 1)

        self.gVOriginalSignal = ZoomAndDropableGraphicView(self.scrollAreaWidgetContents_2)
        self.gVOriginalSignal.setObjectName(u"gVOriginalSignal")
        self.gVOriginalSignal.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.gVOriginalSignal.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.gVOriginalSignal.setRenderHints(QPainter.Antialiasing|QPainter.HighQualityAntialiasing)
        self.gVOriginalSignal.setDragMode(QGraphicsView.NoDrag)

        self.gridLayout_7.addWidget(self.gVOriginalSignal, 9, 1, 1, 3)

        self.scrollArea_5 = QScrollArea(self.scrollAreaWidgetContents_2)
        self.scrollArea_5.setObjectName(u"scrollArea_5")
        self.scrollArea_5.setFrameShape(QFrame.NoFrame)
        self.scrollArea_5.setWidgetResizable(True)
        self.scrollAreaWidgetContents_5 = QWidget()
        self.scrollAreaWidgetContents_5.setObjectName(u"scrollAreaWidgetContents_5")
        self.scrollAreaWidgetContents_5.setGeometry(QRect(0, 0, 400, 330))
        self.gridLayout_4 = QGridLayout(self.scrollAreaWidgetContents_5)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.lCurrentSearchResult = QLabel(self.scrollAreaWidgetContents_5)
        self.lCurrentSearchResult.setObjectName(u"lCurrentSearchResult")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lCurrentSearchResult.sizePolicy().hasHeightForWidth())
        self.lCurrentSearchResult.setSizePolicy(sizePolicy1)
        self.lCurrentSearchResult.setMinimumSize(QSize(0, 0))
        self.lCurrentSearchResult.setMaximumSize(QSize(16777215, 16777215))
        self.lCurrentSearchResult.setAlignment(Qt.AlignCenter)

        self.gridLayout_4.addWidget(self.lCurrentSearchResult, 3, 1, 1, 2)

        self.cbShowDataBitsOnly = QCheckBox(self.scrollAreaWidgetContents_5)
        self.cbShowDataBitsOnly.setObjectName(u"cbShowDataBitsOnly")
        sizePolicy2 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.cbShowDataBitsOnly.sizePolicy().hasHeightForWidth())
        self.cbShowDataBitsOnly.setSizePolicy(sizePolicy2)
        self.cbShowDataBitsOnly.setMinimumSize(QSize(0, 0))
        self.cbShowDataBitsOnly.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_4.addWidget(self.cbShowDataBitsOnly, 2, 0, 1, 5)

        self.btnSearchPrev = QPushButton(self.scrollAreaWidgetContents_5)
        self.btnSearchPrev.setObjectName(u"btnSearchPrev")
        sizePolicy.setHeightForWidth(self.btnSearchPrev.sizePolicy().hasHeightForWidth())
        self.btnSearchPrev.setSizePolicy(sizePolicy)
        self.btnSearchPrev.setMaximumSize(QSize(16777215, 16777215))
        icon3 = QIcon()
        iconThemeName = u"go-previous"
        if QIcon.hasThemeIcon(iconThemeName):
            icon3 = QIcon.fromTheme(iconThemeName)
        else:
            icon3.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnSearchPrev.setIcon(icon3)

        self.gridLayout_4.addWidget(self.btnSearchPrev, 3, 0, 1, 1)

        self.lTotalSearchresults = QLabel(self.scrollAreaWidgetContents_5)
        self.lTotalSearchresults.setObjectName(u"lTotalSearchresults")
        sizePolicy1.setHeightForWidth(self.lTotalSearchresults.sizePolicy().hasHeightForWidth())
        self.lTotalSearchresults.setSizePolicy(sizePolicy1)
        self.lTotalSearchresults.setMaximumSize(QSize(16777215, 16777215))
        self.lTotalSearchresults.setAlignment(Qt.AlignCenter)

        self.gridLayout_4.addWidget(self.lTotalSearchresults, 3, 4, 1, 1)

        self.treeViewSignals = ModulatorTreeView(self.scrollAreaWidgetContents_5)
        self.treeViewSignals.setObjectName(u"treeViewSignals")
        sizePolicy1.setHeightForWidth(self.treeViewSignals.sizePolicy().hasHeightForWidth())
        self.treeViewSignals.setSizePolicy(sizePolicy1)
        self.treeViewSignals.setProperty("showDropIndicator", True)
        self.treeViewSignals.setDragEnabled(True)
        self.treeViewSignals.setDragDropMode(QAbstractItemView.DragOnly)
        self.treeViewSignals.setHeaderHidden(True)

        self.gridLayout_4.addWidget(self.treeViewSignals, 0, 0, 1, 6)

        self.lSlash = QLabel(self.scrollAreaWidgetContents_5)
        self.lSlash.setObjectName(u"lSlash")
        sizePolicy3 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lSlash.sizePolicy().hasHeightForWidth())
        self.lSlash.setSizePolicy(sizePolicy3)
        self.lSlash.setMaximumSize(QSize(7, 16777215))

        self.gridLayout_4.addWidget(self.lSlash, 3, 3, 1, 1)

        self.btnSearchNext = QPushButton(self.scrollAreaWidgetContents_5)
        self.btnSearchNext.setObjectName(u"btnSearchNext")
        sizePolicy.setHeightForWidth(self.btnSearchNext.sizePolicy().hasHeightForWidth())
        self.btnSearchNext.setSizePolicy(sizePolicy)
        self.btnSearchNext.setMaximumSize(QSize(16777215, 16777215))
        icon4 = QIcon()
        iconThemeName = u"go-next"
        if QIcon.hasThemeIcon(iconThemeName):
            icon4 = QIcon.fromTheme(iconThemeName)
        else:
            icon4.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnSearchNext.setIcon(icon4)

        self.gridLayout_4.addWidget(self.btnSearchNext, 3, 5, 1, 1)

        self.chkBoxLockSIV = QCheckBox(self.scrollAreaWidgetContents_5)
        self.chkBoxLockSIV.setObjectName(u"chkBoxLockSIV")
        sizePolicy2.setHeightForWidth(self.chkBoxLockSIV.sizePolicy().hasHeightForWidth())
        self.chkBoxLockSIV.setSizePolicy(sizePolicy2)

        self.gridLayout_4.addWidget(self.chkBoxLockSIV, 1, 0, 1, 5)

        self.scrollArea_5.setWidget(self.scrollAreaWidgetContents_5)

        self.gridLayout_7.addWidget(self.scrollArea_5, 9, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lSamplesInViewModulatedText = QLabel(self.scrollAreaWidgetContents_2)
        self.lSamplesInViewModulatedText.setObjectName(u"lSamplesInViewModulatedText")
        sizePolicy4 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.lSamplesInViewModulatedText.sizePolicy().hasHeightForWidth())
        self.lSamplesInViewModulatedText.setSizePolicy(sizePolicy4)

        self.horizontalLayout.addWidget(self.lSamplesInViewModulatedText)

        self.lSamplesInViewModulated = QLabel(self.scrollAreaWidgetContents_2)
        self.lSamplesInViewModulated.setObjectName(u"lSamplesInViewModulated")
        sizePolicy5 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.lSamplesInViewModulated.sizePolicy().hasHeightForWidth())
        self.lSamplesInViewModulated.setSizePolicy(sizePolicy5)

        self.horizontalLayout.addWidget(self.lSamplesInViewModulated)

        self.label_9 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout.addWidget(self.label_9)

        self.lModulatedSelectedSamples = QLabel(self.scrollAreaWidgetContents_2)
        self.lModulatedSelectedSamples.setObjectName(u"lModulatedSelectedSamples")

        self.horizontalLayout.addWidget(self.lModulatedSelectedSamples)


        self.gridLayout_7.addLayout(self.horizontalLayout, 6, 1, 1, 1)

        self.scrollArea_3 = QScrollArea(self.scrollAreaWidgetContents_2)
        self.scrollArea_3.setObjectName(u"scrollArea_3")
        self.scrollArea_3.setFrameShape(QFrame.NoFrame)
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 380, 141))
        self.gridLayout_2 = QGridLayout(self.scrollAreaWidgetContents_3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.spinBoxSampleRate = KillerDoubleSpinBox(self.scrollAreaWidgetContents_3)
        self.spinBoxSampleRate.setObjectName(u"spinBoxSampleRate")
        sizePolicy6 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.spinBoxSampleRate.sizePolicy().hasHeightForWidth())
        self.spinBoxSampleRate.setSizePolicy(sizePolicy6)
        self.spinBoxSampleRate.setDecimals(3)
        self.spinBoxSampleRate.setMinimum(0.001000000000000)
        self.spinBoxSampleRate.setMaximum(999999999.000000000000000)

        self.gridLayout_2.addWidget(self.spinBoxSampleRate, 2, 1, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_2, 3, 0, 1, 1)

        self.label_3 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_3.setObjectName(u"label_3")
        sizePolicy4.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy4)

        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)

        self.label = QLabel(self.scrollAreaWidgetContents_3)
        self.label.setObjectName(u"label")
        sizePolicy4.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy4)

        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)

        self.spinBoxSamplesPerSymbol = QSpinBox(self.scrollAreaWidgetContents_3)
        self.spinBoxSamplesPerSymbol.setObjectName(u"spinBoxSamplesPerSymbol")
        sizePolicy6.setHeightForWidth(self.spinBoxSamplesPerSymbol.sizePolicy().hasHeightForWidth())
        self.spinBoxSamplesPerSymbol.setSizePolicy(sizePolicy6)
        self.spinBoxSamplesPerSymbol.setMinimum(1)
        self.spinBoxSamplesPerSymbol.setMaximum(999999)

        self.gridLayout_2.addWidget(self.spinBoxSamplesPerSymbol, 1, 1, 1, 1)

        self.linEdDataBits = QLineEdit(self.scrollAreaWidgetContents_3)
        self.linEdDataBits.setObjectName(u"linEdDataBits")
        sizePolicy1.setHeightForWidth(self.linEdDataBits.sizePolicy().hasHeightForWidth())
        self.linEdDataBits.setSizePolicy(sizePolicy1)

        self.gridLayout_2.addWidget(self.linEdDataBits, 0, 0, 1, 2)

        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)

        self.gridLayout_7.addWidget(self.scrollArea_3, 3, 0, 1, 1)

        self.scrollArea_2 = QScrollArea(self.scrollAreaWidgetContents_2)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setFrameShape(QFrame.NoFrame)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 380, 143))
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lCarrierFreq = QLabel(self.scrollAreaWidgetContents)
        self.lCarrierFreq.setObjectName(u"lCarrierFreq")
        sizePolicy4.setHeightForWidth(self.lCarrierFreq.sizePolicy().hasHeightForWidth())
        self.lCarrierFreq.setSizePolicy(sizePolicy4)

        self.gridLayout.addWidget(self.lCarrierFreq, 0, 0, 1, 1)

        self.doubleSpinBoxCarrierFreq = KillerDoubleSpinBox(self.scrollAreaWidgetContents)
        self.doubleSpinBoxCarrierFreq.setObjectName(u"doubleSpinBoxCarrierFreq")
        sizePolicy6.setHeightForWidth(self.doubleSpinBoxCarrierFreq.sizePolicy().hasHeightForWidth())
        self.doubleSpinBoxCarrierFreq.setSizePolicy(sizePolicy6)
        self.doubleSpinBoxCarrierFreq.setDecimals(3)
        self.doubleSpinBoxCarrierFreq.setMinimum(0.000000000000000)
        self.doubleSpinBoxCarrierFreq.setMaximum(99999999999.000000000000000)

        self.gridLayout.addWidget(self.doubleSpinBoxCarrierFreq, 0, 1, 1, 1)

        self.label_2 = QLabel(self.scrollAreaWidgetContents)
        self.label_2.setObjectName(u"label_2")
        sizePolicy4.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy4)

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.doubleSpinBoxCarrierPhase = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.doubleSpinBoxCarrierPhase.setObjectName(u"doubleSpinBoxCarrierPhase")
        sizePolicy6.setHeightForWidth(self.doubleSpinBoxCarrierPhase.sizePolicy().hasHeightForWidth())
        self.doubleSpinBoxCarrierPhase.setSizePolicy(sizePolicy6)
        self.doubleSpinBoxCarrierPhase.setDecimals(3)
        self.doubleSpinBoxCarrierPhase.setMaximum(360.000000000000000)

        self.gridLayout.addWidget(self.doubleSpinBoxCarrierPhase, 1, 1, 1, 1)

        self.btnAutoDetect = QPushButton(self.scrollAreaWidgetContents)
        self.btnAutoDetect.setObjectName(u"btnAutoDetect")
        self.btnAutoDetect.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.btnAutoDetect.sizePolicy().hasHeightForWidth())
        self.btnAutoDetect.setSizePolicy(sizePolicy6)

        self.gridLayout.addWidget(self.btnAutoDetect, 2, 0, 1, 2)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_3, 3, 0, 1, 1)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_7.addWidget(self.scrollArea_2, 1, 0, 1, 1)

        self.lPlus = QLabel(self.scrollAreaWidgetContents_2)
        self.lPlus.setObjectName(u"lPlus")
        sizePolicy2.setHeightForWidth(self.lPlus.sizePolicy().hasHeightForWidth())
        self.lPlus.setSizePolicy(sizePolicy2)
        self.lPlus.setMaximumSize(QSize(32, 32))
        self.lPlus.setPixmap(QPixmap(u":/icons/icons/plus.svg"))
        self.lPlus.setScaledContents(True)
        self.lPlus.setAlignment(Qt.AlignCenter)

        self.gridLayout_7.addWidget(self.lPlus, 2, 2, 1, 1)

        self.gVCarrier = ZoomableGraphicView(self.scrollAreaWidgetContents_2)
        self.gVCarrier.setObjectName(u"gVCarrier")
        sizePolicy7 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.gVCarrier.sizePolicy().hasHeightForWidth())
        self.gVCarrier.setSizePolicy(sizePolicy7)
        self.gVCarrier.setAcceptDrops(False)
        self.gVCarrier.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.gVCarrier.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.gVCarrier.setRenderHints(QPainter.Antialiasing|QPainter.HighQualityAntialiasing)
        self.gVCarrier.setDragMode(QGraphicsView.NoDrag)

        self.gridLayout_7.addWidget(self.gVCarrier, 1, 1, 1, 3)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer, 2, 1, 1, 1)

        self.gVModulated = ZoomableGraphicView(self.scrollAreaWidgetContents_2)
        self.gVModulated.setObjectName(u"gVModulated")
        sizePolicy7.setHeightForWidth(self.gVModulated.sizePolicy().hasHeightForWidth())
        self.gVModulated.setSizePolicy(sizePolicy7)
        self.gVModulated.setAcceptDrops(False)
        self.gVModulated.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.gVModulated.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.gVModulated.setRenderHints(QPainter.Antialiasing|QPainter.HighQualityAntialiasing)
        self.gVModulated.setDragMode(QGraphicsView.NoDrag)

        self.gridLayout_7.addWidget(self.gVModulated, 5, 1, 1, 3)

        self.gVData = ZoomableGraphicView(self.scrollAreaWidgetContents_2)
        self.gVData.setObjectName(u"gVData")
        sizePolicy7.setHeightForWidth(self.gVData.sizePolicy().hasHeightForWidth())
        self.gVData.setSizePolicy(sizePolicy7)
        self.gVData.setAcceptDrops(False)
        self.gVData.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.gVData.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.gVData.setRenderHints(QPainter.Antialiasing|QPainter.HighQualityAntialiasing)
        self.gVData.setDragMode(QGraphicsView.NoDrag)

        self.gridLayout_7.addWidget(self.gVData, 3, 1, 1, 3)

        self.scrollArea_4 = QScrollArea(self.scrollAreaWidgetContents_2)
        self.scrollArea_4.setObjectName(u"scrollArea_4")
        self.scrollArea_4.setFrameShape(QFrame.NoFrame)
        self.scrollArea_4.setWidgetResizable(True)
        self.scrollAreaWidgetContents_4 = QWidget()
        self.scrollAreaWidgetContents_4.setObjectName(u"scrollAreaWidgetContents_4")
        self.scrollAreaWidgetContents_4.setGeometry(QRect(0, 0, 400, 227))
        self.gridLayout_3 = QGridLayout(self.scrollAreaWidgetContents_4)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.spinBoxBitsPerSymbol = QSpinBox(self.scrollAreaWidgetContents_4)
        self.spinBoxBitsPerSymbol.setObjectName(u"spinBoxBitsPerSymbol")
        self.spinBoxBitsPerSymbol.setMinimum(1)
        self.spinBoxBitsPerSymbol.setMaximum(10)

        self.gridLayout_3.addWidget(self.spinBoxBitsPerSymbol, 1, 1, 1, 1)

        self.spinBoxGaussBT = QDoubleSpinBox(self.scrollAreaWidgetContents_4)
        self.spinBoxGaussBT.setObjectName(u"spinBoxGaussBT")
        self.spinBoxGaussBT.setMinimum(0.010000000000000)
        self.spinBoxGaussBT.setMaximum(0.990000000000000)
        self.spinBoxGaussBT.setSingleStep(0.010000000000000)

        self.gridLayout_3.addWidget(self.spinBoxGaussBT, 3, 1, 1, 1)

        self.lGaussWidth = QLabel(self.scrollAreaWidgetContents_4)
        self.lGaussWidth.setObjectName(u"lGaussWidth")

        self.gridLayout_3.addWidget(self.lGaussWidth, 4, 0, 1, 1)

        self.lGaussBT = QLabel(self.scrollAreaWidgetContents_4)
        self.lGaussBT.setObjectName(u"lGaussBT")

        self.gridLayout_3.addWidget(self.lGaussBT, 3, 0, 1, 1)

        self.spinBoxGaussFilterWidth = QDoubleSpinBox(self.scrollAreaWidgetContents_4)
        self.spinBoxGaussFilterWidth.setObjectName(u"spinBoxGaussFilterWidth")
        self.spinBoxGaussFilterWidth.setMinimum(0.010000000000000)
        self.spinBoxGaussFilterWidth.setMaximum(100.000000000000000)
        self.spinBoxGaussFilterWidth.setSingleStep(0.010000000000000)
        self.spinBoxGaussFilterWidth.setValue(1.000000000000000)

        self.gridLayout_3.addWidget(self.spinBoxGaussFilterWidth, 4, 1, 1, 1)

        self.labelBitsPerSymbol = QLabel(self.scrollAreaWidgetContents_4)
        self.labelBitsPerSymbol.setObjectName(u"labelBitsPerSymbol")

        self.gridLayout_3.addWidget(self.labelBitsPerSymbol, 1, 0, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_4, 5, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 5, 1, 1, 1)

        self.lineEditParameters = QLineEdit(self.scrollAreaWidgetContents_4)
        self.lineEditParameters.setObjectName(u"lineEditParameters")
        self.lineEditParameters.setClearButtonEnabled(False)

        self.gridLayout_3.addWidget(self.lineEditParameters, 2, 1, 1, 1)

        self.comboBoxModulationType = QComboBox(self.scrollAreaWidgetContents_4)
        self.comboBoxModulationType.addItem("")
        self.comboBoxModulationType.addItem("")
        self.comboBoxModulationType.addItem("")
        self.comboBoxModulationType.addItem("")
        self.comboBoxModulationType.setObjectName(u"comboBoxModulationType")
        sizePolicy1.setHeightForWidth(self.comboBoxModulationType.sizePolicy().hasHeightForWidth())
        self.comboBoxModulationType.setSizePolicy(sizePolicy1)
        self.comboBoxModulationType.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_3.addWidget(self.comboBoxModulationType, 0, 0, 1, 2)

        self.labelParameters = QLabel(self.scrollAreaWidgetContents_4)
        self.labelParameters.setObjectName(u"labelParameters")

        self.gridLayout_3.addWidget(self.labelParameters, 2, 0, 1, 1)

        self.scrollArea_4.setWidget(self.scrollAreaWidgetContents_4)

        self.gridLayout_7.addWidget(self.scrollArea_4, 5, 0, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_4, 4, 3, 1, 1)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_6, 8, 3, 1, 1)

        self.lEqual_qm = QLabel(self.scrollAreaWidgetContents_2)
        self.lEqual_qm.setObjectName(u"lEqual_qm")
        sizePolicy.setHeightForWidth(self.lEqual_qm.sizePolicy().hasHeightForWidth())
        self.lEqual_qm.setSizePolicy(sizePolicy)
        self.lEqual_qm.setMaximumSize(QSize(32, 32))
        self.lEqual_qm.setPixmap(QPixmap(u":/icons/icons/equals_qm.svg"))
        self.lEqual_qm.setScaledContents(True)
        self.lEqual_qm.setAlignment(Qt.AlignCenter)

        self.gridLayout_7.addWidget(self.lEqual_qm, 8, 2, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.lSamplesInViewOrigSignalText = QLabel(self.scrollAreaWidgetContents_2)
        self.lSamplesInViewOrigSignalText.setObjectName(u"lSamplesInViewOrigSignalText")
        sizePolicy4.setHeightForWidth(self.lSamplesInViewOrigSignalText.sizePolicy().hasHeightForWidth())
        self.lSamplesInViewOrigSignalText.setSizePolicy(sizePolicy4)

        self.horizontalLayout_2.addWidget(self.lSamplesInViewOrigSignalText)

        self.lSamplesInViewOrigSignal = QLabel(self.scrollAreaWidgetContents_2)
        self.lSamplesInViewOrigSignal.setObjectName(u"lSamplesInViewOrigSignal")
        sizePolicy1.setHeightForWidth(self.lSamplesInViewOrigSignal.sizePolicy().hasHeightForWidth())
        self.lSamplesInViewOrigSignal.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.lSamplesInViewOrigSignal)

        self.label_10 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_10.setObjectName(u"label_10")

        self.horizontalLayout_2.addWidget(self.label_10)

        self.lOriginalSignalSamplesSelected = QLabel(self.scrollAreaWidgetContents_2)
        self.lOriginalSignalSamplesSelected.setObjectName(u"lOriginalSignalSamplesSelected")

        self.horizontalLayout_2.addWidget(self.lOriginalSignalSamplesSelected)


        self.gridLayout_7.addLayout(self.horizontalLayout_2, 10, 1, 1, 1)

        self.gridLayout_7.setRowStretch(1, 1)
        self.gridLayout_7.setRowStretch(3, 1)
        self.gridLayout_7.setRowStretch(5, 1)
        self.gridLayout_7.setRowStretch(8, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout.addWidget(self.scrollArea)

        QWidget.setTabOrder(self.btnAddModulation, self.scrollArea_2)
        QWidget.setTabOrder(self.scrollArea_2, self.doubleSpinBoxCarrierFreq)
        QWidget.setTabOrder(self.doubleSpinBoxCarrierFreq, self.doubleSpinBoxCarrierPhase)
        QWidget.setTabOrder(self.doubleSpinBoxCarrierPhase, self.btnAutoDetect)
        QWidget.setTabOrder(self.btnAutoDetect, self.scrollArea_3)
        QWidget.setTabOrder(self.scrollArea_3, self.linEdDataBits)
        QWidget.setTabOrder(self.linEdDataBits, self.spinBoxSamplesPerSymbol)
        QWidget.setTabOrder(self.spinBoxSamplesPerSymbol, self.spinBoxSampleRate)
        QWidget.setTabOrder(self.spinBoxSampleRate, self.scrollArea_4)
        QWidget.setTabOrder(self.scrollArea_4, self.comboBoxModulationType)
        QWidget.setTabOrder(self.comboBoxModulationType, self.spinBoxBitsPerSymbol)
        QWidget.setTabOrder(self.spinBoxBitsPerSymbol, self.lineEditParameters)
        QWidget.setTabOrder(self.lineEditParameters, self.spinBoxGaussBT)
        QWidget.setTabOrder(self.spinBoxGaussBT, self.spinBoxGaussFilterWidth)
        QWidget.setTabOrder(self.spinBoxGaussFilterWidth, self.scrollArea_5)
        QWidget.setTabOrder(self.scrollArea_5, self.treeViewSignals)
        QWidget.setTabOrder(self.treeViewSignals, self.chkBoxLockSIV)
        QWidget.setTabOrder(self.chkBoxLockSIV, self.gVCarrier)
        QWidget.setTabOrder(self.gVCarrier, self.gVData)
        QWidget.setTabOrder(self.gVData, self.gVModulated)
        QWidget.setTabOrder(self.gVModulated, self.gVOriginalSignal)
        QWidget.setTabOrder(self.gVOriginalSignal, self.cbShowDataBitsOnly)
        QWidget.setTabOrder(self.cbShowDataBitsOnly, self.btnSearchPrev)
        QWidget.setTabOrder(self.btnSearchPrev, self.btnSearchNext)
        QWidget.setTabOrder(self.btnSearchNext, self.btnRemoveModulation)
        QWidget.setTabOrder(self.btnRemoveModulation, self.comboBoxCustomModulations)
        QWidget.setTabOrder(self.comboBoxCustomModulations, self.scrollArea)

        self.retranslateUi(DialogModulation)
    # setupUi

    def retranslateUi(self, DialogModulation):
        DialogModulation.setWindowTitle(QCoreApplication.translate("DialogModulation", u"Modulation", None))
        self.comboBoxCustomModulations.setItemText(0, QCoreApplication.translate("DialogModulation", u"My Modulation", None))

        self.btnAddModulation.setText(QCoreApplication.translate("DialogModulation", u"...", None))
        self.btnRemoveModulation.setText(QCoreApplication.translate("DialogModulation", u"...", None))
        self.label_5.setText(QCoreApplication.translate("DialogModulation", u"Data (raw bits)", None))
        self.lEqual.setText("")
        self.label_6.setText(QCoreApplication.translate("DialogModulation", u"Modulation", None))
        self.label_7.setText(QCoreApplication.translate("DialogModulation", u"Original Signal (drag&drop)", None))
        self.label_4.setText(QCoreApplication.translate("DialogModulation", u"Carrier", None))
        self.lCurrentSearchResult.setText(QCoreApplication.translate("DialogModulation", u"-", None))
        self.cbShowDataBitsOnly.setText(QCoreApplication.translate("DialogModulation", u"Show Only Data Sequence\n"
"(10)", None))
        self.btnSearchPrev.setText("")
        self.lTotalSearchresults.setText(QCoreApplication.translate("DialogModulation", u"-", None))
        self.lSlash.setText(QCoreApplication.translate("DialogModulation", u"/", None))
        self.btnSearchNext.setText("")
        self.chkBoxLockSIV.setText(QCoreApplication.translate("DialogModulation", u"Lock view to original signal", None))
        self.lSamplesInViewModulatedText.setText(QCoreApplication.translate("DialogModulation", u"Samples in View:", None))
#if QT_CONFIG(tooltip)
        self.lSamplesInViewModulated.setToolTip(QCoreApplication.translate("DialogModulation", u"<html><head/><body><p>Shown Samples in View:</p><p><span style=\" font-weight:600; color:#ff0000;\">Red</span> - if samples in view differ from original signal</p><p><span style=\" font-weight:600;\">Normal</span> - if samples in view are equal to the original signal</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lSamplesInViewModulated.setText(QCoreApplication.translate("DialogModulation", u"101010121", None))
        self.label_9.setText(QCoreApplication.translate("DialogModulation", u"Samples selected:", None))
        self.lModulatedSelectedSamples.setText(QCoreApplication.translate("DialogModulation", u"0", None))
        self.label_3.setText(QCoreApplication.translate("DialogModulation", u"Sample Rate (Sps):", None))
        self.label.setText(QCoreApplication.translate("DialogModulation", u"Samples per Symbol:", None))
        self.linEdDataBits.setPlaceholderText(QCoreApplication.translate("DialogModulation", u"Enter Data Bits here", None))
        self.lCarrierFreq.setText(QCoreApplication.translate("DialogModulation", u"Frequency:", None))
        self.doubleSpinBoxCarrierFreq.setSuffix("")
        self.label_2.setText(QCoreApplication.translate("DialogModulation", u"Phase:", None))
        self.doubleSpinBoxCarrierPhase.setSuffix(QCoreApplication.translate("DialogModulation", u"\u00b0", None))
#if QT_CONFIG(tooltip)
        self.btnAutoDetect.setToolTip(QCoreApplication.translate("DialogModulation", u"<html><head/><body><p>Auto detect the frequency based on the original signal. You have to select a signal (<span style=\" font-weight:600;\">bottom of this window</span>) to use this feature.</p><p><br/></p><p>Select a signal by dragging it from the tree and dropping it on the graphics pane to the right.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnAutoDetect.setText(QCoreApplication.translate("DialogModulation", u"Auto detect from original signal", None))
        self.lPlus.setText("")
        self.lGaussWidth.setText(QCoreApplication.translate("DialogModulation", u"Gauss filter width:", None))
        self.lGaussBT.setText(QCoreApplication.translate("DialogModulation", u"Gauss BT:", None))
        self.labelBitsPerSymbol.setText(QCoreApplication.translate("DialogModulation", u"Bits per Symbol:", None))
        self.comboBoxModulationType.setItemText(0, QCoreApplication.translate("DialogModulation", u"Amplitude Shift Keying (ASK)", None))
        self.comboBoxModulationType.setItemText(1, QCoreApplication.translate("DialogModulation", u"Frequency Shift Keying (FSK)", None))
        self.comboBoxModulationType.setItemText(2, QCoreApplication.translate("DialogModulation", u"Gaussian Frequency Shift Keying (GFSK)", None))
        self.comboBoxModulationType.setItemText(3, QCoreApplication.translate("DialogModulation", u"Phase Shift Keying (PSK)", None))

        self.labelParameters.setText(QCoreApplication.translate("DialogModulation", u"Parameters:", None))
        self.lEqual_qm.setText("")
        self.lSamplesInViewOrigSignalText.setText(QCoreApplication.translate("DialogModulation", u"Samples in View:", None))
#if QT_CONFIG(tooltip)
        self.lSamplesInViewOrigSignal.setToolTip(QCoreApplication.translate("DialogModulation", u"<html><head/><body><p>Shown Samples in View:</p><p><span style=\" font-weight:600; color:#ff0000;\">Red</span> - if samples in view differ from original signal</p><p><span style=\" font-weight:600;\">Normal</span> - if samples in view are equal to the original signal</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lSamplesInViewOrigSignal.setText(QCoreApplication.translate("DialogModulation", u"0", None))
        self.label_10.setText(QCoreApplication.translate("DialogModulation", u"Samples selected:", None))
        self.lOriginalSignalSamplesSelected.setText(QCoreApplication.translate("DialogModulation", u"0", None))
    # retranslateUi

