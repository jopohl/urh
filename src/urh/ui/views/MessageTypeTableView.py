from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot
from PyQt5.QtGui import QContextMenuEvent, QKeySequence, QIcon
from PyQt5.QtWidgets import QAbstractItemView, QMenu, QAction, QTableView

from urh.models.MessageTypeTableModel import MessageTypeTableModel


class MessageTypeTableView(QTableView):
    auto_message_type_update_triggered = pyqtSignal()
    configure_message_type_rules_triggered = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)

        self.del_rows_action = QAction("Delete selected message types", self)
        self.del_rows_action.setShortcut(QKeySequence.Delete)
        self.del_rows_action.setIcon(QIcon.fromTheme("edit-delete"))
        self.del_rows_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.del_rows_action.triggered.connect(self.delete_rows)

        self.addAction(self.del_rows_action)

    def model(self) -> MessageTypeTableModel:
        return super().model()

    def open_persistent_editor(self, column=1):
        for row in range(self.model().rowCount()):
            self.openPersistentEditor(self.model().index(row, column))

    def selection_range(self):
        """
        :rtype: int, int
        """
        selected = self.selectionModel().selection()
        """:type: QItemSelection """

        if selected.isEmpty():
            return -1, -1

        min_row = min(rng.top() for rng in selected)
        max_row = max(rng.bottom() for rng in selected)

        return min_row, max_row

    def create_context_menu(self):
        menu = QMenu()

        if self.model().rowCount() > 1:
            menu.addAction(self.del_rows_action)

        menu.addSeparator()
        update_message_types_action = menu.addAction(
            "Update automatically assigned message types"
        )
        update_message_types_action.setIcon(QIcon.fromTheme("view-refresh"))
        update_message_types_action.triggered.connect(
            self.auto_message_type_update_triggered.emit
        )

        menu.addSeparator()
        show_all_action = menu.addAction("Show all message types")
        show_all_action.triggered.connect(self.on_show_all_action_triggered)
        hide_all_action = menu.addAction("Hide all message types")
        hide_all_action.triggered.connect(self.on_hide_all_action_triggered)

        return menu

    def contextMenuEvent(self, event: QContextMenuEvent):
        self.create_context_menu().exec_(self.mapToGlobal(event.pos()))

    def delete_rows(self):
        min_row, max_row = self.selection_range()
        if min_row > -1:
            # prevent default message type from being deleted
            min_row = max(1, min_row)
            self.model().delete_message_types_at(min_row, max_row)

    @pyqtSlot()
    def on_show_all_action_triggered(self):
        for i in range(self.model().rowCount()):
            self.model().setData(
                self.model().index(i, 0), Qt.Checked, role=Qt.CheckStateRole
            )

    @pyqtSlot()
    def on_hide_all_action_triggered(self):
        for i in range(self.model().rowCount()):
            self.model().setData(
                self.model().index(i, 0), Qt.Unchecked, role=Qt.CheckStateRole
            )
