from collections import defaultdict

import numpy
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QUndoStack, QMessageBox

from urh import constants
from urh.cythonext.signalFunctions import Symbol


class TableModel(QAbstractTableModel):
    def __init__(self, participants, parent=None):
        super().__init__(parent)
        self.controller = None
        """:type: CompareFrameController or GeneratorTabController """
        self.protocol = None # Reimplement in Child classes
        """:type: ProtocolAnalyzer """

        self.col_count = 0
        self.row_count = 0
        self.display_data = None
        """:type: list[str] """

        self.search_results = []
        self.search_value = ""
        self._proto_view = 0
        self._refindex = -1

        self.first_messages = []
        self.hidden_rows = set()

        self.is_writeable = False
        self.locked = False
        self.decode = True  # False for Generator

        self.symbols = {}
        """:type: dict[str, Symbol] """

        self.background_colors = defaultdict(lambda: None)
        self.bold_fonts = defaultdict(lambda: False)
        self.text_colors = defaultdict(lambda: None)
        self.tooltips = defaultdict(lambda: None)
        self.vertical_header_text = defaultdict(lambda: None)
        self.vertical_header_colors = defaultdict(lambda: None)

        self._diffs = defaultdict(set)
        """:type: dict[int, set[int]] """

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
            self._diffs = self.protocol.find_differences(self._refindex, self._proto_view)
        self.update()

    def headerData(self, section: int, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Vertical:
            if role == Qt.DisplayRole:
                return self.vertical_header_text[section]
            elif role == Qt.BackgroundColorRole:
                return self.vertical_header_colors[section]
            elif role == Qt.TextColorRole:
                color = self.vertical_header_colors[section]
                if color:
                    red, green, blue  = color.red(), color.green(), color.blue()
                    return QColor("black") if (red * 0.299 + green * 0.587 + blue * 0.114) > 186 else QColor("white")
                else:
                    return None

        return super().headerData(section, orientation, role)

    def update(self):
        self.locked = True

        self.symbols.clear()
        self.symbols = {symbol.name: symbol for symbol in self.protocol.used_symbols}

        if self.protocol.num_messages > 0:
            if self.decode:
                if self.proto_view == 0:
                    self.display_data = self.protocol.decoded_proto_bits_str
                elif self.proto_view == 1:
                    self.display_data = self.protocol.decoded_hex_str
                elif self.proto_view == 2:
                    self.display_data = self.protocol.decoded_ascii_str
            else:
                #
                # Generator Model
                if self.proto_view == 0:
                    self.display_data = self.protocol.plain_bits_str
                elif self.proto_view == 1:
                    self.display_data = self.protocol.plain_hex_str
                else:
                    self.display_data = self.protocol.plain_ascii_str

            visible_messages = [msg for i, msg in enumerate(self.display_data) if i not in self.hidden_rows]
            if len(visible_messages) == 0:
                self.col_count = 0
            else:
                self.col_count = numpy.max([len(msg) for msg in visible_messages])

            if self._refindex >= 0:
                self._diffs = self.protocol.find_differences(self._refindex, self.proto_view)
            else:
                self._diffs.clear()

            self.row_count = self.protocol.num_messages
            self.find_protocol_value(self.search_value)
        else:
            self.col_count = 0
            self.row_count = 0
            self.display_data = None

        # Cache background colors for performance
        self.refresh_bgcolors_and_tooltips()
        self.refresh_fonts()  # Will be overriden
        self.refresh_vertical_header()

        self.beginResetModel()
        self.endResetModel()
        self.locked = False

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self.col_count

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self.row_count

    def refresh_bgcolors_and_tooltips(self):
        self.background_colors.clear()
        self.tooltips.clear()
        label_colors = constants.LABEL_COLORS

        for i, message in enumerate(self.protocol.messages):
            for lbl in message.message_type:
                bg_color = label_colors[lbl.color_index]
                start, end = message.get_label_range(lbl, self.proto_view, self.decode)
                for j in range(start, end):
                    self.background_colors[i, j] = bg_color
                    self.tooltips[i, j] = lbl.name

    def refresh_fonts(self):
        """
        Will be overriden

        :return:
        """
        pass

    def refresh_vertical_header(self):
        self.vertical_header_colors.clear()
        self.vertical_header_text.clear()
        for i in range(self.row_count):
            try:
                participant = self.protocol.messages[i].participant
            except IndexError:
                participant = None
            if participant:
                self.vertical_header_text[i] = "{0} ({1})".format(i + 1, participant.shortname)
                self.vertical_header_colors[i] = constants.PARTICIPANT_COLORS[participant.color_index]
            else:
                self.vertical_header_text[i] = str(i+1)


    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        i = index.row()
        j = index.column()
        if role == Qt.DisplayRole and self.display_data:
            try:
                return self.display_data[i][j]
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
            return font

        elif role == Qt.TextColorRole:
            return self.text_colors[i, j]

        elif role == Qt.ToolTipRole:
            return self.tooltips[i, j]

        else:
            return None

    def setData(self, index: QModelIndex, value, role=Qt.DisplayRole):
        if role == Qt.EditRole:
            i = index.row()
            j = index.column()
            hex_chars = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f")

            if self.proto_view == 0:
                if value in ("0", "1"):
                    try:
                        self.protocol.messages[i][j] = bool(int(value))
                        self.update()
                    except IndexError:
                        return False
                elif value in self.symbols.keys():
                    try:
                        self.protocol.messages[i][j] = self.symbols[value]
                        self.update()
                    except IndexError:
                        return False
            elif self.proto_view == 1:
                if value in hex_chars:
                    index = self.protocol.convert_index(j, 1, 0, True, message_indx=i)[0]
                    bits = "{0:04b}".format(int(value, 16))
                    for k in range(4):
                        try:
                            if type(self.protocol.messages[i][index + k]) != Symbol:
                                self.protocol.messages[i][index + k] = bool(int(bits[k]))
                            else:
                                break
                        except IndexError:
                            break
                    self.update()
                elif value in self.symbols.keys():
                    QMessageBox.information(None, "Setting symbol", "You can only set custom bit symbols in bit view!")
            elif self.proto_view == 2 and len(value) == 1:
                if value in self.symbols.keys():
                    QMessageBox.information(None, "Setting symbol", "You can only set custom bit symbols in bit view!")

                index = self.protocol.convert_index(j, 2, 0, True, message_indx=i)[0]
                bits = "{0:08b}".format(ord(value))
                for k in range(8):
                    try:
                        if type(self.protocol.messages[i][index + k]) != Symbol:
                            self.protocol.messages[i][index + k] = bool(int(bits[k]))
                        else:
                            break
                    except IndexError:
                        break
                self.update()
        return True

    def find_protocol_value(self, value):
        self.search_results[:] = []
        self.search_value = value

        if len(value) == 0:
            return 0

        for i, message in enumerate(self.display_data):
            if i in self.hidden_rows:
                continue

            j = message.find(value)
            while j != -1:
                self.search_results.append((i, j))
                j = message.find(value, j + 1)

        return len(self.search_results)