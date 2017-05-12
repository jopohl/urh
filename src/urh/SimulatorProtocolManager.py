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

    items_deleted = pyqtSignal(list)
    item_updated = pyqtSignal(SimulatorItem)
    items_moved = pyqtSignal(list)
    items_added = pyqtSignal(list)

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
        participants = self.participants

        messages = [msg for msg in self.get_all_messages() if ((msg.participant and msg.participant not in participants) or
                    (msg.destination and msg.destination not in participants))]

        self.delete_items(messages)

        self.participants_changed.emit()

    @property
    def participants(self):
        return self.project_manager.participants + [self.broadcast_part]

    def add_items(self, items, pos: int, parent_item: SimulatorItem):
        if parent_item is None:
            parent_item = self.rootItem

        for item in items:
            parent_item.insert_child(pos, item)
            pos += 1

        self.items_added.emit(items)

    def delete_items(self, items):
        for i, item in enumerate(items):
            if (isinstance(item, SimulatorRuleCondition) and
                    item.type == ConditionType.IF):
                items[i] = item.parent()

            items[i].delete()

        self.items_deleted.emit(items)

    def move_items(self, items, new_pos: int, new_parent: SimulatorItem):
        if new_parent is None:
            new_parent = self.rootItem

        for item in items:
            if item.parent() is new_parent and item.get_pos() < new_pos:
                new_pos -= 1

            new_parent.insert_child(new_pos, item)
            new_pos += 1

        self.items_moved.emit(items)

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

        sim_label = SimulatorProtocolLabel(name, start, end, color_index, type)
        self.add_items([sim_label], -1, parent_item)
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