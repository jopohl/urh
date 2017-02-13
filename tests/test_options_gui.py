import os
import unittest

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDropEvent
from PyQt5.QtTest import QTest

import tests.utils_testing
from tests.utils_testing import get_path_for_data_file
from urh import constants
from urh.controller.MainController import MainController
from urh.controller.OptionsController import OptionsController

app = tests.utils_testing.app


class TestOptionsGUI(unittest.TestCase):
    def setUp(self):
        self.form = MainController()
        self.dialog = OptionsController(self.form.plugin_manager.installed_plugins, parent=self.form)
        with open(constants.SETTINGS.fileName(), "r") as f:
            self.settings_content = f.read()

    def tearDown(self):
        with open(constants.SETTINGS.fileName(), "w") as f:
            f.write(self.settings_content)

    def test_interpretation_tab(self):
        self.dialog.ui.tabWidget.setCurrentIndex(0)

        if self.dialog.ui.chkBoxEnableSymbols.isChecked():
            self.assertNotEqual(self.dialog.ui.lSymbolLength.text(), "0%")
        else:
            self.assertEqual(self.dialog.ui.lSymbolLength.text(), "0%")

        self.dialog.ui.chkBoxEnableSymbols.click()

        if self.dialog.ui.chkBoxEnableSymbols.isChecked():
            self.assertNotEqual(self.dialog.ui.lSymbolLength.text(), "0%")
        else:
            self.assertEqual(self.dialog.ui.lSymbolLength.text(), "0%")

        self.dialog.ui.chkBoxEnableSymbols.click()
        if self.dialog.ui.chkBoxEnableSymbols.isChecked():
            self.assertNotEqual(self.dialog.ui.lSymbolLength.text(), "0%")
        else:
            self.assertEqual(self.dialog.ui.lSymbolLength.text(), "0%")

    def test_generation_tab(self):
        self.dialog.ui.tabWidget.setCurrentIndex(0)
        self.assertEqual(self.dialog.ui.checkBoxDefaultFuzzingPause.isChecked(),
                         self.dialog.ui.doubleSpinBoxFuzzingPause.isEnabled())

        self.dialog.ui.checkBoxDefaultFuzzingPause.click()
        self.assertEqual(self.dialog.ui.checkBoxDefaultFuzzingPause.isChecked(),
                         self.dialog.ui.doubleSpinBoxFuzzingPause.isEnabled())

        self.dialog.ui.checkBoxDefaultFuzzingPause.click()
        self.assertEqual(self.dialog.ui.checkBoxDefaultFuzzingPause.isChecked(),
                         self.dialog.ui.doubleSpinBoxFuzzingPause.isEnabled())