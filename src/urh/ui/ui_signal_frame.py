# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'signal_frame.ui'
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

from urh.ui.views.EpicGraphicView import EpicGraphicView
from urh.ui.views.TextEditProtocolView import TextEditProtocolView
from urh.ui.views.SpectrogramGraphicView import SpectrogramGraphicView

import urh.ui.urh_rc

class Ui_SignalFrame(object):
    def setupUi(self, SignalFrame):
        if SignalFrame.objectName():
            SignalFrame.setObjectName(u"SignalFrame")
        SignalFrame.resize(1057, 652)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SignalFrame.sizePolicy().hasHeightForWidth())
        SignalFrame.setSizePolicy(sizePolicy)
        SignalFrame.setMinimumSize(QSize(0, 0))
        SignalFrame.setMaximumSize(QSize(16777215, 16777215))
        SignalFrame.setSizeIncrement(QSize(0, 0))
        SignalFrame.setBaseSize(QSize(0, 0))
        SignalFrame.setMouseTracking(False)
        SignalFrame.setAcceptDrops(True)
        SignalFrame.setAutoFillBackground(False)
        SignalFrame.setStyleSheet(u"")
        SignalFrame.setFrameShape(QFrame.NoFrame)
        SignalFrame.setFrameShadow(QFrame.Raised)
        SignalFrame.setLineWidth(1)
        self.horizontalLayout = QHBoxLayout(SignalFrame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setSizeConstraint(QLayout.SetFixedSize)
        self.lSignalViewText = QLabel(SignalFrame)
        self.lSignalViewText.setObjectName(u"lSignalViewText")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lSignalViewText.sizePolicy().hasHeightForWidth())
        self.lSignalViewText.setSizePolicy(sizePolicy1)
        font = QFont()
        font.setUnderline(False)
        self.lSignalViewText.setFont(font)

        self.gridLayout_2.addWidget(self.lSignalViewText, 17, 0, 1, 1)

        self.spinBoxBitsPerSymbol = QSpinBox(SignalFrame)
        self.spinBoxBitsPerSymbol.setObjectName(u"spinBoxBitsPerSymbol")
        self.spinBoxBitsPerSymbol.setMinimum(1)
        self.spinBoxBitsPerSymbol.setMaximum(10)

        self.gridLayout_2.addWidget(self.spinBoxBitsPerSymbol, 11, 1, 1, 1)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.btnSaveSignal = QToolButton(SignalFrame)
        self.btnSaveSignal.setObjectName(u"btnSaveSignal")
        self.btnSaveSignal.setMinimumSize(QSize(24, 24))
        self.btnSaveSignal.setMaximumSize(QSize(24, 24))
        icon = QIcon()
        iconThemeName = u"document-save"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnSaveSignal.setIcon(icon)

        self.gridLayout.addWidget(self.btnSaveSignal, 0, 3, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_4, 0, 2, 1, 1)

        self.btnCloseSignal = QToolButton(SignalFrame)
        self.btnCloseSignal.setObjectName(u"btnCloseSignal")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.btnCloseSignal.sizePolicy().hasHeightForWidth())
        self.btnCloseSignal.setSizePolicy(sizePolicy2)
        self.btnCloseSignal.setMinimumSize(QSize(24, 24))
        self.btnCloseSignal.setMaximumSize(QSize(24, 24))
        self.btnCloseSignal.setStyleSheet(u"color:red;")
        icon1 = QIcon()
        iconThemeName = u"window-close"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnCloseSignal.setIcon(icon1)

        self.gridLayout.addWidget(self.btnCloseSignal, 0, 9, 1, 1)

        self.lSignalTyp = QLabel(SignalFrame)
        self.lSignalTyp.setObjectName(u"lSignalTyp")
        sizePolicy3 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lSignalTyp.sizePolicy().hasHeightForWidth())
        self.lSignalTyp.setSizePolicy(sizePolicy3)

        self.gridLayout.addWidget(self.lSignalTyp, 0, 1, 1, 1)

        self.lSignalNr = QLabel(SignalFrame)
        self.lSignalNr.setObjectName(u"lSignalNr")
        sizePolicy4 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.lSignalNr.sizePolicy().hasHeightForWidth())
        self.lSignalNr.setSizePolicy(sizePolicy4)
        self.lSignalNr.setWordWrap(False)
        self.lSignalNr.setMargin(0)
        self.lSignalNr.setIndent(-1)

        self.gridLayout.addWidget(self.lSignalNr, 0, 0, 1, 1)

        self.btnInfo = QToolButton(SignalFrame)
        self.btnInfo.setObjectName(u"btnInfo")
        self.btnInfo.setMinimumSize(QSize(24, 24))
        self.btnInfo.setMaximumSize(QSize(24, 24))
        icon2 = QIcon()
        iconThemeName = u"dialog-information"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnInfo.setIcon(icon2)

        self.gridLayout.addWidget(self.btnInfo, 0, 6, 1, 1)

        self.btnReplay = QToolButton(SignalFrame)
        self.btnReplay.setObjectName(u"btnReplay")
        self.btnReplay.setMinimumSize(QSize(24, 24))
        self.btnReplay.setMaximumSize(QSize(24, 24))
        icon3 = QIcon()
        iconThemeName = u"media-playback-start"
        if QIcon.hasThemeIcon(iconThemeName):
            icon3 = QIcon.fromTheme(iconThemeName)
        else:
            icon3.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnReplay.setIcon(icon3)

        self.gridLayout.addWidget(self.btnReplay, 0, 5, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 2)

        self.cbProtoView = QComboBox(SignalFrame)
        self.cbProtoView.addItem("")
        self.cbProtoView.addItem("")
        self.cbProtoView.addItem("")
        self.cbProtoView.setObjectName(u"cbProtoView")

        self.gridLayout_2.addWidget(self.cbProtoView, 23, 1, 1, 1)

        self.lCenterSpacing = QLabel(SignalFrame)
        self.lCenterSpacing.setObjectName(u"lCenterSpacing")

        self.gridLayout_2.addWidget(self.lCenterSpacing, 4, 0, 1, 1)

        self.spinBoxTolerance = QSpinBox(SignalFrame)
        self.spinBoxTolerance.setObjectName(u"spinBoxTolerance")
        self.spinBoxTolerance.setMinimumSize(QSize(100, 0))
        self.spinBoxTolerance.setMaximumSize(QSize(16777215, 16777215))
        self.spinBoxTolerance.setMaximum(9999)

        self.gridLayout_2.addWidget(self.spinBoxTolerance, 8, 1, 1, 1)

        self.lSamplesPerSymbol = QLabel(SignalFrame)
        self.lSamplesPerSymbol.setObjectName(u"lSamplesPerSymbol")
        sizePolicy1.setHeightForWidth(self.lSamplesPerSymbol.sizePolicy().hasHeightForWidth())
        self.lSamplesPerSymbol.setSizePolicy(sizePolicy1)
        self.lSamplesPerSymbol.setTextInteractionFlags(Qt.LinksAccessibleByMouse)

        self.gridLayout_2.addWidget(self.lSamplesPerSymbol, 5, 0, 1, 1)

        self.lErrorTolerance = QLabel(SignalFrame)
        self.lErrorTolerance.setObjectName(u"lErrorTolerance")
        sizePolicy1.setHeightForWidth(self.lErrorTolerance.sizePolicy().hasHeightForWidth())
        self.lErrorTolerance.setSizePolicy(sizePolicy1)
        self.lErrorTolerance.setMinimumSize(QSize(0, 0))
        self.lErrorTolerance.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_2.addWidget(self.lErrorTolerance, 8, 0, 1, 1)

        self.lCenterOffset = QLabel(SignalFrame)
        self.lCenterOffset.setObjectName(u"lCenterOffset")
        sizePolicy1.setHeightForWidth(self.lCenterOffset.sizePolicy().hasHeightForWidth())
        self.lCenterOffset.setSizePolicy(sizePolicy1)
        self.lCenterOffset.setMinimumSize(QSize(0, 0))
        self.lCenterOffset.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_2.addWidget(self.lCenterOffset, 3, 0, 1, 1)

        self.labelModulation = QLabel(SignalFrame)
        self.labelModulation.setObjectName(u"labelModulation")

        self.gridLayout_2.addWidget(self.labelModulation, 10, 0, 1, 1)

        self.cbSignalView = QComboBox(SignalFrame)
        self.cbSignalView.addItem("")
        self.cbSignalView.addItem("")
        self.cbSignalView.addItem("")
        self.cbSignalView.setObjectName(u"cbSignalView")
        sizePolicy5 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.cbSignalView.sizePolicy().hasHeightForWidth())
        self.cbSignalView.setSizePolicy(sizePolicy5)

        self.gridLayout_2.addWidget(self.cbSignalView, 17, 1, 1, 1)

        self.spinBoxNoiseTreshold = QDoubleSpinBox(SignalFrame)
        self.spinBoxNoiseTreshold.setObjectName(u"spinBoxNoiseTreshold")
        self.spinBoxNoiseTreshold.setDecimals(4)
        self.spinBoxNoiseTreshold.setMaximum(1.000000000000000)
        self.spinBoxNoiseTreshold.setSingleStep(0.000100000000000)

        self.gridLayout_2.addWidget(self.spinBoxNoiseTreshold, 2, 1, 1, 1)

        self.spinBoxCenterSpacing = QDoubleSpinBox(SignalFrame)
        self.spinBoxCenterSpacing.setObjectName(u"spinBoxCenterSpacing")
        self.spinBoxCenterSpacing.setDecimals(4)
        self.spinBoxCenterSpacing.setMinimum(0.000100000000000)
        self.spinBoxCenterSpacing.setMaximum(5.000000000000000)
        self.spinBoxCenterSpacing.setSingleStep(0.000100000000000)
        self.spinBoxCenterSpacing.setValue(1.000000000000000)

        self.gridLayout_2.addWidget(self.spinBoxCenterSpacing, 4, 1, 1, 1)

        self.lineEditSignalName = QLineEdit(SignalFrame)
        self.lineEditSignalName.setObjectName(u"lineEditSignalName")
        sizePolicy6 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.lineEditSignalName.sizePolicy().hasHeightForWidth())
        self.lineEditSignalName.setSizePolicy(sizePolicy6)
        self.lineEditSignalName.setMinimumSize(QSize(214, 0))
        self.lineEditSignalName.setMaximumSize(QSize(16777215, 16777215))
        self.lineEditSignalName.setAcceptDrops(False)

        self.gridLayout_2.addWidget(self.lineEditSignalName, 1, 0, 1, 2)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setSpacing(7)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.cbModulationType = QComboBox(SignalFrame)
        self.cbModulationType.addItem("")
        self.cbModulationType.addItem("")
        self.cbModulationType.addItem("")
        self.cbModulationType.setObjectName(u"cbModulationType")

        self.horizontalLayout_5.addWidget(self.cbModulationType)

        self.btnAdvancedModulationSettings = QToolButton(SignalFrame)
        self.btnAdvancedModulationSettings.setObjectName(u"btnAdvancedModulationSettings")
        icon4 = QIcon()
        iconThemeName = u"configure"
        if QIcon.hasThemeIcon(iconThemeName):
            icon4 = QIcon.fromTheme(iconThemeName)
        else:
            icon4.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnAdvancedModulationSettings.setIcon(icon4)
        self.btnAdvancedModulationSettings.setIconSize(QSize(16, 16))

        self.horizontalLayout_5.addWidget(self.btnAdvancedModulationSettings)


        self.gridLayout_2.addLayout(self.horizontalLayout_5, 10, 1, 1, 1)

        self.chkBoxSyncSelection = QCheckBox(SignalFrame)
        self.chkBoxSyncSelection.setObjectName(u"chkBoxSyncSelection")
        self.chkBoxSyncSelection.setChecked(True)

        self.gridLayout_2.addWidget(self.chkBoxSyncSelection, 24, 0, 1, 1)

        self.labelSpectrogramMin = QLabel(SignalFrame)
        self.labelSpectrogramMin.setObjectName(u"labelSpectrogramMin")

        self.gridLayout_2.addWidget(self.labelSpectrogramMin, 21, 0, 1, 1)

        self.labelSpectrogramMax = QLabel(SignalFrame)
        self.labelSpectrogramMax.setObjectName(u"labelSpectrogramMax")

        self.gridLayout_2.addWidget(self.labelSpectrogramMax, 22, 0, 1, 1)

        self.chkBoxShowProtocol = QCheckBox(SignalFrame)
        self.chkBoxShowProtocol.setObjectName(u"chkBoxShowProtocol")

        self.gridLayout_2.addWidget(self.chkBoxShowProtocol, 23, 0, 1, 1)

        self.spinBoxSamplesPerSymbol = QSpinBox(SignalFrame)
        self.spinBoxSamplesPerSymbol.setObjectName(u"spinBoxSamplesPerSymbol")
        self.spinBoxSamplesPerSymbol.setMinimumSize(QSize(100, 0))
        self.spinBoxSamplesPerSymbol.setMinimum(1)
        self.spinBoxSamplesPerSymbol.setMaximum(999999999)

        self.gridLayout_2.addWidget(self.spinBoxSamplesPerSymbol, 5, 1, 1, 1)

        self.btnAutoDetect = QToolButton(SignalFrame)
        self.btnAutoDetect.setObjectName(u"btnAutoDetect")
        sizePolicy6.setHeightForWidth(self.btnAutoDetect.sizePolicy().hasHeightForWidth())
        self.btnAutoDetect.setSizePolicy(sizePolicy6)
        self.btnAutoDetect.setIconSize(QSize(16, 16))
        self.btnAutoDetect.setCheckable(False)
        self.btnAutoDetect.setChecked(False)
        self.btnAutoDetect.setPopupMode(QToolButton.MenuButtonPopup)
        self.btnAutoDetect.setArrowType(Qt.NoArrow)

        self.gridLayout_2.addWidget(self.btnAutoDetect, 13, 0, 1, 2)

        self.line = QFrame(SignalFrame)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.line, 15, 0, 1, 2)

        self.sliderSpectrogramMin = QSlider(SignalFrame)
        self.sliderSpectrogramMin.setObjectName(u"sliderSpectrogramMin")
        sizePolicy6.setHeightForWidth(self.sliderSpectrogramMin.sizePolicy().hasHeightForWidth())
        self.sliderSpectrogramMin.setSizePolicy(sizePolicy6)
        self.sliderSpectrogramMin.setMinimum(-150)
        self.sliderSpectrogramMin.setMaximum(10)
        self.sliderSpectrogramMin.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.sliderSpectrogramMin, 21, 1, 1, 1)

        self.labelFFTWindowSize = QLabel(SignalFrame)
        self.labelFFTWindowSize.setObjectName(u"labelFFTWindowSize")

        self.gridLayout_2.addWidget(self.labelFFTWindowSize, 20, 0, 1, 1)

        self.sliderSpectrogramMax = QSlider(SignalFrame)
        self.sliderSpectrogramMax.setObjectName(u"sliderSpectrogramMax")
        sizePolicy6.setHeightForWidth(self.sliderSpectrogramMax.sizePolicy().hasHeightForWidth())
        self.sliderSpectrogramMax.setSizePolicy(sizePolicy6)
        self.sliderSpectrogramMax.setMinimum(-150)
        self.sliderSpectrogramMax.setMaximum(10)
        self.sliderSpectrogramMax.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.sliderSpectrogramMax, 22, 1, 1, 1)

        self.spinBoxCenterOffset = QDoubleSpinBox(SignalFrame)
        self.spinBoxCenterOffset.setObjectName(u"spinBoxCenterOffset")
        self.spinBoxCenterOffset.setMinimumSize(QSize(100, 0))
        self.spinBoxCenterOffset.setMaximumSize(QSize(16777215, 16777215))
        self.spinBoxCenterOffset.setDecimals(4)
        self.spinBoxCenterOffset.setMinimum(-3.150000000000000)
        self.spinBoxCenterOffset.setMaximum(6.280000000000000)
        self.spinBoxCenterOffset.setSingleStep(0.000100000000000)

        self.gridLayout_2.addWidget(self.spinBoxCenterOffset, 3, 1, 1, 1)

        self.labelNoise = QLabel(SignalFrame)
        self.labelNoise.setObjectName(u"labelNoise")

        self.gridLayout_2.addWidget(self.labelNoise, 2, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_2, 14, 0, 1, 1)

        self.sliderFFTWindowSize = QSlider(SignalFrame)
        self.sliderFFTWindowSize.setObjectName(u"sliderFFTWindowSize")
        sizePolicy6.setHeightForWidth(self.sliderFFTWindowSize.sizePolicy().hasHeightForWidth())
        self.sliderFFTWindowSize.setSizePolicy(sizePolicy6)
        self.sliderFFTWindowSize.setMinimum(6)
        self.sliderFFTWindowSize.setMaximum(15)
        self.sliderFFTWindowSize.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.sliderFFTWindowSize, 20, 1, 1, 1)

        self.lBitsPerSymbol = QLabel(SignalFrame)
        self.lBitsPerSymbol.setObjectName(u"lBitsPerSymbol")

        self.gridLayout_2.addWidget(self.lBitsPerSymbol, 11, 0, 1, 1)


        self.horizontalLayout.addLayout(self.gridLayout_2)

        self.splitter = QSplitter(SignalFrame)
        self.splitter.setObjectName(u"splitter")
        sizePolicy7 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy7)
        self.splitter.setStyleSheet(u"QSplitter::handle:vertical {\n"
"margin: 4px 0px;\n"
"    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, \n"
"stop:0 rgba(255, 255, 255, 0), \n"
"stop:0.5 rgba(100, 100, 100, 100), \n"
"stop:1 rgba(255, 255, 255, 0));\n"
"	image: url(:/icons/icons/splitter_handle_horizontal.svg);\n"
"}")
        self.splitter.setFrameShape(QFrame.NoFrame)
        self.splitter.setLineWidth(1)
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setHandleWidth(6)
        self.splitter.setChildrenCollapsible(False)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.stackedWidget = QStackedWidget(self.layoutWidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setLineWidth(0)
        self.pageSignal = QWidget()
        self.pageSignal.setObjectName(u"pageSignal")
        self.horizontalLayout_6 = QHBoxLayout(self.pageSignal)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.gvSignal = EpicGraphicView(self.pageSignal)
        self.gvSignal.setObjectName(u"gvSignal")
        self.gvSignal.setEnabled(True)
        sizePolicy7.setHeightForWidth(self.gvSignal.sizePolicy().hasHeightForWidth())
        self.gvSignal.setSizePolicy(sizePolicy7)
        self.gvSignal.setMinimumSize(QSize(0, 150))
        self.gvSignal.setMaximumSize(QSize(16777215, 16777215))
        self.gvSignal.setMouseTracking(True)
        self.gvSignal.setFocusPolicy(Qt.WheelFocus)
        self.gvSignal.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.gvSignal.setAutoFillBackground(False)
        self.gvSignal.setStyleSheet(u"")
        self.gvSignal.setFrameShape(QFrame.NoFrame)
        self.gvSignal.setFrameShadow(QFrame.Raised)
        self.gvSignal.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.gvSignal.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.gvSignal.setInteractive(False)
        self.gvSignal.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
        self.gvSignal.setDragMode(QGraphicsView.NoDrag)
        self.gvSignal.setCacheMode(QGraphicsView.CacheNone)
        self.gvSignal.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.gvSignal.setResizeAnchor(QGraphicsView.NoAnchor)
        self.gvSignal.setViewportUpdateMode(QGraphicsView.MinimalViewportUpdate)
        self.gvSignal.setRubberBandSelectionMode(Qt.ContainsItemShape)
        self.gvSignal.setOptimizationFlags(QGraphicsView.DontClipPainter|QGraphicsView.DontSavePainterState)

        self.horizontalLayout_6.addWidget(self.gvSignal)

        self.stackedWidget.addWidget(self.pageSignal)
        self.pageSpectrogram = QWidget()
        self.pageSpectrogram.setObjectName(u"pageSpectrogram")
        self.horizontalLayout_4 = QHBoxLayout(self.pageSpectrogram)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gvSpectrogram = SpectrogramGraphicView(self.pageSpectrogram)
        self.gvSpectrogram.setObjectName(u"gvSpectrogram")
        self.gvSpectrogram.setMouseTracking(True)
        self.gvSpectrogram.setFrameShape(QFrame.NoFrame)
        self.gvSpectrogram.setInteractive(False)
        self.gvSpectrogram.setRenderHints(QPainter.TextAntialiasing)
        self.gvSpectrogram.setCacheMode(QGraphicsView.CacheNone)
        self.gvSpectrogram.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.gvSpectrogram.setViewportUpdateMode(QGraphicsView.MinimalViewportUpdate)
        self.gvSpectrogram.setOptimizationFlags(QGraphicsView.DontClipPainter|QGraphicsView.DontSavePainterState)

        self.horizontalLayout_4.addWidget(self.gvSpectrogram)

        self.stackedWidget.addWidget(self.pageSpectrogram)
        self.pageLoading = QWidget()
        self.pageLoading.setObjectName(u"pageLoading")
        self.verticalLayout_2 = QVBoxLayout(self.pageLoading)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.labelLoadingAutoInterpretation = QLabel(self.pageLoading)
        self.labelLoadingAutoInterpretation.setObjectName(u"labelLoadingAutoInterpretation")
        font1 = QFont()
        font1.setPointSize(12)
        self.labelLoadingAutoInterpretation.setFont(font1)
        self.labelLoadingAutoInterpretation.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.labelLoadingAutoInterpretation)

        self.stackedWidget.addWidget(self.pageLoading)

        self.horizontalLayout_2.addWidget(self.stackedWidget)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.lYScale = QLabel(self.layoutWidget)
        self.lYScale.setObjectName(u"lYScale")

        self.verticalLayout_5.addWidget(self.lYScale)

        self.sliderYScale = QSlider(self.layoutWidget)
        self.sliderYScale.setObjectName(u"sliderYScale")
        self.sliderYScale.setMinimum(1)
        self.sliderYScale.setMaximum(100)
        self.sliderYScale.setOrientation(Qt.Vertical)
        self.sliderYScale.setTickPosition(QSlider.TicksBelow)

        self.verticalLayout_5.addWidget(self.sliderYScale)


        self.horizontalLayout_2.addLayout(self.verticalLayout_5)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.btnShowHideStartEnd = QToolButton(self.layoutWidget)
        self.btnShowHideStartEnd.setObjectName(u"btnShowHideStartEnd")
        sizePolicy1.setHeightForWidth(self.btnShowHideStartEnd.sizePolicy().hasHeightForWidth())
        self.btnShowHideStartEnd.setSizePolicy(sizePolicy1)
        self.btnShowHideStartEnd.setAutoFillBackground(False)
        self.btnShowHideStartEnd.setStyleSheet(u"")
        icon5 = QIcon()
        iconThemeName = u"arrow-down-double"
        if QIcon.hasThemeIcon(iconThemeName):
            icon5 = QIcon.fromTheme(iconThemeName)
        else:
            icon5.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnShowHideStartEnd.setIcon(icon5)
        self.btnShowHideStartEnd.setCheckable(True)

        self.horizontalLayout_3.addWidget(self.btnShowHideStartEnd)

        self.lNumSelectedSamples = QLabel(self.layoutWidget)
        self.lNumSelectedSamples.setObjectName(u"lNumSelectedSamples")

        self.horizontalLayout_3.addWidget(self.lNumSelectedSamples)

        self.lTextSelectedSamples = QLabel(self.layoutWidget)
        self.lTextSelectedSamples.setObjectName(u"lTextSelectedSamples")

        self.horizontalLayout_3.addWidget(self.lTextSelectedSamples)

        self.line_3 = QFrame(self.layoutWidget)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.VLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_3.addWidget(self.line_3)

        self.lDuration = QLabel(self.layoutWidget)
        self.lDuration.setObjectName(u"lDuration")

        self.horizontalLayout_3.addWidget(self.lDuration)

        self.line_2 = QFrame(self.layoutWidget)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_3.addWidget(self.line_2)

        self.labelRSSI = QLabel(self.layoutWidget)
        self.labelRSSI.setObjectName(u"labelRSSI")

        self.horizontalLayout_3.addWidget(self.labelRSSI)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.btnFilter = QToolButton(self.layoutWidget)
        self.btnFilter.setObjectName(u"btnFilter")
        icon6 = QIcon()
        iconThemeName = u"view-filter"
        if QIcon.hasThemeIcon(iconThemeName):
            icon6 = QIcon.fromTheme(iconThemeName)
        else:
            icon6.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnFilter.setIcon(icon6)
        self.btnFilter.setPopupMode(QToolButton.MenuButtonPopup)
        self.btnFilter.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.btnFilter.setArrowType(Qt.NoArrow)

        self.horizontalLayout_3.addWidget(self.btnFilter)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.additionalInfos = QHBoxLayout()
        self.additionalInfos.setSpacing(6)
        self.additionalInfos.setObjectName(u"additionalInfos")
        self.lStart = QLabel(self.layoutWidget)
        self.lStart.setObjectName(u"lStart")

        self.additionalInfos.addWidget(self.lStart)

        self.spinBoxSelectionStart = QSpinBox(self.layoutWidget)
        self.spinBoxSelectionStart.setObjectName(u"spinBoxSelectionStart")
        self.spinBoxSelectionStart.setReadOnly(False)
        self.spinBoxSelectionStart.setMaximum(99999999)

        self.additionalInfos.addWidget(self.spinBoxSelectionStart)

        self.lEnd = QLabel(self.layoutWidget)
        self.lEnd.setObjectName(u"lEnd")

        self.additionalInfos.addWidget(self.lEnd)

        self.spinBoxSelectionEnd = QSpinBox(self.layoutWidget)
        self.spinBoxSelectionEnd.setObjectName(u"spinBoxSelectionEnd")
        self.spinBoxSelectionEnd.setMaximum(99999999)

        self.additionalInfos.addWidget(self.spinBoxSelectionEnd)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.additionalInfos.addItem(self.horizontalSpacer)

        self.lZoomText = QLabel(self.layoutWidget)
        self.lZoomText.setObjectName(u"lZoomText")
        sizePolicy8 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.lZoomText.sizePolicy().hasHeightForWidth())
        self.lZoomText.setSizePolicy(sizePolicy8)
        self.lZoomText.setMinimumSize(QSize(0, 0))
        self.lZoomText.setMaximumSize(QSize(16777215, 16777215))
        font2 = QFont()
        font2.setItalic(False)
        font2.setUnderline(False)
        self.lZoomText.setFont(font2)
        self.lZoomText.setTextFormat(Qt.PlainText)
        self.lZoomText.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.additionalInfos.addWidget(self.lZoomText)

        self.spinBoxXZoom = QSpinBox(self.layoutWidget)
        self.spinBoxXZoom.setObjectName(u"spinBoxXZoom")
        self.spinBoxXZoom.setMinimum(100)
        self.spinBoxXZoom.setMaximum(999999999)

        self.additionalInfos.addWidget(self.spinBoxXZoom)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.additionalInfos.addItem(self.horizontalSpacer_2)

        self.lSamplesInView = QLabel(self.layoutWidget)
        self.lSamplesInView.setObjectName(u"lSamplesInView")

        self.additionalInfos.addWidget(self.lSamplesInView)

        self.lStrich = QLabel(self.layoutWidget)
        self.lStrich.setObjectName(u"lStrich")

        self.additionalInfos.addWidget(self.lStrich)

        self.lSamplesTotal = QLabel(self.layoutWidget)
        self.lSamplesTotal.setObjectName(u"lSamplesTotal")

        self.additionalInfos.addWidget(self.lSamplesTotal)

        self.lSamplesViewText = QLabel(self.layoutWidget)
        self.lSamplesViewText.setObjectName(u"lSamplesViewText")

        self.additionalInfos.addWidget(self.lSamplesViewText)


        self.verticalLayout.addLayout(self.additionalInfos)

        self.splitter.addWidget(self.layoutWidget)
        self.txtEdProto = TextEditProtocolView(self.splitter)
        self.txtEdProto.setObjectName(u"txtEdProto")
        sizePolicy9 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(0)
        sizePolicy9.setHeightForWidth(self.txtEdProto.sizePolicy().hasHeightForWidth())
        self.txtEdProto.setSizePolicy(sizePolicy9)
        self.txtEdProto.setMinimumSize(QSize(0, 80))
        self.txtEdProto.setMaximumSize(QSize(16777215, 16777215))
        self.txtEdProto.setBaseSize(QSize(0, 0))
        self.txtEdProto.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.txtEdProto.setAcceptDrops(False)
        self.splitter.addWidget(self.txtEdProto)

        self.horizontalLayout.addWidget(self.splitter)

        QWidget.setTabOrder(self.btnSaveSignal, self.btnReplay)
        QWidget.setTabOrder(self.btnReplay, self.btnInfo)
        QWidget.setTabOrder(self.btnInfo, self.btnCloseSignal)
        QWidget.setTabOrder(self.btnCloseSignal, self.gvSignal)
        QWidget.setTabOrder(self.gvSignal, self.lineEditSignalName)
        QWidget.setTabOrder(self.lineEditSignalName, self.spinBoxNoiseTreshold)
        QWidget.setTabOrder(self.spinBoxNoiseTreshold, self.spinBoxCenterOffset)
        QWidget.setTabOrder(self.spinBoxCenterOffset, self.spinBoxCenterSpacing)
        QWidget.setTabOrder(self.spinBoxCenterSpacing, self.spinBoxSamplesPerSymbol)
        QWidget.setTabOrder(self.spinBoxSamplesPerSymbol, self.spinBoxTolerance)
        QWidget.setTabOrder(self.spinBoxTolerance, self.cbModulationType)
        QWidget.setTabOrder(self.cbModulationType, self.spinBoxBitsPerSymbol)
        QWidget.setTabOrder(self.spinBoxBitsPerSymbol, self.btnAdvancedModulationSettings)
        QWidget.setTabOrder(self.btnAdvancedModulationSettings, self.btnShowHideStartEnd)
        QWidget.setTabOrder(self.btnShowHideStartEnd, self.btnAutoDetect)
        QWidget.setTabOrder(self.btnAutoDetect, self.txtEdProto)
        QWidget.setTabOrder(self.txtEdProto, self.cbSignalView)
        QWidget.setTabOrder(self.cbSignalView, self.sliderFFTWindowSize)
        QWidget.setTabOrder(self.sliderFFTWindowSize, self.sliderSpectrogramMin)
        QWidget.setTabOrder(self.sliderSpectrogramMin, self.sliderSpectrogramMax)
        QWidget.setTabOrder(self.sliderSpectrogramMax, self.cbProtoView)
        QWidget.setTabOrder(self.cbProtoView, self.chkBoxShowProtocol)
        QWidget.setTabOrder(self.chkBoxShowProtocol, self.chkBoxSyncSelection)
        QWidget.setTabOrder(self.chkBoxSyncSelection, self.sliderYScale)
        QWidget.setTabOrder(self.sliderYScale, self.btnFilter)
        QWidget.setTabOrder(self.btnFilter, self.spinBoxSelectionStart)
        QWidget.setTabOrder(self.spinBoxSelectionStart, self.spinBoxSelectionEnd)
        QWidget.setTabOrder(self.spinBoxSelectionEnd, self.spinBoxXZoom)
        QWidget.setTabOrder(self.spinBoxXZoom, self.gvSpectrogram)

        self.retranslateUi(SignalFrame)

        self.stackedWidget.setCurrentIndex(0)

    # setupUi

    def retranslateUi(self, SignalFrame):
        SignalFrame.setWindowTitle(QCoreApplication.translate("SignalFrame", u"Frame", None))
        self.lSignalViewText.setText(QCoreApplication.translate("SignalFrame", u"Signal View:", None))
