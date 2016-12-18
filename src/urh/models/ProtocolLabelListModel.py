from PyQt5.QtCore import QAbstractListModel, pyqtSignal, Qt, QModelIndex, QMimeData

from urh import constants
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer


class ProtocolLabelListModel(QAbstractListModel):
    protolabel_visibility_changed = pyqtSignal(ProtocolLabel)
    protolabel_type_edited = pyqtSignal()
    label_removed = pyqtSignal(ProtocolLabel)

    def __init__(self, proto_analyzer: ProtocolAnalyzer, controller, parent=None):
        super().__init__(parent)
        self.proto_analyzer = proto_analyzer
        self.message_type = controller.active_message_type
        """:type urh.signalprocessing.MessageType.MessageType"""

        self.controller = controller
        """:type: urh.controller.CompareFrameController.CompareFrameController"""

        self.field_types = [t for t in ProtocolLabel.Type if t.value] # without custom

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.message_type)

    def update(self):
        self.message_type = self.controller.active_message_type
        """:type: urh.signalprocessing.MessageType.MessageType """
        self.layoutChanged.emit()


    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if row >= len(self.message_type):
            return

        if role == Qt.DisplayRole:
            return self.message_type[row].title
        elif role == Qt.CheckStateRole:
            return self.message_type[row].show
        elif role == Qt.BackgroundColorRole:
            return constants.LABEL_COLORS[self.message_type[row].color_index]


    def setData(self, index: QModelIndex, value, role=Qt.DisplayRole):
        if role == Qt.CheckStateRole:
            proto_label = self.message_type[index.row()]
            proto_label.show = value
            self.protolabel_visibility_changed.emit(proto_label)
        elif role == Qt.EditRole:
            proto_label = self.message_type[index.row()]
            try:
                field_type = self.field_types[value]
                proto_label.type = field_type
                proto_label.name = field_type.value
            except IndexError:
                proto_label.type = ProtocolLabel.Type.CUSTOM
                proto_label.name = self.message_type.custom_field_types[value - len(self.field_types)]

            self.protolabel_type_edited.emit()

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
        return self.message_type[row]

    def delete_label_at(self, label_id: int):
        try:
            lbl = self.message_type[label_id]
            self.message_type.remove(lbl)
            self.label_removed.emit(lbl)
        except IndexError:
            pass

    def delete_labels_at(self, start: int, end: int):
        for row in range(end, start-1, -1):
            self.delete_label_at(row)

    def add_labels_to_message_type(self, start: int, end: int, message_type_id: int):
        for lbl in self.message_type[start:end+1]:
            self.controller.proto_analyzer.message_types[message_type_id].add_label(lbl)
        self.controller.updateUI(resize_table=False)

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