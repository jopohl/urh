from PyQt5.QtCore import QAbstractListModel, pyqtSignal, Qt, QModelIndex, QMimeData
from PyQt5.QtGui import QFont

from urh import constants
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer


class ProtocolLabelListModel(QAbstractListModel):
    protolabel_visibility_changed = pyqtSignal(ProtocolLabel)
    label_removed = pyqtSignal(ProtocolLabel)

    def __init__(self, proto_analyzer: ProtocolAnalyzer, controller, parent=None):
        super().__init__(parent)
        self.proto_analyzer = proto_analyzer
        self.proto_labels = controller.active_labelset
        self.selected_labels = []
        self.controller = controller

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.proto_labels)

    def update(self):
        self.proto_labels = self.controller.active_labelset
        self.layoutChanged.emit()


    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if row >= len(self.proto_labels):
            return

        if role == Qt.DisplayRole:
            return self.proto_labels[row].name
        elif role == Qt.CheckStateRole:
            return self.proto_labels[row].show
        elif role == Qt.BackgroundColorRole:
            return constants.LABEL_COLORS[self.proto_labels[row].color_index]
        elif role == Qt.FontRole and self.proto_labels[row] in self.selected_labels:
            font = QFont()
            font.setBold(True)
            return font


    def setData(self, index: QModelIndex, value, role=Qt.DisplayRole):
        if role == Qt.CheckStateRole:
            proto_label = self.proto_labels[index.row()]
            proto_label.show = value
            self.protolabel_visibility_changed.emit(proto_label)
        elif role == Qt.EditRole:
            if len(value) > 0:
                proto_label = self.proto_labels[index.row()]
                proto_label.name = value
        return True

    def showAll(self):
        hiddenLabels = [label for label in self.proto_analyzer.protocol_labels if not label.show]
        for label in hiddenLabels:
            label.show = Qt.Checked
            self.protolabel_visibility_changed.emit(label)

    def hideAll(self):
        visibleLabels = [label for label in self.proto_analyzer.protocol_labels if label.show]
        for label in visibleLabels:
            label.show = Qt.Unchecked
            self.protolabel_visibility_changed.emit(label)

    def get_label_at(self, row):
        return self.proto_labels[row]

    def delete_label_at(self, label_id: int):
        try:
            lbl = self.proto_labels[label_id]
            for group in self.controller.active_groups:
                group.remove_label(lbl)
            self.label_removed.emit(lbl)
        except IndexError:
            pass

    def delete_labels_at(self, start: int, end: int):
        for row in range(end, start-1, -1):
            self.delete_label_at(row)

    def add_labels_to_labelset(self, start: int, end: int, group_id: int):
        pass # TODO
        #self.controller.add_labels_to_labelset(list(range(start, end + 1)), group_id)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable |\
               Qt.ItemIsEditable | Qt.ItemIsDragEnabled

    def supportedDragActions(self):
        return Qt.MoveAction | Qt.CopyAction

    def mimeTypes(self):
        return['text/plain']

    def mimeData(self, indexes):
        data = "PLabels:"
        data += "/".join([str(index.row()) for index in indexes])
        mimeData = QMimeData()
        mimeData.setText(data)
        return mimeData