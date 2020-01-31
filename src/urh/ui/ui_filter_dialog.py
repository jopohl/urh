# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'filter_dialog.ui'
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


class Ui_FilterDialog(object):
    def setupUi(self, FilterDialog):
        if FilterDialog.objectName():
            FilterDialog.setObjectName(u"FilterDialog")
        FilterDialog.resize(528, 485)
        icon = QIcon()
        iconThemeName = u"view-filter"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        FilterDialog.setWindowIcon(icon)
        self.gridLayout = QGridLayout(FilterDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.radioButtonCustomTaps = QRadioButton(FilterDialog)
        self.radioButtonCustomTaps.setObjectName(u"radioButtonCustomTaps")
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.radioButtonCustomTaps.setFont(font)

        self.gridLayout.addWidget(self.radioButtonCustomTaps, 9, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(FilterDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)

        self.gridLayout.addWidget(self.buttonBox, 15, 0, 1, 2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 16, 0, 1, 1)

        self.line = QFrame(FilterDialog)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line, 7, 0, 1, 2)

        self.radioButtonMovingAverage = QRadioButton(FilterDialog)
        self.radioButtonMovingAverage.setObjectName(u"radioButtonMovingAverage")
        self.radioButtonMovingAverage.setFont(font)
        self.radioButtonMovingAverage.setChecked(True)

        self.gridLayout.addWidget(self.radioButtonMovingAverage, 8, 0, 1, 2)

        self.spinBoxNumTaps = QSpinBox(FilterDialog)
        self.spinBoxNumTaps.setObjectName(u"spinBoxNumTaps")
        self.spinBoxNumTaps.setMinimum(1)
        self.spinBoxNumTaps.setMaximum(999999999)
        self.spinBoxNumTaps.setValue(10)

        self.gridLayout.addWidget(self.spinBoxNumTaps, 10, 1, 1, 1)

        self.label_4 = QLabel(FilterDialog)
        self.label_4.setObjectName(u"label_4")
        font1 = QFont()
        font1.setItalic(True)
        self.label_4.setFont(font1)
        self.label_4.setWordWrap(True)

        self.gridLayout.addWidget(self.label_4, 6, 0, 1, 2)

        self.lineEditCustomTaps = QLineEdit(FilterDialog)
        self.lineEditCustomTaps.setObjectName(u"lineEditCustomTaps")

        self.gridLayout.addWidget(self.lineEditCustomTaps, 9, 1, 1, 1)

        self.label = QLabel(FilterDialog)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 10, 0, 1, 1)

        self.label_3 = QLabel(FilterDialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font1)
        self.label_3.setWordWrap(True)

        self.gridLayout.addWidget(self.label_3, 13, 0, 1, 2)

        self.label_2 = QLabel(FilterDialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font1)
        self.label_2.setWordWrap(True)

        self.gridLayout.addWidget(self.label_2, 14, 0, 1, 2)

        self.radioButtonDCcorrection = QRadioButton(FilterDialog)
        self.radioButtonDCcorrection.setObjectName(u"radioButtonDCcorrection")
        self.radioButtonDCcorrection.setFont(font)

        self.gridLayout.addWidget(self.radioButtonDCcorrection, 0, 0, 1, 2)


        self.retranslateUi(FilterDialog)
    # setupUi

    def retranslateUi(self, FilterDialog):
        FilterDialog.setWindowTitle(QCoreApplication.translate("FilterDialog", u"Configure filter", None))
        self.radioButtonCustomTaps.setText(QCoreApplication.translate("FilterDialog", u"Custom taps:", None))
        self.radioButtonMovingAverage.setText(QCoreApplication.translate("FilterDialog", u"Moving average", None))
        self.label_4.setText(QCoreApplication.translate("FilterDialog", u"A DC correction filter will remove the DC component (mean value) of the signal and center it around zero.", None))
#if QT_CONFIG(tooltip)
        self.lineEditCustomTaps.setToolTip(QCoreApplication.translate("FilterDialog", u"<html><head/><body><p>You can configure custom filter taps here either explicit using [0.1, 0.2, 0.3] or with <span style=\" font-weight:600;\">python programming shortcuts</span> like [0.1] * 3 + [0.2] * 4 will result in [0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.2]</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEditCustomTaps.setText(QCoreApplication.translate("FilterDialog", u"[0.1]*10", None))
        self.label.setText(QCoreApplication.translate("FilterDialog", u"Number of taps:", None))
        self.label_3.setText(QCoreApplication.translate("FilterDialog", u"You can imagine taps as weighting factors applied to n samples of the signal whereby n is the number of taps.  By default we use 10 taps with each tap set to 0.1 producing a moving average filter.", None))
        self.label_2.setText(QCoreApplication.translate("FilterDialog", u"These n weighted samples get summed up to produce the output of the filter. In DSP terms you configure the impulse response of the filter here.", None))
        self.radioButtonDCcorrection.setText(QCoreApplication.translate("FilterDialog", u"DC correction", None))
    # retranslateUi

