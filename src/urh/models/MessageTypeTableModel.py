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
                return message_type.show
            elif index.column() == 1:
                return None
        elif role == Qt.EditRole:
            if index.column() == 0:
                return message_type.name

    def setData(self, index: QModelIndex, value, role=Qt.DisplayRole):
        if role == Qt.CheckStateRole:
            if index.column() == 0:
                message_type = self.message_types[index.row()]
                message_type.show = value
                self.message_type_visibility_changed.emit(message_type)
        elif role == Qt.EditRole:
            if index.column() == 0 and value:
                message_type = self.message_types[index.row()]
                message_type.name = value

        return True

    # Todo: Migrate the following methods to table
    def showAll(self):
        hidden_labels = [label for label in self.proto_analyzer.protocol_labels if not label.show]
        for label in hidden_labels:
            label.show = Qt.Checked
            self.protolabel_visibility_changed.emit(label)

    def hideAll(self):
        visible_labels = [label for label in self.proto_analyzer.protocol_labels if label.show]
        for label in visible_labels:
            label.show = Qt.Unchecked
            self.protolabel_visibility_changed.emit(label)

    def get_label_at(self, row):
        return self.message_type[row]

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
