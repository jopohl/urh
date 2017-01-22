from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItemGroup, QGraphicsSceneDragDropEvent
from PyQt5.QtGui import QPen, QDragEnterEvent, QDropEvent, QPolygonF, QColor, QFont
from PyQt5.QtCore import Qt, QRectF, QSizeF, QPointF, QSizeF
import math

from urh import constants

class LabelTextItem(QGraphicsTextItem):
    def __init__(self, parent, color):
        self.color = color
        super().__init__(parent)

    def paint(self, painter, option, widget):
        painter.setBrush(self.color)
        painter.drawRect(self.boundingRect())
        super().paint(painter, option, widget)

class MessageArrowItem(QGraphicsLineItem):

    def __init__(self, parent=None, source=None, destination=None):
        super().__init__(parent)
        self.myColor = Qt.black
        self.setPen(QPen(self.myColor, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.arrowHead = QPolygonF()
        self.source = source
        self.destination = destination

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0

        return QRectF(self.line().p1(), QSizeF(self.line().p2().x() - self.line().p1().x(), self.line().p2().y() - self.line().p1().y())).normalized().adjusted(-extra, -extra, extra, extra)


    def shape(self):
        path = super().shape()
        path.addPolygon(self.arrowHead)
        return path

    def paint(self, painter, option, widget):
        if self.line().length() == 0:
            return

        myPen = self.pen()
        myPen.setColor(self.myColor)
        arrowSize = 10.0
        painter.setPen(myPen)
        painter.setBrush(self.myColor)

        angle = math.acos(self.line().dx() / self.line().length())
        if self.line().dy() >= 0:
            angle = (math.pi * 2) - angle

        arrowP1 = self.line().p2() - QPointF(math.sin(angle + math.pi / 2.5) * arrowSize, math.cos(angle + math.pi / 2.5) * arrowSize)
        arrowP2 = self.line().p2() - QPointF(math.sin(angle + math.pi - math.pi / 2.5) * arrowSize, math.cos(angle + math.pi - math.pi / 2.5) * arrowSize)

        self.arrowHead.clear()
        self.arrowHead.append(self.line().p2())
        self.arrowHead.append(arrowP1)
        self.arrowHead.append(arrowP2)
        painter.drawLine(self.line())
        painter.drawPolygon(self.arrowHead)

class SimulatorScene(QGraphicsScene):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.tree_root_item = None
        self.participants_dict = {}
        self.participants = []
        self.messages_dict = {}
        self.messages = []

    def update_participants(self, participants):
        for key in list(self.participants_dict.keys()):
            if key not in participants:
                for child in self.participants_dict[key].childItems():
                    self.removeItem(child)

                self.participants.remove(self.participants_dict[key])
                self.destroyItemGroup(self.participants_dict[key])
                del self.participants_dict[key]

        for participant in participants:
            if participant in self.participants_dict:
                text = self.participants_dict[participant].childItems()[0]
                text.setPlainText(participant.shortname)
            else:
                text = QGraphicsTextItem(participant.shortname)
                #text.setFont(QFont("Courier", 8))
                line = QGraphicsLineItem()
                line.setPen(QPen(Qt.darkGray, 1, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))
                part_group = QGraphicsItemGroup()
                part_group.addToGroup(text)
                part_group.addToGroup(line)
                self.addItem(part_group)
                self.participants_dict[participant] = part_group
                self.participants.append(part_group)

    def update_messages(self, messages):
        for key in list(self.messages_dict.keys()):
            if key not in messages:
                for child in self.messages_dict[key].childItems():
                    self.removeItem(child)

                self.messages.remove(self.messages_dict[key])
                self.destroyItemGroup(self.messages_dict[key])
                del self.messages_dict[key]

        for message in messages:
            if message in self.messages_dict:
                arrow = self.messages_dict[message].childItems()[0]
                #arrow.setPlainText(participant.shortname)
                arrow.source = self.participants_dict[message.source]
                arrow.destination = self.participants_dict[message.destination]
            else:
                arrow = MessageArrowItem()
                arrow.source = self.participants_dict[message.source]
                arrow.destination = self.participants_dict[message.destination]
                msg_group = QGraphicsItemGroup()
                msg_group.addToGroup(arrow)

                for label in message.labels:
                    label_item = LabelTextItem(None, constants.LABEL_COLORS[label.color_index])
                    label_item.setPlainText("[Auto]")
                   # label_item.setPos(start_x, start_y - label_item.boundingRect().height())
                    label_item.setFont(QFont("Courier", 8))
                    msg_group.addToGroup(label_item)

                self.addItem(msg_group)
                self.messages_dict[message] = msg_group
                self.messages.append(msg_group)

    def arrange_items(self):
        if len(self.participants) < 1:
            return

        text = self.participants[0].childItems()[0]
        text.setPos(50 - (text.boundingRect().width() / 2), 0)

        line = self.participants[0].childItems()[1]
        line.setLine(50, 30, 50, (len(self.messages) + 1) * 50)

        for i in range(1, len(self.participants)):
            curr_participant = self.participants[i]
            participants_left = self.participants[:i]
            messages = [msg for msg in self.messages
                    if (msg.childItems()[0].source == curr_participant and msg.childItems()[0].destination in participants_left)
                    or (msg.childItems()[0].source in participants_left and msg.childItems()[0].destination == curr_participant)]

            x_max = self.participants[i-1].childItems()[1].line().x1() + 50

            for msg in messages:
                width = sum([lbl.boundingRect().width() for lbl in msg.childItems()[1:]]) + 30
                width += 5 * (len(msg.childItems()[1:]) - 1)
                x = width + (msg.childItems()[0].source.childItems()[1].line().x1()
                    if msg.childItems()[0].source != curr_participant else msg.childItems()[0].destination.childItems()[1].line().x1())

                if x > x_max:
                    x_max = x

            text = curr_participant.childItems()[0]
            text.setPos(x_max - (text.boundingRect().width() / 2), 0)
            line = curr_participant.childItems()[1].setLine(x_max, 30, x_max, (len(self.messages) + 1) * 50)

        for i, message in enumerate(self.messages):
            source = message.childItems()[0].source
            destination = message.childItems()[0].destination
            message.childItems()[0].setLine(source.childItems()[1].line().x1(), (i + 1) * 50, destination.childItems()[1].line().x1(), (i + 1) * 50)

            labels_width = sum([lbl.boundingRect().width() for lbl in message.childItems()[1:]])
            labels_width += 5 * (len(message.childItems()[1:]) - 1)
            x = min(source.childItems()[1].line().x1(), destination.childItems()[1].line().x1())
            start_x = x + ((message.childItems()[0].line().length() - labels_width) / 2)
            start_y = (i + 1) * 50

            for label in message.childItems()[1:]:
                label.setPos(start_x, start_y - (label.boundingRect().height() + 5))
                start_x += label.boundingRect().width() + 5

    def dragEnterEvent(self, event: QGraphicsSceneDragDropEvent):
        event.setAccepted(True)

    def dragMoveEvent(self, event: QGraphicsSceneDragDropEvent):
        pass

    def dropEvent(self, event: QDropEvent):
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

        self.controller.add_protocols(protocols_to_add)

        super().dropEvent(event)