from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex

class SimulatorMessageFieldModel(QAbstractTableModel):
    header_labels = ['Name', 'Value']

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__message = None
        """:type: urh.ui.SimulatorScene.MessageItem"""

    @property
    def message(self):
        return __message

    @message.setter
    def message(self, value):
        self.__message = value
        self.update()

    @property
    def labels(self):
        if self.__message:
            return self.__message.labels
        else:
            return []

    def update(self):
        self.beginResetModel()
        self.endResetModel()

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.header_labels)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.labels)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft

        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            i = index.row()
            j = index.column()
            lbl = self.labels[i]

            if j == 0:
                return lbl.name
            elif j == 1:
                return lbl.value

    def setData(self, index: QModelIndex, value, role=None):
        pass

    def flags(self, index: QModelIndex):
        return super().flags(index)