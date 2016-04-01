from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QContextMenuEvent
from PyQt5.QtWidgets import QListWidget, QMenu

from urh import constants


class ListWidget(QListWidget):
    internalMove = pyqtSignal()
    deleteElement = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.installEventFilter(self)
        self.active_element = 0
        self.active_element_text = ""
        # self.new_element = 0
        # self.new_element_pos = 0

    def internalMoveSignal(self):
        self.internalMove.emit()

    def deleteElementSignal(self):
        self.deleteElement.emit()

    def dragEnterEvent(self, event: QDragEnterEvent):
        self.active_element = self.indexAt(event.pos()).row()
        event.accept()
        super().dragEnterEvent(event)

    def eventFilter(self, sender, event):
        if event.type() == QEvent.ChildRemoved:
            ListWidget.internalMoveSignal(self)
        elif event.type() == QEvent.KeyPress and (event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace):
            item = self.currentRow()
            item_name = self.currentItem().text()
            self.active_element_text = item_name
            self.takeItem(item)
            ListWidget.deleteElementSignal(self)
        return False

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu()
        item = self.indexAt(event.pos()).row()
        if item < 0:
            return

        item_name = self.item(item).text()

        # Menu Entries
        rmFunction = menu.addAction(self.tr("Delete"))
        if constants.DECODING_DISABLED_PREFIX in item_name:
            disableFunction = menu.addAction(self.tr("Enable"))
        else:
            disableFunction = menu.addAction(self.tr("Disable"))
        menu.addSeparator()
        clearAll = menu.addAction(self.tr("Clear All"))

        # Menu Actions
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == rmFunction:
            self.active_element_text = item_name
            self.takeItem(item)
            ListWidget.deleteElementSignal(self)
        elif action == clearAll:
            while self.count() > 0:
                self.takeItem(0)
            ListWidget.deleteElementSignal(self)
        elif action == disableFunction:
            if constants.DECODING_DISABLED_PREFIX in item_name:
                item_name = item_name[len(constants.DECODING_DISABLED_PREFIX):]
            else:
                item_name = constants.DECODING_DISABLED_PREFIX + item_name
            self.takeItem(item)
            self.insertItem(item, item_name)
            ListWidget.internalMoveSignal(self)