#if QT_CONFIG(tooltip)
        self.spinBoxBitsPerSymbol.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p><span style=\" font-weight:600;\">Higher order</span> modulations can carry <span style=\" font-weight:600;\">multiple</span> bits with <span style=\" font-weight:600;\">each</span> symbol. Configure <span style=\" font-weight:600;\">how many</span> bits are represented by a symbol. (Default = Binary modulation with one bit per symbol)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnSaveSignal.setText(QCoreApplication.translate("SignalFrame", u"...", None))
        self.btnCloseSignal.setText(QCoreApplication.translate("SignalFrame", u"X", None))
        self.lSignalTyp.setText(QCoreApplication.translate("SignalFrame", u"<Signaltyp>", None))
        self.lSignalNr.setText(QCoreApplication.translate("SignalFrame", u"1:", None))
        self.btnInfo.setText(QCoreApplication.translate("SignalFrame", u"...", None))
#if QT_CONFIG(tooltip)
        self.btnReplay.setToolTip(QCoreApplication.translate("SignalFrame", u"Replay signal", None))
#endif // QT_CONFIG(tooltip)
        self.btnReplay.setText("")
        self.cbProtoView.setItemText(0, QCoreApplication.translate("SignalFrame", u"Bits", None))
        self.cbProtoView.setItemText(1, QCoreApplication.translate("SignalFrame", u"Hex", None))
        self.cbProtoView.setItemText(2, QCoreApplication.translate("SignalFrame", u"ASCII", None))

