from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QTableView, QMenu

from urh.models.PLabelTableModel import PLabelTableModel


class ProtocolLabelTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def model(self) -> PLabelTableModel:
        return super().model()

    def contextMenuEvent(self, event):
        menu = QMenu()
        pos = event.pos()
        row = self.rowAt(pos.y())
        if row != -1:
            delAction = menu.addAction("Delete Protocol Label")
            action = menu.exec_(self.mapToGlobal(pos))
            if action == delAction:
                lbl = self.model().proto_analyzer.protocol_labels[row]
                self.model().remove_label(lbl)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Delete:
            # Delete selected rows
            rows = [i.row() for i in self.selectedIndexes()]
            for row in sorted(rows, reverse=True):
                self.model().remove_label_at(row)
        else:
            event.accept()