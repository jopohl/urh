from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from urh.signalprocessing.ProtocoLabel import ProtocolLabel

from urh.signalprocessing.FieldType import FieldType


class FieldTypeTableModel(QAbstractTableModel):
    header_labels = ["Caption", "Function", "Default display type"]

    def __init__(self, fieldtypes, parent=None):
        """

        :type fieldtypes: list of FieldType
        :param parent:
        """
        self.field_types = fieldtypes
        super().__init__(parent)

    def update(self):
        self.beginResetModel()
        self.endResetModel()

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.header_labels)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.field_types)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole or role == Qt.EditRole:
            i = index.row()
            j = index.column()
            fieldtype = self.field_types[i]

            if j == 0:
                return fieldtype.caption
            elif j == 1:
                return fieldtype.function.name
            elif j == 2:
                return ProtocolLabel.DISPLAY_FORMATS[fieldtype.display_format_index]

    def setData(self, index: QModelIndex, value, role=None):
        if role == Qt.EditRole:
            i, j = index.row(), index.column()
            fieldtype = self.field_types[i]
            try:
                if j == 0:
                    present_captions = {ft.caption for ft in self.field_types}
                    if value not in present_captions:
                        fieldtype.caption = value
                elif j == 1:
                    try:
                        fieldtype.function = FieldType.Function[value]
                    except KeyError:
                        return False
                if j == 2:
                    fieldtype.display_format_index = int(value)
            except ValueError:
                return False

            return True

    def flags(self, index: QModelIndex):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
