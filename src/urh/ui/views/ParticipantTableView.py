from PyQt5.QtCore import pyqtSlot, Qt, QItemSelection, QItemSelectionModel
from PyQt5.QtGui import QKeySequence, QIcon, QContextMenuEvent
from PyQt5.QtWidgets import QTableView, QAction, QMenu

from urh import settings
from urh.models.ParticipantTableModel import ParticipantTableModel
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate


class ParticipantTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.remove_action = QAction("Remove selected participants", self)
        self.remove_action.setShortcut(QKeySequence.Delete)
        self.remove_action.setIcon(QIcon.fromTheme("list-remove"))
        self.remove_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.remove_action.triggered.connect(self.on_remove_action_triggered)
        self.addAction(self.remove_action)

    @property
    def selected_columns(self) -> (int, int):
        selection = self.selectionModel().selection()
        if selection.isEmpty():
            return 0, self.model().columnCount() - 1

        return min([rng.left() for rng in selection]), max(
            [rng.right() for rng in selection]
        )

    def select(self, row_1, col_1, row_2, col_2):
        selection = QItemSelection()
        start_index = self.model().index(row_1, col_1)
        end_index = self.model().index(row_2, col_2)
        selection.select(start_index, end_index)
        self.selectionModel().select(selection, QItemSelectionModel.Select)

    def model(self) -> ParticipantTableModel:
        return super().model()

    def setModel(self, model: ParticipantTableModel):
        if self.model():
            self.model().updated.disconnect()

        super().setModel(model)
        self.model().updated.connect(self.refresh_participant_table)

    def create_context_menu(self):
        menu = QMenu()
        add_action = menu.addAction(QIcon.fromTheme("list-add"), "Add participant")
        add_action.triggered.connect(self.on_add_action_triggered)

        if not self.selectionModel().selection().isEmpty():
            menu.addAction(self.remove_action)
            menu.addSeparator()

            move_up = menu.addAction(
                QIcon.fromTheme("go-up"), "Move selected participants up"
            )
            move_up.triggered.connect(self.on_move_up_action_triggered)
            move_down = menu.addAction(
                QIcon.fromTheme("go-down"), "Move selected participants down"
            )
            move_down.triggered.connect(self.on_move_down_action_triggered)

        return menu

    def contextMenuEvent(self, event: QContextMenuEvent):
        self.create_context_menu().exec_(self.mapToGlobal(event.pos()))

    def refresh_participant_table(self):
        n = len(self.model().participants)
        items = [str(i) for i in range(n)]
        if len(items) >= 2:
            items[0] += " (low)"
            items[-1] += " (high)"

        for row in range(n):
            self.closePersistentEditor(self.model().index(row, 3))

        self.setItemDelegateForColumn(
            2,
            ComboBoxDelegate(
                [""] * len(settings.PARTICIPANT_COLORS),
                colors=settings.PARTICIPANT_COLORS,
                parent=self,
            ),
        )
        self.setItemDelegateForColumn(3, ComboBoxDelegate(items, parent=self))

        for row in range(n):
            self.openPersistentEditor(self.model().index(row, 2))
            self.openPersistentEditor(self.model().index(row, 3))

    @pyqtSlot()
    def on_remove_action_triggered(self):
        self.model().remove_participants(self.selectionModel().selection())

    @pyqtSlot()
    def on_add_action_triggered(self):
        self.model().add_participant()

    @pyqtSlot()
    def on_move_up_action_triggered(self):
        col_start, col_end = self.selected_columns
        start, end = self.model().move_up(self.selectionModel().selection())
        if start is not None and end is not None:
            self.select(start - 1, col_start, end - 1, col_end)

    @pyqtSlot()
    def on_move_down_action_triggered(self):
        col_start, col_end = self.selected_columns
        start, end = self.model().move_down(self.selectionModel().selection())
        if start is not None and end is not None:
            self.select(start + 1, col_start, end + 1, col_end)
