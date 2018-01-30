from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QFrame, QVBoxLayout

from urh import constants
from urh.models.PluginListModel import PluginListModel
from urh.ui.ui_plugins import Ui_FramePlugins


class PluginFrame(QFrame):
    def __init__(self, plugins, highlighted_plugins=None, parent=None):
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

        try:
            self.restoreGeometry(constants.SETTINGS.value("{}/geometry".format(self.__class__.__name__)))
        except TypeError:
            pass


    def create_connects(self):
        self.ui.listViewPlugins.selectionModel().selectionChanged.connect(self.on_list_selection_changed)
        for plugin in self.model.plugins:
            if hasattr(plugin, "show_proto_sniff_dialog_clicked"):
                plugin.show_proto_sniff_dialog_clicked.connect(self.parent().parent().show_proto_sniff_dialog)

    def save_enabled_states(self):
        for plugin in self.model.plugins:
            constants.SETTINGS.setValue(plugin.name, plugin.enabled)

    @pyqtSlot()
    def on_list_selection_changed(self):
        i = self.ui.listViewPlugins.currentIndex().row()
        self.ui.txtEditPluginDescription.setText(self.model.plugins[i].description)

        if self.settings_layout.count() > 0:
            widget = self.settings_layout.takeAt(0).widget()
            self.settings_layout.removeWidget(widget)
            widget.setParent(None)

        self.settings_layout.addWidget(self.model.plugins[i].settings_frame)
