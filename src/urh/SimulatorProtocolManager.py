import copy

from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.SimulatorItem import SimulatorItem
from urh.signalprocessing.SimulatorRule import SimulatorRule, SimulatorRuleCondition, ConditionType
from urh.signalprocessing.SimulatorMessage import SimulatorMessage
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.signalprocessing.SimulatorGotoAction import SimulatorGotoAction

from urh.util.ProjectManager import ProjectManager

from PyQt5.QtCore import pyqtSignal, QObject

class SimulatorProtocolManager(QObject):
    message_added = pyqtSignal(SimulatorMessage)
    label_added = pyqtSignal(SimulatorProtocolLabel, SimulatorMessage)
    rule_added = pyqtSignal(SimulatorRule)
    rule_condition_added = pyqtSignal(SimulatorRuleCondition)
    goto_action_added = pyqtSignal(SimulatorGotoAction)

    participants_changed = pyqtSignal()

    item_deleted = pyqtSignal(SimulatorItem)
    item_moved = pyqtSignal(SimulatorItem)

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

    def add_rule(self, rule: SimulatorRule, pos: int, parent_item: SimulatorItem):
        assert isinstance(rule, SimulatorRule)
        self.add_item(rule, pos, parent_item)
        self.rule_added.emit(rule)

    def add_rule_condition(self, rule_condition: SimulatorRuleCondition, pos: int, parent_item: SimulatorItem):
        assert isinstance(rule_condition, SimulatorRuleCondition)
        self.add_item(rule_condition, pos, parent_item)
        self.rule_condition_added.emit(rule_condition)

    def add_goto_action(self, goto_action: SimulatorGotoAction, pos: int, parent_item: SimulatorItem):
        assert isinstance(goto_action, SimulatorGotoAction)
        self.add_item(goto_action, pos, parent_item)
        self.goto_action_added.emit(goto_action)
        
    def add_message(self, msg: SimulatorMessage, pos: int, parent_item: SimulatorItem):
        assert isinstance(msg, SimulatorMessage)
        self.add_item(msg, pos, parent_item)
        self.message_added.emit(msg)

    def add_label(self, name: str, start: int, end: int, color_index: int, type: FieldType=None, parent_item: SimulatorMessage=None):
        assert isinstance(parent_item, SimulatorMessage)
        sim_label = SimulatorProtocolLabel(name, start, end - 1, color_index, type)
        parent_item.message_type.append(sim_label)
        self.label_added.emit(sim_label, parentItem)

    def n_top_level_items(self):
        return self.rootItem.child_count()

    def get_all_messages(self):
        return [item for item in self.get_all_items() if isinstance(item, SimulatorMessage)]

    def get_all_items(self):
        items = []
        self.__get_all_items(self.rootItem, items)
        return items

    @staticmethod
    def __get_all_items(node: SimulatorItem, items: list):
        for child in node.children:
            SimulatorProtocolManager.__get_all_items(child, items)

        if isinstance(node, SimulatorMessage):
            for lbl in node.message_type:
                items.append(lbl)

        items.append(node)

    def delete_item(self, item: SimulatorItem):
        if (isinstance(item, SimulatorRuleCondition) and
                item.type == ConditionType.IF):
            item = item.parent()

        item.delete()
        self.item_deleted.emit(item)

    def move_item(self, item: SimulatorItem, new_pos: int, new_parent: SimulatorItem):
        if new_parent is None:
            new_parent = self.rootItem

        item.delete()
        new_parent.insert_child(new_pos, item)
        self.item_moved.emit(item)