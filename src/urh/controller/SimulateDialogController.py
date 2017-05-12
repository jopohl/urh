from PyQt5.QtWidgets import QDialog, QGraphicsView
from PyQt5.QtCore import Qt

from urh.ui.SimulatorScene import SimulatorScene
from urh.ui.ui_simulate_dialog import Ui_SimulateDialog
from urh.models.SimulateListModel import SimulateListModel
from urh.util.ProjectManager import ProjectManager
from urh.SimulatorProtocolManager import SimulatorProtocolManager

class SimulateDialogController(QDialog):
    def __init__(self, project_manager: ProjectManager, sim_proto_manager: SimulatorProtocolManager, parent=None):
        super().__init__(parent)
        self.ui = Ui_SimulateDialog()
        self.ui.setupUi(self)

        self.project_manager = project_manager
        self.sim_proto_manager = sim_proto_manager

        self.simulator_scene = SimulatorScene(mode=1, sim_proto_manager=self.sim_proto_manager)
        self.ui.gvSimulator.setScene(self.simulator_scene)
        self.ui.gvSimulator.setDragMode(QGraphicsView.RubberBandDrag)

        self.simulate_list_model = SimulateListModel(self.project_manager.participants)
        self.ui.listViewSimulate.setModel(self.simulate_list_model)

    def create_connects(self):
        self.project_manager.project_updated.connect(self.on_project_updated)

    def on_project_updated(self):
        self.simulate_list_model.participants = self.project_manager.participants
        self.simulate_list_model.update()