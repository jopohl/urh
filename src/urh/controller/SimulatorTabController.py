from PyQt5.QtWidgets import QWidget

from urh.plugins.PluginManager import PluginManager
from urh.util.ProjectManager import ProjectManager
from urh.ui.ui_simulator import Ui_SimulatorTab

class SimulatorTabController(QWidget):
    def __init__(self, plugin_manager: PluginManager,
                 project_manager: ProjectManager, parent):

        super().__init__(parent)

        self.project_manager = project_manager
        self.plugin_manager = plugin_manager

        self.ui = Ui_SimulatorTab()
        self.ui.setupUi(self)

        self.ui.splitter_2.setSizes([self.width() / 0.7, self.width() / 0.3])
