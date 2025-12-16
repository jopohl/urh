from PyQt6.QtWidgets import QTreeView, QAbstractItemView
from PyQt6.QtCore import QItemSelectionModel

from urh.models.GeneratorTreeModel import GeneratorTreeModel


class GeneratorTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def model(self) -> GeneratorTreeModel:
        return super().model()

    def selectionModel(self) -> QItemSelectionModel:
        return super().selectionModel()
