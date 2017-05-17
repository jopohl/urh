from PyQt5.QtCore import pyqtSignal, QRect
from PyQt5.QtGui import QWheelEvent, QMouseEvent
from PyQt5.QtWidgets import QToolTip

from urh.ui.GridScene import GridScene
from urh.ui.views.ZoomableGraphicView import ZoomableGraphicView
from urh.util.Formatter import Formatter


class LiveGraphicView(ZoomableGraphicView):
    freq_clicked = pyqtSignal(float)
    wheel_event_triggered = pyqtSignal(QWheelEvent)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.capturing_data = True

    def wheelEvent(self, event: QWheelEvent):
        self.wheel_event_triggered.emit(event)
        if self.capturing_data:
            return

        super().wheelEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if isinstance(self.scene(), GridScene):
            freq = self.scene().get_freq_for_pos(int(self.mapToScene(event.pos()).x()))
            if freq is not None:
                QToolTip.showText(self.mapToGlobal(event.pos()), "Tune to:" + Formatter.big_value_with_suffix(freq),
                                  None, QRect(), 10000)

    def mousePressEvent(self, event: QMouseEvent):
        if isinstance(self.scene(), GridScene):
            freq = self.scene().get_freq_for_pos(int(self.mapToScene(event.pos()).x()))
            if freq is not None:
                self.freq_clicked.emit(freq)

    def update(self, *__args):
        try:
            super().update(*__args)
            super().show_full_scene()
        except RuntimeError:
            pass
