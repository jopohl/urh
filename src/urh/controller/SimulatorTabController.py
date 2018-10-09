import xml.etree.ElementTree as ET

import numpy
from PyQt5.QtCore import pyqtSlot, Qt, QDir, QStringListModel, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QFileDialog, QCompleter, QMessageBox, QFrame, \
    QHBoxLayout, QToolButton, QDialog

from urh.controller.CompareFrameController import CompareFrameController
from urh.controller.GeneratorTabController import GeneratorTabController
from urh.controller.dialogs.ModulatorDialog import ModulatorDialog
from urh.controller.dialogs.ProtocolLabelDialog import ProtocolLabelDialog
from urh.controller.dialogs.SimulatorDialog import SimulatorDialog
from urh.controller.widgets.ChecksumWidget import ChecksumWidget
from urh.models.ParticipantTableModel import ParticipantTableModel
from urh.models.SimulatorMessageFieldModel import SimulatorMessageFieldModel
from urh.models.SimulatorMessageTableModel import SimulatorMessageTableModel
from urh.models.SimulatorParticipantListModel import SimulatorParticipantListModel
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.simulator.SimulatorConfiguration import SimulatorConfiguration
from urh.simulator.SimulatorCounterAction import SimulatorCounterAction
from urh.simulator.SimulatorExpressionParser import SimulatorExpressionParser
from urh.simulator.SimulatorGotoAction import SimulatorGotoAction
from urh.simulator.SimulatorItem import SimulatorItem
from urh.simulator.SimulatorMessage import SimulatorMessage
from urh.simulator.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.simulator.SimulatorRule import SimulatorRuleCondition, ConditionType
from urh.simulator.SimulatorSleepAction import SimulatorSleepAction
from urh.simulator.SimulatorTriggerCommandAction import SimulatorTriggerCommandAction
from urh.ui.RuleExpressionValidator import RuleExpressionValidator
from urh.ui.SimulatorScene import SimulatorScene
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.delegates.ProtocolValueDelegate import ProtocolValueDelegate
from urh.ui.ui_simulator import Ui_SimulatorTab
from urh.util import util, FileOperator
from urh.util.Errors import Errors
from urh.util.Logger import logger
from urh.util.ProjectManager import ProjectManager


