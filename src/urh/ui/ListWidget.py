from PyQt5.QtCore import Qt, QEvent, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QDragEnterEvent, QContextMenuEvent, QIcon
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
        self.context_menu_pos = None

    def dragEnterEvent(self, event: QDragEnterEvent):
        self.active_element = self.indexAt(event.pos()).row()
        event.accept()
        super().dragEnterEvent(event)

    def eventFilter(self, sender, event):
        if event.type() == QEvent.ChildRemoved:
            self.internalMove.emit()
        elif event.type() == QEvent.KeyPress and (event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace):
            item = self.currentRow()
            item_name = self.currentItem().text()
            self.active_element_text = item_name
            self.takeItem(item)
            self.deleteElement.emit()
        return False

    def create_context_menu(self):
        menu = QMenu()
        item = self.indexAt(self.context_menu_pos).row()
        if item < 0:
            return menu

        item_name = self.item(item).text()

        # Menu Entries
        rm_action = menu.addAction(self.tr("Delete"))
        rm_action.setIcon(QIcon.fromTheme("list-remove"))
        rm_action.triggered.connect(self.on_rm_action_triggered)
        if constants.DECODING_DISABLED_PREFIX in item_name:
            disable_function = menu.addAction(self.tr("Enable"))
        else:
            disable_function = menu.addAction(self.tr("Disable"))

        disable_function.triggered.connect(self.on_disable_function_triggered)

        menu.addSeparator()
        clear_all_action = menu.addAction(self.tr("Clear All"))
        clear_all_action.triggered.connect(self.on_clear_all_action_triggered)
        return menu

    def contextMenuEvent(self, event: QContextMenuEvent):
        self.context_menu_pos = event.pos()
        menu = self.create_context_menu()
        menu.exec_(self.mapToGlobal(event.pos()))
        self.context_menu_pos = None

    @pyqtSlot()
    def on_rm_action_triggered(self):
        item = self.indexAt(self.context_menu_pos).row()
        item_name = self.item(item).text()
        self.active_element_text = item_name
        self.takeItem(item)
        self.deleteElement.emit()

    @pyqtSlot()
    def on_disable_function_triggered(self):
        item = self.indexAt(self.context_menu_pos).row()
        item_name = self.item(item).text()
        if constants.DECODING_DISABLED_PREFIX in item_name:
            item_name = item_name[len(constants.DECODING_DISABLED_PREFIX):]
        else:
            item_name = constants.DECODING_DISABLED_PREFIX + item_name
        self.takeItem(item)
        self.insertItem(item, item_name)
        self.internalMove.emit()

    @pyqtSlot()
    def on_clear_all_action_triggered(self):
        while self.count() > 0:
            self.takeItem(0)
        self.deleteElement.emit()
