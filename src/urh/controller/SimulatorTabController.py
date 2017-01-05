from PyQt5.QtWidgets import QWidget

from PyQt5.QtCore import pyqtSlot

from urh.models.SimulatorTableModel import SimulatorTableModel
from urh.models.SimulateListModel import SimulateListModel
from urh.plugins.PluginManager import PluginManager
from urh.util.ProjectManager import ProjectManager
from urh.ui.ui_simulator import Ui_SimulatorTab
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer

from urh.controller.CompareFrameController import CompareFrameController
from urh.signalprocessing.Message import Message
import copy

class SimulatorTabController(QWidget):
    def __init__(self, plugin_manager: PluginManager,
                 project_manager: ProjectManager, parent, cf_controller: CompareFrameController):

        super().__init__(parent)

        self.proto_analyzer = ProtocolAnalyzer(None)
        self.project_manager = project_manager
        self.plugin_manager = plugin_manager
        self.cf_controller = cf_controller

        self.ui = Ui_SimulatorTab()
        self.ui.setupUi(self)

        self.ui.splitter_2.setSizes([self.width() / 0.7, self.width() / 0.3])

        self.simulate_list_model = SimulateListModel(self.project_manager.participants)
        self.ui.listViewSimulate.setModel(self.simulate_list_model)

        self.simulator_model = SimulatorTableModel(self.proto_analyzer, self.project_manager.participants, self)
        self.ui.tblViewSimulator.setModel(self.simulator_model)

        self.create_connects()

    def create_connects(self):
        self.project_manager.project_updated.connect(self.on_project_updated)
        self.ui.tblViewSimulator.participant_changed.connect(self.on_participant_edited)
        self.ui.btnAddMessage.clicked.connect(self.on_btn_add_message_clicked)

    def updateUI(self, ignore_table_model=False, resize_table=True):
        if not ignore_table_model:
            self.simulator_model.update()

        if resize_table:
            self.ui.tblViewSimulator.resize_columns()

    def on_project_updated(self):
        self.simulate_list_model.participants = self.project_manager.participants
        self.simulate_list_model.update()
        self.simulator_model.participants = self.project_manager.participants
        self.simulator_model.refresh_vertical_header()

    def on_participant_edited(self):
        self.simulator_model.refresh_vertical_header()
        self.ui.tblViewSimulator.resize_vertical_header()

    @pyqtSlot()
    def on_btn_add_message_clicked(self):
        msg = self.cf_controller.protocol_list[0].messages[0]

        self.proto_analyzer.messages.append(Message(plain_bits=copy.copy(msg.decoded_bits), pause=msg.pause,
                            message_type=copy.deepcopy(msg.message_type),
                            rssi=msg.rssi, modulator_indx=0, decoder=msg.decoder, bit_len=msg.bit_len, participant=msg.participant))

        self.updateUI()