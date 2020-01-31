# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
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

from urh.ui.views.DirectoryTreeView import DirectoryTreeView

import urh.ui.urh_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(798, 469)
        icon = QIcon()
        icon.addFile(u":/icons/icons/appicon.png", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setTabShape(QTabWidget.Rounded)
        MainWindow.setDockNestingEnabled(False)
        self.actionFSK = QAction(MainWindow)
        self.actionFSK.setObjectName(u"actionFSK")
        self.actionFSK.setCheckable(True)
        self.actionOOK = QAction(MainWindow)
        self.actionOOK.setObjectName(u"actionOOK")
        self.actionOOK.setCheckable(True)
        self.actionOOK.setChecked(True)
        self.actionPSK = QAction(MainWindow)
        self.actionPSK.setObjectName(u"actionPSK")
        self.actionPSK.setCheckable(True)
        self.actionNone = QAction(MainWindow)
        self.actionNone.setObjectName(u"actionNone")
        self.actionNone.setCheckable(True)
        self.actionAuto_Fit_Y = QAction(MainWindow)
        self.actionAuto_Fit_Y.setObjectName(u"actionAuto_Fit_Y")
        self.actionAuto_Fit_Y.setCheckable(True)
        self.actionAuto_Fit_Y.setChecked(True)
        self.actionUndo = QAction(MainWindow)
        self.actionUndo.setObjectName(u"actionUndo")
        icon1 = QIcon()
        iconThemeName = u"edit-undo"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.actionUndo.setIcon(icon1)
        self.actionRedo = QAction(MainWindow)
        self.actionRedo.setObjectName(u"actionRedo")
        icon2 = QIcon()
        iconThemeName = u"edit-redo"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.actionRedo.setIcon(icon2)
        self.actionShow_Confirm_Close_Dialog = QAction(MainWindow)
        self.actionShow_Confirm_Close_Dialog.setObjectName(u"actionShow_Confirm_Close_Dialog")
        self.actionShow_Confirm_Close_Dialog.setCheckable(True)
        self.actionShow_Confirm_Close_Dialog.setChecked(False)
        self.actionTest = QAction(MainWindow)
        self.actionTest.setObjectName(u"actionTest")
        self.actionHold_Shift_to_Drag = QAction(MainWindow)
        self.actionHold_Shift_to_Drag.setObjectName(u"actionHold_Shift_to_Drag")
        self.actionHold_Shift_to_Drag.setCheckable(True)
        self.actionHold_Shift_to_Drag.setChecked(False)
        self.actionDocumentation = QAction(MainWindow)
        self.actionDocumentation.setObjectName(u"actionDocumentation")
        icon3 = QIcon()
        iconThemeName = u"help-contents"
        if QIcon.hasThemeIcon(iconThemeName):
            icon3 = QIcon.fromTheme(iconThemeName)
        else:
            icon3.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.actionDocumentation.setIcon(icon3)
        self.actionDocumentation.setIconVisibleInMenu(True)
        self.actionAbout_AutomaticHacker = QAction(MainWindow)
        self.actionAbout_AutomaticHacker.setObjectName(u"actionAbout_AutomaticHacker")
        icon4 = QIcon()
        iconThemeName = u"help-about"
        if QIcon.hasThemeIcon(iconThemeName):
            icon4 = QIcon.fromTheme(iconThemeName)
        else:
            icon4.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.actionAbout_AutomaticHacker.setIcon(icon4)
        self.actionAbout_AutomaticHacker.setIconVisibleInMenu(True)
        self.actionOpenSignal = QAction(MainWindow)
        self.actionOpenSignal.setObjectName(u"actionOpenSignal")
        self.actionOpenProtocol = QAction(MainWindow)
        self.actionOpenProtocol.setObjectName(u"actionOpenProtocol")
        self.actionShow_Compare_Frame = QAction(MainWindow)
        self.actionShow_Compare_Frame.setObjectName(u"actionShow_Compare_Frame")
        self.actionShow_Compare_Frame.setCheckable(True)
        self.actionShow_Compare_Frame.setChecked(True)
        self.actionCloseAllFiles = QAction(MainWindow)
        self.actionCloseAllFiles.setObjectName(u"actionCloseAllFiles")
        icon5 = QIcon()
        iconThemeName = u"window-close"
        if QIcon.hasThemeIcon(iconThemeName):
            icon5 = QIcon.fromTheme(iconThemeName)
        else:
            icon5.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.actionCloseAllFiles.setIcon(icon5)
        self.actionCloseAllFiles.setIconVisibleInMenu(True)
        self.actionSaveAllSignals = QAction(MainWindow)
        self.actionSaveAllSignals.setObjectName(u"actionSaveAllSignals")
        icon6 = QIcon()
        iconThemeName = u"document-save"
        if QIcon.hasThemeIcon(iconThemeName):
            icon6 = QIcon.fromTheme(iconThemeName)
        else:
            icon6.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.actionSaveAllSignals.setIcon(icon6)
        self.actionSaveAllSignals.setIconVisibleInMenu(True)
        self.actionSeperate_Protocols_in_Compare_Frame = QAction(MainWindow)
        self.actionSeperate_Protocols_in_Compare_Frame.setObjectName(u"actionSeperate_Protocols_in_Compare_Frame")
        self.actionSeperate_Protocols_in_Compare_Frame.setCheckable(True)
        self.actionSeperate_Protocols_in_Compare_Frame.setChecked(True)
        self.actionOpenArchive = QAction(MainWindow)
        self.actionOpenArchive.setObjectName(u"actionOpenArchive")
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        icon7 = QIcon()
        iconThemeName = u"document-open"
        if QIcon.hasThemeIcon(iconThemeName):
            icon7 = QIcon.fromTheme(iconThemeName)
        else:
            icon7.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.actionOpen.setIcon(icon7)
        self.actionOpen.setIconVisibleInMenu(True)
        self.actionOpen_Folder = QAction(MainWindow)
        self.actionOpen_Folder.setObjectName(u"actionOpen_Folder")
        icon8 = QIcon()
        iconThemeName = u"folder-open"
        if QIcon.hasThemeIcon(iconThemeName):
            icon8 = QIcon.fromTheme(iconThemeName)
        else:
            icon8.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.actionOpen_Folder.setIcon(icon8)
        self.actionShow_only_Compare_Frame = QAction(MainWindow)
        self.actionShow_only_Compare_Frame.setObjectName(u"actionShow_only_Compare_Frame")
        self.actionShow_only_Compare_Frame.setCheckable(True)
        self.actionShow_only_Compare_Frame.setChecked(True)
        self.actionConfigurePlugins = QAction(MainWindow)
        self.actionConfigurePlugins.setObjectName(u"actionConfigurePlugins")
        self.actionConfigurePlugins.setIconVisibleInMenu(True)
        self.actionSort_Frames_by_Name = QAction(MainWindow)
        self.actionSort_Frames_by_Name.setObjectName(u"actionSort_Frames_by_Name")
        self.actionConvert_Folder_to_Project = QAction(MainWindow)
        self.actionConvert_Folder_to_Project.setObjectName(u"actionConvert_Folder_to_Project")
        self.actionConvert_Folder_to_Project.setIconVisibleInMenu(True)
        self.actionDecoding = QAction(MainWindow)
        self.actionDecoding.setObjectName(u"actionDecoding")
        icon9 = QIcon()
        icon9.addFile(u":/icons/icons/decoding.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionDecoding.setIcon(icon9)
        self.actionRecord = QAction(MainWindow)
        self.actionRecord.setObjectName(u"actionRecord")
        icon10 = QIcon()
        iconThemeName = u"media-record"
        if QIcon.hasThemeIcon(iconThemeName):
            icon10 = QIcon.fromTheme(iconThemeName)
        else:
            icon10.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.actionRecord.setIcon(icon10)
        self.actionRecord.setIconVisibleInMenu(True)
        self.actionSpectrum_Analyzer = QAction(MainWindow)
        self.actionSpectrum_Analyzer.setObjectName(u"actionSpectrum_Analyzer")
        icon11 = QIcon()
        icon11.addFile(u":/icons/icons/spectrum.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionSpectrum_Analyzer.setIcon(icon11)
        self.actionSpectrum_Analyzer.setIconVisibleInMenu(True)
        self.actionOptions = QAction(MainWindow)
        self.actionOptions.setObjectName(u"actionOptions")
        icon12 = QIcon()
        iconThemeName = u"configure"
        if QIcon.hasThemeIcon(iconThemeName):
            icon12 = QIcon.fromTheme(iconThemeName)
        else:
            icon12.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.actionOptions.setIcon(icon12)
        self.actionOptions.setIconVisibleInMenu(True)
        self.actionNew_Project = QAction(MainWindow)
        self.actionNew_Project.setObjectName(u"actionNew_Project")
        icon13 = QIcon()
        iconThemeName = u"folder-new"
        if QIcon.hasThemeIcon(iconThemeName):
            icon13 = QIcon.fromTheme(iconThemeName)
        else:
            icon13.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.actionNew_Project.setIcon(icon13)
        self.actionSniff_protocol = QAction(MainWindow)
        self.actionSniff_protocol.setObjectName(u"actionSniff_protocol")
        icon14 = QIcon()
        icon14.addFile(u":/icons/icons/sniffer.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionSniff_protocol.setIcon(icon14)
        self.actionProject_settings = QAction(MainWindow)
        self.actionProject_settings.setObjectName(u"actionProject_settings")
        self.actionProject_settings.setIcon(icon12)
        self.actionSave_project = QAction(MainWindow)
        self.actionSave_project.setObjectName(u"actionSave_project")
        self.actionSave_project.setIcon(icon6)
        self.actionFullscreen_mode = QAction(MainWindow)
        self.actionFullscreen_mode.setObjectName(u"actionFullscreen_mode")
        self.actionFullscreen_mode.setCheckable(True)
        self.actionOpen_directory = QAction(MainWindow)
        self.actionOpen_directory.setObjectName(u"actionOpen_directory")
        self.actionOpen_directory.setIcon(icon8)
        self.actionAbout_Qt = QAction(MainWindow)
        self.actionAbout_Qt.setObjectName(u"actionAbout_Qt")
        self.actionShowFileTree = QAction(MainWindow)
        self.actionShowFileTree.setObjectName(u"actionShowFileTree")
        self.actionShowFileTree.setCheckable(True)
        self.actionSamples_from_csv = QAction(MainWindow)
        self.actionSamples_from_csv.setObjectName(u"actionSamples_from_csv")
        icon15 = QIcon()
        iconThemeName = u"text-csv"
        if QIcon.hasThemeIcon(iconThemeName):
            icon15 = QIcon.fromTheme(iconThemeName)
        else:
            icon15.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.actionSamples_from_csv.setIcon(icon15)
        self.actionClose_project = QAction(MainWindow)
        self.actionClose_project.setObjectName(u"actionClose_project")
        icon16 = QIcon()
        iconThemeName = u"document-close"
        if QIcon.hasThemeIcon(iconThemeName):
            icon16 = QIcon.fromTheme(iconThemeName)
        else:
            icon16.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.actionClose_project.setIcon(icon16)
        self.actionAuto_detect_new_signals = QAction(MainWindow)
        self.actionAuto_detect_new_signals.setObjectName(u"actionAuto_detect_new_signals")
        self.actionAuto_detect_new_signals.setCheckable(True)
        self.actionAuto_detect_new_signals.setChecked(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_4 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.splitter = QSplitter(self.centralwidget)
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
        self.verticalLayout_3 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_3.setSpacing(7)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(11, 11, 11, 0)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.lnEdtTreeFilter = QLineEdit(self.layoutWidget)
        self.lnEdtTreeFilter.setObjectName(u"lnEdtTreeFilter")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lnEdtTreeFilter.sizePolicy().hasHeightForWidth())
        self.lnEdtTreeFilter.setSizePolicy(sizePolicy)
        self.lnEdtTreeFilter.setAcceptDrops(False)
        self.lnEdtTreeFilter.setInputMethodHints(Qt.ImhDialableCharactersOnly)
        self.lnEdtTreeFilter.setClearButtonEnabled(True)

        self.horizontalLayout_3.addWidget(self.lnEdtTreeFilter)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.btnFileTreeGoUp = QToolButton(self.layoutWidget)
        self.btnFileTreeGoUp.setObjectName(u"btnFileTreeGoUp")
        icon17 = QIcon()
        iconThemeName = u"go-up"
        if QIcon.hasThemeIcon(iconThemeName):
            icon17 = QIcon.fromTheme(iconThemeName)
        else:
            icon17.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnFileTreeGoUp.setIcon(icon17)

        self.horizontalLayout_3.addWidget(self.btnFileTreeGoUp)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.fileTree = DirectoryTreeView(self.layoutWidget)
        self.fileTree.setObjectName(u"fileTree")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(10)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.fileTree.sizePolicy().hasHeightForWidth())
        self.fileTree.setSizePolicy(sizePolicy1)
        self.fileTree.setMaximumSize(QSize(16777215, 16777215))
        self.fileTree.setFrameShape(QFrame.StyledPanel)
        self.fileTree.setAutoScroll(True)
        self.fileTree.setDragEnabled(True)
        self.fileTree.setDragDropMode(QAbstractItemView.DragOnly)
        self.fileTree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.fileTree.setSortingEnabled(False)
        self.fileTree.header().setCascadingSectionResizes(True)
        self.fileTree.header().setStretchLastSection(False)

        self.verticalLayout_3.addWidget(self.fileTree)

        self.tabWidget_Project = QTabWidget(self.layoutWidget)
        self.tabWidget_Project.setObjectName(u"tabWidget_Project")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.tabWidget_Project.sizePolicy().hasHeightForWidth())
        self.tabWidget_Project.setSizePolicy(sizePolicy2)
        self.tabWidget_Project.setStyleSheet(u"QTabWidget::pane { border: 0; }")
        self.tabParticipants = QWidget()
        self.tabParticipants.setObjectName(u"tabParticipants")
        self.horizontalLayout = QHBoxLayout(self.tabParticipants)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.listViewParticipants = QListView(self.tabParticipants)
        self.listViewParticipants.setObjectName(u"listViewParticipants")
        self.listViewParticipants.setFrameShape(QFrame.StyledPanel)

        self.horizontalLayout.addWidget(self.listViewParticipants)

        self.tabWidget_Project.addTab(self.tabParticipants, "")
        self.tabDescription = QWidget()
        self.tabDescription.setObjectName(u"tabDescription")
        self.horizontalLayout_2 = QHBoxLayout(self.tabDescription)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.textEditProjectDescription = QTextEdit(self.tabDescription)
        self.textEditProjectDescription.setObjectName(u"textEditProjectDescription")

        self.horizontalLayout_2.addWidget(self.textEditProjectDescription)

        self.tabWidget_Project.addTab(self.tabDescription, "")

        self.verticalLayout_3.addWidget(self.tabWidget_Project)

        self.splitter.addWidget(self.layoutWidget)
        self.tabWidget = QTabWidget(self.splitter)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy3)
        self.tabWidget.setBaseSize(QSize(0, 0))
        self.tab_interpretation = QWidget()
        self.tab_interpretation.setObjectName(u"tab_interpretation")
        self.verticalLayout_2 = QVBoxLayout(self.tab_interpretation)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tabWidget.addTab(self.tab_interpretation, "")
        self.tab_protocol = QWidget()
        self.tab_protocol.setObjectName(u"tab_protocol")
        self.verticalLayout = QVBoxLayout(self.tab_protocol)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tabWidget.addTab(self.tab_protocol, "")
        self.tab_generator = QWidget()
        self.tab_generator.setObjectName(u"tab_generator")
        self.verticalLayout_5 = QVBoxLayout(self.tab_generator)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.tabWidget.addTab(self.tab_generator, "")
        self.tab_simulator = QWidget()
        self.tab_simulator.setObjectName(u"tab_simulator")
        self.verticalLayout_7 = QVBoxLayout(self.tab_simulator)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.tabWidget.addTab(self.tab_simulator, "")
        self.splitter.addWidget(self.tabWidget)

        self.verticalLayout_4.addWidget(self.splitter)

        self.labelNonProjectMode = QLabel(self.centralwidget)
        self.labelNonProjectMode.setObjectName(u"labelNonProjectMode")
        self.labelNonProjectMode.setStyleSheet(u"background: rgba(255,255,0,64)")
        self.labelNonProjectMode.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.labelNonProjectMode)

        self.verticalLayout_4.setStretch(0, 100)
        self.verticalLayout_4.setStretch(1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 798, 28))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuImport = QMenu(self.menuFile)
        self.menuImport.setObjectName(u"menuImport")
        icon18 = QIcon()
        iconThemeName = u"document-import"
        if QIcon.hasThemeIcon(iconThemeName):
            icon18 = QIcon.fromTheme(iconThemeName)
        else:
            icon18.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.menuImport.setIcon(icon18)
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionNew_Project)
        self.menuFile.addAction(self.actionProject_settings)
        self.menuFile.addAction(self.actionSave_project)
        self.menuFile.addAction(self.actionClose_project)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionOpen_directory)
        self.menuFile.addAction(self.menuImport.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSpectrum_Analyzer)
        self.menuFile.addAction(self.actionRecord)
        self.menuFile.addAction(self.actionSniff_protocol)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSaveAllSignals)
        self.menuFile.addAction(self.actionCloseAllFiles)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionConvert_Folder_to_Project)
        self.menuImport.addAction(self.actionSamples_from_csv)
        self.menuEdit.addAction(self.actionDecoding)
        self.menuEdit.addAction(self.actionOptions)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionShowFileTree)
        self.menuEdit.addAction(self.actionFullscreen_mode)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionAuto_detect_new_signals)
        self.menuHelp.addAction(self.actionAbout_AutomaticHacker)
        self.menuHelp.addAction(self.actionAbout_Qt)

        self.retranslateUi(MainWindow)

        self.tabWidget_Project.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(0)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Universal Radio Hacker", None))
        self.actionFSK.setText(QCoreApplication.translate("MainWindow", u"Undo", None))
        self.actionOOK.setText(QCoreApplication.translate("MainWindow", u"Redo", None))
        self.actionPSK.setText(QCoreApplication.translate("MainWindow", u"PSK", None))
        self.actionNone.setText(QCoreApplication.translate("MainWindow", u"None (bei .bin)", None))
        self.actionAuto_Fit_Y.setText(QCoreApplication.translate("MainWindow", u"&Auto Fit Y", None))
        self.actionUndo.setText(QCoreApplication.translate("MainWindow", u"&Undo", None))
        self.actionRedo.setText(QCoreApplication.translate("MainWindow", u"&Redo", None))
        self.actionShow_Confirm_Close_Dialog.setText(QCoreApplication.translate("MainWindow", u"&Show Confirm Close Dialog", None))
        self.actionTest.setText(QCoreApplication.translate("MainWindow", u"test", None))
        self.actionHold_Shift_to_Drag.setText(QCoreApplication.translate("MainWindow", u"&Hold Shift to Drag", None))
        self.actionDocumentation.setText(QCoreApplication.translate("MainWindow", u"&Documentation", None))
        self.actionAbout_AutomaticHacker.setText(QCoreApplication.translate("MainWindow", u"&About Universal Radio Hacker...", None))
        self.actionOpenSignal.setText(QCoreApplication.translate("MainWindow", u"&Signal", None))
        self.actionOpenProtocol.setText(QCoreApplication.translate("MainWindow", u"&Protocol", None))
        self.actionShow_Compare_Frame.setText(QCoreApplication.translate("MainWindow", u"Show &Compare Frame", None))
        self.actionCloseAllFiles.setText(QCoreApplication.translate("MainWindow", u"&Close all files", None))
        self.actionSaveAllSignals.setText(QCoreApplication.translate("MainWindow", u"&Save all signals", None))
        self.actionSeperate_Protocols_in_Compare_Frame.setText(QCoreApplication.translate("MainWindow", u"Seperate &Protocols in Compare Frame", None))
        self.actionOpenArchive.setText(QCoreApplication.translate("MainWindow", u"&Archive", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"&Open...", None))
        self.actionOpen_Folder.setText(QCoreApplication.translate("MainWindow", u"Open &Folder..", None))
        self.actionShow_only_Compare_Frame.setText(QCoreApplication.translate("MainWindow", u"Show Compare Frame only", None))
        self.actionConfigurePlugins.setText(QCoreApplication.translate("MainWindow", u"Configure...", None))
        self.actionSort_Frames_by_Name.setText(QCoreApplication.translate("MainWindow", u"Sort &Frames by Name", None))
        self.actionConvert_Folder_to_Project.setText(QCoreApplication.translate("MainWindow", u"Conv&ert Folder to Project", None))
        self.actionDecoding.setText(QCoreApplication.translate("MainWindow", u"&Decoding...", None))
        self.actionRecord.setText(QCoreApplication.translate("MainWindow", u"&Record signal...", None))
        self.actionSpectrum_Analyzer.setText(QCoreApplication.translate("MainWindow", u"Spectrum &Analyzer...", None))
        self.actionOptions.setText(QCoreApplication.translate("MainWindow", u"&Options...", None))
        self.actionNew_Project.setText(QCoreApplication.translate("MainWindow", u"&New Project..", None))
        self.actionSniff_protocol.setText(QCoreApplication.translate("MainWindow", u"Sn&iff protocol...", None))
        self.actionProject_settings.setText(QCoreApplication.translate("MainWindow", u"&Project settings...", None))
        self.actionSave_project.setText(QCoreApplication.translate("MainWindow", u"Sa&ve project", None))
        self.actionFullscreen_mode.setText(QCoreApplication.translate("MainWindow", u"&Fullscreen mode", None))
        self.actionOpen_directory.setText(QCoreApplication.translate("MainWindow", u"Open &folder...", None))
        self.actionAbout_Qt.setText(QCoreApplication.translate("MainWindow", u"About &Qt", None))
        self.actionShowFileTree.setText(QCoreApplication.translate("MainWindow", u"&Show file tree", None))
        self.actionSamples_from_csv.setText(QCoreApplication.translate("MainWindow", u"IQ samples from csv", None))
        self.actionClose_project.setText(QCoreApplication.translate("MainWindow", u"Close project", None))
        self.actionAuto_detect_new_signals.setText(QCoreApplication.translate("MainWindow", u"Auto detect signals on loading", None))
        self.lnEdtTreeFilter.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Filter", None))
        self.btnFileTreeGoUp.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.tabWidget_Project.setTabText(self.tabWidget_Project.indexOf(self.tabParticipants), QCoreApplication.translate("MainWindow", u"Participants", None))
        self.tabWidget_Project.setTabText(self.tabWidget_Project.indexOf(self.tabDescription), QCoreApplication.translate("MainWindow", u"Description", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_interpretation), QCoreApplication.translate("MainWindow", u"Interpretation", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_protocol), QCoreApplication.translate("MainWindow", u"Analysis", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_generator), QCoreApplication.translate("MainWindow", u"Generator", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_simulator), QCoreApplication.translate("MainWindow", u"Simulator", None))
        self.labelNonProjectMode.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Warning: You are running URH in non project mode. All your settings will be lost after closing the program. If you want to keep your settings create a project via File -&gt; <a href=\"open_new_project_dialog\"><span style=\" text-decoration: underline; color:#0000ff;\">New Project</span></a>. <a href=\"dont_show_non_project_again\"><span style=\" text-decoration: underline; color:#0000ff;\">Don't show this hint</span></a></p></body></html>", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"Fi&le", None))
        self.menuImport.setTitle(QCoreApplication.translate("MainWindow", u"Import", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edi&t", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Hel&p", None))
    # retranslateUi

