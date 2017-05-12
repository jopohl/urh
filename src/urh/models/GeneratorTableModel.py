from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QColor

from urh import constants
from urh.models.ProtocolTreeItem import ProtocolTreeItem
from urh.models.TableModel import TableModel
from urh.signalprocessing.Message import Message
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer
from urh.signalprocessing.encoder import Encoder
from urh.ui.actions.Clear import Clear
from urh.ui.actions.DeleteBitsAndPauses import DeleteBitsAndPauses
from urh.ui.actions.InsertBitsAndPauses import InsertBitsAndPauses
from urh.ui.actions.InsertColumn import InsertColumn
from urh.util.Logger import logger


class GeneratorTableModel(TableModel):
    def __init__(self, tree_root_item: ProtocolTreeItem, modulators, decodings, parent = None):
        super().__init__(participants=[], parent=parent)
        self.protocol = ProtocolAnalyzerContainer(modulators)
        self.tree_root_item = tree_root_item
        self.dropped_row = -1

        self.decodings = decodings  # type: list[Encoder]

        self.cfc = None
        self.is_writeable = True
        self.decode = False
        self.is_generator = True

    def refresh_fonts(self):
        self.bold_fonts.clear()
        self.text_colors.clear()
        pac = self.protocol
        assert isinstance(pac, ProtocolAnalyzerContainer)
        for i, message in enumerate(pac.messages):
            if message.fuzz_created:
                for lbl in (lbl for lbl in message.message_type if lbl.fuzz_created):
                    for j in range(*message.get_label_range(lbl=lbl, view=self.proto_view, decode=False)):
                        self.bold_fonts[i, j] = True

            for lbl in message.active_fuzzing_labels:
                for j in range(*message.get_label_range(lbl=lbl, view=self.proto_view, decode=False)):
                    self.bold_fonts[i, j] = True
                    self.text_colors[i, j] = QColor("orange")

    def delete_range(self, msg_start: int, msg_end: int, index_start: int, index_end: int):
        if msg_start > msg_end:
            msg_start, msg_end = msg_end, msg_start
        if index_start > index_end:
            index_start, index_end = index_end, index_start

        remove_action = DeleteBitsAndPauses(self.protocol, msg_start, msg_end, index_start,
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
            try:
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
            except ValueError:
                continue

        # Which Nodes to add?
        nodes_to_add = []  # type: list[ProtocolTreeItem]

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

    def add_empty_row_behind(self, row_index: int, num_bits: int):
        message = Message(plain_bits=[0]*num_bits,
                          pause=constants.SETTINGS.value("default_fuzzing_pause", 10**6, int),
                          message_type=self.protocol.default_message_type)

        tmp_protocol = ProtocolAnalyzer(None)
        tmp_protocol.messages = [message]
        undo_action = InsertBitsAndPauses(self.protocol, row_index+1, tmp_protocol)
        self.undo_stack.push(undo_action)

    def get_selected_label_index(self, row: int, column: int):
        if self.row_count == 0:
            return -1

        try:
            msg = self.protocol.messages[row]
        except IndexError:
            logger.warning("{} is out of range for generator protocol".format(row))
            return -1

        for i, lbl in enumerate(msg.message_type):
            if column in range(*msg.get_label_range(lbl, self.proto_view, False)):
                return i

        return -1

    def insert_column(self, index: int, rows: list):
        insert_action = InsertColumn(self.protocol, index, rows, self.proto_view)
        self.undo_stack.push(insert_action)
