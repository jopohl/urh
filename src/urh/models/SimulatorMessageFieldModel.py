from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, pyqtSignal
from PyQt5.QtGui import QFont

from urh.signalprocessing.SimulatorMessage import SimulatorMessage
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel

class SimulatorMessageFieldModel(QAbstractTableModel):
    header_labels = ['Name', 'Display format', 'Value type', 'Value']

    protocol_label_updated = pyqtSignal(SimulatorProtocolLabel)

    def __init__(self, controller, parent=None):
        super().__init__(parent)

        self.controller = controller # type: SimulatorTabController

        self.message_type = None # type: MessageType

    def update(self):
        self.beginResetModel()
        self.endResetModel()

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.header_labels)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.message_type) if self.message_type is not None else 0

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft

        return super().headerData(section, orientation, role)

    def value_str(self, label: SimulatorProtocolLabel):
        message = label.parent()
        start, end = message.get_label_range(label, label.display_format_index % 3, True)

        if label.display_format_index == 0:
            return message.decoded_bits_str[start:end]
        elif label.display_format_index == 1:
            return message.decoded_hex_str[start:end]
        elif label.display_format_index == 2:
            return message.decoded_ascii_str[start:end]
        elif label.display_format_index == 3:
            return int(message.decoded_bits_str[start:end], 2)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        i, j = index.row(), index.column()
        label = self.message_type[i]

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if j == 0:
                return label.name
            elif j == 1:
                return label.DISPLAY_FORMATS[label.display_format_index]
            elif j == 2:
                return label.VALUE_TYPES[label.value_type_index]
            elif j == 3:
                if label.value_type_index == 0:
                    return self.value_str(label)
                elif label.value_type_index in [1, 4]:
                    return "-"
                elif label.value_type_index == 2:
                    return label.formula
                elif label.value_type_index == 3:
                    return label.external_program
        elif role == Qt.FontRole:
            if j == 0:
                font = QFont()
                font.setItalic(label.type is None)
                return font

    def setData(self, index: QModelIndex, value, role=None):
        if role == Qt.EditRole:
            i, j = index.row(), index.column()
            label = self.message_type[i]

            if j == 0:
                label.name = value

                if value in self.controller.field_types_by_caption:
                    label.type = self.controller.field_types_by_caption[value]
                else:
                    label.type = None
            elif j == 1:
                label.display_format_index = value
            elif j == 2:
                label.value_type_index = value
            elif j == 3:
                if label.value_type_index == 2:
                    label.formula = value
                elif label.value_type_index == 3:
                    label.external_program = value

            self.protocol_label_updated.emit(label)

        return True

    def flags(self, index: QModelIndex):
        row, col = index.row(), index.column()
        label = self.message_type[row]

        flags = super().flags(index)

        if not(col == 3 and label.value_type_index in [0, 1, 4]):
            flags |= Qt.ItemIsEditable

        return flags