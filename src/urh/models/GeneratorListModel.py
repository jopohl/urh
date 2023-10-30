from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex, pyqtSignal

from urh import settings
from urh.signalprocessing.Message import Message
from urh.signalprocessing.ProtocoLabel import ProtocolLabel


class GeneratorListModel(QAbstractListModel):
    protolabel_fuzzing_status_changed = pyqtSignal(ProtocolLabel)
    protolabel_removed = pyqtSignal(ProtocolLabel)

    def __init__(self, message: Message, parent=None):
        super().__init__(parent)
        self.__message = message

    @property
    def labels(self):
        if self.message:
            return self.message.message_type
        else:
            return []

    @property
    def message(self):
        return self.__message

    @message.setter
    def message(self, value: Message):
        if value != self.message:
            self.__message = value
            self.update()

    def last_index(self):
        return self.index(len(self.labels) - 1)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.labels)

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if row >= len(self.labels):
            return

        if role == Qt.DisplayRole:
            nfuzzval = len(self.labels[row].fuzz_values)
            nfuzzval = str(nfuzzval - 1) if nfuzzval > 1 else "empty"
            try:
                return self.labels[row].name + " (" + nfuzzval + ")"
            except TypeError:
                return ""
        elif role == Qt.CheckStateRole:
            return self.labels[row].fuzz_me
        elif role == Qt.BackgroundColorRole:
            return settings.LABEL_COLORS[self.labels[row].color_index]

    def setData(self, index: QModelIndex, value, role=Qt.DisplayRole):
        if role == Qt.CheckStateRole:
            proto_label = self.labels[index.row()]
            proto_label.fuzz_me = value
            self.protolabel_fuzzing_status_changed.emit(proto_label)
        elif role == Qt.EditRole:
            if len(value) > 0:
                self.labels[index.row()].name = value
        return True

    def fuzzAll(self):
        unfuzzedLabels = [label for label in self.labels if not label.fuzz_me]
        for label in unfuzzedLabels:
            label.fuzz_me = Qt.Checked
            self.protolabel_fuzzing_status_changed.emit(label)

    def unfuzzAll(self):
        fuzzedLabels = [label for label in self.labels if label.fuzz_me]
        for label in fuzzedLabels:
            label.fuzz_me = Qt.Unchecked
            self.protolabel_fuzzing_status_changed.emit(label)

    def delete_label_at(self, row: int):
        lbl = self.labels[row]
        self.labels.remove(lbl)
        self.protolabel_removed.emit(lbl)

    def update(self):
        self.beginResetModel()
        self.endResetModel()

    def flags(self, index):
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

        try:
            lbl = self.labels[index.row()]
        except IndexError:
            return flags

        if len(lbl.fuzz_values) > 1:
            flags |= Qt.ItemIsUserCheckable
        else:
            lbl.fuzz_me = False
        return flags
