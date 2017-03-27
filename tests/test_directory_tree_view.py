import os

from PyQt5.QtCore import QDir

from tests.QtTestCase import QtTestCase
from urh.models.FileFilterProxyModel import FileFilterProxyModel
from urh.models.FileSystemModel import FileSystemModel
from urh.ui.views.DirectoryTreeView import DirectoryTreeView


class TestDirectoryTreeView(QtTestCase):
    def test_remove_file(self):
        self.directory_tree_view = DirectoryTreeView()
        file_model = FileSystemModel()
        file_model.setRootPath(QDir.tempPath())
        file_proxy_model = FileFilterProxyModel()
        file_proxy_model.setSourceModel(file_model)
        self.directory_tree_view.setModel(file_proxy_model)
        self.directory_tree_view.setRootIndex(file_proxy_model.mapFromSource(file_model.index(QDir.tempPath())))

        menu = self.directory_tree_view.create_context_menu()
        remove_action = next((action for action in menu.actions() if action.text() == "Delete"), None)
        self.assertIsNotNone(remove_action)

        f = os.path.join(QDir.tempPath(), "test")
        open(f, "w").close()
        self.assertTrue(os.path.isfile(f))
        self.directory_tree_view.setCurrentIndex(file_proxy_model.mapFromSource(file_model.index(f)))

        remove_action.trigger()
        self.assertFalse(os.path.isfile(f))
