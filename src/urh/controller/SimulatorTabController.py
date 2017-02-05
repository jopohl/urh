from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot, Qt

from urh.models.SimulateListModel import SimulateListModel
from urh.models.GeneratorTreeModel import GeneratorTreeModel
from urh.util.ProjectManager import ProjectManager
from urh.ui.ui_simulator import Ui_SimulatorTab
from urh.ui.SimulatorScene import SimulatorScene
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer

from urh.controller.CompareFrameController import CompareFrameController
from urh.signalprocessing.SimulatorMessage import SimulatorMessage
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel

class SimulatorTabController(QWidget):
    def __init__(self, compare_frame_controller: CompareFrameController,
                 project_manager: ProjectManager, parent):

        super().__init__(parent)

        self.project_manager = project_manager

        self.ui = Ui_SimulatorTab()
        self.ui.setupUi(self)

        self.ui.splitter_2.setSizes([self.width() / 0.7, self.width() / 0.3])

        self.simulate_list_model = SimulateListModel(self.project_manager.participants)
        self.ui.listViewSimulate.setModel(self.simulate_list_model)

        self.ui.treeProtocols.setHeaderHidden(True)
        self.tree_model = GeneratorTreeModel(compare_frame_controller)
        self.tree_model.set_root_item(compare_frame_controller.proto_tree_model.rootItem)
        self.tree_model.controller = self
        self.ui.treeProtocols.setModel(self.tree_model)

        self.simulator_scene = SimulatorScene(controller=self)
        self.simulator_scene.tree_root_item = compare_frame_controller.proto_tree_model.rootItem
        #self.simulator_scene.setSceneRect(0, 0, 500, 500)
        self.ui.gvSimulator.setScene(self.simulator_scene)
        self.ui.gvSimulator.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.create_connects(compare_frame_controller)

    def create_connects(self, compare_frame_controller):
        self.project_manager.project_updated.connect(self.on_project_updated)
        compare_frame_controller.proto_tree_model.modelReset.connect(self.refresh_tree)

    def on_project_updated(self):
        self.simulate_list_model.participants = self.project_manager.participants
        self.simulate_list_model.update()

        self.simulator_scene.update_view()

    @pyqtSlot()
    def refresh_tree(self):
        self.tree_model.beginResetModel()
        self.tree_model.endResetModel()
        self.ui.treeProtocols.expandAll()

    def close_all(self):
        self.tree_model.rootItem.clearChilds()
        self.tree_model.rootItem.addGroup()
        self.refresh_tree()