import re

from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import pyqtSlot, Qt, QDir

from urh.models.SimulatorRulesetTableModel import SimulatorRulesetTableModel
from urh.models.GeneratorTreeModel import GeneratorTreeModel
from urh.models.SimulatorMessageFieldModel import SimulatorMessageFieldModel
from urh.util.ProjectManager import ProjectManager
from urh.ui.ui_simulator import Ui_SimulatorTab
from urh.ui.SimulatorScene import SimulatorScene, GotoAction, ExternalProgramAction
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.Ruleset import OPERATION_DESCRIPTION
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.SimulatorRuleset import SimulatorRuleset, SimulatorRulesetItem, Mode
from urh.signalprocessing.MessageItem import MessageItem
from urh.signalprocessing.RuleItem import RuleConditionItem, RuleItem, ConditionType

from urh.SimulatorProtocolManager import SimulatorProtocolManager

from urh.controller.CompareFrameController import CompareFrameController
from urh.controller.SimulateDialogController import SimulateDialogController

from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.delegates.MessageComboBoxDelegate import MessageComboBoxDelegate

class SimulatorTabController(QWidget):
    def __init__(self, compare_frame_controller: CompareFrameController,
                 project_manager: ProjectManager, parent):

        super().__init__(parent)

        self.project_manager = project_manager
        self.compare_frame_controller = compare_frame_controller
        self.proto_analyzer = compare_frame_controller.proto_analyzer

        self.sim_proto_manager = SimulatorProtocolManager(self.project_manager)

        self.ui = Ui_SimulatorTab()
        self.ui.setupUi(self)

        self.ui.splitter_2.setSizes([self.width() / 0.7, self.width() / 0.3])

        self.ui.treeProtocols.setHeaderHidden(True)
        self.tree_model = GeneratorTreeModel(compare_frame_controller)
        self.tree_model.set_root_item(compare_frame_controller.proto_tree_model.rootItem)
        self.tree_model.controller = self
        self.ui.treeProtocols.setModel(self.tree_model)

        self.simulator_message_field_model = SimulatorMessageFieldModel(self)
        self.ui.tblViewFieldValues.setModel(self.simulator_message_field_model)
        self.update_field_types()

        self.simulator_scene = SimulatorScene(controller=self)
        self.simulator_scene.tree_root_item = compare_frame_controller.proto_tree_model.rootItem
        self.ui.gvSimulator.setScene(self.simulator_scene)
        self.ui.gvSimulator.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.ui.gvSimulator.proto_analyzer = compare_frame_controller.proto_analyzer

        self.field_types = FieldType.load_from_xml()
        self.field_types_by_id = {field_type.id: field_type for field_type in self.field_types}
        self.field_types_by_caption = {field_type.caption: field_type for field_type in self.field_types}

        operator_descriptions = list(OPERATION_DESCRIPTION.values())
        operator_descriptions.sort()
        self.simulator_ruleset_model = SimulatorRulesetTableModel(operator_descriptions, parent=self)
        self.ui.tblViewSimulatorRuleset.setModel(self.simulator_ruleset_model)
        self.ui.tblViewSimulatorRuleset.setItemDelegateForColumn(0, MessageComboBoxDelegate(self.simulator_scene, parent=self))
        self.ui.tblViewSimulatorRuleset.setItemDelegateForColumn(1, ComboBoxDelegate(ProtocolLabel.DISPLAY_FORMATS, parent=self))
        self.ui.tblViewSimulatorRuleset.setItemDelegateForColumn(2, ComboBoxDelegate(operator_descriptions, parent=self))

        self.selected_item = None

        self.create_connects(compare_frame_controller)

    def update_field_types(self):
        self.field_types = FieldType.load_from_xml()
        self.field_types_by_id = {field_type.id: field_type for field_type in self.field_types}
        self.field_types_by_caption = {field_type.caption: field_type for field_type in self.field_types}
        self.update_field_name_column()

    def update_field_name_column(self):
        field_types = [ft.caption for ft in self.field_types]
        self.ui.tblViewFieldValues.setItemDelegateForColumn(0, ComboBoxDelegate(field_types, is_editable=True, return_index=False, parent=self))

    def create_connects(self, compare_frame_controller):
        self.ui.btnAddRule.clicked.connect(self.on_btn_add_rule_clicked)
        self.ui.btnRemoveRule.clicked.connect(self.on_btn_remove_rule_clicked)
        self.ui.btnChooseExtProg.clicked.connect(self.on_btn_choose_ext_prog_clicked)
        self.ui.extProgramLineEdit.textChanged.connect(self.on_ext_program_line_edit_text_changed)
        self.ui.cmdLineArgsLineEdit.textChanged.connect(self.on_cmd_line_args_line_edit_text_changed)
        self.project_manager.project_updated.connect(self.on_project_updated)
        compare_frame_controller.proto_tree_model.modelReset.connect(self.refresh_tree)
        self.ui.rbAllApply.toggled.connect(self.on_cb_rulesetmode_toggled)
        self.ui.rbOneApply.toggled.connect(self.on_cb_rulesetmode_toggled)

        self.simulator_scene.selectionChanged.connect(self.on_simulator_scene_selection_changed)
        self.simulator_scene.items_changed.connect(self.update_ui)

        self.ui.btnStartSim.clicked.connect(self.on_show_simulate_dialog_action_triggered)

        self.ui.btnNextNav.clicked.connect(self.on_btn_next_nav_clicked)
        self.ui.btnPrevNav.clicked.connect(self.on_btn_prev_nav_clicked)
        self.ui.navLineEdit.returnPressed.connect(self.on_nav_line_edit_return_pressed)
        self.ui.goto_combobox.activated.connect(self.on_goto_combobox_activated)

    def update_goto_combobox(self):
        item = self.simulator_scene.get_first_item()
        goto_combobox = self.ui.goto_combobox
        goto_combobox.clear()

        goto_combobox.addItem("---Select target---", None)

        while item:
            if item != self.selected_item and not (isinstance(item, RuleConditionItem)
            and (item.type == ConditionType.ELSE or item.type == ConditionType.ELSE_IF)):
                goto_combobox.addItem(item.index, item)

            item = item.next()

        if self.selected_item.goto_target:
            goto_combobox.setCurrentText(self.selected_item.goto_target.index)
        else:
            goto_combobox.setCurrentIndex(0)

    def update_ui(self):
        selected_items = self.simulator_scene.selectedItems()
        self.selected_item = None
        self.ui.goto_combobox.clear()

        if selected_items:
            self.selected_item = selected_items[0]
                
            self.ui.navLineEdit.setText(self.selected_item.index)

            self.ui.btnNextNav.setEnabled(not self.selected_item.is_last_item())
            self.ui.btnPrevNav.setEnabled(not self.selected_item.is_first_item())

            self.ui.lblMsgFieldsValues.setText(self.tr("Detail view for item #") + self.selected_item.index)

            if isinstance(self.selected_item, GotoAction):
                self.update_goto_combobox()
                self.ui.detail_view_widget.setCurrentIndex(1)
            elif isinstance(self.selected_item, MessageItem):
                self.simulator_message_field_model.message = self.selected_item.model_item
                self.simulator_message_field_model.update()

                self.ui.detail_view_widget.setCurrentIndex(2)
            elif isinstance(self.selected_item, RuleConditionItem) and self.selected_item.type != ConditionType.ELSE:
                self.ui.btnRemoveRule.setEnabled(len(self.selected_item.ruleset) > 0)
                self.simulator_ruleset_model.ruleset = self.selected_item.ruleset
                self.simulator_ruleset_model.update()

                if self.selected_item.ruleset.mode == Mode.all_apply:
                    self.ui.rbAllApply.setChecked(True)
                else:
                    self.ui.rbOneApply.setChecked(True)

                for i in range(len(self.selected_item.ruleset)):
                    self.open_ruleset_editors(i)

                self.ui.detail_view_widget.setCurrentIndex(3)
            elif isinstance(self.selected_item, ExternalProgramAction):
                self.ui.extProgramLineEdit.setText(self.selected_item.ext_prog)
                self.ui.cmdLineArgsLineEdit.setText(self.selected_item.args)
                self.ui.detail_view_widget.setCurrentIndex(4)
            else:
                self.ui.detail_view_widget.setCurrentIndex(0)
        else:
            self.ui.navLineEdit.clear()
            self.ui.btnNextNav.setEnabled(False)
            self.ui.btnPrevNav.setEnabled(False)

            self.ui.lblMsgFieldsValues.setText(self.tr("Detail view for item"))
            self.ui.detail_view_widget.setCurrentIndex(0)

    @pyqtSlot()
    def on_goto_combobox_activated(self):
        self.selected_item.goto_target = self.ui.goto_combobox.currentData()

    @pyqtSlot()
    def on_btn_next_nav_clicked(self):
        self.ui.gvSimulator.navigate_forward()

    @pyqtSlot()
    def on_btn_prev_nav_clicked(self):
        self.ui.gvSimulator.navigate_backward()

    @pyqtSlot()
    def on_simulator_scene_selection_changed(self):
        self.update_ui()

    @pyqtSlot()
    def on_show_simulate_dialog_action_triggered(self):
        s = SimulateDialogController(project_manager=self.project_manager, scene=self.simulator_scene, parent=self)
        s.show()

    @pyqtSlot()
    def on_nav_line_edit_return_pressed(self):
        items = self.simulator_scene.sim_items
        nav_text = self.ui.navLineEdit.text()
        target_item = None

        if re.match(r"^\d+(\.\d+){0,2}$", nav_text):
            index_list = nav_text.split(".")
            index_list = list(map(int, index_list))

            for index in index_list:
                if not items or index > len(items):
                    break

                target_item = items[index - 1]

                if isinstance(target_item, RuleItem):
                    items = target_item.conditions
                    target_item =  target_item.conditions[0]
                elif isinstance(target_item, RuleConditionItem):
                    items = target_item.sim_items
                else:
                    items = None

        if target_item:
            self.ui.gvSimulator.jump_to_item(target_item)
        else:
            self.update_ui()
                    
    def on_project_updated(self):
        self.simulator_scene.update_view()

    def open_ruleset_editors(self, row):
        self.ui.tblViewSimulatorRuleset.openPersistentEditor(self.simulator_ruleset_model.index(row, 0))
        self.ui.tblViewSimulatorRuleset.openPersistentEditor(self.simulator_ruleset_model.index(row, 1))
        self.ui.tblViewSimulatorRuleset.openPersistentEditor(self.simulator_ruleset_model.index(row, 2))

    @pyqtSlot(bool)
    def on_cb_rulesetmode_toggled(self, checked: bool):
        if self.ui.rbAllApply.isChecked():
            self.selected_item.ruleset.mode = Mode(0)
        else:
            self.selected_item.ruleset.mode = Mode(1)

    @pyqtSlot()
    def on_btn_add_rule_clicked(self):
        self.ui.btnRemoveRule.setEnabled(True)
        self.selected_item.ruleset.append(SimulatorRulesetItem(variable=None, operator="=", target_value="1", value_type=0))
        self.simulator_ruleset_model.update()

        for i in range(len(self.selected_item.ruleset)):
            self.open_ruleset_editors(i)

    @pyqtSlot()
    def on_btn_remove_rule_clicked(self):
        self.selected_item.ruleset.remove(self.selected_item.ruleset[-1])
        self.simulator_ruleset_model.update()
        self.ui.btnRemoveRule.setEnabled(len(self.selected_item.ruleset) > 0)

        for i in range(len(self.selected_item.ruleset)):
            self.open_ruleset_editors(i)

    @pyqtSlot()
    def on_btn_choose_ext_prog_clicked(self):
        file_name, ok = QFileDialog.getOpenFileName(self, self.tr("Choose external program"), QDir.homePath())

        if file_name and ok:
            self.ui.extProgramLineEdit.setText(file_name)

    @pyqtSlot()
    def on_ext_program_line_edit_text_changed(self):
        self.selected_item.ext_prog = self.ui.extProgramLineEdit.text()

    @pyqtSlot()
    def on_cmd_line_args_line_edit_text_changed(self):
        self.selected_item.args = self.ui.cmdLineArgsLineEdit.text()

    @pyqtSlot()
    def refresh_tree(self):
        self.tree_model.beginResetModel()
        self.tree_model.endResetModel()
        self.ui.treeProtocols.expandAll()

    def close_all(self):
        self.tree_model.rootItem.clearChilds()
        self.tree_model.rootItem.addGroup()
        self.refresh_tree()