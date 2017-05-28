# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FilterDialog(object):
    def setupUi(self, FilterDialog):
        FilterDialog.setObjectName("FilterDialog")
        FilterDialog.resize(469, 327)
        self.gridLayout = QtWidgets.QGridLayout(FilterDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(FilterDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.spinBoxNumTaps = QtWidgets.QSpinBox(FilterDialog)
        self.spinBoxNumTaps.setMinimum(1)
        self.spinBoxNumTaps.setMaximum(999999999)
        self.spinBoxNumTaps.setProperty("value", 10)
        self.spinBoxNumTaps.setObjectName("spinBoxNumTaps")
        self.gridLayout.addWidget(self.spinBoxNumTaps, 3, 1, 1, 1)
        self.radioButtonCustomTaps = QtWidgets.QRadioButton(FilterDialog)
        self.radioButtonCustomTaps.setObjectName("radioButtonCustomTaps")
        self.gridLayout.addWidget(self.radioButtonCustomTaps, 6, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 11, 0, 1, 1)
        self.lineEditCustomTaps = QtWidgets.QLineEdit(FilterDialog)
        self.lineEditCustomTaps.setObjectName("lineEditCustomTaps")
        self.gridLayout.addWidget(self.lineEditCustomTaps, 8, 0, 1, 2)
        self.radioButtonMovingAverage = QtWidgets.QRadioButton(FilterDialog)
        self.radioButtonMovingAverage.setChecked(True)
        self.radioButtonMovingAverage.setObjectName("radioButtonMovingAverage")
        self.gridLayout.addWidget(self.radioButtonMovingAverage, 5, 0, 1, 2)
        self.buttonBox = QtWidgets.QDialogButtonBox(FilterDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 2)
        self.label_3 = QtWidgets.QLabel(FilterDialog)
        font = QtGui.QFont()
        font.setItalic(True)
        self.label_3.setFont(font)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(FilterDialog)
        font = QtGui.QFont()
        font.setItalic(True)
        self.label_2.setFont(font)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 2)

        self.retranslateUi(FilterDialog)
        QtCore.QMetaObject.connectSlotsByName(FilterDialog)

    def retranslateUi(self, FilterDialog):
        _translate = QtCore.QCoreApplication.translate
        FilterDialog.setWindowTitle(_translate("FilterDialog", "Configure filter"))
        self.label.setText(_translate("FilterDialog", "Number of taps:"))
        self.radioButtonCustomTaps.setText(_translate("FilterDialog", "Custom taps:"))
        self.lineEditCustomTaps.setToolTip(_translate("FilterDialog", "<html><head/><body><p>You can configure custom filter taps here either explicit using [0.1, 0.2, 0.3] or with <span style=\" font-weight:600;\">python programming shortcuts</span> like [0.1] * 3 + [0.2] * 4 will result in [0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.2]</p></body></html>"))
        self.lineEditCustomTaps.setText(_translate("FilterDialog", "[0.1]*10"))
        self.radioButtonMovingAverage.setText(_translate("FilterDialog", "Moving average filter"))
        self.label_3.setText(_translate("FilterDialog", "You can imagine taps as weighting factors applied to n samples of the signal whereby n is the number of taps.  By default we use 10 taps with each tap set to 0.1 producing a moving average filter."))
        self.label_2.setText(_translate("FilterDialog", "These n weighted samples get summed up to produce the output of the filter. In DSP terms you configure the impulse response of the filter here."))

