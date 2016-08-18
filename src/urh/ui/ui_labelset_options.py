# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogLabelsetOptions(object):
    def setupUi(self, DialogLabelsetOptions):
        DialogLabelsetOptions.setObjectName("DialogLabelsetOptions")
        DialogLabelsetOptions.resize(471, 359)
        self.gridLayout = QtWidgets.QGridLayout(DialogLabelsetOptions)
        self.gridLayout.setObjectName("gridLayout")
        self.rbAssignManually = QtWidgets.QRadioButton(DialogLabelsetOptions)
        self.rbAssignManually.setObjectName("rbAssignManually")
        self.gridLayout.addWidget(self.rbAssignManually, 0, 0, 1, 1)
        self.rbAssignAutomatically = QtWidgets.QRadioButton(DialogLabelsetOptions)
        self.rbAssignAutomatically.setObjectName("rbAssignAutomatically")
        self.gridLayout.addWidget(self.rbAssignAutomatically, 0, 1, 1, 1)
        self.cbRulesetMode = QtWidgets.QComboBox(DialogLabelsetOptions)
        self.cbRulesetMode.setObjectName("cbRulesetMode")
        self.cbRulesetMode.addItem("")
        self.cbRulesetMode.addItem("")
        self.cbRulesetMode.addItem("")
        self.gridLayout.addWidget(self.cbRulesetMode, 1, 0, 1, 2)
        self.tblViewRuleset = QtWidgets.QTableView(DialogLabelsetOptions)
        self.tblViewRuleset.setObjectName("tblViewRuleset")
        self.gridLayout.addWidget(self.tblViewRuleset, 2, 0, 3, 2)
        self.btnAddRule = QtWidgets.QToolButton(DialogLabelsetOptions)
        icon = QtGui.QIcon.fromTheme("list-add")
        self.btnAddRule.setIcon(icon)
        self.btnAddRule.setObjectName("btnAddRule")
        self.gridLayout.addWidget(self.btnAddRule, 2, 2, 1, 1)
        self.btnRemoveRule = QtWidgets.QToolButton(DialogLabelsetOptions)
        icon = QtGui.QIcon.fromTheme("list-remove")
        self.btnRemoveRule.setIcon(icon)
        self.btnRemoveRule.setObjectName("btnRemoveRule")
        self.gridLayout.addWidget(self.btnRemoveRule, 3, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 145, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 2, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnSaveAndApply = QtWidgets.QPushButton(DialogLabelsetOptions)
        self.btnSaveAndApply.setObjectName("btnSaveAndApply")
        self.horizontalLayout.addWidget(self.btnSaveAndApply)
        self.btnClose = QtWidgets.QPushButton(DialogLabelsetOptions)
        self.btnClose.setObjectName("btnClose")
        self.horizontalLayout.addWidget(self.btnClose)
        self.gridLayout.addLayout(self.horizontalLayout, 5, 0, 1, 2)

        self.retranslateUi(DialogLabelsetOptions)
        QtCore.QMetaObject.connectSlotsByName(DialogLabelsetOptions)

    def retranslateUi(self, DialogLabelsetOptions):
        _translate = QtCore.QCoreApplication.translate
        DialogLabelsetOptions.setWindowTitle(_translate("DialogLabelsetOptions", "Dialog"))
        self.rbAssignManually.setText(_translate("DialogLabelsetOptions", "Assi&gn manually"))
        self.rbAssignAutomatically.setText(_translate("DialogLabelsetOptions", "Assign a&utomatically"))
        self.cbRulesetMode.setItemText(0, _translate("DialogLabelsetOptions", "All rules must apply (AND)"))
        self.cbRulesetMode.setItemText(1, _translate("DialogLabelsetOptions", "At leat one rule must apply (OR)"))
        self.cbRulesetMode.setItemText(2, _translate("DialogLabelsetOptions", "No rule must apply (NOR)"))
        self.btnAddRule.setToolTip(_translate("DialogLabelsetOptions", "Add ruleset"))
        self.btnAddRule.setText(_translate("DialogLabelsetOptions", "..."))
        self.btnRemoveRule.setToolTip(_translate("DialogLabelsetOptions", "Remove ruleset"))
        self.btnRemoveRule.setText(_translate("DialogLabelsetOptions", "..."))
        self.btnSaveAndApply.setText(_translate("DialogLabelsetOptions", "Save and apply"))
        self.btnClose.setText(_translate("DialogLabelsetOptions", "Close"))

