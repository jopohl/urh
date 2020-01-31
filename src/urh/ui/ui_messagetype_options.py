# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'messagetype_options.ui'
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


class Ui_DialogMessageType(object):
    def setupUi(self, DialogMessageType):
        if DialogMessageType.objectName():
            DialogMessageType.setObjectName(u"DialogMessageType")
        DialogMessageType.resize(471, 359)
        self.gridLayout = QGridLayout(DialogMessageType)
        self.gridLayout.setObjectName(u"gridLayout")
        self.cbRulesetMode = QComboBox(DialogMessageType)
        self.cbRulesetMode.addItem("")
        self.cbRulesetMode.addItem("")
        self.cbRulesetMode.addItem("")
        self.cbRulesetMode.setObjectName(u"cbRulesetMode")

        self.gridLayout.addWidget(self.cbRulesetMode, 1, 0, 1, 2)

        self.tblViewRuleset = QTableView(DialogMessageType)
        self.tblViewRuleset.setObjectName(u"tblViewRuleset")
        self.tblViewRuleset.setShowGrid(False)

        self.gridLayout.addWidget(self.tblViewRuleset, 2, 0, 3, 2)

        self.btnRemoveRule = QToolButton(DialogMessageType)
        self.btnRemoveRule.setObjectName(u"btnRemoveRule")
        icon = QIcon()
        iconThemeName = u"list-remove"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnRemoveRule.setIcon(icon)

        self.gridLayout.addWidget(self.btnRemoveRule, 3, 2, 1, 1)

        self.rbAssignManually = QRadioButton(DialogMessageType)
        self.rbAssignManually.setObjectName(u"rbAssignManually")

        self.gridLayout.addWidget(self.rbAssignManually, 0, 0, 1, 1)

        self.rbAssignAutomatically = QRadioButton(DialogMessageType)
        self.rbAssignAutomatically.setObjectName(u"rbAssignAutomatically")

        self.gridLayout.addWidget(self.rbAssignAutomatically, 0, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 145, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 4, 2, 1, 1)

        self.btnAddRule = QToolButton(DialogMessageType)
        self.btnAddRule.setObjectName(u"btnAddRule")
        icon1 = QIcon()
        iconThemeName = u"list-add"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btnAddRule.setIcon(icon1)

        self.gridLayout.addWidget(self.btnAddRule, 2, 2, 1, 1)

        self.buttonBox = QDialogButtonBox(DialogMessageType)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)


        self.retranslateUi(DialogMessageType)
    # setupUi

    def retranslateUi(self, DialogMessageType):
        DialogMessageType.setWindowTitle(QCoreApplication.translate("DialogMessageType", u"Dialog", None))
        self.cbRulesetMode.setItemText(0, QCoreApplication.translate("DialogMessageType", u"All rules must apply (AND)", None))
        self.cbRulesetMode.setItemText(1, QCoreApplication.translate("DialogMessageType", u"At leat one rule must apply (OR)", None))
        self.cbRulesetMode.setItemText(2, QCoreApplication.translate("DialogMessageType", u"No rule must apply (NOR)", None))

#if QT_CONFIG(tooltip)
        self.btnRemoveRule.setToolTip(QCoreApplication.translate("DialogMessageType", u"Remove ruleset", None))
#endif // QT_CONFIG(tooltip)
        self.btnRemoveRule.setText(QCoreApplication.translate("DialogMessageType", u"...", None))
        self.rbAssignManually.setText(QCoreApplication.translate("DialogMessageType", u"Assi&gn manually", None))
        self.rbAssignAutomatically.setText(QCoreApplication.translate("DialogMessageType", u"Assign a&utomatically", None))
#if QT_CONFIG(tooltip)
        self.btnAddRule.setToolTip(QCoreApplication.translate("DialogMessageType", u"Add ruleset", None))
#endif // QT_CONFIG(tooltip)
        self.btnAddRule.setText(QCoreApplication.translate("DialogMessageType", u"...", None))
    # retranslateUi

