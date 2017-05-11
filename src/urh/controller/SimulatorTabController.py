import re
import numpy
import itertools

from PyQt5.QtWidgets import QWidget, QFileDialog, QInputDialog
from PyQt5.QtCore import pyqtSlot, Qt, QDir

from urh.models.SimulatorRulesetTableModel import SimulatorRulesetTableModel
from urh.models.GeneratorTreeModel import GeneratorTreeModel
from urh.models.SimulatorMessageFieldModel import SimulatorMessageFieldModel
from urh.models.SimulatorMessageTableModel import SimulatorMessageTableModel
from urh.util.ProjectManager import ProjectManager
from urh.ui.ui_simulator import Ui_SimulatorTab
from urh.ui.SimulatorScene import SimulatorScene
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.Ruleset import OPERATION_DESCRIPTION
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.SimulatorRuleset import SimulatorRulesetItem, Mode
from urh.signalprocessing.SimulatorRule import SimulatorRule, SimulatorRuleCondition, ConditionType
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.signalprocessing.SimulatorItem import SimulatorItem
from urh.signalprocessing.SimulatorMessage import SimulatorMessage
from urh.signalprocessing.SimulatorGotoAction import SimulatorGotoAction
from urh.signalprocessing.SimulatorProgramAction import SimulatorProgramAction
from urh.signalprocessing.SimulatorFormulaParser import SimulatorFormulaParser

from urh.SimulatorProtocolManager import SimulatorProtocolManager

from urh.controller.CompareFrameController import CompareFrameController
from urh.controller.SimulateDialogController import SimulateDialogController

from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.delegates.ProtocolValueDelegate import ProtocolValueDelegate