#if QT_CONFIG(tooltip)
        self.lCenterSpacing.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>For <span style=\" font-weight:600;\">higher order</span> modulations (&gt; 1 Bits/Symbol), there are <span style=\" font-weight:600;\">multiple</span> centers. We assume that the <span style=\" font-weight:600;\">spacing</span> between all possible symbols is <span style=\" font-weight:600;\">constant</span>. Therefore you configure the spacing between centers.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lCenterSpacing.setText(QCoreApplication.translate("SignalFrame", u"Center Spacing:", None))
#if QT_CONFIG(tooltip)
        self.spinBoxTolerance.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>This is the error tolerance for determining the <span style=\" font-weight:600;\">pulse lengths</span> in the demodulated signal.</p><p><span style=\" font-weight:400; font-style:italic;\">Example:</span> Say, we are reading a ones pulse and the tolerance value was set to 5. Then 5 errors (which must follow sequentially) are accepted.</p><p>Tune this value if you have <span style=\" font-weight:600;\">spiky data</span> after demodulation.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.lSamplesPerSymbol.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>This is the length of one symbol <span style=\" font-weight:600;\">in samples</span>. For <span style=\" font-weight:600;\">binary modulations </span>(default) this is the <span style=\" font-weight:600;\">bit length</span>.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lSamplesPerSymbol.setText(QCoreApplication.translate("SignalFrame", u"Samples/Symbol:", None))
