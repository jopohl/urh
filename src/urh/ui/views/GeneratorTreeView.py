from PyQt5.QtWidgets import QTreeView, QAbstractItemView
from PyQt5.QtCore import QItemSelectionModel

from urh.models.GeneratorTreeModel import GeneratorTreeModel


class GeneratorTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def model(self) -> GeneratorTreeModel:
        return super().model()

    def selectionModel(self) -> QItemSelectionModel:
        return super().selectionModel()