import copy

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QDropEvent
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsSceneDragDropEvent, QAbstractItemView

from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Participant import Participant
from urh.simulator.ActionItem import ActionItem, GotoActionItem, TriggerCommandActionItem, SleepActionItem, \
    CounterActionItem
from urh.simulator.GraphicsItem import GraphicsItem
from urh.simulator.LabelItem import LabelItem
from urh.simulator.MessageItem import MessageItem
from urh.simulator.ParticipantItem import ParticipantItem
from urh.simulator.RuleItem import RuleItem, RuleConditionItem
from urh.simulator.SimulatorConfiguration import SimulatorConfiguration
from urh.simulator.SimulatorCounterAction import SimulatorCounterAction
from urh.simulator.SimulatorGotoAction import SimulatorGotoAction
from urh.simulator.SimulatorItem import SimulatorItem
from urh.simulator.SimulatorMessage import SimulatorMessage
from urh.simulator.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.simulator.SimulatorRule import SimulatorRule, SimulatorRuleCondition, ConditionType
from urh.simulator.SimulatorSleepAction import SimulatorSleepAction
from urh.simulator.SimulatorTriggerCommandAction import SimulatorTriggerCommandAction


class SimulatorScene(QGraphicsScene):
    files_dropped = pyqtSignal(list)

    model_to_scene_class_mapping = {
        SimulatorRule: RuleItem,
        SimulatorRuleCondition: RuleConditionItem,
        SimulatorGotoAction: GotoActionItem,
        SimulatorTriggerCommandAction: TriggerCommandActionItem,
        SimulatorCounterAction: CounterActionItem,
        SimulatorSleepAction: SleepActionItem,
        SimulatorMessage: MessageItem,
        SimulatorProtocolLabel: LabelItem
    }

    def __init__(self, mode: int, simulator_config: SimulatorConfiguration, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.simulator_config = simulator_config
        self.tree_root_item = None

        self.participants_dict = {}
        self.participant_items = []

        self.broadcast_part = self.insert_participant(self.simulator_config.broadcast_part)
        self.not_assigned_part = self.insert_participant(None)
        self.update_participants(refresh=False)

        self.items_dict = {}

        self.on_items_added([item for item in self.simulator_config.rootItem.children])

        self.create_connects()

    @property
    def visible_participants(self):
        return [part for part in self.participant_items if part.isVisible()]

    @property
    def visible_participants_without_broadcast(self):
        return [part for part in self.participant_items if part.isVisible() and part is not self.broadcast_part]

    def create_connects(self):
        self.simulator_config.participants_changed.connect(self.update_participants)

        self.simulator_config.items_deleted.connect(self.on_items_deleted)
        self.simulator_config.items_updated.connect(self.on_items_updated)
        self.simulator_config.items_moved.connect(self.on_items_moved)
        self.simulator_config.items_added.connect(self.on_items_added)

    def on_items_deleted(self, items):
        if self is None:
            return

        for item in items:
            scene_item = self.model_to_scene(item)

            if scene_item in self.items():
                self.removeItem(scene_item)

        self.update_items_dict()
        self.update_view()

    def on_items_updated(self, items):
        scene_items = [self.model_to_scene(item) for item in items]

        for scene_item in scene_items:
            scene_item.refresh()

        self.update_view()

    def on_items_moved(self, items):
        for item in items:
            scene_item = self.model_to_scene(item)
            self.insert_item(scene_item)

        self.update_view()

    def on_items_added(self, items):
        for item in items:
            self.on_item_added(item)

        self.update_view()

    def on_item_added(self, item: SimulatorItem):
        scene_item = self.model_to_scene_class_mapping[type(item)](model_item=item)
        self.insert_item(scene_item)

        # add children to scene ...
        for child in item.children:
            self.on_item_added(child)

    def model_to_scene(self, model_item: SimulatorItem):
        if (model_item is None or model_item is self.simulator_config.rootItem):
            return None

        try:
            return self.items_dict[model_item]
        except KeyError:
            return None

    def insert_participant(self, participant: Participant):
        participant_item = ParticipantItem(participant)
        participant_item.setVisible(False)
        self.participant_items.insert(-2, participant_item)
        self.participants_dict[participant] = participant_item
        self.addItem(participant_item)

        return participant_item

    def insert_item(self, item: GraphicsItem):
        parent_scene_item = self.get_parent_scene_item(item)
        item.setParentItem(parent_scene_item)

        self.items_dict[item.model_item] = item

        if item not in self.items():
            self.addItem(item)

        item.update_flags()
        item.refresh()

    def get_parent_scene_item(self, item: GraphicsItem):
        return self.model_to_scene(item.model_item.parent())

    def min_items_width(self):
        width = 0
        items = [item for item in self.items() if isinstance(item, (RuleConditionItem, ActionItem))]

        for item in items:
            if item.labels_width() > width:
                width = item.labels_width()

        return width

    def items_width(self):
        vp = self.visible_participants

        if len(vp) >= 2:
            width = vp[-1].x_pos()
            width -= vp[0].x_pos()
        else:
            width = self.min_items_width()

        return width

    def delete_selected_items(self):
        items = self.selectedItems()
        self.clearSelection()

        self.simulator_config.delete_items([item.model_item for item in items])

    def log_selected_items(self, logging_active: bool):
        items = self.selectedItems()
        self.log_items(items, logging_active)

    def log_items(self, items, logging_active: bool):

        for item in items:
            item.model_item.logging_active = logging_active

        self.simulator_config.items_updated.emit([item.model_item for item in items])

    def log_toggle_selected_items(self):
        items = self.selectedItems()

        for item in items:
            item.model_item.logging_active = not item.model_item.logging_active

        self.simulator_config.items_updated.emit([item.model_item for item in items])

    def log_all_items(self, logging_active: bool):
        self.log_items(self.selectable_items(), logging_active)

    def selectable_items(self):
        return [item for item in self.items() if isinstance(item, GraphicsItem) and
                item.is_selectable()]

    def move_items(self, items, ref_item, position):
        new_pos, new_parent = self.insert_at(ref_item, position)
        self.simulator_config.move_items(items, new_pos, new_parent)

    def select_all_items(self):
        for item in self.simulator_config.rootItem.children:
            scene_item = self.model_to_scene(item)
            scene_item.select_all()

    def update_numbering(self):
        for item in self.simulator_config.rootItem.children:
            scene_item = self.model_to_scene(item)
            scene_item.update_numbering()

    def update_valid_states(self):
        self.simulator_config.update_valid_states()

    def update_view(self):
        self.update_numbering()
        self.update_valid_states()
        self.arrange_participants()
        self.arrange_items()

        # resize scrollbar
        self.setSceneRect(self.itemsBoundingRect().adjusted(-10, 0, 0, 0))

    def update_participants(self, refresh=True):
        for participant in list(self.participants_dict):
            if participant is None or participant == self.simulator_config.broadcast_part:
                continue

            self.removeItem(self.participants_dict[participant])
            self.participant_items.remove(self.participants_dict[participant])
            del self.participants_dict[participant]

        for participant in self.simulator_config.participants:
            if participant in self.participants_dict:
                self.participants_dict[participant].refresh()
            else:
                self.insert_participant(participant)

        if refresh:
            self.update_view()

    def refresh_participant(self, participant: Participant):
        try:
            self.participants_dict[participant].refresh()
        except KeyError:
            pass

    def update_items_dict(self):
        sim_items = self.simulator_config.get_all_items()

        for key in list(self.items_dict.keys()):
            if key not in sim_items:
                del self.items_dict[key]

    def get_all_message_items(self):
        """

        :rtype: list[MessageItem]
        """
        return [item for item in self.items() if isinstance(item, MessageItem)]

    def get_selected_messages(self):
        """

        :rtype: list[SimulatorMessage]
        """
        return [item.model_item for item in self.selectedItems() if isinstance(item, MessageItem)]

    def select_messages_with_participant(self, participant: ParticipantItem, from_part=True):
        messages = self.get_all_message_items()
        self.clearSelection()

        for msg in messages:
            if ((from_part and msg.source is participant) or
                    (not from_part and msg.destination is participant)):
                msg.select_all()

    def arrange_participants(self):
        messages = self.get_all_message_items()

        for participant in self.participant_items:
            if any(msg.source == participant or msg.destination == participant for msg in messages):
                participant.setVisible(True)
            else:
                participant.setVisible(False)
                participant.update_position(x_pos=30)

        vp = self.visible_participants

        if not vp:
            return

        vp[0].update_position(x_pos=0)

        for i in range(1, len(vp)):
            curr_participant = vp[i]
            participants_left = vp[:i]

            items = [msg for msg in messages
                     if ((msg.source == curr_participant and msg.destination in participants_left)
                         or (msg.source in participants_left and msg.destination == curr_participant))]

            x_max = vp[i - 1].x_pos()
            x_max += (vp[i - 1].width() + curr_participant.width()) / 2
            x_max += 10

            for msg in items:
                x = msg.width() + 30
                x += msg.source.x_pos() if msg.source != curr_participant else msg.destination.x_pos()

                if x > x_max:
                    x_max = x

            if i == len(vp) - 1:
                if self.min_items_width() > x_max:
                    x_max = self.min_items_width()

            curr_participant.update_position(x_pos=x_max)

    def arrange_items(self):
        x_pos = 0
        y_pos = 30

        for item in self.simulator_config.rootItem.children:
            scene_item = self.model_to_scene(item)
            scene_item.update_position(x_pos, y_pos)
            y_pos += round(scene_item.boundingRect().height())

        for participant in self.participant_items:
            participant.update_position(y_pos=max(y_pos, 50))

    def dragMoveEvent(self, event: QGraphicsSceneDragDropEvent):
        if any(item.acceptDrops() for item in self.items(event.scenePos())):
            super().dragMoveEvent(event)
        else:
            event.setAccepted(True)

    def insert_at(self, ref_item, position, insert_rule=False):
        if ref_item:
            ref_item = ref_item.model_item

        if ref_item is None:
            parent_item = self.simulator_config.rootItem
            insert_position = self.simulator_config.n_top_level_items()
        elif insert_rule:
            parent_item = self.simulator_config.rootItem

            while ref_item.parent() != self.simulator_config.rootItem:
                ref_item = ref_item.parent()

            insert_position = ref_item.get_pos()
        elif isinstance(ref_item, SimulatorRuleCondition):
            if position == QAbstractItemView.OnItem:
                parent_item = ref_item
                insert_position = parent_item.child_count()
            else:
                parent_item = self.simulator_config.rootItem
                insert_position = ref_item.parent().get_pos()
        else:
            parent_item = ref_item.parent()
            insert_position = ref_item.get_pos()

        if position == QAbstractItemView.BelowItem:
            insert_position += 1

        return (insert_position, parent_item)

    def dropEvent(self, event: QDropEvent):
        items = [item for item in self.items(event.scenePos()) if isinstance(item, GraphicsItem) and item.acceptDrops()]
        item = None if len(items) == 0 else items[0]
        if len(event.mimeData().urls()) > 0:
            self.files_dropped.emit(event.mimeData().urls())

        indexes = list(event.mimeData().text().split("/")[:-1])

        group_nodes = []
        file_nodes = []
        for index in indexes:
            try:
                row, column, parent = map(int, index.split(","))
                if parent == -1:
                    parent = self.tree_root_item
                else:
                    parent = self.tree_root_item.child(parent)
                node = parent.child(row)
                if node.is_group:
                    group_nodes.append(node)
                else:
                    file_nodes.append(node)
            except ValueError:
                continue

        # Which Nodes to add?
        nodes_to_add = []
        """:type: list of ProtocolTreeItem """
        for group_node in group_nodes:
            nodes_to_add.extend(group_node.children)
        nodes_to_add.extend([file_node for file_node in file_nodes if file_node not in nodes_to_add])
        protocols_to_add = [node.protocol for node in nodes_to_add]

        ref_item = item
        position = None if ref_item is None else item.drop_indicator_position
        self.add_protocols(ref_item, position, protocols_to_add)
        super().dropEvent(event)

    def add_rule(self, ref_item, position):
        rule = SimulatorRule()
        pos, parent = self.insert_at(ref_item, position, True)
        self.simulator_config.add_items([rule], pos, parent)

        self.add_rule_condition(rule, ConditionType.IF)
        return rule

    def add_rule_condition(self, rule: SimulatorRule, type: ConditionType):
        rule_condition = SimulatorRuleCondition(type)

        pos = rule.child_count()

        if type is ConditionType.ELSE_IF and rule.has_else_condition:
            pos -= 1

        self.simulator_config.add_items([rule_condition], pos, rule)
        return rule_condition

    def add_goto_action(self, ref_item, position):
        goto_action = SimulatorGotoAction()
        pos, parent = self.insert_at(ref_item, position, False)
        self.simulator_config.add_items([goto_action], pos, parent)
        return goto_action

    def add_sleep_action(self, ref_item, position):
        sleep_action = SimulatorSleepAction()
        pos, parent = self.insert_at(ref_item, position, False)
        self.simulator_config.add_items([sleep_action], pos, parent)
        return sleep_action

    def add_counter_action(self, ref_item, position):
        counter_action = SimulatorCounterAction()
        pos, parent = self.insert_at(ref_item, position, False)
        self.simulator_config.add_items([counter_action], pos, parent)
        return counter_action

    def add_trigger_command_action(self, ref_item, position):
        command_action = SimulatorTriggerCommandAction()
        pos, parent = self.insert_at(ref_item, position, False)
        self.simulator_config.add_items([command_action], pos, parent)
        return command_action

    def add_message(self, plain_bits, pause, message_type, ref_item, position, decoder=None, source=None,
                    destination=None):
        message = self.create_message(destination, plain_bits, pause, message_type, decoder, source)
        pos, parent = self.insert_at(ref_item, position, False)
        self.simulator_config.add_items([message], pos, parent)
        return message

    def create_message(self, destination, plain_bits, pause, message_type, decoder, source):
        if destination is None:
            destination = self.simulator_config.broadcast_part

        sim_message = SimulatorMessage(destination=destination, plain_bits=plain_bits, pause=pause,
                                       message_type=MessageType(message_type.name), decoder=decoder, source=source)

        for lbl in message_type:
            sim_label = SimulatorProtocolLabel(copy.deepcopy(lbl))
            sim_message.insert_child(-1, sim_label)

        return sim_message

    def clear_all(self):
        self.simulator_config.delete_items([item for item in self.simulator_config.rootItem.children])

    def add_protocols(self, ref_item, position, protocols_to_add: list):
        pos, parent = self.insert_at(ref_item, position)
        messages = []

        for protocol in protocols_to_add:
            for msg in protocol.messages:
                source, destination = self.detect_source_destination(msg)

                messages.append(self.create_message(destination=destination,
                                                    plain_bits=copy.copy(msg.decoded_bits),
                                                    pause=0,
                                                    message_type=msg.message_type,
                                                    decoder=msg.decoder,
                                                    source=source))

        self.simulator_config.add_items(messages, pos, parent)

    def get_drag_nodes(self):
        drag_nodes = []
        self.__get_drag_nodes(self.simulator_config.rootItem, drag_nodes)
        return drag_nodes

    def __get_drag_nodes(self, node: SimulatorItem, drag_nodes: list):
        scene_item = self.model_to_scene(node)

        if scene_item and scene_item.isSelected() and scene_item.is_movable():
            drag_nodes.append(scene_item.model_item)

        for child in node.children:
            self.__get_drag_nodes(child, drag_nodes)

    def detect_source_destination(self, message: Message):
        participants = self.simulator_config.participants

        source = None if len(participants) < 2 else participants[0]
        destination = self.simulator_config.broadcast_part

        if message.participant:
            source = message.participant
            dst_address_label = next((lbl for lbl in message.message_type if lbl.field_type and
                                      lbl.field_type.function == FieldType.Function.DST_ADDRESS), None)
            if dst_address_label:
                start, end = message.get_label_range(dst_address_label, view=1, decode=True)
                dst_address = message.decoded_hex_str[start:end]
                dst = next((p for p in participants if p.address_hex == dst_address), None)
                if dst is not None and dst != source:
                    destination = dst

        return source, destination
