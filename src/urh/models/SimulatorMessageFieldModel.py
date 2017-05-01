from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, pyqtSignal
from PyQt5.QtGui import QFont

from urh.signalprocessing.SimulatorMessage import SimulatorMessage
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel

class SimulatorMessageFieldModel(QAbstractTableModel):
    header_labels = ['Name', 'Value type', 'Value']

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

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        i, j = index.row(), index.column()
        label = self.message_type[i]

        if role == Qt.DisplayRole:
            if j == 0:
                return label.name
            elif j == 1:
                return label.VALUE_TYPES[label.value_type_index]
            elif j == 2:
                return label.value
        elif role == Qt.FontRole:
            if j == 0:
                font = QFont()
                font.setItalic(label.type is None)
                return font
        elif role == Qt.EditRole:
            if j == 2:
                return label.value

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
                label.value_type_index = value
            elif j == 2:
                label.value = value

            self.protocol_label_updated.emit(label)

        return True

    def flags(self, index: QModelIndex):
        flags = super().flags(index)
        #column = index.column()

        #if column == 0 or column == 1:
        flags |= Qt.ItemIsEditable

        return flags