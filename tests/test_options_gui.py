import unittest

from PyQt5.QtCore import QModelIndex

import tests.utils_testing
from urh.controller.MainController import MainController
from urh.controller.OptionsController import OptionsController
from urh.models.PluginListModel import PluginListModel
from urh.plugins.PluginManager import PluginManager

app = tests.utils_testing.app


class TestOptionsGUI(unittest.TestCase):
    def setUp(self):
        self.form = MainController()
        self.dialog = OptionsController(self.form.plugin_manager.installed_plugins, parent=self.form)

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

    def test_plugins_tab(self):
        self.dialog.ui.tabWidget.setCurrentIndex(4)
        self.assertEqual(self.dialog.ui.tabWidget.tabText(4), "Plugins")

        list_view = self.dialog.plugin_controller.ui.listViewPlugins
        model = list_view.model()
        self.assertIsInstance(model, PluginListModel)
        self.assertEqual(model.rowCount(), len(PluginManager().installed_plugins))

        for i in range(model.rowCount()):
            descr = self.dialog.plugin_controller.ui.txtEditPluginDescription.toPlainText()
            list_view.setCurrentIndex(model.index(i, 0))
            self.assertNotEqual(descr, self.dialog.plugin_controller.ui.txtEditPluginDescription.toPlainText())


    def test_device_tab(self):
        self.dialog.ui.tabWidget.setCurrentIndex(5)
        self.assertEqual(self.dialog.ui.tabWidget.tabText(5), "Device")
        use_custom_site_packages = self.dialog.ui.checkBoxCustomSitePackagePath.isChecked()
        self.assertEqual(self.dialog.ui.lineEditCustomSitePackagePath.isEnabled(), use_custom_site_packages)
        self.dialog.ui.checkBoxCustomSitePackagePath.click()
        self.assertNotEqual(self.dialog.ui.checkBoxCustomSitePackagePath.isChecked(), use_custom_site_packages)
        self.assertNotEqual(self.dialog.ui.lineEditCustomSitePackagePath.isEnabled(), use_custom_site_packages)

        if not self.dialog.ui.checkBoxCustomSitePackagePath.isChecked():
            self.dialog.ui.checkBoxCustomSitePackagePath.click()

        self.assertTrue(self.dialog.ui.lineEditCustomSitePackagePath.isEnabled())

