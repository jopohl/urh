import locale
import os
import time

import numpy
from PyQt5.QtCore import pyqtSlot, QTimer, Qt, pyqtSignal, QItemSelection, QItemSelectionModel, QLocale
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QMessageBox, QFrame, QAbstractItemView, QUndoStack, QMenu

from urh import constants
from urh.controller.MessageTypeDialogController import MessageTypeDialogController
from urh.controller.ProtocolLabelController import ProtocolLabelController
from urh.models.LabelValueTableModel import LabelValueTableModel
from urh.models.ParticipantListModel import ParticipantListModel
from urh.models.ProtocolLabelListModel import ProtocolLabelListModel
from urh.models.ProtocolTableModel import ProtocolTableModel
from urh.models.ProtocolTreeModel import ProtocolTreeModel
from urh.plugins.PluginManager import PluginManager
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolGroup import ProtocolGroup
from urh.signalprocessing.encoder import Encoder
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.ui_analysis import Ui_TabAnalysis
from urh.util import FileOperator
from urh.util.Formatter import Formatter
from urh.util.Logger import logger
from urh.util.ProjectManager import ProjectManager


class CompareFrameController(QFrame):
    show_interpretation_clicked = pyqtSignal(int, int, int, int)
    show_decoding_clicked = pyqtSignal()
    files_dropped = pyqtSignal(list)
    participant_changed = pyqtSignal()
    show_config_field_types_triggered = pyqtSignal()

    def __init__(self, plugin_manager: PluginManager, project_manager: ProjectManager, parent):

        super().__init__(parent)

        self.proto_analyzer = ProtocolAnalyzer(None)
        self.project_manager = project_manager
        self.decodings = []  # type: list[Encoder]
        self.load_decodings()

        self.ui = Ui_TabAnalysis()
        self.ui.setupUi(self)
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

        self.search_select_search_menu = QMenu()
        self.search_action = self.search_select_search_menu.addAction(self.tr("Search"))
        self.select_action = self.search_select_search_menu.addAction(self.tr("Select all"))
        self.filter_action = self.search_select_search_menu.addAction(self.tr("Filter"))
        self.ui.btnSearchSelectFilter.setMenu(self.search_select_search_menu)

        self.analyze_menu = QMenu()
        self.assign_participants_action = self.analyze_menu.addAction(self.tr("Assign participants"))
        self.assign_participants_action.setCheckable(True)
        self.assign_participants_action.setChecked(True)
        self.assign_decodings_action = self.analyze_menu.addAction(self.tr("Assign decodings"))
        self.assign_decodings_action.setCheckable(True)
        self.assign_decodings_action.setChecked(True)
        self.assign_message_type_action = self.analyze_menu.addAction(self.tr("Assign message type"))
        self.assign_message_type_action.setCheckable(True)
        self.assign_message_type_action.setChecked(True)
        self.assign_labels_action = self.analyze_menu.addAction(self.tr("Assign labels"))
        self.assign_labels_action.setCheckable(True)
        self.assign_labels_action.setChecked(True)
        self.ui.btnAnalyze.setMenu(self.analyze_menu)

        self.ui.lFilterShown.hide()

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

        self.selection_timer = QTimer()
        self.selection_timer.setSingleShot(True)

        self.setFrameStyle(0)
        self.setAcceptDrops(False)

        self.proto_tree_model = ProtocolTreeModel(controller=self)  # type: ProtocolTreeModel
        self.ui.treeViewProtocols.setModel(self.proto_tree_model)

        self.create_connects()
        self.fill_decoding_combobox()

        self.rows_for_protocols = {}
        self.__protocols = None

        self.min_height = self.minimumHeight()
        self.max_height = self.maximumHeight()

        self.__set_decoding_error_label(None)

        self.__set_default_message_type_ui_status()

        self.field_types = FieldType.load_from_xml()
        self.field_types_by_id = {field_type.id: field_type for field_type in self.field_types}
        self.field_types_by_caption = {field_type.caption: field_type for field_type in self.field_types}

    # region properties

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
        :rtype: list of ProtocolAnalyzer
        """
        result = []
        for group in self.groups:
            result.extend(group.protocols)
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
            self.ui.lDecodingErrorsValue.setText("")

            # self.ui.lSupport.setStyleSheet("color: green")

    def create_connects(self):
        self.protocol_undo_stack.indexChanged.connect(self.on_undo_stack_index_changed)
        self.ui.cbProtoView.currentIndexChanged.connect(self.on_protocol_view_changed)
        self.ui.cbDecoding.currentIndexChanged.connect(self.on_combobox_decoding_current_index_changed)
        self.ui.cbShowDiffs.clicked.connect(self.on_chkbox_show_differences_clicked)
        self.ui.chkBoxOnlyShowLabelsInProtocol.stateChanged.connect(self.on_check_box_show_only_labels_state_changed)
        self.ui.chkBoxShowOnlyDiffs.stateChanged.connect(self.on_check_box_show_only_diffs_state_changed)

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

        self.ui.btnSearchSelectFilter.clicked.connect(self.on_btn_search_clicked)
        self.ui.btnNextSearch.clicked.connect(self.on_btn_next_search_clicked)
        self.ui.btnPrevSearch.clicked.connect(self.on_btn_prev_search_clicked)
        self.ui.lineEditSearch.returnPressed.connect(self.ui.btnSearchSelectFilter.click)
        self.search_action.triggered.connect(self.on_search_action_triggered)
        self.select_action.triggered.connect(self.on_select_action_triggered)
        self.filter_action.triggered.connect(self.on_filter_action_triggered)

        self.protocol_label_list_model.protolabel_visibility_changed.connect(self.on_protolabel_visibility_changed)
        self.protocol_label_list_model.protolabel_type_edited.connect(self.label_value_model.update)
        self.protocol_label_list_model.label_removed.connect(self.on_label_removed)

        self.ui.btnSaveProto.clicked.connect(self.on_btn_save_protocol_clicked)
        self.ui.btnAnalyze.clicked.connect(self.on_btn_analyze_clicked)

        self.ui.listViewLabelNames.editActionTriggered.connect(self.on_edit_label_action_triggered)
        self.ui.listViewLabelNames.configureActionTriggered.connect(self.show_config_field_types_triggered.emit)
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

    def set_decoding(self, decoding: Encoder, messages=None):
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

            self.clear_search()

            selected = self.ui.tblViewProtocol.selectionModel().selection()

            if not selected.isEmpty() and self.isVisible() and self.proto_analyzer.num_messages > 0:
                max_row = numpy.max([rng.bottom() for rng in selected])
                max_row = max_row if max_row < len(self.proto_analyzer.messages) else -1
                try:
                    msg = self.proto_analyzer.messages[max_row]
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

    def load_decodings(self):
        if self.project_manager.project_file:
            prefix = os.path.realpath(os.path.dirname(self.project_manager.project_file))
        else:
            prefix = os.path.realpath(os.path.join(constants.SETTINGS.fileName(), ".."))

        fallback = [Encoder(["Non Return To Zero (NRZ)"]),

                    Encoder(["Non Return To Zero Inverted (NRZ-I)",
                             constants.DECODING_INVERT]),

                    Encoder(["Manchester I",
                             constants.DECODING_EDGE]),

                    Encoder(["Manchester II",
                             constants.DECODING_EDGE,
                             constants.DECODING_INVERT]),

                    Encoder(["Differential Manchester",
                             constants.DECODING_EDGE,
                             constants.DECODING_DIFFERENTIAL])
                    ]

        try:
            f = open(os.path.join(prefix, constants.DECODINGS_FILE), "r")
        except FileNotFoundError:
            self.decodings = fallback
            return

        if not f:
            self.decodings = fallback
            return

        self.decodings = []
        """:type: list of encoding """

        for line in f:
            tmp_conf = []
            for j in line.split(","):
                tmp = j.strip()
                tmp = tmp.replace("'", "")
                if not "\n" in tmp and tmp != "":
                    tmp_conf.append(tmp)
            self.decodings.append(Encoder(tmp_conf))
        f.close()

        if len(self.decodings) == 0:
            self.decodings = fallback

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
        protocol.qt_signals.protocol_updated.connect(self.set_shown_protocols)
        if protocol.signal:
            protocol.signal.sample_rate_changed.connect(self.set_shown_protocols)  # Refresh times
        protocol.qt_signals.show_state_changed.connect(self.set_shown_protocols)
        protocol.qt_signals.show_state_changed.connect(self.filter_search_results)
        for i in range(self.proto_tree_model.ngroups):
            self.expand_group_node(i)
        return protocol

    def add_protocol_from_file(self, filename: str) -> ProtocolAnalyzer:
        """

        :rtype: list of ProtocolAnalyzer
        """
        pa = ProtocolAnalyzer(signal=None)
        pa.name = "Loaded Protocol"
        pa.filename = filename
        pa.from_xml_file(filename=filename, read_bits=True)
        for messsagetype in pa.message_types:
            if messsagetype not in self.proto_analyzer.message_types:
                self.proto_analyzer.message_types.append(messsagetype)

        self.fill_message_type_combobox()
        self.add_protocol(protocol=pa)

        self.set_shown_protocols()
        return pa

    def add_sniffed_protocol_messages(self, messages: list):
        if len(messages) > 0:
            proto_analyzer = ProtocolAnalyzer(None)
            proto_analyzer.messages = messages
            self.add_protocol(proto_analyzer, group_id=self.proto_tree_model.ngroups - 1)
            self.refresh()

    def add_protocol_label(self, start: int, end: int, messagenr: int, proto_view: int, edit_label_name=True):
        # Ensure atleast one Group is active
        start, end = self.proto_analyzer.convert_range(start, end, proto_view, 0, decoded=True, message_indx=messagenr)
        proto_label = self.proto_analyzer.messages[messagenr].message_type.add_protocol_label(start=start, end=end)

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
        # Instant Visual Refresh of Tree
        self.proto_tree_model.update()
        self.ui.treeViewProtocols.expandAll()

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
                        if i > 0:
                            rel_time = proto.messages[i - 1].get_duration(proto.signal.sample_rate)
                            abs_time += rel_time
                    except (IndexError, AttributeError):
                        pass  # No signal, loaded from protocol file

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

        # Hidden Rows auf neue Reihenfolge übertragen
        [self.ui.tblViewProtocol.showRow(i) for i in range(self.protocol_model.row_count)]
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

        startCol, endCol = numpy.min(sel_cols), numpy.max(sel_cols)
        startRow, endRow = numpy.min(sel_rows), numpy.max(sel_rows)
        new_view = self.ui.cbProtoView.currentIndex()

        message = self.proto_analyzer.messages[endRow]
        startCol = message.convert_index(startCol, old_view, new_view, True)[0]
        endCol = message.convert_index(endCol, old_view, new_view, True)[1]

        endCol = endCol if endCol < len(self.protocol_model.display_data[endRow]) else len(
            self.protocol_model.display_data[endRow]) - 1

        startindex = self.protocol_model.index(startRow, startCol)
        endindex = self.protocol_model.index(endRow, endCol)
        mid_index = self.protocol_model.index(int((startRow + endRow) / 2), int((startCol + endCol) / 2))

        sel = QItemSelection()
        sel.select(startindex, endindex)

        self.ui.tblViewProtocol.selectionModel().select(sel, QItemSelectionModel.ClearAndSelect)
        self.ui.tblViewProtocol.scrollTo(mid_index)

    def expand_group_node(self, group_id):
        self.ui.treeViewProtocols.expand(
            self.proto_tree_model.createIndex(group_id, 0, self.proto_tree_model.rootItem.child(group_id)))

    def updateUI(self, ignore_table_model=False, resize_table=True):
        if not ignore_table_model:
            self.protocol_model.update()

        self.protocol_label_list_model.update()
        self.proto_tree_model.layoutChanged.emit()  # no not call update, as it prevents editing
        self.ui.treeViewProtocols.expandAll()
        self.label_value_model.update()
        self.protocol_label_list_model.update()

        if resize_table:
            self.ui.tblViewProtocol.resize_columns()

    def refresh(self):
        self.__protocols = None
        self.set_shown_protocols()
        self.updateUI()

    def reset(self):
        for message_type in self.proto_analyzer.message_types:
            message_type.clear()
        self.proto_tree_model.rootItem.clearChilds()
        self.proto_tree_model.rootItem.addGroup()
        self.refresh()

    def show_protocol_label_dialog(self, preselected_index: int):
        view_type = self.ui.cbProtoView.currentIndex()
        longest_message = max((msg for msg in self.proto_analyzer.messages if msg.message_type == self.active_message_type), key=len)
        label_controller = ProtocolLabelController(preselected_index=preselected_index,
                                                   message=longest_message, viewtype=view_type, parent=self)
        label_controller.apply_decoding_changed.connect(self.on_apply_decoding_changed)
        label_controller.exec_()

        self.protocol_label_list_model.update()
        self.update_field_type_combobox()
        self.label_value_model.update()
        self.show_all_cols()
        for lbl in self.proto_analyzer.protocol_labels:
            self.set_protocol_label_visibility(lbl)
        self.set_show_only_status()
        self.protocol_model.update()
        self.ui.tblViewProtocol.resize_columns()

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
        if self.ui.btnSearchSelectFilter.text() != "Filter":
            return

        if self.ui.lineEditSearch.text():
            self.search()
            self.ui.tblLabelValues.clearSelection()

            matching_rows = set(search_result[0] for search_result in self.protocol_model.search_results)
            self.ui.tblViewProtocol.blockSignals(True)
            rc = self.protocol_model.row_count
            for i in set(range(0, rc)) - matching_rows:
                self.ui.tblViewProtocol.hide_row(row=i)
            self.ui.tblViewProtocol.blockSignals(False)
            self.ui.tblViewProtocol.row_visibility_changed.emit()

            self.ui.lFilterShown.setText(self.tr("shown: {}/{}".format(rc - len(self.protocol_model.hidden_rows), rc)))

        else:
            for i in range(0, self.protocol_model.row_count):
                self.ui.tblViewProtocol.showRow(i)

            self.ui.lFilterShown.setText("")
            self.set_shown_protocols()

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
        self.ui.lineEditSearch.clear()
        self.ui.btnPrevSearch.setEnabled(False)
        self.ui.btnNextSearch.setEnabled(False)
        self.ui.lSearchTotal.setText("-")
        self.ui.lSearchCurrent.setText("-")
        self.protocol_model.search_results[:] = []
        self.protocol_model.search_value = ""

    def set_protocol_label_visibility(self, lbl: ProtocolLabel, message: Message = None):
        try:
            message = message if message else next(
                msg for msg in self.proto_analyzer.messages if lbl in msg.message_type)
            start, end = message.get_label_range(lbl, self.ui.cbProtoView.currentIndex(), True)

            for i in range(start, end):
                self.ui.tblViewProtocol.setColumnHidden(i, not lbl.show)
        except Exception as e:
            pass

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
        filename = FileOperator.get_save_file_name("{0}.proto".format(text), caption="Save protocol")

        if not filename:
            return

        self.proto_analyzer.to_xml_file(filename=filename, decoders=self.decodings,
                                        participants=self.project_manager.participants, write_bits=True)

    def show_differences(self, show_differences: bool):
        if show_differences:
            if self.protocol_model.refindex == -1:
                self.protocol_model.refindex = 0
        else:
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
            for lbl in msg.message_type:
                if lbl.show:
                    start, end = msg.get_label_range(lbl=lbl, view=self.ui.cbProtoView.currentIndex(),
                                                     decode=True)
                    visible_columns |= (set(range(start, end)))

        for i in range(self.protocol_model.col_count):
            if i in visible_columns:
                self.ui.tblViewProtocol.showColumn(i)
            else:
                self.ui.tblViewProtocol.hideColumn(i)

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
        selected = self.ui.tblViewProtocol.selectionModel().selection()
        """:type: QtWidgets.QItemSelection """

        for i in range(self.protocol_model.col_count):
            self.ui.tblViewProtocol.showColumn(i)

        for lbl in self.proto_analyzer.protocol_labels:
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

    def reload_field_types(self):
        self.field_types = FieldType.load_from_xml()
        self.field_types_by_id = {field_type.id: field_type for field_type in self.field_types}
        self.field_types_by_caption = {field_type.caption: field_type for field_type in self.field_types}

    def refresh_field_types_for_labels(self):
        self.reload_field_types()
        for mt in self.proto_analyzer.message_types:
            for lbl in (lbl for lbl in mt if lbl.type is not None):  # type: ProtocolLabel
                if lbl.type.id not in self.field_types_by_id:
                    lbl.type = None
                else:
                    lbl.type = self.field_types_by_id[lbl.type.id]

        self.update_field_type_combobox()

    def mousePressEvent(self, event):
        return

    def contextMenuEvent(self, event: QContextMenuEvent):
        pass

    @pyqtSlot()
    def on_btn_analyze_clicked(self):
        self.setCursor(Qt.WaitCursor)
        self.ui.stackedWidgetLogicAnalysis.setCurrentIndex(1)

        self.ui.progressBarLogicAnalyzer.setFormat("%p% (Detecting participants)")
        self.ui.progressBarLogicAnalyzer.setValue(0)

        if self.assign_participants_action.isChecked():
            t = time.time()
            for protocol in self.protocol_list:
                protocol.auto_assign_participants(self.protocol_model.participants)
            self.refresh_assigned_participants_ui()
            logger.debug("Time for auto assigning participants: " + str(time.time() - t))

        self.ui.progressBarLogicAnalyzer.setFormat("%p% (Assign decodings)")
        self.ui.progressBarLogicAnalyzer.setValue(25)

        if self.assign_decodings_action.isChecked():
            t = time.time()
            self.proto_analyzer.auto_assign_decodings(self.decodings)
            self.protocol_model.update()
            self.label_value_model.update()
            logger.debug("Time for auto assigning decodings: " + str(time.time() - t))

        self.ui.progressBarLogicAnalyzer.setFormat("%p% (Assign message type by rules)")
        self.ui.progressBarLogicAnalyzer.setValue(50)

        if self.assign_message_type_action.isChecked():
            t = time.time()
            self.update_automatic_assigned_message_types()
            logger.debug("Time for auto assigning message types: " + str(time.time() - t))

        self.ui.progressBarLogicAnalyzer.setFormat("%p% (Find new labels/message types)")
        self.ui.progressBarLogicAnalyzer.setValue(75)

        if self.assign_labels_action.isChecked():
            t = time.time()
            self.proto_analyzer.auto_assign_labels()
            self.protocol_model.update()
            self.label_value_model.update()
            self.protocol_label_list_model.update()
            self.ui.listViewLabelNames.clearSelection()
            logger.debug("Time for auto assigning labels: " + str(time.time() - t))

        self.ui.progressBarLogicAnalyzer.setValue(100)
        self.unsetCursor()
        self.ui.stackedWidgetLogicAnalysis.setCurrentIndex(0)

        self.fill_message_type_combobox()  # in case message types were added by logic analyzer

    @pyqtSlot()
    def on_btn_save_protocol_clicked(self):
        self.save_protocol()

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
        dialog = MessageTypeDialogController(self.active_message_type, parent=self)
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
        self.ui.lFilterShown.hide()
        self.ui.btnSearchSelectFilter.setText("Search")
        self.set_search_ui_visibility(True)
        self.ui.btnSearchSelectFilter.clicked.disconnect()
        self.ui.btnSearchSelectFilter.clicked.connect(self.on_btn_search_clicked)

    @pyqtSlot()
    def on_select_action_triggered(self):
        self.ui.lFilterShown.hide()
        self.ui.btnSearchSelectFilter.setText("Select all")
        self.set_search_ui_visibility(False)
        self.ui.btnSearchSelectFilter.clicked.disconnect()
        self.ui.btnSearchSelectFilter.clicked.connect(self.select_all_search_results)

    @pyqtSlot()
    def on_filter_action_triggered(self):
        if len(self.protocol_model.hidden_rows) == 0:
            self.ui.lFilterShown.setText("")
        else:
            nhidden = len(self.protocol_model.hidden_rows)
            rc = self.protocol_model.row_count
            self.ui.lFilterShown.setText("shown: {}/{}".format(rc - nhidden, rc))

        self.ui.lFilterShown.show()
        self.ui.btnSearchSelectFilter.setText("Filter")
        self.set_search_ui_visibility(False)
        self.ui.btnSearchSelectFilter.clicked.disconnect()
        self.ui.btnSearchSelectFilter.clicked.connect(self.filter_search_results)

    @pyqtSlot(bool)
    def on_writeable_changed(self, writeable_status: bool):
        self.protocol_model.is_writeable = writeable_status
        self.proto_tree_model.set_copy_mode(writeable_status)
        self.refresh()

    @pyqtSlot()
    def on_project_updated(self):
        self.participant_list_model.participants = self.project_manager.participants
        self.participant_list_model.update()
        self.protocol_model.participants = self.project_manager.participants
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
        selected = self.ui.tblViewProtocol.selectionModel().selection()
        """:type: QtWidgets.QItemSelection """

        if selected.isEmpty():
            self.ui.lBitsSelection.setText("")
            self.ui.lDecimalSelection.setText("")
            self.ui.lHexSelection.setText("")
            self.ui.lNumSelectedColumns.setText("0")
            self.ui.lblLabelValues.setText(self.tr("Label values for message "))
            self.label_value_model.message_index = -1
            self.active_message_type = self.proto_analyzer.default_message_type
            return -1, -1

        min_row = numpy.min([rng.top() for rng in selected])
        max_row = numpy.max([rng.bottom() for rng in selected])
        start = numpy.min([rng.left() for rng in selected])
        end = numpy.max([rng.right() for rng in selected]) + 1

        selected_messages = self.selected_messages

        cur_view = self.ui.cbProtoView.currentIndex()
        self.ui.lNumSelectedColumns.setText(str(end - start))

        self.active_message_type = self.proto_analyzer.messages[max_row].message_type

        if cur_view == 1:
            start *= 4
            end *= 4
        elif cur_view == 2:
            start *= 8
            end *= 8

        bits = self.proto_analyzer.decoded_proto_bits_str[max_row][start:end]
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
        message = self.proto_analyzer.messages[max_row]

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
        if new_ref_index == -1:
            self.proto_tree_model.reference_protocol = -1
        else:
            i = 0
            visible_protos = [proto for proto in self.protocol_list if proto.show]
            for proto in visible_protos:
                i += proto.num_messages
                if i > new_ref_index:
                    self.proto_tree_model.reference_protocol = proto
                    return
            self.proto_tree_model.reference_protocol = -1

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
