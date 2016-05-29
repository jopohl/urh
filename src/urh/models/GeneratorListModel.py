from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex, pyqtSignal
from PyQt5.QtGui import QColor

from urh import constants
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer


class GeneratorListModel(QAbstractListModel):
    protolabel_fuzzing_status_changed = pyqtSignal(ProtocolLabel)
    protolabel_removed = pyqtSignal(ProtocolLabel)

    def __init__(self, proto_container: ProtocolAnalyzerContainer, parent=None):
        super().__init__(parent)
        self.proto_container = proto_container

    def last_index(self):
        return self.index(len(self.proto_container.protocol_labels) - 1)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.proto_container.protocol_labels)

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if row >= len(self.proto_container.protocol_labels):
            return

        if role == Qt.DisplayRole:
            nfuzzval = len(self.proto_container.protocol_labels[row].fuzz_values)
            nfuzzval = str(nfuzzval - 1) if nfuzzval > 1 else "empty"
            try:
                return self.proto_container.protocol_labels[row].name + " (" + nfuzzval + ")"
            except TypeError:
                return ""
        elif role == Qt.CheckStateRole:
            return self.proto_container.protocol_labels[row].fuzz_me
        elif role == Qt.BackgroundColorRole:
            return constants.LABEL_COLORS[self.proto_container.protocol_labels[row].color_index]


    def setData(self, index: QModelIndex, value, role=Qt.DisplayRole):
        if role == Qt.CheckStateRole:
            proto_label = self.proto_container.protocol_labels[index.row()]
            proto_label.fuzz_me = value
            self.protolabel_fuzzing_status_changed.emit(proto_label)
        elif role == Qt.EditRole:
            if len(value) > 0:
                self.proto_container.protocol_labels[index.row()].name = value
        return True

    def fuzzAll(self):
        unfuzzedLabels = [label for label in self.proto_container.protocol_labels if not label.fuzz_me]
        for label in unfuzzedLabels:
            label.fuzz_me = Qt.Checked
            self.protolabel_fuzzing_status_changed.emit(label)

    def unfuzzAll(self):
        fuzzedLabels = [label for label in self.proto_container.protocol_labels if label.fuzz_me]
        for label in fuzzedLabels:
            label.fuzz_me = Qt.Unchecked
            self.protolabel_fuzzing_status_changed.emit(label)

    def delete_label_at(self, row: int):
        lbl = self.proto_container.protocol_labels[row]
        self.proto_container.remove_label(lbl)
        self.protolabel_removed.emit(lbl)

    def update(self):
        self.layoutChanged.emit()

    def flags(self, index):
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

        try:
            lbl = self.proto_container.protocol_labels[index.row()]
        except IndexError:
            return flags

        if len(lbl.fuzz_values) > 1:
            flags |= Qt.ItemIsUserCheckable
        else:
            lbl.fuzz_me = False
        return flags
