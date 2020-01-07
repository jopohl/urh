from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import qApp

from urh import settings
from urh.signalprocessing.FieldType import FieldType
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
                if lbl.is_checksum_label:
                    return "Checksum"
                else:
                    return lbl.VALUE_TYPES[lbl.value_type_index]
            elif j == 3:
                if lbl.value_type_index == 0:
                    message = lbl.parent()

                    try:
                        data = message.plain_bits[lbl.start:lbl.end]
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
            elif j == 2 and self.link_index(index):
                font = QFont()
                font.setUnderline(True)
                return font
        elif role == Qt.BackgroundColorRole:
            if j == 0:
                return settings.LABEL_COLORS[lbl.color_index]
            elif j == 3:
                if (lbl.value_type_index == 2 and
                        not self.controller.sim_expression_parser.validate_expression(lbl.formula)[0]):
                    return settings.ERROR_BG_COLOR
        elif role == Qt.TextColorRole:
            if self.link_index(index):
                return qApp.palette().link().color()

    def link_index(self, index: QModelIndex):
        try:
            lbl = self.message_type[index.row()]  # type: SimulatorProtocolLabel
            if index.column() == 2 and lbl.is_checksum_label:
                return True
        except:
            return False
        return False

    def setData(self, index: QModelIndex, value, role=None):
        if role == Qt.EditRole:
            i, j = index.row(), index.column()
            label = self.message_type[i]  # type: SimulatorProtocolLabel

            if j == 0:
                label.name = value
                ft = self.controller.field_types_by_caption.get(value, FieldType("Custom", FieldType.Function.CUSTOM))
                label.field_type = ft
            elif j == 1:
                label.display_format_index = value
            elif j == 2:
                label.value_type_index = value
            elif j == 3:
                if label.value_type_index == 0:
                    message = label.parent()
                    try:
                        bits = util.convert_string_to_bits(value, label.display_format_index,
                                                           target_num_bits=label.end-label.start)

                        message.plain_bits[label.start:label.end] = bits
                    except ValueError:
                        pass
                elif label.value_type_index == 2:
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

        if col == 2 and label.is_checksum_label:
            return Qt.ItemIsSelectable

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        if not(col == 3 and label.value_type_index == 1):
            flags |= Qt.ItemIsEditable

        return flags

    def remove_label_at(self, index: int):
        try:
            label = self.message_type[index]
            self.controller.simulator_config.delete_items([label])
        except IndexError:
            pass

    def set_value_type_index(self, rows: list, value_type_index: int):
        for row in rows:
            label = self.message_type[row]
            if not label.is_checksum_label:
                label.value_type_index = value_type_index
                self.protocol_label_updated.emit(label)
        self.update()
