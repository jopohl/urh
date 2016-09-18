from collections import defaultdict

from PyQt5.QtCore import pyqtSignal, QModelIndex, Qt

from urh import constants
from urh.models.TableModel import TableModel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.ui.actions.DeleteBitsAndPauses import DeleteBitsAndPauses


class ProtocolTableModel(TableModel):
    ref_index_changed = pyqtSignal(int)

    def __init__(self, proto_analyzer: ProtocolAnalyzer, participants, controller, parent=None):
        super().__init__(participants=participants, parent=parent)

        self.controller = controller
        """:type: urh.controller.CompareFrameController.CompareFrameController"""

        self.protocol = proto_analyzer
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

    def addProtoLabel(self, start, end, messagenr):
        self.controller.add_protocol_label(start=start, end=end, messagenr=messagenr, proto_view=self.proto_view)

    def refresh_fonts(self):
        self.bold_fonts.clear()
        self.text_colors.clear()
        for i in self._diffs.keys():
            for j in self._diffs[i]:
                self.bold_fonts[i, j] = True
                self.text_colors[i, j] = constants.DIFFERENCE_CELL_COLOR

        if self._refindex >= 0:
            for j in range(self.col_count):
                self.text_colors[self._refindex, j] = constants.SELECTED_ROW_COLOR

    def delete_range(self, min_row: int, max_row: int, start: int, end: int):
        if not self.is_writeable:
            return

        del_action = DeleteBitsAndPauses(proto_analyzer=self.protocol, start_message=min_row, end_message=max_row,
                                         start=start, end=end, view=self.proto_view, decoded=True,
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
