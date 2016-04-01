from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QFrame, QVBoxLayout

from urh.models.PluginListModel import PluginListModel
from urh import constants
from urh.ui.ui_plugins import Ui_FramePlugins


class PluginController(QFrame):
    def __init__(self, plugins, highlighted_plugins = None, parent=None):
        """
        :type plugins: list of Plugin
        :type highlighted_plugins: list of Plugin
        """
        super().__init__(parent)
        self.ui = Ui_FramePlugins()
        self.ui.setupUi(self)
        self.model = PluginListModel(plugins, highlighted_plugins=highlighted_plugins)
        self.ui.listViewPlugins.setModel(self.model)
        self.settings_layout = QVBoxLayout()
        self.ui.groupBoxSettings.setLayout(self.settings_layout)
        self.create_connects()

    def create_connects(self):
        self.ui.listViewPlugins.selectionModel().selectionChanged.connect(self.handle_list_selection_changed)

    def save_enabled_states(self):
        for plugin in self.model.plugins:
            constants.SETTINGS.setValue(plugin.name, plugin.enabled)

    @pyqtSlot()
    def handle_list_selection_changed(self):
        i = self.ui.listViewPlugins.currentIndex().row()
        self.ui.txtEditPluginDescription.setText(self.model.plugins[i].description)
        self.model.plugins[i].load_settings_frame()

        if self.settings_layout.count() > 0:
            self.settings_layout.takeAt(0).widget().setParent(None)

        self.settings_layout.addWidget(self.model.plugins[i].settings_frame)
