import locale
import os

import numpy
from PyQt5.QtCore import pyqtSlot, QTimer, Qt, pyqtSignal, QItemSelection, QItemSelectionModel, QLocale, QModelIndex
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QMessageBox, QFrame, QAbstractItemView, QUndoStack, QApplication, QMenu

from urh import constants
from urh.controller.OptionsController import OptionsController
from urh.controller.ProtocolLabelController import ProtocolLabelController
from urh.controller.ProtocolSniffDialogController import ProtocolSniffDialogController
from urh.models.LabelValueTableModel import LabelValueTableModel
from urh.models.ParticipantListModel import ParticipantListModel
from urh.models.ProtocolLabelListModel import ProtocolLabelListModel
from urh.models.ProtocolTableModel import ProtocolTableModel
from urh.models.ProtocolTreeModel import ProtocolTreeModel
from urh.plugins.PluginManager import PluginManager
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolBlock import ProtocolBlock
from urh.signalprocessing.encoding import encoding
from urh.signalprocessing.ProtocolGroup import ProtocolGroup
from urh.ui.ui_analysis_frame import Ui_FAnalysis
from urh.util import FileOperator
from urh.util.Errors import Errors
from urh.util.Formatter import Formatter
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

        self.participant_list_model = ParticipantListModel(project_manager.participants)
        self.ui.listViewParticipants.setModel(self.participant_list_model)

        self.__active_group_ids = [0]
        self.selected_protocols = set()

        self.searchselectsearch_menu = QMenu()
        self.search_action = self.searchselectsearch_menu.addAction("Search")
        self.select_action = self.searchselectsearch_menu.addAction("Select all")
        self.filter_action = self.searchselectsearch_menu.addAction("Filter")
        self.ui.btnSearchSelectFilter.setMenu(self.searchselectsearch_menu)

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
        self.ui.lSignalName.setText(self.tr("Compare your protocols here"))
        self.ui.lSignalNr.setText("")
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
        self.proto_tree_model.labels_on_group_dropped.connect(self.add_labels_to_group)
        self.ui.treeViewProtocols.selection_changed.connect(self.handle_tree_view_selection_changed)
        self.proto_tree_model.group_deleted.connect(self.handle_group_deleted)
        self.proto_tree_model.proto_to_group_added.connect(self.expand_group_node)
        self.proto_tree_model.group_added.connect(self.handle_group_added)




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
        self.participant_list_model.show_state_changed.connect(self.set_shown_protocols)
        self.ui.tblViewProtocol.participant_changed.connect(self.ui.tblViewProtocol.resize_vertical_header)
        self.ui.tblViewProtocol.participant_changed.connect(self.participant_changed.emit)

        self.search_action.triggered.connect(self.__set_mode_to_search)
        self.select_action.triggered.connect(self.__set_mode_to_select_all)
        self.filter_action.triggered.connect(self.__set_mode_to_filter)

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
        group =self.proto_tree_model.add_protocol(protocol, group_id)
        protocol.set_decoder_for_blocks(group.decoding)
        protocol.qt_signals.protocol_updated.connect(self.set_shown_protocols)
        if protocol.signal:
            protocol.signal.sample_rate_changed.connect(self.set_shown_protocols)  # Refresh times
        protocol.qt_signals.show_state_changed.connect(self.set_shown_protocols)
        for i in range(self.proto_tree_model.ngroups):
            self.expand_group_node(i)
        return protocol

    def add_protocol_from_file(self, filename: str):
        """

        :rtype: list of ProtocolAnalyzer
        """
        try:
            view, groups, symbols = ProtocolAnalyzer.from_file(filename)
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error while loading protocol file"), e.args[0])
            return None

        protolist = []
        for i, group_data in enumerate(groups):
            name = group_data["name"]
            self.proto_tree_model.addGroup(name)
            group = self.proto_tree_model.groups[-1]
            try:
                group.decoding = self.decodings[group_data["decoding_index"]]
                group.loaded_from_file = True
            except IndexError:
                pass
            pa = ProtocolAnalyzer(None)
            pa.used_symbols = symbols
            pa.name = "Protocol " + str(i)
            pa.filename = filename
            pa.blocks = group_data["blocks"]
            self.add_protocol(pa, group_id=self.proto_tree_model.ngroups - 1)
            protolist.append(pa)

            for lbl in group_data["labels"]:
                group.add_label(lbl, refresh=False)

        if protolist:
            self.ui.cbDecoding.blockSignals(True)
            try:
                self.ui.cbDecoding.setCurrentIndex(groups[0]["decoding_index"])
            except IndexError:
                pass
            self.ui.cbDecoding.blockSignals(False)

        self.set_shown_protocols()
        self.ui.cbProtoView.setCurrentIndex(view)

        return protolist

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
            if proto.show:
                num_blocks = 0
                for i, block in enumerate(proto.blocks):
                    if not block:
                        continue
                    if block.participant is None and not self.participant_list_model.show_unassigned:
                        continue
                    if block.participant is not None and not block.participant.show:
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
                    self.proto_analyzer.blocks.append(block)

                self.proto_analyzer.used_symbols |= proto.used_symbols

                line += num_blocks
                rows_for_cur_proto = list(range(prev_line, line))
                self.rows_for_protocols[proto] = rows_for_cur_proto[:]


                prev_line = line
                if line != 0:
                    first_block_indices.append(line)

        for group in self.groups:
            if not group.loaded_from_file:
                group.refresh_labels()

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

        for group in self.groups:
            for lbl in group.labels:
                self.set_protocol_label_visibility(lbl, group)

        self.handle_show_only_checkbox_changed()

        self.restore_selection(old_view, sel_cols, sel_rows)

    def restore_selection(self, old_view: int, sel_cols, sel_rows):
        if len(sel_cols) == 0 or len(sel_rows) == 0:
            return

        startCol, endCol = numpy.min(sel_cols), numpy.max(sel_cols)
        startRow, endRow = numpy.min(sel_rows), numpy.max(sel_rows)
        new_view = self.ui.cbProtoView.currentIndex()

        group = self.get_group_for_row(startRow)
        startCol = group.convert_index(startCol, old_view, new_view, True)[0]
        endCol = group.convert_index(endCol, old_view, new_view, True)[1]

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
            self.set_decoding(self.decodings[new_index], for_all_blocks=False)

    def set_decoding(self, decoding: encoding, for_all_blocks=True):
        if decoding is None:
            self.show_decoding_clicked.emit()
        else:
            self.show_all_cols()

            if for_all_blocks:
                for group in self.groups:
                    group.decoding = decoding

            else:
                for i in self.active_group_ids:
                    self.groups[i].decoding = decoding

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

            for group in self.groups:
                for lbl in group.labels:
                    self.set_protocol_label_visibility(lbl, group)

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
            return -1, -1

        min_row = numpy.min([rng.top() for rng in selected])
        max_row = numpy.max([rng.bottom() for rng in selected])
        start = numpy.min([rng.left() for rng in selected])
        end = numpy.max([rng.right() for rng in selected]) + 1

        self.protocol_label_list_model.selected_labels = self.get_labels_from_selection(min_row, max_row,
                                                                                        start, end - 1)

        cur_view = self.ui.cbProtoView.currentIndex()
        self.ui.lNumSelectedColumns.setText(str(end - start))

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

        block = self.proto_analyzer.blocks[min_row]
        self.ui.lblRSSI.setText(locale.format_string("%.2f", block.rssi))
        abs_time = Formatter.science_time(block.absolute_time)
        rel_time = Formatter.science_time(block.relative_time)
        self.ui.lTime.setText("{0} (+{1})".format(abs_time, rel_time))

        # Set Decoding Combobox
        self.ui.cbDecoding.blockSignals(True)
        group = self.get_group_for_row(min_row)
        if group:
            self.ui.cbDecoding.setCurrentText(group.decoding.name)
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

    def add_labels_to_group(self, label_ids, group_id: int):
        labels = [self.protocol_label_list_model.proto_labels[i] for i in label_ids]
        group = self.groups[group_id]
        for label in labels:
            ol = group.find_overlapping_labels(label.start, label.end, 0)
            if len(ol) > 0:
                reply = QMessageBox.question(self, self.tr("Overlapping Label"),
                                             self.tr(
                                                 "Adding label {0} to group {1} would overlap with existing label(s) {2}.\n\n"
                                                 "Do you want to split the existing labels in order to add {0}?\n"
                                                 "If you choose 'no' the label will not be added to group.\n\n"
                                                 "Note, only partial overlapped labels will be splitted."
                                                 "Fully overlapped labels will be removed.".
                                                 format(label.name, group.name,
                                                        ",".join([lbl.name for lbl in ol]))),
                                             QMessageBox.Yes | QMessageBox.No)

                if reply == QMessageBox.Yes:
                    group.split_for_new_label(label)
                    group.add_protocol_label(start=label.start, end=label.end-1,
                                             type_index=0,
                                             name=label.name, color_ind=label.color_index)
                else:
                    continue
            else:
                if group.num_protocols > 0:
                    group.add_protocol_label(start=label.start, end=label.end-1, type_index=0,
                             name=label.name, color_ind=label.color_index)
                else:
                    Errors.empty_group()


        self.refresh()

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

        if show_decoding:
            self.ui.cbDecoding.blockSignals(True)
            self.ui.cbDecoding.setCurrentText(self.groups[self.active_group_ids[0]].decoding.name)
            self.ui.cbDecoding.blockSignals(False)

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
        for group in self.groups:
            group.labels[:] = []
        for block in self.proto_analyzer.blocks:
            block.exclude_from_decoding_labels[:] = []
        self.refresh()

    def refresh_protocol_labels(self):
        for group in self.groups:
            group.refresh_labels()

    @pyqtSlot(int)
    def on_undo_stack_index_changed(self, index: int):
        self.refresh_protocol_labels()
        self.protocol_model.update()
        self.protocol_label_list_model.update()

    @pyqtSlot(ProtocolLabel)
    def on_edit_label_clicked_in_table(self, proto_label: ProtocolLabel):
        group = self.get_group_for_label(proto_label)
        self.show_protocol_labels(group.labels.index(proto_label))

    @pyqtSlot(int)
    def show_protocol_labels(self, preselected_index: int):
        view_type = self.ui.cbProtoView.currentIndex()
        active_group = self.active_groups[0] if self.active_groups else self.groups[0]
        offset = sum(self.groups[i].num_blocks for i in range(0, self.groups.index(active_group)))
        label_controller = ProtocolLabelController(preselected_index, active_group, offset,
                                                   viewtype=view_type,
                                                   parent=self)
        label_controller.exec_()

        self.protocol_label_list_model.update()
        self.label_value_model.update()
        self.show_all_cols()
        for group in self.groups:
            for lbl in group.labels:
                self.set_protocol_label_visibility(lbl, group)
        self.handle_show_only_checkbox_changed()
        self.protocol_model.update()
        self.ui.tblViewProtocol.resize_columns()

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
        self.search()
        self.ui.tblLabelValues.clearSelection()

        matching_rows = set(search_result[0] for search_result in self.protocol_model.search_results)
        self.ui.tblViewProtocol.blockSignals(True)
        for i in set(range(0, self.protocol_model.row_count)) - matching_rows:
            self.ui.tblViewProtocol.hide_row(row=i)
        self.ui.tblViewProtocol.blockSignals(False)
        self.ui.tblViewProtocol.row_visibilty_changed.emit()

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

    def set_protocol_label_visibility(self, lbl: ProtocolLabel, group: ProtocolGroup = None):
        group = self.get_group_for_label(lbl) if not group else group
        start, end = group.get_label_range(lbl, self.ui.cbProtoView.currentIndex(), True)

        for i in range(start, end):
            self.ui.tblViewProtocol.setColumnHidden(i, not lbl.show)

    def get_group_for_label(self, lbl: ProtocolLabel) -> ProtocolGroup:
        for group in self.groups:
            if lbl in group.labels:
                return group
        return None

    def show_all_cols(self):
        for i in range(self.protocol_model.col_count):
            self.ui.tblViewProtocol.showColumn(i)

    def save_protocol(self):
        viewtype = self.ui.cbProtoView.currentIndex()

        for group in self.groups:
            if not group.decoding.is_nrz:
                reply = QMessageBox.question(self, "Saving of protocol",
                                             "You want to save this protocol with an encoding different from NRZ.\n"
                                             "This may cause loss of information if you load it again.\n\n"
                                             "Save anyway?", QMessageBox.Yes | QMessageBox.No)
                if reply != QMessageBox.Yes:
                    return
                else:
                    break

        text = "protocol"
        filename = FileOperator.get_save_file_name("{0}.txt".format(text), parent=self, caption="Save protocol")

        if not filename:
            return


        FileOperator.save_protocol(filename, viewtype, self.groups, list(map(str, self.decodings)),
                                   self.proto_analyzer.used_symbols)

    def handle_writeable_changed(self, writeable_status: bool):
        self.protocol_model.is_writeable = writeable_status
        self.proto_tree_model.set_copy_mode(writeable_status)
        self.refresh()

    def handle_label_removed(self, plabel: ProtocolLabel):
        if not plabel.show:
            self.show_all_cols()
            for group in self.groups:
                for lbl in group.labels:
                    self.set_protocol_label_visibility(lbl, group)

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

        group = self.get_group_for_label(label)
        start, end = group.get_label_range(label, self.protocol_model.proto_view, True)
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
        for group in self.groups:
            for lbl in group.labels:
                if lbl.show:
                    start, end = group.get_label_range(lbl, self.ui.cbProtoView.currentIndex(),
                                                       True)
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
        for group in self.groups:
            for lbl in group.labels:
                if lbl.show:
                    start, end = group.get_label_range(lbl, self.ui.cbProtoView.currentIndex(),
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

        for group in self.groups:
            for lbl in group.labels:
                self.set_protocol_label_visibility(lbl, group)

        if not selected.isEmpty():
            min_row = numpy.min([rng.top() for rng in selected])
            start = numpy.min([rng.left() for rng in selected])
            self.ui.tblViewProtocol.scrollTo(self.protocol_model.index(min_row, start))

    def add_protocol_label(self, start: int, end: int, blocknr: int,
                           proto_view: int, edit_label_name=True):
        # Ensure atleast one Group is active
        active_group_id = self.active_group_ids[0] if self.active_group_ids else 0
        group = self.proto_tree_model.group_at(active_group_id)

        overlapping_labels = group.find_overlapping_labels(start, end, proto_view)
        if len(overlapping_labels) > 0:
            reply = QMessageBox.question(self, self.tr("Overlapping Label"),
                                         self.tr("This label would overlap with existing label(s) {0}.\n\n"
                                                 "Do you want to split the existing labels in order to create the new one?\n"
                                                 "If you choose 'no' label creation will be cancelled.\n\n"
                                                 "Note, only partial overlapped labels will be splitted."
                                                 "Fully overlapped labels will be removed.".
                                                 format(",".join([lbl.name for lbl in overlapping_labels]))),
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                group.split_labels(start, end, proto_view)
            else:
                return False

        proto_label = group.add_protocol_label(start=start, end=end, type_index=proto_view)

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
        available_analyze_plugins = self.plugin_manager.label_assign_plugins
        if len(available_analyze_plugins) == 0:
            QMessageBox.critical(self, self.tr("No analyze plugins available"),
                                 self.tr("Could not find any plugins for protocol analysis."))
            return

        active_analyze_plugins = [p for p in available_analyze_plugins if p.enabled]
        if len(active_analyze_plugins) == 0:
            installed_plugins = self.plugin_manager.installed_plugins
            options_controller = OptionsController(installed_plugins, highlighted_plugins=available_analyze_plugins)
            options_controller.exec_()
            return

        self.setCursor(Qt.WaitCursor)
        self.protocol_model.undo_stack.blockSignals(True)
        for p in active_analyze_plugins:
            self.protocol_model.undo_stack.push(p.get_action(self.groups))
        self.protocol_model.undo_stack.blockSignals(False)
        self.protocol_model.update()
        self.protocol_label_list_model.update()
        self.unsetCursor()

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
        offset = 0
        result = []
        for group in self.groups:
            for lbl in group.labels:
                lbl_start, lbl_end = group.get_label_range(lbl, view, True)
                if any(i-offset in lbl.block_numbers for i in range(row_start, row_end)) and\
                    any(j in range(lbl_start, lbl_end) for j in range(col_start, col_end)):
                    result.append(lbl)

            offset += group.num_blocks

        return result

    def on_project_updated(self):
        self.participant_list_model.participants = self.project_manager.participants
        self.participant_list_model.update()
        self.protocol_model.participants = self.project_manager.participants

    def set_search_ui_visibility(self, visible: bool):
        self.ui.btnPrevSearch.setVisible(visible)
        self.ui.lSearchCurrent.setVisible(visible)
        self.ui.lSlash.setVisible(visible)
        self.ui.lSearchTotal.setVisible(visible)
        self.ui.btnNextSearch.setVisible(visible)

    def __set_mode_to_search(self):
        self.ui.btnSearchSelectFilter.setText("Search")
        self.set_search_ui_visibility(True)
        self.ui.btnSearchSelectFilter.clicked.disconnect()
        self.ui.btnSearchSelectFilter.clicked.connect(self.search)

    def __set_mode_to_select_all(self):
        self.ui.btnSearchSelectFilter.setText("Select all")
        self.set_search_ui_visibility(False)
        self.ui.btnSearchSelectFilter.clicked.disconnect()
        self.ui.btnSearchSelectFilter.clicked.connect(self.select_all_search_results)

    def __set_mode_to_filter(self):
        self.ui.btnSearchSelectFilter.setText("Filter")
        self.set_search_ui_visibility(False)
        self.ui.btnSearchSelectFilter.clicked.disconnect()
        self.ui.btnSearchSelectFilter.clicked.connect(self.filter_search_results)