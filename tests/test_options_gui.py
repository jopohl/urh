import sys
import unittest

import sip
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from urh.controller.MainController import MainController
from urh.controller.OptionsController import OptionsController
from urh.models.PluginListModel import PluginListModel
from urh.plugins.PluginManager import PluginManager

class TestOptionsGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
        sip.delete(cls.app)

    def setUp(self):
        self.form = MainController()
        self.dialog = OptionsController(self.form.plugin_manager.installed_plugins, parent=self.form)

    def tearDown(self):
        self.form.close_all()
        self.dialog.close()
        QApplication.instance().processEvents()
        QTest.qWait(1)

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

        self.dialog.ui.listWidgetDevices.setCurrentRow(0)
        dev_name = self.dialog.ui.listWidgetDevices.currentItem().text()
        for i in range(1, self.dialog.ui.listWidgetDevices.count()):
            self.dialog.ui.listWidgetDevices.setCurrentRow(i)
            self.assertNotEqual(dev_name, self.dialog.ui.listWidgetDevices.currentItem().text())
            dev_name = self.dialog.ui.listWidgetDevices.currentItem().text()

        self.dialog.ui.radioButtonPython2Interpreter.click()

        self.assertTrue(self.dialog.ui.lineEditPython2Interpreter.isEnabled())
        self.assertFalse(self.dialog.ui.lineEditGnuradioDirectory.isEnabled())

        self.dialog.ui.radioButtonGnuradioDirectory.click()
        self.assertFalse(self.dialog.ui.lineEditPython2Interpreter.isEnabled())
        self.assertTrue(self.dialog.ui.lineEditGnuradioDirectory.isEnabled())

        self.dialog.ui.radioButtonPython2Interpreter.click()
        self.assertFalse(self.dialog.ui.radioButtonGnuradioDirectory.isChecked())
        self.assertFalse(self.dialog.ui.lineEditGnuradioDirectory.isEnabled())
        self.assertTrue(self.dialog.ui.lineEditPython2Interpreter.isEnabled())
