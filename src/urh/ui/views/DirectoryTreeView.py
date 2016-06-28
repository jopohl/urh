from PyQt5.QtGui import QContextMenuEvent, QIcon
from PyQt5.QtWidgets import QTreeView, QInputDialog, QMessageBox, QMenu


class DirectoryTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def create_directory(self):
        index = self.model().mapToSource(self.rootIndex())
        """:type: QModelIndex """

        model = self.model().sourceModel()

        if not index.isValid():
            return

        dir_name, ok = QInputDialog.getText(self, self.tr("Create Directory"), self.tr("Directory name"))

        if ok and len(dir_name) > 0:
            if not model.mkdir(index, dir_name).isValid():
                QMessageBox.information(self, self.tr("Create Directoy"), self.tr("Failed to create the directory"))

    def remove(self):
        index = self.model().mapToSource(self.currentIndex())
        if not index.isValid():
            return

        model = self.model().sourceModel()
        if model.fileInfo(index).isDir():
            ok = model.rmdir(index)
        else:
            ok = model.remove(index)

        if not ok:
            QMessageBox.information(self, self.tr("Remove"),
                                    self.tr("Failed to remove {0}".format(model.fileName(index))))

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu(self)
        newdirAction = menu.addAction("New Directory")
        newdirAction.setIcon(QIcon.fromTheme("folder"))
        delAction = menu.addAction("Delete")
        delAction.setIcon(QIcon.fromTheme("edit-delete"))

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == newdirAction:
            self.create_directory()

        elif action == delAction:
            self.remove()
