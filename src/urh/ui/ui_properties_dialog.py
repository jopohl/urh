# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogLabels(object):
    def setupUi(self, DialogLabels):
        DialogLabels.setObjectName("DialogLabels")
        DialogLabels.resize(714, 463)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(DialogLabels)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBoxSettings = QtWidgets.QGroupBox(DialogLabels)
        self.groupBoxSettings.setObjectName("groupBoxSettings")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBoxSettings)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tblViewProtoLabels = ProtocolLabelTableView(self.groupBoxSettings)
        self.tblViewProtoLabels.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tblViewProtoLabels.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tblViewProtoLabels.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tblViewProtoLabels.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tblViewProtoLabels.setObjectName("tblViewProtoLabels")
        self.verticalLayout.addWidget(self.tblViewProtoLabels)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.groupBoxSettings)
        font = QtGui.QFont()
        font.setUnderline(False)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.cbProtoView = QtWidgets.QComboBox(self.groupBoxSettings)
        self.cbProtoView.setObjectName("cbProtoView")
        self.cbProtoView.addItem("")
        self.cbProtoView.addItem("")
        self.cbProtoView.addItem("")
        self.horizontalLayout_2.addWidget(self.cbProtoView)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3.addWidget(self.groupBoxSettings)
        self.groupBoxAdvancedSettings = QtWidgets.QGroupBox(DialogLabels)
        self.groupBoxAdvancedSettings.setObjectName("groupBoxAdvancedSettings")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBoxAdvancedSettings)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabWidgetAdvancedSettings = QtWidgets.QTabWidget(self.groupBoxAdvancedSettings)
        self.tabWidgetAdvancedSettings.setObjectName("tabWidgetAdvancedSettings")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tabWidgetAdvancedSettings.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidgetAdvancedSettings.addTab(self.tab_2, "")
        self.verticalLayout_2.addWidget(self.tabWidgetAdvancedSettings)
        self.verticalLayout_3.addWidget(self.groupBoxAdvancedSettings)
        self.btnConfirm = QtWidgets.QPushButton(DialogLabels)
        self.btnConfirm.setObjectName("btnConfirm")
        self.verticalLayout_3.addWidget(self.btnConfirm)

        self.retranslateUi(DialogLabels)
        QtCore.QMetaObject.connectSlotsByName(DialogLabels)

    def retranslateUi(self, DialogLabels):
        _translate = QtCore.QCoreApplication.translate
        DialogLabels.setWindowTitle(_translate("DialogLabels", "Manage Protocol Labels"))
        self.groupBoxSettings.setTitle(_translate("DialogLabels", "Protocol Label Settings"))
        self.label.setText(_translate("DialogLabels", "View Type:"))
        self.cbProtoView.setItemText(0, _translate("DialogLabels", "Bits"))
        self.cbProtoView.setItemText(1, _translate("DialogLabels", "Hex"))
        self.cbProtoView.setItemText(2, _translate("DialogLabels", "ASCII"))
        self.groupBoxAdvancedSettings.setTitle(_translate("DialogLabels", "Advanced Settings"))
        self.tabWidgetAdvancedSettings.setTabText(self.tabWidgetAdvancedSettings.indexOf(self.tab), _translate("DialogLabels", "Tab 1"))
        self.tabWidgetAdvancedSettings.setTabText(self.tabWidgetAdvancedSettings.indexOf(self.tab_2), _translate("DialogLabels", "Tab 2"))
        self.btnConfirm.setText(_translate("DialogLabels", "Confirm"))

from urh.ui.views.ProtocolLabelTableView import ProtocolLabelTableView
