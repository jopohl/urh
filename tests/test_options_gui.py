from tests.QtTestCase import QtTestCase
from urh.controller.dialogs.OptionsDialog import OptionsDialog
from urh.dev.BackendHandler import BackendHandler
from urh.models.PluginListModel import PluginListModel
from urh.plugins.PluginManager import PluginManager


class TestOptionsGUI(QtTestCase):
    def setUp(self):
        super().setUp()
        self.dialog = OptionsDialog(
            self.form.plugin_manager.installed_plugins, parent=self.form
        )

        if self.SHOW:
            self.dialog.show()

    def test_generation_tab(self):
        self.dialog.ui.tabWidget.setCurrentIndex(0)
        self.assertEqual(
            self.dialog.ui.checkBoxDefaultFuzzingPause.isChecked(),
            self.dialog.ui.doubleSpinBoxFuzzingPause.isEnabled(),
        )

        self.dialog.ui.checkBoxDefaultFuzzingPause.click()
        self.assertEqual(
            self.dialog.ui.checkBoxDefaultFuzzingPause.isChecked(),
            self.dialog.ui.doubleSpinBoxFuzzingPause.isEnabled(),
        )

        self.dialog.ui.checkBoxDefaultFuzzingPause.click()
        self.assertEqual(
            self.dialog.ui.checkBoxDefaultFuzzingPause.isChecked(),
            self.dialog.ui.doubleSpinBoxFuzzingPause.isEnabled(),
        )

    def test_plugins_tab(self):
        self.dialog.ui.tabWidget.setCurrentIndex(3)
        self.assertEqual(self.dialog.ui.tabWidget.tabText(3), "Plugins")

        list_view = self.dialog.plugin_controller.ui.listViewPlugins
        model = list_view.model()
        self.assertIsInstance(model, PluginListModel)
        self.assertEqual(model.rowCount(), len(PluginManager().installed_plugins))

        for i in range(model.rowCount()):
            descr = (
                self.dialog.plugin_controller.ui.txtEditPluginDescription.toPlainText()
            )
            list_view.setCurrentIndex(model.index(i, 0))
            self.assertNotEqual(
                descr,
                self.dialog.plugin_controller.ui.txtEditPluginDescription.toPlainText(),
            )

    def test_device_tab(self):
        self.dialog.ui.tabWidget.setCurrentIndex(4)
        self.assertEqual(self.dialog.ui.tabWidget.tabText(4), "Device")

        self.assertEqual(
            self.dialog.ui.tblDevices.model().rowCount(),
            len(BackendHandler.DEVICE_NAMES),
        )

    def test_field_type_tab(self):
        self.dialog.ui.tabWidget.setCurrentWidget(self.dialog.ui.tabFieldtypes)
        n_rows = self.dialog.ui.tblLabeltypes.model().rowCount()
        self.assertGreater(n_rows, 1)
        self.dialog.ui.btnAddLabelType.click()
        self.assertEqual(n_rows + 1, self.dialog.ui.tblLabeltypes.model().rowCount())
        self.dialog.ui.btnRemoveLabeltype.click()
        self.assertEqual(n_rows, self.dialog.ui.tblLabeltypes.model().rowCount())
