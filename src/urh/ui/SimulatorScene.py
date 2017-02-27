from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItemGroup, QGraphicsSceneDragDropEvent, QGraphicsItem, QMenu, QAction, QActionGroup, QGraphicsObject, QAbstractItemView
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

    def hoverEnterEvent(self, event):
        self.hover_active = True
        super().update()

    def hoverLeaveEvent(self, event):
        self.hover_active = False
        super().update()

    def dragEnterEvent(self, event: QGraphicsSceneDragDropEvent):
        self.drag_over = True
        super().update()

    def dragLeaveEvent(self, event: QGraphicsSceneDragDropEvent):
        self.drag_over = False
        super().update()

    def dropEvent(self, event: QDropEvent):
        self.drag_over = False
        super().update()

    def dragMoveEvent(self, event: QDropEvent):
        rect = self.boundingRect()
        self.drop_indicator_position = self.position(event.pos(), rect)

        x1 = self.scene().participants[0].line.line().x1()
        x2 = self.scene().participants[-1].line.line().x1()

        if self.drop_indicator_position == QAbstractItemView.AboveItem:
            self.drop_indicator_line = QLineF(x1, rect.top(), x2, rect.top())
        else:
            self.drop_indicator_line = QLineF(x1, rect.bottom(), x2, rect.bottom())

        super().update()
        
    @staticmethod
    def position(pos, rect):
        if pos.y() - rect.top() < rect.height() / 2:
            return QAbstractItemView.AboveItem
        else:
            return QAbstractItemView.BelowItem

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

    def boundingRect(self):
        rect = self.childrenBoundingRect()
        x = self.scene().participants[0].line.line().x1()
        width = self.scene().participants[-1].line.line().x1() - x
        return QRectF(x, rect.y(), width, rect.height())

class ConditionType(Enum):
    IF = "if ..."
    ELSE_IF = "else if ..."
    ELSE = "else"

