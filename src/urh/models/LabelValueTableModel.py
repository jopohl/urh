from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex

from urh import constants
from urh.signalprocessing.ChecksumLabel import ChecksumLabel
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.util import util


class LabelValueTableModel(QAbstractTableModel):
    header_labels = ["Name", 'Display format', 'Value']

    def __init__(self, proto_analyzer: ProtocolAnalyzer, controller, parent=None):
        super().__init__(parent)
        self.proto_analyzer = proto_analyzer
        self.controller = controller
        self.__message_index = 0
        self.display_labels = controller.active_message_type  # type: MessageType

        self.bit_str = self.proto_analyzer.decoded_proto_bits_str
        self.hex_str = self.proto_analyzer.decoded_hex_str
        self.ascii_str = self.proto_analyzer.decoded_ascii_str

    @property
    def message_index(self):
        return self.__message_index

    @message_index.setter
    def message_index(self, value):
        self.__message_index = value
        self.update()

    @property
    def message(self):
        if self.message_index != -1 and self.message_index < len(self.proto_analyzer.messages):
            return self.proto_analyzer.messages[self.message_index]
        else:
            return None

    def update(self):
        self.display_labels = self.controller.active_message_type
        self.bit_str = self.proto_analyzer.decoded_proto_bits_str
        self.hex_str = self.proto_analyzer.decoded_hex_str
        self.ascii_str = self.proto_analyzer.decoded_ascii_str
        self.beginResetModel()
        self.endResetModel()

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.header_labels)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.display_labels)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft

        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        i, j = index.row(), index.column()

        try:
            lbl = self.display_labels[i]
        except IndexError:
            return None

        if not lbl or not self.message:
            return None

        if isinstance(lbl, ChecksumLabel):
            calculated_crc = lbl.calculate_checksum_for_message(self.message, use_decoded_bits=True)
        else:
            calculated_crc = None

        if role == Qt.DisplayRole:
            if j == 0:
                return lbl.name
            elif j == 1:
                return lbl.DISPLAY_FORMATS[lbl.display_format_index]
            elif j == 2:
                try:
                    if lbl.display_format_index == 1:
                        start, end = self.message.get_label_range(lbl, 1, True)
                        data = self.hex_str[self.message_index][start:end]
                    elif lbl.display_format_index == 2:
                        start, end = self.message.get_label_range(lbl, 2, True)
                        data = self.ascii_str[self.message_index][start:end]
                    else:
                        start, end = self.message.get_label_range(lbl, 0, True)
                        data = self.bit_str[self.message_index][start:end]
                except IndexError:
                    return None

                if lbl.display_format_index == 3:  # decimal
                    try:
                        data = str(int(data, 2))
                    except ValueError:
                        return None

                if calculated_crc is not None:
                    data += " (should be {0})".format(
                        util.convert_bits_to_string(calculated_crc, lbl.display_format_index))

                return data

        elif role == Qt.BackgroundColorRole:
            if isinstance(lbl, ChecksumLabel):
                start, end = self.message.get_label_range(lbl, 0, True)
                if calculated_crc == self.message.decoded_bits[start:end]:
                    return constants.BG_COLOR_CORRECT
                else:
                    return constants.BG_COLOR_WRONG

            else:
                return None

    def setData(self, index: QModelIndex, value, role=None):
        if role == Qt.EditRole:
            row = index.row()
            lbl = self.display_labels[row]
            if index.column() == 1:
                lbl.display_format_index = value
                self.dataChanged.emit(self.index(row, 0),
                                      self.index(row, self.columnCount()))

    def flags(self, index: QModelIndex):
        flags = super().flags(index)
        if index.column() == 1:
            flags |= Qt.ItemIsEditable

        return flags
