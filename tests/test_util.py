import sys

import os
from PyQt5.QtGui import QIcon

from tests.QtTestCase import QtTestCase
from urh import constants
from urh.util import util


class TestUtil(QtTestCase):
    def test_set_icon_theme(self):
        constants.SETTINGS.setValue("icon_theme_index", 0)
        util.set_icon_theme()

        self.assertEqual(QIcon.themeName(), "oxy")

        constants.SETTINGS.setValue("icon_theme_index", 1)
        util.set_icon_theme()

        if sys.platform == "linux":
            self.assertNotEqual(QIcon.themeName(), "oxy")
        else:
            self.assertEqual(QIcon.themeName(), "oxy")

    def test_set_windows_lib_path(self):
        before = os.environ["PATH"]
        util.set_windows_lib_path()

        if sys.platform == "win32":
            self.assertNotEqual(before, os.environ["PATH"])
        else:
            self.assertEqual(before, os.environ["PATH"])

    def test_create_textbox_dialog(self):
        dialog = util.create_textbox_dialog("Test content", "Test title", parent=self.form)
        self.assertEqual(dialog.windowTitle(), "Test title")
        self.assertEqual(dialog.layout().itemAt(0).widget().toPlainText(), "Test content")
        dialog.close()