#if QT_CONFIG(tooltip)
        self.lErrorTolerance.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>This is the error tolerance for determining the <span style=\" font-weight:600;\">pulse lengths</span> in the demodulated signal.</p><p><span style=\" font-weight:400; font-style:italic;\">Example:</span> Say, we are reading a ones pulse and the tolerance value was set to 5. Then 5 errors (which must follow sequentially) are accepted.</p><p>Tune this value if you have <span style=\" font-weight:600;\">spiky data</span> after demodulation.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lErrorTolerance.setText(QCoreApplication.translate("SignalFrame", u"Error Tolerance:", None))
#if QT_CONFIG(tooltip)
        self.lCenterOffset.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>This is the threshold used for determining if a <span style=\" font-weight:600;\">bit is one or zero</span>. You can set it here or grab the middle of the area in <span style=\" font-style:italic;\">Quadrature Demod View.</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.lCenterOffset.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        self.lCenterOffset.setText(QCoreApplication.translate("SignalFrame", u"Center:", None))
#if QT_CONFIG(tooltip)
        self.labelModulation.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>Choose signals modulation:</p><ul><li>Amplitude Shift Keying (ASK)</li><li>Frequency Shift Keying (FSK)</li><li>Phase Shift Keying (PSK)</li></ul></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.labelModulation.setText(QCoreApplication.translate("SignalFrame", u"Modulation:", None))
        self.cbSignalView.setItemText(0, QCoreApplication.translate("SignalFrame", u"Analog", None))
        self.cbSignalView.setItemText(1, QCoreApplication.translate("SignalFrame", u"Demodulated", None))
        self.cbSignalView.setItemText(2, QCoreApplication.translate("SignalFrame", u"Spectrogram", None))

