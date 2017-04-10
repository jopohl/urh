from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItemGroup, QGraphicsSceneDragDropEvent, QGraphicsItem, QMenu, QAction, QActionGroup, QGraphicsObject, QAbstractItemView, QApplication
from PyQt5.QtGui import QPen, QDragEnterEvent, QDropEvent, QPolygonF, QColor, QFont, QFontDatabase, QTransform, QBrush
from PyQt5.QtCore import Qt, QRectF, QSizeF, QPointF, QSizeF, pyqtSignal, pyqtSlot, QLineF
import math

import weakref

from urh import constants

from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.SimulatorItem import SimulatorItem
from urh.signalprocessing.SimulatorMessage import SimulatorMessage
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.SimulatorRuleset import SimulatorRuleset
from urh.signalprocessing.LabelItem import LabelItem
from urh.signalprocessing.UnlabeledRangeItem import UnlabeledRangeItem
from urh.signalprocessing.MessageItem import MessageItem
from urh.signalprocessing.SimulatorGraphicsItem import SimulatorGraphicsItem

class ActionItem(SimulatorGraphicsItem):
    def __init__(self, type, parent=None):
        super().__init__(parent)
        self.text = QGraphicsTextItem(self)

        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(8)
        font.setWeight(QFont.DemiBold)
        self.text.setFont(font)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def refresh(self, x_pos, y_pos):
        self.setPos(x_pos, y_pos)
        self.number.setPos(0, 0)
        self.text.setPos(self.number.boundingRect().width(), 0)
        super().refresh(x_pos, y_pos)

