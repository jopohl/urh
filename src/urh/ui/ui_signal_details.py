# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'signal_details.ui'
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

import KillerDoubleSpinBox

class Ui_SignalDetails(object):
    def setupUi(self, SignalDetails):
        if SignalDetails.objectName():
            SignalDetails.setObjectName(u"SignalDetails")
        SignalDetails.resize(469, 200)
        self.verticalLayout = QVBoxLayout(SignalDetails)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 2, 2, 1, 1)

        self.dsb_sample_rate = KillerDoubleSpinBox(SignalDetails)
        self.dsb_sample_rate.setObjectName(u"dsb_sample_rate")
        self.dsb_sample_rate.setWrapping(False)
        self.dsb_sample_rate.setProperty("showGroupSeparator", False)
        self.dsb_sample_rate.setMinimum(0.010000000000000)
        self.dsb_sample_rate.setMaximum(999999999999999945575230987042816.000000000000000)
        self.dsb_sample_rate.setValue(1000000.000000000000000)

        self.gridLayout.addWidget(self.dsb_sample_rate, 5, 1, 1, 1)

        self.label = QLabel(SignalDetails)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.lblFile = QLabel(SignalDetails)
        self.lblFile.setObjectName(u"lblFile")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFile.sizePolicy().hasHeightForWidth())
        self.lblFile.setSizePolicy(sizePolicy)
        self.lblFile.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByKeyboard|Qt.TextSelectableByMouse)

        self.gridLayout.addWidget(self.lblFile, 1, 1, 1, 1)

        self.label_2 = QLabel(SignalDetails)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.label_5 = QLabel(SignalDetails)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)

        self.label_6 = QLabel(SignalDetails)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 1)

        self.lblSamplesTotal = QLabel(SignalDetails)
        self.lblSamplesTotal.setObjectName(u"lblSamplesTotal")

        self.gridLayout.addWidget(self.lblSamplesTotal, 4, 1, 1, 1)

        self.label_3 = QLabel(SignalDetails)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.lblName = QLabel(SignalDetails)
        self.lblName.setObjectName(u"lblName")
        sizePolicy.setHeightForWidth(self.lblName.sizePolicy().hasHeightForWidth())
        self.lblName.setSizePolicy(sizePolicy)
        self.lblName.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByKeyboard|Qt.TextSelectableByMouse)

        self.gridLayout.addWidget(self.lblName, 0, 1, 1, 1)

        self.lblFileSize = QLabel(SignalDetails)
        self.lblFileSize.setObjectName(u"lblFileSize")

        self.gridLayout.addWidget(self.lblFileSize, 2, 1, 1, 1)

        self.label_4 = QLabel(SignalDetails)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)

        self.lFileCreated = QLabel(SignalDetails)
        self.lFileCreated.setObjectName(u"lFileCreated")

        self.gridLayout.addWidget(self.lFileCreated, 3, 1, 1, 1)

        self.label_7 = QLabel(SignalDetails)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 1)

        self.lDuration = QLabel(SignalDetails)
        self.lDuration.setObjectName(u"lDuration")

        self.gridLayout.addWidget(self.lDuration, 6, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.verticalSpacer = QSpacerItem(20, 135, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(SignalDetails)
    # setupUi

    def retranslateUi(self, SignalDetails):
        SignalDetails.setWindowTitle(QCoreApplication.translate("SignalDetails", u"Signal details", None))
        self.label.setText(QCoreApplication.translate("SignalDetails", u"Name:", None))
        self.lblFile.setText(QCoreApplication.translate("SignalDetails", u"TextLabel", None))
        self.label_2.setText(QCoreApplication.translate("SignalDetails", u"File:", None))
        self.label_5.setText(QCoreApplication.translate("SignalDetails", u"Samples:", None))
        self.label_6.setText(QCoreApplication.translate("SignalDetails", u"Sample Rate (Sps):", None))
        self.lblSamplesTotal.setText(QCoreApplication.translate("SignalDetails", u"TextLabel", None))
        self.label_3.setText(QCoreApplication.translate("SignalDetails", u"File size:", None))
        self.lblName.setText(QCoreApplication.translate("SignalDetails", u"TextLabel", None))
        self.lblFileSize.setText(QCoreApplication.translate("SignalDetails", u"TextLabel", None))
        self.label_4.setText(QCoreApplication.translate("SignalDetails", u"File created:", None))
        self.lFileCreated.setText(QCoreApplication.translate("SignalDetails", u"TextLabel", None))
        self.label_7.setText(QCoreApplication.translate("SignalDetails", u"Duration:", None))
        self.lDuration.setText(QCoreApplication.translate("SignalDetails", u"42s", None))
    # retranslateUi

