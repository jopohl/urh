# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'properties_dialog.ui'
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

from urh.ui.views.ProtocolLabelTableView import ProtocolLabelTableView

import urh.ui.urh_rc

class Ui_DialogLabels(object):
    def setupUi(self, DialogLabels):
        if DialogLabels.objectName():
            DialogLabels.setObjectName(u"DialogLabels")
        DialogLabels.resize(714, 463)
        self.verticalLayout_3 = QVBoxLayout(DialogLabels)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.splitter = QSplitter(DialogLabels)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setStyleSheet(u"QSplitter::handle:vertical {\n"
"margin: 4px 0px;\n"
"    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, \n"
"stop:0 rgba(255, 255, 255, 0), \n"
"stop:0.5 rgba(100, 100, 100, 100), \n"
"stop:1 rgba(255, 255, 255, 0));\n"
"	image: url(:/icons/icons/splitter_handle_horizontal.svg);\n"
"}")
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setHandleWidth(6)
        self.splitter.setChildrenCollapsible(False)
        self.groupBoxSettings = QGroupBox(self.splitter)
        self.groupBoxSettings.setObjectName(u"groupBoxSettings")
        self.verticalLayout = QVBoxLayout(self.groupBoxSettings)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tblViewProtoLabels = ProtocolLabelTableView(self.groupBoxSettings)
        self.tblViewProtoLabels.setObjectName(u"tblViewProtoLabels")
        self.tblViewProtoLabels.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tblViewProtoLabels.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.tblViewProtoLabels.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tblViewProtoLabels.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tblViewProtoLabels.setShowGrid(False)

        self.verticalLayout.addWidget(self.tblViewProtoLabels)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.groupBoxSettings)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setUnderline(False)
        self.label.setFont(font)

        self.horizontalLayout_2.addWidget(self.label)

        self.cbProtoView = QComboBox(self.groupBoxSettings)
        self.cbProtoView.addItem("")
        self.cbProtoView.addItem("")
        self.cbProtoView.addItem("")
        self.cbProtoView.setObjectName(u"cbProtoView")

        self.horizontalLayout_2.addWidget(self.cbProtoView)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.splitter.addWidget(self.groupBoxSettings)
        self.groupBoxAdvancedSettings = QGroupBox(self.splitter)
        self.groupBoxAdvancedSettings.setObjectName(u"groupBoxAdvancedSettings")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxAdvancedSettings)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tabWidgetAdvancedSettings = QTabWidget(self.groupBoxAdvancedSettings)
        self.tabWidgetAdvancedSettings.setObjectName(u"tabWidgetAdvancedSettings")

        self.verticalLayout_2.addWidget(self.tabWidgetAdvancedSettings)

        self.splitter.addWidget(self.groupBoxAdvancedSettings)

        self.verticalLayout_3.addWidget(self.splitter)

        self.btnConfirm = QPushButton(DialogLabels)
        self.btnConfirm.setObjectName(u"btnConfirm")

        self.verticalLayout_3.addWidget(self.btnConfirm)


        self.retranslateUi(DialogLabels)
    # setupUi

    def retranslateUi(self, DialogLabels):
        DialogLabels.setWindowTitle(QCoreApplication.translate("DialogLabels", u"Manage Protocol Labels", None))
        self.groupBoxSettings.setTitle(QCoreApplication.translate("DialogLabels", u"Protocol Label Settings", None))
        self.label.setText(QCoreApplication.translate("DialogLabels", u"Start/End values refer to view type:", None))
        self.cbProtoView.setItemText(0, QCoreApplication.translate("DialogLabels", u"Bits", None))
        self.cbProtoView.setItemText(1, QCoreApplication.translate("DialogLabels", u"Hex", None))
        self.cbProtoView.setItemText(2, QCoreApplication.translate("DialogLabels", u"ASCII", None))

        self.groupBoxAdvancedSettings.setTitle(QCoreApplication.translate("DialogLabels", u"Advanced Settings", None))
        self.btnConfirm.setText(QCoreApplication.translate("DialogLabels", u"Confirm", None))
    # retranslateUi

