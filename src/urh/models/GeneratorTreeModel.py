from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QModelIndex, Qt

from urh import constants
from urh.models.ProtocolTreeModel import ProtocolTreeModel


class GeneratorTreeModel(ProtocolTreeModel):
    def __init__(self, controller, parent=None):
        super().__init__(controller, parent)

    def set_root_item(self, root_item):
        self.rootItem = root_item

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemIsEnabled

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

    def mimeTypes(self):
        return [] # Prohibit Drag Drop in Generator

    def data(self, index: QModelIndex, role=None):
        item = self.getItem(index)
        if role == Qt.DisplayRole:#
            return item.data()
        elif role == Qt.DecorationRole and item.is_group:
            return QIcon.fromTheme("folder")