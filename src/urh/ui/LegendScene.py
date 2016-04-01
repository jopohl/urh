from PyQt5.QtWidgets import QGraphicsScene

from urh.ui.LabeledArrow import LabeledArrow


class LegendScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ones_arrow = None
        self.zeros_arrow = None

    def draw_one_zero_arrows(self, ymid):
        y = self.sceneRect().y()
        h = self.sceneRect().height()
        if ymid < y:
            ymid = y
        elif ymid > y + h:
            ymid = y + h

        w_view = self.sceneRect().width()

        if self.zeros_arrow is None:
            self.zeros_arrow = LabeledArrow(w_view / 2, y + h / 2 + ymid, w_view / 2, y + h, 0)
            self.addItem(self.zeros_arrow)
        else:
            self.removeItem(self.zeros_arrow)
            self.zeros_arrow = LabeledArrow(w_view / 2, y + h / 2 + ymid, w_view / 2, y + h, 0)
            self.addItem(self.zeros_arrow)

        if self.ones_arrow is None:
            self.ones_arrow = LabeledArrow(w_view / 2, y, w_view / 2, y + h / 2 + ymid, 1)
            self.addItem(self.ones_arrow)
        else:
            self.removeItem(self.ones_arrow)
            self.ones_arrow = LabeledArrow(w_view / 2, y, w_view / 2, y + h / 2 + ymid, 1)
            self.addItem(self.ones_arrow)

    def clear(self):
        self.zeros_arrow = None
        self.ones_arrow = None
        super().clear()