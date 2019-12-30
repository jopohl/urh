# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analysis.ui'
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

import ProtocolTableView
import LabelValueTableView
import ProtocolTreeView
import MessageTypeTableView

class Ui_TabAnalysis(object):
    def setupUi(self, TabAnalysis):
        if TabAnalysis.objectName():
            TabAnalysis.setObjectName(u"TabAnalysis")
        TabAnalysis.resize(1331, 739)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TabAnalysis.sizePolicy().hasHeightForWidth())
        TabAnalysis.setSizePolicy(sizePolicy)
        TabAnalysis.setFocusPolicy(Qt.ClickFocus)
        TabAnalysis.setAcceptDrops(True)
        TabAnalysis.setProperty("lineWidth", 1)
        TabAnalysis.setProperty("midLineWidth", 0)
        self.verticalLayout_7 = QVBoxLayout(TabAnalysis)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(TabAnalysis)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1331, 739))
        self.verticalLayout_5 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.splitter_2 = QSplitter(self.scrollAreaWidgetContents)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setStyleSheet(u"QSplitter::handle:vertical {\n"
"margin: 4px 0px;\n"
"    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, \n"
"stop:0 rgba(255, 255, 255, 0), \n"
"stop:0.5 rgba(100, 100, 100, 100), \n"
"stop:1 rgba(255, 255, 255, 0));\n"
"image: url(:/icons/icons/splitter_handle_horizontal.svg);\n"
"}")
        self.splitter_2.setOrientation(Qt.Vertical)
        self.splitter_2.setHandleWidth(6)
        self.splitter = QSplitter(self.splitter_2)
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
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayout_2 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.tabWidget = QTabWidget(self.layoutWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setStyleSheet(u"QTabWidget::pane { border: 0; }")
        self.tab_protocols = QWidget()
        self.tab_protocols.setObjectName(u"tab_protocols")
        self.verticalLayout_3 = QVBoxLayout(self.tab_protocols)
        self.verticalLayout_3.setSpacing(7)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.treeViewProtocols = ProtocolTreeView(self.tab_protocols)
        self.treeViewProtocols.setObjectName(u"treeViewProtocols")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.treeViewProtocols.sizePolicy().hasHeightForWidth())
        self.treeViewProtocols.setSizePolicy(sizePolicy1)
        self.treeViewProtocols.setAcceptDrops(True)
        self.treeViewProtocols.setFrameShape(QFrame.StyledPanel)
        self.treeViewProtocols.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.treeViewProtocols.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.treeViewProtocols.setDragEnabled(True)
        self.treeViewProtocols.setDragDropOverwriteMode(False)
        self.treeViewProtocols.setDragDropMode(QAbstractItemView.DragDrop)
        self.treeViewProtocols.setDefaultDropAction(Qt.IgnoreAction)
        self.treeViewProtocols.setSelectionMode(QAbstractItemView.SingleSelection)
        self.treeViewProtocols.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.treeViewProtocols.setTextElideMode(Qt.ElideRight)
        self.treeViewProtocols.setAnimated(True)
        self.treeViewProtocols.header().setVisible(False)
        self.treeViewProtocols.header().setCascadingSectionResizes(False)
        self.treeViewProtocols.header().setStretchLastSection(True)

        self.verticalLayout_3.addWidget(self.treeViewProtocols)

        self.tabWidget.addTab(self.tab_protocols, QString())
        self.tab_participants = QWidget()
        self.tab_participants.setObjectName(u"tab_participants")
        self.verticalLayout_11 = QVBoxLayout(self.tab_participants)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.listViewParticipants = QListView(self.tab_participants)
        self.listViewParticipants.setObjectName(u"listViewParticipants")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.listViewParticipants.sizePolicy().hasHeightForWidth())
        self.listViewParticipants.setSizePolicy(sizePolicy2)
        self.listViewParticipants.setFrameShape(QFrame.StyledPanel)
        self.listViewParticipants.setTextElideMode(Qt.ElideRight)

        self.verticalLayout_11.addWidget(self.listViewParticipants)

        self.tabWidget.addTab(self.tab_participants, QString())

        self.verticalLayout_2.addWidget(self.tabWidget)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_5 = QLabel(self.layoutWidget)
        self.label_5.setObjectName(u"label_5")
        font = QFont()
        font.setBold(True)
        font.setWeight(75);
        self.label_5.setFont(font)

        self.gridLayout_3.addWidget(self.label_5, 1, 0, 1, 1)

        self.label_4 = QLabel(self.layoutWidget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font)

        self.gridLayout_3.addWidget(self.label_4, 0, 0, 1, 1)

        self.lEncodingErrors = QLabel(self.layoutWidget)
        self.lEncodingErrors.setObjectName(u"lEncodingErrors")
        sizePolicy.setHeightForWidth(self.lEncodingErrors.sizePolicy().hasHeightForWidth())
        self.lEncodingErrors.setSizePolicy(sizePolicy)
        self.lEncodingErrors.setFont(font)

        self.gridLayout_3.addWidget(self.lEncodingErrors, 2, 0, 1, 1)

        self.cbDecoding = QComboBox(self.layoutWidget)
        self.cbDecoding.addItem(QString())
        self.cbDecoding.addItem(QString())
        self.cbDecoding.addItem(QString())
        self.cbDecoding.addItem(QString())
        self.cbDecoding.addItem(QString())
        self.cbDecoding.setObjectName(u"cbDecoding")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.cbDecoding.sizePolicy().hasHeightForWidth())
        self.cbDecoding.setSizePolicy(sizePolicy3)
        self.cbDecoding.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.gridLayout_3.addWidget(self.cbDecoding, 1, 1, 1, 1)

        self.chkBoxShowOnlyDiffs = QCheckBox(self.layoutWidget)
        self.chkBoxShowOnlyDiffs.setObjectName(u"chkBoxShowOnlyDiffs")
        sizePolicy3.setHeightForWidth(self.chkBoxShowOnlyDiffs.sizePolicy().hasHeightForWidth())
        self.chkBoxShowOnlyDiffs.setSizePolicy(sizePolicy3)

        self.gridLayout_3.addWidget(self.chkBoxShowOnlyDiffs, 4, 0, 1, 2)

        self.cbProtoView = QComboBox(self.layoutWidget)
        self.cbProtoView.addItem(QString())
        self.cbProtoView.addItem(QString())
        self.cbProtoView.addItem(QString())
        self.cbProtoView.setObjectName(u"cbProtoView")
        sizePolicy3.setHeightForWidth(self.cbProtoView.sizePolicy().hasHeightForWidth())
        self.cbProtoView.setSizePolicy(sizePolicy3)

        self.gridLayout_3.addWidget(self.cbProtoView, 0, 1, 1, 1)

        self.lDecodingErrorsValue = QLabel(self.layoutWidget)
        self.lDecodingErrorsValue.setObjectName(u"lDecodingErrorsValue")
        sizePolicy3.setHeightForWidth(self.lDecodingErrorsValue.sizePolicy().hasHeightForWidth())
        self.lDecodingErrorsValue.setSizePolicy(sizePolicy3)

        self.gridLayout_3.addWidget(self.lDecodingErrorsValue, 2, 1, 1, 1)

        self.chkBoxOnlyShowLabelsInProtocol = QCheckBox(self.layoutWidget)
        self.chkBoxOnlyShowLabelsInProtocol.setObjectName(u"chkBoxOnlyShowLabelsInProtocol")
        sizePolicy3.setHeightForWidth(self.chkBoxOnlyShowLabelsInProtocol.sizePolicy().hasHeightForWidth())
        self.chkBoxOnlyShowLabelsInProtocol.setSizePolicy(sizePolicy3)

        self.gridLayout_3.addWidget(self.chkBoxOnlyShowLabelsInProtocol, 5, 0, 1, 2)

        self.cbShowDiffs = QCheckBox(self.layoutWidget)
        self.cbShowDiffs.setObjectName(u"cbShowDiffs")
        sizePolicy3.setHeightForWidth(self.cbShowDiffs.sizePolicy().hasHeightForWidth())
        self.cbShowDiffs.setSizePolicy(sizePolicy3)

        self.gridLayout_3.addWidget(self.cbShowDiffs, 3, 0, 1, 2)

        self.stackedWidgetLogicAnalysis = QStackedWidget(self.layoutWidget)
        self.stackedWidgetLogicAnalysis.setObjectName(u"stackedWidgetLogicAnalysis")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.stackedWidgetLogicAnalysis.sizePolicy().hasHeightForWidth())
        self.stackedWidgetLogicAnalysis.setSizePolicy(sizePolicy4)
        self.pageButtonAnalyzer = QWidget()
        self.pageButtonAnalyzer.setObjectName(u"pageButtonAnalyzer")
        self.verticalLayout_8 = QVBoxLayout(self.pageButtonAnalyzer)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.btnAnalyze = QToolButton(self.pageButtonAnalyzer)
        self.btnAnalyze.setObjectName(u"btnAnalyze")
        sizePolicy3.setHeightForWidth(self.btnAnalyze.sizePolicy().hasHeightForWidth())
        self.btnAnalyze.setSizePolicy(sizePolicy3)
        self.btnAnalyze.setPopupMode(QToolButton.MenuButtonPopup)
        self.btnAnalyze.setToolButtonStyle(Qt.ToolButtonTextOnly)

        self.verticalLayout_8.addWidget(self.btnAnalyze)

        self.stackedWidgetLogicAnalysis.addWidget(self.pageButtonAnalyzer)
        self.pageProgressBar = QWidget()
        self.pageProgressBar.setObjectName(u"pageProgressBar")
        self.verticalLayout_9 = QVBoxLayout(self.pageProgressBar)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.progressBarLogicAnalyzer = QProgressBar(self.pageProgressBar)
        self.progressBarLogicAnalyzer.setObjectName(u"progressBarLogicAnalyzer")
        sizePolicy3.setHeightForWidth(self.progressBarLogicAnalyzer.sizePolicy().hasHeightForWidth())
        self.progressBarLogicAnalyzer.setSizePolicy(sizePolicy3)
        self.progressBarLogicAnalyzer.setValue(24)

        self.verticalLayout_9.addWidget(self.progressBarLogicAnalyzer)

        self.stackedWidgetLogicAnalysis.addWidget(self.pageProgressBar)

        self.gridLayout_3.addWidget(self.stackedWidgetLogicAnalysis, 6, 0, 1, 2)


        self.verticalLayout_2.addLayout(self.gridLayout_3)

        self.splitter.addWidget(self.layoutWidget)
        self.layoutWidget1 = QWidget(self.splitter)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.verticalLayout = QVBoxLayout(self.layoutWidget1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.btnSaveProto = QToolButton(self.layoutWidget1)
        self.btnSaveProto.setObjectName(u"btnSaveProto")
        sizePolicy5 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.btnSaveProto.sizePolicy().hasHeightForWidth())
        self.btnSaveProto.setSizePolicy(sizePolicy5)
        self.btnSaveProto.setBaseSize(QSize(0, 0))
        icon = QIcon()
        iconThemeName = u"document-save"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnSaveProto.setIcon(icon)
        self.btnSaveProto.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.gridLayout_2.addWidget(self.btnSaveProto, 0, 16, 1, 1)

        self.lSlash = QLabel(self.layoutWidget1)
        self.lSlash.setObjectName(u"lSlash")
        sizePolicy.setHeightForWidth(self.lSlash.sizePolicy().hasHeightForWidth())
        self.lSlash.setSizePolicy(sizePolicy)
        self.lSlash.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.lSlash, 0, 7, 1, 1)

        self.lblShownRows = QLabel(self.layoutWidget1)
        self.lblShownRows.setObjectName(u"lblShownRows")

        self.gridLayout_2.addWidget(self.lblShownRows, 0, 4, 1, 1)

        self.lTime = QLabel(self.layoutWidget1)
        self.lTime.setObjectName(u"lTime")
        sizePolicy6 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.lTime.sizePolicy().hasHeightForWidth())
        self.lTime.setSizePolicy(sizePolicy6)
        self.lTime.setTextFormat(Qt.PlainText)
        self.lTime.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.lTime, 0, 15, 1, 1)

        self.lSearchCurrent = QLabel(self.layoutWidget1)
        self.lSearchCurrent.setObjectName(u"lSearchCurrent")
        sizePolicy.setHeightForWidth(self.lSearchCurrent.sizePolicy().hasHeightForWidth())
        self.lSearchCurrent.setSizePolicy(sizePolicy)
        self.lSearchCurrent.setStyleSheet(u"QLabel\n"
"{\n"
"    qproperty-alignment: AlignCenter;\n"
"}")

        self.gridLayout_2.addWidget(self.lSearchCurrent, 0, 6, 1, 1)

        self.lblRSSI = QLabel(self.layoutWidget1)
        self.lblRSSI.setObjectName(u"lblRSSI")
        sizePolicy6.setHeightForWidth(self.lblRSSI.sizePolicy().hasHeightForWidth())
        self.lblRSSI.setSizePolicy(sizePolicy6)

        self.gridLayout_2.addWidget(self.lblRSSI, 0, 12, 1, 1)

        self.btnNextSearch = QToolButton(self.layoutWidget1)
        self.btnNextSearch.setObjectName(u"btnNextSearch")
        self.btnNextSearch.setEnabled(False)
        sizePolicy.setHeightForWidth(self.btnNextSearch.sizePolicy().hasHeightForWidth())
        self.btnNextSearch.setSizePolicy(sizePolicy)
        icon1 = QIcon()
        iconThemeName = u"go-next"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnNextSearch.setIcon(icon1)

        self.gridLayout_2.addWidget(self.btnNextSearch, 0, 9, 1, 1)

        self.btnPrevSearch = QToolButton(self.layoutWidget1)
        self.btnPrevSearch.setObjectName(u"btnPrevSearch")
        self.btnPrevSearch.setEnabled(False)
        sizePolicy.setHeightForWidth(self.btnPrevSearch.sizePolicy().hasHeightForWidth())
        self.btnPrevSearch.setSizePolicy(sizePolicy)
        icon2 = QIcon()
        iconThemeName = u"go-previous"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnPrevSearch.setIcon(icon2)

        self.gridLayout_2.addWidget(self.btnPrevSearch, 0, 5, 1, 1)

        self.lSearchTotal = QLabel(self.layoutWidget1)
        self.lSearchTotal.setObjectName(u"lSearchTotal")
        sizePolicy.setHeightForWidth(self.lSearchTotal.sizePolicy().hasHeightForWidth())
        self.lSearchTotal.setSizePolicy(sizePolicy)
        self.lSearchTotal.setStyleSheet(u"QLabel\n"
"{\n"
"    qproperty-alignment: AlignCenter;\n"
"}")

        self.gridLayout_2.addWidget(self.lSearchTotal, 0, 8, 1, 1)

        self.label_3 = QLabel(self.layoutWidget1)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_3, 0, 14, 1, 1)

        self.line_2 = QFrame(self.layoutWidget1)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.line_2, 0, 13, 1, 1)

        self.btnSearchSelectFilter = QToolButton(self.layoutWidget1)
        self.btnSearchSelectFilter.setObjectName(u"btnSearchSelectFilter")
        sizePolicy.setHeightForWidth(self.btnSearchSelectFilter.sizePolicy().hasHeightForWidth())
        self.btnSearchSelectFilter.setSizePolicy(sizePolicy)
        icon3 = QIcon()
        iconThemeName = u"edit-find"
        if QIcon.hasThemeIcon(iconThemeName):
            icon3 = QIcon.fromTheme(iconThemeName)
        else:
            icon3.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnSearchSelectFilter.setIcon(icon3)
        self.btnSearchSelectFilter.setPopupMode(QToolButton.MenuButtonPopup)
        self.btnSearchSelectFilter.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.btnSearchSelectFilter.setAutoRaise(False)
        self.btnSearchSelectFilter.setArrowType(Qt.NoArrow)

        self.gridLayout_2.addWidget(self.btnSearchSelectFilter, 0, 2, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(60, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_2, 0, 10, 1, 1)

        self.line = QFrame(self.layoutWidget1)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.line, 0, 11, 1, 1)

        self.btnLoadProto = QToolButton(self.layoutWidget1)
        self.btnLoadProto.setObjectName(u"btnLoadProto")
        sizePolicy5.setHeightForWidth(self.btnLoadProto.sizePolicy().hasHeightForWidth())
        self.btnLoadProto.setSizePolicy(sizePolicy5)
        icon4 = QIcon()
        iconThemeName = u"document-open"
        if QIcon.hasThemeIcon(iconThemeName):
            icon4 = QIcon.fromTheme(iconThemeName)
        else:
            icon4.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnLoadProto.setIcon(icon4)

        self.gridLayout_2.addWidget(self.btnLoadProto, 0, 17, 1, 1)

        self.lblClearAlignment = QLabel(self.layoutWidget1)
        self.lblClearAlignment.setObjectName(u"lblClearAlignment")

        self.gridLayout_2.addWidget(self.lblClearAlignment, 0, 3, 1, 1)

        self.lineEditSearch = QLineEdit(self.layoutWidget1)
        self.lineEditSearch.setObjectName(u"lineEditSearch")
        sizePolicy6.setHeightForWidth(self.lineEditSearch.sizePolicy().hasHeightForWidth())
        self.lineEditSearch.setSizePolicy(sizePolicy6)
        self.lineEditSearch.setAcceptDrops(False)
        self.lineEditSearch.setClearButtonEnabled(True)

        self.gridLayout_2.addWidget(self.lineEditSearch, 0, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_2)

        self.tblViewProtocol = ProtocolTableView(self.layoutWidget1)
        self.tblViewProtocol.setObjectName(u"tblViewProtocol")
        sizePolicy7 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.tblViewProtocol.sizePolicy().hasHeightForWidth())
        self.tblViewProtocol.setSizePolicy(sizePolicy7)
        self.tblViewProtocol.setAcceptDrops(True)
        self.tblViewProtocol.setAutoFillBackground(True)
        self.tblViewProtocol.setFrameShape(QFrame.StyledPanel)
        self.tblViewProtocol.setFrameShadow(QFrame.Sunken)
        self.tblViewProtocol.setLineWidth(1)
        self.tblViewProtocol.setAutoScroll(True)
        self.tblViewProtocol.setDragDropMode(QAbstractItemView.DropOnly)
        self.tblViewProtocol.setAlternatingRowColors(True)
        self.tblViewProtocol.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tblViewProtocol.setTextElideMode(Qt.ElideNone)
        self.tblViewProtocol.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tblViewProtocol.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tblViewProtocol.setShowGrid(False)
        self.tblViewProtocol.setGridStyle(Qt.NoPen)
        self.tblViewProtocol.setSortingEnabled(False)
        self.tblViewProtocol.setWordWrap(False)
        self.tblViewProtocol.setCornerButtonEnabled(False)
        self.tblViewProtocol.horizontalHeader().setDefaultSectionSize(57)

        self.verticalLayout.addWidget(self.tblViewProtocol)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.lBits = QLabel(self.layoutWidget1)
        self.lBits.setObjectName(u"lBits")
        sizePolicy.setHeightForWidth(self.lBits.sizePolicy().hasHeightForWidth())
        self.lBits.setSizePolicy(sizePolicy)
        self.lBits.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_3.addWidget(self.lBits)

        self.lBitsSelection = QLineEdit(self.layoutWidget1)
        self.lBitsSelection.setObjectName(u"lBitsSelection")
        sizePolicy6.setHeightForWidth(self.lBitsSelection.sizePolicy().hasHeightForWidth())
        self.lBitsSelection.setSizePolicy(sizePolicy6)
        self.lBitsSelection.setMaximumSize(QSize(16777215, 16777215))
        self.lBitsSelection.setAcceptDrops(False)
        self.lBitsSelection.setStyleSheet(u"background-color: rgba(255, 255, 255, 0);")
        self.lBitsSelection.setFrame(False)
        self.lBitsSelection.setReadOnly(True)

        self.horizontalLayout_3.addWidget(self.lBitsSelection)

        self.lHex = QLabel(self.layoutWidget1)
        self.lHex.setObjectName(u"lHex")
        sizePolicy.setHeightForWidth(self.lHex.sizePolicy().hasHeightForWidth())
        self.lHex.setSizePolicy(sizePolicy)
        self.lHex.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_3.addWidget(self.lHex)

        self.lHexSelection = QLineEdit(self.layoutWidget1)
        self.lHexSelection.setObjectName(u"lHexSelection")
        sizePolicy6.setHeightForWidth(self.lHexSelection.sizePolicy().hasHeightForWidth())
        self.lHexSelection.setSizePolicy(sizePolicy6)
        self.lHexSelection.setMaximumSize(QSize(16777215, 16777215))
        self.lHexSelection.setAcceptDrops(False)
        self.lHexSelection.setStyleSheet(u"background-color: rgba(255, 255, 255, 0);")
        self.lHexSelection.setFrame(False)
        self.lHexSelection.setReadOnly(True)

        self.horizontalLayout_3.addWidget(self.lHexSelection)

        self.lDecimal = QLabel(self.layoutWidget1)
        self.lDecimal.setObjectName(u"lDecimal")
        sizePolicy.setHeightForWidth(self.lDecimal.sizePolicy().hasHeightForWidth())
        self.lDecimal.setSizePolicy(sizePolicy)
        self.lDecimal.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_3.addWidget(self.lDecimal)

        self.lDecimalSelection = QLineEdit(self.layoutWidget1)
        self.lDecimalSelection.setObjectName(u"lDecimalSelection")
        sizePolicy6.setHeightForWidth(self.lDecimalSelection.sizePolicy().hasHeightForWidth())
        self.lDecimalSelection.setSizePolicy(sizePolicy6)
        self.lDecimalSelection.setMaximumSize(QSize(16777215, 16777215))
        self.lDecimalSelection.setAcceptDrops(False)
        self.lDecimalSelection.setStyleSheet(u"background-color: rgba(255, 255, 255, 0);")
        self.lDecimalSelection.setFrame(False)
        self.lDecimalSelection.setReadOnly(True)

        self.horizontalLayout_3.addWidget(self.lDecimalSelection)

        self.lNumSelectedColumns = QLabel(self.layoutWidget1)
        self.lNumSelectedColumns.setObjectName(u"lNumSelectedColumns")
        sizePolicy6.setHeightForWidth(self.lNumSelectedColumns.sizePolicy().hasHeightForWidth())
        self.lNumSelectedColumns.setSizePolicy(sizePolicy6)
        self.lNumSelectedColumns.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.lNumSelectedColumns)

        self.lColumnsSelectedText = QLabel(self.layoutWidget1)
        self.lColumnsSelectedText.setObjectName(u"lColumnsSelectedText")

        self.horizontalLayout_3.addWidget(self.lColumnsSelectedText)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.splitter.addWidget(self.layoutWidget1)
        self.splitter_2.addWidget(self.splitter)
        self.layoutWidget2 = QWidget(self.splitter_2)
        self.layoutWidget2.setObjectName(u"layoutWidget2")
        self.verticalLayout_4 = QVBoxLayout(self.layoutWidget2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(11, 11, 11, 11)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.layoutWidget2)
        self.label.setObjectName(u"label")
        sizePolicy3.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy3)
        self.label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.lblLabelValues = QLabel(self.layoutWidget2)
        self.lblLabelValues.setObjectName(u"lblLabelValues")
        sizePolicy3.setHeightForWidth(self.lblLabelValues.sizePolicy().hasHeightForWidth())
        self.lblLabelValues.setSizePolicy(sizePolicy3)
        self.lblLabelValues.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.lblLabelValues, 0, 1, 1, 1)

        self.btnAddMessagetype = QToolButton(self.layoutWidget2)
        self.btnAddMessagetype.setObjectName(u"btnAddMessagetype")
        sizePolicy3.setHeightForWidth(self.btnAddMessagetype.sizePolicy().hasHeightForWidth())
        self.btnAddMessagetype.setSizePolicy(sizePolicy3)
        icon5 = QIcon()
        iconThemeName = u"list-add"
        if QIcon.hasThemeIcon(iconThemeName):
            icon5 = QIcon.fromTheme(iconThemeName)
        else:
            icon5.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnAddMessagetype.setIcon(icon5)
        self.btnAddMessagetype.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.gridLayout.addWidget(self.btnAddMessagetype, 3, 0, 1, 1)

        self.tblLabelValues = LabelValueTableView(self.layoutWidget2)
        self.tblLabelValues.setObjectName(u"tblLabelValues")
        sizePolicy6.setHeightForWidth(self.tblLabelValues.sizePolicy().hasHeightForWidth())
        self.tblLabelValues.setSizePolicy(sizePolicy6)
        self.tblLabelValues.setFrameShape(QFrame.StyledPanel)
        self.tblLabelValues.setAlternatingRowColors(True)
        self.tblLabelValues.setShowGrid(False)
        self.tblLabelValues.horizontalHeader().setVisible(True)
        self.tblLabelValues.horizontalHeader().setCascadingSectionResizes(False)
        self.tblLabelValues.horizontalHeader().setDefaultSectionSize(150)
        self.tblLabelValues.horizontalHeader().setStretchLastSection(True)
        self.tblLabelValues.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.tblLabelValues, 1, 1, 3, 1)

        self.tblViewMessageTypes = MessageTypeTableView(self.layoutWidget2)
        self.tblViewMessageTypes.setObjectName(u"tblViewMessageTypes")
        sizePolicy.setHeightForWidth(self.tblViewMessageTypes.sizePolicy().hasHeightForWidth())
        self.tblViewMessageTypes.setSizePolicy(sizePolicy)
        self.tblViewMessageTypes.setAcceptDrops(False)
        self.tblViewMessageTypes.setFrameShape(QFrame.StyledPanel)
        self.tblViewMessageTypes.setAlternatingRowColors(True)
        self.tblViewMessageTypes.setShowGrid(False)
        self.tblViewMessageTypes.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.tblViewMessageTypes, 1, 0, 2, 1)


        self.verticalLayout_4.addLayout(self.gridLayout)

        self.splitter_2.addWidget(self.layoutWidget2)

        self.verticalLayout_5.addWidget(self.splitter_2)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_7.addWidget(self.scrollArea)


        self.retranslateUi(TabAnalysis)

        self.tabWidget.setCurrentIndex(0)
        self.stackedWidgetLogicAnalysis.setCurrentIndex(0)

    # setupUi

    def retranslateUi(self, TabAnalysis):
        TabAnalysis.setWindowTitle(QCoreApplication.translate("TabAnalysis", u"Frame", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_protocols), QCoreApplication.translate("TabAnalysis", u"Protocols", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_participants), QCoreApplication.translate("TabAnalysis", u"Participants", None))
        self.label_5.setText(QCoreApplication.translate("TabAnalysis", u"Decoding:", None))
        self.label_4.setText(QCoreApplication.translate("TabAnalysis", u"View data as:", None))
        self.lEncodingErrors.setText(QCoreApplication.translate("TabAnalysis", u"Decoding errors:", None))
        self.cbDecoding.setItemText(0, QCoreApplication.translate("TabAnalysis", u"NRZ", None))
        self.cbDecoding.setItemText(1, QCoreApplication.translate("TabAnalysis", u"Manchester", None))
        self.cbDecoding.setItemText(2, QCoreApplication.translate("TabAnalysis", u"Manchester II", None))
        self.cbDecoding.setItemText(3, QCoreApplication.translate("TabAnalysis", u"Differential Manchester", None))
        self.cbDecoding.setItemText(4, QCoreApplication.translate("TabAnalysis", u"...", None))

        self.chkBoxShowOnlyDiffs.setText(QCoreApplication.translate("TabAnalysis", u"Show only diffs in protocol", None))
        self.cbProtoView.setItemText(0, QCoreApplication.translate("TabAnalysis", u"Bits", None))
        self.cbProtoView.setItemText(1, QCoreApplication.translate("TabAnalysis", u"Hex", None))
        self.cbProtoView.setItemText(2, QCoreApplication.translate("TabAnalysis", u"ASCII", None))