class SimulatorTabController(QWidget):
    def __init__(self, compare_frame_controller: CompareFrameController,
                 project_manager: ProjectManager, parent):
        super().__init__(parent)

        self.project_manager = project_manager
        self.compare_frame_controller = compare_frame_controller
        self.proto_analyzer = compare_frame_controller.proto_analyzer

        self.sim_proto_manager = SimulatorProtocolManager(self.project_manager)
        self.sim_formula_parser = SimulatorFormulaParser(self.sim_proto_manager)

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
        self.ui.tblViewFieldValues.setItemDelegateForColumn(1, ComboBoxDelegate(SimulatorProtocolLabel.DISPLAY_FORMATS, parent=self))
        self.ui.tblViewFieldValues.setItemDelegateForColumn(2, ComboBoxDelegate(SimulatorProtocolLabel.VALUE_TYPES, parent=self))
        self.ui.tblViewFieldValues.setItemDelegateForColumn(3, ProtocolValueDelegate(controller=self, parent=self))
        self.reload_field_types()
        self.update_field_name_column()

        self.simulator_message_table_model = SimulatorMessageTableModel(self)
        self.ui.tblViewMessage.setModel(self.simulator_message_table_model)

        self.simulator_scene = SimulatorScene(mode=0, sim_proto_manager=self.sim_proto_manager)
        self.simulator_scene.tree_root_item = compare_frame_controller.proto_tree_model.rootItem
        self.ui.gvSimulator.setScene(self.simulator_scene)
        self.ui.gvSimulator.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.ui.gvSimulator.proto_analyzer = compare_frame_controller.proto_analyzer

        operator_descriptions = list(OPERATION_DESCRIPTION.values())
        operator_descriptions.sort()
        self.simulator_ruleset_model = SimulatorRulesetTableModel(operator_descriptions, controller=self, parent=self)
        self.ui.tblViewSimulatorRuleset.setModel(self.simulator_ruleset_model)
        self.ui.tblViewSimulatorRuleset.setItemDelegateForColumn(1, ComboBoxDelegate(SimulatorRulesetItem.VIEW_TYPES, parent=self))
        self.ui.tblViewSimulatorRuleset.setItemDelegateForColumn(2, ComboBoxDelegate(operator_descriptions, parent=self))

        self.active_item = None

        self.create_connects(compare_frame_controller)

    def refresh_field_types_for_labels(self):
        self.reload_field_types()

        for msg in self.sim_proto_manager.get_all_messages():
            for lbl in (lbl for lbl in msg.message_type if lbl.type is not None):
                if lbl.type.id not in self.field_types_by_id:
                    lbl.type = None
                else:
                    lbl.type = self.field_types_by_id[lbl.type.id]

        self.update_field_name_column()
        self.update_ui()

    def reload_field_types(self):
        self.field_types = FieldType.load_from_xml()
        self.field_types_by_id = {field_type.id: field_type for field_type in self.field_types}
        self.field_types_by_caption = {field_type.caption: field_type for field_type in self.field_types}

    def update_field_name_column(self):
        field_types = [ft.caption for ft in self.field_types]
        self.ui.tblViewFieldValues.setItemDelegateForColumn(0, ComboBoxDelegate(field_types, is_editable=True, return_index=False, parent=self))

    def update_label_name_column(self):
        self.ui.tblViewSimulatorRuleset.setItemDelegateForColumn(0,
                ComboBoxDelegate(self.sim_formula_parser.label_list, is_editable=True, return_index=False, parent=self))

    def create_connects(self, compare_frame_controller):
        self.ui.btnAddRule.clicked.connect(self.on_btn_add_rule_clicked)
        self.ui.btnRemoveRule.clicked.connect(self.on_btn_remove_rule_clicked)
        self.ui.btnChooseExtProg.clicked.connect(self.on_btn_choose_ext_prog_clicked)
        self.ui.extProgramLineEdit.textChanged.connect(self.on_ext_program_line_edit_text_changed)
        self.ui.cmdLineArgsLineEdit.textChanged.connect(self.on_cmd_line_args_line_edit_text_changed)
        self.ui.rbAllApply.toggled.connect(self.on_cb_rulesetmode_toggled)
        self.ui.rbOneApply.toggled.connect(self.on_cb_rulesetmode_toggled)
        self.ui.btnStartSim.clicked.connect(self.on_show_simulate_dialog_action_triggered)
        self.ui.btnNextNav.clicked.connect(self.ui.gvSimulator.navigate_forward)
        self.ui.btnPrevNav.clicked.connect(self.ui.gvSimulator.navigate_backward)
        self.ui.navLineEdit.returnPressed.connect(self.on_nav_line_edit_return_pressed)
        self.ui.goto_combobox.activated.connect(self.on_goto_combobox_activated)
        self.ui.cbViewType.currentIndexChanged.connect(self.on_view_type_changed)
        self.ui.tblViewMessage.create_fuzzing_label_clicked.connect(self.create_fuzzing_label)
        self.ui.tblViewMessage.selectionModel().selectionChanged.connect(self.on_table_selection_changed)
        self.ui.tabWidget.currentChanged.connect(self.on_selected_tab_changed)

        compare_frame_controller.proto_tree_model.modelReset.connect(self.refresh_tree)

        self.simulator_scene.selectionChanged.connect(self.on_simulator_scene_selection_changed)

        self.simulator_message_field_model.protocol_label_updated.connect(self.sim_proto_manager.item_updated.emit)
        self.ui.gvSimulator.message_updated.connect(self.sim_proto_manager.item_updated.emit)
        self.ui.gvSimulator.new_messagetype_clicked.connect(self.add_message_type)

        self.sim_proto_manager.items_added.connect(self.refresh_message_table)
        self.sim_proto_manager.item_updated.connect(self.refresh_message_table)
        self.sim_proto_manager.items_moved.connect(self.refresh_message_table)
        self.sim_proto_manager.items_deleted.connect(self.refresh_message_table)
        self.sim_proto_manager.participants_changed.connect(self.update_vertical_table_header)

    def add_message_type(self, message: SimulatorMessage):
        names = set(message_type.name for message_type in self.proto_analyzer.message_types)
        name = "Message type #"
        i = next(i for i in itertools.count(start=1) if name+str(i) not in names)

        msg_type_name, ok = QInputDialog.getText(self, self.tr("Enter message type name"),
                                                 self.tr("Name:"), text=name + str(i))

        if ok:
            msg_type = MessageType(name=msg_type_name)

            for lbl in message.message_type:
                msg_type.add_protocol_label(start=lbl.start, end=lbl.end - 1, name=lbl.name,
                                            color_ind=lbl.color_index, type=lbl.type)

            self.proto_analyzer.message_types.append(msg_type)
            self.compare_frame_controller.fill_message_type_combobox()
            self.compare_frame_controller.active_message_type = self.compare_frame_controller.active_message_type
            
    def on_selected_tab_changed(self, index: int):
        if index == 0:
            if self.active_item is not None:
                scene_item = self.simulator_scene.model_to_scene(self.active_item)
                self.ui.gvSimulator.jump_to_item(scene_item)
            else:
                self.update_ui()
        else:
            self.ui.tblViewMessage.resize_columns()
            self.update_vertical_table_header()

    def refresh_message_table(self):
        self.simulator_message_table_model.protocol.messages[:] = self.sim_proto_manager.get_all_messages()
        self.simulator_message_table_model.update()
        self.ui.tblViewMessage.resize_columns()
        self.update_ui()

    @pyqtSlot(int, int, int)
    def create_fuzzing_label(self, msg_index: int, start: int, end: int):
        con = self.simulator_message_table_model.protocol
        start, end = con.convert_range(start, end - 1, self.ui.cbViewType.currentIndex(), 0, False, msg_index)
        lbl = self.sim_proto_manager.add_label(start=start, end=end, parent_item=con.messages[msg_index])
        index = self.simulator_message_field_model.message_type.index(lbl)
        self.ui.tblViewFieldValues.edit(self.simulator_message_field_model.createIndex(index, 0))

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

        if self.active_item.goto_target is not None:
            goto_combobox.setCurrentText(self.active_item.goto_target.index())
        else:
            goto_combobox.setCurrentIndex(0)

    def update_ui(self):
        if self.active_item is not None:
            if isinstance(self.active_item, SimulatorGotoAction):
                self.update_goto_combobox()

                self.ui.detail_view_widget.setCurrentIndex(1)
            elif isinstance(self.active_item, SimulatorMessage):
                self.simulator_message_field_model.message_type = self.active_item.message_type
                self.simulator_message_field_model.update()

                self.ui.detail_view_widget.setCurrentIndex(2)
            elif (isinstance(self.active_item, SimulatorRuleCondition) and
                    self.active_item.type != ConditionType.ELSE):
                self.ui.btnRemoveRule.setEnabled(len(self.active_item.ruleset) > 0)
                self.simulator_ruleset_model.ruleset = self.active_item.ruleset
                self.simulator_ruleset_model.update()

                if self.active_item.ruleset.mode == Mode.all_apply:
                    self.ui.rbAllApply.setChecked(True)
                else:
                    self.ui.rbOneApply.setChecked(True)

                self.update_label_name_column()

                self.ui.detail_view_widget.setCurrentIndex(3)
            elif isinstance(self.active_item, SimulatorProgramAction):
                self.ui.extProgramLineEdit.setText(self.active_item.ext_prog)
                self.ui.cmdLineArgsLineEdit.setText(self.active_item.args)

                self.ui.detail_view_widget.setCurrentIndex(4)
            else:
                self.ui.detail_view_widget.setCurrentIndex(0)

            scene_item = self.simulator_scene.model_to_scene(self.active_item)
            self.ui.navLineEdit.setText(self.active_item.index())
            self.ui.btnNextNav.setEnabled(not scene_item.next() is None)
            self.ui.btnPrevNav.setEnabled(not scene_item.prev() is None)

            self.ui.lblMsgFieldsValues.setText(self.tr("Detail view for item #") + self.active_item.index())
        else:
            self.ui.detail_view_widget.setCurrentIndex(0)

            self.ui.navLineEdit.clear()
            self.ui.btnNextNav.setEnabled(False)
            self.ui.btnPrevNav.setEnabled(False)

            self.ui.lblMsgFieldsValues.setText(self.tr("Detail view for item"))

    def update_vertical_table_header(self):
        self.simulator_message_table_model.refresh_vertical_header()
        self.ui.tblViewMessage.resize_vertical_header()

    @pyqtSlot()
    def on_view_type_changed(self):
        self.simulator_message_table_model.proto_view = self.ui.cbViewType.currentIndex()
        self.simulator_message_table_model.update()
        self.ui.tblViewMessage.resize_columns()
        
    @pyqtSlot()
    def on_goto_combobox_activated(self):
        self.active_item.goto_target = self.ui.goto_combobox.currentData()

    @pyqtSlot()
    def on_simulator_scene_selection_changed(self):
        selected_items = self.simulator_scene.selectedItems()
        self.active_item = selected_items[0].model_item if selected_items else None

        self.update_ui()

    @pyqtSlot()
    def on_table_selection_changed(self):
        selection = self.ui.tblViewMessage.selectionModel().selection()

        if selection.isEmpty():
            self.active_item = None
        else:
            min_row = numpy.min([rng.top() for rng in selection])
            self.active_item = self.simulator_message_table_model.protocol.messages[min_row]

        self.update_ui()

    @pyqtSlot()
    def on_show_simulate_dialog_action_triggered(self):
        s = SimulateDialogController(project_manager=self.project_manager, sim_proto_manager=self.sim_proto_manager, parent=self)
        s.show()

    @pyqtSlot()
    def on_nav_line_edit_return_pressed(self):
        nav_text = self.ui.navLineEdit.text()
        target_item = None

        curr_item = self.sim_proto_manager.rootItem

        if re.match(r"^\d+(\.\d+)*$", nav_text):
            index_list = nav_text.split(".")
            index_list = list(map(int, index_list))

            for index in index_list:
                if (curr_item is None or index > curr_item.child_count()
                        or isinstance(curr_item, SimulatorMessage)):
                    break

                curr_item = curr_item.children[index - 1]

            if isinstance(curr_item, SimulatorRule):
                curr_item = curr_item.children[0]

            target_item = self.simulator_scene.model_to_scene(curr_item)

        if target_item is not None:
            self.ui.gvSimulator.jump_to_item(target_item)
        else:
            self.update_ui()

    @pyqtSlot(bool)
    def on_cb_rulesetmode_toggled(self, checked: bool):
        self.active_item.ruleset.mode = Mode(0) if self.ui.rbAllApply.isChecked() else Mode(1)

    @pyqtSlot()
    def on_btn_add_rule_clicked(self):
        self.ui.btnRemoveRule.setEnabled(True)
        rule = SimulatorRulesetItem(variable="", operator="=", target_value="1", value_type=0)
        self.active_item.ruleset.append(rule)
        self.simulator_ruleset_model.update()

        index = self.active_item.ruleset.index(rule)
        self.ui.tblViewSimulatorRuleset.edit(self.simulator_ruleset_model.createIndex(index, 0))

    @pyqtSlot()
    def on_btn_remove_rule_clicked(self):
        self.active_item.ruleset.remove(self.active_item.ruleset[-1])
        self.simulator_ruleset_model.update()
        self.ui.btnRemoveRule.setEnabled(len(self.active_item.ruleset) > 0)

    @pyqtSlot()
    def on_btn_choose_ext_prog_clicked(self):
        file_name, ok = QFileDialog.getOpenFileName(self, self.tr("Choose external program"), QDir.homePath())

        if file_name is not None and ok:
            self.ui.extProgramLineEdit.setText(file_name)

    @pyqtSlot()
    def on_ext_program_line_edit_text_changed(self):
        self.active_item.ext_prog = self.ui.extProgramLineEdit.text()

    @pyqtSlot()
    def on_cmd_line_args_line_edit_text_changed(self):
        self.active_item.args = self.ui.cmdLineArgsLineEdit.text()

    @pyqtSlot()
    def refresh_tree(self):
        self.tree_model.beginResetModel()
        self.tree_model.endResetModel()
        self.ui.treeProtocols.expandAll()

    def close_all(self):
        self.tree_model.rootItem.clearChilds()
        self.tree_model.rootItem.addGroup()
        self.refresh_tree()