#if QT_CONFIG(tooltip)
        self.cbSignalView.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>Choose the view of your signal. Analog, Demodulated or Spectrogram.</p><p>The quadrature demodulation uses a <span style=\" font-weight:600;\">threshold of magnitudes,</span> to <span style=\" font-weight:600;\">supress noise</span>. All samples with a magnitude lower than this treshold will be eliminated after demodulation.</p><p>Tune this value by selecting a <span style=\" font-style:italic;\">noisy area</span> and mark it as noise using <span style=\" font-weight:600;\">context menu</span>.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.spinBoxNoiseTreshold.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>Set the <span style=\" font-weight:600;\">noise magnitude</span> of your signal. You can tune this value to mute noise in your signal and reveal the true data.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.spinBoxNoiseTreshold.setSuffix("")
#if QT_CONFIG(tooltip)
        self.spinBoxCenterSpacing.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>For <span style=\" font-weight:600;\">higher order</span> modulations (&gt; 1 Bits/Symbol), there are <span style=\" font-weight:600;\">multiple</span> centers. We assume that the <span style=\" font-weight:600;\">spacing</span> between all possible symbols is <span style=\" font-weight:600;\">constant</span>. Therefore you configure the spacing between centers.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEditSignalName.setText(QCoreApplication.translate("SignalFrame", u"SignalName", None))
        self.cbModulationType.setItemText(0, QCoreApplication.translate("SignalFrame", u"ASK", None))
        self.cbModulationType.setItemText(1, QCoreApplication.translate("SignalFrame", u"FSK", None))
        self.cbModulationType.setItemText(2, QCoreApplication.translate("SignalFrame", u"PSK", None))

