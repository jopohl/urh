import locale
import os

import numpy
import time
from PyQt5.QtCore import pyqtSlot, QTimer, Qt, pyqtSignal, QItemSelection, QItemSelectionModel, QLocale, QModelIndex
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QMessageBox, QFrame, QAbstractItemView, QUndoStack, QApplication, QMenu

from urh import constants
from urh.controller.LabelsetOptionsDialogController import LabelsetOptionsDialogController
from urh.controller.OptionsController import OptionsController
from urh.controller.ProtocolLabelController import ProtocolLabelController
from urh.controller.ProtocolSniffDialogController import ProtocolSniffDialogController
from urh.models.LabelValueTableModel import LabelValueTableModel
from urh.models.ParticipantListModel import ParticipantListModel
from urh.models.ProtocolLabelListModel import ProtocolLabelListModel
from urh.models.ProtocolTableModel import ProtocolTableModel
from urh.models.ProtocolTreeModel import ProtocolTreeModel
from urh.plugins.PluginManager import PluginManager
from urh.signalprocessing.LabelSet import LabelSet
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolBlock import ProtocolBlock
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

        self.__selected_labelset = self.proto_analyzer.default_labelset
        self.fill_labelset_combobox()


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
        self.assign_labelsets_action = self.analyze_menue.addAction("Assign labelsets")
        self.assign_labelsets_action.setCheckable(True)
        self.assign_labelsets_action.setChecked(True)
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

        self.__set_default_labelset_ui_status()

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
    def active_labelset(self):
        return self.__selected_labelset

    @active_labelset.setter
    def active_labelset(self, val):
        if val not in self.proto_analyzer.labelsets:
            logger.error("Labelset {} not in labelsets".format(val.name))
            return

        self.__selected_labelset = val

        self.ui.cbLabelsets.blockSignals(True)
        self.ui.cbLabelsets.setCurrentIndex(self.proto_analyzer.labelsets.index(val))
        self.__set_default_labelset_ui_status()
        self.protocol_label_list_model.update()
        self.ui.cbLabelsets.blockSignals(False)


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
    def selected_blocks(self):
        return self.ui.tblViewProtocol.selected_blocks

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
            for line in self.protocol_model.first_blocks:
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
        self.ui.tblViewProtocol.labelset_selected.connect(self.on_labelset_selected)
        self.ui.tblViewProtocol.new_labelset_clicked.connect(self.on_new_labelset_clicked)
        self.ui.btnAddLabelset.clicked.connect(self.on_new_labelset_clicked)
        self.ui.btnRemoveLabelset.clicked.connect(self.on_remove_labelset_clicked)

        self.ui.lineEditSearch.returnPressed.connect(self.ui.btnSearchSelectFilter.click)

        self.ui.cbLabelsets.currentIndexChanged.connect(self.on_cblabelset_index_changed)
        self.ui.cbLabelsets.editTextChanged.connect(self.on_labelsetname_edited)

        self.search_action.triggered.connect(self.__set_mode_to_search)
        self.select_action.triggered.connect(self.__set_mode_to_select_all)
        self.filter_action.triggered.connect(self.__set_mode_to_filter)

        self.ui.btnLabelsetSettings.clicked.connect(self.on_btn_labelset_settings_clicked)



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

    def fill_labelset_combobox(self):
        self.ui.cbLabelsets.blockSignals(True)
        self.ui.cbLabelsets.clear()
        for labelset in self.proto_analyzer.labelsets:
            self.ui.cbLabelsets.addItem(labelset.name)
        self.ui.cbLabelsets.blockSignals(False)
        if self.ui.cbLabelsets.count() <= 1:
            self.ui.cbLabelsets.setEditable(False)

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

    def get_block_numbers_for_groups(self) -> dict:
        result = {}
        prev = 0
        for i in sorted(self.protocols.keys()):
            group_protos = self.protocols[i]
            num_blocks = prev
            for gp in group_protos:
                if gp.show:
                    num_blocks += gp.num_blocks
            result[i] = (prev, num_blocks)
            prev = num_blocks
        return result

    def get_blocks_of_active_groups(self):
        bnfg = self.get_block_numbers_for_groups()
        result = [self.proto_analyzer.blocks[r] for i, rng in bnfg.items() for r in range(*rng) if i in
                  self.active_group_ids]

        for i, rng in bnfg.items():
            if i in self.active_group_ids:
                result.extend(self.proto_analyzer.blocks[rng[0]:rng[1]])

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
        for labelset in pa.labelsets:
            if labelset not in self.proto_analyzer.labelsets:
                self.proto_analyzer.labelsets.append(labelset)

        self.fill_labelset_combobox()
        self.add_protocol(protocol=pa)

        self.set_shown_protocols()
        return pa

    def add_sniffed_protocol_blocks(self, blocks: list):
        if len(blocks) > 0:
            proto_analyzer = ProtocolAnalyzer(None)
            proto_analyzer.blocks = blocks
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
        self.proto_analyzer.blocks[:] = []
        self.proto_analyzer.used_symbols.clear()
        self.rows_for_protocols.clear()
        line = 0
        first_block_indices = []
        prev_line = 0
        for proto in self.protocol_list:
            abs_time = 0
            rel_time = 0
            if proto.show and proto.blocks:
                num_blocks = 0
                for i, block in enumerate(proto.blocks):
                    if not block:
                        continue

                    try:
                        if i > 0:
                            rel_time = proto.blocks[i-1].get_duration(proto.signal.sample_rate)
                            abs_time += rel_time
                    except (IndexError, AttributeError):
                        pass  # No signal, loaded from protocol file

                    block.absolute_time = abs_time
                    block.relative_time = rel_time

                    num_blocks += 1
                    if block.labelset not in self.proto_analyzer.labelsets:
                        block.labelset = self.proto_analyzer.default_labelset
                    self.proto_analyzer.blocks.append(block)

                self.proto_analyzer.used_symbols |= proto.used_symbols

                line += num_blocks
                rows_for_cur_proto = list(range(prev_line, line))
                self.rows_for_protocols[proto] = rows_for_cur_proto[:]


                prev_line = line
                if line != 0:
                    first_block_indices.append(line)

        if not self.show_protocol_seperation:
            self.protocol_model.first_blocks[:] = []
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
            if self.ui.tblViewProtocol.isRowHidden(i) and i in first_block_indices:
                indx = first_block_indices.index(i)
                first_block_indices[indx] += 1
                if indx < len(first_block_indices) and first_block_indices[indx] >= first_block_indices[indx+1]:
                    del first_block_indices[indx]

        for line in first_block_indices:
            self.ui.tblViewProtocol.setRowHeight(line, constants.SEPARATION_ROW_HEIGHT)

        self.protocol_model.first_blocks = first_block_indices[:]
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

        block = self.proto_analyzer.blocks[endRow]
        startCol = block.convert_index(startCol, old_view, new_view, True)[0]
        endCol = block.convert_index(endCol, old_view, new_view, True)[1]

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
            if row in range(offset, offset + group.num_blocks):
                return group
            offset += group.num_blocks

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
            self.set_decoding(self.decodings[new_index], blocks=self.selected_blocks if self.selected_blocks else None)

    def set_decoding(self, decoding: encoding, blocks=None):
        """

        :param decoding:
        :param blocks: None = set for all blocks
        :return:
        """
        if decoding is None:
            self.show_decoding_clicked.emit()
        else:
            if blocks is None:
                blocks = self.proto_analyzer.blocks
                if len(blocks) > 10:
                    reply = QMessageBox.question(self, "Set decoding", "Do you want to apply the selected decoding to {} blocks?".format(len(blocks)), QMessageBox.Yes | QMessageBox.No);
                    if reply != QMessageBox.Yes:
                        self.ui.cbDecoding.blockSignals(True)
                        self.ui.cbDecoding.setCurrentText("...")
                        self.ui.cbDecoding.blockSignals(False)
                        return

            self.show_all_cols()


            for block in blocks:
                block.decoder = decoding

            self.clear_search()

            selected = self.ui.tblViewProtocol.selectionModel().selection()

            if not selected.isEmpty() and self.isVisible() and self.proto_analyzer.num_blocks > 0:
                max_row = numpy.max([rng.bottom() for rng in selected])
                max_row = max_row if max_row < len(self.proto_analyzer.blocks) else -1
                try:
                    block = self.proto_analyzer.blocks[max_row]
                except IndexError:
                    block = None
                self.__set_decoding_error_label(block)
            else:
                self.__set_decoding_error_label(None)

            self.protocol_model.update()
            self.protocol_label_list_model.update()
            self.label_value_model.update()

            for lbl in self.proto_analyzer.protocol_labels:
                self.set_protocol_label_visibility(lbl)

            self.ui.tblViewProtocol.resize_columns()


    def __set_decoding_error_label(self, block: ProtocolBlock):
        if block:
            errors = block.decoding_errors
            percent = 100 * (errors / len(block))
            if percent <= 100:
                self.ui.lDecodingErrorsValue.setText(
                    locale.format_string("%d (%.02f%%)", (errors, 100 * (errors / len(block)))))
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
            self.ui.lblLabelValues.setText(self.tr("Label values for block "))
            self.label_value_model.block_index = -1
            self.active_labelset = self.proto_analyzer.default_labelset
            return -1, -1

        min_row = numpy.min([rng.top() for rng in selected])
        max_row = numpy.max([rng.bottom() for rng in selected])
        start = numpy.min([rng.left() for rng in selected])
        end = numpy.max([rng.right() for rng in selected]) + 1

        selected_blocks = self.selected_blocks

        cur_view = self.ui.cbProtoView.currentIndex()
        self.ui.lNumSelectedColumns.setText(str(end - start))

        self.active_labelset = self.proto_analyzer.blocks[max_row].labelset

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
        block = self.proto_analyzer.blocks[max_row]

        self.ui.lBitsSelection.setText(bits)
        self.ui.lHexSelection.setText(hexs)
        self.__set_decoding_error_label(block)
        if len(decimals) > 0:
            self.ui.lDecimalSelection.setText("".join(decimals))
        else:
            self.ui.lDecimalSelection.setText("")

        self.ui.lblLabelValues.setText(self.tr("Label values for block #") + str(min_row + 1))
        if min_row != self.label_value_model.block_index:
            self.label_value_model.block_index = min_row

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

        self.ui.lblRSSI.setText(locale.format_string("%.2f", block.rssi))
        abs_time = Formatter.science_time(block.absolute_time)
        rel_time = Formatter.science_time(block.relative_time)
        self.ui.lTime.setText("{0} (+{1})".format(abs_time, rel_time))

        # Set Decoding Combobox
        self.ui.cbDecoding.blockSignals(True)
        different_encodings = False
        enc = block.decoder
        for block in selected_blocks:
            if block.decoder != enc:
                different_encodings = True
                break

        if not different_encodings:
            self.ui.cbDecoding.setCurrentText(block.decoder.name)
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
                i += proto.num_blocks
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
        for labelset in self.proto_analyzer.labelsets:
            labelset.clear()
        self.refresh()

    @pyqtSlot(int)
    def on_undo_stack_index_changed(self, index: int):
        self.protocol_model.update()
        self.protocol_label_list_model.update()

    @pyqtSlot(ProtocolLabel)
    def on_edit_label_clicked_in_table(self, proto_label: ProtocolLabel):

        labelset = self.get_labelset_for_label(proto_label)
        self.show_protocol_labels(labelset.index(proto_label))

    @pyqtSlot(int)
    def show_protocol_labels(self, preselected_index: int):
        view_type = self.ui.cbProtoView.currentIndex()
        block = next(block for block in self.proto_analyzer.blocks if self.active_labelset.id == block.labelset.id)
        label_controller = ProtocolLabelController(preselected_index=preselected_index, labelset=self.active_labelset,
                                                   max_end=numpy.max([len(block) for block in self.proto_analyzer.blocks]),
                                                   viewtype=view_type, block=block,
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

    @pyqtSlot(ProtocolLabel, LabelSet)
    def on_apply_decoding_changed(self, lbl: ProtocolLabel, labelset: LabelSet):
        for block in self.proto_analyzer.blocks:
            if block.labelset == labelset:
                block.clear_decoded_bits()
                block.clear_encoded_bits()

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

    def set_protocol_label_visibility(self, lbl: ProtocolLabel, block: ProtocolBlock = None):
        try:
            block = block if block else next(block for block in self.proto_analyzer.blocks if lbl in block.labelset)
            start, end = block.get_label_range(lbl, self.ui.cbProtoView.currentIndex(), True)

            for i in range(start, end):
                self.ui.tblViewProtocol.setColumnHidden(i, not lbl.show)
        except Exception as e:
            pass

    def get_labelset_for_label(self, lbl: ProtocolLabel) -> LabelSet:
        for lblset in self.proto_analyzer.labelsets:
            if lbl in lblset:
                return lblset
        return None

    def show_all_cols(self):
        for i in range(self.protocol_model.col_count):
            self.ui.tblViewProtocol.showColumn(i)

    def save_protocol(self):
        for block in self.proto_analyzer.blocks:
            if not block.decoder.is_nrz:
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

        block = next(block for block in self.proto_analyzer.blocks if label if block.labelset)
        start, end = block.get_label_range(label, self.protocol_model.proto_view, True)
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
        for block in self.proto_analyzer.blocks:
            for lbl in block.labelset:
                if lbl.show:
                    start, end = block.get_label_range(lbl=lbl, view=self.ui.cbProtoView.currentIndex(),
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
                start, end = self.proto_analyzer.get_label_range(lbl, self.ui.cbProtoView.currentIndex(),
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

    def add_protocol_label(self, start: int, end: int, blocknr: int,
                           proto_view: int, edit_label_name=True):
        # Ensure atleast one Group is active
        proto_label = self.active_labelset.add_protocol_label(start=start, end=end, type_index=proto_view)

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

        self.ui.progressBarLogicAnalyzer.setFormat("%p% (Assign labelsets by rules)")
        self.ui.progressBarLogicAnalyzer.setValue(50)

        if self.assign_labelsets_action.isChecked():
            t = time.time()
            self.on_labelset_dialog_finished()
            logger.debug("Time for auto assigning labelsets: " + str(time.time() - t))

        self.ui.progressBarLogicAnalyzer.setFormat("%p% (Find new labels/labelsets)")
        self.ui.progressBarLogicAnalyzer.setValue(75)

        if self.assign_labels_action.isChecked():
            t = time.time()
            self.proto_analyzer.auto_assign_labels()
            self.protocol_model.update()
            self.label_value_model.update()
            self.protocol_label_list_model.update()
            logger.debug("Time for auto assigning labels: " + str(time.time() - t))

        self.ui.progressBarLogicAnalyzer.setValue(100)
        self.unsetCursor()
        self.ui.stackedWidgetLogicAnalysis.setCurrentIndex(0)

        # available_analyze_plugins = self.plugin_manager.label_assign_plugins
        # if len(available_analyze_plugins) == 0:
        #     QMessageBox.critical(self, self.tr("No analyze plugins available"),
        #                          self.tr("Could not find any plugins for protocol analysis."))
        #     return
        #
        # active_analyze_plugins = [p for p in available_analyze_plugins if p.enabled]
        # if len(active_analyze_plugins) == 0:
        #     installed_plugins = self.plugin_manager.installed_plugins
        #     options_controller = OptionsController(installed_plugins, highlighted_plugins=available_analyze_plugins)
        #     options_controller.exec_()
        #     return
        #
        # self.setCursor(Qt.WaitCursor)
        # self.protocol_model.undo_stack.blockSignals(True)
        # for p in active_analyze_plugins:
        #     self.protocol_model.undo_stack.push(p.get_action(self.groups, self.proto_analyzer.default_labelset))
        # self.protocol_model.undo_stack.blockSignals(False)
        # self.protocol_model.update()
        # self.protocol_label_list_model.update()
        # self.unsetCursor()

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
        psd.protocol_accepted.connect(self.add_sniffed_protocol_blocks)
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
            block = self.proto_analyzer.blocks[i]
            for label in block.labelset:
                lbl_start, lbl_end = block.get_label_range(lbl=label, view=view, decode=True)
                if any(j in range(lbl_start, lbl_end) for j in range(col_start, col_end)) and not label in result:
                    result.append(label)

        return result

    def on_project_updated(self):
        self.participant_list_model.participants = self.project_manager.participants
        self.participant_list_model.update()
        self.protocol_model.participants = self.project_manager.participants
        self.protocol_model.refresh_vertical_header()
        self.active_labelset = self.proto_analyzer.default_labelset

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

    def on_cblabelset_index_changed(self):
        self.active_labelset = self.proto_analyzer.labelsets[self.ui.cbLabelsets.currentIndex()]

    def __set_default_labelset_ui_status(self):
        if self.active_labelset == self.proto_analyzer.default_labelset:
            self.ui.cbLabelsets.setEditable(False)
            self.ui.btnRemoveLabelset.hide()
            self.ui.btnLabelsetSettings.hide()
        else:
            self.ui.cbLabelsets.setEditable(True)
            self.ui.btnRemoveLabelset.show()
            self.ui.btnLabelsetSettings.show()

    def on_labelsetname_edited(self, edited_str):
        if self.active_labelset == self.proto_analyzer.labelsets[self.ui.cbLabelsets.currentIndex()]:
            self.active_labelset.name = edited_str
            self.ui.cbLabelsets.setItemText(self.ui.cbLabelsets.currentIndex(), edited_str)

    def on_new_labelset_clicked(self, selected_blocks: list = None):
        selected_blocks = selected_blocks if isinstance(selected_blocks, list) else []
        self.proto_analyzer.add_new_labelset(labels=self.proto_analyzer.default_labelset)
        self.fill_labelset_combobox()
        self.ui.cbLabelsets.setEditable(True)
        self.active_labelset = self.proto_analyzer.labelsets[-1]
        for block in selected_blocks:
            block.labelset = self.active_labelset
        self.ui.cbLabelsets.setFocus()
        self.ui.btnRemoveLabelset.show()
        self.protocol_model.update()

    def on_labelset_selected(self, labelset: LabelSet, selected_blocks):
        for block in selected_blocks:
            block.labelset = labelset
        self.active_labelset  = labelset
        self.protocol_model.update()

    def on_remove_labelset_clicked(self):
        for block in self.proto_analyzer.blocks:
            if block.labelset == self.active_labelset:
                block.labelset = self.proto_analyzer.default_labelset
        self.proto_analyzer.labelsets.remove(self.active_labelset)
        self.fill_labelset_combobox()
        self.protocol_model.update()
        self.active_labelset = self.proto_analyzer.default_labelset

    def on_btn_labelset_settings_clicked(self):
        dialog = LabelsetOptionsDialogController(self.active_labelset, parent=self)
        dialog.show()
        dialog.finished.connect(self.on_labelset_dialog_finished)

    def on_labelset_dialog_finished(self):
        self.proto_analyzer.update_auto_labelsets()
        self.protocol_model.update()

    def on_participant_edited(self):
        self.protocol_model.refresh_vertical_header()
        self.ui.tblViewProtocol.resize_vertical_header()
        self.participant_changed.emit()

    def set_participant_visibility(self):
        for i, block in enumerate(self.proto_analyzer.blocks):
            hide = not block.participant.show if block.participant is not None else not self.participant_list_model.show_unassigned
            self.ui.tblViewProtocol.setRowHidden(i, hide)

        self.ui.tblViewProtocol.hide_row() # Update data structures and call triggers after hiding rows