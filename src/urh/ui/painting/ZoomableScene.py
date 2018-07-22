from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsSceneDragDropEvent

from urh import constants
from urh.ui.painting.HorizontalSelection import HorizontalSelection


class ZoomableScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.noise_area = None
        self.ones_area = None
        self.zeros_area = None
        self.ones_arrow = None
        self.zeros_arrow = None
        self.selection_area = HorizontalSelection(0, 0, 0, 0, fillcolor=constants.SELECTION_COLOR,
                                                  opacity=constants.SELECTION_OPACITY)
        self.addItem(self.selection_area)

    def draw_noise_area(self, y, h):
        x = self.sceneRect().x()
        w = self.sceneRect().width()

        if self.ones_area is not None:
            self.ones_area.hide()
        if self.zeros_area is not None:
            self.zeros_area.hide()

        if self.noise_area is None or self.noise_area.scene() != self:
            roi = HorizontalSelection(x, y, w, h, fillcolor=constants.NOISE_COLOR, opacity=constants.NOISE_OPACITY)
            self.noise_area = roi
            self.addItem(self.noise_area)
        else:
            self.noise_area.show()
            self.noise_area.setY(y)
            self.noise_area.height = h

    def draw_sep_area(self, y_mid):
        x = self.sceneRect().x()
        y = self.sceneRect().y()
        h = self.sceneRect().height()
        w = self.sceneRect().width()
        if self.noise_area is not None:
            self.noise_area.hide()

        if self.ones_area is None:
            self.ones_area = QGraphicsRectItem(x, y, w, h / 2 + y_mid)
            self.ones_area.setBrush(constants.ONES_AREA_COLOR)
            self.ones_area.setOpacity(constants.SEPARATION_OPACITY)
            self.ones_area.setPen(QPen(constants.TRANSPARENT_COLOR, 0))
            self.addItem(self.ones_area)

        else:
            self.ones_area.show()
            self.ones_area.setRect(x, y, w, h / 2 + y_mid)

        start = y + h / 2 + y_mid
        if self.zeros_area is None:
            self.zeros_area = QGraphicsRectItem(x, start, w, (y + h) - start)
            self.zeros_area.setBrush(constants.ZEROS_AREA_COLOR)
            self.zeros_area.setOpacity(constants.SEPARATION_OPACITY)
            self.zeros_area.setPen(QPen(constants.TRANSPARENT_COLOR, 0))
            self.addItem(self.zeros_area)
        else:
            self.zeros_area.show()
            self.zeros_area.setRect(x, start, w, (y + h) - start)

    def clear(self):
        self.noise_area = None
        self.ones_area = None
        self.zeros_area = None
        self.zeros_arrow = None
        self.ones_arrow = None
        self.selection_area = None
        super().clear()

    def dragEnterEvent(self, event: QGraphicsSceneDragDropEvent):
        event.accept()

    def dragMoveEvent(self, event: QGraphicsSceneDragDropEvent):
        event.accept()
