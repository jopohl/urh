# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'project.ui'
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

from urh.ui.views.ParticipantTableView import ParticipantTableView
from urh.ui.KillerDoubleSpinBox import KillerDoubleSpinBox


class Ui_ProjectDialog(object):
    def setupUi(self, ProjectDialog):
        if ProjectDialog.objectName():
            ProjectDialog.setObjectName(u"ProjectDialog")
        ProjectDialog.resize(803, 936)
        self.verticalLayout = QVBoxLayout(ProjectDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lNewProject = QLabel(ProjectDialog)
        self.lNewProject.setObjectName(u"lNewProject")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.lNewProject.setFont(font)

        self.verticalLayout.addWidget(self.lNewProject)

        self.lblName = QLabel(ProjectDialog)
        self.lblName.setObjectName(u"lblName")

        self.verticalLayout.addWidget(self.lblName)

        self.verticalSpacer_2 = QSpacerItem(17, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_5 = QLabel(ProjectDialog)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 3, 4, 1, 2)

        self.lineEdit_Path = QLineEdit(ProjectDialog)
        self.lineEdit_Path.setObjectName(u"lineEdit_Path")

        self.gridLayout.addWidget(self.lineEdit_Path, 0, 3, 1, 1)

        self.label_7 = QLabel(ProjectDialog)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 1, 0, 1, 2)

        self.lblNewPath = QLabel(ProjectDialog)
        self.lblNewPath.setObjectName(u"lblNewPath")

        self.gridLayout.addWidget(self.lblNewPath, 1, 3, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 57, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_3, 15, 4, 1, 2)

        self.txtEdDescription = QPlainTextEdit(ProjectDialog)
        self.txtEdDescription.setObjectName(u"txtEdDescription")

        self.gridLayout.addWidget(self.txtEdDescription, 10, 3, 1, 1)

        self.tblParticipants = ParticipantTableView(ProjectDialog)
        self.tblParticipants.setObjectName(u"tblParticipants")
        self.tblParticipants.setAlternatingRowColors(True)
        self.tblParticipants.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tblParticipants.horizontalHeader().setCascadingSectionResizes(False)
        self.tblParticipants.horizontalHeader().setDefaultSectionSize(100)
        self.tblParticipants.horizontalHeader().setStretchLastSection(True)
        self.tblParticipants.verticalHeader().setCascadingSectionResizes(True)
        self.tblParticipants.verticalHeader().setStretchLastSection(False)

        self.gridLayout.addWidget(self.tblParticipants, 11, 3, 5, 1)

        self.spinBoxBandwidth = KillerDoubleSpinBox(ProjectDialog)
        self.spinBoxBandwidth.setObjectName(u"spinBoxBandwidth")
        self.spinBoxBandwidth.setDecimals(3)
        self.spinBoxBandwidth.setMinimum(1.000000000000000)
        self.spinBoxBandwidth.setMaximum(999999999999.000000000000000)
        self.spinBoxBandwidth.setSingleStep(0.001000000000000)
        self.spinBoxBandwidth.setValue(1000000.000000000000000)

        self.gridLayout.addWidget(self.spinBoxBandwidth, 5, 3, 1, 1)

        self.label_3 = QLabel(ProjectDialog)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 2)

        self.spinBoxFreq = KillerDoubleSpinBox(ProjectDialog)
        self.spinBoxFreq.setObjectName(u"spinBoxFreq")
        self.spinBoxFreq.setDecimals(3)
        self.spinBoxFreq.setMinimum(0.010000000000000)
        self.spinBoxFreq.setMaximum(1000000000000.000000000000000)
        self.spinBoxFreq.setSingleStep(0.001000000000000)
        self.spinBoxFreq.setValue(433920000.000000000000000)

        self.gridLayout.addWidget(self.spinBoxFreq, 4, 3, 1, 1)

        self.spinBoxSampleRate = KillerDoubleSpinBox(ProjectDialog)
        self.spinBoxSampleRate.setObjectName(u"spinBoxSampleRate")
        self.spinBoxSampleRate.setDecimals(3)
        self.spinBoxSampleRate.setMinimum(0.010000000000000)
        self.spinBoxSampleRate.setMaximum(1000000000000.000000000000000)
        self.spinBoxSampleRate.setSingleStep(0.001000000000000)
        self.spinBoxSampleRate.setValue(1000000.000000000000000)

        self.gridLayout.addWidget(self.spinBoxSampleRate, 3, 3, 1, 1)

        self.lineEditBroadcastAddress = QLineEdit(ProjectDialog)
        self.lineEditBroadcastAddress.setObjectName(u"lineEditBroadcastAddress")

        self.gridLayout.addWidget(self.lineEditBroadcastAddress, 16, 3, 1, 1)

        self.line = QFrame(ProjectDialog)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line, 9, 0, 1, 6)

        self.label_10 = QLabel(ProjectDialog)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout.addWidget(self.label_10, 5, 0, 1, 2)

        self.btnAddParticipant = QToolButton(ProjectDialog)
        self.btnAddParticipant.setObjectName(u"btnAddParticipant")
        icon = QIcon()
        iconThemeName = u"list-add"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnAddParticipant.setIcon(icon)

        self.gridLayout.addWidget(self.btnAddParticipant, 11, 4, 1, 2)

        self.btnSelectPath = QToolButton(ProjectDialog)
        self.btnSelectPath.setObjectName(u"btnSelectPath")

        self.gridLayout.addWidget(self.btnSelectPath, 0, 4, 1, 2)

        self.line_2 = QFrame(ProjectDialog)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line_2, 2, 0, 1, 6)

        self.label_6 = QLabel(ProjectDialog)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 4, 4, 1, 2)

        self.label_2 = QLabel(ProjectDialog)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 2)

        self.label = QLabel(ProjectDialog)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.btnRemoveParticipant = QToolButton(ProjectDialog)
        self.btnRemoveParticipant.setObjectName(u"btnRemoveParticipant")
        icon1 = QIcon()
        iconThemeName = u"list-remove"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnRemoveParticipant.setIcon(icon1)

        self.gridLayout.addWidget(self.btnRemoveParticipant, 12, 4, 1, 2)

        self.spinBoxGain = QSpinBox(ProjectDialog)
        self.spinBoxGain.setObjectName(u"spinBoxGain")
        self.spinBoxGain.setMinimum(1)
        self.spinBoxGain.setValue(20)

        self.gridLayout.addWidget(self.spinBoxGain, 6, 3, 1, 1)

        self.label_4 = QLabel(ProjectDialog)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 16, 0, 1, 2)

        self.label_8 = QLabel(ProjectDialog)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_8, 10, 0, 1, 2)

        self.label_12 = QLabel(ProjectDialog)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout.addWidget(self.label_12, 5, 4, 1, 2)

        self.label_11 = QLabel(ProjectDialog)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout.addWidget(self.label_11, 6, 0, 1, 2)

        self.btnUp = QToolButton(ProjectDialog)
        self.btnUp.setObjectName(u"btnUp")
        icon2 = QIcon()
        iconThemeName = u"go-up"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnUp.setIcon(icon2)

        self.gridLayout.addWidget(self.btnUp, 13, 4, 1, 1)

        self.lOpenSpectrumAnalyzer = QLabel(ProjectDialog)
        self.lOpenSpectrumAnalyzer.setObjectName(u"lOpenSpectrumAnalyzer")
        self.lOpenSpectrumAnalyzer.setTextFormat(Qt.AutoText)
        self.lOpenSpectrumAnalyzer.setOpenExternalLinks(False)

        self.gridLayout.addWidget(self.lOpenSpectrumAnalyzer, 8, 0, 1, 4)

        self.label_9 = QLabel(ProjectDialog)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 11, 0, 5, 2)

        self.btnDown = QToolButton(ProjectDialog)
        self.btnDown.setObjectName(u"btnDown")
        icon3 = QIcon()
        iconThemeName = u"go-down"
        if QIcon.hasThemeIcon(iconThemeName):
            icon3 = QIcon.fromTheme(iconThemeName)
        else:
            icon3.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnDown.setIcon(icon3)

        self.gridLayout.addWidget(self.btnDown, 14, 4, 1, 1)

        self.buttonBox = QDialogButtonBox(ProjectDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 17, 3, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        QWidget.setTabOrder(self.lineEdit_Path, self.btnSelectPath)
        QWidget.setTabOrder(self.btnSelectPath, self.spinBoxSampleRate)
        QWidget.setTabOrder(self.spinBoxSampleRate, self.spinBoxFreq)
        QWidget.setTabOrder(self.spinBoxFreq, self.spinBoxBandwidth)
        QWidget.setTabOrder(self.spinBoxBandwidth, self.spinBoxGain)
        QWidget.setTabOrder(self.spinBoxGain, self.txtEdDescription)
        QWidget.setTabOrder(self.txtEdDescription, self.tblParticipants)
        QWidget.setTabOrder(self.tblParticipants, self.btnAddParticipant)
        QWidget.setTabOrder(self.btnAddParticipant, self.btnRemoveParticipant)
        QWidget.setTabOrder(self.btnRemoveParticipant, self.lineEditBroadcastAddress)

        self.retranslateUi(ProjectDialog)
    # setupUi

    def retranslateUi(self, ProjectDialog):
        ProjectDialog.setWindowTitle(QCoreApplication.translate("ProjectDialog", u"Create a new project", None))
        self.lNewProject.setText(QCoreApplication.translate("ProjectDialog", u"New Project", None))
        self.lblName.setText(QCoreApplication.translate("ProjectDialog", u"<Name>", None))
        self.label_5.setText(QCoreApplication.translate("ProjectDialog", u"Sps", None))
#if QT_CONFIG(statustip)
        self.lineEdit_Path.setStatusTip("")
#endif // QT_CONFIG(statustip)
        self.label_7.setText("")
        self.lblNewPath.setText(QCoreApplication.translate("ProjectDialog", u"<html><head/><body><p><span style=\" font-style:italic;\">Note: A new directory will be created.</span></p></body></html>", None))
        self.label_3.setText(QCoreApplication.translate("ProjectDialog", u"Default frequency:", None))
#if QT_CONFIG(tooltip)
        self.lineEditBroadcastAddress.setToolTip(QCoreApplication.translate("ProjectDialog", u"<html><head/><body><p>Enter the broadcast address of your protocol in <span style=\" font-weight:600;\">hex</span>. If you do not know what to enter here, just leave the default.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEditBroadcastAddress.setInputMask("")
        self.lineEditBroadcastAddress.setText(QCoreApplication.translate("ProjectDialog", u"ffff", None))
        self.label_10.setText(QCoreApplication.translate("ProjectDialog", u"Default bandwidth:", None))
#if QT_CONFIG(tooltip)
        self.btnAddParticipant.setToolTip(QCoreApplication.translate("ProjectDialog", u"Add participant", None))
#endif // QT_CONFIG(tooltip)
        self.btnAddParticipant.setText(QCoreApplication.translate("ProjectDialog", u"...", None))
        self.btnSelectPath.setText(QCoreApplication.translate("ProjectDialog", u"...", None))
        self.label_6.setText(QCoreApplication.translate("ProjectDialog", u"Hz", None))
        self.label_2.setText(QCoreApplication.translate("ProjectDialog", u"Default sample rate:", None))
        self.label.setText(QCoreApplication.translate("ProjectDialog", u"Choose a path:", None))
#if QT_CONFIG(tooltip)
        self.btnRemoveParticipant.setToolTip(QCoreApplication.translate("ProjectDialog", u"Remove participant", None))
#endif // QT_CONFIG(tooltip)
        self.btnRemoveParticipant.setText(QCoreApplication.translate("ProjectDialog", u"...", None))
        self.label_4.setText(QCoreApplication.translate("ProjectDialog", u"Broadcast address (hex):", None))
        self.label_8.setText(QCoreApplication.translate("ProjectDialog", u"Description:", None))
        self.label_12.setText(QCoreApplication.translate("ProjectDialog", u"Hz", None))
        self.label_11.setText(QCoreApplication.translate("ProjectDialog", u"Default gain:", None))
#if QT_CONFIG(tooltip)
        self.btnUp.setToolTip(QCoreApplication.translate("ProjectDialog", u"Move selected participants up", None))
#endif // QT_CONFIG(tooltip)
        self.btnUp.setText(QCoreApplication.translate("ProjectDialog", u"...", None))
        self.lOpenSpectrumAnalyzer.setText(QCoreApplication.translate("ProjectDialog", u"<html><head/><body><p>Tip: Open <a href=\"open_spectrum_analyzer\">spectrum analyzer</a> to find these values.</p></body></html>", None))
        self.label_9.setText(QCoreApplication.translate("ProjectDialog", u"Participants:", None))
#if QT_CONFIG(tooltip)
        self.btnDown.setToolTip(QCoreApplication.translate("ProjectDialog", u"Move selected participants down", None))
#endif // QT_CONFIG(tooltip)
        self.btnDown.setText(QCoreApplication.translate("ProjectDialog", u"...", None))
    # retranslateUi

