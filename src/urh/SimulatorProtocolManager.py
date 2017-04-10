import copy

from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.SimulatorItem import SimulatorItem
from urh.signalprocessing.SimulatorMessage import SimulatorMessage
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel

from urh.util.ProjectManager import ProjectManager

from PyQt5.QtCore import pyqtSignal, QObject

class SimulatorProtocolManager(QObject):
    message_added = pyqtSignal(SimulatorMessage)
    label_added = pyqtSignal(SimulatorProtocolLabel, SimulatorMessage)
    participants_changed = pyqtSignal()

    def __init__(self, project_manager: ProjectManager):
        super().__init__()
        self.rootItem = SimulatorItem()
        self.project_manager = project_manager
        self.broadcast_part = Participant("Broadcast", "Broadcast", self.project_manager.broadcast_address_hex)
        #self.broadcast_part.is_broadcast = True

        self.create_connects()

    def create_connects(self):
        self.project_manager.project_updated.connect(self.on_project_updated)

    def on_project_updated(self):
        self.broadcast_part.address_hex = self.project_manager.broadcast_address_hex
        self.participants_changed.emit()

    @property
    def participants(self):
        return self.project_manager.participants + [self.broadcast_part]

    def add_message(self, destination, plain_bits, pause, message_type, decoder, source, pos, parentItem):
        if parentItem is None:
            parentItem = self.rootItem

        assert parentItem == self.rootItem or isinstance(parentItem, SimulatorRuleCondition)

        sim_message = SimulatorMessage(destination=destination, plain_bits=copy.copy(plain_bits), pause=pause,
                        message_type=copy.deepcopy(message_type), decoder=decoder, source=source)

        parentItem.insert_child(pos, sim_message)
        self.message_added.emit(sim_message)
        return sim_message
        
    def add_sim_message(self, msg: SimulatorMessage, pos, parentItem: SimulatorItem=None):
        self.add_message(msg.destination, msg.plain_bits, msg.pause, msg.message_type, msg.decoder, msg.source, pos, parentItem)

    def add_label(self, name: str, start: int, end: int, color_index: int, type: FieldType=None, parentItem: SimulatorMessage=None):
        assert isinstance(parentItem, SimulatorMessage)

        sim_label = SimulatorProtocolLabel(name, start, end - 1, color_index, type)
        parentItem.message_type.append(sim_label)
        #parentItem.insert_child(pos, sim_label)
        self.label_added.emit(sim_label, parentItem)

    def n_top_level_items(self):
        return self.rootItem.childCount()