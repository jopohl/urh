import re

from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import pyqtSlot, Qt, QDir

from urh.models.SimulatorRulesetTableModel import SimulatorRulesetTableModel
from urh.models.GeneratorTreeModel import GeneratorTreeModel
from urh.models.SimulatorMessageFieldModel import SimulatorMessageFieldModel
from urh.models.SimulatorMessageTableModel import SimulatorMessageTableModel
from urh.util.ProjectManager import ProjectManager
from urh.ui.ui_simulator import Ui_SimulatorTab
from urh.ui.SimulatorScene import SimulatorScene, GotoActionItem, ProgramActionItem
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.Ruleset import OPERATION_DESCRIPTION
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.SimulatorRuleset import SimulatorRuleset, SimulatorRulesetItem, Mode
from urh.signalprocessing.MessageItem import MessageItem
from urh.signalprocessing.RuleItem import RuleConditionItem
from urh.signalprocessing.SimulatorRule import SimulatorRule, ConditionType
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel

from urh.SimulatorProtocolManager import SimulatorProtocolManager

from urh.controller.CompareFrameController import CompareFrameController
from urh.controller.SimulateDialogController import SimulateDialogController
from urh.controller.ProtocolLabelDialog import ProtocolLabelDialog

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

        self.simulator_message_table_model = SimulatorMessageTableModel(self)
        self.ui.tblViewMessage.setModel(self.simulator_message_table_model)

        self.simulator_scene = SimulatorScene(controller=self)
        self.simulator_scene.tree_root_item = compare_frame_controller.proto_tree_model.rootItem
        self.ui.gvSimulator.setScene(self.simulator_scene)
        self.ui.gvSimulator.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.ui.gvSimulator.proto_analyzer = compare_frame_controller.proto_analyzer
        self.ui.gvSimulator.sim_proto_manager = self.sim_proto_manager

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
        self.selected_model_item = None

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
        compare_frame_controller.proto_tree_model.modelReset.connect(self.refresh_tree)
        self.ui.rbAllApply.toggled.connect(self.on_cb_rulesetmode_toggled)
        self.ui.rbOneApply.toggled.connect(self.on_cb_rulesetmode_toggled)

        self.simulator_scene.selectionChanged.connect(self.on_simulator_scene_selection_changed)

        self.ui.btnStartSim.clicked.connect(self.on_show_simulate_dialog_action_triggered)

        self.ui.btnNextNav.clicked.connect(self.on_btn_next_nav_clicked)
        self.ui.btnPrevNav.clicked.connect(self.on_btn_prev_nav_clicked)
        self.ui.navLineEdit.returnPressed.connect(self.on_nav_line_edit_return_pressed)
        self.ui.goto_combobox.activated.connect(self.on_goto_combobox_activated)

        self.simulator_message_field_model.protocol_label_updated.connect(self.sim_proto_manager.item_updated.emit)
        self.ui.gvSimulator.message_updated.connect(self.sim_proto_manager.item_updated.emit)

        self.ui.cbViewType.currentIndexChanged.connect(self.on_view_type_changed)
        self.ui.tblViewMessage.create_fuzzing_label_clicked.connect(self.create_fuzzing_label)

    @pyqtSlot(int, int)
    def create_fuzzing_label(self, start: int, end: int):
        con = self.simulator_message_table_model.protocol
        start, end = con.convert_range(start, end, self.ui.cbViewType.currentIndex(), 0, False, 0)
        lbl = self.sim_proto_manager.add_label(start=start, end=end, parent_item=con.messages[0])
        self.show_protocol_label_dialog(lbl)

    def show_protocol_label_dialog(self, label: SimulatorProtocolLabel):
        if label is not None:
            pld = ProtocolLabelDialog(label=label, parent=self)
            pld.show()

    def refresh_label(self, label: SimulatorProtocolLabel):
        self.sim_proto_manager.label_updated.emit(label)

    def update_goto_combobox(self):
        goto_combobox = self.ui.goto_combobox
        goto_combobox.clear()

        goto_combobox.addItem("---Select target---", None)

        items = self.sim_proto_manager.get_all_items()

        for item in items:
            if (isinstance(item, SimulatorProtocolLabel) or
                    isinstance(item, SimulatorRule)):
                continue

            goto_combobox.addItem(item.index(), item)

        if self.selected_model_item.goto_target:
            goto_combobox.setCurrentText(self.selected_model_item.goto_target.index())
        else:
            goto_combobox.setCurrentIndex(0)

    def update_ui(self):
        selected_items = self.simulator_scene.selectedItems()
        self.selected_item = None
        self.selected_model_item = None
        self.ui.goto_combobox.clear()

        if selected_items:
            self.selected_item = selected_items[0]
            self.selected_model_item = self.selected_item.model_item
                
            self.ui.navLineEdit.setText(self.selected_model_item.index())
            self.ui.btnNextNav.setEnabled(not self.selected_item.next() is None)
            self.ui.btnPrevNav.setEnabled(not self.selected_item.prev() is None)

            self.ui.lblMsgFieldsValues.setText(self.tr("Detail view for item #") + self.selected_model_item.index())

            if isinstance(self.selected_item, GotoActionItem):
                self.update_goto_combobox()
                self.ui.detail_view_widget.setCurrentIndex(1)
            elif isinstance(self.selected_item, MessageItem):
                #self.simulator_message_table_model.protocol.messages[:] = []
                #self.simulator_message_table_model.protocol.messages.append(self.selected_model_item)
                #self.simulator_message_table_model.update()
                #self.ui.tblViewMessage.resize_columns()

                self.simulator_message_field_model.message = self.selected_model_item
                self.simulator_message_field_model.update()

                self.ui.detail_view_widget.setCurrentIndex(2)
            elif (isinstance(self.selected_item, RuleConditionItem) and
                    self.selected_model_item.type != ConditionType.ELSE):
                self.ui.btnRemoveRule.setEnabled(len(self.selected_model_item.ruleset) > 0)
                self.simulator_ruleset_model.ruleset = self.selected_model_item.ruleset
                self.simulator_ruleset_model.update()

                if self.selected_model_item.ruleset.mode == Mode.all_apply:
                    self.ui.rbAllApply.setChecked(True)
                else:
                    self.ui.rbOneApply.setChecked(True)

                for i in range(len(self.selected_model_item.ruleset)):
                    self.open_ruleset_editors(i)

                self.ui.detail_view_widget.setCurrentIndex(3)
            elif isinstance(self.selected_item, ProgramActionItem):
                self.ui.extProgramLineEdit.setText(self.selected_model_item.ext_prog)
                self.ui.cmdLineArgsLineEdit.setText(self.selected_model_item.args)
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
    def on_view_type_changed(self):
        self.simulator_message_table_model.proto_view = self.ui.cbViewType.currentIndex()
        self.simulator_message_table_model.update()
        self.ui.tblViewMessage.resize_columns()
        
    @pyqtSlot()
    def on_goto_combobox_activated(self):
        self.selected_model_item.goto_target = self.ui.goto_combobox.currentData()

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
        nav_text = self.ui.navLineEdit.text()
        target_item = None

        curr_item = self.sim_proto_manager.rootItem

        if re.match(r"^\d+(\.\d+){0,2}$", nav_text):
            index_list = nav_text.split(".")
            index_list = list(map(int, index_list))

            for index in index_list:
                if not curr_item or index > curr_item.child_count():
                    break

                curr_item = curr_item.children[index - 1]

            if isinstance(curr_item, SimulatorRule):
                curr_item = curr_item.children[0]

            target_item = self.simulator_scene.model_to_scene(curr_item)

        if target_item:
            self.ui.gvSimulator.jump_to_item(target_item)
        else:
            self.update_ui()

    def open_ruleset_editors(self, row):
        self.ui.tblViewSimulatorRuleset.openPersistentEditor(self.simulator_ruleset_model.index(row, 0))
        self.ui.tblViewSimulatorRuleset.openPersistentEditor(self.simulator_ruleset_model.index(row, 1))
        self.ui.tblViewSimulatorRuleset.openPersistentEditor(self.simulator_ruleset_model.index(row, 2))

    @pyqtSlot(bool)
    def on_cb_rulesetmode_toggled(self, checked: bool):
        if self.ui.rbAllApply.isChecked():
            self.selected_model_item.ruleset.mode = Mode(0)
        else:
            self.selected_model_item.ruleset.mode = Mode(1)

    @pyqtSlot()
    def on_btn_add_rule_clicked(self):
        self.ui.btnRemoveRule.setEnabled(True)
        self.selected_model_item.ruleset.append(SimulatorRulesetItem(variable=None, operator="=", target_value="1", value_type=0))
        self.simulator_ruleset_model.update()

        for i in range(len(self.selected_model_item.ruleset)):
            self.open_ruleset_editors(i)

    @pyqtSlot()
    def on_btn_remove_rule_clicked(self):
        self.selected_model_item.ruleset.remove(self.selected_model_item.ruleset[-1])
        self.simulator_ruleset_model.update()
        self.ui.btnRemoveRule.setEnabled(len(self.selected_model_item.ruleset) > 0)

        for i in range(len(self.selected_model_item.ruleset)):
            self.open_ruleset_editors(i)

    @pyqtSlot()
    def on_btn_choose_ext_prog_clicked(self):
        file_name, ok = QFileDialog.getOpenFileName(self, self.tr("Choose external program"), QDir.homePath())

        if file_name and ok:
            self.ui.extProgramLineEdit.setText(file_name)

    @pyqtSlot()
    def on_ext_program_line_edit_text_changed(self):
        self.selected_model_item.ext_prog = self.ui.extProgramLineEdit.text()

    @pyqtSlot()
    def on_cmd_line_args_line_edit_text_changed(self):
        self.selected_model_item.args = self.ui.cmdLineArgsLineEdit.text()

    @pyqtSlot()
    def refresh_tree(self):
        self.tree_model.beginResetModel()
        self.tree_model.endResetModel()
        self.ui.treeProtocols.expandAll()

    def close_all(self):
        self.tree_model.rootItem.clearChilds()
        self.tree_model.rootItem.addGroup()
        self.refresh_tree()