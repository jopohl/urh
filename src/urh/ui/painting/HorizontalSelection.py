from PyQt5.QtCore import QPointF

from urh.ui.painting.Selection import Selection


class HorizontalSelection(Selection):
    def __init__(self, *args, fillcolor, opacity, parent=None):
        super().__init__(*args, fillcolor=fillcolor, opacity=opacity, parent=parent)

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
        super().clear()
