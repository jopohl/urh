from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, pyqtSignal
from PyQt5.QtGui import QFont

from urh.signalprocessing.SimulatorMessage import SimulatorMessage
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel

class SimulatorMessageFieldModel(QAbstractTableModel):
    header_labels = ['Name', 'Value']

    protocol_label_updated = pyqtSignal(SimulatorProtocolLabel)

    def __init__(self, controller, parent=None):
        super().__init__(parent)

        self.controller = controller # type: SimulatorTabController

        self.__message = None
        """:type: urh.signalprocessing.SimulatorMessage"""

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
            return self.__message.message_type
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

        i = index.row()
        j = index.column()
        lbl = self.labels[i]

        if role == Qt.DisplayRole:
            if j == 0:
                return lbl.name
            elif j == 1:
                return "1::seq"
        elif role == Qt.FontRole:
            if j == 0:
                font = QFont()
                font.setItalic(lbl.type is None)
                return font

    def setData(self, index: QModelIndex, value, role=None):
        if role == Qt.EditRole:
            i, j = index.row(), index.column()
            lbl = self.labels[i]

            if j == 0:
                lbl.name = value

                if value in self.controller.field_types_by_caption:
                    lbl.type = self.controller.field_types_by_caption[value]
                else:
                    lbl.type = None

                self.protol_label_updated.emit(lbl)

        return True

    def flags(self, index: QModelIndex):
        flags = super().flags(index)
        column = index.column()

        if column == 0:
            flags |= Qt.ItemIsEditable

        return flags