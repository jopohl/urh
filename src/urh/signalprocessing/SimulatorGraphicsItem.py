from PyQt5.QtWidgets import QGraphicsObject, QGraphicsItem, QGraphicsTextItem, QGraphicsSceneDragDropEvent
from PyQt5.QtGui import QFontDatabase, QFont, QDropEvent, QPen, QColor
from PyQt5.QtCore import QRectF, Qt

from urh import constants

from urh.signalprocessing.SimulatorItem import SimulatorItem

class SimulatorGraphicsItem(QGraphicsObject):
    def __init__(self, model_item: SimulatorItem, parent=None):
        super().__init__(parent)
        self.model_item = model_item
        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.hover_active = False
        self.drag_over = False
        self.setAcceptHoverEvents(True)
        self.setAcceptDrops(True)
        self.bounding_rect = QRectF()
        self.drop_indicator_position = None
        self.item_under_mouse = None
        self.number = QGraphicsTextItem(self)
        self.index = None
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(8)
        font.setWeight(QFont.DemiBold)
        self.number.setFont(font)

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

    def find_scene_item(self, model_item):
        if model_item is None:
            return None

        for item in self.childItems():
            if isinstance(item, SimulatorGraphicsItem):
                if item.model_item == model_item:
                    return item

        print("WHOOPS: Item not found ... :(")
        return None

    def is_last_item(self):
        return self == self.scene().get_last_item()

    def is_first_item(self):
        return self == self.scene().get_first_item()

    def next_sibling(self):
        result = None
    
        if self.parentItem() is None:
            sim_items = self.scene().sim_items
        else:
            sim_items = self.parentItem().sim_items

        index = sim_items.index(self)

        if index < len(sim_items) - 1:
            result = sim_items[index + 1]

        if isinstance(result, RuleItem):
            result = result.conditions[0]

        return result

    def prev_sibling(self):
        result = None

        if self.parentItem() is None:
            sim_items = self.scene().sim_items
        else:
            sim_items = self.parentItem().sim_items

        index = sim_items.index(self)

        if index > 0:
            result = sim_items[index - 1]

        if isinstance(result, RuleItem):
            result = result.conditions[-1]

        return result

    def next(self):
        if self.children():
            return self.children()[0]

        curr = self

        while True:
            if curr.next_sibling() is not None:
                return curr.next_sibling()

            curr = curr.parentItem()

            if curr is None or isinstance(curr, RuleItem):
                return None

    def prev(self):
        parent = self.parentItem()

        curr = self

        while True:
            if curr.prev_sibling() is not None:
                curr = curr.prev_sibling()
                break
            else:
                return parent

        while curr.children():
            curr = curr.children()[-1]

        return curr

    def children(self):
        return []

    def update_drop_indicator(self, pos):
        rect = self.boundingRect()

        if pos.y() - rect.top() < rect.height() / 2:
            self.drop_indicator_position = QAbstractItemView.AboveItem
        else:
            self.drop_indicator_position = QAbstractItemView.BelowItem

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
        rect = self.boundingRect()

        if self.drop_indicator_position == QAbstractItemView.AboveItem:
            painter.drawLine(QLineF(rect.topLeft(), rect.topRight()))
        else:
            painter.drawLine(QLineF(rect.bottomLeft(), rect.bottomRight()))

    def update_position(self, x_pos, y_pos):
        width = self.scene().items_width()
        self.prepareGeometryChange()
        self.bounding_rect = QRectF(0, 0, width, self.childrenBoundingRect().height())

    def boundingRect(self):
        return self.bounding_rect

    def update_numbering(self, index):
        self.index = index
        self.number.setPlainText(self.index)

    def mouseMoveEvent(self, event):
        items = [item for item in self.scene().items(event.scenePos()) if isinstance(item, SimulatorGraphicsItem) and item != self]
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
            self.item_under_mouse.setSelected(False)
            selected_items = self.scene().cut_selected_messages()

            ref_item = self.item_under_mouse
            position = self.item_under_mouse.drop_indicator_position

            for item in selected_items:
                self.scene().insert_at(ref_item, position, item)
                ref_item = item
                position = QAbstractItemView.BelowItem
                
            self.item_under_mouse = None

        super().mouseReleaseEvent(event)
        self.scene().update_view()