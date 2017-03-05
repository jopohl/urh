from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QContextMenuEvent, QIcon
from PyQt5.QtWidgets import QTreeView, QInputDialog, QMessageBox, QMenu


class DirectoryTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def create_directory(self):
        index = self.model().mapToSource(self.rootIndex())  # type: QModelIndex

        if not index.isValid():
            return

        model = self.model().sourceModel()
        dir_name, ok = QInputDialog.getText(self, self.tr("Create Directory"), self.tr("Directory name"))

        if ok and len(dir_name) > 0:
            if not model.mkdir(index, dir_name).isValid():
                QMessageBox.information(self, self.tr("Create Directoy"), self.tr("Failed to create the directory"))

    def remove(self):
        index = self.model().mapToSource(self.currentIndex())  # type: QModelIndex
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

    def create_context_menu(self) -> QMenu:
        menu = QMenu(self)
        new_dir_action = menu.addAction("New Directory")
        new_dir_action.setIcon(QIcon.fromTheme("folder"))
        new_dir_action.triggered.connect(self.create_directory)

        del_action = menu.addAction("Delete")
        del_action.setIcon(QIcon.fromTheme("edit-delete"))
        del_action.triggered.connect(self.remove)

        return menu

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = self.create_context_menu()
        menu.exec_(self.mapToGlobal(event.pos()))
