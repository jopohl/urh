import array

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, pyqtSignal
from PyQt5.QtGui import QFont

from urh import settings
from urh.signalprocessing.ChecksumLabel import ChecksumLabel
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.util import util


class LabelValueTableModel(QAbstractTableModel):
    protolabel_visibility_changed = pyqtSignal(ProtocolLabel)
    protocol_label_name_edited = pyqtSignal()
    label_removed = pyqtSignal(ProtocolLabel)
    label_color_changed = pyqtSignal(ProtocolLabel)

    header_labels = ["Name", "Color ", "Display format", "Order [Bit/Byte]", "Value"]

    def __init__(self, proto_analyzer: ProtocolAnalyzer, controller, parent=None):
        super().__init__(parent)
        self.proto_analyzer = proto_analyzer
        self.controller = controller
        self.__message_index = 0
        self.display_labels = controller.active_message_type  # type: MessageType
        self.selected_label_indices = set()

        self.show_label_values = True

    def __display_data(self, lbl: ProtocolLabel, expected_checksum: array = None):
        if not self.show_label_values or self.message is None:
            return "-"

        try:
            data = self.message.decoded_bits[lbl.start : lbl.end]
        except IndexError:
            return None

        lsb = lbl.display_bit_order_index == 1
        lsd = lbl.display_bit_order_index == 2

        data = util.convert_bits_to_string(
            data,
            lbl.display_format_index,
            pad_zeros=True,
            lsb=lsb,
            lsd=lsd,
            endianness=lbl.display_endianness,
        )
        if data is None:
            return None

        if expected_checksum is not None:
            data += " (should be {0})".format(
                util.convert_bits_to_string(expected_checksum, lbl.display_format_index)
            )

        return data

    @property
    def message_index(self):
        return self.__message_index

    @message_index.setter
    def message_index(self, value):
        self.__message_index = value
        self.update()

    @property
    def message(self):
        if self.message_index != -1 and self.message_index < len(
            self.proto_analyzer.messages
        ):
            return self.proto_analyzer.messages[self.message_index]
        else:
            return None

    def update(self):
        self.display_labels = self.controller.active_message_type
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

        if isinstance(lbl, ChecksumLabel) and self.message is not None:
            calculated_crc = lbl.calculate_checksum_for_message(
                self.message, use_decoded_bits=True
            )
        else:
            calculated_crc = None

        if role == Qt.DisplayRole:
            if j == 0:
                return lbl.name
            elif j == 1:
                return lbl.color_index
            elif j == 2:
                return lbl.DISPLAY_FORMATS[lbl.display_format_index]
            elif j == 3:
                return lbl.display_order_str
            elif j == 4:
                return self.__display_data(lbl, calculated_crc)
        elif role == Qt.CheckStateRole and j == 0:
            return lbl.show
        elif role == Qt.BackgroundColorRole:
            if isinstance(lbl, ChecksumLabel) and j == 4 and self.message is not None:
                start, end = self.message.get_label_range(lbl, 0, True)
                if calculated_crc == self.message.decoded_bits[start:end]:
                    return settings.BG_COLOR_CORRECT
                else:
                    return settings.BG_COLOR_WRONG

            else:
                return None

        elif role == Qt.ToolTipRole:
            if j == 2:
                return self.tr(
                    "Choose display type for the value of the label:"
                    "<ul>"
                    "<li>Bit</li>"
                    "<li>Hexadecimal (Hex)</li>"
                    "<li>ASCII chars</li>"
                    "<li>Decimal Number</li>"
                    "<li>Binary Coded Decimal (BCD)</li>"
                    "</ul>"
                )
            if j == 3:
                return self.tr(
                    "Choose bit order for the displayed value:"
                    "<ul>"
                    "<li>Most Significant Bit (MSB) [Default]</li>"
                    "<li>Least Significant Bit (LSB)</li>"
                    "<li>Least Significant Digit (LSD)</li>"
                    "</ul>"
                )
        elif role == Qt.FontRole and j == 0:
            font = QFont()
            font.setBold(i in self.selected_label_indices)
            return font

    def setData(self, index: QModelIndex, value, role=None):
        row = index.row()
        lbl = self.display_labels[row]
        if role == Qt.EditRole and index.column() in (0, 1, 2, 3):
            if index.column() == 0:
                lbl.name = value
                new_field_type = self.controller.field_types_by_caption.get(value, None)
                self.controller.active_message_type.change_field_type_of_label(
                    lbl, new_field_type
                )
            elif index.column() == 1:
                lbl.color_index = value
                self.label_color_changed.emit(lbl)
            elif index.column() == 2:
                lbl.display_format_index = value
            elif index.column() == 3:
                lbl.display_order_str = value

            self.dataChanged.emit(
                self.index(row, 0), self.index(row, self.columnCount())
            )
        elif role == Qt.CheckStateRole and index.column() == 0:
            lbl.show = value
            self.protolabel_visibility_changed.emit(lbl)
            return True

    def add_labels_to_message_type(self, start: int, end: int, message_type_id: int):
        for lbl in self.display_labels[start : end + 1]:
            if lbl not in self.controller.proto_analyzer.message_types[message_type_id]:
                self.controller.proto_analyzer.message_types[message_type_id].add_label(
                    lbl
                )
        self.controller.updateUI(resize_table=False)

    def delete_label_at(self, index: int):
        try:
            lbl = self.display_labels[index]
            self.display_labels.remove(lbl)
            self.label_removed.emit(lbl)
        except IndexError:
            pass

    def delete_labels_at(self, start: int, end: int):
        for row in range(end, start - 1, -1):
            self.delete_label_at(row)

    def flags(self, index: QModelIndex):
        flags = super().flags(index)
        if index.column() in (0, 1, 2, 3):
            flags |= Qt.ItemIsEditable
        if index.column() == 0:
            flags |= Qt.ItemIsUserCheckable

        return flags
