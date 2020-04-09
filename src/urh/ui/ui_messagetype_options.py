# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DialogMessageType(object):
    def setupUi(self, DialogMessageType):
        DialogMessageType.setObjectName("DialogMessageType")
        DialogMessageType.resize(471, 359)
        self.gridLayout = QtWidgets.QGridLayout(DialogMessageType)
        self.gridLayout.setObjectName("gridLayout")
        self.cbRulesetMode = QtWidgets.QComboBox(DialogMessageType)
        self.cbRulesetMode.setObjectName("cbRulesetMode")
        self.cbRulesetMode.addItem("")
        self.cbRulesetMode.addItem("")
        self.cbRulesetMode.addItem("")
        self.gridLayout.addWidget(self.cbRulesetMode, 1, 0, 1, 2)
        self.tblViewRuleset = QtWidgets.QTableView(DialogMessageType)
        self.tblViewRuleset.setShowGrid(False)
        self.tblViewRuleset.setObjectName("tblViewRuleset")
        self.gridLayout.addWidget(self.tblViewRuleset, 2, 0, 3, 2)
        self.btnRemoveRule = QtWidgets.QToolButton(DialogMessageType)
        icon = QtGui.QIcon.fromTheme("list-remove")
        self.btnRemoveRule.setIcon(icon)
        self.btnRemoveRule.setObjectName("btnRemoveRule")
        self.gridLayout.addWidget(self.btnRemoveRule, 3, 2, 1, 1)
        self.rbAssignManually = QtWidgets.QRadioButton(DialogMessageType)
        self.rbAssignManually.setObjectName("rbAssignManually")
        self.gridLayout.addWidget(self.rbAssignManually, 0, 0, 1, 1)
        self.rbAssignAutomatically = QtWidgets.QRadioButton(DialogMessageType)
        self.rbAssignAutomatically.setObjectName("rbAssignAutomatically")
        self.gridLayout.addWidget(self.rbAssignAutomatically, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 145, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 2, 1, 1)
        self.btnAddRule = QtWidgets.QToolButton(DialogMessageType)
        icon = QtGui.QIcon.fromTheme("list-add")
        self.btnAddRule.setIcon(icon)
        self.btnAddRule.setObjectName("btnAddRule")
        self.gridLayout.addWidget(self.btnAddRule, 2, 2, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogMessageType)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)

        self.retranslateUi(DialogMessageType)

    def retranslateUi(self, DialogMessageType):
        _translate = QtCore.QCoreApplication.translate
        DialogMessageType.setWindowTitle(_translate("DialogMessageType", "Dialog"))
        self.cbRulesetMode.setItemText(0, _translate("DialogMessageType", "All rules must apply (AND)"))
        self.cbRulesetMode.setItemText(1, _translate("DialogMessageType", "At least one rule must apply (OR)"))
        self.cbRulesetMode.setItemText(2, _translate("DialogMessageType", "No rule must apply (NOR)"))
        self.btnRemoveRule.setToolTip(_translate("DialogMessageType", "Remove ruleset"))
        self.btnRemoveRule.setText(_translate("DialogMessageType", "..."))
        self.rbAssignManually.setText(_translate("DialogMessageType", "Assi&gn manually"))
        self.rbAssignAutomatically.setText(_translate("DialogMessageType", "Assign a&utomatically"))
        self.btnAddRule.setToolTip(_translate("DialogMessageType", "Add ruleset"))
        self.btnAddRule.setText(_translate("DialogMessageType", "..."))
