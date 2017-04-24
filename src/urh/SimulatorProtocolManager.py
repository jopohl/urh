import random

from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.SimulatorItem import SimulatorItem
from urh.signalprocessing.SimulatorRule import SimulatorRule, SimulatorRuleCondition, ConditionType
from urh.signalprocessing.SimulatorMessage import SimulatorMessage
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.signalprocessing.SimulatorGotoAction import SimulatorGotoAction
from urh.signalprocessing.SimulatorProgramAction import SimulatorProgramAction

from urh import constants
from urh.util.ProjectManager import ProjectManager

from PyQt5.QtCore import pyqtSignal, QObject

class SimulatorProtocolManager(QObject):
    message_added = pyqtSignal(SimulatorMessage)
    label_added = pyqtSignal(SimulatorProtocolLabel)
    rule_added = pyqtSignal(SimulatorRule)
    rule_condition_added = pyqtSignal(SimulatorRuleCondition)
    goto_action_added = pyqtSignal(SimulatorGotoAction)
    program_action_added = pyqtSignal(SimulatorProgramAction)

    participants_changed = pyqtSignal()
    label_updated = pyqtSignal(SimulatorProtocolLabel)
    message_updated = pyqtSignal(SimulatorMessage)

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

    def add_program_action(self, program_action: SimulatorProgramAction, pos: int, parent_item: SimulatorItem):
        assert isinstance(program_action, SimulatorProgramAction)
        self.add_item(program_action, pos, parent_item)
        self.program_action_added.emit(program_action)
        
    def add_message(self, msg: SimulatorMessage, pos: int, parent_item: SimulatorItem):
        assert isinstance(msg, SimulatorMessage)
        self.add_item(msg, pos, parent_item)
        self.message_added.emit(msg)

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
        #parent_item.message_type.append(sim_label)
        self.label_added.emit(sim_label)
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

        if isinstance(node, SimulatorMessage):
            for lbl in node.message_type:
                items.append(lbl)

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