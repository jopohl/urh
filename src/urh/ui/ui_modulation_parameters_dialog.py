# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'modulation_parameters_dialog.ui'
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

class Ui_DialogModulationParameters(object):
    def setupUi(self, DialogModulationParameters):
        if DialogModulationParameters.objectName():
            DialogModulationParameters.setObjectName(u"DialogModulationParameters")
        DialogModulationParameters.resize(303, 286)
        DialogModulationParameters.setModal(True)
        self.verticalLayout = QVBoxLayout(DialogModulationParameters)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tblSymbolParameters = QTableWidget(DialogModulationParameters)
        if (self.tblSymbolParameters.columnCount() < 2)
            self.tblSymbolParameters.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.tblSymbolParameters.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tblSymbolParameters.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        if (self.tblSymbolParameters.rowCount() < 2)
            self.tblSymbolParameters.setRowCount(2)
        self.tblSymbolParameters.setObjectName(u"tblSymbolParameters")
        self.tblSymbolParameters.setShowGrid(False)
        self.tblSymbolParameters.setRowCount(2)
        self.tblSymbolParameters.horizontalHeader().setVisible(True)
        self.tblSymbolParameters.verticalHeader().setVisible(False)

        self.verticalLayout.addWidget(self.tblSymbolParameters)

        self.buttonBox = QDialogButtonBox(DialogModulationParameters)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(DialogModulationParameters)
    # setupUi

    def retranslateUi(self, DialogModulationParameters):
        DialogModulationParameters.setWindowTitle(QCoreApplication.translate("DialogModulationParameters", u"Modulation Parameters", None))
        ___qtablewidgetitem = self.tblSymbolParameters.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("DialogModulationParameters", u"Symbol", None));
        ___qtablewidgetitem1 = self.tblSymbolParameters.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("DialogModulationParameters", u"Amplitude", None));
    # retranslateUi

