from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem, QAbstractItemView
from PyQt5.QtCore import Qt, QRectF, QLineF
from PyQt5.QtGui import QFontDatabase, QFont, QPen

from urh.signalprocessing.GraphicsItem import GraphicsItem
from urh.signalprocessing.SimulatorItem import SimulatorItem
from urh.signalprocessing.SimulatorRule import ConditionType

from urh import constants

class RuleItem(GraphicsItem):
    def __init__(self, model_item: SimulatorItem, parent=None):
        super().__init__(model_item=model_item, parent=parent)

        self.bounding_rect = QRectF()

    def has_else_condition(self):
        return self.model_item.has_else_condition()

    def update_numbering(self):
        for child in self.get_scene_children():
            child.update_numbering()

    def setSelected(self, selected):
        for child in self.get_scene_children():
            child.setSelected(selected)

    def update_position(self, x_pos, y_pos):
        self.setPos(x_pos - 20, y_pos)

        start_y = 0

        for child in self.get_scene_children():
            child.update_position(0, start_y)
            start_y += round(child.boundingRect().height())

        self.prepareGeometryChange()
        self.bounding_rect = self.childrenBoundingRect()

    def boundingRect(self):
        return self.bounding_rect

    def paint(self, painter, option, widget):
        pass

class RuleConditionItem(GraphicsItem):
    def __init__(self, model_item: SimulatorItem, parent=None):
        super().__init__(model_item=model_item, is_selectable=True, accept_hover_events=True, accept_drops=True, parent=parent)
        self.text = QGraphicsTextItem(self)
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(10)
        font.setWeight(QFont.DemiBold)
        self.text.setFont(font)

        self.refresh()

    def refresh(self):
        self.text.setPlainText(self.model_item.type.value)

    def update_position(self, x_pos, y_pos):
        self.setPos(x_pos, y_pos)

        start_y = 0
        self.number.setPos(0, start_y)
        self.text.setPos(self.number.boundingRect().width(), start_y)
        start_y += round(self.text.boundingRect().height())

        for child in self.get_scene_children():
            child.update_position(20, start_y)
            start_y += round(child.boundingRect().height())

        width = self.scene().items_width()
        self.prepareGeometryChange()
        self.bounding_rect = QRectF(0, 0, width + 40, self.childrenBoundingRect().height() + 20)

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