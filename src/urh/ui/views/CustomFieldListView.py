from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import  QListView

from urh.models.CustomFieldListModel import CustomFieldListModel


class CustomFieldListView(QListView):
    def __init__(self, parent):
        super().__init__(parent)

    def model(self) -> CustomFieldListModel:
        return super().model()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Delete:
            for index in self.selectedIndexes():
                self.model().remove_field_type_at(index.row())
        else:
            super().keyPressEvent(event)
