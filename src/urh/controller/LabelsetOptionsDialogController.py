from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from urh.models.DataRulesetTableModel import DataRulesetTableModel
from urh.signalprocessing.LabelSet import LabelSet
from urh.signalprocessing.Ruleset import DataRule
from urh.ui.ui_labelset_options import Ui_DialogLabelsetOptions


class LabelsetOptionsDialogController(QDialog):

    def __init__(self, labelset: LabelSet, parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogLabelsetOptions()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setWindowTitle(labelset.name)
        self.ruleset_table_model = DataRulesetTableModel(labelset.ruleset, parent=self)
        self.ui.tblViewRuleset.setModel(self.ruleset_table_model)

        self.ui.btnRemoveRule.setEnabled(len(labelset.ruleset) > 0)

        self.create_connects()

    def create_connects(self):
        self.ui.btnAddRule.clicked.connect(self.on_btn_add_rule_clicked)
        self.ui.btnRemoveRule.clicked.connect(self.on_btn_remove_rule_clicked)

    def on_btn_add_rule_clicked(self):
        self.ui.btnRemoveRule.setEnabled(True)
        self.ruleset_table_model.ruleset.append(DataRule(start=0, end=0, operator="=", target_value="1", value_type=0))
        self.ruleset_table_model.update()

    def on_btn_remove_rule_clicked(self):
        self.ruleset_table_model.ruleset.remove(self.ruleset_table_model.ruleset[-1])
        self.ruleset_table_model.update()
        self.ui.btnRemoveRule.setEnabled(len(self.ruleset_table_model.ruleset) > 0)