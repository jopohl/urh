import locale
import os

import numpy
import time
from PyQt5.QtCore import pyqtSlot, QTimer, Qt, pyqtSignal, QItemSelection, QItemSelectionModel, QLocale, QModelIndex
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QMessageBox, QFrame, QAbstractItemView, QUndoStack, QApplication, QMenu

from urh import constants
from urh.controller.MessageTypeDialogController import MessageTypeDialogController
from urh.controller.OptionsController import OptionsController
from urh.controller.ProtocolLabelController import ProtocolLabelController
from urh.controller.ProtocolSniffDialogController import ProtocolSniffDialogController
from urh.models.LabelValueTableModel import LabelValueTableModel
from urh.models.ParticipantListModel import ParticipantListModel
from urh.models.ProtocolLabelListModel import ProtocolLabelListModel
from urh.models.ProtocolTableModel import ProtocolTableModel
from urh.models.ProtocolTreeModel import ProtocolTreeModel
from urh.plugins.PluginManager import PluginManager
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Message import Message
from urh.signalprocessing.encoding import encoding
from urh.signalprocessing.ProtocolGroup import ProtocolGroup
from urh.ui.ui_analysis_frame import Ui_FAnalysis
from urh.util import FileOperator
from urh.util.Errors import Errors
from urh.util.Formatter import Formatter
from urh.util.Logger import logger
from urh.util.ProjectManager import ProjectManager


