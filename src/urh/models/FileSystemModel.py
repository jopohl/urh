from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileSystemModel


class FileSystemModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilter(QDir.Files | QDir.Dirs | QDir.NoDotAndDotDot)
        self.setReadOnly(True)

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 2
