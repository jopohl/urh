import locale
import os
from datetime import datetime

import numpy
from PyQt5.QtCore import pyqtSlot, QTimer, Qt, pyqtSignal, QItemSelection, QItemSelectionModel, QLocale
from PyQt5.QtGui import QContextMenuEvent, QIcon
from PyQt5.QtWidgets import QMessageBox, QAbstractItemView, QUndoStack, QMenu, QWidget

from urh import constants
from urh.controller.dialogs.MessageTypeDialog import MessageTypeDialog
from urh.controller.dialogs.ProtocolLabelDialog import ProtocolLabelDialog
from urh.models.LabelValueTableModel import LabelValueTableModel
from urh.models.ParticipantListModel import ParticipantListModel
from urh.models.ProtocolLabelListModel import ProtocolLabelListModel
from urh.models.ProtocolTableModel import ProtocolTableModel
from urh.models.ProtocolTreeModel import ProtocolTreeModel
from urh.plugins.PluginManager import PluginManager
from urh.signalprocessing.Encoding import Encoding
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolGroup import ProtocolGroup
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.ui_analysis import Ui_TabAnalysis
from urh.util import FileOperator, util
from urh.util.Formatter import Formatter
from urh.util.Logger import logger
from urh.util.ProjectManager import ProjectManager


