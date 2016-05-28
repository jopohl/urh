from PyQt5.QtCore import QAbstractTableModel, pyqtSignal, Qt, QModelIndex

from urh.signalprocessing.LabelSet import LabelSet
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolGroup import ProtocolGroup


class PLabelTableModel(QAbstractTableModel):
    header_labels = ["Name", "Start", "End", 'Color', 'Apply decoding', 'Delete']

    label_removed = pyqtSignal(ProtocolLabel)

    def __init__(self, labelset: LabelSet, parent=None):
        super().__init__(parent)
        self.row_count = len(labelset)
        self.proto_view = 0
        self.labelset = labelset
        self.layoutChanged.emit()

    def update(self):
        self.row_count = len(self.labelset)
        if self.row_count > 0:
            i1 = self.createIndex(0, 0)
            i2 = self.createIndex(self.row_count-1, len(self.header_labels)-1)
            self.dataChanged.emit(i1, i2)
        self.layoutChanged.emit()

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.header_labels)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.labelset)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            i = index.row()
            j = index.column()
            lbl = self.labelset[i]
            if j == 0:
                return lbl.name
            elif j == 1:
                return self.labelset.get_label_range(lbl, self.proto_view, True)[0] + 1
            elif j == 2:
                return self.labelset.get_label_range(lbl, self.proto_view, True)[1]
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
        if i >= len(self.labelset):
            return False

        lbl = self.labelset[i]

        if j == 0:
            lbl.name = value
        elif j == 1:
            new_start = int(self.labelset.convert_index(int(value) - 1, self.proto_view, 0, True, i)[0])
            lbl.start = new_start
        elif j == 2:
            new_end = int(self.labelset.convert_index(int(value) - 1, self.proto_view, 0, True, i)[1]) + 1
            lbl.end = new_end
        elif j == 3:
            lbl.color_index = value
        elif j == 4:
            lbl.apply_decoding = bool(value)
        elif j == 5:
            self.remove_label(self.labelset[i])

        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        try:
            _ = self.labelset[index.row()]
        except IndexError:
            return Qt.NoItemFlags

        return Qt.ItemIsEditable | Qt.ItemIsEnabled

    def remove_label(self, label):
        self.labelset.remove(label)
        self.update()
        self.label_removed.emit(label)