class CompareFrameController(QFrame):
    show_interpretation_clicked = pyqtSignal(int, int, int, int)
    show_decoding_clicked = pyqtSignal()
    files_dropped = pyqtSignal(list)
    participant_changed = pyqtSignal()

    def __init__(self, plugin_manager: PluginManager,
                 project_manager: ProjectManager, parent):

        super().__init__(parent)

        self.proto_analyzer = ProtocolAnalyzer(None)
        self.project_manager = project_manager
        self.decodings = []
        """:type: list of encoding """

        self.load_decodings()

        self.ui = Ui_FAnalysis()
        self.ui.setupUi(self)
        self.ui.lBitsSelection.setText("")
        self.ui.lDecimalSelection.setText("")
        self.ui.lHexSelection.setText("")
        self.plugin_manager = plugin_manager
        clocale = QLocale()
        self.decimal_point = clocale.decimalPoint()

        self.__selected_message_type = self.proto_analyzer.default_message_type
        self.fill_message_type_combobox()


        self.participant_list_model = ParticipantListModel(project_manager.participants)
        self.ui.listViewParticipants.setModel(self.participant_list_model)

        self.__active_group_ids = [0]
        self.selected_protocols = set()

        self.searchselectsearch_menu = QMenu()
        self.search_action = self.searchselectsearch_menu.addAction("Search")
        self.select_action = self.searchselectsearch_menu.addAction("Select all")
        self.filter_action = self.searchselectsearch_menu.addAction("Filter")
        self.ui.btnSearchSelectFilter.setMenu(self.searchselectsearch_menu)

        self.analyze_menue = QMenu()
        self.assign_participants_action = self.analyze_menue.addAction("Assign participants")
        self.assign_participants_action.setCheckable(True)
        self.assign_participants_action.setChecked(True)
        self.assign_decodings_action = self.analyze_menue.addAction("Assign decodings")
        self.assign_decodings_action.setCheckable(True)
        self.assign_decodings_action.setChecked(True)
        self.assign_message_type_action = self.analyze_menue.addAction("Assign message type")
        self.assign_message_type_action.setCheckable(True)
        self.assign_message_type_action.setChecked(True)
        self.assign_labels_action = self.analyze_menue.addAction("Assign labels")
        self.assign_labels_action.setCheckable(True)
        self.assign_labels_action.setChecked(True)
        self.ui.btnAnalyze.setMenu(self.analyze_menue)

        self.ui.lFilterShown.hide()

        self.protocol_model = ProtocolTableModel(self.proto_analyzer, project_manager.participants, self)
        """:type: ProtocolTableModel"""
        self.protocol_label_list_model = ProtocolLabelListModel(self.proto_analyzer, controller=self)
        """:type:  ProtocolLabelListModel"""

        self.label_value_model = LabelValueTableModel(self.proto_analyzer, controller=self)
        self.ui.tblViewProtocol.setModel(self.protocol_model)
        self.ui.tblViewProtocol.controller = self
        self.ui.tblLabelValues.setModel(self.label_value_model)
        self.ui.listViewLabelNames.setModel(self.protocol_label_list_model)

        self.create_connects()

        self.fill_decoding_combobox()
        #self.ui.splitter.setStretchFactor(1, 1)

        self.selection_timer = QTimer()
        self.selection_timer.setSingleShot(True)
        self.selection_timer.timeout.connect(self.on_table_selection_timer_timeout)
        self.setFrameStyle(0)
        self.setAcceptDrops(False)

        self.proto_tree_model = ProtocolTreeModel(controller=self)
        """:type: ProtocolTreeModel """
        self.proto_tree_model.item_dropped.connect(self.handle_item_in_proto_tree_dropped)
        self.ui.treeViewProtocols.setModel(self.proto_tree_model)

        self.rows_for_protocols = {}
        self.__protocols = None

        self.min_height = self.minimumHeight()
        self.max_height = self.maximumHeight()
        self.__show_protocol_seperation = True

        self.protocol_model.ref_index_changed.connect(self.handle_ref_index_changed)
        self.ui.tblViewProtocol.row_visibilty_changed.connect(self.set_shown_protocols)
        self.ui.treeViewProtocols.selection_changed.connect(self.handle_tree_view_selection_changed)
        self.proto_tree_model.group_deleted.connect(self.handle_group_deleted)
        self.proto_tree_model.proto_to_group_added.connect(self.expand_group_node)
        self.proto_tree_model.group_added.connect(self.handle_group_added)

        self.__set_default_message_type_ui_status()

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
    def active_message_type(self):
        return self.__selected_message_type

    @active_message_type.setter
    def active_message_type(self, val):
        if val not in self.proto_analyzer.message_types:
            logger.error("Message type {} not in mesage types".format(val.name))
            return

        self.__selected_message_type = val

        self.ui.cbMessagetypes.blockSignals(True)
        self.ui.cbMessagetypes.setCurrentIndex(self.proto_analyzer.message_types.index(val))
        self.__set_default_message_type_ui_status()
        self.protocol_label_list_model.update()
        self.ui.cbMessagetypes.blockSignals(False)


    def handle_files_dropped(self, files: list):
        self.files_dropped.emit(files)


    def load_decodings(self):
        if self.project_manager.project_file:
            prefix = os.path.realpath(os.path.dirname(
                self.project_manager.project_file))
        else:
            prefix = os.path.realpath(os.path.join(constants.SETTINGS.fileName(), ".."))

        fallback = [encoding(["Non Return To Zero (NRZ)"]),

                    encoding(["Non Return To Zero Inverted (NRZ-I)",
                              constants.DECODING_INVERT]),

                    encoding(["Manchester I",
                              constants.DECODING_EDGE]),

                    encoding(["Manchester II",
                              constants.DECODING_EDGE,
                              constants.DECODING_INVERT]),

                    encoding(["Differential Manchester",
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
            self.decodings.append(encoding(tmp_conf))
        f.close()

        if len(self.decodings) == 0:
            self.decodings = fallback


    @property
    def selected_messages(self):
        return self.ui.tblViewProtocol.selected_messages

    @property
    def protocol_undo_stack(self) -> QUndoStack:
        return self.protocol_model.undo_stack

    @property
    def name(self):
        return self.ui.lSignalName.text()

    @name.setter
    def name(self, value: str):
        self.ui.lSignalName.setText(value)

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

    @property
    def show_protocol_seperation(self):
        return self.__show_protocol_seperation

    @show_protocol_seperation.setter
    def show_protocol_seperation(self, value: bool):
        self.__show_protocol_seperation = value

        if not value:
            for line in self.protocol_model.first_messages:
                self.ui.tblViewProtocol.setRowHeight(line, constants.SEPARATION_ROW_HEIGHT)

        self.set_shown_protocols()

    def create_connects(self):
        self.protocol_undo_stack.indexChanged.connect(self.on_undo_stack_index_changed)

        self.ui.cbShowDiffs.stateChanged.connect(self.on_chkbox_show_differences_changed)
        self.ui.cbProtoView.currentIndexChanged.connect(self.on_protocol_view_changed)
        self.ui.tblViewProtocol.protocol_view_change_clicked.connect(self.ui.cbProtoView.setCurrentIndex)
        self.ui.cbDecoding.currentIndexChanged.connect(self.on_cbDecoding_currentIndexChanged)
        self.ui.tblViewProtocol.show_interpretation_clicked.connect(self.show_interpretation_clicked.emit)

        self.ui.btnSearchSelectFilter.clicked.connect(self.search)

        self.ui.btnNextSearch.clicked.connect(self.next_search_result)
        self.ui.btnPrevSearch.clicked.connect(self.prev_search_result)
        self.protocol_label_list_model.protolabel_visibility_changed.connect(self.set_protocol_label_visibility)
        self.protocol_label_list_model.protolabel_visibility_changed.connect(self.label_value_model.update)
        self.protocol_label_list_model.protolabel_name_changed.connect(self.on_label_name_edited)
        self.ui.btnSaveProto.clicked.connect(self.save_protocol)
        self.ui.tblViewProtocol.selection_changed.connect(self.handle_table_selection_changed)
        self.ui.listViewLabelNames.editActionTriggered.connect(self.show_protocol_labels)
        self.ui.tblViewProtocol.writeable_changed.connect(self.handle_writeable_changed)
        self.protocol_label_list_model.label_removed.connect(self.handle_label_removed)
        self.ui.listViewLabelNames.selection_changed.connect(self.handle_label_selection_changed)
        self.ui.chkBoxOnlyShowLabelsInProtocol.stateChanged.connect(self.handle_show_only_checkbox_changed)
        self.ui.chkBoxShowOnlyDiffs.stateChanged.connect(self.handle_show_only_checkbox_changed)
        self.protocol_model.ref_index_changed.connect(self.handle_show_only_checkbox_changed)
        self.ui.tblViewProtocol.row_visibilty_changed.connect(self.handle_show_only_checkbox_changed)
        self.ui.tblViewProtocol.edit_label_clicked.connect(self.on_edit_label_clicked_in_table)
        self.ui.btnAnalyze.clicked.connect(self.on_btn_analyze_clicked)
        self.ui.tblViewProtocol.files_dropped.connect(self.handle_files_dropped)
        self.project_manager.project_updated.connect(self.on_project_updated)
        self.participant_list_model.show_state_changed.connect(self.set_participant_visibility)
        self.ui.tblViewProtocol.participant_changed.connect(self.on_participant_edited)
        self.ui.tblViewProtocol.messagetype_selected.connect(self.on_message_type_selected)
        self.ui.tblViewProtocol.new_messagetype_clicked.connect(self.on_new_message_type_clicked)
        self.ui.btnAddMessagetype.clicked.connect(self.on_new_message_type_clicked)
        self.ui.btnRemoveMessagetype.clicked.connect(self.on_remove_message_type_clicked)

        self.ui.lineEditSearch.returnPressed.connect(self.ui.btnSearchSelectFilter.click)

        self.ui.cbMessagetypes.currentIndexChanged.connect(self.on_cbmessagetype_index_changed)
        self.ui.cbMessagetypes.editTextChanged.connect(self.on_messagetype_name_edited)

        self.search_action.triggered.connect(self.__set_mode_to_search)
        self.select_action.triggered.connect(self.__set_mode_to_select_all)
        self.filter_action.triggered.connect(self.__set_mode_to_filter)

        self.ui.btnMessagetypeSettings.clicked.connect(self.on_btn_messagetype_settings_clicked)


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

    def on_chkbox_show_differences_changed(self):
        chkd = self.ui.cbShowDiffs.isChecked()

        if chkd:
            if self.protocol_model.refindex == -1:
                self.protocol_model.refindex = 0
        else:
            self.ui.chkBoxShowOnlyDiffs.setChecked(False)
            self.protocol_model.refindex = -1

    def mousePressEvent(self, event):
        return

    def get_message_numbers_for_groups(self) -> dict:
        result = {}
        prev = 0
        for i in sorted(self.protocols.keys()):
            group_protos = self.protocols[i]
            num_messages = prev
            for gp in group_protos:
                if gp.show:
                    num_messages += gp.num_messages
            result[i] = (prev, num_messages)
            prev = num_messages
        return result

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
        self.proto_tree_model.layoutChanged.emit()
        QApplication.processEvents()

        hidden_rows = {i for i in range(self.protocol_model.row_count) if self.ui.tblViewProtocol.isRowHidden(i)}
        relative_hidden_row_positions = {}
        for proto in self.rows_for_protocols.keys():
            if any(i in hidden_rows for i in self.rows_for_protocols[proto]):
                m = min(self.rows_for_protocols[proto])
                relative_hidden_row_positions[proto] = [i - m for i in hidden_rows if
                                                        i in self.rows_for_protocols[proto]]

        # self.protocol_undo_stack.clear()
        self.proto_analyzer.messages[:] = []
        self.proto_analyzer.used_symbols.clear()
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

                self.proto_analyzer.used_symbols |= proto.used_symbols

                line += num_messages
                rows_for_cur_proto = list(range(prev_line, line))
                self.rows_for_protocols[proto] = rows_for_cur_proto[:]


                prev_line = line
                if line != 0:
                    first_msg_indices.append(line)

        if not self.show_protocol_seperation:
            self.protocol_model.first_messages[:] = []
            self.updateUI()
            return

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


        # Hidden Rows berücksichtigen
        for i in range(self.protocol_model.row_count):
            if self.ui.tblViewProtocol.isRowHidden(i) and i in first_msg_indices:
                indx = first_msg_indices.index(i)
                first_msg_indices[indx] += 1
                if indx < len(first_msg_indices) and first_msg_indices[indx] >= first_msg_indices[indx+1]:
                    del first_msg_indices[indx]

        for line in first_msg_indices:
            self.ui.tblViewProtocol.setRowHeight(line, constants.SEPARATION_ROW_HEIGHT)

        self.protocol_model.first_messages = first_msg_indices[:]
        #self.set_decoding(self.decodings[self.ui.cbDecoding.currentIndex()])

        self.updateUI()
        self.on_chkbox_show_differences_changed()

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

        self.handle_show_only_checkbox_changed()

        self.restore_selection(old_view, sel_cols, sel_rows)

    def restore_selection(self, old_view: int, sel_cols, sel_rows):
        if len(sel_cols) == 0 or len(sel_rows) == 0:
            return

        startCol, endCol = numpy.min(sel_cols), numpy.max(sel_cols)
        startRow, endRow = numpy.min(sel_rows), numpy.max(sel_rows)
        new_view = self.ui.cbProtoView.currentIndex()

        message = self.proto_analyzer.messages[endRow]
        startCol = message.convert_index(startCol, old_view, new_view, True)[0]
        endCol = message.convert_index(endCol, old_view, new_view, True)[1]

        endCol = endCol if endCol < len(self.protocol_model.display_data[endRow]) else len(self.protocol_model.display_data[endRow]) - 1

        startindex = self.protocol_model.index(startRow, startCol)
        endindex = self.protocol_model.index(endRow, endCol)
        mid_index = self.protocol_model.index(int((startRow + endRow) / 2), int((startCol + endCol) / 2))

        sel = QItemSelection()
        sel.select(startindex, endindex)

        self.ui.tblViewProtocol.selectionModel().select(sel, QItemSelectionModel.ClearAndSelect)
        self.ui.tblViewProtocol.scrollTo(mid_index)


    def get_group_for_row(self, row: int):
        offset = 0
        for group in self.groups:
            if row in range(offset, offset + group.num_messages):
                return group
            offset += group.num_messages

        return None

    @pyqtSlot()
    def handle_table_selection_changed(self):
        self.selection_timer.start(100)

    @pyqtSlot()
    def on_cbDecoding_currentIndexChanged(self):
        new_index = self.ui.cbDecoding.currentIndex()
        if new_index == -1:
            return

        if new_index == self.ui.cbDecoding.count() - 1:
            self.set_decoding(None)
        else:
            self.set_decoding(self.decodings[new_index], messages=self.selected_messages if self.selected_messages else None)

    def set_decoding(self, decoding: encoding, messages=None):
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
                    reply = QMessageBox.question(self, "Set decoding", "Do you want to apply the selected decoding to {} messages?".format(len(messages)), QMessageBox.Yes | QMessageBox.No);
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

    def __set_decoding_error_label(self, message: Message):
        if message:
            errors = message.decoding_errors
            percent = 100 * (errors / len(message))
            if percent <= 100:
                self.ui.lDecodingErrorsValue.setText(
                    locale.format_string("%d (%.02f%%)", (errors, 100 * (errors / len(message)))))
            else:
                self.ui.lDecodingErrorsValue.setText(locale.format_string("%d", (errors)))
        else:
            self.ui.lDecodingErrorsValue.setText("")

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
                if proto.show and any(i in self.rows_for_protocols[proto] for i in range(min_row, max_row + 1)):
                    #index = self.proto_tree_model.createIndex(i, 0, tree_item)
                    #selection.select(index, index)
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
    def handle_ref_index_changed(self, new_ref_index):
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

    def contextMenuEvent(self, event: QContextMenuEvent):
        pass

    @pyqtSlot()
    def handle_item_in_proto_tree_dropped(self):
        self.__protocols = None
        self.set_shown_protocols()
        self.ui.treeViewProtocols.clearSelection()

    @pyqtSlot()
    def handle_tree_view_selection_changed(self):
        indexes = self.ui.treeViewProtocols.selectedIndexes()

        selected_items = [self.proto_tree_model.getItem(index) for index in indexes]

        self.ui.tblViewProtocol.blockSignals(True)
        active_group_ids = set()
        sel = QItemSelection()

        col_count = self.protocol_model.col_count
        for item in selected_items:
            if item.is_group:
                active_group_ids.add(self.proto_tree_model.rootItem.index_of(item))
            elif item.show:
                active_group_ids.add(self.proto_tree_model.rootItem.index_of(item.parent()))

                # rows_for_proto = self.rows_for_protocols[item.protocol]
                # if len(rows_for_proto) > 0:
                #     startindex = self.protocol_model.index(rows_for_proto[0], 0)
                #     endindex = self.protocol_model.index(rows_for_proto[-1], col_count - 1)
                #     sel.select(startindex, endindex)

        if len(active_group_ids) == 0:
            active_group_ids.add(0)
            show_decoding = False
        else:
            show_decoding = True

        if active_group_ids == set(self.active_group_ids):
            ignore_table_model_on_update = True
        else:
            ignore_table_model_on_update = False
            self.active_group_ids = list(active_group_ids)
            self.active_group_ids.sort()

        self.ui.tblViewProtocol.selectionModel().select(sel, QItemSelectionModel.ClearAndSelect)
        self.ui.tblViewProtocol.blockSignals(False)

        self.updateUI(ignore_table_model=ignore_table_model_on_update)

    @pyqtSlot(QModelIndex)
    def handle_group_added(self, index):
        self.ui.treeViewProtocols.edit(index)

    def handle_group_deleted(self, deleted_group_id, new_group_id_of_childs):
        try:
            self.active_group_ids.remove(deleted_group_id)
        except:
            pass

        self.updateUI()

    def expand_group_node(self, group_id):
        self.ui.treeViewProtocols.expand(
            self.proto_tree_model.createIndex(group_id, 0, self.proto_tree_model.rootItem.child(group_id)))

    def updateUI(self, ignore_table_model=False, resize_table=True):
        if not ignore_table_model:
            self.protocol_model.update()

        self.protocol_label_list_model.update()
        self.proto_tree_model.layoutChanged.emit()
        self.label_value_model.update()
        self.protocol_label_list_model.update()

        if resize_table:
            self.ui.tblViewProtocol.resize_columns()

    def refresh(self):
        self.__protocols = None
        self.set_shown_protocols()
        self.updateUI()

    def reset(self):
        self.proto_tree_model.rootItem.clearChilds()
        self.proto_tree_model.rootItem.addGroup()
        for message_type in self.proto_analyzer.message_types:
            message_type.clear()
        self.refresh()

    @pyqtSlot(int)
    def on_undo_stack_index_changed(self, index: int):
        self.protocol_model.update()
        self.protocol_label_list_model.update()

    @pyqtSlot(ProtocolLabel)
    def on_edit_label_clicked_in_table(self, proto_label: ProtocolLabel):

        message_type = self.get_message_type_for_label(proto_label)
        try:
            self.show_protocol_labels(message_type.index(proto_label))
        except AttributeError:
            self.show_protocol_labels(0)

    @pyqtSlot(int)
    def show_protocol_labels(self, preselected_index: int):
        view_type = self.ui.cbProtoView.currentIndex()
        message = next(msg for msg in self.proto_analyzer.messages if self.active_message_type.id == msg.message_type.id)
        label_controller = ProtocolLabelController(preselected_index=preselected_index, message_type=self.active_message_type,
                                                   max_end=numpy.max([len(msg) for msg in self.proto_analyzer.messages]),
                                                   viewtype=view_type, message=message,
                                                   parent=self)
        label_controller.apply_decoding_changed.connect(self.on_apply_decoding_changed)
        label_controller.exec_()

        self.protocol_label_list_model.update()
        self.label_value_model.update()
        self.show_all_cols()
        for lbl in self.proto_analyzer.protocol_labels:
            self.set_protocol_label_visibility(lbl)
        self.handle_show_only_checkbox_changed()
        self.protocol_model.update()
        self.ui.tblViewProtocol.resize_columns()

    @pyqtSlot(ProtocolLabel, MessageType)
    def on_apply_decoding_changed(self, lbl: ProtocolLabel, message_type: MessageType):
        for msg in self.proto_analyzer.messages:
            if msg.message_type == message_type:
                msg.clear_decoded_bits()
                msg.clear_encoded_bits()

    @pyqtSlot()
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
            self.ui.tblViewProtocol.row_visibilty_changed.emit()

            self.ui.lFilterShown.setText(self.tr("shown: {}/{}".format(rc-len(self.protocol_model.hidden_rows), rc)))

        else:
            for i in range(0, self.protocol_model.row_count):
                self.ui.tblViewProtocol.showRow(i)

            self.ui.lFilterShown.setText("")
            self.set_shown_protocols()

    @pyqtSlot()
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

    @pyqtSlot()
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
            message = message if message else next(msg for msg in self.proto_analyzer.messages if lbl in msg.message_type)
            start, end = message.get_label_range(lbl, self.ui.cbProtoView.currentIndex(), True)

            for i in range(start, end):
                self.ui.tblViewProtocol.setColumnHidden(i, not lbl.show)
        except Exception as e:
            pass

    def get_message_type_for_label(self, lbl: ProtocolLabel) -> MessageType:
        for msg_type in self.proto_analyzer.message_types:
            if lbl in msg_type:
                return msg_type
        return None

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
        filename = FileOperator.get_save_file_name("{0}.proto".format(text), parent=self, caption="Save protocol")

        if not filename:
            return

        self.proto_analyzer.to_xml_file(filename=filename, decoders=self.decodings, participants=self.project_manager.participants, write_bits=True)

    def handle_writeable_changed(self, writeable_status: bool):
        self.protocol_model.is_writeable = writeable_status
        self.proto_tree_model.set_copy_mode(writeable_status)
        self.refresh()

    def handle_label_removed(self, plabel: ProtocolLabel):
        if not plabel.show:
            self.show_all_cols()
            for lbl in self.proto_analyzer.protocol_labels:
                self.set_protocol_label_visibility(lbl)

            self.ui.tblViewProtocol.resize_columns()

        self.protocol_model.update()
        self.protocol_label_list_model.update()
        self.label_value_model.update()

    def handle_label_selection_changed(self):
        rows = [index.row() for index in self.ui.listViewLabelNames.selectedIndexes()]
        if len(rows) == 0:
            return

        maxrow = numpy.max(rows)

        label = self.protocol_label_list_model.proto_labels[maxrow]
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

    def handle_show_only_checkbox_changed(self):
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
        if not self.ui.cbShowDiffs.isChecked():
            self.ui.cbShowDiffs.setChecked(True)

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
                start, end = self.proto_analyzer.messages[0].get_label_range(lbl, self.ui.cbProtoView.currentIndex(), True)
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

    def add_protocol_label(self, start: int, end: int, messagenr: int, proto_view: int, edit_label_name=True):
        # Ensure atleast one Group is active
        start, end = self.proto_analyzer.convert_range(start, end, proto_view, 0, decoded=True, message_indx=messagenr)
        proto_label = self.proto_analyzer.messages[messagenr].message_type.add_protocol_label(start=start, end=end)

        self.protocol_label_list_model.update()
        self.protocol_model.update()

        if edit_label_name:
            try:
                index = self.protocol_label_list_model.proto_labels.index(proto_label)
                self.ui.listViewLabelNames.edit(self.protocol_label_list_model.createIndex(index, 0))
            except ValueError:
                pass

        self.label_value_model.update()

        return True

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
            self.on_participant_edited()
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
            self.on_message_type_dialog_finished()
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

        self.fill_message_type_combobox() # in case message types were added by logic analyzer

    def show_proto_sniff_dialog(self):
        pm = self.project_manager
        signal = None
        for proto in self.protocol_list:
            signal = proto.signal
            if signal:
                break

        if signal:
            bit_len = signal.bit_len
            mod_type = signal.modulation_type
            tolerance = signal.tolerance
            noise = signal.noise_treshold
            center = signal.qad_center
        else:
            bit_len = 100
            mod_type = 1
            tolerance = 5
            noise = 0.001
            center = 0.02

        psd = ProtocolSniffDialogController(pm.frequency, pm.sample_rate,
                                            pm.bandwidth, pm.gain,
                                            pm.device, noise, center,
                                            bit_len, tolerance, mod_type,
                                            parent=self)
        psd.protocol_accepted.connect(self.add_sniffed_protocol_messages)
        psd.show()


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

    def on_project_updated(self):
        self.participant_list_model.participants = self.project_manager.participants
        self.participant_list_model.update()
        self.protocol_model.participants = self.project_manager.participants
        self.protocol_model.refresh_vertical_header()
        self.active_message_type = self.proto_analyzer.default_message_type

    def set_search_ui_visibility(self, visible: bool):
        self.ui.btnPrevSearch.setVisible(visible)
        self.ui.lSearchCurrent.setVisible(visible)
        self.ui.lSlash.setVisible(visible)
        self.ui.lSearchTotal.setVisible(visible)
        self.ui.btnNextSearch.setVisible(visible)

    def __set_mode_to_search(self):
        self.ui.lFilterShown.hide()
        self.ui.btnSearchSelectFilter.setText("Search")
        self.set_search_ui_visibility(True)
        self.ui.btnSearchSelectFilter.clicked.disconnect()
        self.ui.btnSearchSelectFilter.clicked.connect(self.search)

    def __set_mode_to_select_all(self):
        self.ui.lFilterShown.hide()
        self.ui.btnSearchSelectFilter.setText("Select all")
        self.set_search_ui_visibility(False)
        self.ui.btnSearchSelectFilter.clicked.disconnect()
        self.ui.btnSearchSelectFilter.clicked.connect(self.select_all_search_results)

    def __set_mode_to_filter(self):
        if len(self.protocol_model.hidden_rows) == 0:
            self.ui.lFilterShown.setText("")
        else:
            nhidden = len(self.protocol_model.hidden_rows)
            rc = self.protocol_model.row_count
            self.ui.lFilterShown.setText("shown: {}/{}".format(rc-nhidden, rc))

        self.ui.lFilterShown.show()
        self.ui.btnSearchSelectFilter.setText("Filter")
        self.set_search_ui_visibility(False)
        self.ui.btnSearchSelectFilter.clicked.disconnect()
        self.ui.btnSearchSelectFilter.clicked.connect(self.filter_search_results)

    def on_cbmessagetype_index_changed(self):
        self.active_message_type = self.proto_analyzer.message_types[self.ui.cbMessagetypes.currentIndex()]

    def __set_default_message_type_ui_status(self):
        if self.active_message_type == self.proto_analyzer.default_message_type:
            self.ui.cbMessagetypes.setEditable(False)
            self.ui.btnRemoveMessagetype.hide()
            self.ui.btnMessagetypeSettings.hide()
        else:
            self.ui.cbMessagetypes.setEditable(True)
            self.ui.btnRemoveMessagetype.show()
            self.ui.btnMessagetypeSettings.show()

    def on_messagetype_name_edited(self, edited_str):
        if self.active_message_type == self.proto_analyzer.message_types[self.ui.cbMessagetypes.currentIndex()]:
            self.active_message_type.name = edited_str
            self.ui.cbMessagetypes.setItemText(self.ui.cbMessagetypes.currentIndex(), edited_str)

    def on_new_message_type_clicked(self, selected_messages: list = None):
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

    def on_message_type_selected(self, message_type: MessageType, selected_messages):
        for msg in selected_messages:
            msg.message_type = message_type
        self.active_message_type  = message_type
        self.protocol_model.update()

    def on_remove_message_type_clicked(self):
        for msg in self.proto_analyzer.messages:
            if msg.message_type == self.active_message_type:
                msg.message_type = self.proto_analyzer.default_message_type
        self.proto_analyzer.message_types.remove(self.active_message_type)
        self.fill_message_type_combobox()
        self.protocol_model.update()
        self.active_message_type = self.proto_analyzer.default_message_type

    def on_btn_messagetype_settings_clicked(self):
        dialog = MessageTypeDialogController(self.active_message_type, parent=self)
        dialog.show()
        dialog.finished.connect(self.on_message_type_dialog_finished)

    def on_message_type_dialog_finished(self):
        self.proto_analyzer.update_auto_message_types()
        self.protocol_model.update()

    def on_participant_edited(self):
        self.protocol_model.refresh_vertical_header()
        self.ui.tblViewProtocol.resize_vertical_header()
        self.participant_changed.emit()

    def set_participant_visibility(self):
        for i, msg in enumerate(self.proto_analyzer.messages):
            hide = not msg.participant.show if msg.participant is not None else not self.participant_list_model.show_unassigned
            self.ui.tblViewProtocol.setRowHidden(i, hide)

        self.set_shown_protocols()

    def on_label_name_edited(self, protolabel: ProtocolLabel, message_type: MessageType):
        # Check if label with the same name is already in another message type.
        # If yes, copy the attributes of this label to the edited one
        other_label = None
        for msg_type in self.proto_analyzer.message_types:
            if msg_type == message_type:
                continue
            other_label = next((p for p in msg_type if p.name == protolabel.name), None)
            if other_label:
                break
        if other_label:
            protolabel.color_index = other_label.color_index
            protolabel.display_type_index = other_label.display_type_index
            self.protocol_model.update()
            self.label_value_model.update()