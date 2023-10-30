from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen, QTransform
from PyQt5.QtWidgets import QGraphicsRectItem


class Selection(QGraphicsRectItem):
    def __init__(self, *args, fillcolor, opacity, parent=None):
        if len(args) == 0:
            super().__init__(parent)
        elif len(args) == 1:
            super().__init__(args[0], parent)
        elif len(args) == 4:
            x0, y0, w, h = args
            super().__init__(x0, y0, w, h, parent)

        self.finished = False
        self.selected_edge = None  # type: int
        self.resizing = False

        self.setBrush(fillcolor)
        self.setPen(QPen(QColor(Qt.transparent), 0))
        self.setOpacity(opacity)

    @property
    def is_empty(self) -> bool:
        raise NotImplementedError("Overwrite in subclass")

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
    def y(self):
        return self.rect().y()

    def setY(self, p_float):
        if p_float == self.y:
            return

        r = self.rect()
        r.setY(p_float)
        self.setRect(r)

    @property
    def start(self):
        raise NotImplementedError("Overwrite in subclass")

    @start.setter
    def start(self, value):
        raise NotImplementedError("Overwrite in subclass")

    @property
    def end(self):
        raise NotImplementedError("Overwrite in subclass")

    @end.setter
    def end(self, value):
        raise NotImplementedError("Overwrite in subclass")

    def _get_selected_edge(
        self, pos: QPointF, transform: QTransform, horizontal_selection: bool
    ):
        x1, x2 = self.x, self.x + self.width
        y1, y2 = self.y, self.y + self.height
        x, y = pos.x(), pos.y()

        spacing = 5
        spacing /= transform.m11() if horizontal_selection else transform.m22()

        if horizontal_selection:
            x1a, x1b = x1 - spacing, x1 + spacing
            y1a, y1b = y1, y2
            x2a, x2b = x2 - spacing, x2 + spacing
            y2a, y2b = y1, y2
        else:
            x1a, x1b, x2a, x2b = x1, x2, x1, x2
            y1a, y1b = min(y1 - spacing, y1 + spacing), max(y1 - spacing, y1 + spacing)
            y2a, y2b = min(y2 - spacing, y2 + spacing), max(y2 - spacing, y2 + spacing)

        if x1a < x < x1b and y1a < y < y1b:
            self.selected_edge = 0
            return 0

        if x2a < x < x2b and y2a < y < y2b:
            self.selected_edge = 1
            return 1

        self.selected_edge = None
        return None

    def clear(self):
        self.resizing = False
        self.selected_edge = None
        self.finished = False
