from PyQt5.QtCore import Qt, QRectF, QLineF
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QGraphicsTextItem, QAbstractItemView

from urh import settings
from urh.simulator.GraphicsItem import GraphicsItem
from urh.simulator.SimulatorRule import (
    SimulatorRule,
    SimulatorRuleCondition,
    ConditionType,
)


class RuleItem(GraphicsItem):
    def __init__(self, model_item: SimulatorRule, parent=None):
        assert isinstance(model_item, SimulatorRule)
        super().__init__(model_item=model_item, parent=parent)

    @property
    def has_else_condition(self) -> bool:
        return self.model_item.has_else_condition

    def update_numbering(self):
        for child in self.get_scene_children():
            child.update_numbering()

    def update_position(self, x_pos, y_pos):
        self.setPos(x_pos - 20, y_pos)

        start_y = 5

        for child in self.get_scene_children():
            child.update_position(0, start_y)
            start_y += round(child.boundingRect().height()) - 1

        self.prepareGeometryChange()
        self.bounding_rect = self.childrenBoundingRect().adjusted(0, 0, 0, 10)

    def boundingRect(self):
        return self.bounding_rect

    def paint(self, painter, option, widget):
        pass


class RuleConditionItem(GraphicsItem):
    def __init__(self, model_item: SimulatorRuleCondition, parent=None):
        assert isinstance(model_item, SimulatorRuleCondition)
        super().__init__(model_item=model_item, parent=parent)

        self.number.setFont(self.font_bold)

        self.text = QGraphicsTextItem(self)
        self.text.setPlainText(self.model_item.type.value)
        self.text.setFont(self.font_bold)

        self.desc = QGraphicsTextItem(self)
        self.desc.setFont(self.font)

    def update_flags(self):
        if self.scene().mode == 0:
            self.set_flags(
                is_selectable=True, accept_hover_events=True, accept_drops=True
            )
        else:
            self.set_flags(is_selectable=True, accept_hover_events=True)

    def labels_width(self):
        return max(
            self.number.boundingRect().width() + self.text.boundingRect().width(),
            self.desc.boundingRect().width(),
        )

    def refresh(self):
        if len(self.model_item.condition):
            if len(self.model_item.condition) > 20:
                self.desc.setPlainText(self.model_item.condition[:20] + "...")
            else:
                self.desc.setPlainText(self.model_item.condition)
        elif self.model_item.type != ConditionType.ELSE:
            self.desc.setPlainText("<Condition>")

    def update_position(self, x_pos, y_pos):
        self.setPos(x_pos, y_pos)

        start_y = 0
        start_x = (
            (self.scene().items_width() + 40)
            - (self.number.boundingRect().width() + self.text.boundingRect().width())
        ) / 2
        self.number.setPos(start_x, start_y)
        start_x += self.number.boundingRect().width()
        self.text.setPos(start_x, start_y)
        start_y += round(self.number.boundingRect().height())
        start_x = (
            (self.scene().items_width() + 40) - self.desc.boundingRect().width()
        ) / 2
        self.desc.setPos(start_x, start_y)

        if self.model_item.type != ConditionType.ELSE:
            start_y += round(self.desc.boundingRect().height())

        start_y += 5

        for child in self.get_scene_children():
            child.update_position(20, start_y)
            start_y += round(child.boundingRect().height())

        width = self.scene().items_width()
        self.prepareGeometryChange()
        self.bounding_rect = QRectF(
            0, 0, width + 40, self.childrenBoundingRect().height() + 5
        )

    def update_drop_indicator(self, pos):
        rect = self.boundingRect()

        if pos.y() - rect.top() < rect.height() / 3:
            self.drop_indicator_position = QAbstractItemView.AboveItem
        elif rect.bottom() - pos.y() < rect.height() / 3:
            self.drop_indicator_position = QAbstractItemView.BelowItem
        else:
            self.drop_indicator_position = QAbstractItemView.OnItem

        self.update()

    def paint(self, painter, option, widget):
        if self.scene().mode == 1:
            self.setOpacity(1 if self.model_item.logging_active else 0.3)

        painter.setOpacity(settings.SELECTION_OPACITY)

        if self.hover_active or self.isSelected():
            painter.setBrush(settings.SELECTION_COLOR)
        elif not self.is_valid():
            painter.setBrush(QColor(255, 0, 0, 150))
        else:
            painter.setBrush(QColor.fromRgb(204, 204, 204, 255))

        height = self.number.boundingRect().height()

        if self.model_item.type != ConditionType.ELSE:
            height += self.desc.boundingRect().height()

        painter.drawRect(QRectF(0, 0, self.boundingRect().width(), height))

        painter.setBrush(Qt.NoBrush)
        painter.drawRect(self.boundingRect())

        if self.drag_over:
            self.paint_drop_indicator(painter)

    def paint_drop_indicator(self, painter):
        painter.setPen(QPen(Qt.darkRed, 2, Qt.SolidLine))
        painter.setBrush(Qt.NoBrush)
        rect = self.boundingRect()

        if self.drop_indicator_position == QAbstractItemView.AboveItem:
            painter.drawLine(QLineF(rect.topLeft(), rect.topRight()))
        elif self.drop_indicator_position == QAbstractItemView.OnItem:
            painter.drawRect(rect)
        else:
            painter.drawLine(QLineF(rect.bottomLeft(), rect.bottomRight()))
