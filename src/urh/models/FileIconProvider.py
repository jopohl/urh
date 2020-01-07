import os

from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileIconProvider

from urh import settings


class FileIconProvider(QFileIconProvider):
    def __init__(self):
        super().__init__()

    def icon(self, arg):
        if isinstance(arg, QFileInfo):
            try:
                if (arg.isDir() and os.path.isfile(os.path.join(arg.filePath(), settings.PROJECT_FILE))) \
                        or (arg.isFile() and arg.fileName() == settings.PROJECT_FILE):
                    return QIcon(":/icons/icons/appicon.png")
            except:
                # In some environments (e.g. docker) there tend to be encoding errors
                pass

        return super().icon(arg)
