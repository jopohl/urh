from PyQt5.QtCore import Qt, QModelIndex, QAbstractTableModel, pyqtSignal

from urh.signalprocessing.MessageType import MessageType


class MessageTypeTableModel(QAbstractTableModel):
    message_type_visibility_changed = pyqtSignal(MessageType)
    message_type_removed = pyqtSignal(MessageType)
    header_labels = ["Name", "Edit"]

    def __init__(self, message_types: list, parent=None):
        super().__init__(parent)
        self.message_types = message_types  # type: list[MessageType]

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.message_types)

    def columnCount(self, parent: QModelIndex = None, *args, **kwargs):
        return len(self.header_labels)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return super().headerData(section, orientation, role)

    def update(self):
        self.beginResetModel()
        self.endResetModel()

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if not index.isValid() or row >= len(self.message_types):
            return

        message_type = self.message_types[row]

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return message_type.name
            elif index.column() == 1:
                return ""
        elif role == Qt.CheckStateRole:
            if index.column() == 0:
                if message_type.show:
                    return Qt.Checked
                else:
                    return Qt.Unchecked
            elif index.column() == 1:
                return None
        elif role == Qt.EditRole:
            if index.column() == 0:
                return message_type.name

    def setData(self, index: QModelIndex, value, role=Qt.DisplayRole):
        if role == Qt.CheckStateRole:
            if index.column() == 0:
                message_type = self.message_types[index.row()]
                message_type.show = bool(value)
                self.message_type_visibility_changed.emit(message_type)
        elif role == Qt.EditRole:
            if index.column() == 0 and value:
                message_type = self.message_types[index.row()]
                message_type.name = value

        return True

    def delete_message_type_at(self, index: int):
        try:
            message_type = self.message_types[index]
            self.message_types.remove(message_type)
            self.message_type_removed.emit(message_type)
        except IndexError:
            pass

    def delete_message_types_at(self, start: int, end: int):
        for row in range(end, start - 1, -1):
            self.delete_message_type_at(row)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable
