import math
from PyQt5.QtCore import QAbstractTableModel, pyqtSignal, Qt, QModelIndex

from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Message import Message
from urh.signalprocessing.ProtocolGroup import ProtocolGroup


class PLabelTableModel(QAbstractTableModel):
    header_labels = ["Name", "Start", "End", 'Color', 'Apply decoding', 'Delete']

    label_removed = pyqtSignal(ProtocolLabel)
    apply_decoding_changed = pyqtSignal(ProtocolLabel)

    def __init__(self, message_type: MessageType, parent=None):
        super().__init__(parent)
        self.row_count = len(message_type)
        self.proto_view = 0
        self.message_type = message_type
        self.layoutChanged.emit()


    def __index2bit(self, index: int, from_view: int):
        return index if from_view == 0 else 4 * index if from_view == 1 else 8 * index

    def __bit2index(self, index: int, to_view: int):
        return index if to_view == 0 else int(math.ceil(index / 4)) if to_view == 1 else int(math.ceil(index / 8))

    def update(self):
        self.row_count = len(self.message_type)
        if self.row_count > 0:
            i1 = self.createIndex(0, 0)
            i2 = self.createIndex(self.row_count-1, len(self.header_labels)-1)
            self.dataChanged.emit(i1, i2)
        self.layoutChanged.emit()

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.header_labels)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.message_type)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            i = index.row()
            j = index.column()
            lbl = self.message_type[i]
            if j == 0:
                return lbl.name
            elif j == 1:
                return self.__bit2index(lbl.start, self.proto_view) + 1
            elif j == 2:
                return self.__bit2index(lbl.end, self.proto_view)
            elif j == 3:
                return lbl.color_index
            elif j == 4:
                return lbl.apply_decoding
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        else:
            return None

    def setData(self, index: QModelIndex, value, role=Qt.DisplayRole):
        if value == "":
            return True

        i = index.row()
        j = index.column()
        if i >= len(self.message_type):
            return False

        lbl = self.message_type[i]

        if j == 0:
            lbl.name = value
        elif j == 1:
            lbl.start = self.__index2bit(int(value) - 1, self.proto_view)
        elif j == 2:
            lbl.end = self.__index2bit((int(value) - 1), self.proto_view) + 1
        elif j == 3:
            lbl.color_index = value
        elif j == 4:
            if bool(value) != lbl.apply_decoding:
                lbl.apply_decoding = bool(value)
                self.apply_decoding_changed.emit(lbl)
        elif j == 5:
            self.remove_label(self.message_type[i])

        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        try:
            _ = self.message_type[index.row()]
        except IndexError:
            return Qt.NoItemFlags

        return Qt.ItemIsEditable | Qt.ItemIsEnabled

    def remove_label(self, label):
        self.message_type.remove(label)
        self.update()
        self.label_removed.emit(label)