# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'send_recv.ui'
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

from urh.ui.views.LiveGraphicView import LiveGraphicView
from urh.ui.views.EditableGraphicView import EditableGraphicView

import urh.ui.urh_rc

class Ui_SendRecvDialog(object):
    def setupUi(self, SendRecvDialog):
        if SendRecvDialog.objectName():
            SendRecvDialog.setObjectName(u"SendRecvDialog")
        SendRecvDialog.setWindowModality(Qt.NonModal)
        SendRecvDialog.resize(1246, 1123)
        SendRecvDialog.setMouseTracking(False)
        self.verticalLayout = QVBoxLayout(SendRecvDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(SendRecvDialog)
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
        self.scrollArea = QScrollArea(self.splitter)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 621, 1101))
        self.verticalLayout_8 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.groupBox = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setStyleSheet(u"QGroupBox\n"
"{\n"
" border: none;\n"
"}")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.progressBarMessage = QProgressBar(self.groupBox)
        self.progressBarMessage.setObjectName(u"progressBarMessage")
        self.progressBarMessage.setValue(0)

        self.gridLayout_2.addWidget(self.progressBarMessage, 19, 0, 1, 1)

        self.labelCurrentMessage = QLabel(self.groupBox)
        self.labelCurrentMessage.setObjectName(u"labelCurrentMessage")

        self.gridLayout_2.addWidget(self.labelCurrentMessage, 18, 0, 1, 1)

        self.lReceiveBufferFullText = QLabel(self.groupBox)
        self.lReceiveBufferFullText.setObjectName(u"lReceiveBufferFullText")

        self.gridLayout_2.addWidget(self.lReceiveBufferFullText, 7, 0, 1, 1)

        self.progressBarSample = QProgressBar(self.groupBox)
        self.progressBarSample.setObjectName(u"progressBarSample")
        self.progressBarSample.setValue(0)

        self.gridLayout_2.addWidget(self.progressBarSample, 21, 0, 1, 1)

        self.lSamplesSentText = QLabel(self.groupBox)
        self.lSamplesSentText.setObjectName(u"lSamplesSentText")

        self.gridLayout_2.addWidget(self.lSamplesSentText, 20, 0, 1, 1)

        self.lTimeText = QLabel(self.groupBox)
        self.lTimeText.setObjectName(u"lTimeText")

        self.gridLayout_2.addWidget(self.lTimeText, 12, 0, 1, 1)

        self.lSamplesCapturedText = QLabel(self.groupBox)
        self.lSamplesCapturedText.setObjectName(u"lSamplesCapturedText")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lSamplesCapturedText.sizePolicy().hasHeightForWidth())
        self.lSamplesCapturedText.setSizePolicy(sizePolicy)

        self.gridLayout_2.addWidget(self.lSamplesCapturedText, 5, 0, 1, 1)

        self.lSignalSizeText = QLabel(self.groupBox)
        self.lSignalSizeText.setObjectName(u"lSignalSizeText")
        sizePolicy.setHeightForWidth(self.lSignalSizeText.sizePolicy().hasHeightForWidth())
        self.lSignalSizeText.setSizePolicy(sizePolicy)

        self.gridLayout_2.addWidget(self.lSignalSizeText, 9, 0, 1, 1)

        self.lSamplesCaptured = QLabel(self.groupBox)
        self.lSamplesCaptured.setObjectName(u"lSamplesCaptured")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lSamplesCaptured.sizePolicy().hasHeightForWidth())
        self.lSamplesCaptured.setSizePolicy(sizePolicy1)
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lSamplesCaptured.setFont(font)
        self.lSamplesCaptured.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.lSamplesCaptured, 6, 0, 1, 2)

        self.lTime = QLabel(self.groupBox)
        self.lTime.setObjectName(u"lTime")
        self.lTime.setFont(font)
        self.lTime.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.lTime, 15, 0, 1, 2)

        self.lSignalSize = QLabel(self.groupBox)
        self.lSignalSize.setObjectName(u"lSignalSize")
        sizePolicy1.setHeightForWidth(self.lSignalSize.sizePolicy().hasHeightForWidth())
        self.lSignalSize.setSizePolicy(sizePolicy1)
        self.lSignalSize.setFont(font)
        self.lSignalSize.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.lSignalSize, 11, 0, 1, 2)

        self.lblRepeatText = QLabel(self.groupBox)
        self.lblRepeatText.setObjectName(u"lblRepeatText")

        self.gridLayout_2.addWidget(self.lblRepeatText, 16, 0, 1, 1)

        self.lblCurrentRepeatValue = QLabel(self.groupBox)
        self.lblCurrentRepeatValue.setObjectName(u"lblCurrentRepeatValue")
        self.lblCurrentRepeatValue.setFont(font)
        self.lblCurrentRepeatValue.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.lblCurrentRepeatValue, 17, 0, 1, 1)

        self.labelReceiveBufferFull = QLabel(self.groupBox)
        self.labelReceiveBufferFull.setObjectName(u"labelReceiveBufferFull")
        sizePolicy1.setHeightForWidth(self.labelReceiveBufferFull.sizePolicy().hasHeightForWidth())
        self.labelReceiveBufferFull.setSizePolicy(sizePolicy1)
        self.labelReceiveBufferFull.setFont(font)
        self.labelReceiveBufferFull.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.labelReceiveBufferFull, 8, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.btnStart = QToolButton(self.groupBox)
        self.btnStart.setObjectName(u"btnStart")
        self.btnStart.setMinimumSize(QSize(64, 64))
        icon = QIcon()
        iconThemeName = u"media-record"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnStart.setIcon(icon)
        self.btnStart.setIconSize(QSize(32, 32))
        self.btnStart.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.horizontalLayout.addWidget(self.btnStart)

        self.btnStop = QToolButton(self.groupBox)
        self.btnStop.setObjectName(u"btnStop")
        self.btnStop.setMinimumSize(QSize(64, 64))
        icon1 = QIcon()
        iconThemeName = u"media-playback-stop"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnStop.setIcon(icon1)
        self.btnStop.setIconSize(QSize(32, 32))
        self.btnStop.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.horizontalLayout.addWidget(self.btnStop)

        self.btnSave = QToolButton(self.groupBox)
        self.btnSave.setObjectName(u"btnSave")
        self.btnSave.setMinimumSize(QSize(64, 64))
        icon2 = QIcon()
        iconThemeName = u"document-save"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnSave.setIcon(icon2)
        self.btnSave.setIconSize(QSize(32, 32))
        self.btnSave.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.horizontalLayout.addWidget(self.btnSave)

        self.btnClear = QToolButton(self.groupBox)
        self.btnClear.setObjectName(u"btnClear")
        self.btnClear.setMinimumSize(QSize(64, 64))
        icon3 = QIcon()
        iconThemeName = u"view-refresh"
        if QIcon.hasThemeIcon(iconThemeName):
            icon3 = QIcon.fromTheme(iconThemeName)
        else:
            icon3.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnClear.setIcon(icon3)
        self.btnClear.setIconSize(QSize(32, 32))
        self.btnClear.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.horizontalLayout.addWidget(self.btnClear)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 2)

        self.verticalSpacer_2 = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout_2.addItem(self.verticalSpacer_2, 2, 0, 1, 1)


        self.verticalLayout_8.addWidget(self.groupBox)

        self.txtEditErrors = QTextEdit(self.scrollAreaWidgetContents_2)
        self.txtEditErrors.setObjectName(u"txtEditErrors")
        self.txtEditErrors.setReadOnly(True)

        self.verticalLayout_8.addWidget(self.txtEditErrors)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents_2)
        self.splitter.addWidget(self.scrollArea)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.horizontalLayout_2 = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.layoutWidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page_receive = QWidget()
        self.page_receive.setObjectName(u"page_receive")
        self.verticalLayout_2 = QVBoxLayout(self.page_receive)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.graphicsViewReceive = LiveGraphicView(self.page_receive)
        self.graphicsViewReceive.setObjectName(u"graphicsViewReceive")
        self.graphicsViewReceive.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicsViewReceive.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.verticalLayout_2.addWidget(self.graphicsViewReceive)

        self.stackedWidget.addWidget(self.page_receive)
        self.page_send = QWidget()
        self.page_send.setObjectName(u"page_send")
        self.verticalLayout_3 = QVBoxLayout(self.page_send)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.graphicsViewSend = EditableGraphicView(self.page_send)
        self.graphicsViewSend.setObjectName(u"graphicsViewSend")
        self.graphicsViewSend.setMouseTracking(True)
        self.graphicsViewSend.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
        self.graphicsViewSend.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.graphicsViewSend.setResizeAnchor(QGraphicsView.NoAnchor)

        self.verticalLayout_3.addWidget(self.graphicsViewSend)

        self.label_7 = QLabel(self.page_send)
        self.label_7.setObjectName(u"label_7")
        font1 = QFont()
        font1.setItalic(True)
        self.label_7.setFont(font1)

        self.verticalLayout_3.addWidget(self.label_7)

        self.stackedWidget.addWidget(self.page_send)
        self.page_continuous_send = QWidget()
        self.page_continuous_send.setObjectName(u"page_continuous_send")
        self.verticalLayout_6 = QVBoxLayout(self.page_continuous_send)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.graphicsViewContinuousSend = LiveGraphicView(self.page_continuous_send)
        self.graphicsViewContinuousSend.setObjectName(u"graphicsViewContinuousSend")
        self.graphicsViewContinuousSend.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)

        self.verticalLayout_6.addWidget(self.graphicsViewContinuousSend)

        self.stackedWidget.addWidget(self.page_continuous_send)
        self.page_spectrum = QWidget()
        self.page_spectrum.setObjectName(u"page_spectrum")
        self.verticalLayout_7 = QVBoxLayout(self.page_spectrum)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.graphicsViewFFT = LiveGraphicView(self.page_spectrum)
        self.graphicsViewFFT.setObjectName(u"graphicsViewFFT")

        self.verticalLayout_7.addWidget(self.graphicsViewFFT)

        self.graphicsViewSpectrogram = QGraphicsView(self.page_spectrum)
        self.graphicsViewSpectrogram.setObjectName(u"graphicsViewSpectrogram")
        self.graphicsViewSpectrogram.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.graphicsViewSpectrogram.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicsViewSpectrogram.setRenderHints(QPainter.SmoothPixmapTransform|QPainter.TextAntialiasing)
        self.graphicsViewSpectrogram.setCacheMode(QGraphicsView.CacheNone)
        self.graphicsViewSpectrogram.setViewportUpdateMode(QGraphicsView.MinimalViewportUpdate)

        self.verticalLayout_7.addWidget(self.graphicsViewSpectrogram)

        self.verticalLayout_7.setStretch(0, 1)
        self.verticalLayout_7.setStretch(1, 1)
        self.stackedWidget.addWidget(self.page_spectrum)
        self.page_sniff = QWidget()
        self.page_sniff.setObjectName(u"page_sniff")
        self.verticalLayout_4 = QVBoxLayout(self.page_sniff)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.graphicsView_sniff_Preview = LiveGraphicView(self.page_sniff)
        self.graphicsView_sniff_Preview.setObjectName(u"graphicsView_sniff_Preview")

        self.verticalLayout_4.addWidget(self.graphicsView_sniff_Preview)

        self.txtEd_sniff_Preview = QPlainTextEdit(self.page_sniff)
        self.txtEd_sniff_Preview.setObjectName(u"txtEd_sniff_Preview")
        self.txtEd_sniff_Preview.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.txtEd_sniff_Preview.setReadOnly(True)
        self.txtEd_sniff_Preview.setMaximumBlockCount(100)

        self.verticalLayout_4.addWidget(self.txtEd_sniff_Preview)

        self.btnAccept = QPushButton(self.page_sniff)
        self.btnAccept.setObjectName(u"btnAccept")
        self.btnAccept.setAutoDefault(False)

        self.verticalLayout_4.addWidget(self.btnAccept)

        self.stackedWidget.addWidget(self.page_sniff)

        self.horizontalLayout_2.addWidget(self.stackedWidget)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_y_scale = QLabel(self.layoutWidget)
        self.label_y_scale.setObjectName(u"label_y_scale")

        self.verticalLayout_5.addWidget(self.label_y_scale)

        self.sliderYscale = QSlider(self.layoutWidget)
        self.sliderYscale.setObjectName(u"sliderYscale")
        self.sliderYscale.setMinimum(1)
        self.sliderYscale.setMaximum(1000)
        self.sliderYscale.setValue(1)
        self.sliderYscale.setOrientation(Qt.Vertical)
        self.sliderYscale.setTickInterval(1)

        self.verticalLayout_5.addWidget(self.sliderYscale)


        self.horizontalLayout_2.addLayout(self.verticalLayout_5)

        self.splitter.addWidget(self.layoutWidget)

        self.verticalLayout.addWidget(self.splitter)

        QWidget.setTabOrder(self.btnStart, self.btnStop)
        QWidget.setTabOrder(self.btnStop, self.btnSave)
        QWidget.setTabOrder(self.btnSave, self.btnClear)
        QWidget.setTabOrder(self.btnClear, self.txtEd_sniff_Preview)
        QWidget.setTabOrder(self.txtEd_sniff_Preview, self.sliderYscale)
        QWidget.setTabOrder(self.sliderYscale, self.txtEditErrors)
        QWidget.setTabOrder(self.txtEditErrors, self.graphicsViewSend)
        QWidget.setTabOrder(self.graphicsViewSend, self.graphicsViewReceive)
        QWidget.setTabOrder(self.graphicsViewReceive, self.btnAccept)

        self.retranslateUi(SendRecvDialog)

        self.stackedWidget.setCurrentIndex(4)

    # setupUi

    def retranslateUi(self, SendRecvDialog):
        SendRecvDialog.setWindowTitle(QCoreApplication.translate("SendRecvDialog", u"Record Signal", None))
        self.groupBox.setTitle("")
        self.progressBarMessage.setFormat(QCoreApplication.translate("SendRecvDialog", u"%v/%m", None))
        self.labelCurrentMessage.setText(QCoreApplication.translate("SendRecvDialog", u"Current message:", None))
        self.lReceiveBufferFullText.setText(QCoreApplication.translate("SendRecvDialog", u"Receive buffer full:", None))
        self.progressBarSample.setFormat(QCoreApplication.translate("SendRecvDialog", u"%v/%m", None))
        self.lSamplesSentText.setText(QCoreApplication.translate("SendRecvDialog", u"Current sample:", None))
        self.lTimeText.setText(QCoreApplication.translate("SendRecvDialog", u"Time (in seconds):", None))
        self.lSamplesCapturedText.setText(QCoreApplication.translate("SendRecvDialog", u"Samples captured:", None))
        self.lSignalSizeText.setText(QCoreApplication.translate("SendRecvDialog", u"Signal size (in MiB):", None))
        self.lSamplesCaptured.setText(QCoreApplication.translate("SendRecvDialog", u"0", None))
        self.lTime.setText(QCoreApplication.translate("SendRecvDialog", u"0", None))
        self.lSignalSize.setText(QCoreApplication.translate("SendRecvDialog", u"0", None))
        self.lblRepeatText.setText(QCoreApplication.translate("SendRecvDialog", u"Current iteration:", None))
        self.lblCurrentRepeatValue.setText(QCoreApplication.translate("SendRecvDialog", u"0", None))
        self.labelReceiveBufferFull.setText(QCoreApplication.translate("SendRecvDialog", u"0%", None))
