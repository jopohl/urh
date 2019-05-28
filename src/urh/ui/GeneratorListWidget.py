from PySide2.QtCore import Signal, Slot
from PySide2.QtGui import QContextMenuEvent, QFocusEvent
from PySide2.QtWidgets import QListWidget, QMenu, QAction


class GeneratorListWidget(QListWidget):
    item_edit_clicked = Signal(int)
    edit_all_items_clicked = Signal()
    lost_focus = Signal()

    def __init__(self, parent):
        super().__init__(parent)

    def create_context_menu(self) -> QMenu:
        menu = QMenu()
        sel_indexes = [index.row() for index in self.selectedIndexes()]
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(self.on_edit_action_triggered)
        if len(sel_indexes) == 0:
            edit_action.setEnabled(False)

        menu.addAction(edit_action)

        if self.count() > 0:
            edit_all_action = QAction("Edit all", self)
            edit_all_action.triggered.connect(self.on_edit_all_action_triggered)
            menu.addAction(edit_all_action)

        return menu

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = self.create_context_menu()
        menu.exec_(self.mapToGlobal(event.pos()))

    def focusOutEvent(self, event: QFocusEvent):
        self.lost_focus.emit()
        super().focusOutEvent(event)

    @Slot()
    def on_edit_action_triggered(self):
        if len(self.selectedIndexes()) > 0:
            selected_indx = self.selectedIndexes()[0].row()
            self.item_edit_clicked.emit(selected_indx)

    @Slot()
    def on_edit_all_action_triggered(self):
        self.edit_all_items_clicked.emit()
