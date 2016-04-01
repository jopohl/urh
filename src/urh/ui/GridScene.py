import locale
from PyQt5.QtCore import QRectF, QLineF, Qt
from PyQt5.QtGui import QPainter, QFont, QFontMetrics, QPen
import numpy as np

from urh.ui.ZoomableScene import ZoomableScene


class GridScene(ZoomableScene):
    def __init__(self, parent=None):
        self.draw_grid = False
        self.font_metrics = QFontMetrics(QFont())
        self.center_freq = 433.92e6
        self.frequencies = []
        super().__init__(parent)

    def drawBackground(self, painter: QPainter, rect: QRectF):
        # freqs = np.fft.fftfreq(len(w), 1 / self.sample_rate)
        if self.draw_grid and len(self.frequencies) > 0:
            painter.setPen(QPen(painter.pen().color(), Qt.FlatCap))
            parent_width = self.parent().width() if hasattr(self.parent(), "width") else 750
            view_rect = self.parent().view_rect() if hasattr(self.parent(), "view_rect") else rect

            font_width = self.font_metrics.width(self.value_with_suffix(self.center_freq) + "   ")
            x_grid_size = int(view_rect.width() / parent_width * font_width)
            # x_grid_size = int(0.1 * view_rect.width()) if 0.1 * view_rect.width() > 1 else 1
            y_grid_size = view_rect.height() / parent_width * font_width
            x_mid = np.where(self.frequencies == 0)[0]
            x_mid = int(x_mid[0]) if len(x_mid) > 0 else 0

            left = int(rect.left()) - (int(rect.left()) % x_grid_size)
            left = left if left > 0 else 0

            top = rect.top() - (rect.top() % y_grid_size)
            bottom = rect.bottom() - (rect.bottom() % y_grid_size)
            right_border = int(rect.right()) if rect.right() < len(self.frequencies) else len(self.frequencies)

            x_range = list(range(x_mid, left, -x_grid_size)) + list(range(x_mid, right_border, x_grid_size))

            lines = [QLineF(x, rect.top(), x, bottom) for x in x_range] \
                    + [QLineF(rect.left(), y, rect.right(), y) for y in np.arange(top, bottom, y_grid_size)]

            painter.drawLines(lines)
            scale_x = view_rect.width() / parent_width
            scale_y = view_rect.height() / parent_width
            painter.scale(scale_x, scale_y)

            font_height = self.font_metrics.height()

            for x in x_range:
                value = self.value_with_suffix(self.center_freq + self.frequencies[x])
                font_width = self.font_metrics.width(value)
                painter.drawText(x / scale_x - font_width / 2,
                                 bottom / scale_y + font_height, value)

    def value_with_suffix(self, value: float):
        if value >= 10 ** 9:
            return locale.format_string("%.2f", value / 10 ** 9) + "G"
        elif value >= 10 ** 6:
            return locale.format_string("%.2f",value / 10 ** 6) + "M"
        elif value >= 10 ** 3:
            return locale.format_string("%.2f", value / 10 ** 3) + "K"
        else:
            return locale.format_string("%.2f", value)
