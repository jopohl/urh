# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'filter_bandwidth_dialog.ui'
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

class Ui_DialogFilterBandwidth(object):
    def setupUi(self, DialogFilterBandwidth):
        if DialogFilterBandwidth.objectName():
            DialogFilterBandwidth.setObjectName(u"DialogFilterBandwidth")
        DialogFilterBandwidth.resize(502, 426)
        self.verticalLayout = QVBoxLayout(DialogFilterBandwidth)
        self.verticalLayout.setSpacing(7)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.labelExplanation = QLabel(DialogFilterBandwidth)
        self.labelExplanation.setObjectName(u"labelExplanation")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelExplanation.sizePolicy().hasHeightForWidth())
        self.labelExplanation.setSizePolicy(sizePolicy)
        self.labelExplanation.setAlignment(Qt.AlignJustify|Qt.AlignTop)
        self.labelExplanation.setWordWrap(True)

        self.verticalLayout.addWidget(self.labelExplanation)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.doubleSpinBoxCustomBandwidth = QDoubleSpinBox(DialogFilterBandwidth)
        self.doubleSpinBoxCustomBandwidth.setObjectName(u"doubleSpinBoxCustomBandwidth")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.doubleSpinBoxCustomBandwidth.sizePolicy().hasHeightForWidth())
        self.doubleSpinBoxCustomBandwidth.setSizePolicy(sizePolicy1)
        self.doubleSpinBoxCustomBandwidth.setDecimals(4)
        self.doubleSpinBoxCustomBandwidth.setMinimum(0.000100000000000)
        self.doubleSpinBoxCustomBandwidth.setMaximum(0.500000000000000)

        self.gridLayout.addWidget(self.doubleSpinBoxCustomBandwidth, 7, 1, 1, 1)

        self.spinBoxCustomKernelLength = QSpinBox(DialogFilterBandwidth)
        self.spinBoxCustomKernelLength.setObjectName(u"spinBoxCustomKernelLength")
        self.spinBoxCustomKernelLength.setMinimum(8)
        self.spinBoxCustomKernelLength.setMaximum(999999999)

        self.gridLayout.addWidget(self.spinBoxCustomKernelLength, 7, 2, 1, 1)

        self.radioButtonCustom = QRadioButton(DialogFilterBandwidth)
        self.radioButtonCustom.setObjectName(u"radioButtonCustom")

        self.gridLayout.addWidget(self.radioButtonCustom, 7, 0, 1, 1)

        self.labelMediumKernelLength = QLabel(DialogFilterBandwidth)
        self.labelMediumKernelLength.setObjectName(u"labelMediumKernelLength")

        self.gridLayout.addWidget(self.labelMediumKernelLength, 4, 2, 1, 1)

        self.radioButtonWide = QRadioButton(DialogFilterBandwidth)
        self.radioButtonWide.setObjectName(u"radioButtonWide")

        self.gridLayout.addWidget(self.radioButtonWide, 5, 0, 1, 1)

        self.labelVeryWideKernelLength = QLabel(DialogFilterBandwidth)
        self.labelVeryWideKernelLength.setObjectName(u"labelVeryWideKernelLength")

        self.gridLayout.addWidget(self.labelVeryWideKernelLength, 6, 2, 1, 1)

        self.radioButtonNarrow = QRadioButton(DialogFilterBandwidth)
        self.radioButtonNarrow.setObjectName(u"radioButtonNarrow")

        self.gridLayout.addWidget(self.radioButtonNarrow, 3, 0, 1, 1)

        self.labelWideBandwidth = QLabel(DialogFilterBandwidth)
        self.labelWideBandwidth.setObjectName(u"labelWideBandwidth")

        self.gridLayout.addWidget(self.labelWideBandwidth, 5, 1, 1, 1)

        self.labelVeryNarrowKernelLength = QLabel(DialogFilterBandwidth)
        self.labelVeryNarrowKernelLength.setObjectName(u"labelVeryNarrowKernelLength")

        self.gridLayout.addWidget(self.labelVeryNarrowKernelLength, 2, 2, 1, 1)

        self.labelBandwidthCaption = QLabel(DialogFilterBandwidth)
        self.labelBandwidthCaption.setObjectName(u"labelBandwidthCaption")

        self.gridLayout.addWidget(self.labelBandwidthCaption, 0, 1, 1, 1)

        self.labelNarrowBandwidth = QLabel(DialogFilterBandwidth)
        self.labelNarrowBandwidth.setObjectName(u"labelNarrowBandwidth")

        self.gridLayout.addWidget(self.labelNarrowBandwidth, 3, 1, 1, 1)

        self.labelNarrowKernelLength = QLabel(DialogFilterBandwidth)
        self.labelNarrowKernelLength.setObjectName(u"labelNarrowKernelLength")

        self.gridLayout.addWidget(self.labelNarrowKernelLength, 3, 2, 1, 1)

        self.labelVeryNarrowBandwidth = QLabel(DialogFilterBandwidth)
        self.labelVeryNarrowBandwidth.setObjectName(u"labelVeryNarrowBandwidth")

        self.gridLayout.addWidget(self.labelVeryNarrowBandwidth, 2, 1, 1, 1)

        self.labelKernelLengthCaption = QLabel(DialogFilterBandwidth)
        self.labelKernelLengthCaption.setObjectName(u"labelKernelLengthCaption")

        self.gridLayout.addWidget(self.labelKernelLengthCaption, 0, 2, 1, 1)

        self.labelWideKernelLength = QLabel(DialogFilterBandwidth)
        self.labelWideKernelLength.setObjectName(u"labelWideKernelLength")

        self.gridLayout.addWidget(self.labelWideKernelLength, 5, 2, 1, 1)

        self.radioButtonVery_Wide = QRadioButton(DialogFilterBandwidth)
        self.radioButtonVery_Wide.setObjectName(u"radioButtonVery_Wide")

        self.gridLayout.addWidget(self.radioButtonVery_Wide, 6, 0, 1, 1)

        self.radioButtonVery_Narrow = QRadioButton(DialogFilterBandwidth)
        self.radioButtonVery_Narrow.setObjectName(u"radioButtonVery_Narrow")

        self.gridLayout.addWidget(self.radioButtonVery_Narrow, 2, 0, 1, 1)

        self.label = QLabel(DialogFilterBandwidth)
        self.label.setObjectName(u"label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.labelVeryWideBandwidth = QLabel(DialogFilterBandwidth)
        self.labelVeryWideBandwidth.setObjectName(u"labelVeryWideBandwidth")

        self.gridLayout.addWidget(self.labelVeryWideBandwidth, 6, 1, 1, 1)

        self.radioButtonMedium = QRadioButton(DialogFilterBandwidth)
        self.radioButtonMedium.setObjectName(u"radioButtonMedium")

        self.gridLayout.addWidget(self.radioButtonMedium, 4, 0, 1, 1)

        self.labelMediumBandwidth = QLabel(DialogFilterBandwidth)
        self.labelMediumBandwidth.setObjectName(u"labelMediumBandwidth")

        self.gridLayout.addWidget(self.labelMediumBandwidth, 4, 1, 1, 1)

        self.line = QFrame(DialogFilterBandwidth)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line, 1, 0, 1, 3)


        self.verticalLayout.addLayout(self.gridLayout)

        self.buttonBox = QDialogButtonBox(DialogFilterBandwidth)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)

        self.verticalLayout.addWidget(self.buttonBox)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 3)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(DialogFilterBandwidth)
        self.buttonBox.accepted.connect(DialogFilterBandwidth.accept)
        self.buttonBox.rejected.connect(DialogFilterBandwidth.reject)
    # setupUi

    def retranslateUi(self, DialogFilterBandwidth):
        DialogFilterBandwidth.setWindowTitle(QCoreApplication.translate("DialogFilterBandwidth", u"Configure Filter Bandwidth", None))
        self.labelExplanation.setText(QCoreApplication.translate("DialogFilterBandwidth", u"<html><head/><body>To separate the frequency bands from each other a <b>bandpass</b> filter is used. You can configure the <b>bandwidth</b> of this filter here. The bandwidth determines the <b>length N</b> of the<b> filter kernel</b>. Decreasing the bandwidth will increase the accuracy of the filter, at cost of higher computation time.</body></html>", None))
        self.radioButtonCustom.setText(QCoreApplication.translate("DialogFilterBandwidth", u"Custom", None))
        self.labelMediumKernelLength.setText(QCoreApplication.translate("DialogFilterBandwidth", u"TextLabel", None))
        self.radioButtonWide.setText(QCoreApplication.translate("DialogFilterBandwidth", u"Wide", None))
        self.labelVeryWideKernelLength.setText(QCoreApplication.translate("DialogFilterBandwidth", u"TextLabel", None))
        self.radioButtonNarrow.setText(QCoreApplication.translate("DialogFilterBandwidth", u"Narrow", None))
        self.labelWideBandwidth.setText(QCoreApplication.translate("DialogFilterBandwidth", u"TextLabel", None))
        self.labelVeryNarrowKernelLength.setText(QCoreApplication.translate("DialogFilterBandwidth", u"TextLabel", None))
        self.labelBandwidthCaption.setText(QCoreApplication.translate("DialogFilterBandwidth", u"<b>Bandwidth (Hz)</b>", None))
        self.labelNarrowBandwidth.setText(QCoreApplication.translate("DialogFilterBandwidth", u"TextLabel", None))
        self.labelNarrowKernelLength.setText(QCoreApplication.translate("DialogFilterBandwidth", u"TextLabel", None))
        self.labelVeryNarrowBandwidth.setText(QCoreApplication.translate("DialogFilterBandwidth", u"TextLabel", None))
        self.labelKernelLengthCaption.setText(QCoreApplication.translate("DialogFilterBandwidth", u"<b >Kernel Length N</b>", None))
        self.labelWideKernelLength.setText(QCoreApplication.translate("DialogFilterBandwidth", u"TextLabel", None))
        self.radioButtonVery_Wide.setText(QCoreApplication.translate("DialogFilterBandwidth", u"Very Wide", None))
        self.radioButtonVery_Narrow.setText(QCoreApplication.translate("DialogFilterBandwidth", u"Very Narrow", None))
        self.label.setText(QCoreApplication.translate("DialogFilterBandwidth", u"<b>Choose </b>", None))
        self.labelVeryWideBandwidth.setText(QCoreApplication.translate("DialogFilterBandwidth", u"TextLabel", None))
        self.radioButtonMedium.setText(QCoreApplication.translate("DialogFilterBandwidth", u"Medium", None))
        self.labelMediumBandwidth.setText(QCoreApplication.translate("DialogFilterBandwidth", u"TextLabel", None))
    # retranslateUi

