# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FuzzingDialog(object):
    def setupUi(self, FuzzingDialog):
        FuzzingDialog.setObjectName("FuzzingDialog")
        FuzzingDialog.resize(523, 632)
        self.gridLayout_5 = QtWidgets.QGridLayout(FuzzingDialog)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.spinBoxFuzzMessage = QtWidgets.QSpinBox(FuzzingDialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.spinBoxFuzzMessage.sizePolicy().hasHeightForWidth()
        )
        self.spinBoxFuzzMessage.setSizePolicy(sizePolicy)
        self.spinBoxFuzzMessage.setMaximum(999999999)
        self.spinBoxFuzzMessage.setObjectName("spinBoxFuzzMessage")
        self.gridLayout_5.addWidget(self.spinBoxFuzzMessage, 2, 1, 1, 1)
        self.comboBoxStrategy = QtWidgets.QComboBox(FuzzingDialog)
        self.comboBoxStrategy.setObjectName("comboBoxStrategy")
        self.comboBoxStrategy.addItem("")
        self.comboBoxStrategy.addItem("")
        self.comboBoxStrategy.addItem("")
        self.comboBoxStrategy.addItem("")
        self.gridLayout_5.addWidget(self.comboBoxStrategy, 6, 1, 1, 1)
        self.btnAddFuzzingValues = QtWidgets.QPushButton(FuzzingDialog)
        self.btnAddFuzzingValues.setObjectName("btnAddFuzzingValues")
        self.gridLayout_5.addWidget(self.btnAddFuzzingValues, 9, 1, 1, 1)
        self.stackedWidgetLabels = QtWidgets.QStackedWidget(FuzzingDialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.stackedWidgetLabels.sizePolicy().hasHeightForWidth()
        )
        self.stackedWidgetLabels.setSizePolicy(sizePolicy)
        self.stackedWidgetLabels.setObjectName("stackedWidgetLabels")
        self.pageAddRangeLabel = QtWidgets.QWidget()
        self.pageAddRangeLabel.setObjectName("pageAddRangeLabel")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.pageAddRangeLabel)
        self.verticalLayout_3.setContentsMargins(0, 0, -1, 0)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.lStart = QtWidgets.QLabel(self.pageAddRangeLabel)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lStart.sizePolicy().hasHeightForWidth())
        self.lStart.setSizePolicy(sizePolicy)
        self.lStart.setObjectName("lStart")
        self.verticalLayout_3.addWidget(self.lStart)
        self.lEnd = QtWidgets.QLabel(self.pageAddRangeLabel)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lEnd.sizePolicy().hasHeightForWidth())
        self.lEnd.setSizePolicy(sizePolicy)
        self.lEnd.setObjectName("lEnd")
        self.verticalLayout_3.addWidget(self.lEnd)
        self.lStep = QtWidgets.QLabel(self.pageAddRangeLabel)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lStep.sizePolicy().hasHeightForWidth())
        self.lStep.setSizePolicy(sizePolicy)
        self.lStep.setObjectName("lStep")
        self.verticalLayout_3.addWidget(self.lStep)
        self.stackedWidgetLabels.addWidget(self.pageAddRangeLabel)
        self.pageAddBoundariesLabel = QtWidgets.QWidget()
        self.pageAddBoundariesLabel.setObjectName("pageAddBoundariesLabel")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.pageAddBoundariesLabel)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.checkBoxLowerBound = QtWidgets.QCheckBox(self.pageAddBoundariesLabel)
        self.checkBoxLowerBound.setChecked(True)
        self.checkBoxLowerBound.setObjectName("checkBoxLowerBound")
        self.verticalLayout_4.addWidget(self.checkBoxLowerBound)
        self.checkBoxUpperBound = QtWidgets.QCheckBox(self.pageAddBoundariesLabel)
        self.checkBoxUpperBound.setChecked(True)
        self.checkBoxUpperBound.setObjectName("checkBoxUpperBound")
        self.verticalLayout_4.addWidget(self.checkBoxUpperBound)
        self.lNumberBoundaries = QtWidgets.QLabel(self.pageAddBoundariesLabel)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.lNumberBoundaries.sizePolicy().hasHeightForWidth()
        )
        self.lNumberBoundaries.setSizePolicy(sizePolicy)
        self.lNumberBoundaries.setObjectName("lNumberBoundaries")
        self.verticalLayout_4.addWidget(self.lNumberBoundaries)
        self.stackedWidgetLabels.addWidget(self.pageAddBoundariesLabel)
        self.pageAddRandomLabel = QtWidgets.QWidget()
        self.pageAddRandomLabel.setObjectName("pageAddRandomLabel")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.pageAddRandomLabel)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(6)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.lRandomMin = QtWidgets.QLabel(self.pageAddRandomLabel)
        self.lRandomMin.setObjectName("lRandomMin")
        self.verticalLayout_6.addWidget(self.lRandomMin)
        self.lRandomMax = QtWidgets.QLabel(self.pageAddRandomLabel)
        self.lRandomMax.setObjectName("lRandomMax")
        self.verticalLayout_6.addWidget(self.lRandomMax)
        self.lNumRandom = QtWidgets.QLabel(self.pageAddRandomLabel)
        self.lNumRandom.setObjectName("lNumRandom")
        self.verticalLayout_6.addWidget(self.lNumRandom)
        self.stackedWidgetLabels.addWidget(self.pageAddRandomLabel)
        self.gridLayout_5.addWidget(self.stackedWidgetLabels, 7, 0, 2, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lPreBits = QtWidgets.QLabel(FuzzingDialog)
        self.lPreBits.setObjectName("lPreBits")
        self.horizontalLayout_2.addWidget(self.lPreBits)
        self.lFuzzedBits = QtWidgets.QLabel(FuzzingDialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lFuzzedBits.sizePolicy().hasHeightForWidth())
        self.lFuzzedBits.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lFuzzedBits.setFont(font)
        self.lFuzzedBits.setAlignment(QtCore.Qt.AlignCenter)
        self.lFuzzedBits.setObjectName("lFuzzedBits")
        self.horizontalLayout_2.addWidget(self.lFuzzedBits)
        self.lPostBits = QtWidgets.QLabel(FuzzingDialog)
        self.lPostBits.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.lPostBits.setObjectName("lPostBits")
        self.horizontalLayout_2.addWidget(self.lPostBits)
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_2.addItem(spacerItem)
        self.gridLayout_5.addLayout(self.horizontalLayout_2, 1, 1, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lFuzzedValues = QtWidgets.QLabel(FuzzingDialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.lFuzzedValues.sizePolicy().hasHeightForWidth()
        )
        self.lFuzzedValues.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lFuzzedValues.setFont(font)
        self.lFuzzedValues.setAlignment(QtCore.Qt.AlignCenter)
        self.lFuzzedValues.setObjectName("lFuzzedValues")
        self.verticalLayout.addWidget(self.lFuzzedValues)
        self.chkBRemoveDuplicates = QtWidgets.QCheckBox(FuzzingDialog)
        self.chkBRemoveDuplicates.setObjectName("chkBRemoveDuplicates")
        self.verticalLayout.addWidget(self.chkBRemoveDuplicates)
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.btnDelRow = QtWidgets.QToolButton(FuzzingDialog)
        icon = QtGui.QIcon.fromTheme("list-remove")
        self.btnDelRow.setIcon(icon)
        self.btnDelRow.setObjectName("btnDelRow")
        self.gridLayout_4.addWidget(self.btnDelRow, 1, 1, 1, 1)
        self.tblFuzzingValues = FuzzingTableView(FuzzingDialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.tblFuzzingValues.sizePolicy().hasHeightForWidth()
        )
        self.tblFuzzingValues.setSizePolicy(sizePolicy)
        self.tblFuzzingValues.setAlternatingRowColors(True)
        self.tblFuzzingValues.setVerticalScrollMode(
            QtWidgets.QAbstractItemView.ScrollPerPixel
        )
        self.tblFuzzingValues.setHorizontalScrollMode(
            QtWidgets.QAbstractItemView.ScrollPerPixel
        )
        self.tblFuzzingValues.setShowGrid(False)
        self.tblFuzzingValues.setObjectName("tblFuzzingValues")
        self.tblFuzzingValues.horizontalHeader().setHighlightSections(False)
        self.tblFuzzingValues.verticalHeader().setHighlightSections(False)
        self.gridLayout_4.addWidget(self.tblFuzzingValues, 0, 0, 4, 1)
        spacerItem1 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.gridLayout_4.addItem(spacerItem1, 3, 1, 1, 1)
        self.btnAddRow = QtWidgets.QToolButton(FuzzingDialog)
        icon = QtGui.QIcon.fromTheme("list-add")
        self.btnAddRow.setIcon(icon)
        self.btnAddRow.setObjectName("btnAddRow")
        self.gridLayout_4.addWidget(self.btnAddRow, 0, 1, 1, 1)
        self.btnRepeatValues = QtWidgets.QToolButton(FuzzingDialog)
        icon = QtGui.QIcon.fromTheme("media-playlist-repeat")
        self.btnRepeatValues.setIcon(icon)
        self.btnRepeatValues.setObjectName("btnRepeatValues")
        self.gridLayout_4.addWidget(self.btnRepeatValues, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_4)
        self.gridLayout_5.addLayout(self.verticalLayout, 5, 0, 1, 2)
        self.stackedWidgetSpinboxes = QtWidgets.QStackedWidget(FuzzingDialog)
        self.stackedWidgetSpinboxes.setObjectName("stackedWidgetSpinboxes")
        self.pageAddRange = QtWidgets.QWidget()
        self.pageAddRange.setObjectName("pageAddRange")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.pageAddRange)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.sBAddRangeStart = QtWidgets.QSpinBox(self.pageAddRange)
        self.sBAddRangeStart.setObjectName("sBAddRangeStart")
        self.verticalLayout_2.addWidget(self.sBAddRangeStart)
        self.sBAddRangeEnd = QtWidgets.QSpinBox(self.pageAddRange)
        self.sBAddRangeEnd.setObjectName("sBAddRangeEnd")
        self.verticalLayout_2.addWidget(self.sBAddRangeEnd)
        self.sBAddRangeStep = QtWidgets.QSpinBox(self.pageAddRange)
        self.sBAddRangeStep.setMinimum(1)
        self.sBAddRangeStep.setObjectName("sBAddRangeStep")
        self.verticalLayout_2.addWidget(self.sBAddRangeStep)
        self.stackedWidgetSpinboxes.addWidget(self.pageAddRange)
        self.pageAddBoundaries = QtWidgets.QWidget()
        self.pageAddBoundaries.setObjectName("pageAddBoundaries")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.pageAddBoundaries)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.spinBoxLowerBound = QtWidgets.QSpinBox(self.pageAddBoundaries)
        self.spinBoxLowerBound.setObjectName("spinBoxLowerBound")
        self.verticalLayout_5.addWidget(self.spinBoxLowerBound)
        self.spinBoxUpperBound = QtWidgets.QSpinBox(self.pageAddBoundaries)
        self.spinBoxUpperBound.setProperty("value", 13)
        self.spinBoxUpperBound.setObjectName("spinBoxUpperBound")
        self.verticalLayout_5.addWidget(self.spinBoxUpperBound)
        self.spinBoxBoundaryNumber = QtWidgets.QSpinBox(self.pageAddBoundaries)
        self.spinBoxBoundaryNumber.setMinimum(1)
        self.spinBoxBoundaryNumber.setObjectName("spinBoxBoundaryNumber")
        self.verticalLayout_5.addWidget(self.spinBoxBoundaryNumber)
        self.stackedWidgetSpinboxes.addWidget(self.pageAddBoundaries)
        self.pageAddRandom = QtWidgets.QWidget()
        self.pageAddRandom.setObjectName("pageAddRandom")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.pageAddRandom)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setSpacing(6)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.spinBoxRandomMinimum = QtWidgets.QSpinBox(self.pageAddRandom)
        self.spinBoxRandomMinimum.setObjectName("spinBoxRandomMinimum")
        self.verticalLayout_7.addWidget(self.spinBoxRandomMinimum)
        self.spinBoxRandomMaximum = QtWidgets.QSpinBox(self.pageAddRandom)
        self.spinBoxRandomMaximum.setProperty("value", 42)
        self.spinBoxRandomMaximum.setObjectName("spinBoxRandomMaximum")
        self.verticalLayout_7.addWidget(self.spinBoxRandomMaximum)
        self.spinBoxNumberRandom = QtWidgets.QSpinBox(self.pageAddRandom)
        self.spinBoxNumberRandom.setMinimum(1)
        self.spinBoxNumberRandom.setMaximum(999999999)
        self.spinBoxNumberRandom.setObjectName("spinBoxNumberRandom")
        self.verticalLayout_7.addWidget(self.spinBoxNumberRandom)
        self.stackedWidgetSpinboxes.addWidget(self.pageAddRandom)
        self.gridLayout_5.addWidget(self.stackedWidgetSpinboxes, 7, 1, 2, 1)
        self.lSourceBlock = QtWidgets.QLabel(FuzzingDialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lSourceBlock.sizePolicy().hasHeightForWidth())
        self.lSourceBlock.setSizePolicy(sizePolicy)
        self.lSourceBlock.setObjectName("lSourceBlock")
        self.gridLayout_5.addWidget(self.lSourceBlock, 1, 0, 1, 1)
        self.lFuzzingReferenceBlock = QtWidgets.QLabel(FuzzingDialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.lFuzzingReferenceBlock.sizePolicy().hasHeightForWidth()
        )
        self.lFuzzingReferenceBlock.setSizePolicy(sizePolicy)
        self.lFuzzingReferenceBlock.setObjectName("lFuzzingReferenceBlock")
        self.gridLayout_5.addWidget(self.lFuzzingReferenceBlock, 2, 0, 1, 1)
        self.lFuzzingEnd = QtWidgets.QLabel(FuzzingDialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lFuzzingEnd.sizePolicy().hasHeightForWidth())
        self.lFuzzingEnd.setSizePolicy(sizePolicy)
        self.lFuzzingEnd.setObjectName("lFuzzingEnd")
        self.gridLayout_5.addWidget(self.lFuzzingEnd, 4, 0, 1, 1)
        self.lStrategy = QtWidgets.QLabel(FuzzingDialog)
        self.lStrategy.setObjectName("lStrategy")
        self.gridLayout_5.addWidget(self.lStrategy, 6, 0, 1, 1)
        self.comboBoxFuzzingLabel = QtWidgets.QComboBox(FuzzingDialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.comboBoxFuzzingLabel.sizePolicy().hasHeightForWidth()
        )
        self.comboBoxFuzzingLabel.setSizePolicy(sizePolicy)
        self.comboBoxFuzzingLabel.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.comboBoxFuzzingLabel.setEditable(True)
        self.comboBoxFuzzingLabel.setObjectName("comboBoxFuzzingLabel")
        self.gridLayout_5.addWidget(self.comboBoxFuzzingLabel, 0, 1, 1, 1)
        self.spinBoxFuzzingEnd = QtWidgets.QSpinBox(FuzzingDialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.spinBoxFuzzingEnd.sizePolicy().hasHeightForWidth()
        )
        self.spinBoxFuzzingEnd.setSizePolicy(sizePolicy)
        self.spinBoxFuzzingEnd.setMinimum(1)
        self.spinBoxFuzzingEnd.setMaximum(999999999)
        self.spinBoxFuzzingEnd.setObjectName("spinBoxFuzzingEnd")
        self.gridLayout_5.addWidget(self.spinBoxFuzzingEnd, 4, 1, 1, 1)
        self.spinBoxFuzzingStart = QtWidgets.QSpinBox(FuzzingDialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.spinBoxFuzzingStart.sizePolicy().hasHeightForWidth()
        )
        self.spinBoxFuzzingStart.setSizePolicy(sizePolicy)
        self.spinBoxFuzzingStart.setMinimum(1)
        self.spinBoxFuzzingStart.setMaximum(999999999)
        self.spinBoxFuzzingStart.setObjectName("spinBoxFuzzingStart")
        self.gridLayout_5.addWidget(self.spinBoxFuzzingStart, 3, 1, 1, 1)
        self.lFuzzingStart = QtWidgets.QLabel(FuzzingDialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.lFuzzingStart.sizePolicy().hasHeightForWidth()
        )
        self.lFuzzingStart.setSizePolicy(sizePolicy)
        self.lFuzzingStart.setObjectName("lFuzzingStart")
        self.gridLayout_5.addWidget(self.lFuzzingStart, 3, 0, 1, 1)
        self.lFuzzingLabel = QtWidgets.QLabel(FuzzingDialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.lFuzzingLabel.sizePolicy().hasHeightForWidth()
        )
        self.lFuzzingLabel.setSizePolicy(sizePolicy)
        self.lFuzzingLabel.setObjectName("lFuzzingLabel")
        self.gridLayout_5.addWidget(self.lFuzzingLabel, 0, 0, 1, 1)

        self.retranslateUi(FuzzingDialog)
        self.stackedWidgetLabels.setCurrentIndex(0)
        self.stackedWidgetSpinboxes.setCurrentIndex(0)
        self.comboBoxStrategy.currentIndexChanged["int"].connect(
            self.stackedWidgetLabels.setCurrentIndex
        )
        self.comboBoxStrategy.currentIndexChanged["int"].connect(
            self.stackedWidgetSpinboxes.setCurrentIndex
        )

    def retranslateUi(self, FuzzingDialog):
        _translate = QtCore.QCoreApplication.translate
        FuzzingDialog.setWindowTitle(_translate("FuzzingDialog", "Fuzzing"))
        self.comboBoxStrategy.setItemText(
            0, _translate("FuzzingDialog", "Add Range of Values")
        )
        self.comboBoxStrategy.setItemText(
            1, _translate("FuzzingDialog", "Add Boundaries")
        )
        self.comboBoxStrategy.setItemText(
            2, _translate("FuzzingDialog", "Add Random Values from Range")
        )
        self.comboBoxStrategy.setItemText(
            3, _translate("FuzzingDialog", "Add De Bruijn Sequence")
        )
        self.btnAddFuzzingValues.setText(
            _translate("FuzzingDialog", "Add to Fuzzed Values")
        )
        self.lStart.setText(_translate("FuzzingDialog", "Start (Decimal):"))
        self.lEnd.setText(_translate("FuzzingDialog", "End (Decimal):"))
        self.lStep.setText(_translate("FuzzingDialog", "Step (Decimal):"))
        self.checkBoxLowerBound.setText(_translate("FuzzingDialog", "Lower Bound"))
        self.checkBoxUpperBound.setText(_translate("FuzzingDialog", "Upper Bound"))
        self.lNumberBoundaries.setText(
            _translate("FuzzingDialog", "Values per Boundary:")
        )
        self.lRandomMin.setText(_translate("FuzzingDialog", "Range Minimum:"))
        self.lRandomMax.setText(_translate("FuzzingDialog", "Range Maximum:"))
        self.lNumRandom.setText(_translate("FuzzingDialog", "Number Values:"))
        self.lPreBits.setText(_translate("FuzzingDialog", "1111"))
        self.lFuzzedBits.setText(_translate("FuzzingDialog", "1010"))
        self.lPostBits.setText(_translate("FuzzingDialog", "010101"))
        self.lFuzzedValues.setText(_translate("FuzzingDialog", "Fuzzed Values"))
        self.chkBRemoveDuplicates.setText(
            _translate("FuzzingDialog", "Remove Duplicates")
        )
        self.btnDelRow.setToolTip(
            _translate(
                "FuzzingDialog",
                "Remove selected values or last value if nothing is selected.",
            )
        )
        self.btnDelRow.setText(_translate("FuzzingDialog", "..."))
        self.btnAddRow.setToolTip(_translate("FuzzingDialog", "Add a new value."))
        self.btnAddRow.setText(_translate("FuzzingDialog", "..."))
        self.btnRepeatValues.setToolTip(
            _translate(
                "FuzzingDialog",
                "Repeat selected values or all values if nothing is selected.",
            )
        )
        self.btnRepeatValues.setText(_translate("FuzzingDialog", "..."))
        self.lSourceBlock.setText(_translate("FuzzingDialog", "Source Message:"))
        self.lFuzzingReferenceBlock.setText(
            _translate("FuzzingDialog", "Message to fuzz:")
        )
        self.lFuzzingEnd.setText(
            _translate("FuzzingDialog", "Fuzzing Label End Index:")
        )
        self.lStrategy.setText(_translate("FuzzingDialog", "Strategy:"))
        self.lFuzzingStart.setText(
            _translate("FuzzingDialog", "Fuzzing Label Start Index:")
        )
        self.lFuzzingLabel.setText(_translate("FuzzingDialog", "Fuzzing Label:"))


from urh.ui.views.FuzzingTableView import FuzzingTableView
