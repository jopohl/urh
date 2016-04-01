from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QColor

from urh import constants
from urh.models.ProtocolTreeItem import ProtocolTreeItem
from urh.models.TableModel import TableModel
from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer
from urh.ui.actions.Clear import Clear
from urh.ui.actions.DeleteBitsAndPauses import DeleteBitsAndPauses
from urh.ui.actions.InsertBitsAndPauses import InsertBitsAndPauses
from urh.ui.actions.InsertColumn import InsertColumn


class GeneratorTableModel(TableModel):
    def __init__(self, tree_root_item: ProtocolTreeItem, modulators, decoders, parent = None):
        super().__init__(parent)
        self.protocol = ProtocolAnalyzerContainer(modulators, decoders)
        self.tree_root_item = tree_root_item
        self.dropped_row = -1

        self.cfc = None
        self.is_writeable = True
        self.decode = False
        self.is_generator = True

    def refresh_bgcolors_and_tooltips(self):
        self.background_colors.clear()
        self.tooltips.clear()
        label_colors = constants.LABEL_COLORS

        for lbl in self.protocol.protocol_labels:
            bg_color = label_colors[lbl.color_index]
            for i in lbl.block_numbers:
                start, end = self.protocol.get_label_range(lbl, self.proto_view, self.decode)
                for j in range(start, end):
                    self.background_colors[i, j] = bg_color
                    self.tooltips[i, j] = lbl.name

    def refresh_fonts(self):
        self.bold_fonts.clear()
        self.text_colors.clear()
        pac = self.protocol
        for i, block in enumerate(pac.blocks):
            fc = [pac.convert_range(start, end, 0, self.proto_view, False) for start, end in block.fuzz_created]
            for f in fc:
                for j in range(f[0], f[1]):
                    self.bold_fonts[i, j] = True

        for lbl in pac.protocol_labels:
            if lbl.active_fuzzing:
                i = lbl.refblock
                for j in range(*pac.get_label_range(lbl, self.proto_view, False)):
                    self.bold_fonts[i, j] = True
                    self.text_colors[i, j] = QColor("orange")

    def delete_range(self, block_start: int, block_end: int, index_start: int, index_end: int):
        if block_start > block_end:
            block_start, block_end = block_end, block_start
        if index_start > index_end:
            index_start, index_end = index_end, index_start

        remove_action = DeleteBitsAndPauses(self.protocol, block_start, block_end, index_start,
                                            index_end, self.proto_view, False)
        ########## Zugehörige Pausen löschen
        self.undo_stack.push(remove_action)

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemIsEnabled

        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEditable

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def dropMimeData(self, mimedata, action, row, column, parentIndex):
        if action == Qt.IgnoreAction:
            return True

        data_str = str(mimedata.text())
        indexes = list(data_str.split("/")[:-1])

        group_nodes = []
        file_nodes = []
        for index in indexes:
            row, column, parent = map(int, index.split(","))
            if parent == -1:
                parent = self.tree_root_item
            else:
                parent = self.tree_root_item.child(parent)
            node = parent.child(row)
            if node.is_group:
                group_nodes.append(node)
            else:
                file_nodes.append(node)

        # Which Nodes to add?
        nodes_to_add = []
        """:type: list of ProtocolTreeItem """
        for group_node in group_nodes:
            nodes_to_add.extend(group_node.children)
        nodes_to_add.extend([file_node for file_node in file_nodes if file_node not in nodes_to_add])

        for node in reversed(nodes_to_add):
            undo_action = InsertBitsAndPauses(self.protocol, self.dropped_row, node.protocol)
            self.undo_stack.push(undo_action)

        return True

    def clear(self):
        clear_action = Clear(self.protocol)
        self.undo_stack.push(clear_action)

    def duplicate_row(self, row: int):
        self.protocol.duplicate_line(row)
        self.update()

    def get_selected_label_index(self, selected_col: int):
        for i, lbl in enumerate(self.protocol.protocol_labels):
            if selected_col in range(*self.protocol.get_label_range(lbl, self.proto_view, False)):
                return i

        return -1

    def insert_column(self, index: int):
        insert_action = InsertColumn(self.protocol, index)
        self.undo_stack.push(insert_action)
