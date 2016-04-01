from PyQt5.QtWidgets import QTreeView
from PyQt5.QtCore import pyqtSignal, QItemSelectionModel

from urh.models import GeneratorTreeModel


class ModulatorTreeView(QTreeView):
    selection_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def model(self) -> GeneratorTreeModel:
        return super().model()

    def selectionModel(self) -> QItemSelectionModel:
        return super().selectionModel()

    def selectionChanged(self, QItemSelection, QItemSelection_1):
        self.selection_changed.emit()
        super().selectionChanged(QItemSelection, QItemSelection_1)