from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot, Qt

from urh.models.SimulateListModel import SimulateListModel
from urh.models.GeneratorTreeModel import GeneratorTreeModel
from urh.util.ProjectManager import ProjectManager
from urh.ui.ui_simulator import Ui_SimulatorTab
from urh.ui.SimulatorScene import SimulatorScene
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer

from urh.controller.CompareFrameController import CompareFrameController
from urh.signalprocessing.Message import Message
from urh.signalprocessing.SimulatorMessage import SimulatorMessage
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel

class SimulatorTabController(QWidget):
    def __init__(self, compare_frame_controller: CompareFrameController,
                 project_manager: ProjectManager, parent):

        super().__init__(parent)

        self.proto_analyzer = ProtocolAnalyzer(None)
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

        self.messages = []

    def create_connects(self, compare_frame_controller):
        self.project_manager.project_updated.connect(self.on_project_updated)
        compare_frame_controller.proto_tree_model.layoutChanged.connect(self.refresh_tree)
        self.simulate_list_model.simulate_state_changed.connect(self.on_project_updated)

    def on_project_updated(self):
        self.simulate_list_model.participants = self.project_manager.participants
        self.simulate_list_model.update()

        self.messages[:] = [msg for msg in self.messages if msg.source in self.project_manager.participants
                                and msg.destination in self.project_manager.participants]

        self.simulator_scene.update_participants(self.project_manager.participants)
        self.simulator_scene.update_messages(self.messages)
        self.simulator_scene.arrange_items()

    @pyqtSlot()
    def refresh_tree(self):
        self.tree_model.layoutChanged.emit()
        self.ui.treeProtocols.expandAll()

    def close_all(self):
        self.tree_model.rootItem.clearChilds()
        self.tree_model.rootItem.addGroup()
        self.refresh_tree()

    def __detect_source_destination(self, message: Message):
        # TODO: use SRC_ADDRESS and DST_ADDRESS labels
        participants = self.project_manager.participants
        source = None
        destination = None

        if len(participants) < 2:
            return (None, None)

        if message.participant:
            source = message.participant
            destination = participants[0] if source == participants[1] else participants[1]
        else:
            source = participants[0]
            destination = participants[1]

        return (source, destination)

    def add_protocols(self, protocols):
        for protocol in protocols:
            for message in protocol.messages:
                source, destination = self.__detect_source_destination(message)
                simulator_message = SimulatorMessage(message.message_type.name, source=source, destination=destination)
                for label in message.message_type:
                    simulator_message.labels.append(SimulatorProtocolLabel(label.name, label.type, label.end - label.start,
                                                                         label.color_index, label.type))
                self.messages.append(simulator_message)

        self.on_project_updated()