# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SendRecvDialog(object):
    def setupUi(self, SendRecvDialog):
        SendRecvDialog.setObjectName("SendRecvDialog")
        SendRecvDialog.setWindowModality(QtCore.Qt.NonModal)
        SendRecvDialog.resize(1246, 1123)
        SendRecvDialog.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(SendRecvDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(SendRecvDialog)
        self.splitter.setStyleSheet(
            "QSplitter::handle:horizontal {\n"
            "margin: 4px 0px;\n"
            "    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, \n"
            "stop:0 rgba(255, 255, 255, 0), \n"
            "stop:0.5 rgba(100, 100, 100, 100), \n"
            "stop:1 rgba(255, 255, 255, 0));\n"
            "image: url(:/icons/icons/splitter_handle_vertical.svg);\n"
            "}"
        )
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.scrollArea = QtWidgets.QScrollArea(self.splitter)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 621, 1101))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.groupBox = QtWidgets.QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox.setStyleSheet("QGroupBox\n" "{\n" " border: none;\n" "}")
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.progressBarMessage = QtWidgets.QProgressBar(self.groupBox)
        self.progressBarMessage.setProperty("value", 0)
        self.progressBarMessage.setObjectName("progressBarMessage")
        self.gridLayout_2.addWidget(self.progressBarMessage, 19, 0, 1, 1)
        self.labelCurrentMessage = QtWidgets.QLabel(self.groupBox)
        self.labelCurrentMessage.setObjectName("labelCurrentMessage")
        self.gridLayout_2.addWidget(self.labelCurrentMessage, 18, 0, 1, 1)
        self.lReceiveBufferFullText = QtWidgets.QLabel(self.groupBox)
        self.lReceiveBufferFullText.setObjectName("lReceiveBufferFullText")
        self.gridLayout_2.addWidget(self.lReceiveBufferFullText, 7, 0, 1, 1)
        self.progressBarSample = QtWidgets.QProgressBar(self.groupBox)
        self.progressBarSample.setProperty("value", 0)
        self.progressBarSample.setObjectName("progressBarSample")
        self.gridLayout_2.addWidget(self.progressBarSample, 21, 0, 1, 1)
        self.lSamplesSentText = QtWidgets.QLabel(self.groupBox)
        self.lSamplesSentText.setObjectName("lSamplesSentText")
        self.gridLayout_2.addWidget(self.lSamplesSentText, 20, 0, 1, 1)
        self.lTimeText = QtWidgets.QLabel(self.groupBox)
        self.lTimeText.setObjectName("lTimeText")
        self.gridLayout_2.addWidget(self.lTimeText, 12, 0, 1, 1)
        self.lSamplesCapturedText = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.lSamplesCapturedText.sizePolicy().hasHeightForWidth()
        )
        self.lSamplesCapturedText.setSizePolicy(sizePolicy)
        self.lSamplesCapturedText.setObjectName("lSamplesCapturedText")
        self.gridLayout_2.addWidget(self.lSamplesCapturedText, 5, 0, 1, 1)
        self.lSignalSizeText = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.lSignalSizeText.sizePolicy().hasHeightForWidth()
        )
        self.lSignalSizeText.setSizePolicy(sizePolicy)
        self.lSignalSizeText.setObjectName("lSignalSizeText")
        self.gridLayout_2.addWidget(self.lSignalSizeText, 9, 0, 1, 1)
        self.lSamplesCaptured = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.lSamplesCaptured.sizePolicy().hasHeightForWidth()
        )
        self.lSamplesCaptured.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lSamplesCaptured.setFont(font)
        self.lSamplesCaptured.setAlignment(QtCore.Qt.AlignCenter)
        self.lSamplesCaptured.setObjectName("lSamplesCaptured")
        self.gridLayout_2.addWidget(self.lSamplesCaptured, 6, 0, 1, 2)
        self.lTime = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lTime.setFont(font)
        self.lTime.setAlignment(QtCore.Qt.AlignCenter)
        self.lTime.setObjectName("lTime")
        self.gridLayout_2.addWidget(self.lTime, 15, 0, 1, 2)
        self.lSignalSize = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lSignalSize.sizePolicy().hasHeightForWidth())
        self.lSignalSize.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lSignalSize.setFont(font)
        self.lSignalSize.setAlignment(QtCore.Qt.AlignCenter)
        self.lSignalSize.setObjectName("lSignalSize")
        self.gridLayout_2.addWidget(self.lSignalSize, 11, 0, 1, 2)
        self.lblRepeatText = QtWidgets.QLabel(self.groupBox)
        self.lblRepeatText.setObjectName("lblRepeatText")
        self.gridLayout_2.addWidget(self.lblRepeatText, 16, 0, 1, 1)
        self.lblCurrentRepeatValue = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblCurrentRepeatValue.setFont(font)
        self.lblCurrentRepeatValue.setAlignment(QtCore.Qt.AlignCenter)
        self.lblCurrentRepeatValue.setObjectName("lblCurrentRepeatValue")
        self.gridLayout_2.addWidget(self.lblCurrentRepeatValue, 17, 0, 1, 1)
        self.labelReceiveBufferFull = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.labelReceiveBufferFull.sizePolicy().hasHeightForWidth()
        )
        self.labelReceiveBufferFull.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.labelReceiveBufferFull.setFont(font)
        self.labelReceiveBufferFull.setAlignment(QtCore.Qt.AlignCenter)
        self.labelReceiveBufferFull.setObjectName("labelReceiveBufferFull")
        self.gridLayout_2.addWidget(self.labelReceiveBufferFull, 8, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem)
        self.btnStart = QtWidgets.QToolButton(self.groupBox)
        self.btnStart.setMinimumSize(QtCore.QSize(64, 64))
        icon = QtGui.QIcon.fromTheme("media-record")
        self.btnStart.setIcon(icon)
        self.btnStart.setIconSize(QtCore.QSize(32, 32))
        self.btnStart.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.btnStart.setObjectName("btnStart")
        self.horizontalLayout.addWidget(self.btnStart)
        self.btnStop = QtWidgets.QToolButton(self.groupBox)
        self.btnStop.setMinimumSize(QtCore.QSize(64, 64))
        icon = QtGui.QIcon.fromTheme("media-playback-stop")
        self.btnStop.setIcon(icon)
        self.btnStop.setIconSize(QtCore.QSize(32, 32))
        self.btnStop.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.btnStop.setObjectName("btnStop")
        self.horizontalLayout.addWidget(self.btnStop)
        self.btnSave = QtWidgets.QToolButton(self.groupBox)
        self.btnSave.setMinimumSize(QtCore.QSize(64, 64))
        icon = QtGui.QIcon.fromTheme("document-save")
        self.btnSave.setIcon(icon)
        self.btnSave.setIconSize(QtCore.QSize(32, 32))
        self.btnSave.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.btnSave.setObjectName("btnSave")
        self.horizontalLayout.addWidget(self.btnSave)
        self.btnClear = QtWidgets.QToolButton(self.groupBox)
        self.btnClear.setMinimumSize(QtCore.QSize(64, 64))
        icon = QtGui.QIcon.fromTheme("view-refresh")
        self.btnClear.setIcon(icon)
        self.btnClear.setIconSize(QtCore.QSize(32, 32))
        self.btnClear.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.btnClear.setObjectName("btnClear")
        self.horizontalLayout.addWidget(self.btnClear)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem1)
        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 2)
        spacerItem2 = QtWidgets.QSpacerItem(
            20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        self.gridLayout_2.addItem(spacerItem2, 2, 0, 1, 1)
        self.verticalLayout_8.addWidget(self.groupBox)
        self.txtEditErrors = QtWidgets.QTextEdit(self.scrollAreaWidgetContents_2)
        self.txtEditErrors.setReadOnly(True)
        self.txtEditErrors.setObjectName("txtEditErrors")
        self.verticalLayout_8.addWidget(self.txtEditErrors)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_2)
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.stackedWidget = QtWidgets.QStackedWidget(self.layoutWidget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page_receive = QtWidgets.QWidget()
        self.page_receive.setObjectName("page_receive")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.page_receive)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.graphicsViewReceive = LiveGraphicView(self.page_receive)
        self.graphicsViewReceive.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )
        self.graphicsViewReceive.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded
        )
        self.graphicsViewReceive.setObjectName("graphicsViewReceive")
        self.verticalLayout_2.addWidget(self.graphicsViewReceive)
        self.stackedWidget.addWidget(self.page_receive)
        self.page_send = QtWidgets.QWidget()
        self.page_send.setObjectName("page_send")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.page_send)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.graphicsViewSend = EditableGraphicView(self.page_send)
        self.graphicsViewSend.setMouseTracking(True)
        self.graphicsViewSend.setRenderHints(
            QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing
        )
        self.graphicsViewSend.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.graphicsViewSend.setResizeAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.graphicsViewSend.setObjectName("graphicsViewSend")
        self.verticalLayout_3.addWidget(self.graphicsViewSend)
        self.label_7 = QtWidgets.QLabel(self.page_send)
        font = QtGui.QFont()
        font.setItalic(True)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_3.addWidget(self.label_7)
        self.stackedWidget.addWidget(self.page_send)
        self.page_continuous_send = QtWidgets.QWidget()
        self.page_continuous_send.setObjectName("page_continuous_send")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.page_continuous_send)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.graphicsViewContinuousSend = LiveGraphicView(self.page_continuous_send)
        self.graphicsViewContinuousSend.setRenderHints(
            QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing
        )
        self.graphicsViewContinuousSend.setObjectName("graphicsViewContinuousSend")
        self.verticalLayout_6.addWidget(self.graphicsViewContinuousSend)
        self.stackedWidget.addWidget(self.page_continuous_send)
        self.page_spectrum = QtWidgets.QWidget()
        self.page_spectrum.setObjectName("page_spectrum")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.page_spectrum)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.graphicsViewFFT = LiveGraphicView(self.page_spectrum)
        self.graphicsViewFFT.setObjectName("graphicsViewFFT")
        self.verticalLayout_7.addWidget(self.graphicsViewFFT)
        self.graphicsViewSpectrogram = QtWidgets.QGraphicsView(self.page_spectrum)
        self.graphicsViewSpectrogram.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded
        )
        self.graphicsViewSpectrogram.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )
        self.graphicsViewSpectrogram.setRenderHints(
            QtGui.QPainter.SmoothPixmapTransform | QtGui.QPainter.TextAntialiasing
        )
        self.graphicsViewSpectrogram.setCacheMode(QtWidgets.QGraphicsView.CacheNone)
        self.graphicsViewSpectrogram.setViewportUpdateMode(
            QtWidgets.QGraphicsView.MinimalViewportUpdate
        )
        self.graphicsViewSpectrogram.setObjectName("graphicsViewSpectrogram")
        self.verticalLayout_7.addWidget(self.graphicsViewSpectrogram)
        self.verticalLayout_7.setStretch(0, 1)
        self.verticalLayout_7.setStretch(1, 1)
        self.stackedWidget.addWidget(self.page_spectrum)
        self.page_sniff = QtWidgets.QWidget()
        self.page_sniff.setObjectName("page_sniff")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.page_sniff)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.graphicsView_sniff_Preview = LiveGraphicView(self.page_sniff)
        self.graphicsView_sniff_Preview.setObjectName("graphicsView_sniff_Preview")
        self.verticalLayout_4.addWidget(self.graphicsView_sniff_Preview)
        self.txtEd_sniff_Preview = QtWidgets.QPlainTextEdit(self.page_sniff)
        self.txtEd_sniff_Preview.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.txtEd_sniff_Preview.setReadOnly(True)
        self.txtEd_sniff_Preview.setMaximumBlockCount(100)
        self.txtEd_sniff_Preview.setObjectName("txtEd_sniff_Preview")
        self.verticalLayout_4.addWidget(self.txtEd_sniff_Preview)
        self.btnAccept = QtWidgets.QPushButton(self.page_sniff)
        self.btnAccept.setAutoDefault(False)
        self.btnAccept.setObjectName("btnAccept")
        self.verticalLayout_4.addWidget(self.btnAccept)
        self.stackedWidget.addWidget(self.page_sniff)
        self.horizontalLayout_2.addWidget(self.stackedWidget)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_y_scale = QtWidgets.QLabel(self.layoutWidget)
        self.label_y_scale.setObjectName("label_y_scale")
        self.verticalLayout_5.addWidget(self.label_y_scale)
        self.sliderYscale = QtWidgets.QSlider(self.layoutWidget)
        self.sliderYscale.setMinimum(1)
        self.sliderYscale.setMaximum(1000)
        self.sliderYscale.setProperty("value", 1)
        self.sliderYscale.setOrientation(QtCore.Qt.Vertical)
        self.sliderYscale.setTickInterval(1)
        self.sliderYscale.setObjectName("sliderYscale")
        self.verticalLayout_5.addWidget(self.sliderYscale)
        self.horizontalLayout_2.addLayout(self.verticalLayout_5)
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(SendRecvDialog)
        self.stackedWidget.setCurrentIndex(4)
        SendRecvDialog.setTabOrder(self.btnStart, self.btnStop)
        SendRecvDialog.setTabOrder(self.btnStop, self.btnSave)
        SendRecvDialog.setTabOrder(self.btnSave, self.btnClear)
        SendRecvDialog.setTabOrder(self.btnClear, self.txtEd_sniff_Preview)
        SendRecvDialog.setTabOrder(self.txtEd_sniff_Preview, self.sliderYscale)
        SendRecvDialog.setTabOrder(self.sliderYscale, self.txtEditErrors)
        SendRecvDialog.setTabOrder(self.txtEditErrors, self.graphicsViewSend)
        SendRecvDialog.setTabOrder(self.graphicsViewSend, self.graphicsViewReceive)
        SendRecvDialog.setTabOrder(self.graphicsViewReceive, self.btnAccept)

    def retranslateUi(self, SendRecvDialog):
        _translate = QtCore.QCoreApplication.translate
        SendRecvDialog.setWindowTitle(_translate("SendRecvDialog", "Record Signal"))
        self.progressBarMessage.setFormat(_translate("SendRecvDialog", "%v/%m"))
        self.labelCurrentMessage.setText(
            _translate("SendRecvDialog", "Current message:")
        )
        self.lReceiveBufferFullText.setText(
            _translate("SendRecvDialog", "Receive buffer full:")
        )
        self.progressBarSample.setFormat(_translate("SendRecvDialog", "%v/%m"))
        self.lSamplesSentText.setText(_translate("SendRecvDialog", "Current sample:"))
        self.lTimeText.setText(_translate("SendRecvDialog", "Time (in seconds):"))
        self.lSamplesCapturedText.setText(
            _translate("SendRecvDialog", "Samples captured:")
        )
        self.lSignalSizeText.setText(
            _translate("SendRecvDialog", "Signal size (in MiB):")
        )
        self.lSamplesCaptured.setText(_translate("SendRecvDialog", "0"))
        self.lTime.setText(_translate("SendRecvDialog", "0"))
        self.lSignalSize.setText(_translate("SendRecvDialog", "0"))
        self.lblRepeatText.setText(_translate("SendRecvDialog", "Current iteration:"))
        self.lblCurrentRepeatValue.setText(_translate("SendRecvDialog", "0"))
        self.labelReceiveBufferFull.setText(_translate("SendRecvDialog", "0%"))
        self.btnStart.setToolTip(_translate("SendRecvDialog", "Record signal"))
        self.btnStart.setText(_translate("SendRecvDialog", "Start"))
        self.btnStop.setToolTip(_translate("SendRecvDialog", "Stop recording"))
        self.btnStop.setText(_translate("SendRecvDialog", "Stop"))
        self.btnSave.setText(_translate("SendRecvDialog", "Save..."))
        self.btnClear.setToolTip(_translate("SendRecvDialog", "Clear"))
        self.btnClear.setText(_translate("SendRecvDialog", "Clear"))
        self.label_7.setText(
            _translate(
                "SendRecvDialog", "Hint: You can edit the raw signal before sending."
            )
        )
        self.btnAccept.setToolTip(
            _translate(
                "SendRecvDialog",
                '<html><head/><body><p>Accept the sniffed data and load it into <span style=" font-weight:600;">Analysis</span> tab.</p></body></html>',
            )
        )
        self.btnAccept.setText(
            _translate("SendRecvDialog", "Accept data (Open in Analysis)")
        )
        self.label_y_scale.setText(_translate("SendRecvDialog", "Y-Scale"))


from urh.ui.views.EditableGraphicView import EditableGraphicView
from urh.ui.views.LiveGraphicView import LiveGraphicView
from . import urh_rc
