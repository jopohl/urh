import copy

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from urh.models.RulesetTableModel import RulesetTableModel
from urh.signalprocessing import Ruleset
from urh.signalprocessing.LabelSet import LabelSet
from urh.signalprocessing.Ruleset import Rule, OPERATION_DESCRIPTION
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.ui_labelset_options import Ui_DialogLabelsetOptions


class LabelsetOptionsDialogController(QDialog):

    def __init__(self, labelset: LabelSet, parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogLabelsetOptions()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        operator_descriptions = list(OPERATION_DESCRIPTION.values())
        operator_descriptions.sort()

        self.setWindowTitle(labelset.name)
        self.orig_labelset = copy.deepcopy(labelset)
        self.labelset = labelset
        self.ruleset_table_model = RulesetTableModel(labelset.ruleset, operator_descriptions, parent=self)
        self.ui.tblViewRuleset.setModel(self.ruleset_table_model)

        self.ui.btnRemoveRule.setEnabled(len(labelset.ruleset) > 0)
        self.set_ruleset_ui_status()

        self.ui.rbAssignAutomatically.setChecked(self.labelset.assigned_automatically)
        self.ui.rbAssignManually.setChecked(self.labelset.assign_manually)

        self.ui.tblViewRuleset.setItemDelegateForColumn(2, ComboBoxDelegate(["Bit", "Hex", "ASCII"], parent=self))
        self.ui.tblViewRuleset.setItemDelegateForColumn(3, ComboBoxDelegate(operator_descriptions, parent=self))

        for i in range(len(labelset.ruleset)):
            self.open_editors(i)

        self.ui.cbRulesetMode.setCurrentIndex(self.labelset.ruleset.mode.value)

        self.create_connects()

    def create_connects(self):
        self.ui.btnAddRule.clicked.connect(self.on_btn_add_rule_clicked)
        self.ui.btnRemoveRule.clicked.connect(self.on_btn_remove_rule_clicked)
        self.ui.rbAssignAutomatically.clicked.connect(self.on_rb_assign_automatically_clicked)
        self.ui.rbAssignManually.clicked.connect(self.on_rb_assign_manually_clicked)
        self.ui.cbRulesetMode.currentIndexChanged.connect(self.on_cb_rulesetmode_current_index_changed)

        self.ui.btnSaveAndApply.clicked.connect(self.on_btn_save_and_apply_clicked)
        self.ui.btnClose.clicked.connect(self.on_btn_close_clicked)

    def on_btn_add_rule_clicked(self):
        self.ui.btnRemoveRule.setEnabled(True)
        self.labelset.ruleset.append(Rule(start=0, end=0, operator="=", target_value="1", value_type=0))
        self.ruleset_table_model.update()

        for i in range(len(self.labelset.ruleset)):
            self.open_editors(i)

    def on_btn_close_clicked(self):
        self.labelset = self.orig_labelset
        self.close()

    def on_btn_save_and_apply_clicked(self):
        self.close()

    def on_btn_remove_rule_clicked(self):
        self.ruleset_table_model.ruleset.remove(self.labelset.ruleset[-1])
        self.ruleset_table_model.update()
        self.ui.btnRemoveRule.setEnabled(len(self.labelset.ruleset) > 0)

    def on_rb_assign_automatically_clicked(self):
        self.labelset.assigned_automatically = True
        self.set_ruleset_ui_status()

    def on_rb_assign_manually_clicked(self):
        self.labelset.assigned_automatically = False
        self.set_ruleset_ui_status()

    def set_ruleset_ui_status(self):
        self.ui.tblViewRuleset.setEnabled(self.labelset.assigned_automatically)
        self.ui.btnRemoveRule.setEnabled(self.labelset.assigned_automatically and len(self.labelset.ruleset) > 0)
        self.ui.btnAddRule.setEnabled(self.labelset.assigned_automatically)
        self.ui.cbRulesetMode.setEnabled(self.labelset.assigned_automatically)

    def open_editors(self, row):
        self.ui.tblViewRuleset.openPersistentEditor(self.ruleset_table_model.index(row, 2))
        self.ui.tblViewRuleset.openPersistentEditor(self.ruleset_table_model.index(row, 3))

    def on_cb_rulesetmode_current_index_changed(self):
        self.labelset.ruleset.mode = Ruleset.Mode(self.ui.cbRulesetMode.currentIndex())