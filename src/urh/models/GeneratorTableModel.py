import array
import copy

from PyQt5.QtCore import Qt, QModelIndex, pyqtSlot
from PyQt5.QtGui import QColor

from urh import constants
from urh.models.ProtocolTreeItem import ProtocolTreeItem
from urh.models.TableModel import TableModel
from urh.signalprocessing.ChecksumLabel import ChecksumLabel
from urh.signalprocessing.Message import Message
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer
from urh.signalprocessing.Encoding import Encoding
from urh.ui.actions.Clear import Clear
from urh.ui.actions.DeleteBitsAndPauses import DeleteBitsAndPauses
from urh.ui.actions.InsertBitsAndPauses import InsertBitsAndPauses
from urh.ui.actions.InsertColumn import InsertColumn
from urh.util import util
from urh.util.Logger import logger


class GeneratorTableModel(TableModel):
    def __init__(self, tree_root_item: ProtocolTreeItem, modulators, decodings, parent = None):
        super().__init__(participants=[], parent=parent)
        self.protocol = ProtocolAnalyzerContainer(modulators)
        self.tree_root_item = tree_root_item
        self.dropped_row = -1

        self.decodings = decodings  # type: list[Encoding]

        self.cfc = None
        self.is_writeable = True
        self.decode = False
        self.is_generator = True

        self.data_edited.connect(self.on_data_edited)

    def refresh_fonts(self):
        self.italic_fonts.clear()
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

            for lbl in (lbl for lbl in message.message_type if isinstance(lbl, ChecksumLabel)):
                if not lbl.checksum_manually_edited:
                    for j in range(*message.get_label_range(lbl=lbl, view=self.proto_view, decode=False)):
                        self.italic_fonts[i, j] = True

    def delete_range(self, msg_start: int, msg_end: int, index_start: int, index_end: int):
        if msg_start > msg_end:
            msg_start, msg_end = msg_end, msg_start
        if index_start > index_end:
            index_start, index_end = index_end, index_start

        remove_action = DeleteBitsAndPauses(self.protocol, msg_start, msg_end, index_start,
                                            index_end, self.proto_view, False)
        ########## Delete according pauses
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

    def __copy_label_on_write(self, label, message_type):
        if not label.copied:
            index = message_type.index(label)
            label = copy.deepcopy(label)
            message_type[index] = label
            label.copied = True
        return label

    @pyqtSlot(int, int)
    def on_data_edited(self, row: int, column: int):
        edited_range = range(column, column+1)
        message = self.protocol.messages[row]
        checksum_labels = [lbl for lbl in message.message_type if isinstance(lbl, ChecksumLabel)]
        if checksum_labels:
            edited_checksum_labels = [lbl for lbl in checksum_labels
                                      if any(j in edited_range
                                             for j in range(*message.get_label_range(lbl=lbl,
                                                                                     view=self.proto_view,
                                                                                     decode=False)))]

            if edited_checksum_labels:
                for lbl in edited_checksum_labels:
                    lbl = self.__copy_label_on_write(lbl, message.message_type)
                    lbl.checksum_manually_edited = True
            else:
                for lbl in checksum_labels:  # type: ChecksumLabel
                    lbl = self.__copy_label_on_write(lbl, message.message_type)
                    lbl.checksum_manually_edited = False
                    calculated_checksum = lbl.calculate_checksum_for_message(message)
                    label_range = message.get_label_range(lbl=lbl, view=0, decode=False)
                    start, end = label_range[0], label_range[1]
                    message.plain_bits[start:end] = calculated_checksum + array.array("B", [0]*((end-start) - len(calculated_checksum)))

                    label_range = message.get_label_range(lbl=lbl, view=self.proto_view, decode=False)
                    start, end = label_range[0], label_range[1]
                    if self.proto_view == 0:
                        data = calculated_checksum
                    elif self.proto_view == 1:
                        data = util.aggregate_bits(calculated_checksum, size=4)
                    elif self.proto_view == 2:
                        data = util.aggregate_bits(calculated_checksum, size=8)
                    else:
                        data = array.array("B", [])

                    self.display_data[row][start:end] = data + array.array("B", [0]*((end-start) - len(data)))

            # If performance should suffer, we need to update italic fonts only here
            self.refresh_fonts()