class GotoAction(ActionItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text.setPlainText("GOTO")

        self.__goto_target = None

    @property
    def goto_target(self):
        if not self.__goto_target or not self.__goto_target():
            return None
        else:
            return self.__goto_target()

    @goto_target.setter
    def goto_target(self, value):
        self.__goto_target = weakref.ref(value) if value else None

        self.update_label()

    def refresh(self, x_pos, y_pos):
        if self.goto_target not in self.scene().get_all_items():
            self.goto_target = None

        self.update_label()

        super().refresh(x_pos, y_pos)

    def update_label(self):
        if self.goto_target:
            self.text.setPlainText("GOTO " + self.goto_target.index)
        else:
            self.text.setPlainText("GOTO")

class ExternalProgramAction(ActionItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text.setPlainText("Start program [/usr/bin/test]")
        self.ext_prog = None
        self.args = None

class ParticipantItem(QGraphicsItem):
    def __init__(self, model_item: Participant, parent=None):
        super().__init__(parent)

        self.model_item = model_item
        self.text = QGraphicsTextItem(self)
        self.line = QGraphicsLineItem(self)
        self.line.setPen(QPen(Qt.darkGray, 1, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))
        self.refresh()

    def update(self, x_pos = -1, y_pos = -1):
        if x_pos == -1:
            x_pos = self.line.line().x1()

        if y_pos == -1:
            y_pos = self.line.line().y2()

        self.text.setPos(x_pos - (self.text.boundingRect().width() / 2), 0)
        self.line.setLine(x_pos, 30, x_pos, y_pos)
        super().update()

    def refresh(self):
        self.text.setPlainText("?" if not self.model_item else self.model_item.shortname)

    def boundingRect(self):
        return self.childrenBoundingRect()

    def paint(self, painter, option, widget):
        pass

class SimulatorScene(QGraphicsScene):
    items_changed = pyqtSignal()

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.tree_root_item = None
        self.sim_proto_manager = controller.sim_proto_manager

        self.participants_dict = {}
        self.participants = []

        self.not_assigned_part = ParticipantItem(None)
        self.not_assigned_part.setVisible(False)
        self.participants.append(self.not_assigned_part)
        self.participants_dict[None] = self.not_assigned_part
        self.addItem(self.not_assigned_part)

        self.broadcast_part = ParticipantItem(self.sim_proto_manager.broadcast_part)
        self.broadcast_part.setVisible(False)
        self.participants.append(self.broadcast_part)
        self.participants_dict[self.sim_proto_manager.broadcast_part] = self.broadcast_part
        self.addItem(self.broadcast_part)

        self.create_connects()

        self.sim_items = []
        self.update_view()

    def create_connects(self):
        self.sim_proto_manager.message_added.connect(self.on_message_added)
        self.sim_proto_manager.label_added.connect(self.on_label_added)
        self.sim_proto_manager.participants_changed.connect(self.on_participants_changed)

        self.controller.simulator_message_field_model.protocol_label_updated.connect(self.on_label_updated)

    def model_to_scene(self, model_item: SimulatorItem):
        if model_item is None or model_item is self.sim_proto_manager.rootItem:
            return None

        scene_items = self.items()

        for item in scene_items:
            if isinstance(item, SimulatorGraphicsItem):
                if item.model_item is model_item:
                    return item

        print("WHOOPS: Item not found ... :(")
        return None

    def on_participants_changed(self):
        self.update_participants()

    def on_label_updated(self, label: SimulatorProtocolLabel):
        sim_label = self.model_to_scene(label)
        sim_label.refresh()
        
    def on_message_added(self, msg: SimulatorMessage):
        source = self.participants_dict[msg.participant]
        destination = self.participants_dict[msg.destination]

        simulator_message = MessageItem(source, destination, msg)
        self.add_item(simulator_message)

        for lbl in msg.message_type:
            self.on_label_added(lbl, simulator_message)

        simulator_message.refresh_unlabeled_range_marker()
        self.update_view()

    def on_label_added(self, lbl: SimulatorProtocolLabel, msg: SimulatorMessage):
        sim_message = self.model_to_scene(msg)

        LabelItem(model_item=lbl, parent=sim_message)
        sim_message.refresh_unlabeled_range_marker()
        self.update_view()
        
    def add_item(self, item: SimulatorGraphicsItem):
        parent_scene_item = self.get_parent_scene_item(item.model_item)
        item.setParentItem(parent_scene_item)

        if parent_scene_item is None:
            self.addItem(item)

    def get_parent_scene_item(self, model_item: SimulatorItem):
        parent_item = model_item.parent
        return self.model_to_scene(parent_item)

    def items_width(self):
        visible_participants = [part for part in self.participants if part.isVisible()]

        if len(visible_participants) >= 2:
            width = visible_participants[-1].line.line().x1()
            width -= visible_participants[0].line.line().x1()
        else:
            width = 40

        return width        

    def delete_selected_items(self):
        self.delete_items(self.selectedItems())
        self.update_view()

    def get_last_item(self):
        last_item = self.sim_items[-1] if self.sim_items else None

        if isinstance(last_item, RuleItem):
            last_item = last_item.conditions[-1]

            if last_item.sim_items:
                last_item = last_item.sim_items[-1]

        return last_item

    def get_first_item(self):
        first_item = self.sim_items[0] if self.sim_items else None

        if isinstance(first_item, RuleItem):
            first_item = first_item.conditions[0]

        return first_item

    def select_all_items(self):
        for item in self.sim_items:
            item.setSelected(True)

    def delete_items(self, items):
        for item in self.sim_items[:]:
            if item in items:
                self.sim_items.remove(item)
                self.removeItem(item)
            elif type(item) == RuleItem:
                item.delete_items(items)

    def update_numbering(self):
        for i, item in enumerate(self.sim_proto_manager.rootItem.children):
            scene_item = self.model_to_scene(item)
            scene_item.update_numbering(str(i + 1))

    def update_view(self):
        self.update_participants()

        #items = [msg for msg in self.get_all_messages() if (msg.source not in self.participants) or (msg.destination not in self.participants)]
        #self.delete_items(items)

        self.update_numbering()
        self.arrange_participants()
        self.arrange_items()

        self.items_changed.emit()

        # resize scrollbar
        self.setSceneRect(self.itemsBoundingRect().adjusted(-10, 0 , 0, 0))

    def update_participants(self):
        participants = self.sim_proto_manager.participants

        for key in list(self.participants_dict.keys()):
            if key is None:
                continue

            if key not in participants:
                self.removeItem(self.participants_dict[key])
                self.participants.remove(self.participants_dict[key])
                del self.participants_dict[key]

        for participant in participants:
            if participant in self.participants_dict:
                self.participants_dict[participant].refresh()
            else:
                participant_item = ParticipantItem(participant)
                self.addItem(participant_item)
                self.participants_dict[participant] = participant_item
                self.participants.insert(-1, participant_item)

    def get_all_items(self):
        items = []

        for item in self.sim_items:
            if isinstance(item, RuleItem):
                items.extend(item.get_all_items())
            else:
                items.append(item)

        return items

    def get_all_messages(self):
        messages = [item for item in self.items() if isinstance(item, MessageItem)]

        return messages

    def arrange_participants(self):
        for participant in self.participants:
            for msg in self.get_all_messages():
                if msg.source == participant or msg.destination == participant:
                    participant.setVisible(True)
                    break
            else:
                participant.setVisible(False)
                participant.update(x_pos = 30)

        visible_participants = [part for part in self.participants if part.isVisible()]

        if not visible_participants:
            return

        visible_participants[0].update(x_pos = 0)

        for i in range(1, len(visible_participants)):
            curr_participant = visible_participants[i]
            participants_left = visible_participants[:i]

            items = [msg for msg in self.get_all_messages()
                    if ((msg.source == curr_participant and msg.destination in participants_left)
                    or (msg.source in participants_left and msg.destination == curr_participant))]

            x_max = visible_participants[i - 1].line.line().x1() + 50

            for msg in items:
                x = msg.labels_width() + 30
                x += msg.source.line.line().x1() if msg.source != curr_participant else msg.destination.line.line().x1()

                if x > x_max:
                    x_max = x

            curr_participant.update(x_pos = x_max)

    def arrange_items(self):
        x_pos = 0
        y_pos = 30

        for item in self.sim_proto_manager.rootItem.children:
            #print("YEP")
            scene_item = self.model_to_scene(item)
            scene_item.update_position(x_pos, y_pos)
            y_pos += round(scene_item.boundingRect().height())

        for participant in self.participants:
            participant.update(y_pos = max(y_pos, 50))

    def dragMoveEvent(self, event: QGraphicsSceneDragDropEvent):
        super().dragMoveEvent(event)
        event.setAccepted(True)

    def insert_at(self, ref_item, position, insert_rule=False):
        if ref_item:        
            ref_item = ref_item.model_item

        if ref_item is None:
            parent_item = None
            insert_position = self.sim_proto_manager.n_top_level_items()
        elif insert_rule:
            parent_item = None

            while ref_item.parent != self.sim_proto_manager.rootItem:
                ref_item = ref_item.parent

            insert_position = ref_item.get_pos()
        elif isinstance(ref_item, SimulatorRuleCondition):
            if position == QAbstractItemView.OnItem:
                parent_item = ref_item
                insert_position = parent_item.childCount()
            else:
                parent_item = None
                insert_position = ref_item.parent.get_pos()
        else:
            parent_item = ref_item.parent
            insert_position = ref_item.get_pos()

        if position == QAbstractItemView.BelowItem:
            insert_position += 1

        return (insert_position, parent_item)

    def dropEvent(self, event: QDropEvent):
        items = [item for item in self.items(event.scenePos()) if isinstance(item, SimulatorGraphicsItem)]
        item = None if len(items) == 0 else items[0]

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
        rule = RuleItem()
        self.insert_at(ref_item, position, rule, True)
        self.update_view()

    def add_action(self, ref_item, position, type):
        action = ActionItem(type)
        self.insert_at(ref_item, position, action, True)
        self.update_view()

    def add_goto_action(self, ref_item, position):
        goto_action = GotoAction()
        self.insert_at(ref_item, position, goto_action, True)
        self.update_view()

    def add_external_program_action(self, ref_item, position):
        external_program_action = ExternalProgramAction()
        self.insert_at(ref_item, position, external_program_action, True)
        self.update_view()

    def add_message(self, ref_item, position, source=None, destination=None, message_type=[]):
        if source is None:
            source = self.not_assigned_part

        if destination is None:
            destination = self.broadcast_part

        simulator_message = MessageItem(source, destination)

        for label in message_type:
            simulator_message.add_item(label.name, label.color_index, label.type)

        self.insert_at(ref_item, position, simulator_message, True)

        self.update_view()
        return simulator_message

    def add_message_from_message(self, ref_item, position, message, source=None, destination=None):
        #if source is None:
        #    source = self.not_assigned_part

        #if destination is None:
        #    destination = self.broadcast_part

        #simulator_message = MessageItem(source, destination)

        #start = 0

        #for label in message.message_type:
        #    if label.start > start:
        #        simulator_message.add_item(is_unlabeled_data=True, plain_bits=message.plain_bits[start:label.start])

        #    simulator_message.add_item(label.name, label.color_index, label.type)
        #    start = label.end

        #if start < len(message) - 1:
        #    simulator_message.add_item(is_unlabeled_data=True, plain_bits=message.plain_bits[start:len(message)])

        self.insert_at(ref_item, position, simulator_message, True)

        self.update_view()
        return simulator_message

    def clear_all(self):
        for item in self.sim_items[:]:
            self.sim_items.remove(item)
            self.removeItem(item)

        self.update_view()

    def add_protocols(self, ref_item, position, protocols_to_add: list):
        pos, parent = self.insert_at(ref_item, position)

        for protocol in protocols_to_add:
            for msg in protocol.messages:
                source, destination = self.detect_source_destination(msg)

                sim_message = self.sim_proto_manager.add_message(destination, msg.plain_bits, msg.pause,
                    MessageType(msg.message_type.name), msg.decoder, source, pos, parent)

                for lbl in msg.message_type:
                    self.sim_proto_manager.add_label(lbl.name, lbl.start, lbl.end, lbl.color_index,
                        lbl.type, sim_message)

    def cut_selected_messages(self):
        messages = []

        for item in self.sim_items[:]:
            if type(item) is RuleItem:
                messages.extend(item.cut_selected_messages())
            elif item.isSelected():
                messages.append(item)
                self.sim_items.remove(item)

        return messages

    def detect_source_destination(self, message: Message):
        # TODO: use SRC_ADDRESS and DST_ADDRESS labels
        participants = self.sim_proto_manager.participants

        source = None
        destination = self.sim_proto_manager.broadcast_part

        if len(participants) == 1:
            source = participants[0]
        elif len(participants) > 1:
            if message.participant:
                source = message.participant
                destination = participants[0] if message.participant == participants[1] else participants[1]
            else:
                source = participants[0]
                destination = participants[1]

        return (source, destination)