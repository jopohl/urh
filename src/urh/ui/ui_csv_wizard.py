# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'csv_wizard.ui'
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


class Ui_DialogCSVImport(object):
    def setupUi(self, DialogCSVImport):
        if DialogCSVImport.objectName():
            DialogCSVImport.setObjectName(u"DialogCSVImport")
        DialogCSVImport.resize(635, 674)
        self.gridLayout = QGridLayout(DialogCSVImport)
        self.gridLayout.setObjectName(u"gridLayout")
        self.labelFileNotFound = QLabel(DialogCSVImport)
        self.labelFileNotFound.setObjectName(u"labelFileNotFound")

        self.gridLayout.addWidget(self.labelFileNotFound, 1, 2, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.comboBoxCSVSeparator = QComboBox(DialogCSVImport)
        self.comboBoxCSVSeparator.addItem("")
        self.comboBoxCSVSeparator.addItem("")
        self.comboBoxCSVSeparator.setObjectName(u"comboBoxCSVSeparator")

        self.horizontalLayout.addWidget(self.comboBoxCSVSeparator)

        self.btnAddSeparator = QToolButton(DialogCSVImport)
        self.btnAddSeparator.setObjectName(u"btnAddSeparator")
        icon = QIcon()
        iconThemeName = u"list-add"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnAddSeparator.setIcon(icon)
        self.btnAddSeparator.setIconSize(QSize(16, 16))

        self.horizontalLayout.addWidget(self.btnAddSeparator)


        self.gridLayout.addLayout(self.horizontalLayout, 3, 2, 1, 1)

        self.spinBoxTimestampColumn = QSpinBox(DialogCSVImport)
        self.spinBoxTimestampColumn.setObjectName(u"spinBoxTimestampColumn")
        self.spinBoxTimestampColumn.setMaximum(999999999)

        self.gridLayout.addWidget(self.spinBoxTimestampColumn, 6, 2, 1, 1)

        self.label = QLabel(DialogCSVImport)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 4, 0, 1, 2)

        self.spinBoxQDataColumn = QSpinBox(DialogCSVImport)
        self.spinBoxQDataColumn.setObjectName(u"spinBoxQDataColumn")
        self.spinBoxQDataColumn.setMaximum(999999999)

        self.gridLayout.addWidget(self.spinBoxQDataColumn, 5, 2, 1, 1)

        self.label_3 = QLabel(DialogCSVImport)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 6, 0, 1, 2)

        self.label_2 = QLabel(DialogCSVImport)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 5, 0, 1, 2)

        self.groupBox = QGroupBox(DialogCSVImport)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tableWidgetPreview = QTableWidget(self.groupBox)
        if (self.tableWidgetPreview.columnCount() < 3):
            self.tableWidgetPreview.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidgetPreview.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidgetPreview.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidgetPreview.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.tableWidgetPreview.setObjectName(u"tableWidgetPreview")
        self.tableWidgetPreview.setAlternatingRowColors(True)
        self.tableWidgetPreview.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidgetPreview.horizontalHeader().setStretchLastSection(False)
        self.tableWidgetPreview.verticalHeader().setStretchLastSection(False)

        self.verticalLayout_2.addWidget(self.tableWidgetPreview)


        self.gridLayout.addWidget(self.groupBox, 7, 0, 1, 3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.lineEditFilename = QLineEdit(DialogCSVImport)
        self.lineEditFilename.setObjectName(u"lineEditFilename")

        self.horizontalLayout_2.addWidget(self.lineEditFilename)

        self.btnChooseFile = QToolButton(DialogCSVImport)
        self.btnChooseFile.setObjectName(u"btnChooseFile")
        self.btnChooseFile.setToolButtonStyle(Qt.ToolButtonTextOnly)

        self.horizontalLayout_2.addWidget(self.btnChooseFile)


        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 2, 1, 1)

        self.spinBoxIDataColumn = QSpinBox(DialogCSVImport)
        self.spinBoxIDataColumn.setObjectName(u"spinBoxIDataColumn")
        self.spinBoxIDataColumn.setMinimum(1)
        self.spinBoxIDataColumn.setMaximum(999999999)
        self.spinBoxIDataColumn.setValue(1)

        self.gridLayout.addWidget(self.spinBoxIDataColumn, 4, 2, 1, 1)

        self.label_4 = QLabel(DialogCSVImport)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 2)

        self.buttonBox = QDialogButtonBox(DialogCSVImport)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 9, 2, 1, 1)

        self.groupBoxFilePreview = QGroupBox(DialogCSVImport)
        self.groupBoxFilePreview.setObjectName(u"groupBoxFilePreview")
        self.verticalLayout = QVBoxLayout(self.groupBoxFilePreview)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.plainTextEditFilePreview = QPlainTextEdit(self.groupBoxFilePreview)
        self.plainTextEditFilePreview.setObjectName(u"plainTextEditFilePreview")
        self.plainTextEditFilePreview.setUndoRedoEnabled(False)
        self.plainTextEditFilePreview.setReadOnly(True)

        self.verticalLayout.addWidget(self.plainTextEditFilePreview)


        self.gridLayout.addWidget(self.groupBoxFilePreview, 2, 0, 1, 3)

        self.label_5 = QLabel(DialogCSVImport)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 0, 0, 1, 1)

        self.btnAutoDefault = QPushButton(DialogCSVImport)
        self.btnAutoDefault.setObjectName(u"btnAutoDefault")

        self.gridLayout.addWidget(self.btnAutoDefault, 10, 2, 1, 1)

        QWidget.setTabOrder(self.lineEditFilename, self.btnChooseFile)
        QWidget.setTabOrder(self.btnChooseFile, self.plainTextEditFilePreview)
        QWidget.setTabOrder(self.plainTextEditFilePreview, self.comboBoxCSVSeparator)
        QWidget.setTabOrder(self.comboBoxCSVSeparator, self.btnAddSeparator)
        QWidget.setTabOrder(self.btnAddSeparator, self.spinBoxIDataColumn)
        QWidget.setTabOrder(self.spinBoxIDataColumn, self.spinBoxQDataColumn)
        QWidget.setTabOrder(self.spinBoxQDataColumn, self.spinBoxTimestampColumn)
        QWidget.setTabOrder(self.spinBoxTimestampColumn, self.tableWidgetPreview)

        self.retranslateUi(DialogCSVImport)
        self.buttonBox.accepted.connect(DialogCSVImport.accept)
        self.buttonBox.rejected.connect(DialogCSVImport.reject)

        self.btnAutoDefault.setDefault(True)

    # setupUi

    def retranslateUi(self, DialogCSVImport):
        DialogCSVImport.setWindowTitle(QCoreApplication.translate("DialogCSVImport", u"CSV Import", None))
        self.labelFileNotFound.setText(QCoreApplication.translate("DialogCSVImport", u"<html><head/><body><p><span style=\" color:#ff0000;\">Could not open the selected file.</span></p></body></html>", None))
        self.comboBoxCSVSeparator.setItemText(0, QCoreApplication.translate("DialogCSVImport", u",", None))
        self.comboBoxCSVSeparator.setItemText(1, QCoreApplication.translate("DialogCSVImport", u";", None))