#if QT_CONFIG(tooltip)
        self.cbModulationType.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>Choose signals modulation:</p><ul><li>Amplitude Shift Keying (ASK)</li><li>Frequency Shift Keying (FSK)</li><li>Phase Shift Keying (PSK)</li></ul></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnAdvancedModulationSettings.setText(QCoreApplication.translate("SignalFrame", u"...", None))
#if QT_CONFIG(tooltip)
        self.chkBoxSyncSelection.setToolTip(QCoreApplication.translate("SignalFrame", u"If this is set to true, your selected protocol bits will show up in the signal view, and vice versa.", None))
#endif // QT_CONFIG(tooltip)
        self.chkBoxSyncSelection.setText(QCoreApplication.translate("SignalFrame", u"Sync Selection", None))
        self.labelSpectrogramMin.setText(QCoreApplication.translate("SignalFrame", u"Data<sub>min</sub>:", None))
        self.labelSpectrogramMax.setText(QCoreApplication.translate("SignalFrame", u"Data<sub>max</sub>:", None))
#if QT_CONFIG(tooltip)
        self.chkBoxShowProtocol.setToolTip(QCoreApplication.translate("SignalFrame", u"Show the extracted protocol based on the parameters InfoLen, PauseLen and ZeroTreshold (in QuadratureDemod-View).\n"
"\n"
"If you want your protocol to be better seperated, edit the PauseLen using right-click menu from a selection in SignalView or ProtocolView.", None))
#endif // QT_CONFIG(tooltip)
        self.chkBoxShowProtocol.setText(QCoreApplication.translate("SignalFrame", u"Show Signal as", None))