class CompareFrameController(QWidget):
    show_interpretation_clicked = pyqtSignal(int, int, int, int)
    show_decoding_clicked = pyqtSignal()
    files_dropped = pyqtSignal(list)
    participant_changed = pyqtSignal()
    show_config_field_types_triggered = pyqtSignal()
    load_protocol_clicked = pyqtSignal()

    def __init__(self, plugin_manager: PluginManager, project_manager: ProjectManager, parent):

        super().__init__(parent)

        self.proto_analyzer = ProtocolAnalyzer(None)
        self.project_manager = project_manager

        self.ui = Ui_TabAnalysis()
        self.ui.setupUi(self)
        util.set_splitter_stylesheet(self.ui.splitter)
        util.set_splitter_stylesheet(self.ui.splitter_2)

        self.ui.lBitsSelection.setText("")
        self.ui.lDecimalSelection.setText("")
        self.ui.lHexSelection.setText("")
        self.plugin_manager = plugin_manager
        self.decimal_point = QLocale().decimalPoint()

        self.__selected_message_type = self.proto_analyzer.default_message_type
        self.fill_message_type_combobox()

        self.participant_list_model = ParticipantListModel(project_manager.participants)
        self.ui.listViewParticipants.setModel(self.participant_list_model)

        self.__active_group_ids = [0]
        self.selected_protocols = set()

        self.search_select_filter_align_menu = QMenu()
        self.search_action = self.search_select_filter_align_menu.addAction(self.tr("Search"))
        self.select_action = self.search_select_filter_align_menu.addAction(self.tr("Select all"))
        self.filter_action = self.search_select_filter_align_menu.addAction(self.tr("Filter"))
        self.align_action = self.search_select_filter_align_menu.addAction(self.tr("Align"))
        self.ui.btnSearchSelectFilter.setMenu(self.search_select_filter_align_menu)

        self.analyze_menu = QMenu()
        self.assign_participants_action = self.analyze_menu.addAction(self.tr("Assign participants"))
        self.assign_participants_action.setCheckable(True)
        self.assign_participants_action.setChecked(True)
        self.assign_message_type_action = self.analyze_menu.addAction(self.tr("Assign message type"))
        self.assign_message_type_action.setCheckable(True)
        self.assign_message_type_action.setChecked(True)
        self.assign_labels_action = self.analyze_menu.addAction(self.tr("Assign labels"))
        self.assign_labels_action.setCheckable(True)
        self.assign_labels_action.setChecked(False)
        self.assign_participant_address_action = self.analyze_menu.addAction(self.tr("Assign participant addresses"))
        self.assign_participant_address_action.setCheckable(True)
        self.assign_participant_address_action.setChecked(True)
        self.ui.btnAnalyze.setMenu(self.analyze_menu)

        self.ui.lblShownRows.hide()
        self.ui.lblClearAlignment.hide()

        self.protocol_model = ProtocolTableModel(self.proto_analyzer, project_manager.participants,
                                                 self)  # type: ProtocolTableModel
        self.protocol_label_list_model = ProtocolLabelListModel(self.proto_analyzer,
                                                                controller=self)  # type: ProtocolLabelListModel

        self.label_value_model = LabelValueTableModel(self.proto_analyzer,
                                                      controller=self)  # type: LabelValueTableModel
        self.ui.tblViewProtocol.setModel(self.protocol_model)
        self.ui.tblViewProtocol.controller = self
        self.ui.tblLabelValues.setModel(self.label_value_model)
        self.ui.listViewLabelNames.setModel(self.protocol_label_list_model)

        self.selection_timer = QTimer(self)
        self.selection_timer.setSingleShot(True)

        self.setAcceptDrops(False)

        self.proto_tree_model = ProtocolTreeModel(controller=self)  # type: ProtocolTreeModel
        self.ui.treeViewProtocols.setModel(self.proto_tree_model)

        self.create_connects()
        self.fill_decoding_combobox()

        self.rows_for_protocols = {}
        self.__protocols = None

        self.min_height = self.minimumHeight()
        self.max_height = self.maximumHeight()

        self.old_reference_index = 0

        self.__set_decoding_error_label(None)

        self.__set_default_message_type_ui_status()

    # region properties

    @property
    def field_types(self):
        return self.project_manager.field_types

    @property
    def field_types_by_caption(self):
        return self.project_manager.field_types_by_caption

    @property
    def active_group_ids(self):
        """
        Returns a list of currently selected group indices

        :rtype: list of int
        """
        return self.__active_group_ids

    @active_group_ids.setter
    def active_group_ids(self, val: list):
        self.__active_group_ids = val

    @property
    def groups(self):
        """

        :rtype: list of ProtocolGroup
        """
        return self.proto_tree_model.groups

    @property
    def active_groups(self):
        """
        Returns a list of currently selected protocol groups

        :rtype: list of ProtocolGroup
        """
        return [self.proto_tree_model.group_at(i) for i in self.active_group_ids]

    @property
    def active_message_type(self) -> MessageType:
        return self.__selected_message_type

    @active_message_type.setter
    def active_message_type(self, val: MessageType):
        if val not in self.proto_analyzer.message_types:
            logger.error("Message type {} not in mesage types".format(val.name))
            return

        self.__selected_message_type = val

        self.ui.cbMessagetypes.blockSignals(True)
        self.ui.cbMessagetypes.setCurrentIndex(self.proto_analyzer.message_types.index(val))
        self.__set_default_message_type_ui_status()
        self.protocol_label_list_model.update()
        self.ui.cbMessagetypes.blockSignals(False)

        self.update_field_type_combobox()

    @property
    def selected_messages(self):
        return self.ui.tblViewProtocol.selected_messages

    @property
    def protocol_undo_stack(self) -> QUndoStack:
        return self.protocol_model.undo_stack

    @property
    def protocols(self):
        """
        :rtype: dict[int, list of ProtocolAnalyzer]
        """
        if self.__protocols is None:
            self.__protocols = self.proto_tree_model.protocols
        return self.__protocols

    @property
    def protocol_list(self):
        """
        :return: visible protocols
        :rtype: list of ProtocolAnalyzer
        """
        result = []
        for group in self.groups:
            result.extend(group.protocols)
        return result

    @property
    def full_protocol_list(self):
        """
        :return: all protocols including not shown ones
        :rtype: list of ProtocolAnalyzer
        """
        result = []
        for group in self.groups:
            result.extend(group.all_protocols)
        return result

    # endregion

    def __set_decoding_error_label(self, message: Message):
        if message:
            errors = message.decoding_errors
            percent = 100 * (errors / len(message))
            state = message.decoding_state if message.decoding_state != message.decoder.ErrorState.SUCCESS else ""
            color = "green" if errors == 0 and state == "" else "red"

            self.ui.lDecodingErrorsValue.setStyleSheet("color: " + color)
            self.ui.lDecodingErrorsValue.setText(locale.format_string("%d (%.02f%%) %s", (errors, percent, state)))
        else:
            self.ui.lDecodingErrorsValue.setText("No message selected")

    def create_connects(self):
        self.protocol_undo_stack.indexChanged.connect(self.on_undo_stack_index_changed)
        self.ui.cbProtoView.currentIndexChanged.connect(self.on_protocol_view_changed)
        self.ui.cbDecoding.currentIndexChanged.connect(self.on_combobox_decoding_current_index_changed)
        self.ui.cbShowDiffs.clicked.connect(self.on_chkbox_show_differences_clicked)
        self.ui.chkBoxOnlyShowLabelsInProtocol.stateChanged.connect(self.on_check_box_show_only_labels_state_changed)
        self.ui.chkBoxShowOnlyDiffs.stateChanged.connect(self.on_check_box_show_only_diffs_state_changed)

        self.protocol_model.vertical_header_color_status_changed.connect(
            self.ui.tblViewProtocol.on_vertical_header_color_status_changed)

        self.ui.tblViewProtocol.show_interpretation_clicked.connect(self.show_interpretation_clicked.emit)
        self.ui.tblViewProtocol.protocol_view_change_clicked.connect(self.ui.cbProtoView.setCurrentIndex)
        self.ui.tblViewProtocol.selection_changed.connect(self.on_table_selection_changed)
        self.ui.tblViewProtocol.writeable_changed.connect(self.on_writeable_changed)
        self.ui.tblViewProtocol.row_visibility_changed.connect(self.on_tbl_view_protocol_row_visibility_changed)
        self.ui.tblViewProtocol.edit_label_clicked.connect(self.on_edit_label_clicked_in_table)
        self.ui.tblViewProtocol.participant_changed.connect(self.on_participant_edited)
        self.ui.tblViewProtocol.messagetype_selected.connect(self.on_message_type_selected)
        self.ui.tblViewProtocol.new_messagetype_clicked.connect(self.on_table_new_message_type_clicked)
        self.ui.tblViewProtocol.files_dropped.connect(self.on_files_dropped)

        self.ui.tblLabelValues.edit_label_action_triggered.connect(self.on_edit_label_action_triggered)

        self.ui.btnSearchSelectFilter.clicked.connect(self.on_btn_search_clicked)
        self.ui.btnNextSearch.clicked.connect(self.on_btn_next_search_clicked)
        self.ui.btnPrevSearch.clicked.connect(self.on_btn_prev_search_clicked)
        self.ui.lineEditSearch.returnPressed.connect(self.ui.btnSearchSelectFilter.click)
        self.search_action.triggered.connect(self.on_search_action_triggered)
        self.select_action.triggered.connect(self.on_select_action_triggered)
        self.filter_action.triggered.connect(self.on_filter_action_triggered)
        self.align_action.triggered.connect(self.on_align_action_triggered)
        self.ui.lblShownRows.linkActivated.connect(self.on_label_shown_link_activated)
        self.ui.lblClearAlignment.linkActivated.connect(self.on_label_clear_alignment_link_activated)

        self.protocol_label_list_model.protolabel_visibility_changed.connect(self.on_protolabel_visibility_changed)
        self.protocol_label_list_model.protocol_label_name_edited.connect(self.label_value_model.update)
        self.protocol_label_list_model.label_removed.connect(self.on_label_removed)

        self.ui.btnSaveProto.clicked.connect(self.on_btn_save_protocol_clicked)
        self.ui.btnLoadProto.clicked.connect(self.on_btn_load_proto_clicked)

        self.ui.btnAnalyze.clicked.connect(self.on_btn_analyze_clicked)

        self.ui.listViewLabelNames.editActionTriggered.connect(self.on_edit_label_action_triggered)
        self.ui.listViewLabelNames.configureActionTriggered.connect(self.show_config_field_types_triggered.emit)
        self.ui.listViewLabelNames.auto_message_type_update_triggered.connect(
            self.update_automatic_assigned_message_types)
        self.ui.listViewLabelNames.selection_changed.connect(self.on_label_selection_changed)

        self.protocol_model.ref_index_changed.connect(self.on_ref_index_changed)

        self.project_manager.project_updated.connect(self.on_project_updated)
        self.participant_list_model.show_state_changed.connect(self.on_participant_show_state_changed)

        self.ui.btnAddMessagetype.clicked.connect(self.on_btn_new_message_type_clicked)
        self.ui.btnRemoveMessagetype.clicked.connect(self.on_btn_remove_message_type_clicked)

        self.ui.cbMessagetypes.currentIndexChanged.connect(self.on_combobox_messagetype_index_changed)
        self.ui.cbMessagetypes.editTextChanged.connect(self.on_message_type_name_edited)

        self.ui.btnMessagetypeSettings.clicked.connect(self.on_btn_message_type_settings_clicked)
        self.selection_timer.timeout.connect(self.on_table_selection_timer_timeout)
        self.ui.treeViewProtocols.selection_changed.connect(self.on_tree_view_selection_changed)
        self.proto_tree_model.item_dropped.connect(self.on_item_in_proto_tree_dropped)

        self.proto_tree_model.group_deleted.connect(self.on_group_deleted)
        self.proto_tree_model.proto_to_group_added.connect(self.on_proto_to_group_added)

    def get_message_type_for_label(self, lbl: ProtocolLabel) -> MessageType:
        return next((msg_type for msg_type in self.proto_analyzer.message_types if lbl in msg_type), None)

    def update_field_type_combobox(self):
        field_types = [ft.caption for ft in self.field_types]
        self.ui.listViewLabelNames.setItemDelegate(ComboBoxDelegate(field_types, is_editable=True, return_index=False))

    def set_decoding(self, decoding: Encoding, messages=None):
        """

        :param decoding:
        :param messages: None = set for all messages
        :return:
        """
        if decoding is None:
            self.show_decoding_clicked.emit()
        else:
            if messages is None:
                messages = self.proto_analyzer.messages
                if len(messages) > 10:
                    reply = QMessageBox.question(self, "Set decoding",
                                                 "Do you want to apply the selected decoding to {} messages?".format(
                                                     len(messages)), QMessageBox.Yes | QMessageBox.No)
                    if reply != QMessageBox.Yes:
                        self.ui.cbDecoding.blockSignals(True)
                        self.ui.cbDecoding.setCurrentText("...")
                        self.ui.cbDecoding.blockSignals(False)
                        return

            self.show_all_cols()

            for msg in messages:
                msg.decoder = decoding

            self.ui.tblViewProtocol.zero_hide_offsets.clear()
            self.clear_search()

            selected = self.ui.tblViewProtocol.selectionModel().selection()

            if not selected.isEmpty() and self.isVisible() and self.proto_analyzer.num_messages > 0:
                min_row = min(rng.top() for rng in selected)
                min_row = min_row if min_row < len(self.proto_analyzer.messages) else -1
                try:
                    msg = self.proto_analyzer.messages[min_row]
                except IndexError:
                    msg = None
                self.__set_decoding_error_label(msg)
            else:
                self.__set_decoding_error_label(None)

            self.protocol_model.update()
            self.protocol_label_list_model.update()
            self.label_value_model.update()

            for lbl in self.proto_analyzer.protocol_labels:
                self.set_protocol_label_visibility(lbl)

            self.ui.tblViewProtocol.resize_columns()

    @property
    def decodings(self):
        return self.project_manager.decodings

    def refresh_existing_encodings(self):
        """
        Refresh existing encodings for messages, when encoding was changed by user in dialog

        :return:
        """
        update = False

        for msg in self.proto_analyzer.messages:
            i = next((i for i, d in enumerate(self.decodings) if d.name == msg.decoder.name), 0)
            if msg.decoder != self.decodings[i]:
                update = True
                msg.decoder = self.decodings[i]
                msg.clear_decoded_bits()
                msg.clear_encoded_bits()

        if update:
            self.protocol_model.update()
            self.label_value_model.update()

    def fill_decoding_combobox(self):
        cur_item = self.ui.cbDecoding.currentText() if self.ui.cbDecoding.count() > 0 else None
        self.ui.cbDecoding.blockSignals(True)
        self.ui.cbDecoding.clear()
        prev_index = 0
        for i, decoding in enumerate(self.decodings):
            self.ui.cbDecoding.addItem(decoding.name)
            if decoding.name == cur_item:
                prev_index = i

        self.ui.cbDecoding.addItem("...")
        self.ui.cbDecoding.setCurrentIndex(prev_index)
        self.ui.cbDecoding.blockSignals(False)

    def fill_message_type_combobox(self):
        self.ui.cbMessagetypes.blockSignals(True)
        self.ui.cbMessagetypes.clear()
        for message_type in self.proto_analyzer.message_types:
            self.ui.cbMessagetypes.addItem(message_type.name)
        self.ui.cbMessagetypes.blockSignals(False)
        if self.ui.cbMessagetypes.count() <= 1:
            self.ui.cbMessagetypes.setEditable(False)

    def add_protocol(self, protocol: ProtocolAnalyzer, group_id: int = 0) -> ProtocolAnalyzer:
        self.__protocols = None
        self.proto_tree_model.add_protocol(protocol, group_id)
        protocol.qt_signals.protocol_updated.connect(self.on_protocol_updated)
        if protocol.signal:
            protocol.signal.sample_rate_changed.connect(self.set_shown_protocols)  # Refresh times
        protocol.qt_signals.show_state_changed.connect(self.set_shown_protocols)
        protocol.qt_signals.show_state_changed.connect(self.filter_search_results)
        for i in range(self.proto_tree_model.ngroups):
            self.expand_group_node(i)
        return protocol

    def add_protocol_from_file(self, filename: str) -> ProtocolAnalyzer:
        pa = ProtocolAnalyzer(signal=None, filename=filename)
        pa.message_types = []

        if filename.endswith(".bin"):
            pa.from_binary(filename)
        else:
            pa.from_xml_file(filename=filename, read_bits=True)
            for messsage_type in pa.message_types:
                if messsage_type not in self.proto_analyzer.message_types:
                    if messsage_type.name in (mt.name for mt in self.proto_analyzer.message_types):
                        messsage_type.name += " (" + os.path.split(filename)[1].rstrip(".xml").rstrip(".proto") + ")"
                    self.proto_analyzer.message_types.append(messsage_type)

        self.fill_message_type_combobox()
        self.add_protocol(protocol=pa)

        self.set_shown_protocols()
        return pa

    def add_sniffed_protocol_messages(self, messages: list):
        if len(messages) > 0:
            proto_analyzer = ProtocolAnalyzer(None)
            proto_analyzer.name = datetime.fromtimestamp(messages[0].timestamp).strftime("%Y-%m-%d %H:%M:%S")
            proto_analyzer.messages = messages
            self.add_protocol(proto_analyzer, group_id=self.proto_tree_model.ngroups - 1)
            self.refresh()

    def add_protocol_label(self, start: int, end: int, messagenr: int, proto_view: int, edit_label_name=True):
        # Ensure atleast one Group is active
        start, end = self.proto_analyzer.convert_range(start, end, proto_view, 0, decoded=True, message_indx=messagenr)
        message_type = self.proto_analyzer.messages[messagenr].message_type
        try:
            used_field_types = [lbl.field_type for lbl in message_type]
            first_unused_type = next(ft for ft in self.field_types if ft not in used_field_types)
            name = first_unused_type.caption
        except (StopIteration, AttributeError):
            first_unused_type, name = None, None

        proto_label = message_type.add_protocol_label(start=start, end=end, name=name, type=first_unused_type)

        self.protocol_label_list_model.update()
        self.protocol_model.update()

        if edit_label_name:
            try:
                index = self.protocol_label_list_model.message_type.index(proto_label)
                self.ui.listViewLabelNames.edit(self.protocol_label_list_model.createIndex(index, 0))
            except ValueError:
                pass

        self.label_value_model.update()

        return True

    def add_message_type(self, selected_messages: list = None):
        selected_messages = selected_messages if isinstance(selected_messages, list) else []
        self.proto_analyzer.add_new_message_type(labels=self.proto_analyzer.default_message_type)
        self.fill_message_type_combobox()
        self.ui.cbMessagetypes.setEditable(True)
        self.active_message_type = self.proto_analyzer.message_types[-1]
        for msg in selected_messages:
            msg.message_type = self.active_message_type
        self.ui.cbMessagetypes.setFocus()
        self.ui.btnRemoveMessagetype.show()
        self.protocol_model.update()

    def remove_protocol(self, protocol: ProtocolAnalyzer):
        self.__protocols = None
        self.proto_tree_model.remove_protocol(protocol)
        try:
            del self.rows_for_protocols[protocol]
        except KeyError:
            pass
        self.ui.tblViewProtocol.clearSelection()
        self.set_shown_protocols()

    def set_shown_protocols(self):
        hidden_rows = {i for i in range(self.protocol_model.row_count) if self.ui.tblViewProtocol.isRowHidden(i)}
        relative_hidden_row_positions = {}
        for proto in self.rows_for_protocols.keys():
            if any(i in hidden_rows for i in self.rows_for_protocols[proto]):
                m = min(self.rows_for_protocols[proto])
                relative_hidden_row_positions[proto] = [i - m for i in hidden_rows if
                                                        i in self.rows_for_protocols[proto]]

        # self.protocol_undo_stack.clear()
        self.proto_analyzer.messages[:] = []
        self.rows_for_protocols.clear()
        align_labels = constants.SETTINGS.value("align_labels", True, bool)
        line = 0
        first_msg_indices = []
        prev_line = 0
        for proto in self.protocol_list:
            abs_time = 0
            rel_time = 0
            if proto.show and proto.messages:
                num_messages = 0
                for i, message in enumerate(proto.messages):
                    if not message:
                        continue

                    message.align_labels = align_labels
                    try:
                        if hasattr(proto.signal, "sample_rate"):
                            if i > 0:
                                rel_time = proto.messages[i - 1].get_duration(proto.signal.sample_rate)
                                abs_time += rel_time
                        else:
                            # No signal, loaded from protocol file
                            abs_time = datetime.fromtimestamp(message.timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")
                            if i > 0:
                                rel_time = message.timestamp - proto.messages[i - 1].timestamp
                    except IndexError:
                        pass

                    message.absolute_time = abs_time
                    message.relative_time = rel_time

                    num_messages += 1
                    if message.message_type not in self.proto_analyzer.message_types:
                        message.message_type = self.proto_analyzer.default_message_type
                    self.proto_analyzer.messages.append(message)

                line += num_messages
                rows_for_cur_proto = list(range(prev_line, line))
                self.rows_for_protocols[proto] = rows_for_cur_proto[:]

                prev_line = line
                if line != 0:
                    first_msg_indices.append(line)

        # apply hidden rows to new order
        for i in range(self.protocol_model.row_count):
            self.ui.tblViewProtocol.showRow(i)

        self.protocol_model.hidden_rows.clear()
        for proto in relative_hidden_row_positions.keys():
            try:
                start = min(self.rows_for_protocols[proto])
                for rel_pos in relative_hidden_row_positions[proto]:
                    self.ui.tblViewProtocol.hideRow(start + rel_pos)
                    self.protocol_model.hidden_rows.add(start + rel_pos)
            except (KeyError, ValueError):
                pass

        # consider hidden rows
        for i in range(self.protocol_model.row_count):
            if self.ui.tblViewProtocol.isRowHidden(i) and i in first_msg_indices:
                indx = first_msg_indices.index(i)
                first_msg_indices[indx] += 1
                try:
                    if first_msg_indices[indx] >= first_msg_indices[indx + 1]:
                        del first_msg_indices[indx]
                except IndexError:
                    pass

        for line in first_msg_indices:
            self.ui.tblViewProtocol.setRowHeight(line, constants.SEPARATION_ROW_HEIGHT)

        self.protocol_model.first_messages = first_msg_indices[:]

        self.updateUI()
        self.show_differences(self.ui.cbShowDiffs.isChecked())

    def restore_selection(self, old_view: int, sel_cols, sel_rows):
        if len(sel_cols) == 0 or len(sel_rows) == 0:
            return

        start_col, end_col = numpy.min(sel_cols), numpy.max(sel_cols)
        start_row, end_row = numpy.min(sel_rows), numpy.max(sel_rows)
        new_view = self.ui.cbProtoView.currentIndex()

        message = self.proto_analyzer.messages[end_row]
        start_col = message.convert_index(start_col, old_view, new_view, True)[0]
        end_col = message.convert_index(end_col, old_view, new_view, True)[1]

        start_index = self.protocol_model.index(start_row, start_col)
        end_index = self.protocol_model.index(end_row, end_col)
        mid_index = self.protocol_model.index(int((start_row + end_row) / 2), int((start_col + end_col) / 2))

        sel = QItemSelection()
        sel.select(start_index, end_index)

        self.ui.tblViewProtocol.selectionModel().select(sel, QItemSelectionModel.ClearAndSelect)
        self.ui.tblViewProtocol.scrollTo(mid_index)

    def expand_group_node(self, group_id):
        index = self.proto_tree_model.createIndex(group_id, 0, self.proto_tree_model.rootItem.child(group_id))
        self.ui.treeViewProtocols.expand(index)

    def updateUI(self, ignore_table_model=False, resize_table=True):
        if not ignore_table_model:
            self.protocol_model.update()

        self.protocol_label_list_model.update()
        self.proto_tree_model.layoutChanged.emit()  # do not call update, as it prevents editing
        self.label_value_model.update()
        self.protocol_label_list_model.update()

        if resize_table:
            self.ui.tblViewProtocol.resize_columns()

    def refresh(self):
        self.__protocols = None
        self.set_shown_protocols()

    def reset(self):
        for message_type in self.proto_analyzer.message_types:
            message_type.clear()
        self.proto_tree_model.rootItem.clearChilds()
        self.proto_tree_model.rootItem.addGroup()
        self.refresh()

    def create_protocol_label_dialog(self, preselected_index: int):
        view_type = self.ui.cbProtoView.currentIndex()
        try:
            longest_message = max(
                (msg for msg in self.proto_analyzer.messages if msg.message_type == self.active_message_type), key=len)
        except ValueError:
            logger.warning("Configuring message type with empty message set.")
            longest_message = Message([True] * 1000, 1000, self.active_message_type)
        protocol_label_dialog = ProtocolLabelDialog(preselected_index=preselected_index,
                                                    message=longest_message, viewtype=view_type, parent=self)
        protocol_label_dialog.apply_decoding_changed.connect(self.on_apply_decoding_changed)
        protocol_label_dialog.finished.connect(self.on_protocol_label_dialog_finished)

        return protocol_label_dialog

    def show_protocol_label_dialog(self, preselected_index: int):
        dialog = self.create_protocol_label_dialog(preselected_index)
        dialog.exec_()

    def search(self):
        value = self.ui.lineEditSearch.text()
        nresults = self.protocol_model.find_protocol_value(value)

        if nresults > 0:
            self.ui.btnNextSearch.setEnabled(True)
            self.ui.btnPrevSearch.setEnabled(False)
            self.ui.lSearchTotal.setText(str(nresults))
            self.ui.lSearchCurrent.setText("0")
            self.next_search_result()
        else:
            self.clear_search()

    def select_all_search_results(self):
        self.search()
        self.ui.tblViewProtocol.clearSelection()

        for search_result in self.protocol_model.search_results:
            startindex = self.protocol_model.index(search_result[0], search_result[1])
            endindex = self.protocol_model.index(search_result[0],
                                                 search_result[1] + len(self.protocol_model.search_value) - 1)

            sel = QItemSelection()
            sel.select(startindex, endindex)

            self.ui.tblViewProtocol.selectionModel().select(sel, QItemSelectionModel.Select)
            self.ui.tblViewProtocol.scrollTo(startindex, QAbstractItemView.PositionAtCenter)

        self.ui.tblViewProtocol.setFocus()

    def filter_search_results(self):
        if "Filter" not in self.ui.btnSearchSelectFilter.text():
            # Checking for equality is not enough as some desktop environments (I am watching at you KDE!)
            # insert a & at beginning of the string
            return

        self.setCursor(Qt.WaitCursor)
        if self.ui.lineEditSearch.text():
            self.search()
            self.ui.tblLabelValues.clearSelection()

            matching_rows = set(search_result[0] for search_result in self.protocol_model.search_results)
            rows_to_hide = set(range(0, self.protocol_model.row_count)) - matching_rows
            self.ui.tblViewProtocol.hide_row(rows_to_hide)
        else:
            self.show_all_rows()
            self.set_shown_protocols()

        self.unsetCursor()

    def __set_shown_rows_status_label(self):
        if len(self.protocol_model.hidden_rows) > 0:
            rc = self.protocol_model.row_count
            text = self.tr("shown: {}/{} (<a href='reset_filter'>reset</a>)")
            self.ui.lblShownRows.setText(text.format(rc - len(self.protocol_model.hidden_rows), rc))
            self.ui.lblShownRows.show()
        else:
            self.ui.lblShownRows.hide()

    def align_messages(self, pattern=None):
        pattern = self.ui.lineEditSearch.text() if pattern is None else pattern
        self.proto_analyzer.align_messages(pattern, view_type=self.ui.cbProtoView.currentIndex())
        self.ui.lblClearAlignment.setVisible(any(msg.alignment_offset != 0 for msg in self.proto_analyzer.messages))
        self.protocol_model.update()

        row = column = 0
        for i, message in enumerate(self.proto_analyzer.messages):
            if self.ui.tblViewProtocol.isRowHidden(i):
                continue

            data = message.view_to_string(self.ui.cbProtoView.currentIndex(), decoded=True)
            try:
                row = i
                column = data.index(pattern) + len(pattern) + self.protocol_model.get_alignment_offset_at(i) - 1
                break
            except ValueError:
                pass

        self.ui.tblViewProtocol.scrollTo(self.protocol_model.index(row, column))

        self.show_all_cols()
        for lbl in filter(lambda l: not l.show, self.proto_analyzer.protocol_labels):
            self.set_protocol_label_visibility(lbl)

    def next_search_result(self):
        index = int(self.ui.lSearchCurrent.text())
        self.ui.lSearchTotal.setText((str(len(self.protocol_model.search_results))))
        try:
            search_result = self.protocol_model.search_results[index]
            startindex = self.protocol_model.index(search_result[0], search_result[1])
            endindex = self.protocol_model.index(search_result[0],
                                                 search_result[1] + len(self.protocol_model.search_value) - 1)

            sel = QItemSelection()
            sel.select(startindex, endindex)

            self.ui.tblViewProtocol.selectionModel().select(sel, QItemSelectionModel.ClearAndSelect)
            self.ui.tblViewProtocol.scrollTo(startindex, QAbstractItemView.PositionAtCenter)

            self.ui.lSearchCurrent.setText(str(index + 1))
        except IndexError:
            self.ui.lSearchCurrent.setText("-")
        finally:
            if index + 1 == len(self.protocol_model.search_results):
                self.ui.btnNextSearch.setEnabled(False)

            if index > 0 and len(self.protocol_model.search_results) > 0:
                self.ui.btnPrevSearch.setEnabled(True)

    def prev_search_result(self):
        index = int(self.ui.lSearchCurrent.text()) - 2

        try:
            search_result = self.protocol_model.search_results[index]
            startindex = self.protocol_model.index(search_result[0], search_result[1])
            endindex = self.protocol_model.index(search_result[0],
                                                 search_result[1] + len(self.protocol_model.search_value) - 1)

            sel = QItemSelection()
            sel.select(startindex, endindex)

            self.ui.tblViewProtocol.selectionModel().select(sel, QItemSelectionModel.ClearAndSelect)
            self.ui.tblViewProtocol.scrollTo(startindex, QAbstractItemView.PositionAtCenter)

            self.ui.lSearchCurrent.setText(str(index + 1))
        except IndexError:
            self.ui.lSearchCurrent.setText("-")
        finally:
            if self.ui.lSearchCurrent.text() == "1":
                self.ui.btnPrevSearch.setEnabled(False)

            if len(self.protocol_model.search_results) > 0:
                self.ui.btnNextSearch.setEnabled(True)

    def clear_search(self):
        self.ui.btnPrevSearch.setEnabled(False)
        self.ui.btnNextSearch.setEnabled(False)
        self.ui.lSearchTotal.setText("-")
        self.ui.lSearchCurrent.setText("-")
        self.protocol_model.search_results[:] = []
        self.protocol_model.search_value = ""

    def set_protocol_label_visibility(self, lbl: ProtocolLabel, message: Message = None):
        try:
            message = message if message else next(m for m in self.proto_analyzer.messages if lbl in m.message_type)
            start, end = message.get_label_range(lbl, self.ui.cbProtoView.currentIndex(), True, consider_alignment=True)

            for i in range(start, end):
                self.ui.tblViewProtocol.setColumnHidden(i, not lbl.show)
        except Exception as e:
            pass

    def show_all_rows(self):
        self.ui.lblShownRows.hide()
        for i in range(0, self.protocol_model.row_count):
            self.ui.tblViewProtocol.showRow(i)
        self.set_shown_protocols()

    def show_all_cols(self):
        for i in range(self.protocol_model.col_count):
            self.ui.tblViewProtocol.showColumn(i)

    def save_protocol(self):
        for msg in self.proto_analyzer.messages:
            if not msg.decoder.is_nrz:
                reply = QMessageBox.question(self, "Saving of protocol",
                                             "You want to save this protocol with an encoding different from NRZ.\n"
                                             "This may cause loss of information if you load it again.\n\n"
                                             "Save anyway?", QMessageBox.Yes | QMessageBox.No)
                if reply != QMessageBox.Yes:
                    return
                else:
                    break

        text = "protocol"
        filename = FileOperator.get_save_file_name("{0}.proto.xml".format(text), caption="Save protocol")

        if not filename:
            return

        if filename.endswith(".bin"):
            self.proto_analyzer.to_binary(filename, use_decoded=True)
        else:
            self.proto_analyzer.to_xml_file(filename=filename, decoders=self.decodings,
                                            participants=self.project_manager.participants, write_bits=True)

    def show_differences(self, show_differences: bool):
        if show_differences:
            if self.protocol_model.refindex == -1:
                self.protocol_model.refindex = self.old_reference_index
        else:
            if self.protocol_model.refindex != -1:
                self.old_reference_index = self.protocol_model.refindex

            self.ui.chkBoxShowOnlyDiffs.setChecked(False)
            self.protocol_model.refindex = -1

    def set_show_only_status(self):
        """
        Handles the different combinations of the show only checkboxes, namely:
         - Show only labels
         - Show only Diffs
        """
        if self.ui.chkBoxShowOnlyDiffs.isChecked() and not self.ui.cbShowDiffs.isChecked():
            self.ui.cbShowDiffs.setChecked(True)
            self.show_differences(True)

        if self.ui.chkBoxOnlyShowLabelsInProtocol.isChecked() and self.ui.chkBoxShowOnlyDiffs.isChecked():
            self.show_only_diffs_and_labels()
        elif self.ui.chkBoxOnlyShowLabelsInProtocol.isChecked() and not self.ui.chkBoxShowOnlyDiffs.isChecked():
            self.show_only_labels()
        elif not self.ui.chkBoxOnlyShowLabelsInProtocol.isChecked() and self.ui.chkBoxShowOnlyDiffs.isChecked():
            self.show_only_diffs()
        else:
            self.restore_visibility()

        self.ui.tblViewProtocol.resize_columns()

    def show_only_labels(self):
        visible_columns = set()
        for msg in self.proto_analyzer.messages:
            for lbl in filter(lambda lbl: lbl.show, msg.message_type):
                start, end = msg.get_label_range(lbl=lbl, view=self.ui.cbProtoView.currentIndex(), decode=True)
                visible_columns |= set(range(start, end))

        for i in range(self.protocol_model.col_count):
            self.ui.tblViewProtocol.setColumnHidden(i, i not in visible_columns)

    def show_only_diffs(self):
        visible_rows = [i for i in range(self.protocol_model.row_count) if not self.ui.tblViewProtocol.isRowHidden(i)
                        and i != self.protocol_model.refindex]

        visible_diff_columns = [diff_col for i in visible_rows for diff_col in self.protocol_model.diff_columns[i]]

        for j in range(self.protocol_model.col_count):
            if j in visible_diff_columns:
                self.ui.tblViewProtocol.showColumn(j)
            else:
                self.ui.tblViewProtocol.hideColumn(j)

    def show_only_diffs_and_labels(self):
        visible_label_columns = set()
        for lbl in self.proto_analyzer.protocol_labels:
            if lbl.show:
                start, end = self.proto_analyzer.messages[0].get_label_range(lbl, self.ui.cbProtoView.currentIndex(),
                                                                             True)
                visible_label_columns |= (set(range(start, end)))

        visible_rows = [i for i in range(self.protocol_model.row_count) if not self.ui.tblViewProtocol.isRowHidden(i)
                        and i != self.protocol_model.refindex]

        visible_diff_columns = set([diff_col for i in visible_rows for diff_col in self.protocol_model.diff_columns[i]])

        visible_cols = visible_label_columns & visible_diff_columns
        for j in range(self.protocol_model.col_count):
            if j in visible_cols:
                self.ui.tblViewProtocol.showColumn(j)
            else:
                self.ui.tblViewProtocol.hideColumn(j)

    def restore_visibility(self):
        selected = self.ui.tblViewProtocol.selectionModel().selection()  # type: QItemSelection

        for i in range(self.protocol_model.col_count):
            self.ui.tblViewProtocol.showColumn(i)

        for lbl in filter(lambda lbl: not lbl.show, self.proto_analyzer.protocol_labels):
            self.set_protocol_label_visibility(lbl)

        if not selected.isEmpty():
            min_row = numpy.min([rng.top() for rng in selected])
            start = numpy.min([rng.left() for rng in selected])
            self.ui.tblViewProtocol.scrollTo(self.protocol_model.index(min_row, start))

    def get_labels_from_selection(self, row_start: int, row_end: int, col_start: int, col_end: int):
        """

        :rtype: list of ProtocolLabel
        """
        row_end += 1
        col_end += 1

        view = self.ui.cbProtoView.currentIndex()
        result = []
        for i in range(row_start, row_end):
            message = self.proto_analyzer.messages[i]
            for label in message.message_type:
                lbl_start, lbl_end = message.get_label_range(lbl=label, view=view, decode=True)
                if any(j in range(lbl_start, lbl_end) for j in range(col_start, col_end)) and not label in result:
                    result.append(label)

        return result

    def set_search_ui_visibility(self, visible: bool):
        self.ui.btnPrevSearch.setVisible(visible)
        self.ui.lSearchCurrent.setVisible(visible)
        self.ui.lSlash.setVisible(visible)
        self.ui.lSearchTotal.setVisible(visible)
        self.ui.btnNextSearch.setVisible(visible)

    def __set_default_message_type_ui_status(self):
        if self.active_message_type == self.proto_analyzer.default_message_type:
            self.ui.cbMessagetypes.setEditable(False)
            self.ui.btnRemoveMessagetype.hide()
            self.ui.btnMessagetypeSettings.hide()
        else:
            self.ui.cbMessagetypes.setEditable(True)
            self.ui.btnRemoveMessagetype.show()
            self.ui.btnMessagetypeSettings.show()

    def update_automatic_assigned_message_types(self):
        self.proto_analyzer.update_auto_message_types()
        self.protocol_model.update()

    def refresh_assigned_participants_ui(self):
        self.protocol_model.refresh_vertical_header()
        self.ui.tblViewProtocol.resize_vertical_header()
        self.participant_changed.emit()

    def refresh_field_types_for_labels(self):
        for mt in self.proto_analyzer.message_types:
            for lbl in (lbl for lbl in mt if lbl.field_type is not None):  # type: ProtocolLabel
                mt.change_field_type_of_label(lbl, self.field_types_by_caption.get(lbl.field_type.caption, None))

        self.update_field_type_combobox()

    def mousePressEvent(self, event):
        return

    def contextMenuEvent(self, event: QContextMenuEvent):
        pass

    @pyqtSlot(int)
    def on_protocol_label_dialog_finished(self, dialog_result: int):
        self.protocol_label_list_model.update()
        self.update_field_type_combobox()
        self.label_value_model.update()
        self.show_all_cols()
        for lbl in self.proto_analyzer.protocol_labels:
            self.set_protocol_label_visibility(lbl)
        self.set_show_only_status()
        self.protocol_model.update()
        self.ui.tblViewProtocol.resize_columns()

    @pyqtSlot()
    def on_btn_analyze_clicked(self):
        self.setCursor(Qt.WaitCursor)
        self.ui.stackedWidgetLogicAnalysis.setCurrentIndex(1)

        self.ui.progressBarLogicAnalyzer.setFormat("%p% (Detecting participants)")
        self.ui.progressBarLogicAnalyzer.setValue(0)

        if self.assign_participants_action.isChecked():
            for protocol in self.protocol_list:
                protocol.auto_assign_participants(self.protocol_model.participants)
            self.refresh_assigned_participants_ui()

        self.ui.progressBarLogicAnalyzer.setFormat("%p% (Assign message type by rules)")
        self.ui.progressBarLogicAnalyzer.setValue(50)

        if self.assign_message_type_action.isChecked():
            self.update_automatic_assigned_message_types()

        self.ui.progressBarLogicAnalyzer.setFormat("%p% (Find new labels/message types)")
        self.ui.progressBarLogicAnalyzer.setValue(75)

        if self.assign_labels_action.isChecked():
            self.proto_analyzer.auto_assign_labels()
            self.protocol_model.update()
            self.label_value_model.update()
            self.protocol_label_list_model.update()
            self.ui.listViewLabelNames.clearSelection()

        self.ui.progressBarLogicAnalyzer.setValue(90)

        if self.assign_participant_address_action.isChecked():
            self.proto_analyzer.auto_assign_participant_addresses(self.protocol_model.participants)

        self.ui.progressBarLogicAnalyzer.setValue(100)
        self.unsetCursor()
        self.ui.stackedWidgetLogicAnalysis.setCurrentIndex(0)

        self.fill_message_type_combobox()  # in case message types were added by logic analyzer

    @pyqtSlot()
    def on_btn_save_protocol_clicked(self):
        self.save_protocol()

    @pyqtSlot()
    def on_btn_load_proto_clicked(self):
        self.load_protocol_clicked.emit()

    @pyqtSlot()
    def on_btn_next_search_clicked(self):
        self.next_search_result()

    @pyqtSlot()
    def on_btn_prev_search_clicked(self):
        self.prev_search_result()

    @pyqtSlot()
    def on_btn_search_clicked(self):
        self.search()

    @pyqtSlot()
    def on_btn_remove_message_type_clicked(self):
        for msg in self.proto_analyzer.messages:
            if msg.message_type == self.active_message_type:
                msg.message_type = self.proto_analyzer.default_message_type
        self.proto_analyzer.message_types.remove(self.active_message_type)
        self.fill_message_type_combobox()
        self.protocol_model.update()
        self.active_message_type = self.proto_analyzer.default_message_type

    @pyqtSlot()
    def on_btn_message_type_settings_clicked(self):
        dialog = MessageTypeDialog(self.active_message_type, parent=self)
        dialog.show()
        dialog.finished.connect(self.on_message_type_dialog_finished)

    @pyqtSlot()
    def on_btn_new_message_type_clicked(self):
        self.add_message_type()

    @pyqtSlot(list)
    def on_table_new_message_type_clicked(self, selected_messages: list):
        self.add_message_type(selected_messages)

    @pyqtSlot()
    def on_table_selection_changed(self):
        self.selection_timer.start(0)

    @pyqtSlot()
    def on_combobox_decoding_current_index_changed(self):
        new_index = self.ui.cbDecoding.currentIndex()
        if new_index == -1:
            return

        if new_index == self.ui.cbDecoding.count() - 1:
            self.set_decoding(None)
        else:
            self.set_decoding(self.decodings[new_index],
                              messages=self.selected_messages if self.selected_messages else None)

    @pyqtSlot()
    def on_participant_show_state_changed(self):
        for i, msg in enumerate(self.proto_analyzer.messages):
            hide = not msg.participant.show if msg.participant is not None else not self.participant_list_model.show_unassigned
            self.ui.tblViewProtocol.setRowHidden(i, hide)

        self.set_shown_protocols()

    @pyqtSlot(int, int)
    def on_group_deleted(self, deleted_group_id: int, new_group_id_of_childs: int):
        try:
            self.active_group_ids.remove(deleted_group_id)
        except:
            pass

        self.updateUI()

    @pyqtSlot()
    def on_tbl_view_protocol_row_visibility_changed(self):
        self.__set_shown_rows_status_label()
        self.set_shown_protocols()
        self.set_show_only_status()

    @pyqtSlot(int)
    def on_check_box_show_only_labels_state_changed(self, new_state: int):
        self.set_show_only_status()

    @pyqtSlot(int)
    def on_check_box_show_only_diffs_state_changed(self, new_state: int):
        self.set_show_only_status()

    @pyqtSlot(int)
    def on_proto_to_group_added(self, group_id: int):
        self.expand_group_node(group_id)

    @pyqtSlot(ProtocolLabel)
    def on_protolabel_visibility_changed(self, proto_label: ProtocolLabel):
        self.set_protocol_label_visibility(proto_label)
        self.label_value_model.update()

    @pyqtSlot(list)
    def on_files_dropped(self, files: list):
        self.files_dropped.emit(files)

    @pyqtSlot(bool)
    def on_chkbox_show_differences_clicked(self, checked: bool):
        self.show_differences(checked)

    @pyqtSlot()
    def on_search_action_triggered(self):
        self.ui.btnSearchSelectFilter.setText("Search")
        self.ui.btnSearchSelectFilter.setIcon(QIcon.fromTheme("edit-find"))
        self.set_search_ui_visibility(True)
        self.ui.btnSearchSelectFilter.clicked.disconnect()
        self.ui.btnSearchSelectFilter.clicked.connect(self.on_btn_search_clicked)

    @pyqtSlot()
    def on_select_action_triggered(self):
        self.ui.btnSearchSelectFilter.setText("Select all")
        self.ui.btnSearchSelectFilter.setIcon(QIcon.fromTheme("edit-select-all"))
        self.set_search_ui_visibility(False)
        self.ui.btnSearchSelectFilter.clicked.disconnect()
        self.ui.btnSearchSelectFilter.clicked.connect(self.select_all_search_results)

    @pyqtSlot()
    def on_filter_action_triggered(self):
        self.ui.btnSearchSelectFilter.setText("Filter")
        self.ui.btnSearchSelectFilter.setIcon(QIcon.fromTheme("view-filter"))
        self.set_search_ui_visibility(False)
        self.ui.btnSearchSelectFilter.clicked.disconnect()
        self.ui.btnSearchSelectFilter.clicked.connect(self.filter_search_results)

    @pyqtSlot()
    def on_align_action_triggered(self):
        def on_btn_search_select_filter_clicked():
            self.align_messages()

        self.ui.btnSearchSelectFilter.setText("Align")
        self.ui.btnSearchSelectFilter.setIcon(QIcon.fromTheme("align-horizontal-left"))
        self.set_search_ui_visibility(False)
        self.ui.btnSearchSelectFilter.clicked.disconnect()
        self.ui.btnSearchSelectFilter.clicked.connect(on_btn_search_select_filter_clicked)

    @pyqtSlot(bool)
    def on_writeable_changed(self, writeable_status: bool):
        hidden_rows = {i for i in range(self.protocol_model.row_count) if self.ui.tblViewProtocol.isRowHidden(i)}
        self.protocol_model.is_writeable = writeable_status
        self.proto_tree_model.set_copy_mode(writeable_status)
        self.ui.cbDecoding.setDisabled(writeable_status)
        self.refresh()
        self.ui.tblViewProtocol.hide_row(hidden_rows)

    @pyqtSlot()
    def on_project_updated(self):
        self.participant_list_model.update()
        self.protocol_model.refresh_vertical_header()
        self.active_message_type = self.proto_analyzer.default_message_type

    @pyqtSlot(ProtocolLabel)
    def on_label_removed(self, plabel: ProtocolLabel):
        if not plabel.show:
            self.show_all_cols()
            for lbl in self.proto_analyzer.protocol_labels:
                self.set_protocol_label_visibility(lbl)

            self.ui.tblViewProtocol.resize_columns()

        self.protocol_model.update()
        self.protocol_label_list_model.update()
        self.label_value_model.update()

    @pyqtSlot(ProtocolLabel, MessageType)
    def on_apply_decoding_changed(self, lbl: ProtocolLabel, message_type: MessageType):
        for msg in self.proto_analyzer.messages:
            if msg.message_type == message_type:
                msg.clear_decoded_bits()
                msg.clear_encoded_bits()

    @pyqtSlot()
    def on_label_selection_changed(self):
        rows = [index.row() for index in self.ui.listViewLabelNames.selectedIndexes()]
        if len(rows) == 0:
            return

        maxrow = numpy.max(rows)

        label = self.protocol_label_list_model.message_type[maxrow]
        if not label.show:
            return

        try:
            message = next(msg for msg in self.proto_analyzer.messages if label if msg.message_type)
        except StopIteration:
            # No messages present
            return
        start, end = message.get_label_range(label, self.protocol_model.proto_view, True)
        indx = self.protocol_model.index(0, int((start + end) / 2))

        self.ui.tblViewProtocol.scrollTo(indx)

    @pyqtSlot(int)
    def on_undo_stack_index_changed(self, index: int):
        self.protocol_model.update()
        self.protocol_label_list_model.update()
        self.search()

    @pyqtSlot(ProtocolLabel)
    def on_edit_label_clicked_in_table(self, proto_label: ProtocolLabel):

        message_type = self.get_message_type_for_label(proto_label)
        try:
            self.show_protocol_label_dialog(message_type.index(proto_label))
        except AttributeError:
            self.show_protocol_label_dialog(0)

    @pyqtSlot(int)
    def on_edit_label_action_triggered(self, preselected_index: int):
        self.show_protocol_label_dialog(preselected_index)

    @pyqtSlot()
    def on_protocol_view_changed(self):
        old_view = self.protocol_model.proto_view
        selected_indexes = self.ui.tblViewProtocol.selectionModel().selectedIndexes()
        sel_cols = [index.column() for index in selected_indexes]
        sel_rows = [index.row() for index in selected_indexes]

        self.show_all_cols()
        self.protocol_model.proto_view = self.ui.cbProtoView.currentIndex()
        self.clear_search()

        for lbl in self.proto_analyzer.protocol_labels:
            self.set_protocol_label_visibility(lbl)

        self.set_show_only_status()

        self.restore_selection(old_view, sel_cols, sel_rows)

    @pyqtSlot()
    def on_item_in_proto_tree_dropped(self):
        self.__protocols = None
        self.set_shown_protocols()
        self.ui.treeViewProtocols.clearSelection()

    @pyqtSlot()
    def on_tree_view_selection_changed(self):
        indexes = self.ui.treeViewProtocols.selectedIndexes()

        selected_items = [self.proto_tree_model.getItem(index) for index in indexes]

        self.ui.tblViewProtocol.blockSignals(True)
        active_group_ids = set()
        sel = QItemSelection()

        for item in selected_items:
            if item.is_group:
                active_group_ids.add(self.proto_tree_model.rootItem.index_of(item))
            elif item.show:
                active_group_ids.add(self.proto_tree_model.rootItem.index_of(item.parent()))

        if len(active_group_ids) == 0:
            active_group_ids.add(0)

        if active_group_ids == set(self.active_group_ids):
            ignore_table_model_on_update = True
        else:
            ignore_table_model_on_update = False
            self.active_group_ids = list(active_group_ids)
            self.active_group_ids.sort()

        self.ui.tblViewProtocol.selectionModel().select(sel, QItemSelectionModel.ClearAndSelect)
        self.ui.tblViewProtocol.blockSignals(False)

        self.updateUI(ignore_table_model=ignore_table_model_on_update)

    @pyqtSlot()
    def on_table_selection_timer_timeout(self):
        min_row, max_row, start, end = self.ui.tblViewProtocol.selection_range()

        if min_row == max_row == start == end == -1:
            self.ui.lBitsSelection.setText("")
            self.ui.lDecimalSelection.setText("")
            self.ui.lHexSelection.setText("")
            self.ui.lNumSelectedColumns.setText("0")
            self.ui.lblLabelValues.setText(self.tr("Label values for message "))
            self.label_value_model.message_index = -1
            self.active_message_type = self.proto_analyzer.default_message_type
            self.__set_decoding_error_label(message=None)
            return -1, -1

        selected_messages = self.selected_messages

        cur_view = self.ui.cbProtoView.currentIndex()
        self.ui.lNumSelectedColumns.setText(str(end - start))

        message = self.proto_analyzer.messages[min_row]
        self.active_message_type = message.message_type

        if cur_view == 1:
            start *= 4
            end *= 4
        elif cur_view == 2:
            start *= 8
            end *= 8

        bits = message.decoded_bits_str[start:end]
        sym_ind = [i for i, b in enumerate(bits) if b not in ("0", "1")]
        hex_bits = []
        pos = 0
        decimals = []
        for si in sym_ind:
            hb = bits[pos:si]
            hex_bits.append("".join("{0:x}".format(int(hb[i:i + 4], 2)) for i in range(0, len(hb), 4)))
            hex_bits.append(bits[si])

            if len(hb) > 0:
                decimals.append(str(int(hb, 2)))
            decimals.append(bits[si])

            pos = si + 1
        hex_bits.append("".join("{0:x}".format(int(bits[pos:][i:i + 4], 2)) for i in range(0, len(bits[pos:]), 4)))
        if len(bits[pos:]) > 0:
            decimals.append(str(int(bits[pos:], 2)))

        # hexs = "".join(["{0:x}".format(int(bits[i:i + 4], 2)) for i in range(0, len(bits), 4)])
        hexs = "".join(hex_bits)

        self.ui.lBitsSelection.setText(bits)
        self.ui.lHexSelection.setText(hexs)
        self.__set_decoding_error_label(message)
        if len(decimals) > 0:
            self.ui.lDecimalSelection.setText("".join(decimals))
        else:
            self.ui.lDecimalSelection.setText("")

        self.ui.lblLabelValues.setText(self.tr("Label values for message #") + str(min_row + 1))
        if min_row != self.label_value_model.message_index:
            self.label_value_model.message_index = min_row

        active_group_ids = set()
        selection = QItemSelection()
        self.selected_protocols.clear()

        for group, tree_items in self.proto_tree_model.protocol_tree_items.items():
            for i, tree_item in enumerate(tree_items):
                proto = tree_item.protocol
                if proto.show and proto in self.rows_for_protocols:
                    if any(i in self.rows_for_protocols[proto] for i in range(min_row, max_row + 1)):
                        active_group_ids.add(group)
                        self.selected_protocols.add(proto)

        if active_group_ids != set(self.active_group_ids):
            self.active_group_ids = list(active_group_ids)
            self.active_group_ids.sort()

        self.ui.lblRSSI.setText(locale.format_string("%.2f", message.rssi))
        if isinstance(message.absolute_time, str):
            # For protocol files the abs time is the timestamp as string
            abs_time = message.absolute_time
        else:
            abs_time = Formatter.science_time(message.absolute_time)

        rel_time = Formatter.science_time(message.relative_time)
        self.ui.lTime.setText("{0} (+{1})".format(abs_time, rel_time))

        # Set Decoding Combobox
        self.ui.cbDecoding.blockSignals(True)
        different_encodings = False
        enc = message.decoder
        for message in selected_messages:
            if message.decoder != enc:
                different_encodings = True
                break

        if not different_encodings:
            self.ui.cbDecoding.setCurrentText(message.decoder.name)
        else:
            self.ui.cbDecoding.setCurrentText("...")
        self.ui.cbDecoding.blockSignals(False)

        self.ui.treeViewProtocols.blockSignals(True)
        self.ui.treeViewProtocols.selectionModel().select(selection, QItemSelectionModel.ClearAndSelect)
        self.ui.treeViewProtocols.blockSignals(False)

        self.updateUI(ignore_table_model=True, resize_table=False)

    @pyqtSlot(int)
    def on_ref_index_changed(self, new_ref_index: int):
        if new_ref_index != -1:
            hide_correction = 0
            for i in range(0, self.protocol_model.row_count):
                if self.ui.tblViewProtocol.isRowHidden((new_ref_index + i) % self.protocol_model.row_count):
                    hide_correction = 0
                else:
                    hide_correction = i
                    break

            self.protocol_model.refindex = (new_ref_index + hide_correction) % self.protocol_model.row_count

        self.set_show_only_status()

    @pyqtSlot(int)
    def on_combobox_messagetype_index_changed(self, index: int):
        self.active_message_type = self.proto_analyzer.message_types[index]

    @pyqtSlot(MessageType, list)
    def on_message_type_selected(self, message_type: MessageType, selected_messages: list):
        for msg in selected_messages:
            msg.message_type = message_type
        self.active_message_type = message_type
        self.protocol_model.update()

    @pyqtSlot(str)
    def on_message_type_name_edited(self, edited_str: str):
        if self.active_message_type == self.proto_analyzer.message_types[self.ui.cbMessagetypes.currentIndex()]:
            self.active_message_type.name = edited_str
            self.ui.cbMessagetypes.setItemText(self.ui.cbMessagetypes.currentIndex(), edited_str)

    @pyqtSlot(int)
    def on_message_type_dialog_finished(self, status: int):
        self.update_automatic_assigned_message_types()

    @pyqtSlot()
    def on_participant_edited(self):
        self.refresh_assigned_participants_ui()

    @pyqtSlot(str)
    def on_label_shown_link_activated(self, link: str):
        if link == "reset_filter":
            self.ui.lineEditSearch.clear()
            self.show_all_rows()

    @pyqtSlot(str)
    def on_label_clear_alignment_link_activated(self, link: str):
        if link == "reset_alignment":
            self.align_messages(pattern="")

    @pyqtSlot()
    def on_protocol_updated(self):
        self.set_shown_protocols()
        self.ui.tblViewProtocol.zero_hide_offsets.clear()
