from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItemGroup, QGraphicsSceneDragDropEvent, QGraphicsItem, QMenu, QAction, QActionGroup, QGraphicsObject, QAbstractItemView, QApplication
from PyQt5.QtGui import QPen, QDragEnterEvent, QDropEvent, QPolygonF, QColor, QFont, QFontDatabase, QTransform, QBrush
from PyQt5.QtCore import Qt, QRectF, QSizeF, QPointF, QSizeF, pyqtSignal, pyqtSlot, QLineF
import math
from enum import Enum

from urh import constants
from urh.signalprocessing.Message import Message

class SimulatorItem(QGraphicsObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.hover_active = False
        self.drag_over = False
        self.setAcceptHoverEvents(True)
        self.setAcceptDrops(True)
        self.drop_indicator_line = QLineF()
        self.bounding_rect = QRectF()
        self.item_under_mouse = None

    def hoverEnterEvent(self, event):
        self.hover_active = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.hover_active = False
        self.update()

    def dragEnterEvent(self, event: QGraphicsSceneDragDropEvent):
        self.drag_over = True
        self.update()

    def dragLeaveEvent(self, event: QGraphicsSceneDragDropEvent):
        self.drag_over = False
        self.update()

    def dropEvent(self, event: QDropEvent):
        self.drag_over = False
        self.update()

    def dragMoveEvent(self, event: QDropEvent):
        self.update_drop_indicator(event.pos())

    def parent_item(self):
        if isinstance(self, RuleConditionItem):
            return self
        else:
            return self.parentItem()

    def update_drop_indicator(self, pos):
        rect = self.boundingRect()

        if pos.y() - rect.top() < rect.height() / 2:
            self.drop_indicator_position = QAbstractItemView.AboveItem
            self.drop_indicator_line = QLineF(rect.topLeft(), rect.topRight())
        else:
            self.drop_indicator_position = QAbstractItemView.BelowItem
            self.drop_indicator_line = QLineF(rect.bottomLeft(), rect.bottomRight())

        self.update()

    def paint(self, painter, option, widget):
        if self.hover_active or self.isSelected():
            painter.setOpacity(constants.SELECTION_OPACITY)
            painter.setBrush(constants.SELECTION_COLOR)
            painter.setPen(QPen(QColor(Qt.transparent), Qt.FlatCap))
            painter.drawRect(self.boundingRect())

        if self.drag_over:
            self.paint_drop_indicator(painter)

    def paint_drop_indicator(self, painter):
        brush = QBrush(QColor(Qt.darkRed))
        pen = QPen(brush, 2, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(self.drop_indicator_line)

    def refresh(self, x_pos, y_pos):
        width = self.scene().participants[-1].line.line().x1()
        width -= self.scene().participants[0].line.line().x1()
        self.prepareGeometryChange()
        self.bounding_rect = QRectF(0, 0, width, self.childrenBoundingRect().height())

    def boundingRect(self):
        return self.bounding_rect

    def mouseMoveEvent(self, event):
        items = [item for item in self.scene().items(event.scenePos()) if isinstance(item, SimulatorItem) and item != self]
        item = None if len(items) == 0 else items[0]

        if self.item_under_mouse and self.item_under_mouse != item:
            self.item_under_mouse.dragLeaveEvent(None)
            self.item_under_mouse = None

            if item:
                self.item_under_mouse = item
                self.item_under_mouse.dragEnterEvent(None)
        elif self.item_under_mouse and self.item_under_mouse == item:
            self.item_under_mouse.update_drop_indicator(self.mapToItem(self.item_under_mouse, event.pos()))
        elif item:
            self.item_under_mouse = item
            self.item_under_mouse.dragEnterEvent(None)          

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.item_under_mouse:
            self.item_under_mouse.dragLeaveEvent(None)
            selected_items = self.scene().cut_selected_messages()
            parent_item = self.item_under_mouse.parent_item()

            if parent_item == None:
                position = self.scene().sim_items.index(self.item_under_mouse)
            elif isinstance(self.item_under_mouse, RuleConditionItem):
                position = len(parent_item.sim_items)
            else:
                position = parent_item.sim_items.index(self.item_under_mouse)

            if self.item_under_mouse.drop_indicator_position == QAbstractItemView.BelowItem:
                position += 1

            for item in selected_items:
                if parent_item:
                    parent_item.sim_items.insert(position, item)
                else:
                    self.scene().sim_items.insert(position, item)

                item.setParentItem(parent_item)
                position += 1
                
            self.item_under_mouse = None

        super().mouseReleaseEvent(event)
        self.scene().update_view()

class ConditionType(Enum):
    IF = "if ..."
    ELSE_IF = "else if ..."
    ELSE = "else"

class RuleItem(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.conditions = []
        self.bounding_rect = QRectF()
        self.conditions.append(RuleConditionItem(ConditionType.IF, self))

    def has_else_condition(self):
        return len([cond for cond in self.conditions if cond.type is ConditionType.ELSE]) == 1

    def get_all_messages(self):
        messages = []

        for cond in self.conditions:
            messages.extend([item for item in cond.sim_items if type(item) is MessageItem])

        return messages

    def cut_selected_messages(self):
        messages = []

        for cond in self.conditions:
            for item in cond.sim_items[:]:
                if item.isSelected():
                    messages.append(item)
                    cond.sim_items.remove(item)

        return messages

    def add_else_cond(self):
        self.conditions.append(RuleConditionItem(ConditionType.ELSE, self))

    def add_else_if_cond(self):
        self.conditions.append(RuleConditionItem(ConditionType.ELSE_IF, self))

    def setSelected(self, selected):
        for condition in self.conditions:
            condition.setSelected(selected)

    def delete_items(self, items):
        for condition in self.conditions[:]:
            if condition in items and condition.type == ConditionType.IF:
                self.scene().sim_items.remove(self)
                self.scene().removeItem(self)
                return
            elif condition in items:
                self.conditions.remove(condition)
                self.scene().removeItem(condition)
            else:
                condition.delete_items(items)

    def refresh(self, x_pos, y_pos):
        self.setPos(x_pos - 20, y_pos)

        if_cond = [cond for cond in self.conditions if cond.type is ConditionType.IF][0]

        start_y = 0
        if_cond.refresh(0, start_y)
        start_y += round(if_cond.boundingRect().height())

        for cond in [cond for cond in self.conditions if cond.type is ConditionType.ELSE_IF]:
            cond.refresh(0, start_y)
            start_y += round(cond.boundingRect().height())

        else_cond = [cond for cond in self.conditions if cond.type is ConditionType.ELSE]

        if len(else_cond) == 1:
            else_cond[0].refresh(0, start_y)

        self.prepareGeometryChange()
        self.bounding_rect = self.childrenBoundingRect()

    def boundingRect(self):
        return self.bounding_rect

    def paint(self, painter, option, widget):
        pass

class RuleTextItem(QGraphicsTextItem):
    def __init__(self, text, color, parent=None):
        super().__init__(parent)
        self.color = color
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(10)
        font.setWeight(QFont.DemiBold)
        self.setFont(font)
        self.setPlainText(text)

    def paint(self, painter, option, widget):
        painter.setPen(QPen(QColor(Qt.transparent), Qt.FlatCap))
        painter.drawRect(self.boundingRect())
        super().paint(painter, option, widget)

class RuleConditionItem(SimulatorItem):
    def __init__(self, type, parent):
        super().__init__(parent)
        self.type = type
        self.text = RuleTextItem(type.value, QColor.fromRgb(139,148,148), self)
        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.sim_items = []

    def refresh(self, x_pos, y_pos):
        self.setPos(x_pos, y_pos)

        start_y = 0
        self.text.setPos(0, start_y)
        start_y += round(self.text.boundingRect().height())

        for item in self.sim_items:
            item.refresh(20, start_y)
            start_y += round(item.boundingRect().height())

        width = self.scene().participants[-1].line.line().x1()
        width -= self.scene().participants[0].line.line().x1()
        self.prepareGeometryChange()
        self.bounding_rect = QRectF(0, 0, width + 40, self.childrenBoundingRect().height())

    def paint(self, painter, option, widget):
        if self.hover_active or self.isSelected():
            painter.setOpacity(constants.SELECTION_OPACITY)
            painter.setBrush(constants.SELECTION_COLOR)
        else:
            painter.setOpacity(0.8)
            painter.setBrush(constants.LABEL_COLORS[-3])

        painter.setPen(QPen(Qt.darkGray, 1, Qt.DotLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawRect(self.boundingRect())

        if self.drag_over:
            self.paint_drop_indicator(painter)

    def delete_items(self, items):
        for item in self.sim_items[:]:
            if item in items:
                self.sim_items.remove(item)
                self.scene().removeItem(item)

class LabelItem(QGraphicsTextItem):
    def __init__(self, text, color, parent=None):
        super().__init__(parent)
        self.color = color
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(8)
        self.setFont(font)
        self.setPlainText(text)

    def paint(self, painter, option, widget):
        painter.setBrush(self.color)
        painter.drawRect(self.boundingRect())
        super().paint(painter, option, widget)

    @property
    def name(self):
        return self.toPlainText()

    @property
    def value(self):
        return "1::seq + 1"

class DataItem(QGraphicsTextItem):
    def __init__(self, plain_bits, parent=None):
        super().__init__(parent)
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(8)
        self.setFont(font)
        self.setPlainText("...")

        self.__plain_bits = plain_bits

    @property
    def plain_bits(self):
        """

        :rtype: list[bool]
        """
        return self.__plain_bits

    def __str__(self):
        return self.bits2string(self.plain_bits)

    def bits2string(self, bits) -> str:
        """

        :type bits: list[bool]
        """
        return "".join("1" if bit else "0" for bit in bits)

    @property
    def name(self):
        return "[Unlabeled data]"

    @property
    def value(self):
        return str(self)

class ActionType(Enum):
    external_program = 0
    goto = 1

class ActionItem(SimulatorItem):
    def __init__(self, type, parent=None):
        super().__init__(parent)
        self.text = QGraphicsTextItem(self)

        self.type = type

        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(8)
        font.setWeight(QFont.DemiBold)
        self.text.setFont(font)
        self.setFlag(QGraphicsItem.ItemIsMovable)

        if type == ActionType.external_program:
            self.text.setPlainText("Start program [/usr/bin/test]")
        elif type == ActionType.goto:
            self.text.setPlainText("goto 6")

    def refresh(self, x_pos, y_pos):
        self.setPos(x_pos, y_pos)
        self.text.setPos(0, 0)
        super().refresh(x_pos, y_pos)

class ParticipantItem(QGraphicsItem):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.text = QGraphicsTextItem(name, self)
        self.line = QGraphicsLineItem(self)
        self.line.setPen(QPen(Qt.darkGray, 1, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))

    def update(self, x_pos = -1, y_pos = -1):
        if x_pos == -1:
            x_pos = self.line.line().x1()

        if y_pos == -1:
            y_pos = self.line.line().y2()

        self.text.setPos(x_pos - (self.text.boundingRect().width() / 2), 0)
        self.line.setLine(x_pos, 30, x_pos, y_pos)
        super().update()

    def boundingRect(self):
        return self.childrenBoundingRect()

    def paint(self, painter, option, widget):
        pass

class MessageItem(SimulatorItem):
    def __init__(self, source, destination, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsPanel, True)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.arrow = MessageArrowItem(self)
        self.source = source
        self.destination = destination
        self.labels = []

    def labels_width(self):
        width = sum([lbl.boundingRect().width() for lbl in self.labels])
        width += 5 * (len(self.labels) - 1)
        return width

    def add_item(self, item):
        item.setParentItem(self)
        self.labels.append(item)

    def refresh(self, x_pos, y_pos):
        self.setPos(QPointF(x_pos, y_pos))

        p_source = self.mapFromItem(self.source.line, self.source.line.line().p1())
        p_destination = self.mapFromItem(self.destination.line, self.destination.line.line().p1())

        arrow_width = abs(p_source.x() - p_destination.x())

        start_x = min(p_source.x(), p_destination.x())
        start_x += (arrow_width - self.labels_width()) / 2
        start_y = 0

        for label in self.labels:
            label.setPos(start_x, start_y)
            start_x += label.boundingRect().width() + 5

        if len(self.labels) > 0:
            start_y += self.labels[0].boundingRect().height() + 5
        else:
            start_y += 7

        self.arrow.setLine(p_source.x(), start_y, p_destination.x(), start_y)
        super().refresh(x_pos, y_pos)

class MessageArrowItem(QGraphicsLineItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

    def boundingRect(self):
        return super().boundingRect().adjusted(0, -7, 0, 7)

    def paint(self, painter, option, widget):
        if self.line().length() == 0:
            return

        myPen = self.pen()
        myPen.setColor(Qt.black)
        arrowSize = 10.0
        painter.setPen(myPen)
        painter.setBrush(Qt.black)

        angle = math.acos(self.line().dx() / self.line().length())

        if self.line().dy() >= 0:
            angle = (math.pi * 2) - angle

        arrowP1 = self.line().p2() - QPointF(math.sin(angle + math.pi / 2.5) * arrowSize,
                    math.cos(angle + math.pi / 2.5) * arrowSize)

        arrowP2 = self.line().p2() - QPointF(math.sin(angle + math.pi - math.pi / 2.5) * arrowSize,
                    math.cos(angle + math.pi - math.pi / 2.5) * arrowSize)

        arrowHead = QPolygonF()
        arrowHead.append(self.line().p2())
        arrowHead.append(arrowP1)
        arrowHead.append(arrowP2)

        painter.drawLine(self.line())
        painter.drawPolygon(arrowHead)

class SimulatorScene(QGraphicsScene):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.tree_root_item = None

        self.participants_dict = {}
        self.participants = []

        self.not_assigned_part = ParticipantItem("?")
        self.participants.append(self.not_assigned_part)
        self.addItem(self.not_assigned_part)

        self.broadcast_part = ParticipantItem("Broadcast")
        self.participants.append(self.broadcast_part)
        self.addItem(self.broadcast_part)

        self.sim_items = []
        self.update_view()

    def delete_selected_items(self):
        self.delete_items(self.selectedItems())
        self.update_view()

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

    def update_view(self):
        self.update_participants(self.controller.project_manager.participants)

        items = [msg for msg in self.get_all_messages() if (msg.source not in self.participants) or (msg.destination not in self.participants)]
        self.delete_items(items)

        self.arrange_participants()
        self.arrange_items()

        # resize scrollbar
        self.setSceneRect(self.itemsBoundingRect().adjusted(-10, 0 , 0, 0))

    def update_participants(self, participants):
        for key in list(self.participants_dict.keys()):
            if key not in participants:
                self.removeItem(self.participants_dict[key])
                self.participants.remove(self.participants_dict[key])
                del self.participants_dict[key]

        for participant in participants:
            if participant in self.participants_dict:
                participant_item = self.participants_dict[participant]
                participant_item.text.setPlainText(participant.shortname)
            else:
                participant_item = ParticipantItem(participant.shortname)
                self.addItem(participant_item)
                self.participants_dict[participant] = participant_item
                self.participants.insert(-2, participant_item)

    def get_all_messages(self):
        messages = []

        for item in self.sim_items:
            if type(item) is MessageItem:
                messages.append(item)
            elif type(item) is RuleItem:
                messages.extend(item.get_all_messages())

        return messages

    def arrange_participants(self):
        self.participants[0].update(x_pos = 0)

        for i in range(1, len(self.participants)):
            curr_participant = self.participants[i]
            participants_left = self.participants[:i]

            items = [msg for msg in self.get_all_messages()
                    if ((msg.source == curr_participant and msg.destination in participants_left)
                    or (msg.source in participants_left and msg.destination == curr_participant))]

            x_max = self.participants[i - 1].line.line().x1() + 50

            for msg in items:
                x = msg.labels_width() + 30
                x += msg.source.line.line().x1() if msg.source != curr_participant else msg.destination.line.line().x1()

                if x > x_max:
                    x_max = x

            curr_participant.update(x_pos = x_max)

    def arrange_items(self):
        x_pos = self.participants[0].line.line().x1()
        y_pos = 30

        for item in self.sim_items:
            item.refresh(x_pos, y_pos)
            y_pos += round(item.boundingRect().height())

        for participant in self.participants:
            participant.update(y_pos = max(y_pos, 50))

    def dragMoveEvent(self, event: QGraphicsSceneDragDropEvent):
        super().dragMoveEvent(event)
        event.setAccepted(True)

    def dropEvent(self, event: QDropEvent):
        items = [item for item in self.items(event.scenePos()) if isinstance(item, SimulatorItem)]
        item = None if len(items) == 0 else items[0]

        if item == None:
            parent_item = None
        else:
            parent_item = item.parent_item()

        if item == None:
            position = len(self.sim_items)
        elif parent_item == None:
            position = self.sim_items.index(item)
        elif isinstance(item, RuleConditionItem):
            position = len(parent_item.sim_items)
        else:
            position = parent_item.sim_items.index(item)

        if item and item.drop_indicator_position == QAbstractItemView.BelowItem:
            position += 1

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

        self.add_protocols(parent_item, position, protocols_to_add)
        self.update_view()
        super().dropEvent(event)

    def add_rule(self, position):
        rule = RuleItem()
        self.sim_items.insert(position, rule)
        self.addItem(rule)
        self.update_view()

    def add_action(self, parent_item, position, type):
        target_list = self.sim_items if parent_item is None else parent_item.sim_items
        action = ActionItem(type, parent_item)
        target_list.insert(position, action)

        if parent_item is None:
            self.addItem(action)

        self.update_view()

    def add_message(self, parent_item, position, source=None, destination=None, message_type=[]):
        if source == None:
            source = self.not_assigned_part

        if destination == None:
            destination = self.broadcast_part

        target_list = self.sim_items if parent_item is None else parent_item.sim_items

        simulator_message = MessageItem(source, destination, parent_item)

        for label in message_type:
            simulator_message.add_item(LabelItem(label.name, constants.LABEL_COLORS[label.color_index]))

        target_list.insert(position, simulator_message)

        if parent_item is None:
            self.addItem(simulator_message)

        self.update_view()

    def add_message_from_message(self, parent_item, position, message, source=None, destination=None):
        if source == None:
            source = self.not_assigned_part

        if destination == None:
            destination = self.broadcast_part

        target_list = self.sim_items if parent_item is None else parent_item.sim_items

        simulator_message = MessageItem(source, destination, parent_item)

        start = 0

        for label in message.message_type:
            if label.start > start:
                simulator_message.add_item(DataItem(message.plain_bits[start:label.start]))

            simulator_message.add_item(LabelItem(label.name, constants.LABEL_COLORS[label.color_index]))
            start = label.end

        if start < len(message) - 1:
            simulator_message.add_item(DataItem(message.plain_bits[start:len(message)]))

        target_list.insert(position, simulator_message)

        if parent_item is None:
            self.addItem(simulator_message)

        self.update_view()

    def clear_all(self):
        for item in self.sim_items[:]:
            self.sim_items.remove(item)
            self.removeItem(item)

        self.update_view()

    def add_protocols(self, parent_item, position, protocols_to_add: list):
        for protocol in protocols_to_add:
            for message in protocol.messages:
                source, destination = self.detect_source_destination(message)

                self.add_message_from_message(parent_item, position, message, source, destination)
                position += 1

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
        participants = self.controller.project_manager.participants

        source = self.not_assigned_part
        destination = self.broadcast_part

        if len(participants) == 1:
            source = self.participants_dict[participants[0]]
            destination = self.broadcast_part
        else:
            if message.participant:
                source = self.participants_dict[message.participant]
                destination = self.participants_dict[participants[0]] if message.participant == participants[1] else self.participants_dict[participants[1]]
            else:
                source = self.participants_dict[participants[0]]
                destination = self.participants_dict[participants[1]]

        return (source, destination)