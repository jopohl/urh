import math

import numpy as np
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPen, QFont, QTransform, QFontMetrics
from PyQt5.QtWidgets import (
    QGraphicsScene,
    QGraphicsRectItem,
    QGraphicsSceneDragDropEvent,
    QGraphicsSimpleTextItem,
)

from urh import settings
from urh.ui.painting.HorizontalSelection import HorizontalSelection
from urh.util import util


class ZoomableScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.noise_area = None

        self.separation_areas = []  # type: list[QGraphicsRectItem]
        self.captions = []  # type: list[QGraphicsSimpleTextItem]

        self.centers = [0]

        self.always_show_symbols_legend = False

        self.ones_caption = None
        self.zeros_caption = None

        self.ones_arrow = None
        self.zeros_arrow = None
        self.selection_area = HorizontalSelection(
            0,
            0,
            0,
            0,
            fillcolor=settings.SELECTION_COLOR,
            opacity=settings.SELECTION_OPACITY,
        )
        self.addItem(self.selection_area)

    @property
    def bits_per_symbol(self):
        return int(math.log2(len(self.centers) + 1))

    def draw_noise_area(self, y, h):
        x = self.sceneRect().x()
        w = self.sceneRect().width()

        for area in self.separation_areas:
            area.hide()

        if self.noise_area is None or self.noise_area.scene() != self:
            roi = HorizontalSelection(
                x,
                y,
                w,
                h,
                fillcolor=settings.NOISE_COLOR,
                opacity=settings.NOISE_OPACITY,
            )
            self.noise_area = roi
            self.addItem(self.noise_area)
        else:
            self.noise_area.show()
            self.noise_area.setY(y)
            self.noise_area.height = h

    def hide_legend(self):
        for caption in self.captions:
            caption.hide()

    def clear_legend(self):
        for caption in self.captions:
            self.removeItem(caption)
        self.captions.clear()

    def redraw_legend(self, force_show=False):
        if not (force_show or self.always_show_symbols_legend):
            self.hide_legend()
            return

        num_captions = len(self.centers) + 1
        if num_captions != len(self.captions):
            self.clear_legend()

            fmt = "{0:0" + str(self.bits_per_symbol) + "b}"
            for i in range(num_captions):
                font = QFont()
                font.setPointSize(16)
                font.setBold(True)
                self.captions.append(self.addSimpleText(fmt.format(i), font))

        view_rect = self.parent().view_rect()  # type: QRectF
        padding = 0
        fm = QFontMetrics(self.captions[0].font())

        for i, caption in enumerate(self.captions):
            caption.show()
            scale_x, scale_y = util.calc_x_y_scale(
                self.separation_areas[i].rect(), self.parent()
            )
            try:
                caption.setPos(
                    view_rect.x()
                    + view_rect.width()
                    - fm.width(caption.text()) * scale_x,
                    self.centers[i] + padding,
                )
            except IndexError:
                caption.setPos(
                    view_rect.x()
                    + view_rect.width()
                    - fm.width(caption.text()) * scale_x,
                    self.centers[i - 1] - padding - fm.height() * scale_y,
                )

            caption.setTransform(QTransform.fromScale(scale_x, scale_y), False)

    def draw_sep_area(self, centers: np.ndarray, show_symbols=False):
        x = self.sceneRect().x()
        y = self.sceneRect().y()
        w = self.sceneRect().width()
        h = self.sceneRect().height()
        reversed_centers = list(reversed(centers))

        num_areas = len(centers) + 1
        if num_areas != len(self.separation_areas):
            for area in self.separation_areas:
                self.removeItem(area)
            self.separation_areas.clear()

            for i in range(num_areas):
                area = QGraphicsRectItem(0, 0, 0, 0)
                if i % 2 == 0:
                    area.setBrush(settings.ZEROS_AREA_COLOR)
                else:
                    area.setBrush(settings.ONES_AREA_COLOR)
                area.setOpacity(settings.SEPARATION_OPACITY)
                area.setPen(QPen(settings.TRANSPARENT_COLOR, 0))
                self.addItem(area)
                self.separation_areas.append(area)

        start = y

        for i, area in enumerate(self.separation_areas):
            area.show()
            try:
                self.separation_areas[i].setRect(
                    x, start, w, abs(start - reversed_centers[i])
                )
                start += abs(start - reversed_centers[i])
            except IndexError:
                self.separation_areas[i].setRect(x, start, w, abs(start - h))

        if self.noise_area is not None:
            self.noise_area.hide()

        self.centers = centers
        self.redraw_legend(show_symbols)

    def clear(self):
        self.noise_area = None
        self.separation_areas.clear()
        self.captions.clear()
        self.selection_area = None
        super().clear()

    def dragEnterEvent(self, event: QGraphicsSceneDragDropEvent):
        event.accept()

    def dragMoveEvent(self, event: QGraphicsSceneDragDropEvent):
        event.accept()