#if QT_CONFIG(tooltip)
        self.btnStart.setToolTip(QCoreApplication.translate("SendRecvDialog", u"Record signal", None))
#endif // QT_CONFIG(tooltip)
        self.btnStart.setText(QCoreApplication.translate("SendRecvDialog", u"Start", None))
#if QT_CONFIG(tooltip)
        self.btnStop.setToolTip(QCoreApplication.translate("SendRecvDialog", u"Stop recording", None))
#endif // QT_CONFIG(tooltip)
        self.btnStop.setText(QCoreApplication.translate("SendRecvDialog", u"Stop", None))
        self.btnSave.setText(QCoreApplication.translate("SendRecvDialog", u"Save...", None))
#if QT_CONFIG(tooltip)
        self.btnClear.setToolTip(QCoreApplication.translate("SendRecvDialog", u"Clear", None))
#endif // QT_CONFIG(tooltip)
        self.btnClear.setText(QCoreApplication.translate("SendRecvDialog", u"Clear", None))
        self.label_7.setText(QCoreApplication.translate("SendRecvDialog", u"Hint: You can edit the raw signal before sending.", None))
#if QT_CONFIG(tooltip)
        self.btnAccept.setToolTip(QCoreApplication.translate("SendRecvDialog", u"<html><head/><body><p>Accept the sniffed data and load it into <span style=\" font-weight:600;\">Analysis</span> tab.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnAccept.setText(QCoreApplication.translate("SendRecvDialog", u"Accept data (Open in Analysis)", None))
        self.label_y_scale.setText(QCoreApplication.translate("SendRecvDialog", u"Y-Scale", None))
    # retranslateUi

