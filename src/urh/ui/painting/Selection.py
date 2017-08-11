from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen
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
        self.setPen(QPen(QColor(Qt.transparent), Qt.FlatCap))
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
        self.resizing = False
        self.selected_edge = None
        self.finished = False
