from collections import defaultdict

from PyQt5.QtCore import pyqtSignal, QModelIndex, Qt
from PyQt5.QtGui import QColor

from urh import constants
from urh.models.TableModel import TableModel
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.ui.actions.DeleteBitsAndPauses import DeleteBitsAndPauses


class ProtocolTableModel(TableModel):
    ref_index_changed = pyqtSignal(int)

    def __init__(self, proto_analyzer: ProtocolAnalyzer, participants, controller, parent=None):
        super().__init__(parent)

        self.controller = controller
        self.protocol = proto_analyzer
        self.participants = participants

        self.active_group_ids = [0]

    @property
    def diff_columns(self) -> defaultdict(set):
        return self._diffs

    @property
    def refindex(self):
        return self._refindex

    @refindex.setter
    def refindex(self, refindex):
        if refindex != self._refindex:
            self._refindex = refindex
            self.update()
            self.ref_index_changed.emit(self._refindex)

    def addProtoLabel(self, start, end, blocknr):
        self.controller.add_protocol_label(start, end, blocknr, self.proto_view)

    def refresh_fonts(self):
        self.bold_fonts.clear()
        self.text_colors.clear()
        for i in self._diffs.keys():
            for j in self._diffs[i]:
                self.bold_fonts[i, j] = True
                self.text_colors[i, j] = constants.DIFFERENCE_CELL_COLOR

        if self.proto_view == 0:
            for j in self.protocol.bit_alignment_positions:
                for i in range(self.row_count):
                    self.bold_fonts[i, j] = True

        if self._refindex >= 0:
            for j in range(self.col_count):
                self.text_colors[self._refindex, j] = constants.SELECTED_ROW_COLOR

    def delete_range(self, min_row: int, max_row: int, start: int, end: int):
        if not self.is_writeable:
            return

        del_action = DeleteBitsAndPauses(self.protocol, min_row, max_row,
                                         start, end, self.proto_view, True,
                                         self.controller.get_block_numbers_for_groups(),
                                         subprotos=self.controller.protocol_list)
        self.undo_stack.push(del_action)

    def flags(self, index: QModelIndex):
        if index.isValid():
            if self.is_writeable:
                return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable
            else:
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.NoItemFlags
