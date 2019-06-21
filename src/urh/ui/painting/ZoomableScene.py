from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPen, QFont, QTransform, QFontMetrics
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsSceneDragDropEvent, QGraphicsSimpleTextItem

from urh import constants
from urh.ui.painting.HorizontalSelection import HorizontalSelection
from urh.util import util


class ZoomableScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.noise_area = None
        self.ones_area = None
        self.zeros_area = None

        self.ones_caption = None
        self.zeros_caption = None

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

    def draw_sep_area(self, y_mid, show_symbols=False):
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

        if self.ones_caption is None:
            font = QFont()
            font.setPointSize(32)
            font.setBold(True)
            self.ones_caption = self.addSimpleText("1", font)

        if self.zeros_caption is None:
            font = QFont()
            font.setPointSize(32)
            font.setBold(True)
            self.zeros_caption = self.addSimpleText("0", font)

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

        if show_symbols:
            view_rect = self.parent().view_rect()  # type: QRectF

            self.ones_caption.show()
            self.zeros_caption.show()
            padding = view_rect.height() / 20
            scale_x, scale_y = util.calc_x_y_scale(self.ones_area.rect(), self.parent())

            self.ones_caption.setPos(view_rect.center().x(),
                                     y_mid - QFontMetrics(self.ones_caption.font()).height()*scale_y - padding)
            self.ones_caption.setTransform(QTransform.fromScale(scale_x, scale_y), False)

            scale_x, scale_y = util.calc_x_y_scale(self.zeros_area.rect(), self.parent())

            self.zeros_caption.setPos(view_rect.center().x(), y_mid + padding)
            self.zeros_caption.setTransform(QTransform.fromScale(scale_x, scale_y), False)
        else:
            self.ones_caption.hide()
            self.zeros_caption.hide()

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