#if QT_CONFIG(tooltip)
        self.cbProtoView.setToolTip(QCoreApplication.translate("TabAnalysis", u"<html><head/><body><p>Set the desired view here.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lDecodingErrorsValue.setText(QCoreApplication.translate("TabAnalysis", u"0 (0.00%)", None))
        self.chkBoxOnlyShowLabelsInProtocol.setText(QCoreApplication.translate("TabAnalysis", u"Show only labels in protocol", None))
        self.cbShowDiffs.setText(QCoreApplication.translate("TabAnalysis", u"Mark diffs in protocol", None))
#if QT_CONFIG(tooltip)
        self.btnAnalyze.setToolTip(QCoreApplication.translate("TabAnalysis", u"<html><head/><body><p>Run some automatic analysis on the protocol e.g. assign labels automatically. You can configure which checks to run with the arrow on the right of this button.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnAnalyze.setText(QCoreApplication.translate("TabAnalysis", u"Analyze Protocol", None))
#if QT_CONFIG(tooltip)
        self.btnSaveProto.setToolTip(QCoreApplication.translate("TabAnalysis", u"Save current protocol.", None))
#endif // QT_CONFIG(tooltip)
        self.btnSaveProto.setText("")
        self.lSlash.setText(QCoreApplication.translate("TabAnalysis", u"/", None))
        self.lblShownRows.setText(QCoreApplication.translate("TabAnalysis", u"shown: 42/108", None))
#if QT_CONFIG(tooltip)
        self.lTime.setToolTip(QCoreApplication.translate("TabAnalysis", u"<html><head/><body><p>The <span style=\" font-weight:600;\">Message</span><span style=\" font-weight:600;\">Start</span> is the point in time when a protocol message begins. Additionally the relative time (+ ...) from the previous message is shown.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lTime.setText(QCoreApplication.translate("TabAnalysis", u"0 (+0)", None))
        self.lSearchCurrent.setText(QCoreApplication.translate("TabAnalysis", u"-", None))
#if QT_CONFIG(tooltip)
        self.lblRSSI.setToolTip(QCoreApplication.translate("TabAnalysis", u"<html><head/><body><p>This is the average signal power of the current message. The nearer this value is to zero, the stronger the signal is.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblRSSI.setText(QCoreApplication.translate("TabAnalysis", u"-\u221e dBm", None))
        self.btnNextSearch.setText(QCoreApplication.translate("TabAnalysis", u">", None))
        self.btnPrevSearch.setText(QCoreApplication.translate("TabAnalysis", u"<", None))
        self.lSearchTotal.setText(QCoreApplication.translate("TabAnalysis", u"-", None))
#if QT_CONFIG(tooltip)
        self.label_3.setToolTip(QCoreApplication.translate("TabAnalysis", u"<html><head/><body><p>The <span style=\" font-weight:600;\">Message Start</span> is the point in time when a protocol message begins. Additionally the relative time (+ ...) from the previous message is shown.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_3.setText(QCoreApplication.translate("TabAnalysis", u"Timestamp:", None))
        self.btnSearchSelectFilter.setText(QCoreApplication.translate("TabAnalysis", u"Search", None))
#if QT_CONFIG(tooltip)
        self.btnLoadProto.setToolTip(QCoreApplication.translate("TabAnalysis", u"Load a protocol.", None))
#endif // QT_CONFIG(tooltip)
        self.btnLoadProto.setText(QCoreApplication.translate("TabAnalysis", u"...", None))
        self.lblClearAlignment.setText(QCoreApplication.translate("TabAnalysis", u"<html><head/><body><p><a href=\"reset_alignment\"><span style=\" text-decoration: underline; color:#0000ff;\">Reset alignment</span></a></p></body></html>", None))
        self.lineEditSearch.setPlaceholderText(QCoreApplication.translate("TabAnalysis", u"Enter pattern here", None))
        self.lBits.setText(QCoreApplication.translate("TabAnalysis", u"Bit:", None))
        self.lHex.setText(QCoreApplication.translate("TabAnalysis", u"Hex:", None))
        self.lDecimal.setText(QCoreApplication.translate("TabAnalysis", u"Decimal:", None))
        self.lNumSelectedColumns.setText(QCoreApplication.translate("TabAnalysis", u"0", None))
        self.lColumnsSelectedText.setText(QCoreApplication.translate("TabAnalysis", u"column(s) selected", None))
        self.label.setText(QCoreApplication.translate("TabAnalysis", u"Message types", None))
        self.lblLabelValues.setText(QCoreApplication.translate("TabAnalysis", u"Labels for message", None))
#if QT_CONFIG(tooltip)
        self.btnAddMessagetype.setToolTip(QCoreApplication.translate("TabAnalysis", u"Add a new message type", None))
#endif // QT_CONFIG(tooltip)
        self.btnAddMessagetype.setText(QCoreApplication.translate("TabAnalysis", u"Add new message type", None))
#if QT_CONFIG(tooltip)
        self.tblViewMessageTypes.setToolTip("")
#endif // QT_CONFIG(tooltip)
    # retranslateUi

