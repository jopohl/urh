import os

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QFileIconProvider

from urh import constants


class FileIconProvider(QFileIconProvider):
    def __init__(self):
        super().__init__()

    def icon(self, arg):
        if isinstance(arg, QFileInfo):
            if (arg.isDir() and os.path.isfile(os.path.join(arg.filePath(), constants.PROJECT_FILE))) \
                    or (arg.isFile() and arg.fileName() == constants.PROJECT_FILE):
                return QIcon(":/icons/data/icons/appicon.png")

        return super().icon(arg)
