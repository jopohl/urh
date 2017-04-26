import random

from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.SimulatorItem import SimulatorItem
from urh.signalprocessing.SimulatorRule import SimulatorRuleCondition, ConditionType
from urh.signalprocessing.SimulatorMessage import SimulatorMessage
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel

from urh import constants
from urh.util.ProjectManager import ProjectManager

from PyQt5.QtCore import pyqtSignal, QObject

class SimulatorProtocolManager(QObject):
    participants_changed = pyqtSignal()

    item_deleted = pyqtSignal(SimulatorItem)
    item_updated = pyqtSignal(SimulatorItem)
    item_moved = pyqtSignal(SimulatorItem)
    item_added = pyqtSignal(SimulatorItem)

    def __init__(self, project_manager: ProjectManager):
        super().__init__()
        self.rootItem = SimulatorItem()
        self.project_manager = project_manager
        self.broadcast_part = Participant("Broadcast", "Broadcast", self.project_manager.broadcast_address_hex)

        self.create_connects()

    def create_connects(self):
        self.project_manager.project_updated.connect(self.on_project_updated)

    def on_project_updated(self):
        self.broadcast_part.address_hex = self.project_manager.broadcast_address_hex

        messages = [msg for msg in self.get_all_messages() if ((msg.participant and msg.participant not in self.participants) or
                    (msg.destination and msg.destination not in self.participants))]

        for msg in messages:
            self.delete_item(msg)

        self.participants_changed.emit()

    @property
    def participants(self):
        return self.project_manager.participants + [self.broadcast_part]

    def add_item(self, item: SimulatorItem, pos: int, parent_item: SimulatorItem):
        if parent_item is None:
            parent_item = self.rootItem

        parent_item.insert_child(pos, item)
        self.item_added.emit(item)

    def delete_item(self, item: SimulatorItem):
        if (isinstance(item, SimulatorRuleCondition) and
                item.type == ConditionType.IF):
            item = item.parent()

        item.delete()
        self.item_deleted.emit(item)

    def move_item(self, item: SimulatorItem, new_pos: int, new_parent: SimulatorItem):
        if new_parent is None:
            new_parent = self.rootItem

        new_parent.insert_child(new_pos, item)
        self.item_moved.emit(item)

    def add_label(self, start: int, end: int, name: str = None, color_index: int = None,
                    type: FieldType=None, parent_item: SimulatorMessage=None):
        assert isinstance(parent_item, SimulatorMessage)

        name = "" if not name else name
        used_colors = [p.color_index for p in parent_item.message_type]
        avail_colors = [i for i, _ in enumerate(constants.LABEL_COLORS) if i not in used_colors]

        if color_index is None:
            if len(avail_colors) > 0:
                color_index = avail_colors[0]
            else:
                color_index = random.randint(0, len(constants.LABEL_COLORS) - 1)

        sim_label = SimulatorProtocolLabel(name, start, end - 1, color_index, type)
        self.add_item(sim_label, -1, parent_item)
        return sim_label

    def n_top_level_items(self):
        return self.rootItem.child_count()

    def get_all_messages(self):
        return [item for item in self.get_all_items() if isinstance(item, SimulatorMessage)]

    def get_all_items(self):
        items = []

        for child in self.rootItem.children:
            self.__get_all_items(child, items)

        return items

    @staticmethod
    def __get_all_items(node: SimulatorItem, items: list):
        items.append(node)

        for child in node.children:
            SimulatorProtocolManager.__get_all_items(child, items)