class SimulatorTabController(QWidget):
    open_in_analysis_requested = pyqtSignal(str)
    rx_file_saved = pyqtSignal(str)

    def __init__(self, compare_frame_controller: CompareFrameController,
                 generator_tab_controller: GeneratorTabController,
                 project_manager: ProjectManager, parent):
        super().__init__(parent)

        self.project_manager = project_manager
        self.compare_frame_controller = compare_frame_controller
        self.generator_tab_controller = generator_tab_controller
        self.proto_analyzer = compare_frame_controller.proto_analyzer

        self.simulator_config = SimulatorConfiguration(self.project_manager)
        self.sim_expression_parser = SimulatorExpressionParser(self.simulator_config)
        SimulatorItem.simulator_config = self.simulator_config
        SimulatorItem.expression_parser = self.sim_expression_parser

        self.ui = Ui_SimulatorTab()
        self.ui.setupUi(self)
        util.set_splitter_stylesheet(self.ui.splitter)
        util.set_splitter_stylesheet(self.ui.splitterLeftRight)

        self.ui.splitter.setSizes([self.width() / 0.7, self.width() / 0.3])

        self.ui.treeProtocols.setHeaderHidden(True)
        self.tree_model = self.generator_tab_controller.tree_model
        self.ui.treeProtocols.setModel(self.tree_model)

        self.participant_table_model = ParticipantTableModel(project_manager.participants)
        self.ui.tableViewParticipants.setModel(self.participant_table_model)
        self.participant_table_model.update()

        self.simulator_message_field_model = SimulatorMessageFieldModel(self)
        self.ui.tblViewFieldValues.setModel(self.simulator_message_field_model)
        self.ui.tblViewFieldValues.setItemDelegateForColumn(1, ComboBoxDelegate(ProtocolLabel.DISPLAY_FORMATS,
                                                                                parent=self.ui.tblViewFieldValues))
        self.ui.tblViewFieldValues.setItemDelegateForColumn(2, ComboBoxDelegate(SimulatorProtocolLabel.VALUE_TYPES,
                                                                                parent=self.ui.tblViewFieldValues))
        self.ui.tblViewFieldValues.setItemDelegateForColumn(3, ProtocolValueDelegate(controller=self,
                                                                                     parent=self.ui.tblViewFieldValues))
        self.project_manager.reload_field_types()
        self.update_field_name_column()

        self.simulator_message_table_model = SimulatorMessageTableModel(self.project_manager, self)
        self.ui.tblViewMessage.setModel(self.simulator_message_table_model)

        self.ui.ruleCondLineEdit.setValidator(RuleExpressionValidator(self.sim_expression_parser, is_formula=False))
        self.completer_model = QStringListModel([])
        self.ui.ruleCondLineEdit.setCompleter(QCompleter(self.completer_model, self.ui.ruleCondLineEdit))
        self.ui.ruleCondLineEdit.setToolTip(self.sim_expression_parser.rule_condition_help)

        self.simulator_scene = SimulatorScene(mode=0, simulator_config=self.simulator_config)
        self.simulator_scene.tree_root_item = compare_frame_controller.proto_tree_model.rootItem
        self.ui.gvSimulator.setScene(self.simulator_scene)
        self.ui.gvSimulator.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.ui.gvSimulator.proto_analyzer = compare_frame_controller.proto_analyzer

        self.__active_item = None

        self.ui.listViewSimulate.setModel(SimulatorParticipantListModel(self.simulator_config))
        self.ui.spinBoxNRepeat.setValue(self.project_manager.simulator_num_repeat)
        self.ui.spinBoxTimeout.setValue(self.project_manager.simulator_timeout_ms)
        self.ui.spinBoxRetries.setValue(self.project_manager.simulator_retries)
        self.ui.comboBoxError.setCurrentIndex(self.project_manager.simulator_error_handling_index)

        # place save/load button at corner of tab widget
        frame = QFrame(parent=self)
        frame.setLayout(QHBoxLayout())
        frame.setFrameStyle(frame.NoFrame)
        self.ui.btnSave = QToolButton(self.ui.tab)
        self.ui.btnSave.setIcon(QIcon.fromTheme("document-save"))
        frame.layout().addWidget(self.ui.btnSave)

        self.ui.btnLoad = QToolButton(self.ui.tab)
        self.ui.btnLoad.setIcon(QIcon.fromTheme("document-open"))
        frame.layout().addWidget(self.ui.btnLoad)
        frame.layout().setContentsMargins(0, 0, 0, 0)
        self.ui.tabWidget.setCornerWidget(frame)

        self.ui.splitterLeftRight.setSizes([0.2 * self.width(), 0.8 * self.width()])

        self.create_connects()

    def refresh_field_types_for_labels(self):
        for msg in self.simulator_config.get_all_messages():
            for lbl in (lbl for lbl in msg.message_type if lbl.field_type is not None):
                msg.message_type.change_field_type_of_label(lbl, self.field_types_by_caption.get(lbl.field_type.caption,
                                                                                                 None))

        self.update_field_name_column()
        self.update_ui()

    @property
    def field_types(self):
        return self.project_manager.field_types

    @property
    def field_types_by_caption(self):
        return self.project_manager.field_types_by_caption

    def update_field_name_column(self):
        field_types = [ft.caption for ft in self.field_types]
        self.ui.tblViewFieldValues.setItemDelegateForColumn(0, ComboBoxDelegate(field_types, is_editable=True,
                                                                                return_index=False,
                                                                                parent=self.ui.tblViewFieldValues))

    def create_connects(self):
        self.ui.btnChooseCommand.clicked.connect(self.on_btn_choose_command_clicked)
        self.ui.lineEditTriggerCommand.textChanged.connect(self.on_line_edit_trigger_command_text_changed)
        self.ui.checkBoxPassTranscriptSTDIN.clicked.connect(self.on_check_box_pass_transcript_STDIN_clicked)
        self.ui.doubleSpinBoxSleep.editingFinished.connect(self.on_spinbox_sleep_editing_finished)
        self.ui.ruleCondLineEdit.textChanged.connect(self.on_rule_cond_line_edit_text_changed)
        self.ui.btnStartSim.clicked.connect(self.on_btn_simulate_clicked)
        self.ui.goto_combobox.currentIndexChanged.connect(self.on_goto_combobox_index_changed)
        self.ui.spinBoxRepeat.valueChanged.connect(self.on_repeat_value_changed)
        self.ui.cbViewType.currentIndexChanged.connect(self.on_view_type_changed)
        self.ui.tblViewMessage.create_label_triggered.connect(self.create_simulator_label)
        self.ui.tblViewMessage.open_modulator_dialog_clicked.connect(self.open_modulator_dialog)
        self.ui.tblViewMessage.selectionModel().selectionChanged.connect(self.on_table_selection_changed)
        self.ui.tabWidget.currentChanged.connect(self.on_selected_tab_changed)
        self.ui.btnSave.clicked.connect(self.on_btn_save_clicked)
        self.ui.btnLoad.clicked.connect(self.on_btn_load_clicked)

        self.ui.listViewSimulate.model().participant_simulate_changed.connect(self.on_participant_simulate_changed)

        self.ui.btnAddParticipant.clicked.connect(self.ui.tableViewParticipants.on_add_action_triggered)
        self.ui.btnRemoveParticipant.clicked.connect(self.ui.tableViewParticipants.on_remove_action_triggered)
        self.ui.btnUp.clicked.connect(self.ui.tableViewParticipants.on_move_up_action_triggered)
        self.ui.btnDown.clicked.connect(self.ui.tableViewParticipants.on_move_down_action_triggered)
        self.participant_table_model.participant_edited.connect(self.on_participant_edited)

        self.tree_model.modelReset.connect(self.refresh_tree)

        self.simulator_scene.selectionChanged.connect(self.on_simulator_scene_selection_changed)
        self.simulator_scene.files_dropped.connect(self.on_files_dropped)

        self.simulator_message_field_model.protocol_label_updated.connect(self.item_updated)
        self.ui.gvSimulator.message_updated.connect(self.item_updated)
        self.ui.gvSimulator.consolidate_messages_clicked.connect(self.consolidate_messages)

        self.simulator_config.items_added.connect(self.refresh_message_table)
        self.simulator_config.items_updated.connect(self.refresh_message_table)
        self.simulator_config.items_moved.connect(self.refresh_message_table)
        self.simulator_config.items_deleted.connect(self.refresh_message_table)
        self.simulator_config.participants_changed.connect(self.on_participants_changed)
        self.simulator_config.item_dict_updated.connect(self.on_item_dict_updated)
        self.simulator_config.active_participants_updated.connect(self.on_active_participants_updated)

        self.ui.gvSimulator.message_updated.connect(self.on_message_source_or_destination_updated)

        self.ui.spinBoxNRepeat.valueChanged.connect(self.on_spinbox_num_repeat_value_changed)
        self.ui.spinBoxTimeout.valueChanged.connect(self.on_spinbox_timeout_value_changed)
        self.ui.comboBoxError.currentIndexChanged.connect(self.on_combobox_error_handling_index_changed)
        self.ui.spinBoxRetries.valueChanged.connect(self.on_spinbox_retries_value_changed)

        self.ui.tblViewFieldValues.item_link_clicked.connect(self.on_table_item_link_clicked)
        self.ui.tblViewMessage.edit_label_triggered.connect(self.on_edit_label_triggered)

        self.ui.spinBoxCounterStart.editingFinished.connect(self.on_spinbox_counter_start_editing_finished)
        self.ui.spinBoxCounterStep.editingFinished.connect(self.on_spinbox_counter_step_editing_finished)

    def consolidate_messages(self):
        self.simulator_config.consolidate_messages()

    def on_repeat_value_changed(self, value):
        self.active_item.repeat = value
        self.simulator_config.items_updated.emit([self.active_item])

    def on_item_dict_updated(self):
        self.completer_model.setStringList(self.sim_expression_parser.get_identifiers())

    def on_selected_tab_changed(self, index: int):
        if index == 0:
            if self.active_item is not None:
                self.ui.gvSimulator.jump_to_item(self.active_item)
            else:
                self.update_ui()
        else:
            self.ui.tblViewMessage.resize_columns()
            self.update_vertical_table_header()

    def refresh_message_table(self):
        self.simulator_message_table_model.protocol.messages[:] = self.simulator_config.get_all_messages()
        self.simulator_message_table_model.update()

        if isinstance(self.active_item, SimulatorMessage):
            self.simulator_message_field_model.update()

        self.ui.tblViewMessage.resize_columns()
        self.update_ui()

    def load_config_from_xml_tag(self, xml_tag, update_before=True):
        if xml_tag is None:
            return

        if update_before:
            self.simulator_config.on_project_updated()

        self.simulator_config.load_from_xml(xml_tag, self.proto_analyzer.message_types)
        self.project_manager.project_updated.emit()

    def load_simulator_file(self, filename: str):
        try:
            tree = ET.parse(filename)
            self.load_config_from_xml_tag(tree.getroot(), update_before=False)
        except Exception as e:
            logger.exception(e)

    def save_simulator_file(self, filename: str):
        tag = self.simulator_config.save_to_xml(standalone=True)
        util.write_xml_to_file(tag, filename)

    def close_all(self):
        self.simulator_scene.clear_all()

    @pyqtSlot(int, int, int)
    def create_simulator_label(self, msg_index: int, start: int, end: int):
        con = self.simulator_message_table_model.protocol
        start, end = con.convert_range(start, end - 1, self.ui.cbViewType.currentIndex(), 0, False, msg_index)
        lbl = self.simulator_config.add_label(start=start, end=end, parent_item=con.messages[msg_index])

        try:
            index = self.simulator_message_field_model.message_type.index(lbl)
            self.ui.tblViewFieldValues.edit(self.simulator_message_field_model.createIndex(index, 0))
        except ValueError:
            pass

    @pyqtSlot()
    def open_modulator_dialog(self):
        selected_message = self.simulator_message_table_model.protocol.messages[self.ui.tblViewMessage.selected_rows[0]]
        preselected_index = selected_message.modulator_index

        modulator_dialog = ModulatorDialog(self.project_manager.modulators, tree_model=self.tree_model, parent=self)
        modulator_dialog.ui.comboBoxCustomModulations.setCurrentIndex(preselected_index)
        modulator_dialog.showMaximized()
        modulator_dialog.initialize(selected_message.encoded_bits_str[0:10])

        modulator_dialog.finished.connect(self.refresh_modulators)
        modulator_dialog.finished.connect(self.generator_tab_controller.refresh_pause_list)

    @pyqtSlot()
    def refresh_modulators(self):
        # update Generator tab ...
        cBoxModulations = self.generator_tab_controller.ui.cBoxModulations
        current_index = cBoxModulations.currentIndex()
        cBoxModulations.clear()

        for modulator in self.project_manager.modulators:
            cBoxModulations.addItem(modulator.name)

        cBoxModulations.setCurrentIndex(current_index)

        # update Simulator tab ...
        index = self.sender().ui.comboBoxCustomModulations.currentIndex()

        for row in self.ui.tblViewMessage.selected_rows:
            self.simulator_message_table_model.protocol.messages[row].modulator_index = index

    def update_goto_combobox(self, active_item: SimulatorGotoAction):
        assert isinstance(active_item, SimulatorGotoAction)
        goto_combobox = self.ui.goto_combobox

        goto_combobox.blockSignals(True)
        goto_combobox.clear()
        goto_combobox.addItem("Select item ...")
        goto_combobox.addItems(active_item.get_valid_goto_targets())
        goto_combobox.setCurrentIndex(-1)
        goto_combobox.blockSignals(False)

        index = goto_combobox.findText(self.active_item.goto_target)

        if index == -1:
            index = 0

        goto_combobox.setCurrentIndex(index)

    def update_ui(self):
        if self.active_item is not None:
            text = self.tr("Detail view for item #") + self.active_item.index()

            if isinstance(self.active_item, SimulatorMessage):
                text += " (" + self.active_item.message_type.name + ")"
                self.ui.spinBoxRepeat.setValue(self.active_item.repeat)
                self.ui.lblEncodingDecoding.setText(self.active_item.decoder.name)

            self.ui.lblMsgFieldsValues.setText(text)
        else:
            self.ui.lblMsgFieldsValues.setText(self.tr("Detail view for item"))

    def update_vertical_table_header(self):
        self.simulator_message_table_model.refresh_vertical_header()
        self.ui.tblViewMessage.resize_vertical_header()

    @pyqtSlot()
    def on_rule_cond_line_edit_text_changed(self):
        self.active_item.condition = self.ui.ruleCondLineEdit.text()
        self.item_updated(self.active_item)

    @pyqtSlot()
    def on_view_type_changed(self):
        self.simulator_message_table_model.proto_view = self.ui.cbViewType.currentIndex()
        self.simulator_message_table_model.update()
        self.ui.tblViewMessage.resize_columns()

    @pyqtSlot()
    def on_goto_combobox_index_changed(self):
        if not isinstance(self.active_item, SimulatorGotoAction):
            return

        self.active_item.goto_target = None if self.ui.goto_combobox.currentIndex() == 0 else self.ui.goto_combobox.currentText()
        self.item_updated(self.active_item)

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
            self.ui.lNumSelectedColumns.setText("0")
        else:
            max_row = numpy.max([rng.bottom() for rng in selection])
            self.active_item = self.simulator_message_table_model.protocol.messages[max_row]
            _, _, start, end = self.ui.tblViewMessage.selection_range()
            self.ui.lNumSelectedColumns.setText(str(end - start))

        self.update_ui()

    @property
    def active_item(self):
        return self.__active_item

    @active_item.setter
    def active_item(self, value):
        self.__active_item = value

        if isinstance(self.active_item, SimulatorGotoAction):
            self.update_goto_combobox(self.active_item)

            self.ui.detail_view_widget.setCurrentIndex(1)
        elif isinstance(self.active_item, SimulatorMessage):
            self.simulator_message_field_model.update()
            self.ui.spinBoxRepeat.setValue(self.active_item.repeat)
            self.ui.lblEncodingDecoding.setText(self.active_item.decoder.name)

            self.ui.detail_view_widget.setCurrentIndex(2)
        elif (isinstance(self.active_item, SimulatorRuleCondition) and
              self.active_item.type != ConditionType.ELSE):
            self.ui.ruleCondLineEdit.setText(self.active_item.condition)
            self.ui.detail_view_widget.setCurrentIndex(3)
        elif isinstance(self.active_item, SimulatorTriggerCommandAction):
            self.ui.lineEditTriggerCommand.setText(self.active_item.command)
            self.ui.checkBoxPassTranscriptSTDIN.setChecked(self.active_item.pass_transcript)
            self.ui.detail_view_widget.setCurrentIndex(4)
        elif isinstance(self.active_item, SimulatorSleepAction):
            self.ui.doubleSpinBoxSleep.setValue(self.active_item.sleep_time)
            self.ui.detail_view_widget.setCurrentIndex(5)
        elif isinstance(self.active_item, SimulatorCounterAction):
            self.ui.spinBoxCounterStart.setValue(self.active_item.start)
            self.ui.spinBoxCounterStep.setValue(self.active_item.step)
            self.ui.detail_view_widget.setCurrentIndex(6)
        else:
            self.ui.detail_view_widget.setCurrentIndex(0)

        self.update_ui()

    @pyqtSlot()
    def on_btn_simulate_clicked(self):
        if not self.simulator_config.protocol_valid():
            QMessageBox.critical(self, self.tr("Invalid protocol configuration"),
                                 self.tr(
                                     "There are some problems with your protocol configuration. Please fix them first."))
            return

        if not len(self.simulator_config.get_all_messages()):
            QMessageBox.critical(self, self.tr("No messages found"), self.tr("Please add at least one message."))
            return

        num_simulated = len([p for p in self.project_manager.participants if p.simulate])
        if num_simulated == 0:
            if self.ui.listViewSimulate.model().rowCount() == 0:
                QMessageBox.critical(self, self.tr("No active participants"),
                                     self.tr("You have no active participants.<br>"
                                             "Please add a participant in the <i>Participants tab</i> and "
                                             "assign it to at least one message as <i>source</i> or <i>destination.</i>"))
                return
            else:
                QMessageBox.critical(self, self.tr("No participant for simulation selected"),
                                     self.tr("Please check at least one participant from the "
                                             "<i>Simulate these participants</i> list."))
                return

        try:
            self.get_simulator_dialog().exec_()
        except Exception as e:
            Errors.generic_error("An error occurred", str(e))

    def get_simulator_dialog(self) -> SimulatorDialog:
        protos = [p for proto_list in self.tree_model.protocols.values() for p in proto_list]
        signals = [p.signal for p in protos if p.signal is not None]

        s = SimulatorDialog(self.simulator_config, self.project_manager.modulators,
                            self.sim_expression_parser, self.project_manager, signals=signals,
                            signal_tree_model=self.tree_model, parent=self)

        s.rx_parameters_changed.connect(self.project_manager.on_simulator_rx_parameters_changed)
        s.sniff_parameters_changed.connect(self.project_manager.on_simulator_sniff_parameters_changed)
        s.tx_parameters_changed.connect(self.project_manager.on_simulator_tx_parameters_changed)
        s.open_in_analysis_requested.connect(self.open_in_analysis_requested.emit)
        s.rx_file_saved.connect(self.rx_file_saved.emit)

        return s

    @pyqtSlot()
    def on_btn_choose_command_clicked(self):
        file_name, ok = QFileDialog.getOpenFileName(self, self.tr("Choose program"), QDir.homePath())

        if file_name is not None and ok:
            self.ui.lineEditTriggerCommand.setText(file_name)

    @pyqtSlot()
    def on_line_edit_trigger_command_text_changed(self):
        self.active_item.command = self.ui.lineEditTriggerCommand.text()
        self.item_updated(self.active_item)

    @pyqtSlot()
    def on_check_box_pass_transcript_STDIN_clicked(self):
        self.active_item.pass_transcript = self.ui.checkBoxPassTranscriptSTDIN.isChecked()
        self.item_updated(self.active_item)

    @pyqtSlot()
    def on_spinbox_counter_start_editing_finished(self):
        self.active_item.start = self.ui.spinBoxCounterStart.value()
        self.item_updated(self.active_item)

    @pyqtSlot()
    def on_spinbox_counter_step_editing_finished(self):
        self.active_item.step = self.ui.spinBoxCounterStep.value()
        self.item_updated(self.active_item)

    @pyqtSlot()
    def on_spinbox_sleep_editing_finished(self):
        self.active_item.sleep_time = self.ui.doubleSpinBoxSleep.value()
        self.item_updated(self.active_item)

    @pyqtSlot()
    def on_participants_changed(self):
        self.update_vertical_table_header()
        self.participant_table_model.update()
        self.ui.listViewSimulate.model().update()

    def item_updated(self, item: SimulatorItem):
        self.simulator_config.items_updated.emit([item])

    @pyqtSlot()
    def refresh_tree(self):
        self.ui.treeProtocols.expandAll()

    @pyqtSlot()
    def on_btn_save_clicked(self):
        filename = FileOperator.get_save_file_name(initial_name="myprofile.sim.xml", caption="Save simulator profile")
        if filename:
            self.save_simulator_file(filename)

    @pyqtSlot()
    def on_btn_load_clicked(self):
        dialog = FileOperator.get_open_dialog(False, parent=self, name_filter="simulator")
        if dialog.exec_():
            self.load_simulator_file(dialog.selectedFiles()[0])

    @pyqtSlot()
    def on_participant_edited(self):
        self.project_manager.project_updated.emit()

    @pyqtSlot(int)
    def on_spinbox_num_repeat_value_changed(self, value):
        self.project_manager.simulator_num_repeat = value

    @pyqtSlot(int)
    def on_spinbox_timeout_value_changed(self, value):
        self.project_manager.simulator_timeout_ms = value

    @pyqtSlot(int)
    def on_spinbox_retries_value_changed(self, value):
        self.project_manager.simulator_retries = value

    @pyqtSlot(int)
    def on_combobox_error_handling_index_changed(self, index: int):
        self.project_manager.simulator_error_handling_index = index

    @pyqtSlot()
    def on_message_source_or_destination_updated(self):
        self.simulator_config.update_active_participants()

    @pyqtSlot(int, int)
    def on_table_item_link_clicked(self, row: int, column: int):
        try:
            lbl = self.simulator_message_field_model.message_type[row]  # type: SimulatorProtocolLabel
            assert lbl.is_checksum_label
            assert isinstance(self.active_item, SimulatorMessage)
        except (IndexError, AssertionError):
            return

        d = QDialog(parent=self)
        layout = QHBoxLayout()
        layout.addWidget(ChecksumWidget(lbl.label, self.active_item, self.ui.cbViewType.currentIndex()))
        d.setLayout(layout)
        d.show()

    @pyqtSlot(Participant)
    def on_participant_simulate_changed(self, participant: Participant):
        self.simulator_scene.refresh_participant(participant)

    @pyqtSlot()
    def on_active_participants_updated(self):
        self.ui.listViewSimulate.model().update()

    @pyqtSlot(int)
    def on_edit_label_triggered(self, label_index: int):
        view_type = self.ui.cbViewType.currentIndex()
        protocol_label_dialog = ProtocolLabelDialog(message=self.ui.tblViewMessage.selected_message,
                                                    viewtype=view_type, selected_index=label_index, parent=self)
        protocol_label_dialog.finished.connect(self.on_protocol_label_dialog_finished)
        protocol_label_dialog.showMaximized()

    @pyqtSlot()
    def on_protocol_label_dialog_finished(self):
        self.simulator_message_field_model.update()
        self.simulator_message_table_model.update()
        self.update_ui()

    @pyqtSlot(list)
    def on_files_dropped(self, file_urls: list):
        for filename in (file_url.toLocalFile() for file_url in file_urls if file_url.isLocalFile()):
            self.load_simulator_file(filename)