#if QT_CONFIG(tooltip)
        self.btnAddSeparator.setToolTip(QCoreApplication.translate("DialogCSVImport", u"Add a custom separator.", None))
#endif // QT_CONFIG(tooltip)
        self.btnAddSeparator.setText(QCoreApplication.translate("DialogCSVImport", u"...", None))
#if QT_CONFIG(tooltip)
        self.spinBoxTimestampColumn.setToolTip(QCoreApplication.translate("DialogCSVImport", u"<html><head/><body><p> If your dataset contains timestamps URH will calculate the sample rate from them. You can manually edit the sample rate after import in the signal details.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.spinBoxTimestampColumn.setSpecialValueText(QCoreApplication.translate("DialogCSVImport", u"Not present", None))
        self.label.setText(QCoreApplication.translate("DialogCSVImport", u"I Data Column:", None))
        self.spinBoxQDataColumn.setSpecialValueText(QCoreApplication.translate("DialogCSVImport", u"Not present", None))
#if QT_CONFIG(tooltip)
        self.label_3.setToolTip(QCoreApplication.translate("DialogCSVImport", u"<html><head/><body><p> If your dataset contains timestamps URH will calculate the sample rate from them. You can manually edit the sample rate after import in the signal details.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_3.setText(QCoreApplication.translate("DialogCSVImport", u"Timestamp Column:", None))
        self.label_2.setText(QCoreApplication.translate("DialogCSVImport", u"Q Data Column:", None))
        self.groupBox.setTitle(QCoreApplication.translate("DialogCSVImport", u"Preview", None))
        ___qtablewidgetitem = self.tableWidgetPreview.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("DialogCSVImport", u"Timestamp", None));
        ___qtablewidgetitem1 = self.tableWidgetPreview.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("DialogCSVImport", u"I", None));
        ___qtablewidgetitem2 = self.tableWidgetPreview.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("DialogCSVImport", u"Q", None));
        self.btnChooseFile.setText(QCoreApplication.translate("DialogCSVImport", u"...", None))
        self.label_4.setText(QCoreApplication.translate("DialogCSVImport", u"CSV Separator:", None))
        self.groupBoxFilePreview.setTitle(QCoreApplication.translate("DialogCSVImport", u"File Content (at most 100 rows)", None))
        self.label_5.setText(QCoreApplication.translate("DialogCSVImport", u"File to import:", None))
        self.btnAutoDefault.setText(QCoreApplication.translate("DialogCSVImport", u"Prevent Dialog From Close with Enter", None))
    # retranslateUi

