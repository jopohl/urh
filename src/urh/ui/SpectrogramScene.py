import math

import numpy as np
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPainter

from urh.signalprocessing.Spectrogram import Spectrogram
from urh.ui.ZoomableScene import ZoomableScene


class SpectrogramScene(ZoomableScene):
    def __init__(self, spectrogram: Spectrogram, parent=None):
        super().__init__(parent)
        self.spectrogram = spectrogram
        time_bins, freq_bins = self.spectrogram.dimension
        self.setSceneRect(0, 0, time_bins, freq_bins)


    def drawBackground(self, painter: QPainter, rect: QRectF):
        time_bins, freq_bins = self.spectrogram.dimension

        try:
            x_res = int(math.ceil(rect.width() / self.parent().width()))
            y_res = int(math.ceil(rect.height() / self.parent().height()))
        except AttributeError:
            x_res, y_res = 1, 1

        x_start = int(rect.x()) if rect.x() > 0 else 0
        x_end = int(rect.x() + rect.width()) if rect.x() + rect.width() < time_bins else time_bins
        y_start = int(rect.y()) if rect.y() > 0 else 0
        y_end = int(rect.y() + rect.height()) if rect.y() + rect.height() < freq_bins else freq_bins

        for x in range(x_start, x_end, x_res):
            for y in range(y_start, y_end, y_res):
                value = np.mean(self.spectrogram.data[x:x+x_res, y:y+y_res])
                color = self.spectrogram.get_color_for_value(value)
                painter.setPen(color)
                painter.drawEllipse(x, y, 1, 1)
