import array
import math
from collections import defaultdict

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QUndoStack
from urh.util.Logger import logger

from urh import constants
from urh.signalprocessing.ChecksumLabel import ChecksumLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.ui.actions.InsertColumn import InsertColumn
from urh.util import util


class TableModel(QAbstractTableModel):
    ALIGNMENT_CHAR = " "

    data_edited = pyqtSignal(int, int)
    vertical_header_color_status_changed = pyqtSignal(bool)

    def __init__(self, participants, parent=None):
        super().__init__(parent)
        self.controller = None  # :type: CompareFrameController|GeneratorTabController
        self.protocol = None  # type: ProtocolAnalyzer

        self.col_count = 0
        self.row_count = 0
        self.display_data = None  # type: list[str]

        self.search_results = []
        self.search_value = ""
        self._proto_view = 0
        self._refindex = -1

        self.first_messages = []
        self.hidden_rows = set()

        self.is_writeable = False
        self.locked = False
        self.decode = True  # False for Generator

        self.background_colors = defaultdict(lambda: None)
        self.bold_fonts = defaultdict(lambda: False)
        self.italic_fonts = defaultdict(lambda: False)
        self.text_colors = defaultdict(lambda: None)
        self.vertical_header_text = defaultdict(lambda: None)
        self.vertical_header_colors = defaultdict(lambda: None)

        self._diffs = defaultdict(set)  # type: dict[int, set[int]]

        self.undo_stack = QUndoStack()

        self.__participants = participants

    @property
    def participants(self):
        return self.__participants

    @participants.setter
    def participants(self, value):
        self.__participants = value
        for msg in self.protocol.messages:
            if msg.participant not in self.__participants:
                msg.participant = None

    @property
    def proto_view(self):
        return self._proto_view

    @proto_view.setter
    def proto_view(self, value):
        self._proto_view = value
        if self._refindex >= 0:
            self._diffs = self.find_differences(self._refindex)
        self.update()

    def get_alignment_offset_at(self, index: int):
        f = 1 if self.proto_view == 0 else 4 if self.proto_view == 1 else 8
        alignment_offset = int(math.ceil(self.protocol.messages[index].alignment_offset / f))
        return alignment_offset

    def __pad_until_index(self, row: int, bit_pos: int):
        """
        Pad message in given row with zeros until given column so user can enter values behind end of message
        :return:
        """
        try:
            new_bits = array.array("B", [0] * max(0, bit_pos - len(self.protocol.messages[row])))
            if len(new_bits) == 0:
                return True

            self.protocol.messages[row].plain_bits = self.protocol.messages[row].plain_bits + new_bits
            msg = self.protocol.messages[row]
            self.display_data[
                row] = msg.plain_bits if self.proto_view == 0 else msg.plain_hex_array if self.proto_view == 1 else msg.plain_ascii_array
        except IndexError:
            return False

        return True

    def headerData(self, section: int, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Vertical:
            if role == Qt.DisplayRole:
                return self.vertical_header_text[section]
            elif role == Qt.BackgroundColorRole:
                return self.vertical_header_colors[section]
            elif role == Qt.TextColorRole:
                color = self.vertical_header_colors[section]
                if color:
                    red, green, blue = color.red(), color.green(), color.blue()
                    return QColor("black") if (red * 0.299 + green * 0.587 + blue * 0.114) > 186 else QColor("white")
                else:
                    return None

        return super().headerData(section, orientation, role)

    def update(self):
        self.locked = True

        if self.protocol.num_messages > 0:
            if self.decode:
                if self.proto_view == 0:
                    self.display_data = [msg.decoded_bits for msg in self.protocol.messages]
                elif self.proto_view == 1:
                    self.display_data = [msg.decoded_hex_array for msg in self.protocol.messages]
                elif self.proto_view == 2:
                    self.display_data = [msg.decoded_ascii_array for msg in self.protocol.messages]
            else:
                # Generator Model
                if self.proto_view == 0:
                    self.display_data = [msg.plain_bits for msg in self.protocol.messages]
                elif self.proto_view == 1:
                    self.display_data = [msg.plain_hex_array for msg in self.protocol.messages]
                else:
                    self.display_data = [msg.plain_ascii_array for msg in self.protocol.messages]

            visible_messages = [msg for i, msg in enumerate(self.display_data) if i not in self.hidden_rows]
            if len(visible_messages) == 0:
                self.col_count = 0
            else:
                self.col_count = max(len(msg) + self.get_alignment_offset_at(i)
                                     for i, msg in enumerate(self.display_data) if i not in self.hidden_rows)

            if self._refindex >= 0:
                self._diffs = self.find_differences(self._refindex)
            else:
                self._diffs.clear()

            self.row_count = self.protocol.num_messages
            self.find_protocol_value(self.search_value)
        else:
            self.col_count = 0
            self.row_count = 0
            self.display_data = None

        # Cache background colors for performance
        self.refresh_bgcolors()
        self.refresh_fonts()  # Will be overriden
        self.refresh_vertical_header()

        self.beginResetModel()
        self.endResetModel()
        self.locked = False

    def insert_column(self, index: int, rows: list):
        if self.protocol is None or not self.is_writeable:
            return

        insert_action = InsertColumn(self.protocol, index, rows, self.proto_view)
        self.undo_stack.push(insert_action)

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self.col_count

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self.row_count

    def refresh_bgcolors(self):
        self.background_colors.clear()
        label_colors = constants.LABEL_COLORS

        for i, message in enumerate(self.protocol.messages):
            for lbl in message.message_type:
                bg_color = label_colors[lbl.color_index]
                a = self.get_alignment_offset_at(i)
                start, end = message.get_label_range(lbl, self.proto_view, self.decode)
                for j in range(start, end):
                    self.background_colors[i, j + a] = bg_color

    def refresh_fonts(self):
        """
        Will be overriden

        :return:
        """
        pass

    def refresh_vertical_header(self):
        self.vertical_header_colors.clear()
        self.vertical_header_text.clear()
        use_colors = False
        for i in range(self.row_count):
            try:
                participant = self.protocol.messages[i].participant
            except IndexError:
                participant = None
            if participant:
                self.vertical_header_text[i] = "{0} ({1})".format(i + 1, participant.shortname)
                self.vertical_header_colors[i] = constants.PARTICIPANT_COLORS[participant.color_index]
                use_colors = True
            else:
                self.vertical_header_text[i] = str(i + 1)

        self.vertical_header_color_status_changed.emit(use_colors)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        i = index.row()
        j = index.column()
        if role == Qt.DisplayRole and self.display_data:
            try:
                alignment_offset = self.get_alignment_offset_at(i)
                if j < alignment_offset:
                    return self.ALIGNMENT_CHAR

                if self.proto_view == 0:
                    return self.display_data[i][j - alignment_offset]
                elif self.proto_view == 1:
                    return "{0:x}".format(self.display_data[i][j - alignment_offset])
                elif self.proto_view == 2:
                    return chr(self.display_data[i][j - alignment_offset])
            except IndexError:
                return None

        elif role == Qt.TextAlignmentRole:
            if i in self.first_messages:
                return Qt.AlignHCenter + Qt.AlignBottom
            else:
                return Qt.AlignCenter

        elif role == Qt.BackgroundColorRole:
            return self.background_colors[i, j]

        elif role == Qt.FontRole:
            font = QFont()
            font.setBold(self.bold_fonts[i, j])
            font.setItalic(self.italic_fonts[i, j])
            return font

        elif role == Qt.TextColorRole:
            return self.text_colors[i, j]

        elif role == Qt.ToolTipRole:
            return self.get_tooltip(i, j)
        else:
            return None

    def get_tooltip(self, row: int, column: int) -> str:
        msg = self.protocol.messages[row]
        try:
            lbl = next(lbl for lbl in msg.message_type
                       if column in range(*msg.get_label_range(lbl, self.proto_view, self.decode)))
        except StopIteration:
            return ""

        result = lbl.name
        if isinstance(lbl, ChecksumLabel):
            calculated_crc = lbl.calculate_checksum_for_message(msg, use_decoded_bits=self.decode)
            start, end = msg.get_label_range(lbl=lbl, view=0, decode=self.decode)
            bits = msg.decoded_bits if self.decode else msg.plain_bits
            color = "green" if bits[start:end] == calculated_crc else "red"
            expected = util.convert_bits_to_string(calculated_crc, self.proto_view)
            result += '<br><font color="{}">Expected <b>{}</b></font>'.format(color, expected)

        return result

    def setData(self, index: QModelIndex, value, role=Qt.DisplayRole):
        if role != Qt.EditRole:
            return True

        i = index.row()
        j = index.column()
        a = self.get_alignment_offset_at(i)
        j -= a
        hex_chars = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f")

        if i >= len(self.protocol.messages):
            return False

        if self.proto_view == 0 and value in ("0", "1") and self.__pad_until_index(i, j + 1):
            self.protocol.messages[i][j] = bool(int(value))
            self.display_data[i][j] = int(value)
        elif self.proto_view == 1 and value in hex_chars and self.__pad_until_index(i, (j + 1) * 4):
            converted_j = self.protocol.convert_index(j, 1, 0, self.decode, message_indx=i)[0]
            bits = "{0:04b}".format(int(value, 16))
            for k in range(4):
                self.protocol.messages[i][converted_j + k] = bool(int(bits[k]))
            self.display_data[i][j] = int(value, 16)
        elif self.proto_view == 2 and len(value) == 1 and self.__pad_until_index(i, (j + 1) * 8):
            converted_j = self.protocol.convert_index(j, 2, 0, self.decode, message_indx=i)[0]
            bits = "{0:08b}".format(ord(value))
            for k in range(8):
                self.protocol.messages[i][converted_j + k] = bool(int(bits[k]))
            self.display_data[i][j] = ord(value)
        else:
            return False

        self.data_edited.emit(i, j)
        return True

    def find_protocol_value(self, value):
        self.search_results.clear()
        if self.proto_view == 1:
            value = value.lower()

        self.search_value = value

        if len(value) == 0:
            return 0

        for i, message in enumerate(self.protocol.messages):
            if i in self.hidden_rows:
                continue

            data = message.view_to_string(self.proto_view, self.decode)
            j = data.find(value)
            while j != -1:
                self.search_results.append((i, j + self.get_alignment_offset_at(i)))
                j = data.find(value, j + 1)

        return len(self.search_results)

    def find_differences(self, refindex: int):
        """
        Search all differences between protocol messages regarding a reference message

        :param refindex: index of reference message
        :rtype: dict[int, set[int]]
        """
        differences = defaultdict(set)

        if refindex >= len(self.protocol.messages):
            return differences

        if self.proto_view == 0:
            proto = self.protocol.decoded_proto_bits_str
        elif self.proto_view == 1:
            proto = self.protocol.decoded_hex_str
        elif self.proto_view == 2:
            proto = self.protocol.decoded_ascii_str
        else:
            return differences

        ref_message = proto[refindex]
        ref_offset = self.get_alignment_offset_at(refindex)

        for i, message in enumerate(proto):
            if i == refindex:
                continue

            msg_offset = self.get_alignment_offset_at(i)
            short, long = sorted([len(ref_message) + ref_offset, len(message) + msg_offset])

            differences[i] = {
                j for j in range(max(msg_offset, ref_offset), long)
                if j >= short or message[j - msg_offset] != ref_message[j - ref_offset]
            }

        return differences

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
