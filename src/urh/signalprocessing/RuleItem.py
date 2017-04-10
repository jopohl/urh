from enum import Enum

from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, QRectF

from urh.signalprocessing.SimulatorGraphicsItem import SimulatorGraphicsItem

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

    def get_all_items(self):
        items = []

        for cond in self.conditions:
            items.append(cond)
            items.extend(cond.sim_items)

        return items

    def cut_selected_messages(self):
        messages = []

        for cond in self.conditions:
            for item in cond.sim_items[:]:
                if item.isSelected():
                    messages.append(item)
                    cond.sim_items.remove(item)

        return messages

    def update_numbering(self, index):
        sub_index = 1

        for cond in self.conditions:
            cond.update_numbering(index + "." + str(sub_index))
            sub_index += 1

    def add_else_cond(self):
        self.conditions.append(RuleConditionItem(ConditionType.ELSE, self))

    def add_else_if_cond(self):
        if self.has_else_condition():
            self.conditions.insert(-1, RuleConditionItem(ConditionType.ELSE_IF, self))
        else:
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

        start_y = 0

        for cond in self.conditions:
            cond.refresh(0, start_y)
            start_y += round(cond.boundingRect().height())

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

class RuleConditionItem(SimulatorGraphicsItem):
    def __init__(self, type, parent):
        super().__init__(parent)
        self.type = type
        self.text = RuleTextItem(type.value, QColor.fromRgb(139,148,148), self)
        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.sim_items = []
        self.ruleset = SimulatorRuleset()

    def refresh(self, x_pos, y_pos):
        self.setPos(x_pos, y_pos)

        start_y = 0
        self.number.setPos(0, start_y)
        self.text.setPos(self.number.boundingRect().width(), start_y)
        start_y += round(self.text.boundingRect().height())

        for item in self.sim_items:
            item.refresh(20, start_y)
            start_y += round(item.boundingRect().height())

        visible_participants = [part for part in self.scene().participants if part.isVisible()]
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

    def update_numbering(self, index):
        super().update_numbering(index)

        sub_index = 1

        for item in self.sim_items:
            item.update_numbering(index + "." + str(sub_index))
            sub_index += 1

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

    def delete_items(self, items):
        for item in self.sim_items[:]:
            if item in items:
                self.sim_items.remove(item)
                self.scene().removeItem(item)

    def next_sibling(self):
        result = None

        conditions = self.parentItem().conditions
        index = self.parentItem().conditions.index(self)

        if index < len(conditions) - 1:
            result = conditions[index + 1]
        else:
            sim_items = self.scene().sim_items

            if sim_items.index(self.parentItem()) < len(sim_items) - 1:
                result = sim_items[sim_items.index(self.parentItem()) + 1]

        if isinstance(result, RuleItem):
            result = result.conditions[0]

        return result

    def prev_sibling(self):
        result = None

        conditions = self.parentItem().conditions
        index = conditions.index(self)

        if index > 0:
            result = conditions[index - 1]
        else:
            sim_items = self.scene().sim_items

            if sim_items.index(self.parentItem()) > 0:
                result = sim_items[sim_items.index(self.parentItem()) - 1]

        if isinstance(result, RuleItem):
            result = result.conditions[-1]

        return result

    def children(self):
        return self.sim_items