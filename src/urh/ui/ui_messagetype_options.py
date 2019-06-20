# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/joe/GIT/urh/data/ui/messagetype_options.ui',
# licensing of '/home/joe/GIT/urh/data/ui/messagetype_options.ui' applies.
#
# Created: Thu Jun 20 11:48:50 2019
#      by: pyside2-uic  running on PySide2 5.12.3
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

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
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("."), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        self.btnAddRule.setIcon(icon)
        self.btnAddRule.setObjectName("btnAddRule")
        self.gridLayout.addWidget(self.btnAddRule, 2, 2, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogMessageType)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)

        self.retranslateUi(DialogMessageType)

    def retranslateUi(self, DialogMessageType):
        DialogMessageType.setWindowTitle(QtWidgets.QApplication.translate("DialogMessageType", "Dialog", None, -1))
        self.cbRulesetMode.setItemText(0, QtWidgets.QApplication.translate("DialogMessageType", "All rules must apply (AND)", None, -1))
        self.cbRulesetMode.setItemText(1, QtWidgets.QApplication.translate("DialogMessageType", "At leat one rule must apply (OR)", None, -1))
        self.cbRulesetMode.setItemText(2, QtWidgets.QApplication.translate("DialogMessageType", "No rule must apply (NOR)", None, -1))
        self.btnRemoveRule.setToolTip(QtWidgets.QApplication.translate("DialogMessageType", "Remove ruleset", None, -1))
        self.btnRemoveRule.setText(QtWidgets.QApplication.translate("DialogMessageType", "...", None, -1))
        self.rbAssignManually.setText(QtWidgets.QApplication.translate("DialogMessageType", "Assi&gn manually", None, -1))
        self.rbAssignAutomatically.setText(QtWidgets.QApplication.translate("DialogMessageType", "Assign a&utomatically", None, -1))
        self.btnAddRule.setToolTip(QtWidgets.QApplication.translate("DialogMessageType", "Add ruleset", None, -1))
        self.btnAddRule.setText(QtWidgets.QApplication.translate("DialogMessageType", "...", None, -1))

