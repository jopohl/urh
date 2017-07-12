from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QContextMenuEvent, QFocusEvent
from PyQt5.QtWidgets import QListWidget, QMenu, QAction


class GeneratorListWidget(QListWidget):
    item_edit_clicked = pyqtSignal(int)
    edit_all_items_clicked = pyqtSignal()
    lost_focus = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu()
        sel_indexes = [index.row() for index in self.selectedIndexes()]
        edit_action = QAction("Edit", self)
        if len(sel_indexes) == 0:
            edit_action.setEnabled(False)

        menu.addAction(edit_action)

        if self.count() > 0:
            edit_all_action = QAction("Edit all", self)
            edit_all_action.triggered.connect(self.on_edit_all_action_triggered)
            menu.addAction(edit_all_action)

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == edit_action:
            selected_indx = sel_indexes[0]
            self.item_edit_clicked.emit(selected_indx)

    def focusOutEvent(self, event: QFocusEvent):
        self.lost_focus.emit()
        super().focusOutEvent(event)

    @pyqtSlot()
    def on_edit_all_action_triggered(self):
        self.edit_all_items_clicked.emit()