#if QT_CONFIG(tooltip)
        self.spinBoxSamplesPerSymbol.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>This is the length of one symbol <span style=\" font-weight:600;\">in samples</span>. For <span style=\" font-weight:600;\">binary modulations </span>(default) this is the <span style=\" font-weight:600;\">bit length</span>.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btnAutoDetect.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>Automatically detect <span style=\" font-weight:600;\">center</span>, <span style=\" font-weight:600;\">bit length</span> and <span style=\" font-weight:600;\">tolerance</span>. You can also choose to addtionally detect the <span style=\" font-weight:600;\">noise</span> and <span style=\" font-weight:600;\">modulation</span> when clicking this button.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnAutoDetect.setText(QCoreApplication.translate("SignalFrame", u"Autodetect parameters", None))
        self.labelFFTWindowSize.setText(QCoreApplication.translate("SignalFrame", u"FFT Window Size:", None))
#if QT_CONFIG(tooltip)
        self.spinBoxCenterOffset.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>This is the threshold used for determining if a <span style=\" font-weight:600;\">bit is one or zero</span>. You can set it here or grab the middle of the area in <span style=\" font-style:italic;\">Quadrature Demod View</span>.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.labelNoise.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>Set the <span style=\" font-weight:600;\">noise magnitude</span> of your signal. You can tune this value to mute noise in your signal and reveal the true data.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.labelNoise.setText(QCoreApplication.translate("SignalFrame", u"Noise:", None))
