from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtWidgets import QTableView, QMenu, QAction

from urh.models.PLabelTableModel import PLabelTableModel


class ProtocolLabelTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.delete_action = QAction("Delete selected labels", self)
        self.delete_action.setShortcut(QKeySequence.Delete)
        self.delete_action.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.delete_action.triggered.connect(self.delete_selected_rows)
        self.addAction(self.delete_action)

    def model(self) -> PLabelTableModel:
        return super().model()

    def create_context_menu(self):
        menu = QMenu()
        menu.addAction(self.delete_action)
        return menu

    def contextMenuEvent(self, event):
        self.create_context_menu().exec_(self.mapToGlobal(event.pos()))

    def delete_selected_rows(self):
        rows = [i.row() for i in self.selectedIndexes()]
        for row in sorted(rows, reverse=True):
            self.model().remove_label_at(row)
