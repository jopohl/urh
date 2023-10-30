import array
from collections import defaultdict

from PyQt5.QtCore import Qt, QModelIndex, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QColor

from urh import settings
from urh.models.ProtocolTreeItem import ProtocolTreeItem
from urh.models.TableModel import TableModel
from urh.signalprocessing.ChecksumLabel import ChecksumLabel
from urh.signalprocessing.Encoding import Encoding
from urh.signalprocessing.Message import Message
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer
from urh.ui.actions.Clear import Clear
from urh.ui.actions.DeleteBitsAndPauses import DeleteBitsAndPauses
from urh.ui.actions.InsertBitsAndPauses import InsertBitsAndPauses
from urh.util import util
from urh.cythonext import util as c_util


class GeneratorTableModel(TableModel):
    first_protocol_added = pyqtSignal(ProtocolAnalyzer)

    def __init__(self, tree_root_item: ProtocolTreeItem, decodings, parent=None):
        super().__init__(participants=[], parent=parent)
        self.protocol = ProtocolAnalyzerContainer()
        self.tree_root_item = tree_root_item
        self.dropped_row = -1

        self.decodings = decodings  # type: list[Encoding]

        self.cfc = None
        self.is_writeable = True
        self.decode = False
        self.is_generator = True

        self.edited_checksum_labels_by_row = defaultdict(set)

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
                    for j in range(
                        *message.get_label_range(
                            lbl=lbl, view=self.proto_view, decode=False
                        )
                    ):
                        self.bold_fonts[i, j] = True

            for lbl in message.active_fuzzing_labels:
                for j in range(
                    *message.get_label_range(
                        lbl=lbl, view=self.proto_view, decode=False
                    )
                ):
                    self.bold_fonts[i, j] = True
                    self.text_colors[i, j] = QColor("orange")

            for lbl in (
                lbl for lbl in message.message_type if isinstance(lbl, ChecksumLabel)
            ):
                if (
                    lbl not in self.edited_checksum_labels_by_row[i]
                    and not lbl.fuzz_created
                ):
                    self.__set_italic_font_for_label_range(
                        row=i, label=lbl, italic=True
                    )

    def delete_range(
        self, msg_start: int, msg_end: int, index_start: int, index_end: int
    ):
        if msg_start > msg_end:
            msg_start, msg_end = msg_end, msg_start
        if index_start > index_end:
            index_start, index_end = index_end, index_start

        remove_action = DeleteBitsAndPauses(
            self.protocol,
            msg_start,
            msg_end,
            index_start,
            index_end,
            self.proto_view,
            False,
        )
        ########## Delete according pauses
        self.undo_stack.push(remove_action)

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemIsEnabled

        return (
            Qt.ItemIsEnabled
            | Qt.ItemIsDropEnabled
            | Qt.ItemIsSelectable
            | Qt.ItemIsDragEnabled
            | Qt.ItemIsEditable
        )

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
        nodes_to_add.extend(
            [file_node for file_node in file_nodes if file_node not in nodes_to_add]
        )

        is_empty = self.row_count == 0

        for node in reversed(nodes_to_add):
            undo_action = InsertBitsAndPauses(
                self.protocol, self.dropped_row, node.protocol
            )
            self.undo_stack.push(undo_action)

        if is_empty and self.row_count > 0:
            self.first_protocol_added.emit(nodes_to_add[0].protocol)

        return True

    def clear(self):
        clear_action = Clear(self.protocol)
        self.undo_stack.push(clear_action)

    def duplicate_rows(self, rows: list):
        self.protocol.duplicate_lines(rows)
        self.update()

    def add_empty_row_behind(self, row_index: int, num_bits: int):
        message = Message(
            plain_bits=[0] * num_bits,
            pause=settings.read("default_fuzzing_pause", 10**6, int),
            message_type=self.protocol.default_message_type,
        )

        tmp_protocol = ProtocolAnalyzer(None)
        tmp_protocol.messages = [message]
        undo_action = InsertBitsAndPauses(self.protocol, row_index + 1, tmp_protocol)
        self.undo_stack.push(undo_action)

    def generate_de_bruijn(self, row_index: int, start: int, end: int):
        if start < 0 or end < 0:
            return

        f = 1 if self.proto_view == 0 else 4 if self.proto_view == 1 else 8
        start, end = f * start, f * end

        de_bruijn_seq = c_util.de_bruijn(end - start)

        tmp_protocol = ProtocolAnalyzer(None)
        tmp_protocol.messages = []
        LINE_BREAK_AFTER = 5000 * f
        for i in range(0, len(de_bruijn_seq), LINE_BREAK_AFTER):
            message = Message(
                plain_bits=de_bruijn_seq[i : i + LINE_BREAK_AFTER],
                pause=0,
                message_type=self.protocol.default_message_type,
            )
            tmp_protocol.messages.append(message)

        undo_action = InsertBitsAndPauses(self.protocol, row_index + 1, tmp_protocol)
        self.undo_stack.push(undo_action)

    def __set_italic_font_for_label_range(self, row, label, italic: bool):
        message = self.protocol.messages[row]
        for j in range(
            *message.get_label_range(lbl=label, view=self.proto_view, decode=False)
        ):
            self.italic_fonts[row, j] = italic

    def update_checksums_for_row(self, row: int):
        msg = self.protocol.messages[row]
        for lbl in msg.message_type.checksum_labels:  # type: ChecksumLabel
            if lbl.fuzz_created:
                continue

            self.__set_italic_font_for_label_range(row, lbl, italic=True)
            self.edited_checksum_labels_by_row[row].discard(lbl)

            calculated_checksum = lbl.calculate_checksum_for_message(
                msg, use_decoded_bits=False
            )
            label_range = msg.get_label_range(lbl=lbl, view=0, decode=False)
            start, end = label_range[0], label_range[1]
            msg[start:end] = calculated_checksum + array.array(
                "B", [0] * ((end - start) - len(calculated_checksum))
            )

            label_range = msg.get_label_range(
                lbl=lbl, view=self.proto_view, decode=False
            )
            start, end = label_range[0], label_range[1]
            if self.proto_view == 0:
                data = calculated_checksum
            elif self.proto_view == 1:
                data = util.aggregate_bits(calculated_checksum, size=4)
            elif self.proto_view == 2:
                data = util.aggregate_bits(calculated_checksum, size=8)
            else:
                data = array.array("B", [])

            self.display_data[row][start:end] = data + array.array(
                "B", [0] * ((end - start) - len(data))
            )

    @pyqtSlot(int, int)
    def on_data_edited(self, row: int, column: int):
        edited_range = range(column, column + 1)
        message = self.protocol.messages[row]
        checksum_labels = message.message_type.checksum_labels
        if checksum_labels:
            edited_checksum_labels = [
                lbl
                for lbl in checksum_labels
                if any(
                    j in edited_range
                    for j in range(
                        *message.get_label_range(
                            lbl=lbl, view=self.proto_view, decode=False
                        )
                    )
                )
            ]

            if edited_checksum_labels:
                for lbl in edited_checksum_labels:
                    if lbl.fuzz_created:
                        continue

                    self.__set_italic_font_for_label_range(row, lbl, italic=False)
                    self.edited_checksum_labels_by_row[row].add(lbl)
            else:
                self.update_checksums_for_row(row)
