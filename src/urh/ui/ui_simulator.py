# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'simulator.ui'
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

import ParticipantTableView
import GeneratorTreeView
import SimulatorGraphicsView
import SimulatorMessageTableView
import ExpressionLineEdit
import SimulatorLabelTableView

class Ui_SimulatorTab(object):
    def setupUi(self, SimulatorTab):
        if SimulatorTab.objectName():
            SimulatorTab.setObjectName(u"SimulatorTab")
        SimulatorTab.resize(842, 689)
        self.verticalLayout_8 = QVBoxLayout(SimulatorTab)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(SimulatorTab)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 842, 689))
        self.verticalLayout_5 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.splitterLeftRight = QSplitter(self.scrollAreaWidgetContents)
        self.splitterLeftRight.setObjectName(u"splitterLeftRight")
        self.splitterLeftRight.setStyleSheet(u"QSplitter::handle:horizontal {\n"
"margin: 4px 0px;\n"
"    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
"stop:0 rgba(255, 255, 255, 0), \n"
"stop:0.5 rgba(100, 100, 100, 100), \n"
"stop:1 rgba(255, 255, 255, 0));\n"
"image: url(:/icons/icons/splitter_handle_vertical.svg);\n"
"}")
        self.splitterLeftRight.setOrientation(Qt.Horizontal)
        self.splitterLeftRight.setHandleWidth(6)
        self.layoutWidget = QWidget(self.splitterLeftRight)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayout_3 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(11, 11, 11, 11)
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")

        self.verticalLayout_3.addWidget(self.label)

        self.treeProtocols = GeneratorTreeView(self.layoutWidget)
        self.treeProtocols.setObjectName(u"treeProtocols")

        self.verticalLayout_3.addWidget(self.treeProtocols)

        self.label_6 = QLabel(self.layoutWidget)
        self.label_6.setObjectName(u"label_6")

        self.verticalLayout_3.addWidget(self.label_6)

        self.listViewSimulate = QListView(self.layoutWidget)
        self.listViewSimulate.setObjectName(u"listViewSimulate")
        self.listViewSimulate.setAlternatingRowColors(True)

        self.verticalLayout_3.addWidget(self.listViewSimulate)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_4 = QLabel(self.layoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)

        self.spinBoxNRepeat = QSpinBox(self.layoutWidget)
        self.spinBoxNRepeat.setObjectName(u"spinBoxNRepeat")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBoxNRepeat.sizePolicy().hasHeightForWidth())
        self.spinBoxNRepeat.setSizePolicy(sizePolicy)
        self.spinBoxNRepeat.setMaximum(9999999)

        self.gridLayout.addWidget(self.spinBoxNRepeat, 0, 1, 1, 1)

        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.spinBoxTimeout = QSpinBox(self.layoutWidget)
        self.spinBoxTimeout.setObjectName(u"spinBoxTimeout")
        sizePolicy.setHeightForWidth(self.spinBoxTimeout.sizePolicy().hasHeightForWidth())
        self.spinBoxTimeout.setSizePolicy(sizePolicy)
        self.spinBoxTimeout.setMinimum(1)
        self.spinBoxTimeout.setMaximum(9999999)

        self.gridLayout.addWidget(self.spinBoxTimeout, 1, 1, 1, 1)

        self.label_7 = QLabel(self.layoutWidget)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 2, 0, 1, 1)

        self.comboBoxError = QComboBox(self.layoutWidget)
        self.comboBoxError.addItem(QString())
        self.comboBoxError.addItem(QString())
        self.comboBoxError.addItem(QString())
        self.comboBoxError.setObjectName(u"comboBoxError")
        sizePolicy.setHeightForWidth(self.comboBoxError.sizePolicy().hasHeightForWidth())
        self.comboBoxError.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.comboBoxError, 2, 1, 1, 1)

        self.label_8 = QLabel(self.layoutWidget)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 3, 0, 1, 1)

        self.spinBoxRetries = QSpinBox(self.layoutWidget)
        self.spinBoxRetries.setObjectName(u"spinBoxRetries")
        self.spinBoxRetries.setMinimum(1)
        self.spinBoxRetries.setMaximum(9999999)
        self.spinBoxRetries.setValue(10)

        self.gridLayout.addWidget(self.spinBoxRetries, 3, 1, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout)

        self.btnStartSim = QPushButton(self.layoutWidget)
        self.btnStartSim.setObjectName(u"btnStartSim")
        icon = QIcon()
        iconThemeName = u"media-playback-start"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnStartSim.setIcon(icon)

        self.verticalLayout_3.addWidget(self.btnStartSim)

        self.splitterLeftRight.addWidget(self.layoutWidget)
        self.splitter = QSplitter(self.splitterLeftRight)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setStyleSheet(u"QSplitter::handle:vertical {\n"
"margin: 4px 0px;\n"
"    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, \n"
"stop:0 rgba(255, 255, 255, 0), \n"
"stop:0.5 rgba(100, 100, 100, 100), \n"
"stop:1 rgba(255, 255, 255, 0));\n"
"image: url(:/icons/icons/splitter_handle_horizontal.svg);\n"
"}")
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setHandleWidth(6)
        self.layoutWidget_2 = QWidget(self.splitter)
        self.layoutWidget_2.setObjectName(u"layoutWidget_2")
        self.verticalLayout_2 = QVBoxLayout(self.layoutWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.tabWidget = QTabWidget(self.layoutWidget_2)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy1)
        self.tabWidget.setStyleSheet(u"QTabWidget::pane { border: 0; }")
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout = QVBoxLayout(self.tab)
        self.verticalLayout.setSpacing(7)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.gvSimulator = SimulatorGraphicsView(self.tab)
        self.gvSimulator.setObjectName(u"gvSimulator")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.gvSimulator.sizePolicy().hasHeightForWidth())
        self.gvSimulator.setSizePolicy(sizePolicy2)

        self.verticalLayout.addWidget(self.gvSimulator)

        self.tabWidget.addTab(self.tab, QString())
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_6 = QVBoxLayout(self.tab_2)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.tblViewMessage = SimulatorMessageTableView(self.tab_2)
        self.tblViewMessage.setObjectName(u"tblViewMessage")
        sizePolicy2.setHeightForWidth(self.tblViewMessage.sizePolicy().hasHeightForWidth())
        self.tblViewMessage.setSizePolicy(sizePolicy2)
        self.tblViewMessage.setAlternatingRowColors(True)
        self.tblViewMessage.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tblViewMessage.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tblViewMessage.setShowGrid(False)
        self.tblViewMessage.horizontalHeader().setHighlightSections(False)
        self.tblViewMessage.verticalHeader().setHighlightSections(False)

        self.verticalLayout_6.addWidget(self.tblViewMessage)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.lNumSelectedColumns = QLabel(self.tab_2)
        self.lNumSelectedColumns.setObjectName(u"lNumSelectedColumns")
        self.lNumSelectedColumns.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.lNumSelectedColumns)

        self.lColumnsSelectedText = QLabel(self.tab_2)
        self.lColumnsSelectedText.setObjectName(u"lColumnsSelectedText")

        self.horizontalLayout_3.addWidget(self.lColumnsSelectedText)

        self.horizontalSpacer_4 = QSpacerItem(138, 33, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)

        self.label_5 = QLabel(self.tab_2)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_3.addWidget(self.label_5)

        self.cbViewType = QComboBox(self.tab_2)
        self.cbViewType.addItem(QString())
        self.cbViewType.addItem(QString())
        self.cbViewType.addItem(QString())
        self.cbViewType.setObjectName(u"cbViewType")

        self.horizontalLayout_3.addWidget(self.cbViewType)


        self.verticalLayout_6.addLayout(self.horizontalLayout_3)

        self.tabWidget.addTab(self.tab_2, QString())
        self.tabParticipants = QWidget()
        self.tabParticipants.setObjectName(u"tabParticipants")
        self.horizontalLayout = QHBoxLayout(self.tabParticipants)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.tableViewParticipants = ParticipantTableView(self.tabParticipants)
        self.tableViewParticipants.setObjectName(u"tableViewParticipants")

        self.horizontalLayout.addWidget(self.tableViewParticipants)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.btnAddParticipant = QToolButton(self.tabParticipants)
        self.btnAddParticipant.setObjectName(u"btnAddParticipant")
        icon1 = QIcon()
        iconThemeName = u"list-add"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnAddParticipant.setIcon(icon1)

        self.verticalLayout_9.addWidget(self.btnAddParticipant)

        self.btnRemoveParticipant = QToolButton(self.tabParticipants)
        self.btnRemoveParticipant.setObjectName(u"btnRemoveParticipant")
        icon2 = QIcon()
        iconThemeName = u"list-remove"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnRemoveParticipant.setIcon(icon2)

        self.verticalLayout_9.addWidget(self.btnRemoveParticipant)

        self.btnUp = QToolButton(self.tabParticipants)
        self.btnUp.setObjectName(u"btnUp")
        icon3 = QIcon()
        iconThemeName = u"go-up"
        if QIcon.hasThemeIcon(iconThemeName):
            icon3 = QIcon.fromTheme(iconThemeName)
        else:
            icon3.addFile(u"../../../../", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnUp.setIcon(icon3)

        self.verticalLayout_9.addWidget(self.btnUp)

        self.btnDown = QToolButton(self.tabParticipants)
        self.btnDown.setObjectName(u"btnDown")
        icon4 = QIcon()
        iconThemeName = u"go-down"
        if QIcon.hasThemeIcon(iconThemeName):
            icon4 = QIcon.fromTheme(iconThemeName)
        else:
            icon4.addFile(u"../../../../", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnDown.setIcon(icon4)

        self.verticalLayout_9.addWidget(self.btnDown)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_9.addItem(self.verticalSpacer)


        self.horizontalLayout.addLayout(self.verticalLayout_9)

        self.tabWidget.addTab(self.tabParticipants, QString())

        self.verticalLayout_2.addWidget(self.tabWidget)

        self.splitter.addWidget(self.layoutWidget_2)
        self.layoutWidget_3 = QWidget(self.splitter)
        self.layoutWidget_3.setObjectName(u"layoutWidget_3")
        self.verticalLayout_4 = QVBoxLayout(self.layoutWidget_3)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(11, 11, 11, 11)
        self.lblMsgFieldsValues = QLabel(self.layoutWidget_3)
        self.lblMsgFieldsValues.setObjectName(u"lblMsgFieldsValues")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lblMsgFieldsValues.sizePolicy().hasHeightForWidth())
        self.lblMsgFieldsValues.setSizePolicy(sizePolicy3)
        font = QFont()
        font.setBold(True)
        font.setWeight(75);
        self.lblMsgFieldsValues.setFont(font)
        self.lblMsgFieldsValues.setAlignment(Qt.AlignCenter)

        self.verticalLayout_4.addWidget(self.lblMsgFieldsValues)

        self.detail_view_widget = QStackedWidget(self.layoutWidget_3)
        self.detail_view_widget.setObjectName(u"detail_view_widget")
        self.page_empty = QWidget()
        self.page_empty.setObjectName(u"page_empty")
        self.detail_view_widget.addWidget(self.page_empty)
        self.page_goto_action = QWidget()
        self.page_goto_action.setObjectName(u"page_goto_action")
        self.verticalLayout_7 = QGridLayout(self.page_goto_action)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label_9 = QLabel(self.page_goto_action)
        self.label_9.setObjectName(u"label_9")

        self.verticalLayout_7.addWidget(self.label_9, 0, 0, 1, 1)

        self.goto_combobox = QComboBox(self.page_goto_action)
        self.goto_combobox.setObjectName(u"goto_combobox")

        self.verticalLayout_7.addWidget(self.goto_combobox, 0, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.verticalLayout_7.addItem(self.horizontalSpacer, 0, 2, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer_4, 1, 0, 1, 3)

        self.detail_view_widget.addWidget(self.page_goto_action)
        self.page_message = QWidget()
        self.page_message.setObjectName(u"page_message")
        self.gridLayout_6 = QGridLayout(self.page_message)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label_10 = QLabel(self.page_message)
        self.label_10.setObjectName(u"label_10")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy4)

        self.gridLayout_6.addWidget(self.label_10, 1, 0, 1, 1)

        self.tblViewFieldValues = SimulatorLabelTableView(self.page_message)
        self.tblViewFieldValues.setObjectName(u"tblViewFieldValues")
        self.tblViewFieldValues.setAlternatingRowColors(True)
        self.tblViewFieldValues.setShowGrid(False)
        self.tblViewFieldValues.horizontalHeader().setDefaultSectionSize(150)
        self.tblViewFieldValues.horizontalHeader().setStretchLastSection(True)
        self.tblViewFieldValues.verticalHeader().setVisible(False)

        self.gridLayout_6.addWidget(self.tblViewFieldValues, 2, 2, 1, 1)

        self.label_11 = QLabel(self.page_message)
        self.label_11.setObjectName(u"label_11")
        sizePolicy4.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy4)
        self.label_11.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.gridLayout_6.addWidget(self.label_11, 2, 0, 1, 1)

        self.spinBoxRepeat = QSpinBox(self.page_message)
        self.spinBoxRepeat.setObjectName(u"spinBoxRepeat")
        self.spinBoxRepeat.setMinimum(1)

        self.gridLayout_6.addWidget(self.spinBoxRepeat, 1, 2, 1, 1)

        self.label_2 = QLabel(self.page_message)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_6.addWidget(self.label_2, 0, 0, 1, 1)

        self.lblEncodingDecoding = QLabel(self.page_message)
        self.lblEncodingDecoding.setObjectName(u"lblEncodingDecoding")

        self.gridLayout_6.addWidget(self.lblEncodingDecoding, 0, 2, 1, 1)

        self.detail_view_widget.addWidget(self.page_message)
        self.page_rule = QWidget()
        self.page_rule.setObjectName(u"page_rule")
        self.gridLayout_3 = QGridLayout(self.page_rule)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_12 = QLabel(self.page_rule)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_3.addWidget(self.label_12, 0, 0, 1, 1)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_5, 1, 0, 1, 2)

        self.ruleCondLineEdit = ExpressionLineEdit(self.page_rule)
        self.ruleCondLineEdit.setObjectName(u"ruleCondLineEdit")

        self.gridLayout_3.addWidget(self.ruleCondLineEdit, 0, 1, 1, 1)

        self.detail_view_widget.addWidget(self.page_rule)
        self.page_ext_prog_action = QWidget()
        self.page_ext_prog_action.setObjectName(u"page_ext_prog_action")
        self.gridLayout_9 = QGridLayout(self.page_ext_prog_action)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.checkBoxPassTranscriptSTDIN = QCheckBox(self.page_ext_prog_action)
        self.checkBoxPassTranscriptSTDIN.setObjectName(u"checkBoxPassTranscriptSTDIN")

        self.gridLayout_9.addWidget(self.checkBoxPassTranscriptSTDIN, 2, 0, 1, 4)

        self.label_14 = QLabel(self.page_ext_prog_action)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_9.addWidget(self.label_14, 1, 0, 1, 1)

        self.lineEditTriggerCommand = QLineEdit(self.page_ext_prog_action)
        self.lineEditTriggerCommand.setObjectName(u"lineEditTriggerCommand")
        self.lineEditTriggerCommand.setReadOnly(False)

        self.gridLayout_9.addWidget(self.lineEditTriggerCommand, 1, 1, 1, 1)

        self.btnChooseCommand = QToolButton(self.page_ext_prog_action)
        self.btnChooseCommand.setObjectName(u"btnChooseCommand")

        self.gridLayout_9.addWidget(self.btnChooseCommand, 1, 2, 1, 2)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_9.addItem(self.verticalSpacer_6, 4, 0, 1, 4)

        self.label_18 = QLabel(self.page_ext_prog_action)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setWordWrap(True)

        self.gridLayout_9.addWidget(self.label_18, 3, 0, 1, 4)

        self.detail_view_widget.addWidget(self.page_ext_prog_action)
        self.page_sleep = QWidget()
        self.page_sleep.setObjectName(u"page_sleep")
        self.verticalLayout_10 = QVBoxLayout(self.page_sleep)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_13 = QLabel(self.page_sleep)
        self.label_13.setObjectName(u"label_13")

        self.horizontalLayout_2.addWidget(self.label_13)

        self.doubleSpinBoxSleep = QDoubleSpinBox(self.page_sleep)
        self.doubleSpinBoxSleep.setObjectName(u"doubleSpinBoxSleep")
        self.doubleSpinBoxSleep.setDecimals(6)
        self.doubleSpinBoxSleep.setMaximum(10000.000000000000000)
        self.doubleSpinBoxSleep.setValue(1.000000000000000)

        self.horizontalLayout_2.addWidget(self.doubleSpinBoxSleep)


        self.verticalLayout_10.addLayout(self.horizontalLayout_2)

        self.verticalSpacer_2 = QSpacerItem(20, 231, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer_2)

        self.detail_view_widget.addWidget(self.page_sleep)
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.verticalLayout_11 = QVBoxLayout(self.page)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.spinBoxCounterStep = QSpinBox(self.page)
        self.spinBoxCounterStep.setObjectName(u"spinBoxCounterStep")
        self.spinBoxCounterStep.setMinimum(1)
        self.spinBoxCounterStep.setMaximum(999999)

        self.gridLayout_2.addWidget(self.spinBoxCounterStep, 2, 1, 1, 1)

        self.label_15 = QLabel(self.page)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_2.addWidget(self.label_15, 1, 0, 1, 1)

        self.label_16 = QLabel(self.page)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_2.addWidget(self.label_16, 2, 0, 1, 1)

        self.spinBoxCounterStart = QSpinBox(self.page)
        self.spinBoxCounterStart.setObjectName(u"spinBoxCounterStart")
        self.spinBoxCounterStart.setMaximum(999999)

        self.gridLayout_2.addWidget(self.spinBoxCounterStart, 1, 1, 1, 1)


        self.verticalLayout_11.addLayout(self.gridLayout_2)

        self.label_17 = QLabel(self.page)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setWordWrap(True)

        self.verticalLayout_11.addWidget(self.label_17)

        self.verticalSpacer_3 = QSpacerItem(20, 36, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_11.addItem(self.verticalSpacer_3)

        self.detail_view_widget.addWidget(self.page)

        self.verticalLayout_4.addWidget(self.detail_view_widget)

        self.splitter.addWidget(self.layoutWidget_3)
        self.splitterLeftRight.addWidget(self.splitter)

        self.verticalLayout_5.addWidget(self.splitterLeftRight)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_8.addWidget(self.scrollArea)


        self.retranslateUi(SimulatorTab)

        self.tabWidget.setCurrentIndex(0)
        self.detail_view_widget.setCurrentIndex(2)

    # setupUi

    def retranslateUi(self, SimulatorTab):
        SimulatorTab.setWindowTitle(QCoreApplication.translate("SimulatorTab", u"Form", None))
        self.label.setText(QCoreApplication.translate("SimulatorTab", u"Protocols (Drag&Drop to Flow Graph):", None))
        self.label_6.setText(QCoreApplication.translate("SimulatorTab", u"Simulate these participants:", None))
        self.label_4.setText(QCoreApplication.translate("SimulatorTab", u"Repeat simulation this often:", None))
        self.spinBoxNRepeat.setSpecialValueText(QCoreApplication.translate("SimulatorTab", u"Infinite", None))
        self.label_3.setText(QCoreApplication.translate("SimulatorTab", u"Timeout:", None))
        self.spinBoxTimeout.setSuffix(QCoreApplication.translate("SimulatorTab", u"ms", None))
        self.label_7.setText(QCoreApplication.translate("SimulatorTab", u"In case of an overdue response:", None))
        self.comboBoxError.setItemText(0, QCoreApplication.translate("SimulatorTab", u"Resend last message", None))
        self.comboBoxError.setItemText(1, QCoreApplication.translate("SimulatorTab", u"Stop simulation", None))
        self.comboBoxError.setItemText(2, QCoreApplication.translate("SimulatorTab", u"Restart simulation", None))

        self.label_8.setText(QCoreApplication.translate("SimulatorTab", u"Maximum retries:", None))
        self.btnStartSim.setText(QCoreApplication.translate("SimulatorTab", u"Simulate...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("SimulatorTab", u"Flow Graph", None))
        self.lNumSelectedColumns.setText(QCoreApplication.translate("SimulatorTab", u"0", None))
        self.lColumnsSelectedText.setText(QCoreApplication.translate("SimulatorTab", u"column(s) selected", None))
        self.label_5.setText(QCoreApplication.translate("SimulatorTab", u"Viewtype:", None))
        self.cbViewType.setItemText(0, QCoreApplication.translate("SimulatorTab", u"Bit", None))
        self.cbViewType.setItemText(1, QCoreApplication.translate("SimulatorTab", u"Hex", None))
        self.cbViewType.setItemText(2, QCoreApplication.translate("SimulatorTab", u"ASCII", None))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("SimulatorTab", u"Messages", None))
#if QT_CONFIG(tooltip)
        self.btnAddParticipant.setToolTip(QCoreApplication.translate("SimulatorTab", u"Add participant", None))
#endif // QT_CONFIG(tooltip)
        self.btnAddParticipant.setText(QCoreApplication.translate("SimulatorTab", u"Add", None))
#if QT_CONFIG(tooltip)
        self.btnRemoveParticipant.setToolTip(QCoreApplication.translate("SimulatorTab", u"Remove participant", None))
#endif // QT_CONFIG(tooltip)
        self.btnRemoveParticipant.setText(QCoreApplication.translate("SimulatorTab", u"Remove", None))
#if QT_CONFIG(tooltip)
        self.btnUp.setToolTip(QCoreApplication.translate("SimulatorTab", u"Move selected participants up", None))
#endif // QT_CONFIG(tooltip)
        self.btnUp.setText(QCoreApplication.translate("SimulatorTab", u"...", None))
#if QT_CONFIG(tooltip)
        self.btnDown.setToolTip(QCoreApplication.translate("SimulatorTab", u"Move selected participants down", None))
#endif // QT_CONFIG(tooltip)
        self.btnDown.setText(QCoreApplication.translate("SimulatorTab", u"...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabParticipants), QCoreApplication.translate("SimulatorTab", u"Participants", None))
        self.lblMsgFieldsValues.setText(QCoreApplication.translate("SimulatorTab", u"Detail view for item", None))
        self.label_9.setText(QCoreApplication.translate("SimulatorTab", u"Goto:", None))
        self.label_10.setText(QCoreApplication.translate("SimulatorTab", u"Copies:", None))
        self.label_11.setText(QCoreApplication.translate("SimulatorTab", u"Labels:", None))
        self.label_2.setText(QCoreApplication.translate("SimulatorTab", u"Coding:", None))
        self.lblEncodingDecoding.setText(QCoreApplication.translate("SimulatorTab", u"-", None))
        self.label_12.setText(QCoreApplication.translate("SimulatorTab", u"Condition:", None))
        self.ruleCondLineEdit.setPlaceholderText(QCoreApplication.translate("SimulatorTab", u"not (item1.crc == 0b1010 and item2.length >=3)", None))
        self.checkBoxPassTranscriptSTDIN.setText(QCoreApplication.translate("SimulatorTab", u"Pass transcript to STDIN", None))
        self.label_14.setText(QCoreApplication.translate("SimulatorTab", u"Command:", None))
        self.lineEditTriggerCommand.setPlaceholderText(QCoreApplication.translate("SimulatorTab", u"Path [+arguments] to external command e.g. mail or sendsms", None))
        self.btnChooseCommand.setText(QCoreApplication.translate("SimulatorTab", u"...", None))
        self.label_18.setText(QCoreApplication.translate("SimulatorTab", u"<html><head/><body><p>You can access the return code of this item in formulas and rules using the item identifier followed by <span style=\" font-style:italic;\">.rc</span> e.g.<span style=\" font-style:italic;\"> item5.rc</span>.</p></body></html>", None))
        self.label_13.setText(QCoreApplication.translate("SimulatorTab", u"Sleep for:", None))
        self.doubleSpinBoxSleep.setSuffix(QCoreApplication.translate("SimulatorTab", u"s", None))
        self.label_15.setText(QCoreApplication.translate("SimulatorTab", u"Start:", None))
        self.label_16.setText(QCoreApplication.translate("SimulatorTab", u"Step:", None))
        self.label_17.setText(QCoreApplication.translate("SimulatorTab", u"<html><head/><body><p>This counter will increase by <span style=\" font-weight:600;\">step</span> each time it gets hit during simulation. It will preserve it's value during simulation repeats and retries. To reset all counters stop the simulation and start it again.</p><p>Access the value of this counter using item&lt;Number&gt;.counter_value in <span style=\" font-weight:600;\">Formulas</span> or as parameter in <span style=\" font-weight:600;\">external programs</span> e.g. <span style=\" font-style:italic;\">external_py -c item5.counter_value</span>. The value of this counter will be inserted during simulation time.</p></body></html>", None))
    # retranslateUi

