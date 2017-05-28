import copy

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog

from urh import constants
from urh.models.RulesetTableModel import RulesetTableModel
from urh.signalprocessing import Ruleset
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Ruleset import Rule, OPERATION_DESCRIPTION
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.ui_messagetype_options import Ui_DialogMessageType


class MessageTypeDialogController(QDialog):

    def __init__(self, message_type: MessageType, parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogMessageType()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        operator_descriptions = list(OPERATION_DESCRIPTION.values())
        operator_descriptions.sort()

        self.setWindowTitle(message_type.name)
        self.orig_message_type = copy.deepcopy(message_type)
        self.message_type = message_type
        self.ruleset_table_model = RulesetTableModel(message_type.ruleset, operator_descriptions, parent=self)
        self.ui.tblViewRuleset.setModel(self.ruleset_table_model)

        self.ui.btnRemoveRule.setEnabled(len(message_type.ruleset) > 0)
        self.set_ruleset_ui_status()

        self.ui.rbAssignAutomatically.setChecked(self.message_type.assigned_by_ruleset)
        self.ui.rbAssignManually.setChecked(self.message_type.assign_manually)

        self.ui.tblViewRuleset.setItemDelegateForColumn(2, ComboBoxDelegate(["Bit", "Hex", "ASCII"], parent=self))
        self.ui.tblViewRuleset.setItemDelegateForColumn(3, ComboBoxDelegate(operator_descriptions, parent=self))

        for i in range(len(message_type.ruleset)):
            self.open_editors(i)

        self.ui.cbRulesetMode.setCurrentIndex(self.message_type.ruleset.mode.value)

        self.create_connects()

        try:
            self.restoreGeometry(constants.SETTINGS.value("{}/geometry".format(self.__class__.__name__)))
        except TypeError:
            pass

    def create_connects(self):
        self.ui.btnAddRule.clicked.connect(self.on_btn_add_rule_clicked)
        self.ui.btnRemoveRule.clicked.connect(self.on_btn_remove_rule_clicked)
        self.ui.rbAssignAutomatically.clicked.connect(self.on_rb_assign_automatically_clicked)
        self.ui.rbAssignManually.clicked.connect(self.on_rb_assign_manually_clicked)
        self.ui.cbRulesetMode.currentIndexChanged.connect(self.on_cb_rulesetmode_current_index_changed)

        self.ui.btnSaveAndApply.clicked.connect(self.on_btn_save_and_apply_clicked)
        self.ui.btnClose.clicked.connect(self.on_btn_close_clicked)

    def set_ruleset_ui_status(self):
        self.ui.tblViewRuleset.setEnabled(self.message_type.assigned_by_ruleset)
        self.ui.btnRemoveRule.setEnabled(self.message_type.assigned_by_ruleset and len(self.message_type.ruleset) > 0)
        self.ui.btnAddRule.setEnabled(self.message_type.assigned_by_ruleset)
        self.ui.cbRulesetMode.setEnabled(self.message_type.assigned_by_ruleset)

    def open_editors(self, row):
        self.ui.tblViewRuleset.openPersistentEditor(self.ruleset_table_model.index(row, 2))
        self.ui.tblViewRuleset.openPersistentEditor(self.ruleset_table_model.index(row, 3))

    def closeEvent(self, event: QCloseEvent):
        self.ui.tblViewRuleset.setItemDelegateForColumn(2, None)
        self.ui.tblViewRuleset.setItemDelegateForColumn(3, None)
        constants.SETTINGS.setValue("{}/geometry".format(self.__class__.__name__), self.saveGeometry())
        super().closeEvent(event)

    @pyqtSlot()
    def on_btn_add_rule_clicked(self):
        self.ui.btnRemoveRule.setEnabled(True)
        self.message_type.ruleset.append(Rule(start=0, end=0, operator="=", target_value="1", value_type=0))
        self.ruleset_table_model.update()

        for i in range(len(self.message_type.ruleset)):
            self.open_editors(i)

    @pyqtSlot()
    def on_btn_close_clicked(self):
        self.message_type = self.orig_message_type
        self.close()

    @pyqtSlot()
    def on_btn_save_and_apply_clicked(self):
        self.close()

    @pyqtSlot()
    def on_btn_remove_rule_clicked(self):
        self.ruleset_table_model.ruleset.remove(self.message_type.ruleset[-1])
        self.ruleset_table_model.update()
        self.ui.btnRemoveRule.setEnabled(len(self.message_type.ruleset) > 0)

    @pyqtSlot()
    def on_rb_assign_automatically_clicked(self):
        self.message_type.assigned_by_ruleset = True
        self.set_ruleset_ui_status()

    @pyqtSlot()
    def on_rb_assign_manually_clicked(self):
        self.message_type.assigned_by_ruleset = False
        self.set_ruleset_ui_status()

    @pyqtSlot(int)
    def on_cb_rulesetmode_current_index_changed(self, index: int):
        self.message_type.ruleset.mode = Ruleset.Mode(index)
