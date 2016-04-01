from PyQt5.QtCore import QModelIndex, pyqtSlot
from PyQt5.QtWidgets import QItemDelegate, QWidget, QStyleOptionViewItem, QPushButton


class DeleteButtonDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.enabled = True

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        editor = QPushButton(parent)
        editor.setText("Delete")
        editor.clicked.connect(self.clicked)
        return editor

    @pyqtSlot()
    def clicked(self):
        self.commitData.emit(self.sender())