class RuleItem(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.conditions = []
        self.conditions.append(RuleConditionItem(ConditionType.IF, self))

    def has_else_condition(self):
        return len([cond for cond in self.conditions if cond.type is ConditionType.ELSE]) == 1

    def get_all_messages(self):
        messages = []

        for cond in self.conditions:
            messages.extend([item for item in cond.sim_items if type(item) is MessageItem])

        return messages

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

    def update(self, y_pos):
        if_cond = [cond for cond in self.conditions if cond.type is ConditionType.IF][0]

        if_cond.update(y_pos)
        y_pos += round(if_cond.boundingRect().height())

        for cond in [cond for cond in self.conditions if cond.type is ConditionType.ELSE_IF]:
            cond.update(y_pos)
            y_pos += round(cond.boundingRect().height())

        else_cond = [cond for cond in self.conditions if cond.type is ConditionType.ELSE]

        if len(else_cond) == 1:
            else_cond[0].update(y_pos)

        super().update()

    def boundingRect(self):
        return self.childrenBoundingRect()

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
        self.rect = QRectF()

    def update(self, y_pos):
        x = self.scene().participants[0].line.line().x1()
        tmp_y = y_pos

        width = self.scene().participants[-1].line.line().x1() - x
        self.prepareGeometryChange()
        self.text.setPos(-20, tmp_y)
        tmp_y += round(self.text.boundingRect().height())

        for item in self.sim_items:
            item.update(tmp_y)
            tmp_y += round(item.boundingRect().height())

        self.rect.setRect(x - 20, y_pos, width + 40, tmp_y - y_pos)
        super().update()

    def boundingRect(self):
        return self.rect

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

    @pyqtSlot()
    def on_add_message_action_triggered(self):
        source = self.scene().not_assigned_part
        destination = self.scene().broadcast_part

        if self.sender() in self.message_type_actions:
            message_type = self.message_type_actions[self.sender()]
        else:
            message_type = []
            
        simulator_message = MessageItem(source, destination, self)

        for label in message_type:
            simulator_message.add_label(LabelItem(label.name, constants.LABEL_COLORS[label.color_index]))

        self.sim_items.append(simulator_message)
        self.scene().update_view()

    @pyqtSlot()
    def on_add_goto_action_triggered(self):
        action = ActionItem(ActionType.goto, self)
        self.sim_items.append(action)
        self.scene().update_view()

    @pyqtSlot()
    def on_add_external_program_action_triggered(self):
        action = ActionItem(ActionType.external_program, self)
        self.sim_items.append(action)
        self.scene().update_view()

    @pyqtSlot()
    def on_add_else_if_cond_action_triggered(self):
        self.parentItem().conditions.append(RuleConditionItem(ConditionType.ELSE_IF, self.parentItem()))
        self.scene().update_view()

    @pyqtSlot()
    def on_add_else_cond_action_triggered(self):
        self.parentItem().conditions.append(RuleConditionItem(ConditionType.ELSE, self.parentItem()))
        self.scene().update_view()

    @pyqtSlot()
    def on_remove_rule_action_triggered(self):
        scene = self.scene()
        scene.sim_items.remove(self.parentItem())
        scene.removeItem(self.parentItem())
        scene.update_view()

    @pyqtSlot()
    def on_remove_cond_action_triggered(self):
        scene = self.scene()
        self.parentItem().conditions.remove(self)
        scene.removeItem(self)
        scene.update_view()

    def create_context_menu(self):
        menu = QMenu()

        add_message_action = menu.addAction("Add empty message")
        add_message_action.triggered.connect(self.on_add_message_action_triggered)

        message_type_menu = menu.addMenu("Add message with message type ...")
        self.message_type_actions = {}

        for message_type in self.scene().controller.proto_analyzer.message_types:
            action = message_type_menu.addAction(message_type.name)
            self.message_type_actions[action] = message_type
            action.triggered.connect(self.on_add_message_action_triggered)

        action_menu = menu.addMenu("Add action")
        add_goto_action = action_menu.addAction("Goto")
        add_goto_action.triggered.connect(self.on_add_goto_action_triggered)
        add_external_program_action = action_menu.addAction("External program")
        add_external_program_action.triggered.connect(self.on_add_external_program_action_triggered)

        menu.addSeparator()

        add_else_if_cond_action = menu.addAction("Add else if block")
        add_else_if_cond_action.triggered.connect(self.on_add_else_if_cond_action_triggered)

        if not self.parentItem().has_else_condition():
            add_else_cond_action = menu.addAction("Add else block")
            add_else_cond_action.triggered.connect(self.on_add_else_cond_action_triggered)

        menu.addSeparator()

        remove_rule_action = menu.addAction("Remove rule")
        remove_rule_action.triggered.connect(self.on_remove_rule_action_triggered)

        if self.type == ConditionType.ELSE_IF:
            remove_else_if_cond_action = menu.addAction("Remove else if block")
            remove_else_if_cond_action.triggered.connect(self.on_remove_cond_action_triggered)
        elif self.type == ConditionType.ELSE:
            remove_else_cond_action = menu.addAction("Remove else block")
            remove_else_cond_action.triggered.connect(self.on_remove_cond_action_triggered)

        return menu

    def contextMenuEvent(self, event):
        menu = self.create_context_menu()
        self.setSelected(True)
        action = menu.exec_(event.screenPos())

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

        if type == ActionType.external_program:
            self.text.setPlainText("Start program [/usr/bin/test]")
        elif type == ActionType.goto:
            self.text.setPlainText("goto 6")

    def update(self, y_pos):
        x_pos = self.scene().participants[0].line.line().x1()
        self.text.setPos(x_pos, y_pos)
        super().update()

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

        self.prepareGeometryChange()
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
        self.arrow = MessageArrowItem(self)
        self.source = source
        self.destination = destination
        self.labels = []

    def labels_width(self):
        width = sum([lbl.boundingRect().width() for lbl in self.labels])
        width += 5 * (len(self.labels) - 1)
        return width

    def add_label(self, label: LabelItem):
        label.setParentItem(self)
        self.labels.append(label)

    def update(self, y_pos):
        arrow_width = abs(self.source.line.line().x1() - self.destination.line.line().x1())

        start_x = min(self.source.line.line().x1(), self.destination.line.line().x1())
        start_x += (arrow_width - self.labels_width()) / 2

        self.prepareGeometryChange()

        for label in self.labels:
            label.setPos(start_x, y_pos)
            start_x += label.boundingRect().width() + 5

        if len(self.labels) > 0:
            y_pos += self.labels[0].boundingRect().height() + 5
        else:
            y_pos += 7

        self.arrow.setLine(self.source.line.line().x1(), y_pos, self.destination.line.line().x1(), y_pos)
        
        super().update()

    @pyqtSlot()
    def on_del_action_triggered(self):
        scene = self.scene()

        if self.parentItem() is None:
            scene.sim_items.remove(self)
        else:
            self.parentItem().sim_items.remove(self)

        scene.removeItem(self)
        scene.update_view()

    @pyqtSlot()
    def on_source_action_triggered(self):
        self.source = self.source_actions[self.sender()]
        self.scene().update_view()

    @pyqtSlot()
    def on_destination_action_triggered(self):
        self.destination = self.destination_actions[self.sender()]
        self.scene().update_view()

    @pyqtSlot()
    def on_swap_part_action_triggered(self):
        tmp = self.source
        self.source = self.destination
        self.destination = tmp
        self.scene().update_view()

    def create_context_menu(self):
        menu = QMenu()
        scene = self.scene()

        del_action = menu.addAction("Delete message")
        del_action.triggered.connect(self.on_del_action_triggered)

        menu.addSeparator()

        source_group = QActionGroup(scene)
        source_menu = menu.addMenu("Source")
        self.source_actions = {}

        for particpnt in scene.participants:
            if self.destination == particpnt:
                continue

            if particpnt == scene.broadcast_part:
                continue

            pa = source_menu.addAction(particpnt.text.toPlainText())
            pa.setCheckable(True)
            pa.setActionGroup(source_group)

            if self.source == particpnt:
                pa.setChecked(True)

            self.source_actions[pa] = particpnt
            pa.triggered.connect(self.on_source_action_triggered)

        destination_group = QActionGroup(scene)
        destination_menu = menu.addMenu("Destination")
        self.destination_actions = {}

        for particpnt in scene.participants:
            if self.source == particpnt:
                continue

            pa = destination_menu.addAction(particpnt.text.toPlainText())
            pa.setCheckable(True)
            pa.setActionGroup(destination_group)

            if self.destination == particpnt:
                pa.setChecked(True)

            self.destination_actions[pa] = particpnt
            pa.triggered.connect(self.on_destination_action_triggered)

        if self.destination != scene.broadcast_part:
            swap_part_action = menu.addAction("Swap source and destination")
            swap_part_action.triggered.connect(self.on_swap_part_action_triggered)

        return menu

    def contextMenuEvent(self, event):
        menu = self.create_context_menu()
        self.setSelected(True)
        action = menu.exec_(event.screenPos())

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
        y_pos = 30

        for item in self.sim_items:
            item.update(y_pos)
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
            position = len(self.sim_items)
        elif (isinstance(item, MessageItem) or isinstance(item, ActionItem)) and item.parentItem() is None:
            parent_item = None
            position = self.sim_items.index(item)

            if item.drop_indicator_position == QAbstractItemView.BelowItem:
                position += 1
        elif (isinstance(item, MessageItem) or isinstance(item, ActionItem)):
            parent_item = item.parentItem()
            position = parent_item.sim_items.index(item)

            if item.drop_indicator_position == QAbstractItemView.BelowItem:
                position += 1
        elif isinstance(item, RuleConditionItem):
            parent_item = item
            position = len(parent_item.sim_items)

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

    def add_rule(self):
        rule = RuleItem()
        self.sim_items.append(rule)
        self.addItem(rule)
        self.update_view()

    def add_action(self, type):
        action = ActionItem(type)
        self.sim_items.append(action)
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
            simulator_message.add_label(LabelItem(label.name, constants.LABEL_COLORS[label.color_index]))

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

                self.add_message(parent_item, position, source, destination, message.message_type)

    def detect_source_destination(self, message: Message):
        # TODO: use SRC_ADDRESS and DST_ADDRESS labels
        participants = self.controller.project_manager.participants

        source = None
        destination = None

        if len(participants) == 0:
            source = self.not_assigned_part
            destination = self.broadcast_part
        elif len(participants) == 1:
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