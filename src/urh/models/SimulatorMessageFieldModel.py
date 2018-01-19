from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from urh import constants
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.simulator.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.util import util


class SimulatorMessageFieldModel(QAbstractTableModel):
    header_labels = ['Name', 'Display format', 'Value type', 'Value']

    protocol_label_updated = pyqtSignal(SimulatorProtocolLabel)

    def __init__(self, controller, parent=None):
        super().__init__(parent)

        self.controller = controller # type: SimulatorTabController
        self.message_type = None  # type: MessageType

    def update(self):
        self.beginResetModel()
        self.message_type = self.controller.active_item.message_type
        self.endResetModel()

    def columnCount(self, parent: QModelIndex=None, *args, **kwargs):
        return len(self.header_labels)

    def rowCount(self, parent: QModelIndex=None, *args, **kwargs):
        return len(self.message_type) if self.message_type is not None else 0

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft

        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        i, j = index.row(), index.column()
        lbl = self.message_type[i]  # type: SimulatorProtocolLabel

        if role == Qt.DisplayRole:
            if j == 0:
                return lbl.name
            elif j == 1:
                return ProtocolLabel.DISPLAY_FORMATS[lbl.display_format_index]
            elif j == 2:
                return lbl.VALUE_TYPES[lbl.value_type_index]
            elif j == 3:
                if lbl.value_type_index == 0:
                    message = lbl.parent()

                    try:
                        data = message.decoded_bits[lbl.start:lbl.end]
                    except IndexError:
                        return None

                    return util.convert_bits_to_string(data, lbl.display_format_index, pad_zeros=True)
                elif lbl.value_type_index == 1:
                    return "-"
                elif lbl.value_type_index == 2:
                    return lbl.formula
                elif lbl.value_type_index == 3:
                    return lbl.external_program
                elif lbl.value_type_index == 4:
                    return "Range (Decimal): " + str(lbl.random_min) + " - " + str(lbl.random_max)
        elif role == Qt.EditRole:
            if j == 0:
                return lbl.name
            elif j == 1:
                return lbl.display_format_index
            elif j == 2:
                return lbl.value_type_index
            elif j == 3:
                if lbl.value_type_index == 2:
                    return lbl.formula
                elif lbl.value_type_index == 3:
                    return lbl.external_program
                elif lbl.value_type_index == 4:
                    return [lbl.random_min, lbl.random_max]
        elif role == Qt.FontRole:
            if j == 0:
                font = QFont()
                font.setItalic(lbl.field_type is None)
                return font
        elif role == Qt.BackgroundColorRole:
            if j == 0:
                return constants.LABEL_COLORS[lbl.color_index]
            elif j == 3:
                if (lbl.value_type_index == 2 and
                        not self.controller.sim_expression_parser.validate_expression(lbl.formula)[0]):
                    return constants.ERROR_BG_COLOR

    def setData(self, index: QModelIndex, value, role=None):
        if role == Qt.EditRole:
            i, j = index.row(), index.column()
            label = self.message_type[i]  # type: SimulatorProtocolLabel

            if j == 0:
                label.name = value

                if value in self.controller.field_types_by_caption:
                    label.field_type = self.controller.field_types_by_caption[value]
                else:
                    label.field_type = None
            elif j == 1:
                label.display_format_index = value
            elif j == 2:
                label.value_type_index = value
            elif j == 3:
                if label.value_type_index == 2:
                    label.formula = value
                elif label.value_type_index == 3:
                    label.external_program = value
                elif label.value_type_index == 4:
                    label.random_min = value[0]
                    label.random_max = value[1]
            self.dataChanged.emit(self.index(i, 0),
                                  self.index(i, self.columnCount()))
            self.protocol_label_updated.emit(label)

        return True

    def flags(self, index: QModelIndex):
        row, col = index.row(), index.column()
        label = self.message_type[row]  # type: SimulatorProtocolLabel

        flags = super().flags(index)

        if not(col == 3 and label.value_type_index in [0, 1]):
            flags |= Qt.ItemIsEditable

        return flags