#if QT_CONFIG(tooltip)
        self.lBitsPerSymbol.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p><span style=\" font-weight:600;\">Higher order</span> modulations can carry <span style=\" font-weight:600;\">multiple</span> bits with <span style=\" font-weight:600;\">each</span> symbol. Configure <span style=\" font-weight:600;\">how many</span> bits are represented by a symbol. (Default = Binary modulation with one bit per symbol)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lBitsPerSymbol.setText(QCoreApplication.translate("SignalFrame", u"Bits/Symbol:", None))
        self.labelLoadingAutoInterpretation.setText(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>Running automatic detecting of demodulation parameters.</p><p>You can disable this behaviour for newly loaded signals by unchecking <span style=\" font-weight:600;\">Edit</span> -&gt; <span style=\" font-weight:600;\">Auto detect signals on loading</span>.</p></body></html>", None))
        self.lYScale.setText(QCoreApplication.translate("SignalFrame", u"Y-Scale", None))
        self.btnShowHideStartEnd.setText(QCoreApplication.translate("SignalFrame", u"-", None))
#if QT_CONFIG(tooltip)
        self.lNumSelectedSamples.setToolTip(QCoreApplication.translate("SignalFrame", u"Number of currently selected samples.", None))
#endif // QT_CONFIG(tooltip)
        self.lNumSelectedSamples.setText(QCoreApplication.translate("SignalFrame", u"0", None))
#if QT_CONFIG(tooltip)
        self.lTextSelectedSamples.setToolTip(QCoreApplication.translate("SignalFrame", u"Number of currently selected samples.", None))
#endif // QT_CONFIG(tooltip)
        self.lTextSelectedSamples.setText(QCoreApplication.translate("SignalFrame", u"selected", None))
#if QT_CONFIG(tooltip)
        self.lDuration.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.lDuration.setText(QCoreApplication.translate("SignalFrame", u"42 \u00b5s", None))
#if QT_CONFIG(tooltip)
        self.labelRSSI.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>This is the average signal power of the selection. The closer this value is to zero, the stronger the selected signal is.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.labelRSSI.setText(QCoreApplication.translate("SignalFrame", u"0,434 dBm", None))
        self.btnFilter.setText(QCoreApplication.translate("SignalFrame", u"Filter (moving average)", None))
        self.lStart.setText(QCoreApplication.translate("SignalFrame", u"Start:", None))
        self.lEnd.setText(QCoreApplication.translate("SignalFrame", u"End:", None))
#if QT_CONFIG(tooltip)
        self.lZoomText.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>Current (relative) Zoom. Standard is 100%, if you zoom in, this factor increases. You can directly set a value in the spinbox or use the <span style=\" font-weight:600;\">mousewheel to zoom</span>.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lZoomText.setText(QCoreApplication.translate("SignalFrame", u"X-Zoom:", None))
#if QT_CONFIG(tooltip)
        self.spinBoxXZoom.setToolTip(QCoreApplication.translate("SignalFrame", u"<html><head/><body><p>Current (relative) Zoom. Standard is 100%, if you zoom in, this factor increases. You can directly set a value in the spinbox or use the <span style=\" font-weight:600;\">mousewheel to zoom</span>.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.spinBoxXZoom.setSuffix(QCoreApplication.translate("SignalFrame", u"%", None))
        self.lSamplesInView.setText(QCoreApplication.translate("SignalFrame", u"0", None))
        self.lStrich.setText(QCoreApplication.translate("SignalFrame", u"/", None))
        self.lSamplesTotal.setText(QCoreApplication.translate("SignalFrame", u"0", None))
        self.lSamplesViewText.setText(QCoreApplication.translate("SignalFrame", u"Samples in view", None))
    # retranslateUi

