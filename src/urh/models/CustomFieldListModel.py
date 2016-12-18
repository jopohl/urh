from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex


class CustomFieldListModel(QAbstractListModel):
    def __init__(self, message_type, parent=None):
        """
        :type message_type: urh.signalprocessing.MessageType.MessageType
        """
        super().__init__(parent)
        self.custom_field_types = message_type.custom_field_types

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.custom_field_types)

    def data(self, index: QModelIndex, role=None):
        row = index.row()
        if role == Qt.DisplayRole:
            try:
                return self.custom_field_types[row]
            except IndexError:
                return None

    def add_field_type(self, field_type: str):
        if field_type not in self.custom_field_types:
            self.custom_field_types.append(field_type)
            self.layoutChanged.emit()

    def setData(self, index: QModelIndex, value, role=Qt.DisplayRole):
        if role == Qt.EditRole:
            if len(value) > 0:
                try:
                    self.custom_field_types[index.row()] = value
                except IndexError:
                    return True
        return True

    def remove_field_type_at(self, index: int):
        try:
            self.custom_field_types.remove(self.custom_field_types[index])
            self.layoutChanged.emit()
        except (ValueError, IndexError):
            pass


    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable