from PyQt6.QtCore import QDir
from PyQt6.QtGui import QFileSystemModel


class FileSystemModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilter(
            QDir.Filter.Files | QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot
        )
        self.setReadOnly(True)

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 2
