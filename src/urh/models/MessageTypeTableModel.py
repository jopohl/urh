from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex

from urh.signalprocessing.MessageType import MessageType


class MessageTypeTableModel(QAbstractListModel):
    def __init__(self, message_types: list, parent=None):
        super().__init__(parent)
        self.message_types = message_types  # type: list[MessageType]

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.message_types)

    def columnCount(self, parent: QModelIndex = ...):
        return 1

    def update(self):
        self.beginResetModel()
        self.endResetModel()

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if not index.isValid() or row >= len(self.message_types):
            return

        message_type = self.message_types[row]

        if role == Qt.DisplayRole:
            return message_type.name
        elif role == Qt.CheckStateRole:
            return message_type.show

    def setData(self, index: QModelIndex, value, role=Qt.DisplayRole):
        if role == Qt.CheckStateRole:
            message_type = self.message_types[index.row()]
            message_type.show = value
            self.protolabel_visibility_changed.emit(proto_label)
        elif role == Qt.EditRole:
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

    def delete_label_at(self, label_id: int):
        try:
            lbl = self.message_type[label_id]
            self.message_type.remove(lbl)
            self.label_removed.emit(lbl)
        except IndexError:
            pass

    def delete_labels_at(self, start: int, end: int):
        for row in range(end, start - 1, -1):
            self.delete_label_at(row)

    def add_labels_to_message_type(self, start: int, end: int, message_type_id: int):
        for lbl in self.message_type[start:end + 1]:
            self.controller.proto_analyzer.message_types[message_type_id].add_label(lbl)
        self.controller.updateUI(resize_table=False)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable
