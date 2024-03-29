# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DialogFilterBandwidth(object):
    def setupUi(self, DialogFilterBandwidth):
        DialogFilterBandwidth.setObjectName("DialogFilterBandwidth")
        DialogFilterBandwidth.resize(502, 426)
        self.verticalLayout = QtWidgets.QVBoxLayout(DialogFilterBandwidth)
        self.verticalLayout.setSpacing(7)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelExplanation = QtWidgets.QLabel(DialogFilterBandwidth)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.labelExplanation.sizePolicy().hasHeightForWidth()
        )
        self.labelExplanation.setSizePolicy(sizePolicy)
        self.labelExplanation.setAlignment(QtCore.Qt.AlignJustify | QtCore.Qt.AlignTop)
        self.labelExplanation.setWordWrap(True)
        self.labelExplanation.setObjectName("labelExplanation")
        self.verticalLayout.addWidget(self.labelExplanation)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.doubleSpinBoxCustomBandwidth = QtWidgets.QDoubleSpinBox(
            DialogFilterBandwidth
        )
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.doubleSpinBoxCustomBandwidth.sizePolicy().hasHeightForWidth()
        )
        self.doubleSpinBoxCustomBandwidth.setSizePolicy(sizePolicy)
        self.doubleSpinBoxCustomBandwidth.setDecimals(4)
        self.doubleSpinBoxCustomBandwidth.setMinimum(0.0001)
        self.doubleSpinBoxCustomBandwidth.setMaximum(0.5)
        self.doubleSpinBoxCustomBandwidth.setObjectName("doubleSpinBoxCustomBandwidth")
        self.gridLayout.addWidget(self.doubleSpinBoxCustomBandwidth, 7, 1, 1, 1)
        self.spinBoxCustomKernelLength = QtWidgets.QSpinBox(DialogFilterBandwidth)
        self.spinBoxCustomKernelLength.setMinimum(8)
        self.spinBoxCustomKernelLength.setMaximum(999999999)
        self.spinBoxCustomKernelLength.setObjectName("spinBoxCustomKernelLength")
        self.gridLayout.addWidget(self.spinBoxCustomKernelLength, 7, 2, 1, 1)
        self.radioButtonCustom = QtWidgets.QRadioButton(DialogFilterBandwidth)
        self.radioButtonCustom.setObjectName("radioButtonCustom")
        self.gridLayout.addWidget(self.radioButtonCustom, 7, 0, 1, 1)
        self.labelMediumKernelLength = QtWidgets.QLabel(DialogFilterBandwidth)
        self.labelMediumKernelLength.setObjectName("labelMediumKernelLength")
        self.gridLayout.addWidget(self.labelMediumKernelLength, 4, 2, 1, 1)
        self.radioButtonWide = QtWidgets.QRadioButton(DialogFilterBandwidth)
        self.radioButtonWide.setObjectName("radioButtonWide")
        self.gridLayout.addWidget(self.radioButtonWide, 5, 0, 1, 1)
        self.labelVeryWideKernelLength = QtWidgets.QLabel(DialogFilterBandwidth)
        self.labelVeryWideKernelLength.setObjectName("labelVeryWideKernelLength")
        self.gridLayout.addWidget(self.labelVeryWideKernelLength, 6, 2, 1, 1)
        self.radioButtonNarrow = QtWidgets.QRadioButton(DialogFilterBandwidth)
        self.radioButtonNarrow.setObjectName("radioButtonNarrow")
        self.gridLayout.addWidget(self.radioButtonNarrow, 3, 0, 1, 1)
        self.labelWideBandwidth = QtWidgets.QLabel(DialogFilterBandwidth)
        self.labelWideBandwidth.setObjectName("labelWideBandwidth")
        self.gridLayout.addWidget(self.labelWideBandwidth, 5, 1, 1, 1)
        self.labelVeryNarrowKernelLength = QtWidgets.QLabel(DialogFilterBandwidth)
        self.labelVeryNarrowKernelLength.setObjectName("labelVeryNarrowKernelLength")
        self.gridLayout.addWidget(self.labelVeryNarrowKernelLength, 2, 2, 1, 1)
        self.labelBandwidthCaption = QtWidgets.QLabel(DialogFilterBandwidth)
        self.labelBandwidthCaption.setObjectName("labelBandwidthCaption")
        self.gridLayout.addWidget(self.labelBandwidthCaption, 0, 1, 1, 1)
        self.labelNarrowBandwidth = QtWidgets.QLabel(DialogFilterBandwidth)
        self.labelNarrowBandwidth.setObjectName("labelNarrowBandwidth")
        self.gridLayout.addWidget(self.labelNarrowBandwidth, 3, 1, 1, 1)
        self.labelNarrowKernelLength = QtWidgets.QLabel(DialogFilterBandwidth)
        self.labelNarrowKernelLength.setObjectName("labelNarrowKernelLength")
        self.gridLayout.addWidget(self.labelNarrowKernelLength, 3, 2, 1, 1)
        self.labelVeryNarrowBandwidth = QtWidgets.QLabel(DialogFilterBandwidth)
        self.labelVeryNarrowBandwidth.setObjectName("labelVeryNarrowBandwidth")
        self.gridLayout.addWidget(self.labelVeryNarrowBandwidth, 2, 1, 1, 1)
        self.labelKernelLengthCaption = QtWidgets.QLabel(DialogFilterBandwidth)
        self.labelKernelLengthCaption.setObjectName("labelKernelLengthCaption")
        self.gridLayout.addWidget(self.labelKernelLengthCaption, 0, 2, 1, 1)
        self.labelWideKernelLength = QtWidgets.QLabel(DialogFilterBandwidth)
        self.labelWideKernelLength.setObjectName("labelWideKernelLength")
        self.gridLayout.addWidget(self.labelWideKernelLength, 5, 2, 1, 1)
        self.radioButtonVery_Wide = QtWidgets.QRadioButton(DialogFilterBandwidth)
        self.radioButtonVery_Wide.setObjectName("radioButtonVery_Wide")
        self.gridLayout.addWidget(self.radioButtonVery_Wide, 6, 0, 1, 1)
        self.radioButtonVery_Narrow = QtWidgets.QRadioButton(DialogFilterBandwidth)
        self.radioButtonVery_Narrow.setObjectName("radioButtonVery_Narrow")
        self.gridLayout.addWidget(self.radioButtonVery_Narrow, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(DialogFilterBandwidth)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.labelVeryWideBandwidth = QtWidgets.QLabel(DialogFilterBandwidth)
        self.labelVeryWideBandwidth.setObjectName("labelVeryWideBandwidth")
        self.gridLayout.addWidget(self.labelVeryWideBandwidth, 6, 1, 1, 1)
        self.radioButtonMedium = QtWidgets.QRadioButton(DialogFilterBandwidth)
        self.radioButtonMedium.setObjectName("radioButtonMedium")
        self.gridLayout.addWidget(self.radioButtonMedium, 4, 0, 1, 1)
        self.labelMediumBandwidth = QtWidgets.QLabel(DialogFilterBandwidth)
        self.labelMediumBandwidth.setObjectName("labelMediumBandwidth")
        self.gridLayout.addWidget(self.labelMediumBandwidth, 4, 1, 1, 1)
        self.line = QtWidgets.QFrame(DialogFilterBandwidth)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 1, 0, 1, 3)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogFilterBandwidth)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 3)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(DialogFilterBandwidth)
        self.buttonBox.accepted.connect(DialogFilterBandwidth.accept)
        self.buttonBox.rejected.connect(DialogFilterBandwidth.reject)

    def retranslateUi(self, DialogFilterBandwidth):
        _translate = QtCore.QCoreApplication.translate
        DialogFilterBandwidth.setWindowTitle(
            _translate("DialogFilterBandwidth", "Configure Filter Bandwidth")
        )
        self.labelExplanation.setText(
            _translate(
                "DialogFilterBandwidth",
                "<html><head/><body>To separate the frequency bands from each other a <b>bandpass</b> filter is used. You can configure the <b>bandwidth</b> of this filter here. The bandwidth determines the <b>length N</b> of the<b> filter kernel</b>. Decreasing the bandwidth will increase the accuracy of the filter, at cost of higher computation time.</body></html>",
            )
        )
        self.radioButtonCustom.setText(_translate("DialogFilterBandwidth", "Custom"))
        self.labelMediumKernelLength.setText(
            _translate("DialogFilterBandwidth", "TextLabel")
        )
        self.radioButtonWide.setText(_translate("DialogFilterBandwidth", "Wide"))
        self.labelVeryWideKernelLength.setText(
            _translate("DialogFilterBandwidth", "TextLabel")
        )
        self.radioButtonNarrow.setText(_translate("DialogFilterBandwidth", "Narrow"))
        self.labelWideBandwidth.setText(
            _translate("DialogFilterBandwidth", "TextLabel")
        )
        self.labelVeryNarrowKernelLength.setText(
            _translate("DialogFilterBandwidth", "TextLabel")
        )
        self.labelBandwidthCaption.setText(
            _translate("DialogFilterBandwidth", "<b>Bandwidth (Hz)</b>")
        )
        self.labelNarrowBandwidth.setText(
            _translate("DialogFilterBandwidth", "TextLabel")
        )
        self.labelNarrowKernelLength.setText(
            _translate("DialogFilterBandwidth", "TextLabel")
        )
        self.labelVeryNarrowBandwidth.setText(
            _translate("DialogFilterBandwidth", "TextLabel")
        )
        self.labelKernelLengthCaption.setText(
            _translate("DialogFilterBandwidth", "<b >Kernel Length N</b>")
        )
        self.labelWideKernelLength.setText(
            _translate("DialogFilterBandwidth", "TextLabel")
        )
        self.radioButtonVery_Wide.setText(
            _translate("DialogFilterBandwidth", "Very Wide")
        )
        self.radioButtonVery_Narrow.setText(
            _translate("DialogFilterBandwidth", "Very Narrow")
        )
        self.label.setText(_translate("DialogFilterBandwidth", "<b>Choose </b>"))
        self.labelVeryWideBandwidth.setText(
            _translate("DialogFilterBandwidth", "TextLabel")
        )
        self.radioButtonMedium.setText(_translate("DialogFilterBandwidth", "Medium"))
        self.labelMediumBandwidth.setText(
            _translate("DialogFilterBandwidth", "TextLabel")
        )
