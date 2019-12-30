# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'decoding.ui'
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

import ZoomableGraphicView
import ListWidget

class Ui_Decoder(object):
    def setupUi(self, Decoder):
        if Decoder.objectName():
            Decoder.setObjectName(u"Decoder")
        Decoder.setWindowModality(Qt.WindowModal)
        Decoder.resize(1018, 590)
        Decoder.setModal(False)
        self.verticalLayout_4 = QVBoxLayout(Decoder)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.combobox_decodings = QComboBox(Decoder)
        self.combobox_decodings.addItem(QString())
        self.combobox_decodings.addItem(QString())
        self.combobox_decodings.setObjectName(u"combobox_decodings")

        self.horizontalLayout_2.addWidget(self.combobox_decodings)

        self.delete_decoding = QPushButton(Decoder)
        self.delete_decoding.setObjectName(u"delete_decoding")

        self.horizontalLayout_2.addWidget(self.delete_decoding)

        self.saveas = QPushButton(Decoder)
        self.saveas.setObjectName(u"saveas")

        self.horizontalLayout_2.addWidget(self.saveas)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)


        self.verticalLayout_4.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_8 = QLabel(Decoder)
        self.label_8.setObjectName(u"label_8")

        self.verticalLayout_2.addWidget(self.label_8)

        self.basefunctions = QListWidget(Decoder)
        self.basefunctions.setObjectName(u"basefunctions")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.basefunctions.sizePolicy().hasHeightForWidth())
        self.basefunctions.setSizePolicy(sizePolicy)
        self.basefunctions.setDragEnabled(True)
        self.basefunctions.setDragDropMode(QAbstractItemView.DragOnly)

        self.verticalLayout_2.addWidget(self.basefunctions)

        self.label_9 = QLabel(Decoder)
        self.label_9.setObjectName(u"label_9")

        self.verticalLayout_2.addWidget(self.label_9)

        self.additionalfunctions = QListWidget(Decoder)
        self.additionalfunctions.setObjectName(u"additionalfunctions")
        sizePolicy.setHeightForWidth(self.additionalfunctions.sizePolicy().hasHeightForWidth())
        self.additionalfunctions.setSizePolicy(sizePolicy)
        self.additionalfunctions.setDragEnabled(True)
        self.additionalfunctions.setDragDropMode(QAbstractItemView.DragOnly)

        self.verticalLayout_2.addWidget(self.additionalfunctions)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(Decoder)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75);
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label)

        self.decoderchain = ListWidget(Decoder)
        self.decoderchain.setObjectName(u"decoderchain")
        sizePolicy.setHeightForWidth(self.decoderchain.sizePolicy().hasHeightForWidth())
        self.decoderchain.setSizePolicy(sizePolicy)
        self.decoderchain.setAcceptDrops(True)
        self.decoderchain.setDragEnabled(True)
        self.decoderchain.setDragDropMode(QAbstractItemView.DragDrop)
        self.decoderchain.setDefaultDropAction(Qt.MoveAction)
        self.decoderchain.setTextElideMode(Qt.ElideMiddle)
        self.decoderchain.setResizeMode(QListView.Fixed)
        self.decoderchain.setViewMode(QListView.ListMode)

        self.verticalLayout.addWidget(self.decoderchain)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.gb_infoandoptions = QGroupBox(Decoder)
        self.gb_infoandoptions.setObjectName(u"gb_infoandoptions")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.gb_infoandoptions.sizePolicy().hasHeightForWidth())
        self.gb_infoandoptions.setSizePolicy(sizePolicy1)
        self.verticalLayout_5 = QVBoxLayout(self.gb_infoandoptions)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.info = QLabel(self.gb_infoandoptions)
        self.info.setObjectName(u"info")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.info.sizePolicy().hasHeightForWidth())
        self.info.setSizePolicy(sizePolicy2)
        font1 = QFont()
        font1.setItalic(True)
        self.info.setFont(font1)
        self.info.setTextFormat(Qt.PlainText)
        self.info.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.info.setWordWrap(True)

        self.verticalLayout_5.addWidget(self.info)

        self.optionWidget = QStackedWidget(self.gb_infoandoptions)
        self.optionWidget.setObjectName(u"optionWidget")
        sizePolicy1.setHeightForWidth(self.optionWidget.sizePolicy().hasHeightForWidth())
        self.optionWidget.setSizePolicy(sizePolicy1)
        self.page_empty = QWidget()
        self.page_empty.setObjectName(u"page_empty")
        self.optionWidget.addWidget(self.page_empty)
        self.page_redundancy = QWidget()
        self.page_redundancy.setObjectName(u"page_redundancy")
        self.multiple = QSpinBox(self.page_redundancy)
        self.multiple.setObjectName(u"multiple")
        self.multiple.setGeometry(QRect(0, 0, 56, 23))
        self.multiple.setMinimum(2)
        self.label_5 = QLabel(self.page_redundancy)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(60, 0, 171, 21))
        self.optionWidget.addWidget(self.page_redundancy)
        self.page_carrier = QWidget()
        self.page_carrier.setObjectName(u"page_carrier")
        self.carrier = QLineEdit(self.page_carrier)
        self.carrier.setObjectName(u"carrier")
        self.carrier.setGeometry(QRect(0, 0, 113, 23))
        self.label_6 = QLabel(self.page_carrier)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(120, 0, 171, 21))
        self.optionWidget.addWidget(self.page_carrier)
        self.page_substitution = QWidget()
        self.page_substitution.setObjectName(u"page_substitution")
        self.gridLayout = QGridLayout(self.page_substitution)
        self.gridLayout.setObjectName(u"gridLayout")
        self.substitution_rows = QSpinBox(self.page_substitution)
        self.substitution_rows.setObjectName(u"substitution_rows")
        self.substitution_rows.setMinimum(1)
        self.substitution_rows.setMaximum(1000)
        self.substitution_rows.setValue(4)

        self.gridLayout.addWidget(self.substitution_rows, 0, 0, 1, 1)

        self.label_10 = QLabel(self.page_substitution)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout.addWidget(self.label_10, 0, 1, 1, 1)

        self.substitution = QTableWidget(self.page_substitution)
        self.substitution.setObjectName(u"substitution")
        self.substitution.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.substitution.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.gridLayout.addWidget(self.substitution, 1, 0, 1, 2)

        self.optionWidget.addWidget(self.page_substitution)
        self.page_external = QWidget()
        self.page_external.setObjectName(u"page_external")
        self.verticalLayout_6 = QVBoxLayout(self.page_external)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_11 = QLabel(self.page_external)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout_3.addWidget(self.label_11)

        self.external_decoder = QLineEdit(self.page_external)
        self.external_decoder.setObjectName(u"external_decoder")

        self.horizontalLayout_3.addWidget(self.external_decoder)

        self.btnChooseDecoder = QToolButton(self.page_external)
        self.btnChooseDecoder.setObjectName(u"btnChooseDecoder")

        self.horizontalLayout_3.addWidget(self.btnChooseDecoder)


        self.verticalLayout_6.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_12 = QLabel(self.page_external)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout_4.addWidget(self.label_12)

        self.external_encoder = QLineEdit(self.page_external)
        self.external_encoder.setObjectName(u"external_encoder")

        self.horizontalLayout_4.addWidget(self.external_encoder)

        self.btnChooseEncoder = QToolButton(self.page_external)
        self.btnChooseEncoder.setObjectName(u"btnChooseEncoder")

        self.horizontalLayout_4.addWidget(self.btnChooseEncoder)


        self.verticalLayout_6.addLayout(self.horizontalLayout_4)

        self.verticalSpacer = QSpacerItem(20, 158, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer)

        self.optionWidget.addWidget(self.page_external)
        self.page_data_whitening = QWidget()
        self.page_data_whitening.setObjectName(u"page_data_whitening")
        self.datawhitening_sync = QLineEdit(self.page_data_whitening)
        self.datawhitening_sync.setObjectName(u"datawhitening_sync")
        self.datawhitening_sync.setGeometry(QRect(0, 0, 171, 23))
        self.label_13 = QLabel(self.page_data_whitening)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(180, 0, 231, 20))
        self.datawhitening_polynomial = QLineEdit(self.page_data_whitening)
        self.datawhitening_polynomial.setObjectName(u"datawhitening_polynomial")
        self.datawhitening_polynomial.setGeometry(QRect(0, 30, 171, 23))
        self.label_14 = QLabel(self.page_data_whitening)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setGeometry(QRect(180, 30, 341, 21))
        self.datawhitening_overwrite_crc = QCheckBox(self.page_data_whitening)
        self.datawhitening_overwrite_crc.setObjectName(u"datawhitening_overwrite_crc")
        self.datawhitening_overwrite_crc.setGeometry(QRect(0, 60, 491, 20))
        self.optionWidget.addWidget(self.page_data_whitening)
        self.page_cut = QWidget()
        self.page_cut.setObjectName(u"page_cut")
        self.cutmark = QLineEdit(self.page_cut)
        self.cutmark.setObjectName(u"cutmark")
        self.cutmark.setGeometry(QRect(0, 30, 181, 31))
        self.label_15 = QLabel(self.page_cut)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setGeometry(QRect(190, 30, 121, 31))
        self.rB_delbefore = QRadioButton(self.page_cut)
        self.rB_delbefore.setObjectName(u"rB_delbefore")
        self.rB_delbefore.setGeometry(QRect(0, 0, 131, 23))
        self.rB_delafter = QRadioButton(self.page_cut)
        self.rB_delafter.setObjectName(u"rB_delafter")
        self.rB_delafter.setGeometry(QRect(150, 0, 111, 23))
        self.rB_delbeforepos = QRadioButton(self.page_cut)
        self.rB_delbeforepos.setObjectName(u"rB_delbeforepos")
        self.rB_delbeforepos.setGeometry(QRect(0, 70, 111, 23))
        self.rB_delafterpos = QRadioButton(self.page_cut)
        self.rB_delafterpos.setObjectName(u"rB_delafterpos")
        self.rB_delafterpos.setGeometry(QRect(150, 70, 111, 23))
        self.cutmark2 = QSpinBox(self.page_cut)
        self.cutmark2.setObjectName(u"cutmark2")
        self.cutmark2.setGeometry(QRect(0, 100, 181, 33))
        self.cutmark2.setMaximum(1000)
        self.label_16 = QLabel(self.page_cut)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setGeometry(QRect(190, 100, 121, 31))
        self.optionWidget.addWidget(self.page_cut)
        self.page_morse = QWidget()
        self.page_morse.setObjectName(u"page_morse")
        self.label_17 = QLabel(self.page_morse)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setGeometry(QRect(70, 10, 341, 21))
        self.morse_low = QSpinBox(self.page_morse)
        self.morse_low.setObjectName(u"morse_low")
        self.morse_low.setGeometry(QRect(10, 10, 56, 23))
        self.morse_low.setMinimum(1)
        self.morse_low.setValue(1)
        self.label_18 = QLabel(self.page_morse)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setGeometry(QRect(70, 40, 351, 21))
        self.morse_high = QSpinBox(self.page_morse)
        self.morse_high.setObjectName(u"morse_high")
        self.morse_high.setGeometry(QRect(10, 40, 56, 23))
        self.morse_high.setMinimum(1)
        self.morse_high.setValue(3)
        self.label_19 = QLabel(self.page_morse)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setGeometry(QRect(70, 70, 371, 21))
        self.morse_wait = QSpinBox(self.page_morse)
        self.morse_wait.setObjectName(u"morse_wait")
        self.morse_wait.setGeometry(QRect(10, 70, 56, 23))
        self.morse_wait.setMinimum(1)
        self.morse_wait.setValue(1)
        self.optionWidget.addWidget(self.page_morse)

        self.verticalLayout_5.addWidget(self.optionWidget)

        self.btnAddtoYourDecoding = QPushButton(self.gb_infoandoptions)
        self.btnAddtoYourDecoding.setObjectName(u"btnAddtoYourDecoding")

        self.verticalLayout_5.addWidget(self.btnAddtoYourDecoding)

        self.optionWidget.raise()
        self.info.raise()
        self.btnAddtoYourDecoding.raise()

        self.verticalLayout_3.addWidget(self.gb_infoandoptions)


        self.horizontalLayout.addLayout(self.verticalLayout_3)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_5, 0, 1, 1, 1)

        self.inpt = QLineEdit(Decoder)
        self.inpt.setObjectName(u"inpt")
        self.inpt.setInputMethodHints(Qt.ImhDigitsOnly)

        self.gridLayout_2.addWidget(self.inpt, 1, 1, 1, 1)

        self.combobox_signals = QComboBox(Decoder)
        self.combobox_signals.addItem(QString())
        self.combobox_signals.setObjectName(u"combobox_signals")

        self.gridLayout_2.addWidget(self.combobox_signals, 1, 0, 1, 1)

        self.graphicsView_signal = ZoomableGraphicView(Decoder)
        self.graphicsView_signal.setObjectName(u"graphicsView_signal")

        self.gridLayout_2.addWidget(self.graphicsView_signal, 4, 0, 1, 2)

        self.label_2 = QLabel(Decoder)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)

        self.graphicsView_decoded = ZoomableGraphicView(Decoder)
        self.graphicsView_decoded.setObjectName(u"graphicsView_decoded")

        self.gridLayout_2.addWidget(self.graphicsView_decoded, 5, 0, 1, 2)

        self.output = QLineEdit(Decoder)
        self.output.setObjectName(u"output")
        self.output.setReadOnly(True)

        self.gridLayout_2.addWidget(self.output, 3, 1, 1, 1)

        self.label_3 = QLabel(Decoder)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 3, 0, 1, 1)


        self.verticalLayout_4.addLayout(self.gridLayout_2)

        self.decoding_errors_label = QLabel(Decoder)
        self.decoding_errors_label.setObjectName(u"decoding_errors_label")
        self.decoding_errors_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.verticalLayout_4.addWidget(self.decoding_errors_label)


        self.retranslateUi(Decoder)

        self.optionWidget.setCurrentIndex(5)

    # setupUi

    def retranslateUi(self, Decoder):
        Decoder.setWindowTitle(QCoreApplication.translate("Decoder", u"Decoding", None))
        self.combobox_decodings.setItemText(0, QCoreApplication.translate("Decoder", u"Non Return to Zero (NRZ)", None))
        self.combobox_decodings.setItemText(1, QCoreApplication.translate("Decoder", u"Empty", None))

        self.delete_decoding.setText(QCoreApplication.translate("Decoder", u"Delete", None))
        self.saveas.setText(QCoreApplication.translate("Decoder", u"Save as...", None))
        self.label_8.setText(QCoreApplication.translate("Decoder", u"Base Functions", None))
        self.label_9.setText(QCoreApplication.translate("Decoder", u"Additional Functions", None))
        self.label.setText(QCoreApplication.translate("Decoder", u"Your Decoding", None))
        self.gb_infoandoptions.setTitle(QCoreApplication.translate("Decoder", u"Information and Options", None))
        self.info.setText(QCoreApplication.translate("Decoder", u"Please drag functions from the categories base and additional to the decoding process (Decoder). You can reorder functions by drag and drop and remove functions by dropping them outside the Decoder box. Click on every function for detailed information.", None))
        self.label_5.setText(QCoreApplication.translate("Decoder", u"Number of redundant bits", None))
        self.label_6.setText(QCoreApplication.translate("Decoder", u"Carrier ('1_' -> 1_1_1_...)", None))
        self.label_10.setText(QCoreApplication.translate("Decoder", u"Rows", None))
        self.label_11.setText(QCoreApplication.translate("Decoder", u"Decoder", None))
        self.btnChooseDecoder.setText(QCoreApplication.translate("Decoder", u"...", None))
        self.label_12.setText(QCoreApplication.translate("Decoder", u"Encoder", None))
        self.btnChooseEncoder.setText(QCoreApplication.translate("Decoder", u"...", None))
        self.label_13.setText(QCoreApplication.translate("Decoder", u"Synchronization bytes (hex coded)", None))
        self.label_14.setText(QCoreApplication.translate("Decoder", u"Data whitening polynomial (LFSR, hex, w/o first bit)", None))
        self.datawhitening_overwrite_crc.setText(QCoreApplication.translate("Decoder", u"Overwrite CRC16 field with correct value when encoding", None))
        self.cutmark.setText(QCoreApplication.translate("Decoder", u"1010", None))
        self.label_15.setText(QCoreApplication.translate("Decoder", u"Sequence", None))
        self.rB_delbefore.setText(QCoreApplication.translate("Decoder", u"&Cut before", None))
        self.rB_delafter.setText(QCoreApplication.translate("Decoder", u"Cut afte&r", None))
        self.rB_delbeforepos.setText(QCoreApplication.translate("Decoder", u"Cut before", None))
        self.rB_delafterpos.setText(QCoreApplication.translate("Decoder", u"Cut after", None))
        self.label_16.setText(QCoreApplication.translate("Decoder", u"Position (in bit)", None))
        self.label_17.setText(QCoreApplication.translate("Decoder", u"Maximum (<=) length of 1-sequence for: Low (0)", None))
        self.label_18.setText(QCoreApplication.translate("Decoder", u"Minimum (>=) length of 1-sequence for: High (1)", None))
        self.label_19.setText(QCoreApplication.translate("Decoder", u"Number of 0s between 1-sequences (just for encoding)", None))
        self.btnAddtoYourDecoding.setText(QCoreApplication.translate("Decoder", u"Add to Your Decoding", None))
        self.combobox_signals.setItemText(0, QCoreApplication.translate("Decoder", u"Test", None))

        self.label_2.setText(QCoreApplication.translate("Decoder", u"Signal {0,1}:", None))
        self.label_3.setText(QCoreApplication.translate("Decoder", u"Decoded Bits:", None))
        self.decoding_errors_label.setText(QCoreApplication.translate("Decoder", u"[Decoding Errors = 0]", None))
    # retranslateUi

