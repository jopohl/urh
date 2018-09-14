from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QContextMenuEvent, QKeySequence, QIcon
from PyQt5.QtWidgets import QAbstractItemView, QMenu, QAction, QTableView

from urh.models.MessageTypeTableModel import MessageTypeTableModel


class MessageTypeTableView(QTableView):
    # TODO: Review methods when integrated
    configureActionTriggered = pyqtSignal()
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

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu()
        pos = event.pos()
        index = self.indexAt(pos)
        min_row, max_row = self.selection_range()

        assign_actions = []
        message_type_names = []

        if min_row > -1:
            menu.addAction(self.del_rows_action)
            message_type_names = [mt.name for mt in self.model().message_types]

        menu.addSeparator()
        show_all_action = menu.addAction("Show all")
        hide_all_action = menu.addAction("Hide all")

        menu.addSeparator()
        update_message_types_action = menu.addAction("Update automatically assigned message types")
        update_message_types_action.setIcon(QIcon.fromTheme("view-refresh"))
        configure_action = menu.addAction("Configure field types...")

        action = menu.exec_(self.mapToGlobal(pos))

        if action == show_all_action:
            self.model().showAll()
        elif action == hide_all_action:
            self.model().hideAll()
        elif action == configure_action:
            self.configureActionTriggered.emit()
        elif action == update_message_types_action:
            self.auto_message_type_update_triggered.emit()
        elif action in assign_actions:
            message_type_id = message_type_names.index(action.text())
            self.model().add_labels_to_message_type(min_row, max_row, message_type_id)

    def delete_rows(self):
        min_row, max_row = self.selection_range()
        if min_row > -1:
            self.model().delete_message_types_at(min_row, max_row)
