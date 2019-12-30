# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fuzzing.ui'
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

import FuzzingTableView

class Ui_FuzzingDialog(object):
    def setupUi(self, FuzzingDialog):
        if FuzzingDialog.objectName():
            FuzzingDialog.setObjectName(u"FuzzingDialog")
        FuzzingDialog.resize(825, 666)
        self.gridLayout_5 = QGridLayout(FuzzingDialog)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.lFuzzingStart = QLabel(FuzzingDialog)
        self.lFuzzingStart.setObjectName(u"lFuzzingStart")
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lFuzzingStart.sizePolicy().hasHeightForWidth())
        self.lFuzzingStart.setSizePolicy(sizePolicy)

        self.gridLayout_5.addWidget(self.lFuzzingStart, 3, 0, 1, 1)

        self.spinBoxFuzzingStart = QSpinBox(FuzzingDialog)
        self.spinBoxFuzzingStart.setObjectName(u"spinBoxFuzzingStart")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.spinBoxFuzzingStart.sizePolicy().hasHeightForWidth())
        self.spinBoxFuzzingStart.setSizePolicy(sizePolicy1)
        self.spinBoxFuzzingStart.setMinimum(1)
        self.spinBoxFuzzingStart.setMaximum(999999999)

        self.gridLayout_5.addWidget(self.spinBoxFuzzingStart, 3, 1, 1, 1)

        self.lFuzzingLabel = QLabel(FuzzingDialog)
        self.lFuzzingLabel.setObjectName(u"lFuzzingLabel")
        sizePolicy2 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lFuzzingLabel.sizePolicy().hasHeightForWidth())
        self.lFuzzingLabel.setSizePolicy(sizePolicy2)

        self.gridLayout_5.addWidget(self.lFuzzingLabel, 0, 0, 1, 1)

        self.spinBoxFuzzMessage = QSpinBox(FuzzingDialog)
        self.spinBoxFuzzMessage.setObjectName(u"spinBoxFuzzMessage")
        sizePolicy1.setHeightForWidth(self.spinBoxFuzzMessage.sizePolicy().hasHeightForWidth())
        self.spinBoxFuzzMessage.setSizePolicy(sizePolicy1)
        self.spinBoxFuzzMessage.setMaximum(999999999)

        self.gridLayout_5.addWidget(self.spinBoxFuzzMessage, 2, 1, 1, 1)

        self.lSourceBlock = QLabel(FuzzingDialog)
        self.lSourceBlock.setObjectName(u"lSourceBlock")
        sizePolicy.setHeightForWidth(self.lSourceBlock.sizePolicy().hasHeightForWidth())
        self.lSourceBlock.setSizePolicy(sizePolicy)

        self.gridLayout_5.addWidget(self.lSourceBlock, 1, 0, 1, 1)

        self.lFuzzingReferenceBlock = QLabel(FuzzingDialog)
        self.lFuzzingReferenceBlock.setObjectName(u"lFuzzingReferenceBlock")
        sizePolicy2.setHeightForWidth(self.lFuzzingReferenceBlock.sizePolicy().hasHeightForWidth())
        self.lFuzzingReferenceBlock.setSizePolicy(sizePolicy2)

        self.gridLayout_5.addWidget(self.lFuzzingReferenceBlock, 2, 0, 1, 1)

        self.lFuzzingEnd = QLabel(FuzzingDialog)
        self.lFuzzingEnd.setObjectName(u"lFuzzingEnd")
        sizePolicy.setHeightForWidth(self.lFuzzingEnd.sizePolicy().hasHeightForWidth())
        self.lFuzzingEnd.setSizePolicy(sizePolicy)

        self.gridLayout_5.addWidget(self.lFuzzingEnd, 4, 0, 1, 1)

        self.comboBoxFuzzingLabel = QComboBox(FuzzingDialog)
        self.comboBoxFuzzingLabel.setObjectName(u"comboBoxFuzzingLabel")
        sizePolicy1.setHeightForWidth(self.comboBoxFuzzingLabel.sizePolicy().hasHeightForWidth())
        self.comboBoxFuzzingLabel.setSizePolicy(sizePolicy1)
        self.comboBoxFuzzingLabel.setMaximumSize(QSize(16777215, 16777215))
        self.comboBoxFuzzingLabel.setEditable(True)

        self.gridLayout_5.addWidget(self.comboBoxFuzzingLabel, 0, 1, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lFuzzedValues = QLabel(FuzzingDialog)
        self.lFuzzedValues.setObjectName(u"lFuzzedValues")
        sizePolicy1.setHeightForWidth(self.lFuzzedValues.sizePolicy().hasHeightForWidth())
        self.lFuzzedValues.setSizePolicy(sizePolicy1)
        font = QFont()
        font.setBold(True)
        font.setWeight(75);
        self.lFuzzedValues.setFont(font)
        self.lFuzzedValues.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.lFuzzedValues)

        self.chkBRemoveDuplicates = QCheckBox(FuzzingDialog)
        self.chkBRemoveDuplicates.setObjectName(u"chkBRemoveDuplicates")

        self.verticalLayout.addWidget(self.chkBRemoveDuplicates)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.btnDelRow = QToolButton(FuzzingDialog)
        self.btnDelRow.setObjectName(u"btnDelRow")
        icon = QIcon()
        iconThemeName = u"list-remove"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnDelRow.setIcon(icon)

        self.gridLayout_4.addWidget(self.btnDelRow, 1, 1, 1, 1)

        self.tblFuzzingValues = FuzzingTableView(FuzzingDialog)
        self.tblFuzzingValues.setObjectName(u"tblFuzzingValues")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.tblFuzzingValues.sizePolicy().hasHeightForWidth())
        self.tblFuzzingValues.setSizePolicy(sizePolicy3)
        self.tblFuzzingValues.setAlternatingRowColors(True)
        self.tblFuzzingValues.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tblFuzzingValues.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tblFuzzingValues.setShowGrid(False)
        self.tblFuzzingValues.horizontalHeader().setHighlightSections(False)
        self.tblFuzzingValues.verticalHeader().setHighlightSections(False)

        self.gridLayout_4.addWidget(self.tblFuzzingValues, 0, 0, 4, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer, 3, 1, 1, 1)

        self.btnAddRow = QToolButton(FuzzingDialog)
        self.btnAddRow.setObjectName(u"btnAddRow")
        icon1 = QIcon()
        iconThemeName = u"list-add"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnAddRow.setIcon(icon1)

        self.gridLayout_4.addWidget(self.btnAddRow, 0, 1, 1, 1)

        self.btnRepeatValues = QToolButton(FuzzingDialog)
        self.btnRepeatValues.setObjectName(u"btnRepeatValues")
        icon2 = QIcon()
        iconThemeName = u"media-playlist-repeat"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnRepeatValues.setIcon(icon2)

        self.gridLayout_4.addWidget(self.btnRepeatValues, 2, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_4)


        self.gridLayout_5.addLayout(self.verticalLayout, 5, 0, 1, 2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.groupBoxAddRange = QGroupBox(FuzzingDialog)
        self.groupBoxAddRange.setObjectName(u"groupBoxAddRange")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.groupBoxAddRange.sizePolicy().hasHeightForWidth())
        self.groupBoxAddRange.setSizePolicy(sizePolicy4)
        self.gridLayout_2 = QGridLayout(self.groupBoxAddRange)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.lStart = QLabel(self.groupBoxAddRange)
        self.lStart.setObjectName(u"lStart")
        sizePolicy2.setHeightForWidth(self.lStart.sizePolicy().hasHeightForWidth())
        self.lStart.setSizePolicy(sizePolicy2)

        self.gridLayout_2.addWidget(self.lStart, 0, 0, 1, 1)

        self.sBAddRangeStart = QSpinBox(self.groupBoxAddRange)
        self.sBAddRangeStart.setObjectName(u"sBAddRangeStart")

        self.gridLayout_2.addWidget(self.sBAddRangeStart, 0, 1, 1, 1)

        self.lEnd = QLabel(self.groupBoxAddRange)
        self.lEnd.setObjectName(u"lEnd")

        self.gridLayout_2.addWidget(self.lEnd, 1, 0, 1, 1)

        self.sBAddRangeEnd = QSpinBox(self.groupBoxAddRange)
        self.sBAddRangeEnd.setObjectName(u"sBAddRangeEnd")

        self.gridLayout_2.addWidget(self.sBAddRangeEnd, 1, 1, 1, 1)

        self.lStep = QLabel(self.groupBoxAddRange)
        self.lStep.setObjectName(u"lStep")

        self.gridLayout_2.addWidget(self.lStep, 2, 0, 1, 1)

        self.sBAddRangeStep = QSpinBox(self.groupBoxAddRange)
        self.sBAddRangeStep.setObjectName(u"sBAddRangeStep")
        self.sBAddRangeStep.setMinimum(1)

        self.gridLayout_2.addWidget(self.sBAddRangeStep, 2, 1, 1, 1)

        self.btnAddRange = QPushButton(self.groupBoxAddRange)
        self.btnAddRange.setObjectName(u"btnAddRange")

        self.gridLayout_2.addWidget(self.btnAddRange, 3, 0, 1, 2)


        self.horizontalLayout_4.addWidget(self.groupBoxAddRange)

        self.groupBox = QGroupBox(FuzzingDialog)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy4.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy4)
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.checkBoxLowerBound = QCheckBox(self.groupBox)
        self.checkBoxLowerBound.setObjectName(u"checkBoxLowerBound")
        self.checkBoxLowerBound.setChecked(True)

        self.gridLayout.addWidget(self.checkBoxLowerBound, 0, 0, 1, 1)

        self.spinBoxLowerBound = QSpinBox(self.groupBox)
        self.spinBoxLowerBound.setObjectName(u"spinBoxLowerBound")

        self.gridLayout.addWidget(self.spinBoxLowerBound, 0, 1, 1, 1)

        self.checkBoxUpperBound = QCheckBox(self.groupBox)
        self.checkBoxUpperBound.setObjectName(u"checkBoxUpperBound")
        self.checkBoxUpperBound.setChecked(True)

        self.gridLayout.addWidget(self.checkBoxUpperBound, 1, 0, 1, 1)

        self.spinBoxUpperBound = QSpinBox(self.groupBox)
        self.spinBoxUpperBound.setObjectName(u"spinBoxUpperBound")

        self.gridLayout.addWidget(self.spinBoxUpperBound, 1, 1, 1, 1)

        self.lNumberBoundaries = QLabel(self.groupBox)
        self.lNumberBoundaries.setObjectName(u"lNumberBoundaries")
        sizePolicy1.setHeightForWidth(self.lNumberBoundaries.sizePolicy().hasHeightForWidth())
        self.lNumberBoundaries.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.lNumberBoundaries, 2, 0, 1, 1)

        self.spinBoxBoundaryNumber = QSpinBox(self.groupBox)
        self.spinBoxBoundaryNumber.setObjectName(u"spinBoxBoundaryNumber")
        self.spinBoxBoundaryNumber.setMinimum(1)

        self.gridLayout.addWidget(self.spinBoxBoundaryNumber, 2, 1, 1, 1)

        self.btnAddBoundaries = QPushButton(self.groupBox)
        self.btnAddBoundaries.setObjectName(u"btnAddBoundaries")

        self.gridLayout.addWidget(self.btnAddBoundaries, 3, 0, 1, 2)


        self.horizontalLayout_4.addWidget(self.groupBox)

        self.groupBoxxRandom = QGroupBox(FuzzingDialog)
        self.groupBoxxRandom.setObjectName(u"groupBoxxRandom")
        sizePolicy4.setHeightForWidth(self.groupBoxxRandom.sizePolicy().hasHeightForWidth())
        self.groupBoxxRandom.setSizePolicy(sizePolicy4)
        self.gridLayout_3 = QGridLayout(self.groupBoxxRandom)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.lNumRandom = QLabel(self.groupBoxxRandom)
        self.lNumRandom.setObjectName(u"lNumRandom")

        self.gridLayout_3.addWidget(self.lNumRandom, 0, 0, 1, 1)

        self.spinBoxNumberRandom = QSpinBox(self.groupBoxxRandom)
        self.spinBoxNumberRandom.setObjectName(u"spinBoxNumberRandom")
        self.spinBoxNumberRandom.setMinimum(1)
        self.spinBoxNumberRandom.setMaximum(999999999)

        self.gridLayout_3.addWidget(self.spinBoxNumberRandom, 0, 1, 1, 1)

        self.lRandomMin = QLabel(self.groupBoxxRandom)
        self.lRandomMin.setObjectName(u"lRandomMin")

        self.gridLayout_3.addWidget(self.lRandomMin, 1, 0, 1, 1)

        self.spinBoxRandomMinimum = QSpinBox(self.groupBoxxRandom)
        self.spinBoxRandomMinimum.setObjectName(u"spinBoxRandomMinimum")

        self.gridLayout_3.addWidget(self.spinBoxRandomMinimum, 1, 1, 1, 1)

        self.lRandomMax = QLabel(self.groupBoxxRandom)
        self.lRandomMax.setObjectName(u"lRandomMax")

        self.gridLayout_3.addWidget(self.lRandomMax, 2, 0, 1, 1)

        self.spinBoxRandomMaximum = QSpinBox(self.groupBoxxRandom)
        self.spinBoxRandomMaximum.setObjectName(u"spinBoxRandomMaximum")

        self.gridLayout_3.addWidget(self.spinBoxRandomMaximum, 2, 1, 1, 1)

        self.btnAddRandom = QPushButton(self.groupBoxxRandom)
        self.btnAddRandom.setObjectName(u"btnAddRandom")

        self.gridLayout_3.addWidget(self.btnAddRandom, 3, 0, 1, 2)


        self.horizontalLayout_4.addWidget(self.groupBoxxRandom)


        self.gridLayout_5.addLayout(self.horizontalLayout_4, 6, 0, 1, 2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.lPreBits = QLabel(FuzzingDialog)
        self.lPreBits.setObjectName(u"lPreBits")

        self.horizontalLayout_2.addWidget(self.lPreBits)

        self.lFuzzedBits = QLabel(FuzzingDialog)
        self.lFuzzedBits.setObjectName(u"lFuzzedBits")
        sizePolicy5 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.lFuzzedBits.sizePolicy().hasHeightForWidth())
        self.lFuzzedBits.setSizePolicy(sizePolicy5)
        self.lFuzzedBits.setFont(font)
        self.lFuzzedBits.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.lFuzzedBits)

        self.lPostBits = QLabel(FuzzingDialog)
        self.lPostBits.setObjectName(u"lPostBits")
        self.lPostBits.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.lPostBits)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.gridLayout_5.addLayout(self.horizontalLayout_2, 1, 1, 1, 1)

        self.spinBoxFuzzingEnd = QSpinBox(FuzzingDialog)
        self.spinBoxFuzzingEnd.setObjectName(u"spinBoxFuzzingEnd")
        sizePolicy1.setHeightForWidth(self.spinBoxFuzzingEnd.sizePolicy().hasHeightForWidth())
        self.spinBoxFuzzingEnd.setSizePolicy(sizePolicy1)
        self.spinBoxFuzzingEnd.setMinimum(1)
        self.spinBoxFuzzingEnd.setMaximum(999999999)

        self.gridLayout_5.addWidget(self.spinBoxFuzzingEnd, 4, 1, 1, 1)


        self.retranslateUi(FuzzingDialog)
    # setupUi

    def retranslateUi(self, FuzzingDialog):
        FuzzingDialog.setWindowTitle(QCoreApplication.translate("FuzzingDialog", u"Fuzzing", None))
        self.lFuzzingStart.setText(QCoreApplication.translate("FuzzingDialog", u"Fuzzing Label Start Index:", None))
        self.lFuzzingLabel.setText(QCoreApplication.translate("FuzzingDialog", u"Fuzzing Label:", None))
        self.lSourceBlock.setText(QCoreApplication.translate("FuzzingDialog", u"Source Message:", None))
        self.lFuzzingReferenceBlock.setText(QCoreApplication.translate("FuzzingDialog", u"Message to fuzz:", None))
        self.lFuzzingEnd.setText(QCoreApplication.translate("FuzzingDialog", u"Fuzzing Label End Index:", None))
        self.lFuzzedValues.setText(QCoreApplication.translate("FuzzingDialog", u"Fuzzed Values", None))
        self.chkBRemoveDuplicates.setText(QCoreApplication.translate("FuzzingDialog", u"Remove Duplicates", None))
