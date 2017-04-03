from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex

from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.ui.SimulatorScene import MessageDataItem

class SimulatorMessageFieldModel(QAbstractTableModel):
    header_labels = ['Name', 'Log level', 'Log format', 'Value']

    def __init__(self, controller, parent=None):
        super().__init__(parent)

        self.controller = controller

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
                return MessageDataItem.LOG_LEVELS[lbl.log_level_index]
            elif j == 2:
                return ProtocolLabel.DISPLAY_FORMATS[lbl.display_format_index]
            elif j == 3:
                return lbl.value

    def setData(self, index: QModelIndex, value, role=None):
        if role == Qt.EditRole:
            i, j = index.row(), index.column()
            lbl = self.labels[i]

            try:
                if j == 0:
                    lbl.name = value

                    if value == MessageDataItem.UNLABELED_DATA_NAME:
                        lbl.is_unlabeled_data = True
                        lbl.type = None
                    elif value in self.controller.field_types_by_caption:
                        lbl.is_unlabeled_data = False
                        lbl.type = self.controller.field_types_by_caption[value]
                    else:
                        lbl.is_unlabeled_data = False
                        lbl.type = None
                if j == 1:
                    lbl.log_level_index = int(value)
                elif j == 2:
                    lbl.display_format_index = int(value)
            except ValueError:
                return False

            return True


    def flags(self, index: QModelIndex):
        flags = super().flags(index)
        column = index.column()

        if not column == 3:
            flags |= Qt.ItemIsEditable

        return flags