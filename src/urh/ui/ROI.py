from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QGraphicsRectItem

from urh import constants


class ROI(QGraphicsRectItem):
    def __init__(self, *args, fillcolor, opacity, parent=None):
        self.padding = 0
        if len(args) == 0:
            super().__init__(parent)
        elif len(args) == 1:
            super().__init__(args[0], parent)
        elif len(args) == 4:
            x0 = args[0]
            y0 = args[1]
            w = args[2]
            h = args[3]
            ymin = y0 + self.padding * h
            roi_height = (1 - 2 * self.padding) * h
            super().__init__(x0, ymin, w, roi_height, parent)

        self.finished = False
        self.selected_edge = None
        """:type: int """
        self.resizing = False

        self.setBrush(fillcolor)
        self.setPen(QPen(QColor(Qt.transparent), Qt.FlatCap))
        self.setOpacity(opacity)

    @property
    def is_empty(self) -> bool:
        return self.width == 0

    @property
    def width(self):
        return self.rect().width()

    @width.setter
    def width(self, value):
        if value == self.width:
            return

        r = self.rect()
        r.setWidth(value)
        self.setRect(r)

    @property
    def height(self):
        return self.rect().height()

    @height.setter
    def height(self, value):
        if value == self.height:
            return

        r = self.rect()
        r.setHeight(value)
        self.setRect(r)

    @property
    def x(self):
        return self.rect().x()

    def setX(self, p_float):
        if p_float == self.x:
            return

        r = self.rect()
        r.setX(p_float)
        self.setRect(r)

    @property
    def start(self):
        if self.width < 0:
            return self.x + self.width
        else:
            return self.x

    @start.setter
    def start(self, value):
        self.setX(value)

    @property
    def end(self):
        if self.width < 0:
            return self.x
        else:
            return self.x + self.width

    @end.setter
    def end(self, value):
        self.width = value - self.start

    @property
    def y(self):
        return self.rect().y()

    def setY(self, p_float):
        if p_float == self.y:
            return

        r = self.rect()
        r.setY(p_float)
        self.setRect(r)

    def is_in_roi(self, pos: QPointF):
        x1 = self.rect().x()
        x2 = x1 + self.rect().width()
        y1 = self.rect().y()
        y2 = y1 + self.rect().width()

        if x1 < pos.x() < x2 and y1 < pos.y() < y2:
            return True

        return False

    def get_selected_edge(self, pos: QPointF, width_view: float):
        """
        Bestimmt auf welcher Ecke der ROI der Mauszeiger gerade ist.
        0 = links, 1 = rechts

        :param pos: In die Szene gemappte Position des Mauszeigers
        """
        x1 = self.rect().x()
        x2 = x1 + self.rect().width()
        y1 = self.rect().y()
        y2 = y1 + self.rect().height()
        x = pos.x()
        y = pos.y()

        if x1 - 0.025 * width_view < x < x1 + 0.025 * width_view and y1 < y < y2:
            self.selected_edge = 0
            return 0

        if x2 - 0.025 * width_view < x < x2 + 0.025 * width_view and y1 < y < y2:
            self.selected_edge = 1
            return 1

        self.selected_edge = None
        return None

    def clear(self):
        self.width = 0
        self.resizing = False
        self.selected_edge = None
        self.finished = False



