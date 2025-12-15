from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtGui import QIcon

from urh.models.ProtocolTreeModel import ProtocolTreeModel


class GeneratorTreeModel(ProtocolTreeModel):
    def __init__(self, controller, parent=None):
        super().__init__(controller, parent)

    def set_root_item(self, root_item):
        self.rootItem = root_item

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemFlag.ItemIsEnabled

        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
        )

    def mimeTypes(self):
        return []  # Prohibit Drag Drop in Generator

    def data(self, index: QModelIndex, role=None):
        item = self.getItem(index)
        if role == Qt.ItemDataRole.DisplayRole:  #
            return item.data()
        elif role == Qt.ItemDataRole.DecorationRole and item.is_group:
            return QIcon.fromTheme("folder")
