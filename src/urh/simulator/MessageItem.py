from urh import constants
from urh.simulator.GraphicsItem import GraphicsItem
from urh.simulator.SimulatorMessage import SimulatorMessage
from urh.simulator.UnlabeledRangeItem import UnlabeledRangeItem

from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem, QGraphicsLineItem
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPen, QPolygonF

import math


class MessageItem(GraphicsItem):
    def __init__(self, model_item: SimulatorMessage, parent=None):
        assert isinstance(model_item, SimulatorMessage)
        super().__init__(model_item=model_item, parent=parent)

        self.setFlag(QGraphicsItem.ItemIsPanel, True)
        self.arrow = MessageArrowItem(self)

        self.repeat_text = QGraphicsTextItem(self)
        self.repeat_text.setFont(self.font)

    def update_flags(self):
        if self.scene().mode == 0:
            self.set_flags(is_selectable=True, is_movable=True, accept_hover_events=True, accept_drops=True)

    def width(self):
        labels = self.labels()
        width = self.number.boundingRect().width()
        # width += 5
        width += sum([lbl.boundingRect().width() for lbl in labels])
        width += 5 * (len(labels) - 1)
        width += self.repeat_text.boundingRect().width()

        return width

    def refresh(self):
        self.repeat_text.setPlainText("(" + str(self.model_item.repeat) + "x)" if self.model_item.repeat > 1 else "")

    def labels(self):
        self.refresh_unlabeled_range_marker()
        unlabeled_range_items = [uri for uri in self.childItems() if isinstance(uri, UnlabeledRangeItem)]
        result = []

        start = 0
        i = 0

        message = self.model_item

        if len(message) and not message.message_type:
            result.append(unlabeled_range_items[0])
        else:
            for lbl in message.message_type:
                if lbl.start > start:
                    result.append(unlabeled_range_items[i])
                    i += 1

                result.append(self.scene().model_to_scene(lbl))
                start = lbl.end

            if start < len(message):
                result.append(unlabeled_range_items[i])

        return result

    def refresh_unlabeled_range_marker(self):
        msg = self.model_item

        urm = [item for item in self.childItems() if isinstance(item, UnlabeledRangeItem)]

        if len(msg):
            num_unlabeled_ranges = len(msg.message_type.unlabeled_ranges)

            if msg.message_type and msg.message_type[-1].end >= len(msg):
                num_unlabeled_ranges -= 1
        else:
            num_unlabeled_ranges = 0

        if len(urm) < num_unlabeled_ranges:
            for i in range(num_unlabeled_ranges - len(urm)):
                UnlabeledRangeItem(self)
        else:
            for i in range(len(urm) - num_unlabeled_ranges):
                self.scene().removeItem(urm[i])

    def update_position(self, x_pos, y_pos):
        labels = self.labels()
        self.setPos(QPointF(x_pos, y_pos))

        p_source = self.mapFromItem(self.source.line, self.source.line.line().p1())
        p_destination = self.mapFromItem(self.destination.line, self.destination.line.line().p1())

        arrow_width = abs(p_source.x() - p_destination.x())

        start_x = min(p_source.x(), p_destination.x())
        start_x += (arrow_width - self.width()) / 2
        start_y = 0

        self.number.setPos(start_x, start_y)
        start_x += self.number.boundingRect().width()

        for label in labels:
            label.setPos(start_x, start_y)
            start_x += label.boundingRect().width() + 5

        self.repeat_text.setPos(start_x, start_y)

        if labels:
            start_y += labels[0].boundingRect().height() + 5
        else:
            start_y += 26

        self.arrow.setLine(p_source.x(), start_y, p_destination.x(), start_y)
        super().update_position(x_pos, y_pos)

    @property
    def source(self):
        return self.scene().participants_dict[self.model_item.participant]

    @property
    def destination(self):
        return self.scene().participants_dict[self.model_item.destination]


class MessageArrowItem(QGraphicsLineItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

    def boundingRect(self):
        return super().boundingRect().adjusted(0, -5, 0, 5)

    def paint(self, painter, option, widget):
        if self.line().length() == 0:
            return

        pen = self.pen()
        pen.setColor(constants.LINECOLOR)
        painter.setPen(pen)
        painter.setBrush(constants.LINECOLOR)

        arrow_size = 10.0

        angle = math.acos(self.line().dx() / self.line().length())

        if self.line().dy() >= 0:
            angle = (math.pi * 2) - angle

        arrow_p1 = self.line().p2() - QPointF(math.sin(angle + math.pi / 2.5) * arrow_size,
                                              math.cos(angle + math.pi / 2.5) * arrow_size)

        arrow_p2 = self.line().p2() - QPointF(math.sin(angle + math.pi - math.pi / 2.5) * arrow_size,
                                              math.cos(angle + math.pi - math.pi / 2.5) * arrow_size)

        arrow_head = QPolygonF()
        arrow_head.append(self.line().p2())
        arrow_head.append(arrow_p1)
        arrow_head.append(arrow_p2)

        painter.drawLine(self.line())
        painter.drawPolygon(arrow_head)
