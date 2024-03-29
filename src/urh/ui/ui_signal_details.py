# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SignalDetails(object):
    def setupUi(self, SignalDetails):
        SignalDetails.setObjectName("SignalDetails")
        SignalDetails.resize(469, 200)
        self.verticalLayout = QtWidgets.QVBoxLayout(SignalDetails)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridLayout.addItem(spacerItem, 2, 2, 1, 1)
        self.dsb_sample_rate = KillerDoubleSpinBox(SignalDetails)
        self.dsb_sample_rate.setWrapping(False)
        self.dsb_sample_rate.setProperty("showGroupSeparator", False)
        self.dsb_sample_rate.setMinimum(0.01)
        self.dsb_sample_rate.setMaximum(1e33)
        self.dsb_sample_rate.setProperty("value", 1000000.0)
        self.dsb_sample_rate.setObjectName("dsb_sample_rate")
        self.gridLayout.addWidget(self.dsb_sample_rate, 5, 1, 1, 1)
        self.label = QtWidgets.QLabel(SignalDetails)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.lblFile = QtWidgets.QLabel(SignalDetails)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFile.sizePolicy().hasHeightForWidth())
        self.lblFile.setSizePolicy(sizePolicy)
        self.lblFile.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByMouse
            | QtCore.Qt.TextSelectableByKeyboard
            | QtCore.Qt.TextSelectableByMouse
        )
        self.lblFile.setObjectName("lblFile")
        self.gridLayout.addWidget(self.lblFile, 1, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(SignalDetails)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(SignalDetails)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(SignalDetails)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 1)
        self.lblSamplesTotal = QtWidgets.QLabel(SignalDetails)
        self.lblSamplesTotal.setObjectName("lblSamplesTotal")
        self.gridLayout.addWidget(self.lblSamplesTotal, 4, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(SignalDetails)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.lblName = QtWidgets.QLabel(SignalDetails)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblName.sizePolicy().hasHeightForWidth())
        self.lblName.setSizePolicy(sizePolicy)
        self.lblName.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByMouse
            | QtCore.Qt.TextSelectableByKeyboard
            | QtCore.Qt.TextSelectableByMouse
        )
        self.lblName.setObjectName("lblName")
        self.gridLayout.addWidget(self.lblName, 0, 1, 1, 1)
        self.lblFileSize = QtWidgets.QLabel(SignalDetails)
        self.lblFileSize.setObjectName("lblFileSize")
        self.gridLayout.addWidget(self.lblFileSize, 2, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(SignalDetails)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.lFileCreated = QtWidgets.QLabel(SignalDetails)
        self.lFileCreated.setObjectName("lFileCreated")
        self.gridLayout.addWidget(self.lFileCreated, 3, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(SignalDetails)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 1)
        self.lDuration = QtWidgets.QLabel(SignalDetails)
        self.lDuration.setObjectName("lDuration")
        self.gridLayout.addWidget(self.lDuration, 6, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem1 = QtWidgets.QSpacerItem(
            20, 135, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.verticalLayout.addItem(spacerItem1)

        self.retranslateUi(SignalDetails)

    def retranslateUi(self, SignalDetails):
        _translate = QtCore.QCoreApplication.translate
        SignalDetails.setWindowTitle(_translate("SignalDetails", "Signal details"))
        self.label.setText(_translate("SignalDetails", "Name:"))
        self.lblFile.setText(_translate("SignalDetails", "TextLabel"))
        self.label_2.setText(_translate("SignalDetails", "File:"))
        self.label_5.setText(_translate("SignalDetails", "Samples:"))
        self.label_6.setText(_translate("SignalDetails", "Sample Rate (Sps):"))
        self.lblSamplesTotal.setText(_translate("SignalDetails", "TextLabel"))
        self.label_3.setText(_translate("SignalDetails", "File size:"))
        self.lblName.setText(_translate("SignalDetails", "TextLabel"))
        self.lblFileSize.setText(_translate("SignalDetails", "TextLabel"))
        self.label_4.setText(_translate("SignalDetails", "File created:"))
        self.lFileCreated.setText(_translate("SignalDetails", "TextLabel"))
        self.label_7.setText(_translate("SignalDetails", "Duration:"))
        self.lDuration.setText(_translate("SignalDetails", "42s"))


from urh.ui.KillerDoubleSpinBox import KillerDoubleSpinBox
