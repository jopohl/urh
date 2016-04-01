from PyQt5.QtWidgets import QListWidget, QMenu, QAction
from PyQt5.QtGui import QContextMenuEvent, QFocusEvent
from PyQt5.QtCore import pyqtSignal


class GeneratorListWidget(QListWidget):
    item_edit_clicked = pyqtSignal(int)
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

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == edit_action:
            selected_indx = sel_indexes[0]
            self.item_edit_clicked.emit(selected_indx)

    def focusOutEvent(self, event: QFocusEvent):
        self.lost_focus.emit()
        super().focusOutEvent(event)
