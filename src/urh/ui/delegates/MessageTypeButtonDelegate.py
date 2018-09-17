from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QStyledItemDelegate, QToolButton

from urh.ui.views.MessageTypeTableView import MessageTypeTableView


class MessageTypeButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        assert isinstance(parent, MessageTypeTableView)
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        button = QToolButton(parent)
        button.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        button.setIcon(QIcon.fromTheme("configure"))
        button.clicked.connect(self.on_btn_clicked)
        return button

    @pyqtSlot()
    def on_btn_clicked(self):
        button = self.sender()
        index = self.parent().indexAt(button.pos())
        if index.isValid():
            self.parent().configure_message_type_rules_triggered.emit(index.row())
