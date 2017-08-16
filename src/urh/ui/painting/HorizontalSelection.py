from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QTransform

from urh.ui.painting.Selection import Selection


class HorizontalSelection(Selection):
    def __init__(self, *args, fillcolor, opacity, parent=None):
        super().__init__(*args, fillcolor=fillcolor, opacity=opacity, parent=parent)

    @property
    def length(self):
        return self.width

    @property
    def is_empty(self) -> bool:
        return self.width == 0

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

    def clear(self):
        self.width = 0
        super().clear()

    def get_selected_edge(self, pos: QPointF, transform: QTransform):
        return super()._get_selected_edge(pos, transform, horizontal_selection=True)
