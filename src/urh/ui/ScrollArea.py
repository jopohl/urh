from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QDropEvent, QDragEnterEvent, QWheelEvent
from PyQt5.QtWidgets import QScrollArea

class ScrollArea(QScrollArea):
    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dropEvent(self, event: QDropEvent):
        self.files_dropped.emit(event.mimeData().urls())

    def dragEnterEvent(self, event: QDragEnterEvent):
        event.accept()

    def wheelEvent(self, event: QWheelEvent):
        event.ignore()