#if QT_CONFIG(tooltip)
        self.btnDelRow.setToolTip(QCoreApplication.translate("FuzzingDialog", u"Remove selected values or last value if nothing is selected.", None))
#endif // QT_CONFIG(tooltip)
        self.btnDelRow.setText(QCoreApplication.translate("FuzzingDialog", u"...", None))
#if QT_CONFIG(tooltip)
        self.btnAddRow.setToolTip(QCoreApplication.translate("FuzzingDialog", u"Add a new value.", None))
#endif // QT_CONFIG(tooltip)
        self.btnAddRow.setText(QCoreApplication.translate("FuzzingDialog", u"...", None))
#if QT_CONFIG(tooltip)
        self.btnRepeatValues.setToolTip(QCoreApplication.translate("FuzzingDialog", u"Repeat selected values or all values if nothing is selected.", None))
#endif // QT_CONFIG(tooltip)
        self.btnRepeatValues.setText(QCoreApplication.translate("FuzzingDialog", u"...", None))
        self.groupBoxAddRange.setTitle(QCoreApplication.translate("FuzzingDialog", u"Add Range", None))
        self.lStart.setText(QCoreApplication.translate("FuzzingDialog", u"Start (Decimal):", None))
        self.lEnd.setText(QCoreApplication.translate("FuzzingDialog", u"End (Decimal):", None))
        self.lStep.setText(QCoreApplication.translate("FuzzingDialog", u"Step (Decimal):", None))
        self.btnAddRange.setText(QCoreApplication.translate("FuzzingDialog", u"Add to Fuzzed Values", None))
        self.groupBox.setTitle(QCoreApplication.translate("FuzzingDialog", u"Add Boundaries", None))
        self.checkBoxLowerBound.setText(QCoreApplication.translate("FuzzingDialog", u"Lower Bound", None))
        self.checkBoxUpperBound.setText(QCoreApplication.translate("FuzzingDialog", u"Upper Bound", None))
        self.lNumberBoundaries.setText(QCoreApplication.translate("FuzzingDialog", u"Border Values:", None))
        self.btnAddBoundaries.setText(QCoreApplication.translate("FuzzingDialog", u"Add to Fuzzed Values", None))
        self.groupBoxxRandom.setTitle(QCoreApplication.translate("FuzzingDialog", u"Add random values from range", None))
        self.lNumRandom.setText(QCoreApplication.translate("FuzzingDialog", u"Number:", None))
        self.lRandomMin.setText(QCoreApplication.translate("FuzzingDialog", u"Range Minimum:", None))
        self.lRandomMax.setText(QCoreApplication.translate("FuzzingDialog", u"Range Maximum:", None))
        self.btnAddRandom.setText(QCoreApplication.translate("FuzzingDialog", u"Add to Fuzzed Values", None))
        self.lPreBits.setText(QCoreApplication.translate("FuzzingDialog", u"1111", None))
        self.lFuzzedBits.setText(QCoreApplication.translate("FuzzingDialog", u"1010", None))
        self.lPostBits.setText(QCoreApplication.translate("FuzzingDialog", u"010101", None))
    # retranslateUi

